"""
code_hard.py — HARD coding problems with TRUSTED (brute-validated) checkers, for a proper pass@k benchmark.

The reasoning benchmarks hit a ceiling because a frontier model solves anything easy. These are
genuinely tricky (regex/wildcard matching, decode-ways, interleaving, distinct-subsequences, …) and run
at LOW effort, so single-pass fails a meaningful fraction — creating the headroom a proper coverage /
pass@k comparison needs. Every checker uses a canonical reference whose correctness is pinned by
hand-verified cases in the self-check; candidates run isolated in a subprocess. ponytail: stdlib only.
"""
import sys, os, json, subprocess, tempfile, random
from functools import lru_cache

# ---------- trusted reference implementations ----------
def ref_regex(s, p):
    @lru_cache(None)
    def go(i, j):
        if j == len(p): return i == len(s)
        first = i < len(s) and p[j] in (s[i], '.')
        if j + 1 < len(p) and p[j + 1] == '*':
            return go(i, j + 2) or (first and go(i + 1, j))
        return first and go(i + 1, j + 1)
    return go(0, 0)

def ref_wild(s, p):
    @lru_cache(None)
    def go(i, j):
        if j == len(p): return i == len(s)
        if p[j] == '*': return go(i, j + 1) or (i < len(s) and go(i + 1, j))
        if i < len(s) and (p[j] == '?' or p[j] == s[i]): return go(i + 1, j + 1)
        return False
    return go(0, 0)

def ref_decode(s):
    @lru_cache(None)
    def go(i):
        if i == len(s): return 1
        if s[i] == '0': return 0
        r = go(i + 1)
        if i + 1 < len(s) and int(s[i:i + 2]) <= 26: r += go(i + 2)
        return r
    return go(0)

def ref_wbc(s, words):
    w = frozenset(words)
    @lru_cache(None)
    def go(i):
        if i == len(s): return 1
        return sum(go(j) for j in range(i + 1, len(s) + 1) if s[i:j] in w)
    return go(0)

def ref_inter(a, b, c):
    if len(a) + len(b) != len(c): return False
    @lru_cache(None)
    def go(i, j):
        if i == len(a) and j == len(b): return True
        k = i + j
        if i < len(a) and a[i] == c[k] and go(i + 1, j): return True
        if j < len(b) and b[j] == c[k] and go(i, j + 1): return True
        return False
    return go(0, 0)

def ref_lvp(s):
    def valid(t):
        bal = 0
        for ch in t:
            bal += 1 if ch == '(' else -1
            if bal < 0: return False
        return bal == 0
    best = 0
    for i in range(len(s)):
        for j in range(i + 2, len(s) + 1, 2):
            if valid(s[i:j]): best = max(best, j - i)
    return best

def ref_paths(grid):
    R = len(grid); C = len(grid[0]) if R else 0
    if R == 0 or grid[0][0] == 1 or grid[R - 1][C - 1] == 1: return 0
    @lru_cache(None)
    def go(r, c):
        if r == R - 1 and c == C - 1: return 1
        t = 0
        if r + 1 < R and grid[r + 1][c] == 0: t += go(r + 1, c)
        if c + 1 < C and grid[r][c + 1] == 0: t += go(r, c + 1)
        return t
    return go(0, 0)

def ref_ds(s, t):
    @lru_cache(None)
    def go(i, j):
        if j == len(t): return 1
        if i == len(s): return 0
        r = go(i + 1, j)
        if s[i] == t[j]: r += go(i + 1, j + 1)
        return r
    return go(0, 0)


