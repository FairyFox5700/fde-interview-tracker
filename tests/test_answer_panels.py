import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANSWER_TYPES = {"ai", "behavioral", "coding", "design"}


def is_target_question(question: dict) -> bool:
    categories = " ".join(question["categories"])
    return bool(
        re.search(
            r"design|decomposition|technical|artificial|machine|coding|debugging|sql|behavioral|customer|cross",
            categories,
        )
    )


def tracker_questions(html: str) -> list[dict]:
    match = re.search(r"const D=(\[.*?\]),K=", html, re.DOTALL)
    if match is None:
        raise AssertionError("embedded question dataset not found")
    return json.loads(match.group(1))


class AnswerPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.questions = tracker_questions(cls.html)
        cls.document = json.loads((ROOT / "answers.json").read_text(encoding="utf-8"))
        cls.answers = cls.document["answers"]
        cls.architectures = json.loads(
            (ROOT / "architectures.json").read_text(encoding="utf-8")
        )["cases"]

    def test_answer_file_has_versioned_safe_schema(self):
        self.assertEqual(self.document["schema_version"], 1)
        self.assertEqual(set(self.document["fallbacks"]), ANSWER_TYPES)
        urls = [answer["question_url"] for answer in self.answers]
        self.assertEqual(len(urls), len(set(urls)))
        for answer in self.answers:
            self.assertTrue(answer["question_url"].startswith("https://"))
            self.assertIn(answer["type"], ANSWER_TYPES)
            self.assertTrue(answer["answer"])
            self.assertTrue(answer["key_points"])
            self.assertTrue(answer["follow_ups"])
            self.assertNotIn("<script", answer["answer"].lower())

    def test_every_current_target_question_resolves_to_an_answer(self):
        answers_by_url = {answer["question_url"]: answer for answer in self.answers}
        cases_by_url = {case["source_question"]["url"]: case for case in self.architectures}
        target_questions = [
            question for question in self.questions if is_target_question(question)
        ]
        self.assertGreater(len(target_questions), 0)
        for question in target_questions:
            self.assertTrue(
                question["url"] in answers_by_url or question["url"] in cases_by_url,
                question["title"],
            )

    def test_system_design_reuses_architecture_cases(self):
        case_urls = {case["source_question"]["url"] for case in self.architectures}
        answer_urls = {answer["question_url"] for answer in self.answers}
        self.assertTrue(case_urls)
        self.assertFalse(case_urls.intersection(answer_urls))
        self.assertIn("x.title||x.question||x.details||String(x)", self.html)

    def test_disclosure_accessible_name_includes_question_title(self):
        self.assertIn("Reveal ${E(label)} answer for ${E(r.title)}", self.html)

    def test_refresh_validates_coverage_after_updating_dataset(self):
        workflow = (ROOT / ".github" / "workflows" / "refresh-questions.yml").read_text(
            encoding="utf-8"
        )
        refresh = workflow.index("python scripts/update_questions.py")
        tests = workflow.index("python -m unittest discover -s tests -v")
        commit = workflow.index("git commit")
        self.assertLess(refresh, tests)
        self.assertLess(tests, commit)

    def test_index_contains_accessible_answer_disclosures(self):
        for marker in (
            "fetch('answers.json')",
            'class="answer-panel"',
            "<details",
            "<summary",
            'aria-live="polite"',
            "renderAnswerPanel",
            "Continue in Architecture Lab",
            "Open original question:",
            "Mark “",
        ):
            self.assertIn(marker, self.html)

    def test_answer_rendering_escapes_content_and_rejects_unsafe_urls(self):
        for marker in (
            "E(answer.answer)",
            "answer.key_points.map(x=>`<li>${E(x)}</li>`)",
            "answer.follow_ups.map(x=>`<li>${E(x)}</li>`)",
            "safeUrl(r.url)",
        ):
            self.assertIn(marker, self.html)


if __name__ == "__main__":
    unittest.main()
