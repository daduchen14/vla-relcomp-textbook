#!/usr/bin/env python3
"""从 synthetic 配对四格计数计算 Wilson、恢复/损伤与 exact McNemar。"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
def wilson(successes,n,z):
    p=successes/n;den=1+z*z/n;center=(p+z*z/(2*n))/den;margin=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;return {"successes":successes,"trials":n,"rate":round(p,6),"lower":round(center-margin,6),"upper":round(center+margin,6)}
def exact_mcnemar(n01,n10):
    discordant=n01+n10
    if discordant==0:return 1.0
    tail=sum(math.comb(discordant,k) for k in range(min(n01,n10)+1));return min(1.0,2*tail/(2**discordant))
def analyze(input_path:Path,config_path:Path):
    data=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"));counts={key:int(data[key]) for key in ("n00","n01","n10","n11")}
    if not data["source_kind"].startswith("synthetic_paired_counts_") or any(value<0 for value in counts.values()) or cfg.get("test")!="exact_mcnemar_two_sided":raise ValueError("statistics input/config 非法")
    n=sum(counts.values())
    if n<=0:raise ValueError("empty denominator")
    baseline_success=counts["n10"]+counts["n11"];repair_success=counts["n01"]+counts["n11"];baseline_fail=counts["n00"]+counts["n01"];z=float(cfg["wilson_z"]);p_value=exact_mcnemar(counts["n01"],counts["n10"])
    report={"transition_definition":{"n00":"baseline fail, repair fail","n01":"baseline fail, repair success","n10":"baseline success, repair fail","n11":"baseline success, repair success"},"counts":counts,"paired_trials":n,"baseline_success":wilson(baseline_success,n,z),"repair_success":wilson(repair_success,n,z),"paired_success_rate_delta":round((repair_success-baseline_success)/n,6),"recovery_rate_among_baseline_failures":wilson(counts["n01"],baseline_fail,z),"damage_rate_among_baseline_successes":wilson(counts["n10"],baseline_success,z),"mcnemar":{"discordant_pairs":counts["n01"]+counts["n10"],"two_sided_exact_p":round(p_value,8),"alpha":cfg["alpha"],"reject_equal_marginals":p_value<float(cfg["alpha"]),"boundary":"tests paired marginal equality; p-value is not effect size or probability null is true"},"effect_interval_significance_separated":True,"records_source":"synthetic counts only","formal_statistics_available":False,"boundary":"not raw episode, checkpoint, VLA-Arena, or final inferential evidence"}
    return report
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();report=analyze(a.input,a.config);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: n={report['paired_trials']} delta={report['paired_success_rate_delta']:+.3f} exact_p={report['mcnemar']['two_sided_exact_p']:.4f} synthetic=true")
if __name__=="__main__":main()