# ---------- frozen test inputs (deterministic, generated once) ----------
def _inputs():
    R = random.Random(20240607)
    out = {}
    # regex
    cur = [["aa", "a"], ["aa", "a*"], ["ab", ".*"], ["", "c*"], ["mississippi", "mis*is*p*."], ["aaa", "a*a"]]
    for _ in range(24):
        s = "".join(R.choice("ab") for _ in range(R.randint(0, 5)))
        p = "".join(R.choice("ab.*") for _ in range(R.randint(0, 5)))
        if p.startswith("*"): p = "a" + p
        p = p.replace("**", "*a")
        cur.append([s, p])
    out["regex"] = cur
    # wildcard
    cur = [["aa", "a"], ["aa", "*"], ["cb", "?a"], ["adceb", "*a*b"], ["acdcb", "a*c?b"], ["", "*"]]
    for _ in range(24):
        s = "".join(R.choice("ab") for _ in range(R.randint(0, 6)))
        p = "".join(R.choice("ab?*") for _ in range(R.randint(0, 6)))
        out_p = p
        cur.append([s, out_p])
    out["wildcard"] = cur
    # decode
    cur = [["12"], ["226"], ["06"], ["0"], [""], ["10"], ["100"], ["2101"], ["27"], ["11106"]]
    for _ in range(20):
        cur.append(["".join(R.choice("0123") if R.random() < 0.5 else R.choice("123456789") for _ in range(R.randint(1, 6)))])
    out["decode"] = cur
    # word break count
    dicts = [["a", "aa", "aaa"], ["cat", "cats", "and", "sand", "dog"], ["leet", "code", "le", "et"]]
    cur = [["aaa", dicts[0]], ["catsanddog", dicts[1]], ["leetcode", dicts[2]], ["aaaa", dicts[0]], ["", dicts[0]]]
    for _ in range(18):
        d = R.choice(dicts)
        s = "".join(R.choice(d) for _ in range(R.randint(0, 3)))
        cur.append([s, d])
    out["wordbreak"] = cur
    # interleave
    cur = [["aab", "axy", "aaxaby"], ["", "", ""], ["a", "b", "ab"], ["a", "b", "ba"], ["abc", "def", "adbecf"]]
    for _ in range(20):
        a = "".join(R.choice("ab") for _ in range(R.randint(0, 4)))
        b = "".join(R.choice("ab") for _ in range(R.randint(0, 4)))
        # build a true interleaving half the time
        if R.random() < 0.5:
            ai, bi, c = 0, 0, []
            while ai < len(a) or bi < len(b):
                if bi >= len(b) or (ai < len(a) and R.random() < 0.5): c.append(a[ai]); ai += 1
                else: c.append(b[bi]); bi += 1
            c = "".join(c)
        else:
            c = "".join(R.choice("ab") for _ in range(len(a) + len(b)))
        cur.append([a, b, c])
    out["interleave"] = cur
    # longest valid parens
    cur = [["(()"], [")()())"], [""], ["()(()"], ["()(())"], [")("], ["(()())"]]
    for _ in range(20):
        cur.append(["".join(R.choice("()") for _ in range(R.randint(0, 8)))])
    out["parens"] = cur
    # unique paths obstacles
    cur = [[[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], [[[0, 1], [0, 0]]], [[[1]]], [[[0]]], [[[0, 0], [1, 1], [0, 0]]]]
    for _ in range(18):
        r, c = R.randint(1, 4), R.randint(1, 4)
        g = [[1 if R.random() < 0.25 else 0 for _ in range(c)] for _ in range(r)]
        g[0][0] = 0; g[r - 1][c - 1] = 0
        cur.append([g])
    out["paths"] = cur
    # distinct subsequences
    cur = [["rabbbit", "rabbit"], ["babgbag", "bag"], ["", ""], ["a", ""], ["aaa", "a"]]
    for _ in range(20):
        s = "".join(R.choice("ab") for _ in range(R.randint(0, 6)))
        t = "".join(R.choice("ab") for _ in range(R.randint(0, 3)))
        cur.append([s, t])
    out["distinct"] = cur
    return out

_INP = _inputs()

PROBLEMS = {
    "regex": {"fn": "is_match", "ref": ref_regex, "inputs": _INP["regex"],
              "spec": "Write ONLY a Python function `is_match(s, p)` for regular-expression matching where '.' matches any single character and '*' matches zero or more of the PRECEDING element. The match must cover the ENTIRE string s. Return a bool."},
    "wildcard": {"fn": "is_match", "ref": ref_wild, "inputs": _INP["wildcard"],
                 "spec": "Write ONLY a Python function `is_match(s, p)` for wildcard matching where '?' matches any single character and '*' matches any sequence (including empty). The match must cover the ENTIRE string s. Return a bool."},
    "decode": {"fn": "num_decodings", "ref": ref_decode, "inputs": _INP["decode"],
               "spec": "Write ONLY a Python function `num_decodings(s)` returning the number of ways to decode a digit string where '1'->'A' ... '26'->'Z'. '0' has no mapping and leading zeros are invalid. Return an int (0 for undecodable)."},
    "wordbreak": {"fn": "word_break_count", "ref": ref_wbc, "inputs": _INP["wordbreak"],
                  "spec": "Write ONLY a Python function `word_break_count(s, words)` returning the number of distinct ways to segment s into a sequence of words from the list `words` (words may repeat). Return an int."},
    "interleave": {"fn": "is_interleave", "ref": ref_inter, "inputs": _INP["interleave"],
                   "spec": "Write ONLY a Python function `is_interleave(a, b, c)` returning True iff c is formed by interleaving a and b (preserving the relative order of each). Return a bool."},
    "parens": {"fn": "longest_valid_parentheses", "ref": ref_lvp, "inputs": _INP["parens"],
               "spec": "Write ONLY a Python function `longest_valid_parentheses(s)` returning the length of the longest valid (well-formed) parentheses substring of s. Return an int."},
    "paths": {"fn": "unique_paths", "ref": ref_paths, "inputs": _INP["paths"],
              "spec": "Write ONLY a Python function `unique_paths(grid)` where grid is a 2D list of 0/1 (1 = obstacle). Count distinct paths from top-left to bottom-right moving only right or down, never onto an obstacle. Return an int (0 if start/end blocked)."},
    "distinct": {"fn": "num_distinct", "ref": ref_ds, "inputs": _INP["distinct"],
                 "spec": "Write ONLY a Python function `num_distinct(s, t)` returning the number of distinct subsequences of s that equal t. Return an int."},
}


def check(key, code, timeout=10):
    p = PROBLEMS[key]
    expected = [p["ref"](*[json.loads(json.dumps(a)) for a in args]) for args in p["inputs"]]
    runner = (code + "\n\nimport json\n"
              f"_inp=json.loads(r'''{json.dumps(p['inputs'])}''')\n"
              f"_exp=json.loads(r'''{json.dumps(expected)}''')\n"
              "ok=True\n"
              "for a,e in zip(_inp,_exp):\n"
              f"    try:\n        r={p['fn']}(*a)\n        if (r is True or r is False) or (e is True or e is False):\n            if bool(r)!=bool(e): ok=False;break\n        elif r!=e: ok=False;break\n"
              "    except Exception: ok=False;break\n"
              "print('PASS' if ok else 'FAIL')\n")
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
            fh.write(runner); path = fh.name
        out = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=timeout,
                             cwd=tempfile.gettempdir())
        return out.stdout.strip().endswith("PASS")
    except Exception:
        return False
    finally:
        try: os.unlink(path)
        except Exception: pass


