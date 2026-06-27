"""
run_reasoning.py — score the reasoning-strategy benchmark (baseline vs always-divergent vs router).

Accuracy per strategy, overall and on the TRAP subset (tasks whose obvious answer is wrong), where
strategy should matter most. Generation and scoring are separate; checkers are the objective ones in
reasoning_tasks.py. Permutation test on paired per-cell correctness for router vs the others.
Usage: python bench/run_reasoning.py [bench/data/reasoning_raw.json]
"""
import sys, os, re, json, importlib
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RAW = sys.argv[1] if len(sys.argv) > 1 else "bench/data/reasoning_raw.json"
MODULE = sys.argv[2] if len(sys.argv) > 2 else "reasoning_tasks"
rt = importlib.import_module(MODULE)
rows = json.load(open(RAW, encoding="utf-8"))
TRAPS = getattr(rt, "TRAPS", {"monty_hall", "base_rate", "look_and_say", "bear_riddle", "knights_knaves"})


def clean_code(c):
    if "```" in c:
        m = re.search(r"```(?:python)?\s*(.*?)```", c, re.DOTALL)
        if m: c = m.group(1)
    return c.strip()


def _regions(a):
    """Candidate 'stated final answer' snippets — so a verbose answer is graded on the answer it states,
    not penalized for MENTIONING distractor tokens in its reasoning (the artifact we caught)."""
    lines = [ln.strip() for ln in a.splitlines() if ln.strip()]
    regs = [a]                                   # whole text (fine for any-match numeric checks)
    if lines:
        regs += [lines[0], lines[-1]]            # answer often stated first or last
    m = re.search(r"(?:final answer|answer)\s*[:\-]?\s*(.+)$", a, re.IGNORECASE)
    if m: regs.append(m.group(1).strip()[:80])
    return regs


def correct(row):
    t = rt.TASKS[row["task"]]
    a = row["answer"] or ""
    if t["kind"] == "code":
        try: return bool(t["check"](clean_code(a)))
        except Exception: return False
    try:
        return any(t["check"](r) for r in _regions(a))
    except Exception:
        return False


for r in rows:
    r["ok"] = correct(r)

conds, tasks = [], []
for r in rows:
    if r["condition"] not in conds: conds.append(r["condition"])
    if r["task"] not in tasks: tasks.append(r["task"])
order = [c for c in ["baseline", "divergent", "router"] if c in conds] + [c for c in conds if c not in ("baseline", "divergent", "router")]


def acc(rs):
    return (sum(r["ok"] for r in rs) / len(rs)) if rs else float("nan")


print("=" * 78)
print("REASONING-STRATEGY BENCHMARK — baseline vs always-divergent vs router")
print("=" * 78)
hdr = f"{'task':16}{'family':13}" + "".join(f"{c:>12}" for c in order)
print(hdr); print("-" * len(hdr))
for tk in tasks:
    fam = rt.TASKS[tk]["family"]
    trap = "*" if tk in TRAPS else " "
    cells = []
    for c in order:
        rs = [r for r in rows if r["task"] == tk and r["condition"] == c]
        cells.append(f"{acc(rs):.2f}({sum(r['ok'] for r in rs)}/{len(rs)})")
    print(f"{tk+trap:16}{fam:13}" + "".join(f"{x:>12}" for x in cells))
print("-" * len(hdr))


def block(name, subset_tasks):
    print(f"\n## {name}")
    res = {}
    for c in order:
        rs = [r for r in rows if r["condition"] == c and r["task"] in subset_tasks]
        res[c] = acc(rs)
        print(f"  {c:12} accuracy = {acc(rs):.3f}  ({sum(r['ok'] for r in rs)}/{len(rs)})")
    return res


def perm_paired(a_ok, b_ok, iters=20000, seed=0):
    """Paired permutation test on binary correctness (per matched cell)."""
    a, b = np.array(a_ok, float), np.array(b_ok, float)
    d = a - b
    obs = d.mean()
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(iters):
        s = rng.choice([1, -1], size=len(d))
        if abs((d * s).mean()) >= abs(obs) - 1e-12:
            cnt += 1
    return obs, (cnt + 1) / (iters + 1)


block("Overall accuracy (all tasks)", tasks)
if [t for t in tasks if t in TRAPS]:
    block("TRAP tasks only (obvious answer is wrong)", [t for t in tasks if t in TRAPS])

# router vs others, paired per (task,k) cell
print("\n## Significance (paired permutation, router vs others, per matched cell)")
def paired_vectors(ca, cb):
    A, B = [], []
    for tk in tasks:
        for k in sorted({r["k"] for r in rows if r["task"] == tk}):
            ra = [r for r in rows if r["task"] == tk and r["condition"] == ca and r["k"] == k]
            rb = [r for r in rows if r["task"] == tk and r["condition"] == cb and r["k"] == k]
            if ra and rb:
                A.append(int(ra[0]["ok"])); B.append(int(rb[0]["ok"]))
    return A, B
for other in [c for c in order if c != "router"]:
    if "router" in order:
        A, B = paired_vectors("router", other)
        diff, p = perm_paired(A, B)
        print(f"  router - {other}: Δacc={diff:+.3f}  p={p:.4f}  [{'sig' if p<0.05 else 'n.s.'}]  (n={len(A)} cells)")

out = {c: {"overall": acc([r for r in rows if r["condition"] == c]),
           "traps": acc([r for r in rows if r["condition"] == c and r["task"] in TRAPS])} for c in order}
json.dump({"summary": out, "rows": rows}, open("bench/data/reasoning_results.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("\nsaved -> bench/data/reasoning_results.json")
