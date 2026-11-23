"""Native DuckDB regression tests, offline and without Prefect server."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
import duckdb
from school_pipeline.flow import ROOT, load_duckdb
from school_pipeline.duckdb_migration import migrate_backup, merge_records


class DuckDBTests(unittest.TestCase):
    def test_replace_preserves_missing_and_rounded_values(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.state') as tmp:
            db = Path(tmp)/'test.duckdb'
            rows = [{'school_unit_code':'12345678','raw_value':'~100','numeric_value':None,'value_type':'ROUNDED'},
                    {'school_unit_code':'12345678','raw_value':'10,4','numeric_value':10.4,'value_type':'EXISTS'}]
            for _ in range(2):
                self.assertEqual(load_duckdb.fn({'statistics':rows},db,Path(tmp)/'dlt')['status'],'LOADED')
            with duckdb.connect(str(db)) as conn:
                self.assertEqual(conn.execute('SELECT raw_value,numeric_value,value_type FROM main.statistics ORDER BY raw_value').fetchall(),
                                 [('10,4',10.4,'EXISTS'),('~100',None,'ROUNDED')])

    def test_empty_and_approach_replacement_blocked(self):
        for tables in [{}, {'statistics':[]}, {'Approach_codes':[{'a':1}]}]:
            with self.assertRaises(ValueError):
                load_duckdb.fn(tables)

    def test_scope_change_blocked(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.state') as tmp:
            db = Path(tmp)/'test.duckdb'
            with duckdb.connect(str(db)) as conn:
                conn.execute('CREATE TABLE schools (school_unit_code VARCHAR)')
                conn.execute("INSERT INTO schools VALUES ('12345678')")
            with self.assertRaises(ValueError):
                load_duckdb.fn({'schools':[{'school_unit_code':'87654321'}]}, db, Path(tmp)/'dlt')

    def test_sqlite_migration_exact_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.state') as tmp:
            source,target=Path(tmp)/'source.sqlite',Path(tmp)/'target.duckdb'
            with sqlite3.connect(source) as conn:
                conn.execute('CREATE TABLE statistics (school_id TEXT, value REAL, flag TEXT)')
                conn.executemany('INSERT INTO statistics VALUES (?,?,?)',[('00123456',None,'SUPPRESSED'),('00123456',10.4,'EXISTS')])
            result=migrate_backup(source,target)
            self.assertTrue(result['statistics']['exact_values_match'])
            with self.assertRaises(FileExistsError):
                migrate_backup(source,target)

    def test_reconcile_idempotent_and_conflicts_blocked(self):
        a={'id':'a','value':1}
        self.assertEqual(merge_records([a],[a],'id'),[a])
        with self.assertRaises(ValueError):
            merge_records([a],[{'id':'a','value':2}],'id')


if __name__=='__main__':
    unittest.main()
