#!/usr/bin/env python3
"""从结构化 dossier 生成含限制、伦理和负结果的完整教学报告。"""
import argparse,hashlib,json
from pathlib import Path
SECTIONS=("Abstract","Problem and contribution","Methods","Results","Related work","Limitations","Ethics and safety","Negative results","Reproducibility","Conclusion","References")
REQUIRED={"Limitations":("simulator","checkpoint","task suite","statistical uncertainty","physical robot"),"Ethics and safety":("safety","misuse","resource","license","privacy"),"Negative results":("negative","inconclusive","not equivalence","stopping rule")}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(input_path,config_path,output_dir):
 if output_dir.exists():raise FileExistsError("report output 已存在")
 d=json.loads(input_path.read_text());cfg=json.loads(config_path.read_text())
 if d["evidence_mode"]!="synthetic" or d["formal_evidence_available"]:raise ValueError("证据边界不合法")
 if tuple(d["sections"][:10])!=SECTIONS[:10]:raise ValueError("报告章节顺序错误")
 body=d["content"]
 for section,tokens in REQUIRED.items():
  low=body[section].lower()
  if not all(t in low for t in tokens):raise ValueError(f"{section} 缺必要边界")
 if not d["references"] or any(not r.get("label") or not r.get("url") for r in d["references"]):raise ValueError("references 不完整")
 output_dir.mkdir(parents=True);report=output_dir/"complete_report.md";lines=[f"# {cfg['title']}","","> SYNTHETIC TEACHING DRAFT — not a report of executed VLA-Arena experiments.",""]
 for section in SECTIONS[:-1]:lines.extend([f"## {section}","",body[section],""])
 lines.extend(["## References",""]+[f"- [{r['label']}]({r['url']}) — {r['role']}" for r in d["references"]]+[""]);report.write_text("\n".join(lines))
 m={"source_sha256":sha(input_path),"config_sha256":sha(config_path),"report_sha256":sha(report),"sections":list(SECTIONS),"limitation_dimensions":len(REQUIRED["Limitations"]),"ethics_dimensions":len(REQUIRED["Ethics and safety"]),"negative_results_present":True,"references_count":len(d["references"]),"formal_report":False};(output_dir/"manifest.json").write_text(json.dumps(m,indent=2)+"\n");return m
def main():
 p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();m=build(a.input,a.config,a.output_dir);print(f"PASS: sections={len(m['sections'])} limitations={m['limitation_dimensions']} ethics={m['ethics_dimensions']} formal=false")
if __name__=="__main__":main()
