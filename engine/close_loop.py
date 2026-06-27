"""
close_loop.py — the learning loop closed on a REAL EXTERNAL signal (not self-assessment).

The honest gap in v2 was that engine/learn.py defaulted to self-scored records. Here we close the loop
on the only place we have measured, significant variance: the DAT population-diversity benchmark
(Benchmark 1), where the 'archive' strategy beat 'baseline'/'divergence' at p<0.0001.

Protocol (train/test, so this tests GENERALIZATION, not memorization):
  1. Split each strategy's per-trial external diversity scores into train/test halves.
  2. Feed TRAIN scores into the playbook as EXTERNAL records.
  3. The router recommends a strategy for 'maximize_diversity'.
  4. Verify on the held-out TEST half that the learned choice is actually best — and measure the gain.

This is the engine "becoming better": routing learned from data, validated out-of-sample. ponytail: stdlib.
"""
import json, os, sys, random, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import learn

res = json.load(open("bench/data/dat_results.json", encoding="utf-8"))
STRATS = [s for s in ("baseline", "divergence", "archive") if s in res]
data = {s: res[s]["pop"] for s in STRATS}          # per-trial population-diversity (external, objective)

rng = random.Random(0)
train, test = {}, {}
for s in STRATS:
    idx = list(range(len(data[s]))); rng.shuffle(idx)
    h = len(idx) // 2
    train[s] = [data[s][i] for i in idx[:h]]
    test[s] = [data[s][i] for i in idx[h:]]

learn.PB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "diversity_playbook.json")
os.makedirs(os.path.dirname(learn.PB), exist_ok=True)
if os.path.exists(learn.PB):
    os.unlink(learn.PB)

TASK = "maximize_diversity"
for s in STRATS:
    for score in train[s]:
        learn.record(TASK, [s], score, "external")   # external signal, honestly labeled

rec = learn.recommend(TASK, min_uses=2)
learned = rec["plan"][0]

test_mean = {s: statistics.mean(test[s]) for s in STRATS}
best_test = max(test_mean, key=test_mean.get)
routed = test_mean[learned]
base = test_mean.get("baseline", min(test_mean.values()))
rand = statistics.mean(test_mean.values())

print("=" * 70)
print("CLOSED-LOOP LEARNING on the real DAT population-diversity signal")
print("=" * 70)
print(f"strategies: {STRATS}")
print(f"train means: {{ {', '.join(f'{s}:{statistics.mean(train[s]):.3f}' for s in STRATS)} }}")
print(f"LEARNED recommendation for '{TASK}': {learned}")
print(f"held-out TEST means: {{ {', '.join(f'{s}:{test_mean[s]:.3f}' for s in STRATS)} }}")
print(f"best on held-out test: {best_test}")
print(f"generalized (learned == held-out best): {learned == best_test}")
print(f"\nrouted(learned) test diversity = {routed:.3f}")
print(f"baseline test diversity        = {base:.3f}")
print(f"random-strategy avg            = {rand:.3f}")
print(f"=> learned routing beats baseline by +{routed - base:.3f} and random by +{routed - rand:.3f} (out of sample)")

assert learned == best_test, "learning failed to generalize"
json.dump({"task": TASK, "learned": learned, "test_means": test_mean,
           "gain_vs_baseline": routed - base, "generalized": learned == best_test},
          open(os.path.join(os.path.dirname(learn.PB), "close_loop_result.json"), "w", encoding="utf-8"), indent=2)
print("\nclose_loop: learning generalized out-of-sample. saved -> engine/data/close_loop_result.json")
