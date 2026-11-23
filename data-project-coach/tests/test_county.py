import unittest
from school_pipeline.county import MUNICIPALITIES, validate_manifest


class CountyTests(unittest.TestCase):
    def manifest(self):
        return {'selection': {'schools': [{'code': '12345678'}]}, 'sources': [
            {'code': '12345678', 'kind': kind, 'status': 'FETCHED' if kind == 'register' else 'UNAVAILABLE'}
            for kind in ('register', 'statistics', 'parents', 'pupils')]}

    def test_county_scope(self):
        self.assertEqual(len(set(MUNICIPALITIES)), 26)
        self.assertTrue(all(c.startswith('01') for c in MUNICIPALITIES))

    def test_unavailable_is_explicit_coverage(self):
        validate_manifest(self.manifest())

    def test_failed_or_missing_blocked(self):
        for mode in ('failed', 'missing', 'duplicate', 'register'):
            manifest = self.manifest()
            if mode == 'failed':
                manifest['sources'][1]['status'] = 'FAILED'
            elif mode == 'missing':
                manifest['sources'].pop()
            elif mode == 'duplicate':
                manifest['sources'].append(manifest['sources'][0])
            else:
                manifest['sources'][0]['status'] = 'UNAVAILABLE'
            with self.assertRaises(ValueError):
                validate_manifest(manifest)
