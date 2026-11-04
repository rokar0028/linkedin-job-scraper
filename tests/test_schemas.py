import unittest
from src.api.schemas import ScrapeRequest, ScrapeResponse


class TestSchemas(unittest.TestCase):
    def test_scrape_request_valid(self):
        req = ScrapeRequest(job_title="Software Engineer", location="Remote", remote="yes", max_jobs=20)
        self.assertEqual(req.job_title, "Software Engineer")
        self.assertEqual(req.location, "Remote")
        self.assertEqual(req.remote, "yes")
        self.assertEqual(req.max_jobs, 20)

    def test_scrape_request_defaults(self):
        req = ScrapeRequest(job_title="Data Scientist")
        self.assertEqual(req.job_title, "Data Scientist")
        self.assertEqual(req.location, "")
        self.assertEqual(req.remote, "no")
        self.assertIsNone(req.max_jobs)

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
