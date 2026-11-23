import unittest
from school_pipeline.website_focus import Text, candidates, TAXONOMY


class WebsiteFocusTests(unittest.TestCase):
    def test_multiple_candidates_not_confirmed(self):
        rows = candidates('Vi arbetar med montessoripedagogik och musik.')
        self.assertEqual({r['category'] for r in rows}, {'montessori','music'})
        self.assertTrue(all(r['review_status']=='candidate_needs_review' for r in rows))

    def test_generic_academic_claim_not_category(self):
        self.assertEqual(candidates('Alla elever når goda resultat och utvecklas i skolan.'), [])

    def test_remove_scripts_and_navigation(self):
        parser = Text(); parser.feed('<nav>musik</nav><script>montessori</script><p>Waldorfpedagogik</p>')
        self.assertEqual({r['category'] for r in candidates(parser.text())}, {'waldorf'})

    def test_taxonomy(self):
        self.assertEqual(len(TAXONOMY),9)
