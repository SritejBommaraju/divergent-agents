"""
robustness.py — Benchmark 6: does cross-checking k DIVERSE solutions reduce shipped bugs? (done rigorously)

Single-pass ships ONE solution; the engine generates k diverse ones, fuzzes them, and ships the
majority-vote (differential testing). We measure, over 12 novel twisted problems with trusted brute
references and hundreds of fuzzed inputs each:
  * buggy-solution rate    : fraction of solutions that FAIL fuzzing (the single-pass "ship a bug" risk)
  * error rate vs k        : P(engine's shipped answer is wrong on a random input) for k=1,3,5,7 — should fall
  * idiosyncratic vs systematic : of all (input where some solution errs), is the error a MINORITY (majority
                            vote fixes it) or a MAJORITY (systematic — diversity CANNOT fix it)?
Monte-Carlo over samples, bootstrap CIs over problems. ponytail: stdlib + numpy.
Usage: python bench/robustness.py [nfuzz]
"""
import sys, os, re, json, subprocess, tempfile
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import code_twist as ct1
import code_twist2 as ct2

NFUZZ = int(sys.argv[1]) if len(sys.argv) > 1 else 600
RAWS = ["bench/data/code_twist_raw.json", "bench/data/code_twist2_raw.json"]

def mod_of(key):
    return ct1 if key in ct1.PROBLEMS else ct2

def fuzz_for(key, n, seed=21):
    return mod_of(key).fuzz(key, n, seed)

# load solution pool per problem
pool = {}
for raw in RAWS:
    if not os.path.exists(raw): continue
    for r in json.load(open(raw, encoding="utf-8")):
        pool.setdefault(r["problem"], []).append(r["code"])
probs = list(pool.keys())


def clean(code):
    if "```" in code:
        m = re.search(r"```(?:python)?\s*(.*?)```", code, re.DOTALL)
        if m: code = m.group(1)
    return code.strip()

def run_on(key, code, inputs, timeout=12):
    fn = mod_of(key).PROBLEMS[key]["fn"]
    runner = (clean(code) + "\n\nimport json\n"
              f"_inp=json.loads(r'''{json.dumps(inputs)}''')\n"
              "res=[]\n"
              f"for a in _inp:\n    try: res.append({fn}(*a))\n    except Exception: res.append('__ERR__')\n"
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

def norm(v):
    return "T" if v is True else "F" if v is False else str(v)


# evaluate the full pool on fuzz inputs per problem
print(f"Evaluating {sum(len(v) for v in pool.values())} solutions over {len(probs)} problems x {NFUZZ} fuzzed inputs...")
P = {}  # key -> {exp, sols:[outvec], buggy:[bool]}
for key in probs:
    fz = fuzz_for(key, NFUZZ)
    exp = [norm(mod_of(key).PROBLEMS[key]["ref"](*[json.loads(json.dumps(a)) for a in args])) for args in fz]
    sols, buggy = [], []
    for code in pool[key]:
        out = run_on(key, code, fz)
        ov = [norm(o) for o in out] if out and len(out) == len(fz) else None
        sols.append(ov); buggy.append(ov is None or ov != exp)
    P[key] = {"exp": exp, "sols": sols, "buggy": buggy, "fz": fz}

rng = np.random.default_rng(0)

def boot(vals, it=10000):
    x = np.array(vals, float)
    if not len(x): return (float("nan"),) * 2
    m = x[rng.integers(0, len(x), size=(it, len(x)))].mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))

# 1) buggy-solution rate (single-pass "ships a bug" risk)
per_prob_bug = []
for key in probs:
    runnable = [b for b, s in zip(P[key]["buggy"], P[key]["sols"])]
    per_prob_bug.append(sum(P[key]["buggy"]) / len(P[key]["buggy"]))
bug_rate = sum(sum(P[k]["buggy"]) for k in probs) / sum(len(P[k]["buggy"]) for k in probs)
lo, hi = boot(per_prob_bug)

# 2) error rate vs k (majority vote of k random solutions)
def engine_err_rate(k, trials=400):
    """mean over problems of P(majority-of-k wrong on a random fuzzed input)."""
    per_prob = []
    for key in probs:
        good = [s for s in P[key]["sols"] if s is not None]
        if len(good) < 1: per_prob.append(float("nan")); continue
        exp = P[key]["exp"]; n = len(exp)
        errs = 0; tot = 0
        for _ in range(trials):
            idx = rng.integers(0, len(good), size=min(k, len(good)))
            sample = [good[i] for i in idx]
            i = int(rng.integers(0, n))
            votes = Counter(s[i] for s in sample)
            maj = votes.most_common(1)[0][0]
            errs += (maj != exp[i]); tot += 1
        per_prob.append(errs / tot)
    m = float(np.nanmean(per_prob))
    return m, per_prob

print("\n" + "=" * 76)
print(f"BENCHMARK 6 — robustness via differential testing ({len(probs)} problems, {NFUZZ} fuzz inputs)")
print("=" * 76)
print(f"\nBuggy-solution rate (a single forward pass ships a fuzz-failing solution):")
print(f"  {bug_rate:.4f}  ({sum(sum(P[k]['buggy']) for k in probs)}/{sum(len(P[k]['buggy']) for k in probs)} solutions)  95% CI over problems [{lo:.3f},{hi:.3f}]")
print(f"  per-problem buggy solutions: " + ", ".join(f"{k}:{sum(P[k]['buggy'])}/{len(P[k]['buggy'])}" for k in probs))

print(f"\nEngine error rate vs k (majority-vote of k diverse solutions, P(wrong | random input)):")
res_k = {}
for k in [1, 3, 5, 7]:
    m, pp = engine_err_rate(k)
    clo, chi = boot([x for x in pp if x == x])
    res_k[k] = m
    print(f"  k={k}: {m:.5f}   95% CI [{clo:.5f},{chi:.5f}]")

# 3) idiosyncratic vs systematic decomposition
idio = systt = 0
for key in probs:
    good = [s for s in P[key]["sols"] if s is not None]
    if len(good) < 2: continue
    exp = P[key]["exp"]
    for i in range(len(exp)):
        votes = [s[i] for s in good]
        wrong = [v for v in votes if v != exp[i]]
        if not wrong: continue
        maj = Counter(votes).most_common(1)[0][0]
        if maj == exp[i]: idio += 1          # minority wrong -> majority fixes it
        else: systt += 1                      # majority wrong -> systematic, diversity fails
print(f"\nWhen >=1 solution errs on an input, is the error fixable by majority vote?")
print(f"  IDIOSYNCRATIC (minority wrong, majority vote FIXES it): {idio}")
print(f"  SYSTEMATIC   (majority wrong, diversity CANNOT fix):    {systt}")
print(f"  => differential testing rescues {idio}/{idio+systt} = {idio/max(idio+systt,1):.3f} of bug-exposing inputs")

json.dump({"nfuzz": NFUZZ, "buggy_solution_rate": bug_rate, "err_vs_k": res_k,
           "idiosyncratic": idio, "systematic": systt,
           "per_problem_buggy": {k: [sum(P[k]['buggy']), len(P[k]['buggy'])] for k in probs}},
          open("bench/data/robustness_results.json", "w", encoding="utf-8"), indent=2)
print("\nsaved -> bench/data/robustness_results.json")
