#!/usr/bin/env python3
"""构建可审计 claim-evidence 结果锁，并执行 Gate 7 三条随机抽查。"""
from __future__ import annotations
import argparse, hashlib, json, random
from pathlib import Path

LOCKED_COMMIT = "babe582ebffc82b979b77964a7e56417d02f63a4"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def valid_digest(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdef" for char in value)

def validate_claim(claim: dict) -> None:
    required = ("claim_id", "allowed_claim", "forbidden_stronger_claim", "table", "raw_episodes", "versions", "negative_result")
    if not all(key in claim for key in required):
        raise ValueError("claim 字段不完整")
    if not claim["allowed_claim"].strip() or not claim["forbidden_stronger_claim"].strip():
        raise ValueError("允许与禁止主张均不能为空")
    table = claim["table"]
    if not table.get("table_id") or not table.get("path") or not valid_digest(table.get("sha256", "")):
        raise ValueError("table 证据不完整")
    if not claim["raw_episodes"] or any(not row.get("episode_id") or not valid_digest(row.get("sha256", "")) for row in claim["raw_episodes"]):
        raise ValueError("raw episode 证据不完整")
    versions = claim["versions"]
    if versions.get("upstream_commit") != LOCKED_COMMIT or not valid_digest(versions.get("analysis_sha256", "")):
        raise ValueError("版本证据不完整")

def analyze(input_path: Path, config_path: Path) -> dict:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    claims = data["claims"]
    if len({row["claim_id"] for row in claims}) != len(claims):
        raise ValueError("claim_id 必须唯一")
    for claim in claims:
        validate_claim(claim)
    sample_size = config["sample_size"]
    if sample_size != 3 or len(claims) < sample_size:
        raise ValueError("Gate 7 必须随机抽三条")
    selected_ids = random.Random(config["audit_seed"]).sample(sorted(row["claim_id"] for row in claims), sample_size)
    by_id = {row["claim_id"]: row for row in claims}
    audit = [{"claim_id": cid, "allowed_claim": by_id[cid]["allowed_claim"], "table": by_id[cid]["table"], "raw_episodes": by_id[cid]["raw_episodes"], "versions": by_id[cid]["versions"], "forbidden_stronger_claim": by_id[cid]["forbidden_stronger_claim"], "negative_result": by_id[cid]["negative_result"]} for cid in selected_ids]
    formal = data["evidence_mode"] == "formal" and data["formal_evidence_available"] is True
    complete = len(audit) == 3 and all(row["table"] and row["raw_episodes"] and row["versions"] and row["forbidden_stronger_claim"] for row in audit)
    outcome = "通过" if formal and complete else ("补做" if formal else "停止扩张")
    return {"gate":"Gate 7","source_sha256":{"input":sha(input_path),"config":sha(config_path)},"audit_seed":config["audit_seed"],"selected_claims":audit,"claim_count":len(claims),"negative_result_count":sum(bool(row["negative_result"]) for row in claims),"criteria":{"three_claims_randomly_sampled":len(audit)==3,"claim_evidence_links_complete":complete,"formal_evidence_complete":formal,"stronger_claim_boundary_present":all(row["forbidden_stronger_claim"] for row in audit)},"outcome":outcome,"reason":"ALL_FROZEN_EVIDENCE_PRESENT" if outcome=="通过" else ("FORMAL_LINKS_INCOMPLETE" if outcome=="补做" else "FORMAL_EVIDENCE_MISSING"),"learner_gate_status":"REHEARSAL_ONLY_NOT_PASSED","gate7_passed":False,"next_action":"obtain authorized formal tables, raw episode records, and immutable version hashes; rebuild before expanding claims","boundary":"synthetic claim registry validates traceability mechanics only; it is not VLA-Arena result evidence"}

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True);parser.add_argument("--config",type=Path,required=True);parser.add_argument("--report",type=Path,required=True)
    args=parser.parse_args();report=analyze(args.input,args.config);args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"PASS: gate7_outcome={report['outcome']} sampled={len(report['selected_claims'])} learner_passed=false")

if __name__ == "__main__":
    main()
