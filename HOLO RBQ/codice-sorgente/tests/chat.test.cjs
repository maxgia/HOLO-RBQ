const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
// Parser unit tests stay independent of DOM/navigation; compile the full script too.
new vm.Script(script);
const start = script.indexOf('function parseInvoiceSearch(');
const end = script.indexOf('async function showInvoiceSearch(', start);
assert.ok(start >= 0 && end > start);
const context = vm.createContext({});
vm.runInContext(script.slice(start, end), context);

for (const [question, query, status] of [
  ['Cosa deve ancora pagare Rossi?', 'Rossi', 'open'],
  ['Quanto resta da incassare da Studio Rossi?', 'Studio Rossi', 'open'],
  ['Quali fatture di Rossi sono ancora da incassare?', 'Rossi', 'open'],
  ['Quanto resta da incassare?', '', 'open'],
  ['Mostrami le fatture di Studio Rossi scadute', 'Studio Rossi', 'overdue'],
  ['Elenca le fatture saldate', '', 'paid'],
  ['Cerca fatture di Verdi', 'Verdi', 'all'],
  ['Quali fatture di Rossi sono non pagate?', 'Rossi', 'open'],
]) {
  test(question, () => assert.deepEqual({ ...context.parseInvoiceSearch(question) }, { query, status }));
}

for (const question of [
  'Come registro un incasso?',
  'Mostrami i preventivi di Studio Rossi',
  'Cerca Rossi e prepara un preventivo da 800 €',
]) {
  test(question, () => assert.equal(context.parseInvoiceSearch(question), null));
}
