#!/usr/bin/env python3
"""分析双指接触、支撑脱离、持续抬升，并生成阈值敏感性 SVG。"""

from __future__ import annotations
import argparse, csv, json, math
from collections import Counter
from pathlib import Path

SUMMARY_FIELDS=("episode_id","step_count","baseline_z_m","max_height_gain_m","first_bilateral_contact_step","first_lift_step","lift_detected","bilateral_contact_detected","grasp_then_lift","support_released_at_lift","probe_status")
SENSITIVITY_FIELDS=("episode_id","threshold_m","sustained_steps","lift_detected","first_lift_step")

def bit(value: str, name: str) -> bool:
    if value not in {"0","1"}: raise ValueError(f"{name} 必须为 0/1")
    return value=="1"

def first_sustained(gains: list[float], supported: list[bool], threshold: float, length: int) -> int|None:
    # 高度和“已离开原支撑面”必须在同一连续窗口内同时成立。
    run=0
    for step,(gain,on_support) in enumerate(zip(gains,supported)):
        run=run+1 if gain>=threshold and not on_support else 0
        if run==length: return step-length+1
    return None

def render_svg(rows: list[dict], episode_count: int) -> str:
    # 直接从敏感性 CSV 的语义行生成 SVG，避免图与数据由两套逻辑计算。
    thresholds=sorted({float(row["threshold_m"]) for row in rows}); counts=[sum(row["lift_detected"]=="true" and float(row["threshold_m"])==threshold for row in rows) for threshold in thresholds]
    points=[]
    for index,count in enumerate(counts):
        x=60+(300*index/(len(counts)-1) if len(counts)>1 else 150); y=220-160*count/episode_count; points.append(f"{x:.1f},{y:.1f}")
    labels="".join(f'<text x="{60+(300*i/(len(thresholds)-1) if len(thresholds)>1 else 150):.1f}" y="245" text-anchor="middle">{value:.3f}</text>' for i,value in enumerate(thresholds))
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="420" height="280" viewBox="0 0 420 280">\n'
            '<rect width="100%" height="100%" fill="white"/><text x="210" y="24" text-anchor="middle">Lift threshold sensitivity (synthetic)</text>\n'
            '<line x1="60" y1="220" x2="370" y2="220" stroke="black"/><line x1="60" y1="50" x2="60" y2="220" stroke="black"/>\n'
            f'<polyline points="{" ".join(points)}" fill="none" stroke="#1f77b4" stroke-width="3"/>{labels}\n'
            '<text x="210" y="270" text-anchor="middle">height threshold (m)</text><text x="14" y="140" transform="rotate(-90 14 140)" text-anchor="middle">detected episodes</text>\n</svg>\n')

def analyze(trace_path: Path, config_path: Path):
    with trace_path.open(encoding="utf-8",newline="") as handle: raw=list(csv.DictReader(handle))
    config=json.loads(config_path.read_text(encoding="utf-8")); primary=float(config["primary_lift_threshold_m"]); length=int(config["sustained_lift_steps"]); thresholds=[float(v) for v in config["sensitivity_thresholds_m"]]; source=config.get("source_kind","")
    if primary<=0 or length<=0 or thresholds!=sorted(set(thresholds)) or primary not in thresholds or not source.startswith("synthetic_lift_"): raise ValueError("lift config 非法或缺 synthetic boundary")
    groups={}
    for row in raw:
        if not row.get("episode_id"): raise ValueError("episode_id 不能为空")
        groups.setdefault(row["episode_id"],[]).append(row)
    if not groups: raise ValueError("trace 不能为空")
    summaries=[]; sensitivity=[]
    for episode_id,rows in sorted(groups.items()):
        rows.sort(key=lambda row:int(row["step"])); steps=[int(row["step"]) for row in rows]
        if steps!=list(range(len(rows))): raise ValueError("step 必须从 0 连续")
        z=[float(row["target_z_m"]) for row in rows]
        if any(not math.isfinite(v) for v in z): raise ValueError("target_z_m 必须有限")
        left=[bit(row["left_target_contact"],"left_target_contact") for row in rows]; right=[bit(row["right_target_contact"],"right_target_contact") for row in rows]; supported=[bit(row["support_contact"],"support_contact") for row in rows]
        # baseline 是同 episode 的 step 0；不跨物体比较绝对世界坐标 z。
        gains=[value-z[0] for value in z]; first_bilateral=next((i for i,(a,b) in enumerate(zip(left,right)) if a and b),None); first_lift=first_sustained(gains,supported,primary,length)
        lifted=first_lift is not None; bilateral=first_bilateral is not None; ordered=lifted and bilateral and first_bilateral<=first_lift
        if ordered: status="GRASP_AND_LIFT"
        elif lifted: status="LIFT_WITHOUT_BILATERAL_CONTACT"
        elif bilateral: status="BILATERAL_NO_LIFT"
        elif any(a or b for a,b in zip(left,right)): status="ONE_SIDED_CONTACT_ONLY"
        else: status="NO_GRASP_OR_LIFT"
        summaries.append({"episode_id":episode_id,"step_count":len(rows),"baseline_z_m":f"{z[0]:.6f}","max_height_gain_m":f"{max(gains):.6f}","first_bilateral_contact_step":"" if first_bilateral is None else first_bilateral,"first_lift_step":"" if first_lift is None else first_lift,"lift_detected":str(lifted).lower(),"bilateral_contact_detected":str(bilateral).lower(),"grasp_then_lift":str(ordered).lower(),"support_released_at_lift":str(lifted and not supported[first_lift]).lower(),"probe_status":status})
        for threshold in thresholds:
            step=first_sustained(gains,supported,threshold,length); sensitivity.append({"episode_id":episode_id,"threshold_m":f"{threshold:.6f}","sustained_steps":length,"lift_detected":str(step is not None).lower(),"first_lift_step":"" if step is None else step})
    counts=Counter(row["probe_status"] for row in summaries); report={"episode_count":len(summaries),"primary_lift_threshold_m":primary,"sustained_lift_steps":length,"probe_status_counts":dict(sorted(counts.items())),"sensitivity_row_count":len(sensitivity),"source_kind":source,"boundary":"synthetic z/contact trace; bilateral contact and physical lift are separate observables"}
    return summaries,sensitivity,report,render_svg(sensitivity,len(summaries))

def write_csv(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle: writer=csv.DictWriter(handle,fieldnames=fields); writer.writeheader(); writer.writerows(rows)

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--trace",type=Path,required=True); p.add_argument("--config",type=Path,required=True); p.add_argument("--summary",type=Path,required=True); p.add_argument("--sensitivity",type=Path,required=True); p.add_argument("--plot",type=Path,required=True); p.add_argument("--report",type=Path,required=True); a=p.parse_args()
    rows,sensitivity,report,svg=analyze(a.trace,a.config); write_csv(a.summary,rows,SUMMARY_FIELDS); write_csv(a.sensitivity,sensitivity,SENSITIVITY_FIELDS); a.plot.parent.mkdir(parents=True,exist_ok=True); a.plot.write_text(svg,encoding="utf-8"); a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(f"PASS: episodes={len(rows)} sensitivity_rows={len(sensitivity)} bilateral_is_not_lift=true")
if __name__=="__main__": main()
