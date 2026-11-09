import unittest
from pathlib import Path


class CsvExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")

    def test_export_is_csv_with_raw_and_clickable_links(self):
        self.assertIn("a.download='fde-progress.csv'", self.html)
        self.assertIn("['Question','Status','URL','Link']", self.html)
        self.assertIn('=HYPERLINK(', self.html)
        self.assertIn("type:'text/csv;charset=utf-8'", self.html)

    def test_export_rejects_non_https_formula_links(self):
        self.assertIn("x.protocol==='https:'", self.html)
        self.assertIn("/^[=+\\-@]/", self.html)


if __name__ == "__main__":
    unittest.main()
