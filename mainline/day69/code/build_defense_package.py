#!/usr/bin/env python3
"""从冻结 talk spec 生成 10 分钟 slides、逐页口述稿和 Q&A。"""
import argparse,hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(input_path,config_path,output_dir):
 if output_dir.exists():raise FileExistsError("defense output 已存在")
 d=json.loads(input_path.read_text());cfg=json.loads(config_path.read_text());slides=d["slides"];qa=d["qa"]
 if sum(s["seconds"] for s in slides)!=600 or len(slides)<7:raise ValueError("必须是至少 7 页、恰好 600 秒")
 if any(not s["assertion_title"] or not s["visual"] or not s["evidence"] or not s["boundary"] for s in slides):raise ValueError("slide 消息/证据/边界不完整")
 if len(qa)<10 or any(not q["question"] or not q["short_answer"] or not q["evidence"] or not q["cannot_claim"] for q in qa):raise ValueError("Q&A 不完整")
 output_dir.mkdir(parents=True);deck=output_dir/"slides.md";oral=output_dir/"oral_script.md";qpath=output_dir/"qa.md"
 deck_lines=[f"# {cfg['title']}","","> Synthetic teaching defense; no formal VLA-Arena results.",""]
 oral_lines=["# 10-minute oral script",""];elapsed=0
 for i,s in enumerate(slides,1):
  deck_lines.extend([f"## {i}. {s['assertion_title']}","",f"- Visual: {s['visual']}",f"- Evidence: {s['evidence']}",f"- Boundary: {s['boundary']}",f"- Time: {s['seconds']} s",""])
  oral_lines.extend([f"## {elapsed:03d}–{elapsed+s['seconds']:03d}s | Slide {i}","",s["script"],"",f"Boundary sentence: {s['boundary']}",""]);elapsed+=s["seconds"]
 deck.write_text("\n".join(deck_lines));oral.write_text("\n".join(oral_lines));qpath.write_text("# Q&A bank\n\n"+"\n\n".join(f"## Q{i}. {q['question']}\n\nShort answer: {q['short_answer']}\n\nEvidence: `{q['evidence']}`\n\nCannot claim: {q['cannot_claim']}" for i,q in enumerate(qa,1))+"\n")
 m={"source_sha256":sha(input_path),"config_sha256":sha(config_path),"artifacts":{"slides.md":sha(deck),"oral_script.md":sha(oral),"qa.md":sha(qpath)},"slide_count":len(slides),"total_seconds":600,"qa_count":len(qa),"all_titles_assertions":True,"all_slides_bounded":True,"formal_defense":False};(output_dir/"manifest.json").write_text(json.dumps(m,indent=2)+"\n");return m
def main():
 p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();m=build(a.input,a.config,a.output_dir);print(f"PASS: slides={m['slide_count']} seconds=600 qa={m['qa_count']} formal=false")
if __name__=="__main__":main()
