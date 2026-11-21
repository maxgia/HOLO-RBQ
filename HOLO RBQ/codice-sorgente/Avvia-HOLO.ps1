param(
    [ValidateRange(1, 65535)][int]$Port = 8002,
    [switch]$NoBrowser
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try {
    $source = $PSScriptRoot
    $requirements = Join-Path $source 'requirements.txt'
    foreach ($name in @('app.py', 'index.html', 'start_local.py', 'requirements.txt')) {
        if (-not (Test-Path (Join-Path $source $name))) {
            throw "File mancante: $name. Estrarre prima tutto lo ZIP aggiornato."
        }
    }
    Write-Host "Cartella applicazione: $source"
    $venv = Join-Path $source '.venv'
    $python = Join-Path $venv 'Scripts\python.exe'
    if (-not (Test-Path $python)) {
        Write-Host 'Prima preparazione: creazione ambiente Python locale.'
        if (Get-Command py -ErrorAction SilentlyContinue) {
            & py -3 -m venv $venv
        } elseif (Get-Command python -ErrorAction SilentlyContinue) {
            & python -m venv $venv
        } else {
            throw 'Python non trovato. Installare Python 3.10 o successivo, poi riprovare.'
        }
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path $python)) { throw 'Creazione ambiente Python non riuscita.' }
    }
    & $python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
    if ($LASTEXITCODE -ne 0) { throw 'Serve Python 3.10 o successivo in .venv.' }
    $stamp = Join-Path $venv '.holo-requirements.sha256'
    $digest = (Get-FileHash -Algorithm SHA256 $requirements).Hash
    $installed = if (Test-Path $stamp) { (Get-Content $stamp -Raw).Trim() } else { '' }
    if ($installed -ne $digest) {
        Write-Host 'Installazione delle dipendenze richieste (richiede connessione Internet).'
        & $python -m pip install -r $requirements
        if ($LASTEXITCODE -ne 0) { throw 'Installazione non riuscita. Verificare la connessione e riprovare.' }
        Set-Content -Path $stamp -Value $digest -Encoding ASCII
    }
    $launcherArgs = @((Join-Path $source 'start_local.py'), '--port', "$Port")
    if ($NoBrowser) { $launcherArgs += '--no-browser' }
    & $python @launcherArgs
    exit $LASTEXITCODE
} catch {
    Write-Host "Avvio interrotto: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
