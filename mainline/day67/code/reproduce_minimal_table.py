#!/usr/bin/env python3
"""仅用标准库从冻结 CSV 重建最小表与可比较 reproduction log。"""
import argparse,csv,hashlib,json,platform
from collections import defaultdict
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reproduce(input_path,expected_path,output_dir):
 if output_dir.exists():raise FileExistsError("reproduction output 已存在")
 with input_path.open(encoding="utf-8") as h:rows=list(csv.DictReader(h))
 groups=defaultdict(lambda:{"successes":0,"n":0})
 for r in rows:
  g=groups[r["condition"]];g["n"]+=1;g["successes"]+=r["success"].lower()=="true"
 table={k:{**v,"rate":v["successes"]/v["n"]} for k,v in sorted(groups.items())};expected=json.loads(expected_path.read_text())
 if table!=expected:raise ValueError(f"重建值与 expected 不符: {table}")
 output_dir.mkdir(parents=True);table_path=output_dir/"minimal_table.json";table_path.write_text(json.dumps(table,indent=2,sort_keys=True)+"\n")
 log={"status":"PASS","python":platform.python_version(),"standard_library_only":True,"input_sha256":sha(input_path),"expected_sha256":sha(expected_path),"script_sha256":sha(Path(__file__)),"table_sha256":sha(table_path),"row_count":len(rows),"cache_used":False,"gpu_used":False,"vla_arena_used":False,"boundary":"free CPU reproduction of synthetic table only"};(output_dir/"reproduction_log.json").write_text(json.dumps(log,indent=2,sort_keys=True)+"\n");return log
def main():
 p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--expected",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();log=reproduce(a.input,a.expected,a.output_dir);print(f"PASS: rows={log['row_count']} cache=false gpu=false")
if __name__=="__main__":main()
