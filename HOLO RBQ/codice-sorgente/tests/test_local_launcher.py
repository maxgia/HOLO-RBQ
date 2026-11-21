from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from threading import Event
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import start_local
from sqlalchemy.engine import make_url


class LocalLauncherTests(unittest.TestCase):
    def setUp(self):
        config = patch('start_local.postgres_url', return_value=make_url('postgresql+psycopg://user:hidden@127.0.0.1/holo_test'))
        config.start()
        self.addCleanup(config.stop)
    @patch('start_local.webbrowser.open')
    def test_browser_opens_only_when_server_is_ready(self, browser):
        start_local.open_when_ready(SimpleNamespace(started=True, should_exit=False), 'http://127.0.0.1:8002/', Event())
        browser.assert_called_once_with('http://127.0.0.1:8002/')

    @patch('start_local.webbrowser.open')
    def test_stopped_server_does_not_open_browser(self, browser):
        stopped = Event()
        stopped.set()
        start_local.open_when_ready(SimpleNamespace(started=True, should_exit=False), 'unused', stopped)
        browser.assert_not_called()

    @patch('start_local.create_app')
    @patch('start_local.socket.socket')
    def test_busy_port_does_not_open_another_copy_or_touch_database(self, sock, factory):
        sock.return_value.__enter__.return_value.bind.side_effect = OSError('Porta occupata')
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.assertEqual(start_local.main(['--no-browser']), 2)
        factory.assert_not_called()

    @patch('start_local.Thread')
    @patch('start_local.uvicorn.Server')
    @patch('start_local.create_app')
    @patch('start_local.socket.socket')
    def test_no_browser_uses_configured_postgres(self, sock, factory, server, thread):
        with patch('start_local.ROOT', Path('/folder with spaces')), redirect_stdout(StringIO()):
            server.return_value.started = True
            self.assertEqual(start_local.main(['--port', '8003', '--no-browser']), 0)
        self.assertEqual(factory.call_args.args[0].get_backend_name(), 'postgresql')
        sock.return_value.__enter__.return_value.bind.assert_called_once_with(('127.0.0.1', 8003))
        thread.assert_not_called()
        server.return_value.run.assert_called_once()

    def test_invalid_port_is_rejected(self):
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
            start_local.main(['--port', '0'])
