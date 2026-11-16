#!/usr/bin/env python3
"""Download the published OpenHands + Claude Opus 4.5 predictions for SWE-bench Verified and keep
the 25 sampled instances listed in kt_selection.json. Writes kt_preds.jsonl for the harness.

Source: the submission's all_preds.jsonl in the public swe-bench-submissions bucket, the one
referenced by evaluation/verified/20251127_openhands_claude-opus-4-5/metadata.yaml in
github.com/SWE-bench/experiments.
"""
import json
import urllib.request

URL = ("https://swe-bench-submissions.s3.amazonaws.com/"
       "verified/20251127_openhands_claude-opus-4-5/all_preds.jsonl")

want = {r["instance_id"] for r in json.load(open("kt_selection.json"))}
with urllib.request.urlopen(URL) as resp:
    rows = [json.loads(line) for line in resp.read().decode().splitlines() if line.strip()]
keep = [r for r in rows if r["instance_id"] in want]
missing = want - {r["instance_id"] for r in keep}
if missing:
    raise SystemExit(f"missing from the published predictions: {sorted(missing)}")
with open("kt_preds.jsonl", "w") as f:
    for r in sorted(keep, key=lambda r: r["instance_id"]):
        f.write(json.dumps(r) + "\n")
print(f"wrote kt_preds.jsonl: {len(keep)} of {len(rows)} predictions")
