"""Avvio locale: percorso stabile, porta esclusiva e browser solo a server pronto."""
import argparse
from pathlib import Path
import socket
import sys
from threading import Event, Thread
import webbrowser

import uvicorn
from app import create_app

ROOT = Path(__file__).resolve().parent
VERSION = "0.2.0-demo"


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
    database = ROOT / "data" / "holo.sqlite3"
    print(f"HOLO RBQ {VERSION}\nCartella: {ROOT}\nDatabase: {database}\nBrowser: {url}")
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
        server = uvicorn.Server(uvicorn.Config(create_app(database), host="127.0.0.1", port=args.port))
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