if __name__ == "__main__":
    # 1) pin reference correctness with hand-verified cases
    assert ref_regex("aa", "a*") and not ref_regex("aa", "a") and ref_regex("ab", ".*")
    assert ref_wild("adceb", "*a*b") and not ref_wild("acdcb", "a*c?b")
    assert ref_decode("226") == 3 and ref_decode("06") == 0 and ref_decode("10") == 1 and ref_decode("") == 1
    assert ref_inter("aab", "axy", "aaxaby") is True and ref_inter("a", "b", "ba") is True
    assert ref_lvp("(()") == 2 and ref_lvp(")()())") == 4 and ref_lvp("") == 0
    assert ref_paths([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == 2 and ref_paths([[1]]) == 0
    assert ref_ds("rabbbit", "rabbit") == 3 and ref_ds("babgbag", "bag") == 5
    assert ref_wbc("catsanddog", ["cat", "cats", "and", "sand", "dog"]) == 2
    # 2) a gold solution passes; a deliberately-wrong one fails
    gold_regex = "def is_match(s,p):\n import re\n return re.fullmatch(p, s) is not None"
    assert check("regex", gold_regex), "gold regex should pass"
    assert not check("regex", "def is_match(s,p): return s==p"), "wrong regex should fail"
    gold_decode = ("def num_decodings(s):\n from functools import lru_cache\n"
                   " @lru_cache(None)\n def go(i):\n  if i==len(s): return 1\n  if s[i]=='0': return 0\n"
                   "  r=go(i+1)\n  if i+1<len(s) and int(s[i:i+2])<=26: r+=go(i+2)\n  return r\n return go(0)")
    assert check("decode", gold_decode), "gold decode should pass"
    print(f"code_hard self-check passed: {len(PROBLEMS)} problems, refs pinned, gold passes, wrong fails")
