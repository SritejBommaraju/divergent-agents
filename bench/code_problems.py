"""
code_problems.py — problem set + trusted checkers for the coding solution-diversity benchmark.

Question tested: when many correct algorithms exist, does divergence-prompting actually produce
structurally DIFFERENT correct solutions, or does the agent re-derive the same canonical one (the way
best-of-N does)? Correctness is checkable and not the bottleneck — solution DIVERSITY is the signal.

Each candidate is executed in an isolated subprocess with a timeout (generation and scoring are kept
separate; the model never grades itself). ponytail: stdlib only.
"""
import os, sys, json, subprocess, tempfile, ast, hashlib

# ---- trusted reference implementations (used only to check candidates) ----
def _fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def _palin(s):
    t = [c.lower() for c in s if c.isalnum()]
    return t == t[::-1]

def _primes(n):
    if n < 2:
        return []
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [i for i, p in enumerate(sieve) if p]

PROBLEMS = {
    "fib": {
        "fn": "fib",
        "spec": ("Write a Python function `fib(n)` that returns the n-th Fibonacci number, 0-indexed, "
                 "with fib(0)=0 and fib(1)=1. Handle n up to 30."),
        "inputs": [[i] for i in range(0, 31)],
        "ref": _fib,
    },
    "palindrome": {
        "fn": "is_palindrome",
        "spec": ("Write a Python function `is_palindrome(s)` that returns True iff the string s is a "
                 "palindrome considering only alphanumeric characters and ignoring case."),
        "inputs": [["A man, a plan, a canal: Panama"], ["race a car"], [""], ["0P"], ["abccba"],
                   ["Was it a car or a cat I saw?"], ["No lemon, no melon"], ["x"], ["ab"], ["12321"]],
        "ref": _palin,
    },
    "primes": {
        "fn": "primes_up_to",
        "spec": ("Write a Python function `primes_up_to(n)` that returns the sorted list of all prime "
                 "numbers <= n (empty list for n < 2)."),
        "inputs": [[0], [1], [2], [10], [30], [100], [1], [50], [13], [97]],
        "ref": _primes,
    },
}

LENSES = [  # Stage-1 divergence applied to code: each candidate forced to a different approach
    "Use a fundamentally different algorithm than the most obvious one.",
    "Solve it recursively.",
    "Solve it iteratively with O(1) extra space if possible.",
    "Use a mathematically clever / closed-form or number-theoretic trick.",
    "Avoid the standard-library function that trivializes this; implement the logic yourself.",
    "Use a functional style (map/filter/reduce/comprehensions, no explicit mutation).",
    "Use memoization / dynamic programming.",
    "Use a generator or lazy evaluation.",
    "Optimize for readability with an unusual but clear structure.",
    "Use an approach a competitive programmer would pick for speed.",
]


def check(problem_key, code, timeout=8):
    """Run candidate `code` against the reference on all inputs in an isolated subprocess.
    Returns True iff every output matches. Never raises."""
    p = PROBLEMS[problem_key]
    expected = [p["ref"](*args) for args in p["inputs"]]
    runner = (
        code + "\n\n"
        "import json,sys\n"
        f"_inp=json.loads(r'''{json.dumps(p['inputs'])}''')\n"
        f"_exp=json.loads(r'''{json.dumps(expected)}''')\n"
        "ok=True\n"
        "for a,e in zip(_inp,_exp):\n"
        f"    try:\n        r={p['fn']}(*a)\n        bad=(list(r)!=list(e)) if isinstance(e,list) else (r!=e)\n        if bad: ok=False;break\n"
        "    except Exception: ok=False;break\n"
        "print('PASS' if ok else 'FAIL')\n"
    )
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
            fh.write(runner); path = fh.name
        out = subprocess.run([sys.executable, path], capture_output=True, text=True,
                             timeout=timeout, cwd=tempfile.gettempdir())
        return out.stdout.strip().endswith("PASS")
    except Exception:
        return False
    finally:
        try: os.unlink(path)
        except Exception: pass


def structural_sig(code):
    """Canonical AST signature: node-type skeleton with all identifiers/constants erased, so two
    solutions hash equal iff they share the same control/expression STRUCTURE (not naming/cosmetics).
    Returns None if the code doesn't parse."""
    try:
        tree = ast.parse(code)
    except Exception:
        return None
    parts = []
    for node in ast.walk(tree):
        parts.append(type(node).__name__)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            parts.append(f"args:{len(node.args.args)}")
    skel = ",".join(parts)
    return hashlib.sha1(skel.encode()).hexdigest()[:12]
