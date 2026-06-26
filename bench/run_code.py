"""
run_code.py — score the coding solution-diversity benchmark.

For each (problem, condition): check correctness in isolation, then among the CORRECT solutions measure
  * distinct_structural : # of unique AST-skeleton clusters (different algorithms, not different names)
  * semantic_spread     : mean pairwise embedding distance of the correct solutions' source
  * top_cluster_share   : fraction of correct solutions in the single most common structure (collapse)
Correctness here is ~saturated by design — the signal is whether divergence prompting actually explores
the SOLUTION SPACE or re-derives the canonical answer the way best-of-N does.

n=3 problems: this is a descriptive complement to the (inferential) DAT benchmark, reported as such.
Usage: python bench/run_code.py [bench/data/code_raw.json]
"""
import sys, os, re, json
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import code_problems as cp
import score

RAW = sys.argv[1] if len(sys.argv) > 1 else "bench/data/code_raw.json"
rows = json.load(open(RAW, encoding="utf-8"))


def clean(code):
    """Strip markdown fences / prose the model may have added; keep the code body."""
    if "```" in code:
        m = re.search(r"```(?:python)?\s*(.*?)```", code, re.DOTALL)
        if m:
            code = m.group(1)
    return code.strip()


conds, probs = [], []
for r in rows:
    if r["condition"] not in conds: conds.append(r["condition"])
    if r["problem"] not in probs: probs.append(r["problem"])

results = {}
for pk in probs:
    for c in conds:
        sols = [clean(r["code"]) for r in rows if r["problem"] == pk and r["condition"] == c]
        correct = [s for s in sols if cp.check(pk, s)]
        sigs = [cp.structural_sig(s) for s in correct]
        sigs = [s for s in sigs if s]
        cnt = Counter(sigs)
        distinct = len(cnt)
        top_share = (cnt.most_common(1)[0][1] / len(sigs)) if sigs else 0.0
        sem = score.set_diversity(correct) if len(correct) >= 2 else 0.0
        results[(pk, c)] = {"n": len(sols), "correct": len(correct), "distinct_structural": distinct,
                            "top_cluster_share": top_share, "semantic_spread": sem}

print("=" * 80)
print("CODING SOLUTION-DIVERSITY — best-of-N baseline vs lens-diverse engine (n=3 problems)")
print("=" * 80)
hdr = f"{'problem':12}{'cond':10}{'correct':>9}{'distinctAlgos':>15}{'topShare':>10}{'semSpread':>11}"
print(hdr); print("-" * len(hdr))
for pk in probs:
    for c in conds:
        r = results[(pk, c)]
        print(f"{pk:12}{c:10}{r['correct']:>4}/{r['n']:<4}{r['distinct_structural']:>15}{r['top_cluster_share']:>10.2f}{r['semantic_spread']:>11.3f}")
    print("-" * len(hdr))

print("\nAGGREGATE (mean over problems):")
for c in conds:
    da = sum(results[(pk, c)]["distinct_structural"] for pk in probs) / len(probs)
    ts = sum(results[(pk, c)]["top_cluster_share"] for pk in probs) / len(probs)
    ss = sum(results[(pk, c)]["semantic_spread"] for pk in probs) / len(probs)
    cor = sum(results[(pk, c)]["correct"] for pk in probs)
    tot = sum(results[(pk, c)]["n"] for pk in probs)
    print(f"  {c:10} correct={cor}/{tot}  mean distinct-algorithms={da:.2f}  mean top-cluster-share={ts:.2f}  mean semantic-spread={ss:.3f}")

out = {f"{pk}|{c}": results[(pk, c)] for pk in probs for c in conds}
json.dump(out, open("bench/data/code_results.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("\nsaved -> bench/data/code_results.json")
