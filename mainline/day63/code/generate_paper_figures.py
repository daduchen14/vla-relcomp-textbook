#!/usr/bin/env python3
"""从冻结 synthetic spec 生成三面板、可审计 SVG 论文图。"""
import argparse,hashlib,html,json
from pathlib import Path
from xml.etree import ElementTree as ET
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(x,y,s,size=12,anchor="middle"):return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="#222">{html.escape(str(s))}</text>'
def build(input_path,config_path,output_dir):
 if output_dir.exists():raise FileExistsError("figure output 已存在")
 data=json.loads(input_path.read_text());cfg=json.loads(config_path.read_text());axis=cfg["proportion_axis"]
 if axis!={"min":0.0,"max":1.0}:raise ValueError("比例轴必须冻结为 0–1")
 output_dir.mkdir(parents=True);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400">','<rect width="960" height="400" fill="white"/>']
 panels=[("A  Stage funnel",data["funnel"]),("B  Paired transitions",data["pairs"]),("C  Intervention",data["intervention"])]
 for panel,(title,items) in enumerate(panels):
  x0=20+panel*315;svg.append(text(x0+145,28,title,15));svg.append(f'<line x1="{x0+45}" y1="330" x2="{x0+290}" y2="330" stroke="#222"/>');svg.append(f'<line x1="{x0+45}" y1="60" x2="{x0+45}" y2="330" stroke="#222"/>');svg.append(text(x0+38,64,"1.0",10,"end"));svg.append(text(x0+38,334,"0",10,"end"))
  for i,item in enumerate(items):
   for key in ("rate","low","high"):
    if not 0<=item[key]<=1:raise ValueError("rate/interval 超界")
   if not item["low"]<=item["rate"]<=item["high"]:raise ValueError("interval 顺序错误")
   x=x0+68+i*70;y=330-270*item["rate"];lo=330-270*item["low"];hi=330-270*item["high"];color=cfg["palette"][i%len(cfg["palette"])]
   svg.append(f'<rect x="{x}" y="{y:.1f}" width="38" height="{330-y:.1f}" fill="{color}" opacity="0.82"/>');svg.append(f'<line x1="{x+19}" y1="{hi:.1f}" x2="{x+19}" y2="{lo:.1f}" stroke="#111"/><line x1="{x+12}" y1="{hi:.1f}" x2="{x+26}" y2="{hi:.1f}" stroke="#111"/><line x1="{x+12}" y1="{lo:.1f}" x2="{x+26}" y2="{lo:.1f}" stroke="#111"/>');svg.append(text(x+19,y-8,f"{item['rate']:.2f}",10));svg.append(text(x+19,348,item["label"],9));svg.append(text(x+19,362,f"n={item['n']}",9))
 svg.extend([text(480,390,"Synthetic teaching data — 95% Wilson intervals; not VLA-Arena results",12),'</svg>']);path=output_dir/"paper_figures.svg";path.write_text("\n".join(svg)+"\n");ET.parse(path)
 caption=output_dir/"caption.md";caption.write_text("Figure 1. Synthetic stage funnel, paired transitions, and intervention summaries. Bars show observed proportions; whiskers show 95% Wilson intervals; labels report episode denominators. The y-axis is fixed at 0–1. These panels validate rendering only and are not VLA-Arena results.\n")
 m={"source_sha256":sha(input_path),"config_sha256":sha(config_path),"artifacts":{"paper_figures.svg":sha(path),"caption.md":sha(caption)},"panels":3,"axis":axis,"interval":"95% Wilson","denominators_visible":True,"color_alone":False,"formal_results":False};(output_dir/"manifest.json").write_text(json.dumps(m,indent=2)+"\n");return m
def main():
 p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();m=build(a.input,a.config,a.output_dir);print(f"PASS: panels={m['panels']} axis=0..1 formal=false")
if __name__=="__main__":main()
