import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from database import postgres_url


class PostgresConfigurationTests(unittest.TestCase):
    def test_sqlite_url_is_not_a_runtime_fallback(self):
        with self.assertRaises(ValueError):
            postgres_url('sqlite:///holo.sqlite3')

    def test_missing_configuration_does_not_create_sqlite(self):
        with TemporaryDirectory() as folder, patch.dict(os.environ, {}, clear=True):
            path = Path(folder) / 'postgres.json'
            with self.assertRaises(ValueError):
                postgres_url(config=path)
            self.assertEqual(list(Path(folder).iterdir()), [])
