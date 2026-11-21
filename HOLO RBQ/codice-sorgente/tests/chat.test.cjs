const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const element = () => ({ value: '', addEventListener() {}, append() {}, replaceChildren() {}, scrollIntoView() {} });
const elements = new Map();
const document = {
  createElement: element,
  getElementById(id) {
    if (!elements.has(id)) elements.set(id, element());
    return elements.get(id);
  }
};
document.getElementById('quote').elements = {};
const context = vm.createContext({ document, URLSearchParams, setInterval() {}, fetch: () => new Promise(() => {}) });
vm.runInContext(script, context);

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
