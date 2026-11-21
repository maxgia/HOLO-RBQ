"""Avvio locale: percorso stabile, porta esclusiva e browser solo a server pronto."""
import argparse
from pathlib import Path
import socket
import sys
from threading import Event, Thread
import webbrowser

import uvicorn
from app import create_app
from database import postgres_url

ROOT = Path(__file__).resolve().parent
VERSION = "0.3.0-postgres"


def open_when_ready(server, url, stopped):
    for _ in range(300):
        if stopped.is_set() or server.should_exit:
            return
        if server.started:
            try:
                webbrowser.open(url)
            except (webbrowser.Error, OSError):
                print(f"Apri il browser su {url}")
            return
        if stopped.wait(0.1):
            return


def main(argv=None):
    parser = argparse.ArgumentParser(description="Avvia HOLO RBQ senza avviare il worker email.")
    parser.add_argument("--port", type=int, default=8002)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("La porta deve essere tra 1 e 65535.")
    url = f"http://127.0.0.1:{args.port}/"
    try:
        database = postgres_url(config=ROOT / 'data' / 'postgres.json')
    except (ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(f"HOLO RBQ {VERSION}\nCartella: {ROOT}\nDatabase: {database.render_as_string(hide_password=True)}\nBrowser: {url}")
    print("Per fermare il server premi Ctrl+C. Il worker email resta spento.")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        try:
            if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
                listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            listener.bind(("127.0.0.1", args.port))
            listener.listen(128)
        except OSError as error:
            print(f"Porta {args.port} non disponibile: {error}. Chiudi il server precedente "
                  "o scegli una porta diversa con -Port nel comando PowerShell.", file=sys.stderr)
            return 2
        try:
            application = create_app(database)
        except Exception:
            print('Avvio interrotto: PostgreSQL non disponibile o migrazione non verificata. Controlla la configurazione; SQLite non viene usato come ripiego.', file=sys.stderr)
            return 1
        server = uvicorn.Server(uvicorn.Config(application, host="127.0.0.1", port=args.port))
        stopped = Event()
        if not args.no_browser:
            Thread(target=open_when_ready, args=(server, url, stopped), daemon=True).start()
        try:
            server.run(sockets=[listener])
        finally:
            stopped.set()
    return 0 if server.started else 1


if __name__ == "__main__":
    raise SystemExit(main())
