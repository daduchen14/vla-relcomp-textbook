import tempfile
import unittest
from pathlib import Path

from mainline.day05.code.build_interface_card import build_card
from mainline.day05.code.trace_adapter import INPUT_KEYS

ROOT = Path(__file__).resolve().parents[3]


class Day05ToolTests(unittest.TestCase):
    def test_example_contract_has_batch_channel_first_images(self):
        card = build_card(ROOT / "shared/fixtures/day05_interface_a.json")
        self.assertEqual(card["inputs"]["observation.images.image"]["shape"], [1, 3, 2, 3])
        self.assertEqual(card["inputs"]["observation.state"]["shape"], [1, 8])
        self.assertEqual(card["action"]["shape"], [1, 7])

    def test_challenge_changes_shapes_and_task(self):
        a = build_card(ROOT / "shared/fixtures/day05_interface_a.json")
        b = build_card(ROOT / "shared/fixtures/day05_interface_b.json")
        self.assertNotEqual(a["inputs"], b["inputs"])
        self.assertNotEqual(a["task"], b["task"])

    def test_missing_raw_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"form_id":"x","task":"x","raw":{}}')
            with self.assertRaisesRegex(ValueError, "key"):
                build_card(path)

    def test_locked_input_key_list_is_explicit(self):
        self.assertEqual(INPUT_KEYS[-1], "task")
        self.assertEqual(len(INPUT_KEYS), 4)


if __name__ == "__main__":
    unittest.main()
