import json
import tempfile
import unittest
from pathlib import Path

from mainline.day00_diagnostic.code.diagnostic_router import initialise, load_manifest, record


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


if __name__ == "__main__":
    unittest.main()
