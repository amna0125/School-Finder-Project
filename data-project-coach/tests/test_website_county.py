import unittest
from school_pipeline.website_county import relevant_links, NoRedirect


class CountyWebsiteTests(unittest.TestCase):
    def test_scope_deep_listing(self):
        links,_=relevant_links('https://example.se/schools/a','<a href="/schools/b/profil">B</a><a href="/schools/a/pedagogik">A</a>')
        self.assertEqual(links,['https://example.se/schools/a/pedagogik'])

    def test_terms_flagged(self):
        links,terms=relevant_links('https://example.se/','<a href="/terms-of-use">Terms</a><a href="/profil">Profile</a>')
        self.assertEqual(len(terms),1)
        self.assertEqual(len(links),1)

    def test_external_links_excluded(self):
        links,_=relevant_links('https://example.se/','<a href="https://other.se/profil">x</a>')
        self.assertEqual(links,[])

    def test_redirect_not_automatic(self):
        self.assertIsNone(NoRedirect().redirect_request(None,None,301,'',{},'https://other.se'))
