#!/usr/bin/env python3
"""准备隔离的 Gate 8 A/B workspace；不写答案。"""
import argparse,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
STARTER='''"""Gate 8：独立实现 analyze；不得读取 shared/answer_keys。"""\n\ndef analyze(payload, minimum_delta):\n    # TODO: observation summary、四段 funnel、配对四格、首个失败、delta/threshold、boundary\n    raise NotImplementedError("请独立实现 analyze")\n'''
def prepare(form,output):
 if output.exists():raise FileExistsError("capstone workspace 已存在")
 source=ROOT/f"shared/fixtures/day70_capstone_{form.lower()}.json";output.mkdir(parents=True);shutil.copyfile(source,output/"exam.json");(output/"core_module.py").write_text(STARTER);(output/"oral_memo.md").write_text("# Gate 8 oral memo\n\n请在不看答案后独立填写。\n");(output/"FORM.json").write_text(json.dumps({"form_id":form,"answer_key_forbidden_until_submission":True},indent=2)+"\n");print(f"Prepared Gate 8 form {form}: {output}")
def main():
 p=argparse.ArgumentParser();p.add_argument("--form",choices=["A","B"],required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args();prepare(a.form,a.output)
if __name__=="__main__":main()
