#!/usr/bin/env python3
"""按冻结证据顺序从 claim registry 生成有限语言 results draft。"""
import argparse,hashlib,json
from pathlib import Path
ORDER=("denominator","primary","diagnosis","repair","retention","oracle","resources","negative")
BANNED=(" proves "," guarantees "," causes "," universally ")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(input_path,config_path,output_dir):
 if output_dir.exists():raise FileExistsError("results output 已存在")
 data=json.loads(input_path.read_text());cfg=json.loads(config_path.read_text());claims=data["claims"]
 if data["evidence_mode"]!="synthetic" or data["formal_evidence_available"]:raise ValueError("本课只接受 synthetic 教学输入")
 if sorted(c["order"] for c in claims)!=list(range(1,len(claims)+1)):raise ValueError("证据顺序不连续")
 if tuple(c["claim_type"] for c in claims)!=ORDER:raise ValueError("证据顺序必须冻结")
 for c in claims:
  if not c["evidence_ref"] or not c["forbidden_stronger_claim"] or any(t in f" {c['allowed_sentence'].lower()} " for t in BANNED):raise ValueError("主张缺证据/边界或使用越界语言")
 output_dir.mkdir(parents=True);draft=output_dir/"results_draft.md";lines=[f"# {cfg['title']}","","> Evidence status: synthetic teaching results; not VLA-Arena evidence.",""]
 for c in claims:lines.extend([f"## {c['order']}. {c['heading']}","",c["allowed_sentence"],"",f"Evidence: `{c['evidence_ref']}`.","",f"Cannot claim: {c['forbidden_stronger_claim']}",""])
 lines.extend(["## Overall boundary","",data["overall_boundary"],""]);draft.write_text("\n".join(lines))
 m={"source_sha256":sha(input_path),"config_sha256":sha(config_path),"draft_sha256":sha(draft),"claim_types":[c["claim_type"] for c in claims],"claim_count":len(claims),"negative_results_preserved":any(c["claim_type"]=="negative" for c in claims),"all_claims_have_evidence":all(c["evidence_ref"] for c in claims),"all_claims_have_boundaries":all(c["forbidden_stronger_claim"] for c in claims),"formal_results":False};(output_dir/"manifest.json").write_text(json.dumps(m,indent=2)+"\n");return m
def main():
 p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();m=build(a.input,a.config,a.output_dir);print(f"PASS: claims={m['claim_count']} negative_preserved=true formal=false")
if __name__=="__main__":main()
