"""Local destination regression tests; no network or Prefect server required."""
import sqlite3
from pathlib import Path
import tempfile
import unittest
from school_pipeline.flow import ROOT, load_sqlite


class SQLiteTests(unittest.TestCase):
    def test_replace_preserves_values(self):
        (ROOT / '.state').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / '.state') as tmp:
            database = Path(tmp) / 'test.sqlite'
            tables = {'statistics': [
                {'school_unit_code': '12345678', 'raw_value': '~100',
                 'numeric_value': None, 'value_type': 'ROUNDED'},
                {'school_unit_code': '12345678', 'raw_value': '10,4',
                 'numeric_value': 10.4, 'value_type': 'EXISTS'}]}
            for _ in range(2):
                result = load_sqlite.fn(tables, database, Path(tmp) / 'dlt')
                self.assertEqual(result['status'], 'LOADED')
            with sqlite3.connect(database) as conn:
                names = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
                name = next(n for n in names if n.endswith('statistics'))
                rows = conn.execute(f'SELECT raw_value, numeric_value, value_type FROM "{name}" ORDER BY raw_value').fetchall()
                self.assertEqual(rows, [('10,4', 10.4, 'EXISTS'), ('~100', None, 'ROUNDED')])

    def test_empty_replacement_blocked(self):
        with self.assertRaises(ValueError):
            load_sqlite.fn({'statistics': []})


if __name__ == '__main__':
    unittest.main()
