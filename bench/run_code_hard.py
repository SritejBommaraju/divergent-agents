"""
run_code_hard.py — PROPER pass@k benchmark scoring (per BENCHMARKING.md P5).

For each (problem, condition) with n candidate solutions:
  * unbiased pass@k estimator (Chen et al. 2021): pass@k = E_problems[1 - C(n-c,k)/C(n,k)]
  * coverage = pass@n (does ANY candidate solve it)
  * selected-accuracy via a REALISTIC non-oracle selector: majority vote by behavior on the PUBLIC
    example inputs only (self-consistency; no hidden-test leakage) — because coverage without a picker
    flatters a multi-sample method (Large Language Monkeys 2407.21787).
  * a dumb-guessing control (constant return) so coverage gains aren't just answer-prior exploitation.
Compute-matched: both conditions use the same n. Bootstrap 95% CIs over problems.
Usage: python bench/run_code_hard.py [bench/data/code_hard_raw.json]
"""
import sys, os, re, json, importlib
from math import comb
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import subprocess, tempfile

RAW = sys.argv[1] if len(sys.argv) > 1 else "bench/data/code_hard_raw.json"
MODULE = sys.argv[2] if len(sys.argv) > 2 else "code_hard"
ch = importlib.import_module(MODULE)
rows = json.load(open(RAW, encoding="utf-8"))
N_PUBLIC = 6  # first N inputs per problem are the "public examples" usable by a non-oracle selector


def clean(code):
    if "```" in code:
        m = re.search(r"```(?:python)?\s*(.*?)```", code, re.DOTALL)
        if m: code = m.group(1)
    return code.strip()


def outputs(key, code, timeout=10):
    """Run candidate on ALL inputs; return list of outputs ('__ERR__' on failure) or None if it won't run."""
    p = ch.PROBLEMS[key]
    runner = (clean(code) + "\n\nimport json\n"
              f"_inp=json.loads(r'''{json.dumps(p['inputs'])}''')\n"
              "res=[]\n"
              f"for a in _inp:\n    try: res.append({p['fn']}(*a))\n    except Exception: res.append('__ERR__')\n"
              "print(json.dumps(res, default=str))\n")
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
            fh.write(runner); path = fh.name
        out = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=timeout,
                             cwd=tempfile.gettempdir())
        line = out.stdout.strip().splitlines()[-1] if out.stdout.strip() else ""
        return json.loads(line)
    except Exception:
        return None
    finally:
        try: os.unlink(path)
        except Exception: pass


def matches(out, exp):
    if out is None: return False
    if len(out) != len(exp): return False
    for r, e in zip(out, exp):
        if isinstance(e, bool) or r in (True, False):
            if bool(r) != bool(e): return False
        elif r != e: return False
    return True


probs, conds = [], []
for r in rows:
    if r["problem"] not in probs: probs.append(r["problem"])
    if r["condition"] not in conds: conds.append(r["condition"])
order = [c for c in ["baseline", "engine"] if c in conds] + [c for c in conds if c not in ("baseline", "engine")]

# evaluate every candidate once
expected = {k: [ch.PROBLEMS[k]["ref"](*a) for a in ch.PROBLEMS[k]["inputs"]] for k in probs}
cells = {}  # (problem,cond) -> list of {correct, pubsig}
for pk in probs:
    for c in conds:
        lst = []
        for r in [x for x in rows if x["problem"] == pk and x["condition"] == c]:
            out = outputs(pk, r["code"])
            correct = matches(out, expected[pk])
            pubsig = tuple(map(str, out[:N_PUBLIC])) if out else ("__ERR__",)
            lst.append({"correct": correct, "pubsig": pubsig})
        cells[(pk, c)] = lst


def pass_at_k(n, c, k):
    if k > n: return float("nan")
    if n - c < k: return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def selected_correct(lst):
    """Majority vote by public-example behavior; pick the largest cluster's correctness (non-oracle)."""
    from collections import Counter
    if not lst: return 0
    sigs = Counter(x["pubsig"] for x in lst)
    top = sigs.most_common(1)[0][0]
    members = [x for x in lst if x["pubsig"] == top]
    return int(sum(m["correct"] for m in members) > len(members) / 2)


def boot_over_problems(vals, iters=10000, seed=0):
    x = np.array(vals, float)
    if not len(x): return (float("nan"),) * 3
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, len(x), size=(iters, len(x)))].mean(axis=1)
    return float(x.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


nmin = min(len(cells[(pk, c)]) for pk in probs for c in conds)
print("=" * 84)
print(f"HARD CODING — proper pass@k (compute-matched, n={nmin}/cell, {len(probs)} problems)")
print("=" * 84)
print(f"\n{'problem':12}" + "".join(f"{c+' c/n':>16}" for c in order))
for pk in probs:
    line = f"{pk:12}"
    for c in order:
        lst = cells[(pk, c)]; cc = sum(x["correct"] for x in lst)
        line += f"{cc}/{len(lst):>14}"
    print(line)

print("\n## pass@k (mean over problems, unbiased estimator) [95% CI]")
for k in [1, 2, 3, 5, nmin]:
    if k > nmin: continue
    print(f"  k={k}:")
    for c in order:
        vals = [pass_at_k(len(cells[(pk, c)]), sum(x["correct"] for x in cells[(pk, c)]), k) for pk in probs]
        m, lo, hi = boot_over_problems(vals)
        print(f"    {c:10} pass@{k} = {m:.3f}  [{lo:.3f},{hi:.3f}]")

print("\n## selected-accuracy (non-oracle majority vote on public examples) [95% CI]")
for c in order:
    vals = [selected_correct(cells[(pk, c)]) for pk in probs]
    m, lo, hi = boot_over_problems(vals)
    print(f"  {c:10} selected-acc = {m:.3f}  [{lo:.3f},{hi:.3f}]")

print("\n## coverage (pass@n) and per-problem solve counts")
for c in order:
    vals = [1 if any(x["correct"] for x in cells[(pk, c)]) else 0 for pk in probs]
    m, lo, hi = boot_over_problems(vals)
    print(f"  {c:10} coverage = {m:.3f}  [{lo:.3f},{hi:.3f}]")

out = {f"{pk}|{c}": {"n": len(cells[(pk, c)]), "correct": sum(x["correct"] for x in cells[(pk, c)]),
                     "selected": selected_correct(cells[(pk, c)])} for pk in probs for c in conds}
json.dump(out, open("bench/data/code_hard_results.json", "w", encoding="utf-8"), indent=2)
print("\nsaved -> bench/data/code_hard_results.json")
