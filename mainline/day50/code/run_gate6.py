#!/usr/bin/env python3
"""从原始 Day 46–49 inputs 重建 Gate 6，缺正式证据时停止扩张。"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
try:
    from mainline.day46.code.prepare_repeat_launches import analyze as repeats
    from mainline.day47.code.analyze_l0_retention import analyze as retention
    from mainline.day48.code.analyze_ood_results import analyze as ood
    from mainline.day49.code.analyze_cost_matched_ablation import analyze as ablation
except ModuleNotFoundError:
    sys.path.insert(0,str(Path(__file__).resolve().parents[3]));from mainline.day46.code.prepare_repeat_launches import analyze as repeats;from mainline.day47.code.analyze_l0_retention import analyze as retention;from mainline.day48.code.analyze_ood_results import analyze as ood;from mainline.day49.code.analyze_cost_matched_ablation import analyze as ablation
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def analyze(args):
    repeat=repeats(args.split,args.base_plan,args.repeat_plan,args.stability,args.candidate);l0=retention(args.l0_input,args.l0_config)[1];ood_report=ood(args.ood_input,args.ood_config);abl=ablation(args.ablation_input,args.ablation_config)
    sources=[args.split,args.base_plan,args.repeat_plan,args.stability,args.candidate,args.l0_input,args.l0_config,args.ood_input,args.ood_config,args.ablation_input,args.ablation_config]
    formal=repeat["formal_checkpoints_produced"] and l0["vla_arena_run"] and ood_report["vla_arena_run"] and abl["formal_runs_available"]
    criteria={"formal_evidence_complete":formal,"all_registered_seeds_present":repeat["all_registered_seeds"]==[1,2,3],"l0_retention_pass":l0["retention_pass"],"l1_l2_pass":ood_report["all_levels_pass"],"ablation_single_variable":abl["single_variable"],"ablation_cost_matched":abl["all_cost_matched"],"no_cherry_picking":not repeat["variance_policy"]["best_seed_selection"] and not abl["best_seed_selection"]}
    if not formal:outcome="停止扩张";reason="FORMAL_EVIDENCE_MISSING"
    elif all(criteria.values()):outcome="通过";reason="ALL_FROZEN_CRITERIA_PASS"
    else:outcome="补做";reason="FORMAL_CRITERIA_INCOMPLETE_OR_FAILED"
    return {"gate":"Gate 6","source_sha256":{path.name:sha(path) for path in sources},"allowed_materials":["raw registered inputs","locked configs","machine-rebuilt metrics","failure records"],"forbidden_materials":["copied summary values","best-seed subset","post-hoc threshold","synthetic-as-formal claim"],"criteria":criteria,"reconstructed_metrics":{"registered_seeds":repeat["all_registered_seeds"],"l0_retention_rate":l0["retention_rate"],"ood_delta_by_level":{level:row["paired_success_rate_delta"] for level,row in ood_report["levels"].items()},"mean_ablation_component_effect":abl["mean_component_effect"]},"outcome":outcome,"reason":reason,"learner_gate_status":"REHEARSAL_ONLY_NOT_PASSED","gate6_passed":False,"next_action":"obtain authorized formal checkpoints and raw evaluator records, then rerun Gate 6; do not expand claims","boundary":"all current metrics are synthetic/planned teaching evidence, not VLA-Arena project results"}
def parser():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("split","base-plan","repeat-plan","stability","candidate","l0-input","l0-config","ood-input","ood-config","ablation-input","ablation-config","report"):p.add_argument(f"--{name}",type=Path,required=True)
    return p
def main():
    a=parser().parse_args();report=analyze(a);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: gate6_outcome={report['outcome']} reason={report['reason']} learner_passed=false")
if __name__=="__main__":main()
