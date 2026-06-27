"""
fuzz_eval.py — does the pass@1 ceiling survive HARSH adversarial fuzzing?

The checkers used ~26 fixed inputs per problem. A frontier model can pass a small fixed set while still
harboring rare edge-case bugs. Here we re-evaluate every already-generated solution against a much larger
FUZZED input set (hundreds of random cases per problem) using the trusted brute reference as oracle, and
ask two things:
  1. Does fuzzed pass@1 drop below the fixed-test ceiling? (is there hidden headroom?)
  2. DIFFERENTIAL TESTING: where the diverse solutions DISAGREE on a fuzzed input, >=1 is buggy — so
     diversity is itself a correctness oracle, and majority-vote over diverse solutions should beat a
     single random pick. (the engine's value WITHOUT a reference.)

Reuses bench/data/code_twist_raw.json (no new generation). ponytail: stdlib + numpy.
"""
import sys, os, re, json, random, subprocess, tempfile
from math import comb
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import code_twist as ct

RAW = sys.argv[1] if len(sys.argv) > 1 else "bench/data/code_twist_raw.json"
NFUZZ = int(sys.argv[2]) if len(sys.argv) > 2 else 400
rows = json.load(open(RAW, encoding="utf-8"))


def fuzz_inputs(key, n, seed=7):
    R = random.Random(seed)
    out = []
    if key == "diag":
        for _ in range(n):
            r, c = R.randint(1, 5), R.randint(1, 5)
            g = [[1 if R.random() < 0.22 else 0 for _ in range(c)] for _ in range(r)]
            g[0][0] = 0; g[r - 1][c - 1] = 0
            out.append([g])
    elif key == "mono":
        for _ in range(n):
            r, c = R.randint(1, 5), R.randint(1, 5)
            out.append([[[R.randint(1, 8) for _ in range(c)] for _ in range(r)]])
    elif key == "gap":
        for _ in range(n):
            s = "".join(R.choice("ab") for _ in range(R.randint(0, 11)))
            t = "".join(R.choice("ab") for _ in range(R.randint(0, 5)))
            out.append([s, t])
    elif key == "kwords":
        dicts = [["a", "aa"], ["ab", "a", "b"], ["cat", "cats", "and", "sand", "dog"], ["x", "xx", "xxx"]]
        for _ in range(n):
            d = R.choice(dicts)
            s = "".join(R.choice(d) for _ in range(R.randint(0, 4))) if R.random() < 0.8 else \
                "".join(R.choice("abx") for _ in range(R.randint(0, 5)))
            out.append([s, d, R.randint(1, 5)])
    elif key == "bracket":
        for _ in range(n):
            out.append(["".join(R.choice("()[]") for _ in range(R.randint(0, 12)))])
    elif key == "int3":
        for _ in range(n):
            a = "".join(R.choice("ab") for _ in range(R.randint(0, 4)))
            b = "".join(R.choice("ab") for _ in range(R.randint(0, 4)))
            d = "".join(R.choice("ab") for _ in range(R.randint(0, 3)))
            if R.random() < 0.5:
                ai = bi = di = 0; c = []
                while ai < len(a) or bi < len(b) or di < len(d):
                    ch = R.choice([x for x, ok in (("a", ai < len(a)), ("b", bi < len(b)), ("d", di < len(d))) if ok])
                    if ch == "a": c.append(a[ai]); ai += 1
                    elif ch == "b": c.append(b[bi]); bi += 1
                    else: c.append(d[di]); di += 1
                c = "".join(c)
            else:
                c = "".join(R.choice("ab") for _ in range(len(a) + len(b) + len(d)))
            out.append([a, b, d, c])
    return out


def clean(code):
    if "```" in code:
        m = re.search(r"```(?:python)?\s*(.*?)```", code, re.DOTALL)
        if m: code = m.group(1)
    return code.strip()


