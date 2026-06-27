"""
reasoning_tasks_hard.py — HARDER, NOVEL, checkable reasoning tasks (v2 of the set).

The v1 set hit 100% for every strategy: frontier models have memorized Monty Hall, the bear riddle, etc.,
so strategy couldn't separate. These tasks are custom (unique numbers/structure, not famous), so the
model must actually work them out — creating headroom where careful mode-discipline + verification can
help at a low internal-effort budget. Checkers are objective. ponytail: stdlib only.
"""
import re, sys, subprocess, tempfile, os

def _nums(t): return [float(x) for x in re.findall(r"-?\d+\.?\d*", t.replace(",", ""))]
def _alpha(t): return set(re.findall(r"[a-z]+", t.lower()))
def _has(t, v, tol=1e-6): return any(abs(x - v) <= tol for x in _nums(t))


def _check_run(code, timeout=8):
    runner = (code + "\n\n"
        "cases=[[[1,2,1,2,3,4,1]],[[5,4,3,2,1]],[[]],[[1,1,1]],[[1,2,3,4,5]],[[3,3,4,5,1,2]]]\n"
        "exp=[4,1,0,1,5,3]\n"
        "ok=all(longest_increasing_run(*c)==e for c,e in zip(cases,exp))\n"
        "print('PASS' if ok else 'FAIL')\n")
    try:
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False, encoding='utf-8') as fh:
            fh.write(runner); path = fh.name
        out = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=timeout,
                             cwd=tempfile.gettempdir())
        return out.stdout.strip().endswith('PASS')
    except Exception:
        return False
    finally:
        try: os.unlink(path)
        except Exception: pass


TASKS = {
    "houses_logic": {  # answer: position 2 = red
        "kind": "short", "family": "deductive",
        "prompt": ("Five houses stand in a row, positions 1-5 (left to right), each a different color: "
                   "red, blue, green, white, yellow. Clues: (a) the yellow house is at position 1; "
                   "(b) the blue house is at position 5; (c) the green house is immediately to the right "
                   "of the white house; (d) the white house is NOT adjacent to the yellow house. "
                   "What color is the house at position 2? Answer with one color word."),
        "check": lambda a: ("red" in _alpha(a)) and not (_alpha(a) & {"blue", "green", "white", "yellow"}),
    },
    "knaves3": {  # answer: Quinn
        "kind": "short", "family": "deductive",
        "prompt": ("Three islanders: Pat, Quinn, Rosa. Knights always tell the truth; knaves always lie. "
                   "Pat says 'Quinn is a knave.' Quinn says 'Rosa is a knave.' Rosa says 'Pat and Quinn "
                   "are both knaves.' Exactly one of them is a knight. Who is the knight? Answer one name."),
        "check": lambda a: ("quinn" in _alpha(a)) and not (_alpha(a) & {"pat", "rosa"}),
    },
    "increasing_digits": {  # answer: 126
        "kind": "short", "family": "combinatorial",
        "prompt": ("How many 4-digit numbers (from 1000 to 9999) have all four digits strictly increasing "
                   "from left to right? Answer with the number."),
        "check": lambda a: _has(a, 126),
    },
    "sequence_custom": {  # 3,4,7,11,18,29 -> 47 (each term = sum of previous two)
        "kind": "short", "family": "inductive",
        "prompt": ("Find the next term: 3, 4, 7, 11, 18, 29, ? Answer with only the next number."),
        "check": lambda a: _has(a, 47),
    },
    "water_tank": {  # answer: 40 minutes
        "kind": "short", "family": "arithmetic",
        "prompt": ("A 240-liter tank starts empty. Pipe A fills it at 12 L/min and runs the whole time. "
                   "Pipe B drains it at 8 L/min but is opened only 5 minutes after pipe A starts. How "
                   "many minutes after pipe A starts does the tank first contain exactly 200 liters? "
                   "Answer with the number of minutes."),
        "check": lambda a: _has(a, 40),
    },
    "marbles_prob": {  # P(both red) = 5/14 ~= 0.36
        "kind": "short", "family": "probabilistic",
        "prompt": ("A bag has 5 red and 3 blue marbles. You draw 2 at random without replacement. What "
                   "is the probability that both are red? Answer as a decimal rounded to two places."),
        "check": lambda a: any(0.34 <= x <= 0.37 for x in _nums(a)) or ("5/14" in a.replace(" ", "")),
    },
    "longest_run_code": {
        "kind": "code", "family": "algorithmic",
        "prompt": ("Write ONLY a Python function `longest_increasing_run(xs)` that returns the length of "
                   "the longest contiguous run of strictly increasing elements. E.g. [1,2,1,2,3,4,1] -> 4, "
                   "[5,4,3,2,1] -> 1, [] -> 0. No prose, no markdown fences."),
        "check": _check_run,
    },
}

if __name__ == "__main__":
    gold = {
        "houses_logic": "red", "knaves3": "Quinn", "increasing_digits": "126",
        "sequence_custom": "47", "water_tank": "40 minutes", "marbles_prob": "0.36",
        "longest_run_code": ("def longest_increasing_run(xs):\n best=0; cur=0; prev=None\n"
                             " for x in xs:\n  if prev is None or x>prev: cur+=1\n  else: cur=1\n"
                             "  best=max(best,cur); prev=x\n return best"),
    }
    bad = {"houses_logic": "green", "knaves3": "Pat", "increasing_digits": "210",
           "sequence_custom": "40", "water_tank": "35", "marbles_prob": "0.42"}
    for k, t in TASKS.items():
        assert t["check"](gold[k]), f"GOLD failed: {k}"
    for k, a in bad.items():
        assert not TASKS[k]["check"](a), f"WRONG passed: {k}"
    print(f"reasoning_tasks_hard self-check passed: {len(TASKS)} tasks")
