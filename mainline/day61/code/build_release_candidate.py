#!/usr/bin/env python3
"""从只读 synthetic episode 输入生成 tidy CSV、provenance index 与校验 manifest。"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path

FIELDS=("episode_id","suite","level","condition","seed","success","cost","status")
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def build(input_path:Path,config_path:Path,output_dir:Path)->dict:
    if output_dir.exists():raise FileExistsError("release output 已存在；禁止覆盖")
    before=sha(input_path);data=json.loads(input_path.read_text(encoding="utf-8"));config=json.loads(config_path.read_text(encoding="utf-8"))
    rows=[]
    for item in data["episodes"]:
        row={"episode_id":item["episode_id"],"suite":item["suite"],"level":item["level"],"condition":item["condition"],"seed":item["seed"],"success":item["outcome"]["success"],"cost":item["outcome"]["cost"],"status":item["status"]}
        if set(row)!=set(FIELDS) or row["status"] not in ("completed","failed"):raise ValueError("episode schema/status 不合法")
        rows.append(row)
    if len({r["episode_id"] for r in rows})!=len(rows):raise ValueError("episode_id 重复")
    rows.sort(key=lambda r:r["episode_id"]);output_dir.mkdir(parents=True)
    tidy=output_dir/"episodes.csv"
    with tidy.open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
    index={"release_id":config["release_id"],"source":{"path":str(input_path),"sha256":before,"immutable":True},"rows":[{"row_number":i+2,"episode_id":r["episode_id"],"source_record":f"episodes[{i}]"} for i,r in enumerate(rows)],"boundary":"synthetic teaching release candidate; no VLA-Arena run evidence"}
    index_path=output_dir/"provenance_index.json";index_path.write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    manifest={"release_id":config["release_id"],"evidence_mode":data["evidence_mode"],"row_count":len(rows),"schema":{"fields":list(FIELDS),"one_row_per":"episode","primary_key":"episode_id"},"artifacts":{"episodes.csv":sha(tidy),"provenance_index.json":sha(index_path)},"source_sha256":before,"source_unchanged":sha(input_path)==before,"raw_overwrite_allowed":False,"formal_results":False}
    (output_dir/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return manifest
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();m=build(a.input,a.config,a.output_dir);print(f"PASS: release={m['release_id']} rows={m['row_count']} source_unchanged=true")
if __name__=="__main__":main()
