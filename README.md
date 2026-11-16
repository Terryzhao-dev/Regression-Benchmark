# SWE-bench Regression Evaluator

Re-scores SWE-bench patches to separate fixes that broke other tests from real failures.

## How it is different

SWE-bench runs two sets of tests per instance:

- `FAIL_TO_PASS`: should pass once the bug is fixed
- `PASS_TO_PASS`: already passing, should stay passing

The leaderboard collapses both into one bit: resolved or not. So two different outcomes get the same label:

- the agent failed to fix the bug
- the agent fixed the bug and broke working code doing it

This evaluator separates them, into three buckets:

| Bucket | FAIL_TO_PASS | PASS_TO_PASS |
|---|---|---|
| (a) clean resolve | all pass | all pass |
| **(b) fixed-but-broke** | all pass | ≥1 fails |
| (c) not fixed | fails | any |

Bucket (b) is invisible upstream. SWE-bench labels it "unresolved", identical to (c).

**Metric:** regression rate among fixes = `b / (a + b)`.

## Result

25 random Django instances from SWE-bench Verified (seed 42), scoring the published OpenHands + Claude Opus 4.5 patches.

**18 clean / 2 fixed-but-broke / 5 not fixed → 10% regression rate among fixes.**

Two of the 7 the leaderboard calls failures were real fixes with collateral damage: `django-11734` broke 4 `queries.tests` tests and `django-12273` broke `test_issue_6755`. Both were re-run and failed the same way.

Trust checks: gold validation 5/5, and verdicts matched the official leaderboard label 25/25.

## Limits

n=25, one repo, one agent. A **lower bound**: it uses the thin `PASS_TO_PASS` set SWE-bench ships, so a wider net would find more. Regressions in untested code are invisible, exactly as they are to CI.

## Contents

- `kt_bucket.py`: the scoring layer
- `fetch_preds.py` and `kt_selection.json`: the inputs for the 25-instance run
- `results/`: the SWE-bench harness summary for each run (which instances resolved, not the buckets). `random_sample_25_django.json` is the run above. `biased_17_unresolved-weighted_django.json` is an earlier 17-instance sample weighted towards instances the leaderboard marks unresolved; 9 of its 17 errored in the harness, so it isn't used for the result.
- `patches/`: harness modification for local git mirroring (network workaround, does not affect scoring)

## Running it

1. `python fetch_preds.py` downloads the published OpenHands + Claude Opus 4.5 predictions and keeps the 25 instances in `kt_selection.json` (rebuilt from the harness summary's instance list), writing `kt_preds.jsonl`.
2. Install `swebench` 4.1.0 and run the harness on `kt_preds.jsonl` with `--run_id kt_openhands_opus45 --max_workers 1`, which writes `logs/run_evaluation/kt_openhands_opus45/`. Apply `patches/swebench-git-mirror.patch` only if cloning from GitHub fails inside the containers.
3. `python kt_bucket.py` sorts each instance into the three buckets from those logs. The logs aren't in this repo.

MIT. Built on [SWE-bench](https://github.com/SWE-bench/SWE-bench) (MIT).
