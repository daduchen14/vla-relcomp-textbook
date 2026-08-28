"""Day 43 免费 CPU pilot 测试。"""
import json,tempfile,unittest
from pathlib import Path
from mainline.day43.code.run_cpu_training_pilot import run
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"shared/fixtures/day43_pilot_a.json";CA=ROOT/"mainline/day43/config/pilot_config_a.json";B=ROOT/"shared/fixtures/day43_pilot_b.json";CB=ROOT/"mainline/day43/config/pilot_config_b.json"
def paths(root,prefix):return root/f"{prefix}.csv",root/f"{prefix}.pt",root/f"{prefix}.json"
class Day43Tests(unittest.TestCase):
    def test_interruption_writes_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            log,ckpt,report=paths(Path(tmp),"a");result,_=run(A,CA,log,ckpt,report,18,False);self.assertEqual(result["status"],"interrupted");self.assertTrue(ckpt.is_file())
    def test_resume_matches_uninterrupted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);log,ckpt,report=paths(root,"split");run(A,CA,log,ckpt,report,18,False);resumed,rows=run(A,CA,log,ckpt,report,None,True);full,full_rows=run(A,CA,*paths(root,"full"));self.assertEqual((resumed["final_step"],resumed["adapter_sha256"],rows),(full["final_step"],full["adapter_sha256"],full_rows))
    def test_a_early_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            result,_=run(A,CA,*paths(Path(tmp),"a"));self.assertTrue(result["early_stopped"]);self.assertLess(result["final_step"],result["max_steps"])
    def test_frozen_modules_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:self.assertTrue(run(A,CA,*paths(Path(tmp),"a"))[0]["frozen_hashes_unchanged"])
    def test_b_is_new_and_early_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            left,_=run(A,CA,*paths(Path(tmp),"a"));right,_=run(B,CB,*paths(Path(tmp),"b"));self.assertTrue(right["early_stopped"]);self.assertNotEqual(left["input_sha256"],right["input_sha256"])
if __name__=="__main__":unittest.main()
