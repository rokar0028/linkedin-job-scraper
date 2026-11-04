import unittest
import os
from src.core.config import Settings


class TestConfig(unittest.TestCase):
    def test_default_settings(self):
        cfg = Settings()
        self.assertIsInstance(cfg.MAX_JOBS, int)
        self.assertIsInstance(cfg.DEFAULT_TIMEOUT, int)
        self.assertIsInstance(cfg.HEADLESS, bool)
        self.assertEqual(cfg.BROWSER, "chromium")


if __name__ == "__main__":
    unittest.main()
