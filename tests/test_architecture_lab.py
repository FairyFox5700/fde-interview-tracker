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

    def test_six_unique_source_grounded_cases(self):
        self.assertEqual(len(self.cases), 6)
        self.assertEqual(len({case["case_id"] for case in self.cases}), 6)
        for case in self.cases:
            self.assertTrue(case["source"]["canonical_url"].startswith("https://"))
            self.assertGreaterEqual(len(case["source_backed_facts"]), 3)
            self.assertGreaterEqual(len(case["adapted_scenario_proposed_additions"]), 2)

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
