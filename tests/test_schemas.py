import unittest
from src.api.schemas import ScrapeRequest, ScrapeResponse
from src.browser.driver import build_search_url


class TestSchemas(unittest.TestCase):
    def test_scrape_request_valid(self):
        req = ScrapeRequest(
            job_title="Software Engineer",
            location="Remote",
            remote="yes",
            date_posted="past_24h",
            experience_level="entry",
            max_jobs=20
        )
        self.assertEqual(req.job_title, "Software Engineer")
        self.assertEqual(req.location, "Remote")
        self.assertEqual(req.remote, "yes")
        self.assertEqual(req.date_posted, "past_24h")
        self.assertEqual(req.experience_level, "entry")
        self.assertEqual(req.max_jobs, 20)

    def test_scrape_request_defaults(self):
        req = ScrapeRequest(job_title="Data Scientist")
        self.assertEqual(req.job_title, "Data Scientist")
        self.assertEqual(req.location, "")
        self.assertEqual(req.remote, "no")
        self.assertIsNone(req.date_posted)
        self.assertIsNone(req.experience_level)
        self.assertIsNone(req.max_jobs)

    def test_build_search_url_filters(self):
        url = build_search_url(
            job_title="AI Engineer",
            location="United States",
            remote="yes",
            date_posted="past_week",
            experience_level="entry"
        )
        self.assertIn("keywords=AI+Engineer", url)
        self.assertIn("location=United+States", url)
        self.assertIn("f_WT=2", url)
        self.assertIn("f_TPR=r604800", url)
        self.assertIn("f_E=2", url)

    def test_scrape_response(self):
        resp = ScrapeResponse(
            status="success",
            jobs_scraped=5,
            jobs_inserted=3,
            duplicates_skipped=2,
            jobs=[{"title": "Dev", "job_url": "https://linkedin.com/jobs/view/123/"}]
        )
        self.assertEqual(resp.status, "success")
        self.assertEqual(resp.jobs_scraped, 5)
        self.assertEqual(resp.jobs_inserted, 3)
        self.assertEqual(len(resp.jobs), 1)


if __name__ == "__main__":
    unittest.main()
