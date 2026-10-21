import json
import unittest
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from update_questions import extract_payload, normalize_question, replace_dataset


class UpdateQuestionsTests(unittest.TestCase):
    def test_extract_payload_reads_next_data(self):
        payload = {"props": {"pageProps": {"initialQuestions": {"count": 1, "results": [{"id": 7}]}}}}
        html = f'<html><script id="__NEXT_DATA__" type="application/json">{json.dumps(payload)}</script></html>'

        questions = extract_payload(html)

        self.assertEqual(questions["count"], 1)
        self.assertEqual(questions["results"][0]["id"], 7)

    def test_normalize_question_keeps_tracker_schema(self):
        raw = {
            "id": 6455,
            "slug": "design-rag-for-customer",
            "data": {"title": "Design a RAG system."},
            "last_asked_on": "2026-10-15T00:00:00.000Z",
            "category": ["artificial-intelligence", "system-design"],
            "companies": [{"name": "OpenAI"}, {"name": "Google"}],
        }

        result = normalize_question(raw, today=date(2026, 10, 21))

        self.assertEqual(result, {
            "title": "Design a RAG system.",
            "url": "https://www.aced.io/questions/6455/design-rag-for-customer",
            "age": "6 days ago",
            "categories": ["artificial-intelligence", "system-design"],
            "companies": ["OpenAI", "Google"],
        })

    def test_replace_dataset_only_changes_embedded_questions(self):
        html = '<script>const D=[{"title":"old"}],K="tracker";const $=s=>document.querySelector(s)</script>'
        questions = [{"title": "new", "url": "https://example.com", "age": "today", "categories": [], "companies": []}]

        updated = replace_dataset(html, questions)

        self.assertIn('const D=[{"title":"new"', updated)
        self.assertIn('],K="tracker";const $=s=>document.querySelector(s)', updated)
        self.assertNotIn('"old"', updated)


if __name__ == "__main__":
    unittest.main()
