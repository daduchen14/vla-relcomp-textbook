#!/usr/bin/env python3
"""分析 lift 后目标到正确/错误参照物的距离趋势与区域进入事件。"""
from __future__ import annotations
import argparse,csv,json,math
from collections import Counter
from pathlib import Path
FIELDS=("episode_id","reference_object_id","lifted_step_count","initial_reference_distance_m","min_reference_distance_m","net_progress_m","decrease_fraction","first_entry_step","wrong_reference_id","wrong_reference_first_step","approach_detected","probe_status")

def bit(value,name):
    if value not in {"0","1"}:raise ValueError(f"{name} 必须为 0/1")
    return value=="1"
def first_run(values,length):
    # entry 必须连续维持；一次越阈不算进入参照区域。
    run=0
    for index,value in enumerate(values):
        run=run+1 if value else 0
        if run==length:return index-length+1
    return None
def analyze(trace_path:Path,config_path:Path):
    with trace_path.open(encoding="utf-8",newline="") as handle:raw=list(csv.DictReader(handle))
    cfg=json.loads(config_path.read_text(encoding="utf-8"));threshold=float(cfg["entry_threshold_m"]);sustain=int(cfg["sustained_entry_steps"]);minimum=float(cfg["minimum_progress_m"]);epsilon=float(cfg["trend_epsilon_m"]);wrong_threshold=float(cfg["wrong_reference_threshold_m"]);wrong_sustain=int(cfg["wrong_reference_sustained_steps"]);source=cfg.get("source_kind","")
    if min(threshold,sustain,minimum,wrong_threshold,wrong_sustain)<=0 or epsilon<0 or not source.startswith("synthetic_approach_"):raise ValueError("approach config 非法")
    groups={}
    for row in raw:
        if not row.get("episode_id"):raise ValueError("episode_id 不能为空")
        groups.setdefault(row["episode_id"],[]).append(row)
    if not groups:raise ValueError("trace 不能为空")
    output=[]
    for episode_id,rows in sorted(groups.items()):
        rows.sort(key=lambda row:int(row["step"]));steps=[int(row["step"]) for row in rows]
        if steps!=list(range(len(rows))):raise ValueError("step 必须从 0 连续")
        references={row["reference_object_id"] for row in rows}
        if len(references)!=1 or "" in references:raise ValueError("reference_object_id 必须固定")
        # 正确参照物来自任务语义；nearest_other 只用于错误吸引诊断。
        reference=next(iter(references));lifted=[row for row in rows if bit(row["lifted"],"lifted")]
        if not lifted:
            output.append({"episode_id":episode_id,"reference_object_id":reference,"lifted_step_count":0,"initial_reference_distance_m":"","min_reference_distance_m":"","net_progress_m":"","decrease_fraction":"","first_entry_step":"","wrong_reference_id":"","wrong_reference_first_step":"","approach_detected":"false","probe_status":"NO_LIFTED_SEGMENT"});continue
        distances=[float(row["target_reference_distance_m"]) for row in lifted]
        wrong_distances=[float(row["nearest_other_distance_m"]) for row in lifted]
        if any(not math.isfinite(value) or value<0 for value in distances+wrong_distances):raise ValueError("distance 必须有限且非负")
        entry_index=first_run([value<=threshold for value in distances],sustain);entry_step="" if entry_index is None else int(lifted[entry_index]["step"])
        # 趋势和区域进入分别计算，避免“方向对”被误报成“已经到达”。
        deltas=[before-after for before,after in zip(distances,distances[1:])];fraction=sum(delta>epsilon for delta in deltas)/len(deltas) if deltas else 0.0;progress=distances[0]-min(distances)
        wrong_flags=[row["nearest_other_id"] not in {"",reference} and value<=wrong_threshold for row,value in zip(lifted,wrong_distances)];wrong_index=first_run(wrong_flags,wrong_sustain);wrong_id="" if wrong_index is None else lifted[wrong_index]["nearest_other_id"];wrong_step="" if wrong_index is None else int(lifted[wrong_index]["step"])
        if entry_index is not None:status="APPROACHED_REFERENCE"
        elif wrong_index is not None:status="WRONG_REFERENCE_ATTRACTION"
        elif progress>=minimum:status="PROGRESS_NO_ENTRY"
        else:status="NO_PROGRESS"
        output.append({"episode_id":episode_id,"reference_object_id":reference,"lifted_step_count":len(lifted),"initial_reference_distance_m":f"{distances[0]:.6f}","min_reference_distance_m":f"{min(distances):.6f}","net_progress_m":f"{progress:.6f}","decrease_fraction":f"{fraction:.6f}","first_entry_step":entry_step,"wrong_reference_id":wrong_id,"wrong_reference_first_step":wrong_step,"approach_detected":str(entry_index is not None).lower(),"probe_status":status})
    counts=Counter(row["probe_status"] for row in output);report={"episode_count":len(output),"entry_threshold_m":threshold,"sustained_entry_steps":sustain,"minimum_progress_m":minimum,"probe_status_counts":dict(sorted(counts.items())),"source_kind":source,"boundary":"synthetic trajectory; distance trend and wrong-reference attraction are observable, not causal mechanisms"}
    return output,report
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:writer=csv.DictWriter(handle,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--trace",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();rows,report=analyze(a.trace,a.config);write(a.output,rows);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: episodes={len(rows)} statuses={report['probe_status_counts']} trend_is_not_cause=true")
if __name__=="__main__":main()
