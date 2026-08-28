#!/usr/bin/env python3
"""从 tidy synthetic episodes 生成带 counts、Wilson 区间和冻结加粗规则的论文表。"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wilson(k,n,z=1.959963984540054):
    p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;m=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return c-m,c+m
def build(input_path,config_path,output_dir):
    if output_dir.exists():raise FileExistsError("table output 已存在")
    cfg=json.loads(config_path.read_text())
    with input_path.open(encoding="utf-8") as handle:rows=list(csv.DictReader(handle))
    groups=defaultdict(list)
    for r in rows:groups[(int(r["level"]),r["condition"])].append(r)
    stats=[]
    for (level,condition),items in sorted(groups.items()):
        k=sum(r["success"].lower()=="true" for r in items);n=len(items);lo,hi=wilson(k,n);stats.append({"level":level,"condition":condition,"successes":k,"n":n,"rate":k/n,"wilson_low":lo,"wilson_high":hi})
    winners={level:max((r for r in stats if r["level"]==level),key=lambda r:(r["rate"],r["condition"])) ["condition"] for level in {r["level"] for r in stats}}
    output_dir.mkdir(parents=True);csv_path=output_dir/"table.csv"
    with csv_path.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=stats[0]);w.writeheader();w.writerows(stats)
    lines=["# Synthetic success table","",cfg["caption"],"","| Level | Condition | Successes / n | Rate (95% Wilson CI) |","|---:|---|---:|---:|"]
    for r in stats:
        value=f"{r['rate']:.3f} [{r['wilson_low']:.3f}, {r['wilson_high']:.3f}]";value=f"**{value}**" if r["condition"]==winners[r["level"]] else value;lines.append(f"| {r['level']} | {r['condition']} | {r['successes']} / {r['n']} | {value} |")
    lines.extend(["",f"加粗规则：{cfg['bold_rule']}；只作描述，不表示显著性。", "", "证据边界：synthetic teaching data；不能当作 VLA-Arena 结果。"]);md=output_dir/"table.md";md.write_text("\n".join(lines)+"\n",encoding="utf-8")
    manifest={"source_sha256":sha(input_path),"config_sha256":sha(config_path),"row_count":len(rows),"group_count":len(stats),"artifacts":{"table.csv":sha(csv_path),"table.md":sha(md)},"counts_reported":True,"interval":"95% Wilson","bold_rule":cfg["bold_rule"],"formal_results":False};(output_dir/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n");return manifest
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();m=build(a.input,a.config,a.output_dir);print(f"PASS: groups={m['group_count']} interval={m['interval']} formal=false")
if __name__=="__main__":main()
