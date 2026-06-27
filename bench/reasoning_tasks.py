"""
reasoning_tasks.py — a small, checkable, MIXED-reasoning task set + trusted checkers.

The point: different tasks need different thinking (deductive logic, Bayesian base-rate, lateral insight,
multi-step arithmetic, induction, algorithmic). A one-trick engine (always brainstorm) should NOT beat a
router that matches the mode to the task. Several tasks are deliberate TRAPS where the obvious answer is
wrong — those discriminate strategies. Checkers are objective (normalized match / number / code exec).

ponytail: stdlib only.
"""
import re, sys, subprocess, tempfile, os, json


def _nums(t):
    return [float(x) for x in re.findall(r"-?\d+\.?\d*", t.replace(",", ""))]

def _alpha(t):
    return set(re.findall(r"[a-z]+", t.lower()))


def _check_code_dedup(code, timeout=8):
    runner = (code + "\n\n"
        "import json\n"
        "cases=[[[1,1,2,3,3,3,2,4]],[[]],[['a','b','a','c','b']],[[5]],[[2,2,2,2]]]\n"
        "exp=[[1,2,3,4],[],['a','b','c'],[5],[2]]\n"
        "ok=all(list(dedup_stable(*c))==e for c,e in zip(cases,exp))\n"
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
    "logic_order": {
        "kind": "short", "family": "deductive",
        "prompt": ("Five people. Alice is taller than Bob. Carol is taller than Alice. Dan is shorter "
                   "than Bob. Eve is taller than Carol. Order them tallest to shortest; answer with ONLY "
                   "the single name of the person in the MIDDLE (3rd tallest)."),
        "check": lambda a: ("alice" in _alpha(a)) and not (_alpha(a) & {"bob", "carol", "dan", "eve"}),
    },
    "knights_knaves": {
        "kind": "short", "family": "deductive",
        "prompt": ("On an island, knights always tell the truth and knaves always lie. A says 'B is a "
                   "knave'. B says 'A and I are the same type'. What is B? Answer exactly one word: "
                   "'knight' or 'knave'."),
        "check": lambda a: re.sub(r"[^a-z]", "", a.lower()) == "knave"
                            or (("knave" in _alpha(a)) and ("knight" not in _alpha(a))),
    },
    "monty_hall": {
        "kind": "short", "family": "bayesian",
        "prompt": ("Game show: 3 doors, one hides a car. You pick door 1. The host, who knows where the "
                   "car is, opens door 3 to reveal a goat, then offers to let you switch to door 2. To "
                   "maximize your chance of the car, answer exactly one word: 'switch' or 'stay'."),
        "check": lambda a: "switch" in a.lower(),
    },
    "base_rate": {
        "kind": "short", "family": "bayesian",
        "prompt": ("A disease affects 1 in 10000 people. A test is 99% accurate (99% true-positive rate "
                   "and 99% true-negative rate). You test positive. Approximately what is the probability "
                   "you actually have the disease? Answer as a percentage."),
        "check": lambda a: any(0.4 <= x <= 1.6 for x in _nums(a)) if _nums(a) else False,
    },
    "look_and_say": {
        "kind": "short", "family": "inductive",
        "prompt": ("What comes next in this sequence: 1, 11, 21, 1211, 111221, ? "
                   "Answer with only the next term."),
        "check": lambda a: "312211" in re.sub(r"[^0-9]", "", a),
    },
    "pen_change": {
        "kind": "short", "family": "arithmetic",
        "prompt": ("A store sells pens at 3 for $2. Maria buys 12 pens, uses a coupon for $1 off the "
                   "total, and pays with a $20 bill. How much change does she get, in dollars? Answer "
                   "with the number."),
        "check": lambda a: bool(_nums(a)) and abs(_nums(a)[0] - 13) < 1e-6,
    },
    "bear_riddle": {
        "kind": "short", "family": "lateral",
        "prompt": ("A man builds a house with all four walls facing south. A bear wanders past. "
                   "What color is the bear? Answer with one word."),
        "check": lambda a: "white" in a.lower(),
    },
    "dedup_code": {
        "kind": "code", "family": "algorithmic",
        "prompt": ("Write ONLY a Python function `dedup_stable(xs)` that returns a list with duplicates "
                   "removed, preserving the order of first occurrence. No prose, no markdown fences."),
        "check": _check_code_dedup,
    },
}


if __name__ == "__main__":
    # Self-check: the trusted ANSWERS pass their own checkers (guards against a wrong checker).
    gold = {
        "logic_order": "Alice", "knights_knaves": "knave", "monty_hall": "switch",
        "base_rate": "about 1%", "look_and_say": "312211", "pen_change": "13",
        "bear_riddle": "white",
        "dedup_code": "def dedup_stable(xs):\n seen=set(); out=[]\n for x in xs:\n  if x not in seen: seen.add(x); out.append(x)\n return out",
    }
    bad = {"logic_order": "Carol", "monty_hall": "stay", "base_rate": "99%", "bear_riddle": "brown",
           "look_and_say": "123456", "pen_change": "12", "knights_knaves": "knight"}
    for k, t in TASKS.items():
        assert t["check"](gold[k]), f"GOLD failed checker: {k}"
    for k, a in bad.items():
        assert not TASKS[k]["check"](a), f"WRONG answer wrongly passed: {k}"
    print(f"reasoning_tasks self-check passed: {len(TASKS)} tasks, gold all pass, wrong all fail")
