#!/usr/bin/env python3
"""验证 synthetic final pairs 完整性并比较 baseline/repair。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
def analyze(input_path:Path,config_path:Path):
    data=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"));rows=data["records"]
    if not data["source_kind"].startswith("synthetic_final_pairs_") or cfg.get("missing_pair_policy")!="fail_closed" or cfg.get("required_conditions")!=["baseline","repair"] or cfg.get("required_arms")!=["control","counterfactual"]:raise ValueError("pair boundary 非法")
    pair_ids=sorted({row["pair_id"] for row in rows});expected={(pair,condition,arm) for pair in pair_ids for condition in cfg["required_conditions"] for arm in cfg["required_arms"]};observed={(row["pair_id"],row["condition"],row["arm"]) for row in rows};missing=sorted(expected-observed);duplicates=len(rows)-len(observed)
    if missing or duplicates or len(pair_ids)!=int(cfg["registered_pair_count"]):raise ValueError(f"pair integrity 失败: missing={missing} duplicates={duplicates}")
    pair_rows=[];summary={}
    for condition in cfg["required_conditions"]:
        paired_successes=0;flips=0
        for pair in pair_ids:
            values={row["arm"]:bool(row["success"]) for row in rows if row["pair_id"]==pair and row["condition"]==condition};paired=all(values.values());flip=len(set(values.values()))>1;paired_successes+=paired;flips+=flip;pair_rows.append({"pair_id":pair,"condition":condition,"control_success":values["control"],"counterfactual_success":values["counterfactual"],"paired_success":paired,"outcome_flip":flip})
        summary[condition]={"paired_success_rate":round(paired_successes/len(pair_ids),6),"outcome_flip_rate":round(flips/len(pair_ids),6)}
    report={"registered_pair_count":len(pair_ids),"expected_record_count":len(expected),"observed_record_count":len(rows),"missing_records":missing,"duplicate_count":duplicates,"integrity_pass":True,"missing_pair_policy":"fail_closed","condition_summary":summary,"repair_paired_success_gain":round(summary["repair"]["paired_success_rate"]-summary["baseline"]["paired_success_rate"],6),"pair_rows":pair_rows,"records_source":"synthetic fixture only","vla_arena_run":False,"final_pair_data_available":False,"boundary":"not checkpoint, VLA-Arena, or final counterfactual evaluation evidence"}
    return report
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();report=analyze(a.input,a.config);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: pairs={report['registered_pair_count']} gain={report['repair_paired_success_gain']:+.3f} missing=0 synthetic=true")
if __name__=="__main__":main()
