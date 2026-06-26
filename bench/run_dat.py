"""
run_dat.py — score the DAT benchmark honestly.

Reports BOTH axes the literature says you must separate (Wenger & Kenett 2025):
  * within-list DAT  : per-response divergence (is each answer internally spread out?)
  * population spread : between-response diversity (are independent answers distinct, or collapsed
                        onto the same vocabulary?)  <- the axis a per-item metric hides.
Plus lexical homogeneity (recurring-word overlap) as a model-free cross-check. Every comparison gets a
bootstrap 95% CI and a permutation-test p-value. Scoring uses the SemDis-style embedding ensemble.

Usage: python bench/run_dat.py [bench/data/dat_raw.json]
"""
import sys, json, itertools
from collections import Counter
import numpy as np
import score

RAW = sys.argv[1] if len(sys.argv) > 1 else "bench/data/dat_raw.json"
rows = json.load(open(RAW, encoding="utf-8"))
conds = []
for r in rows:
    if r["condition"] not in conds:
        conds.append(r["condition"])


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if (a | b) else 0.0


def sanitize(words):
    """Keep only clean single-word tokens (DAT rule), drop junk/non-English so all conditions are fair."""
    import re
    out = []
    for w in words:
        w = str(w).strip().lower()
        if re.fullmatch(r"[a-z][a-z'-]{1,}", w) and w not in out:
            out.append(w)
    return out


def analyze(cond):
    rs = [r for r in rows if r["condition"] == cond]
    wordsets = [sanitize(r["words"]) for r in rs]
    wordsets = [ws for ws in wordsets if len(ws) >= 7]   # need 7 valid words to score DAT
    # 1) per-response DAT (first 7 words; length controlled by construction)
    dat = [score.dat_score(ws, k=7) for ws in wordsets]
    # 2) population spread: each trial -> ensemble centroid; per-trial mean distance to the OTHER trials
    cents = [score.centroid_ensemble(ws) for ws in wordsets]      # cents[i] = list over models
    nm = len(score.ENSEMBLE)
    pop = []
    for i in range(len(wordsets)):
        per_model = []
        for mi in range(nm):
            ci = cents[i][mi]
            ds = [1.0 - float(ci @ cents[j][mi]) for j in range(len(wordsets)) if j != i]
            per_model.append(np.mean(ds))
        pop.append(float(np.mean(per_model)))
    # 3) lexical homogeneity: per-trial mean Jaccard overlap with the other trials (higher = collapsed)
    overlap = []
    for i in range(len(wordsets)):
        overlap.append(float(np.mean([jaccard(wordsets[i], wordsets[j])
                                      for j in range(len(wordsets)) if j != i])))
    allw = [w for ws in wordsets for w in ws]
    ttr = len(set(allw)) / len(allw)
    top = Counter(allw).most_common(8)
    return {"dat": dat, "pop": pop, "overlap": overlap, "ttr": ttr, "top": top, "n": len(rs)}


A = {c: analyze(c) for c in conds}


def line(name, key, higher_is_better=True, scale=1.0):
    print(f"\n## {name}  (higher = {'MORE' if higher_is_better else 'LESS'} divergent)")
    vals = {}
    for c in conds:
        m, lo, hi, n = score.bootstrap_ci([v * scale for v in A[c][key]])
        vals[c] = [v * scale for v in A[c][key]]
        print(f"  {c:12} mean={m:7.3f}  95% CI=[{lo:7.3f},{hi:7.3f}]  n={n}")
    if "baseline" in conds:
        for c in conds:
            if c == "baseline":
                continue
            diff, p = score.permutation_test(vals[c], vals["baseline"])
            verdict = "SIGNIFICANT" if p < 0.05 else "n.s."
            print(f"  delta({c} - baseline) = {diff:+.3f}   permutation p = {p:.4f}   [{verdict}]")


print("=" * 78)
print("DAT BENCHMARK — divergence prompting vs the standard DAT instruction")
print("embedding ensemble:", ", ".join(score.ENSEMBLE))
print("=" * 78)
line("AXIS 1 — within-response DAT (per-answer spread)", "dat", True)
line("AXIS 2 — population spread (between-answer diversity)", "pop", True)
line("AXIS 3 — lexical homogeneity (recurring-word overlap)", "overlap", False)

print("\n## Vocabulary concentration (model-free)")
for c in conds:
    print(f"  {c:12} type/token={A[c]['ttr']:.3f}  top: " +
          ", ".join(f"{w}×{n}" for w, n in A[c]['top'][:6]))

out = {c: {"dat_mean": float(np.mean(A[c]['dat'])), "pop_mean": float(np.mean(A[c]['pop'])),
           "overlap_mean": float(np.mean(A[c]['overlap'])), "ttr": A[c]['ttr'],
           "top": A[c]['top'], "n": A[c]['n'],
           "dat": A[c]['dat'], "pop": A[c]['pop'], "overlap": A[c]['overlap']} for c in conds}
json.dump(out, open("bench/data/dat_results.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("\nsaved -> bench/data/dat_results.json")
