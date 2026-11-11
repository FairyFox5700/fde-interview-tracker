import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ArchitectureLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((ROOT / "architectures.json").read_text(encoding="utf-8"))
        cls.cases = cls.document["cases"]
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_seven_unique_source_grounded_cases(self):
        self.assertEqual(len(self.cases), 7)
        self.assertEqual(len({case["case_id"] for case in self.cases}), 7)
        for case in self.cases:
            self.assertTrue(case["source"]["canonical_url"].startswith("https://"))
            self.assertGreaterEqual(len(case["source_backed_facts"]), 3)
            self.assertGreaterEqual(len(case["adapted_scenario_proposed_additions"]), 2)

    def test_secure_code_execution_case_uses_requested_source(self):
        case = next(case for case in self.cases if case["case_id"] == "fde-code-sandbox-07")
        self.assertEqual(case["title"], "Secure Coding Platform and Execution Sandbox")
        self.assertEqual(
            case["source"]["canonical_url"],
            "https://www.hellointerview.com/learn/system-design/problem-breakdowns/leetcode",
        )
        self.assertIn("Azure Container Apps", case["supporting_implementation"]["title"])

    def test_every_case_has_complete_fde_practice_sections(self):
        required_lists = (
            "discovery_questions",
            "requirements_constraints",
            "component_flow",
            "tradeoffs",
            "failure_security_challenges",
            "implementation_plan",
        )
        for case in self.cases:
            self.assertTrue(case["customer_scenario"])
            self.assertTrue(case["spoken_answer_60_seconds"])
            for field in required_lists:
                self.assertGreaterEqual(len(case[field]), 4, f"{case['case_id']} missing {field}")

    def test_index_contains_architecture_lab_and_persistence(self):
        for marker in (
            'id="architectureView"',
            'id="caseList"',
            'id="caseDetail"',
            "fetch('architectures.json')",
            "fdeArchitectureProgress1",
            "Reveal source-backed solution",
            "clusterArchitectureQuestions",
            'id="labQuestionTotal"',
            "safeUrl",
            'aria-label="Search architecture cases"',
        ):
            self.assertIn(marker, self.html)


if __name__ == "__main__":
    unittest.main()
