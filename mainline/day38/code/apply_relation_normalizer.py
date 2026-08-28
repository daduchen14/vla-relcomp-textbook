#!/usr/bin/env python3
"""批量应用单一 relation normalizer 并记录输入/输出身份。"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
try:from .relation_normalizer import MODULE_VERSION,normalize_relation_instruction
except ImportError:from relation_normalizer import MODULE_VERSION,normalize_relation_instruction
INPUT=("sample_id","level","target_object_id","start_relation","start_reference_ids","goal_relation","goal_reference_ids","raw_instruction","source_kind");OUTPUT=INPUT+("normalized_instruction","module_version","input_row_sha256")
def analyze(path:Path):
    with path.open(encoding="utf-8",newline="") as handle:reader=csv.DictReader(handle);raw=list(reader);fields=tuple(reader.fieldnames or ())
    if fields!=INPUT or not raw:raise ValueError("input schema/rows 非法")
    output=[];seen=set()
    for row in raw:
        if row["sample_id"] in seen or not row["source_kind"].startswith("synthetic_relation_module_"):raise ValueError("sample/source boundary 非法")
        seen.add(row["sample_id"]);before=dict(row);normalized=normalize_relation_instruction(row)
        if row!=before:raise ValueError("module 修改了输入")
        digest=hashlib.sha256("\x1f".join(row[key] for key in INPUT).encode()).hexdigest();output.append({**row,"normalized_instruction":normalized,"module_version":MODULE_VERSION,"input_row_sha256":digest})
    report={"row_count":len(output),"module_version":MODULE_VERSION,"input_levels":[0],"input_mutation_count":0,"unknown_relation_count":0,"changed_component":"instruction normalization only","upstream_files_modified":False,"model_or_gpu_run":False,"boundary":"synthetic L0 labels; deterministic module regression, not trained-model evidence"}
    return output,report
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:writer=csv.DictWriter(handle,fieldnames=OUTPUT);writer.writeheader();writer.writerows(rows)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();rows,report=analyze(a.input);write(a.output,rows);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: rows={len(rows)} module={report['module_version']} upstream_modified=false model_run=false")
if __name__=="__main__":main()
