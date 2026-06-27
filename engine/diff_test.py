"""
diff_test.py — differential testing: use DIVERSITY as a correctness oracle (no reference solution needed).

The fuzz benchmark (RESULTS.md Benchmark 5) measured a real win: a single forward pass ships a subtly-buggy
solution ~1 in 36 times (passes weak tests, fails fuzzing), but generating DIVERSE solutions and running
them against many random inputs exposes the bug as a DISAGREEMENT — and majority-vote over the diverse set
recovers the correct answer (383/383 disagreement cases in the benchmark). This module is that mechanism,
made reusable: the cognitive engine's `convergent_verify` mode should run it on any code task.

Honest scope: this catches IDIOSYNCRATIC (minority) bugs. If most candidates share the SAME wrong belief
(a systematic error), the majority is wrong and diversity cannot save you — so disagreements are a strong
bug signal but agreement is NOT a correctness proof. We flag that explicitly. ponytail: stdlib only.
"""
import sys, os, json, subprocess, tempfile, re
from collections import Counter


def _run(fn, code, inputs, timeout=12):
    if "```" in code:
        m = re.search(r"```(?:python)?\s*(.*?)```", code, re.DOTALL)
        if m: code = m.group(1)
    runner = (code.strip() + "\n\nimport json\n"
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


def differential_test(fn_name, codes, inputs):
    """Run every candidate (each defining `fn_name`) on `inputs`. Returns a report:
      consensus      : per-input majority output (the answer to ship)
      disagreements  : input indices where candidates disagree (>=1 candidate is buggy there)
      suspect_idx    : candidate indices that ever differ from the consensus (likely buggy)
      agreement      : fraction of inputs with unanimous agreement
      warning        : reminder that agreement != correctness (systematic bugs survive)
    """
    outs = [_run(fn_name, c, inputs) for c in codes]
    ok = [o for o in outs if o is not None and len(o) == len(inputs)]
    if len(ok) < 2:
        return {"error": "need >=2 runnable candidates", "runnable": len(ok)}
    consensus, disagreements = [], []
    for i in range(len(inputs)):
        votes = Counter(str(o[i]) for o in ok)
        consensus.append(votes.most_common(1)[0][0])
        if len(votes) > 1:
            disagreements.append(i)
    suspect = []
    for ci, o in enumerate(outs):
        if o is None or len(o) != len(inputs):
            suspect.append(ci); continue
        if any(str(o[i]) != consensus[i] for i in range(len(inputs))):
            suspect.append(ci)
    return {
        "consensus": consensus,
        "disagreements": disagreements,
        "suspect_candidate_idx": suspect,
        "agreement": 1.0 - len(disagreements) / len(inputs),
        "runnable": len(ok),
        "warning": "disagreement => >=1 candidate is buggy; agreement does NOT prove correctness (a "
                   "systematic bug shared by the majority survives). Treat disagreements as must-investigate.",
    }


if __name__ == "__main__":
    # self-check: 3 correct candidates + 1 with a planted off-by-one bug; the bug must be caught.
    good = "def f(xs):\n return sorted(set(xs))"
    good2 = "def f(xs):\n out=[]\n for x in sorted(xs):\n  if x not in out: out.append(x)\n return out"
    good3 = "def f(xs):\n return sorted(list(dict.fromkeys(xs)))"
    buggy = "def f(xs):\n s=sorted(set(xs))\n return s[1:] if s else s   # planted bug: drops the smallest"
    inputs = [[[3, 1, 2, 1]], [[5]], [[]], [[2, 2, 2]], [[9, 1, 9, 4]]]
    rep = differential_test("f", [good, good2, good3, buggy], inputs)
    assert rep["disagreements"], "should have caught the planted bug via disagreement"
    assert 3 in rep["suspect_candidate_idx"], "the buggy candidate (idx 3) must be flagged"
    assert 0 not in rep["suspect_candidate_idx"], "a correct candidate must not be flagged"
    # consensus should equal the correct answer (buggy is outvoted 3-to-1)
    assert rep["consensus"][0] == "[1, 2, 3]", rep["consensus"][0]
    print(f"diff_test self-check passed: caught planted bug at candidate {rep['suspect_candidate_idx']}, "
          f"consensus correct, agreement={rep['agreement']:.2f}")
