import socket
from contextlib import contextmanager
from threading import Thread
from time import monotonic, sleep

import uvicorn

from app import create_app


@contextmanager
def serve(database):
    app = create_app(database)
    server = uvicorn.Server(uvicorn.Config(app, log_level="warning"))
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        address, port = listener.getsockname()
        worker = Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
        worker.start()
        try:
            deadline = monotonic() + 10
            while not server.started:
                if not worker.is_alive() or monotonic() >= deadline:
                    raise RuntimeError("Uvicorn non ha avviato il server di test.")
                sleep(0.02)
            yield f"http://{address}:{port}/"
        finally:
            server.should_exit = True
            worker.join(timeout=10)
            if worker.is_alive():
                raise RuntimeError("Uvicorn non ha arrestato il server di test.")