def run_on(key, code, inputs, timeout=12):
    p = ct.PROBLEMS[key]
    runner = (clean(code) + "\n\nimport json\n"
              f"_inp=json.loads(r'''{json.dumps(inputs)}''')\n"
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


def norm(v):  # normalize for comparison (bools vs ints)
    if v is True: return "T"
    if v is False: return "F"
    return str(v)


probs = []
for r in rows:
    if r["problem"] not in probs: probs.append(r["problem"])
conds = ["baseline", "engine"]

FUZZ = {k: fuzz_inputs(k, NFUZZ) for k in probs}
EXP = {k: [norm(ct.PROBLEMS[k]["ref"](*[json.loads(json.dumps(a)) for a in args])) for args in FUZZ[k]] for k in probs}

# evaluate each solution on fuzz inputs
sol = {}  # (problem,cond) -> list of {fuzz_ok, outs}
for pk in probs:
    for c in conds:
        lst = []
        for r in [x for x in rows if x["problem"] == pk and x["condition"] == c]:
            outs = run_on(pk, r["code"], FUZZ[pk])
            outs_n = [norm(o) for o in outs] if outs else None
            fuzz_ok = outs_n is not None and outs_n == EXP[pk]
            lst.append({"ok": fuzz_ok, "outs": outs_n})
        sol[(pk, c)] = lst


def pass_at_k(n, c, k):
    if k > n: return float("nan")
    if n - c < k: return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


print("=" * 78)
print(f"FUZZ RE-EVALUATION — {NFUZZ} adversarial inputs/problem vs the trusted reference")
print("=" * 78)
print(f"\n{'problem':10}{'fixed/N':>12}{'  fuzz pass@1 (correct sols / total)':>42}")
fixed_fail = 0
for pk in probs:
    for c in conds:
        lst = sol[(pk, c)]
        cc = sum(x["ok"] for x in lst)
        print(f"{pk:10}{c:>8}{'':>2}{cc}/{len(lst)} solutions pass all {NFUZZ} fuzzed inputs")
    print()

print("## fuzzed pass@k (unbiased estimator, mean over problems)")
n_per = min(len(sol[(pk, c)]) for pk in probs for c in conds)
for k in [1, 2, 3, n_per]:
    if k > n_per: continue
    line = f"  k={k}: "
    for c in conds:
        vals = [pass_at_k(len(sol[(pk, c)]), sum(x["ok"] for x in sol[(pk, c)]), k) for pk in probs]
        line += f"{c}={np.mean(vals):.3f}  "
    print(line)

print("\n## DIFFERENTIAL TESTING — diversity as a correctness oracle (no reference needed)")
print("   For each fuzzed input, pool all solutions' outputs; a DISAGREEMENT means >=1 is buggy.")
tot_dis = 0; maj_correct = 0; maj_total = 0; single_bug = 0; single_total = 0
examples = {}
import random as _r
rng = _r.Random(0)
for pk in probs:
    allsol = [x for c in conds for x in sol[(pk, c)] if x["outs"]]
    if len(allsol) < 2: continue
    dis_here = 0
    for i in range(len(FUZZ[pk])):
        votes = [s["outs"][i] for s in allsol]
        cnt = Counter(votes)
        if len(cnt) > 1:                                  # disagreement => a bug is exposed
            dis_here += 1; tot_dis += 1
            maj = cnt.most_common(1)[0][0]
            maj_total += 1
            if maj == EXP[pk][i]: maj_correct += 1
            if pk not in examples:
                examples[pk] = {"input": FUZZ[pk][i], "votes": dict(cnt), "majority": maj, "reference": EXP[pk][i]}
    # single-pick robustness: a random single solution, on a random fuzzed input, how often buggy?
    for _ in range(200):
        s = rng.choice(allsol); i = rng.randrange(len(FUZZ[pk]))
        single_total += 1
        if s["outs"][i] != EXP[pk][i]: single_bug += 1
    print(f"  {pk:10} disagreement-exposing fuzzed inputs: {dis_here}/{len(FUZZ[pk])}")

print(f"\n  Total bug-exposing disagreements found by diversity: {tot_dis}")
if maj_total:
    print(f"  Majority-vote-over-diverse correct on disagreement cases: {maj_correct}/{maj_total} = {maj_correct/maj_total:.3f}")
print(f"  A single random solution is buggy on a random fuzzed input: {single_bug}/{single_total} = {single_bug/max(single_total,1):.4f}")

print("\n## a concrete bug caught by diversity (found WITHOUT the reference, then confirmed against it)")
for pk, ex in examples.items():
    print(f"  {pk}: input={ex['input']}  -> diverse outputs {ex['votes']}; majority={ex['majority']}, reference={ex['reference']}"
          + ("  [majority == reference: the buggy minority is outvoted]" if str(ex['majority']) == str(ex['reference']) else "  [majority WRONG]"))

json.dump({"nfuzz": NFUZZ,
           "fuzz_correct": {f"{pk}|{c}": sum(x["ok"] for x in sol[(pk, c)]) for pk in probs for c in conds},
           "total_disagreements": tot_dis, "majority_correct_rate": (maj_correct / maj_total) if maj_total else None,
           "single_bug_rate": single_bug / max(single_total, 1)},
          open("bench/data/fuzz_results.json", "w", encoding="utf-8"), indent=2)
print("\nsaved -> bench/data/fuzz_results.json")
