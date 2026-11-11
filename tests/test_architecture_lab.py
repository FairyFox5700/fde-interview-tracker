import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ArchitectureLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((ROOT / "architectures.json").read_text(encoding="utf-8"))
        cls.cases = cls.document["cases"]
        cls.diagrams = json.loads((ROOT / "diagrams.json").read_text(encoding="utf-8"))["diagrams"]
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_twelve_unique_source_grounded_cases(self):
        self.assertEqual(len(self.cases), 12)
        self.assertEqual(len({case["case_id"] for case in self.cases}), 12)
        for case in self.cases:
            self.assertTrue(case["source"]["canonical_url"].startswith("https://"))
            if case.get("supporting_implementation"):
                self.assertTrue(
                    case["supporting_implementation"]["canonical_url"].startswith("https://")
                )
            self.assertGreaterEqual(len(case["source_backed_facts"]), 3)
            self.assertGreaterEqual(len(case["adapted_scenario_proposed_additions"]), 2)

    def test_every_current_system_design_question_has_exactly_one_case(self):
        match = re.search(r"const D=(\[.*?\]),K=", self.html, re.DOTALL)
        if match is None:
            self.fail("embedded question dataset not found")
        questions = json.loads(match.group(1))
        system_design = {
            question["url"]: question
            for question in questions
            if "system-design" in question["categories"]
        }
        case_questions = {case["source_question"]["url"]: case for case in self.cases}
        self.assertEqual(set(case_questions), set(system_design))
        for url, question in system_design.items():
            self.assertEqual(case_questions[url]["source_question"]["title"], question["title"])

    def test_every_case_has_complete_hello_interview_sections(self):
        required_lists = (
            "discovery_questions",
            "functional_requirements",
            "non_functional_requirements",
            "core_entities",
            "api_interface",
            "component_flow",
            "tradeoffs",
            "failure_security_challenges",
            "deep_dives",
            "implementation_plan",
        )
        for case in self.cases:
            self.assertTrue(case["customer_scenario"])
            self.assertTrue(case["spoken_answer_60_seconds"])
            self.assertTrue(case["level_expectations"]["mid_level"])
            self.assertTrue(case["level_expectations"]["senior"])
            for field in required_lists:
                self.assertGreaterEqual(len(case[field]), 4, f"{case['case_id']} missing {field}")

    def test_every_case_has_a_valid_architecture_diagram(self):
        self.assertEqual(
            {diagram["case_id"] for diagram in self.diagrams},
            {case["case_id"] for case in self.cases},
        )
        valid_types = {"client", "service", "data", "queue", "security", "external"}
        for diagram in self.diagrams:
            nodes = diagram["nodes"]
            node_ids = {node["id"] for node in nodes}
            self.assertEqual(len(nodes), len(node_ids), diagram["case_id"])
            self.assertGreaterEqual(len(nodes), 5, diagram["case_id"])
            self.assertGreaterEqual(len(diagram["edges"]), 4, diagram["case_id"])
            for node in nodes:
                self.assertIn(node["type"], valid_types)
                self.assertGreaterEqual(node["col"], 0)
                self.assertGreaterEqual(node["row"], 0)
            for edge in diagram["edges"]:
                self.assertIn(edge["from"], node_ids)
                self.assertIn(edge["to"], node_ids)

    def test_index_contains_architecture_lab_and_persistence(self):
        for marker in (
            'id="architectureView"',
            'id="caseList"',
            'id="caseDetail"',
            "fetch('architectures.json')",
            "fetch('diagrams.json')",
            "renderArchitectureDiagram",
            'class="architecture-diagram"',
            "fdeArchitectureProgress1",
            "Reveal source-backed solution",
            "clusterArchitectureQuestions",
            'id="labQuestionTotal"',
            "safeUrl",
            'aria-label="Search architecture cases"',
            "Understanding the problem",
            "Functional requirements",
            "Non-functional requirements",
            "Core entities",
            "API / system interface",
            "High-level design",
            "Potential deep dives",
            "What is expected at each level?",
        ):
            self.assertIn(marker, self.html)


if __name__ == "__main__":
    unittest.main()
