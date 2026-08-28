import tempfile,unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from mainline.day63.code.generate_paper_figures import build
ROOT=Path(__file__).resolve().parents[3]
class Day63Tests(unittest.TestCase):
 def make(self,s):t=tempfile.TemporaryDirectory();o=Path(t.name)/"o";m=build(ROOT/f"shared/fixtures/day63_figure_{s}.json",ROOT/f"mainline/day63/config/figure_{s}.json",o);return t,o,m
 def test_svg_valid(self):t,o,m=self.make("a");ET.parse(o/"paper_figures.svg");t.cleanup()
 def test_three_panels(self):t,o,m=self.make("a");self.assertEqual(m["panels"],3);t.cleanup()
 def test_axis(self):t,o,m=self.make("a");self.assertEqual(m["axis"],{"min":0.0,"max":1.0});t.cleanup()
 def test_denominators(self):t,o,m=self.make("b");self.assertTrue(m["denominators_visible"]);t.cleanup()
 def test_not_formal(self):t,o,m=self.make("b");self.assertFalse(m["formal_results"]);t.cleanup()
if __name__=="__main__":unittest.main()
