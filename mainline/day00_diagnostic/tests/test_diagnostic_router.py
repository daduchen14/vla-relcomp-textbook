import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from mainline.day00_diagnostic.code.grade_form import grade
from mainline.day00_diagnostic.code.diagnostic_router import initialise, load_manifest, record
from mainline.day00_diagnostic.code.prepare_form import prepare
from shared.answer_keys.day00_reference import solve


class DiagnosticRouterTests(unittest.TestCase):
    def test_manifest_covers_every_foundation_route(self):
        routes = load_manifest()["routes"]
        self.assertEqual([r["id"] for r in routes], [f"F{i:02d}" for i in range(1, 19)])

    def test_init_and_record_preserve_other_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "route.json"
            initialise(output, force=False)
            record(output, "F07", "needs_review")
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["results"]["F07"], "needs_review")
            self.assertEqual(data["results"]["F08"], "untested")

    def test_both_forms_prepare_and_reference_solution_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            for form in ("A", "B"):
                workspace = Path(tmp) / form
                prepare(form, workspace)
                solve(workspace, form)
                result = grade(workspace, form)
                self.assertTrue(result["entry_ready"])
                self.assertEqual(result["recommended_foundations"], [])

    def test_form_a_artifacts_cannot_pass_form_b(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a, b = prepare("A", root / "A"), prepare("B", root / "B")
            solve(a, "A"); solve(b, "B")
            shutil.rmtree(b / "artifacts")
            shutil.copytree(a / "artifacts", b / "artifacts")
            result = grade(b, "B")
            self.assertFalse(result["entry_ready"])
            self.assertFalse(result["tasks"]["task1"])
            self.assertFalse(result["tasks"]["task4"])


if __name__ == "__main__":
    unittest.main()
