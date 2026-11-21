"""Collaudo Windows reale del launcher, senza browser o trasporti email."""
import json
from pathlib import Path
import shutil
import socket
import subprocess
from tempfile import TemporaryDirectory
import time
from urllib.request import Request, build_opener, ProxyHandler


def main():
    opener = build_opener(ProxyHandler({}))
    with TemporaryDirectory(prefix="HOLO RBQ collaudo ") as directory:
        root = Path(directory)
        source = root / "copia con spazi" / "codice-sorgente"
        shutil.copytree(Path(__file__).resolve().parents[1], source,
                        ignore=shutil.ignore_patterns('.venv', 'data', '__pycache__'))
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
        url = f'http://127.0.0.1:{port}'
        command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                   '-File', str(source / 'Avvia-HOLO.ps1'), '-NoBrowser', '-Port', str(port)]

        def get_clients():
            with opener.open(url + '/api/clients', timeout=2) as response:
                return json.load(response)

        def stop(process):
            if process.poll() is None:
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                process.wait(timeout=20)

        def ready(process, log):
            deadline = time.monotonic() + 180
            while process.poll() is None and time.monotonic() < deadline:
                try:
                    return get_clients()
                except OSError:
                    time.sleep(0.3)
            raise AssertionError('Avvio fallito: ' + log.read_text(errors='replace')[-8000:])

        log = root / 'avvio.log'
        with log.open('w') as output:
            process = subprocess.Popen(command, cwd=root, stdout=output, stderr=subprocess.STDOUT)
            try:
                assert len(ready(process, log)) == 3
                stamp = source / '.venv' / '.holo-requirements.sha256'
                installed_at = stamp.stat().st_mtime_ns
                data = json.dumps({'name': 'Cliente persistenza launcher'}).encode()
                with opener.open(Request(url + '/api/clients', data=data,
                                        headers={'Content-Type': 'application/json'})) as response:
                    assert response.status == 201
                second = subprocess.run(command, cwd=root, capture_output=True, timeout=40)
                assert second.returncode == 2, second.stdout.decode(errors='replace')
                assert len(get_clients()) == 4
                print('PASS prima installazione, percorso con spazi, avvio da altra cartella, porta occupata.')
            finally:
                stop(process)
        with log.open('a') as output:
            restarted = subprocess.Popen(command, cwd=root, stdout=output, stderr=subprocess.STDOUT)
            try:
                clients = ready(restarted, log)
                assert any(item['name'] == 'Cliente persistenza launcher' for item in clients)
                assert stamp.stat().st_mtime_ns == installed_at, 'Installazione ripetuta senza variazioni'
                print('PASS riavvio, persistenza dati, nessuna reinstallazione con requisiti invariati.')
            finally:
                stop(restarted)


if __name__ == '__main__':
    main()
