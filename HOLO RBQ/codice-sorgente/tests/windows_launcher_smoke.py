"""Preflight PowerShell 5.1: dipendenze e nessun fallback SQLite senza configurazione PG."""
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory


def main():
    with TemporaryDirectory(prefix='HOLO RBQ collaudo ') as directory:
        root = Path(directory)
        source = root / 'copia con spazi' / 'codice-sorgente'
        shutil.copytree(Path(__file__).resolve().parents[1], source,
                        ignore=shutil.ignore_patterns('.venv', 'data', '__pycache__'))
        command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                   '-File', str(source / 'Avvia-HOLO.ps1'), '-NoBrowser']
        first = subprocess.run(command, cwd=root, capture_output=True, timeout=180)
        assert first.returncode == 1
        assert b'PostgreSQL non configurato' in first.stderr, first.stdout[-3000:]
        assert not (source / 'data' / 'holo.sqlite3').exists()
        stamp = source / '.venv' / '.holo-requirements.sha256'
        before = stamp.stat().st_mtime_ns
        second = subprocess.run(command, cwd=root, capture_output=True, timeout=40)
        assert second.returncode == 1
        assert stamp.stat().st_mtime_ns == before
        print('PASS setup Windows con spazi, dipendenze, mancata configurazione esplicita, nessun fallback SQLite, nessuna reinstallazione.')


if __name__ == '__main__':
    main()
