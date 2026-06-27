"""
code_twist.py — NOVEL TWISTS on known algorithm problems, with trivially-correct brute references.

Classic problems hit a ceiling: a frontier model has memorized them. These are *twists* (3-way
interleave, diagonal-move path counting, exactly-k word break, non-adjacent subsequences, two-bracket
validity, strictly-increasing paths) — so memorized templates are WRONG and the model must actually
reason, creating real headroom at low effort. Every reference is a trivial exhaustive recursion whose
correctness is obvious and pinned by hand-verified cases — the checker is unimpeachable. ponytail: stdlib.
"""
import sys, os, json, subprocess, tempfile, random
from functools import lru_cache

def ref_diag(grid):                              # right / down / DIAGONAL moves, avoid 1s
    R = len(grid); C = len(grid[0]) if R else 0
    if not R or grid[0][0] or grid[R - 1][C - 1]: return 0
    @lru_cache(None)
    def go(r, c):
        if r == R - 1 and c == C - 1: return 1
        t = 0
        for dr, dc in ((1, 0), (0, 1), (1, 1)):
            nr, nc = r + dr, c + dc
            if nr < R and nc < C and grid[nr][nc] == 0: t += go(nr, nc)
        return t
    return go(0, 0)

def ref_mono(grid):                              # right/down path, values STRICTLY INCREASING
    R = len(grid); C = len(grid[0]) if R else 0
    if not R: return 0
    @lru_cache(None)
    def go(r, c):
        if r == R - 1 and c == C - 1: return 1
        t = 0
        for dr, dc in ((1, 0), (0, 1)):
            nr, nc = r + dr, c + dc
            if nr < R and nc < C and grid[nr][nc] > grid[r][c]: t += go(nr, nc)
        return t
    return go(0, 0)

def ref_gap(s, t):                               # subsequences == t with NO TWO ADJACENT indices
    @lru_cache(None)
    def go(i, j, last):
        if j == len(t): return 1
        if i == len(s): return 0
        r = go(i + 1, j, last)
        if s[i] == t[j] and i - last >= 2: r += go(i + 1, j + 1, i)
        return r
    return go(0, 0, -10)

def ref_kwords(s, words, k):                     # segment into EXACTLY k dictionary words
    w = frozenset(words)
    @lru_cache(None)
    def go(i, rem):
        if i == len(s): return 1 if rem == 0 else 0
        if rem <= 0: return 0
        return sum(go(j, rem - 1) for j in range(i + 1, len(s) + 1) if s[i:j] in w)
    return go(0, k)

def ref_bracket(s):                              # longest valid substring with () AND []
    pairs = {')': '(', ']': '['}
    def valid(t):
        st = []
        for ch in t:
            if ch in '([':
                st.append(ch)
            else:
                if not st or st[-1] != pairs[ch]: return False
                st.pop()
        return not st
    best = 0
    for i in range(len(s)):
        for j in range(i + 2, len(s) + 1):
            if valid(s[i:j]): best = max(best, j - i)
    return best

def ref_int3(a, b, d, c):                         # is c an interleaving of THREE strings
    if len(a) + len(b) + len(d) != len(c): return False
    @lru_cache(None)
    def go(i, j, k):
        if i == len(a) and j == len(b) and k == len(d): return True
        p = i + j + k
        if i < len(a) and a[i] == c[p] and go(i + 1, j, k): return True
        if j < len(b) and b[j] == c[p] and go(i, j + 1, k): return True
        if k < len(d) and d[k] == c[p] and go(i, j, k + 1): return True
        return False
    return go(0, 0, 0)


def _inputs():
    R = random.Random(424242)
    out = {}
    cur = [[[[0, 0], [0, 0]]], [[[0, 1], [0, 0]]], [[[0]]], [[[0, 0, 0], [0, 1, 0], [0, 0, 0]]]]
    for _ in range(20):
        r, c = R.randint(1, 4), R.randint(1, 4)
        g = [[1 if R.random() < 0.2 else 0 for _ in range(c)] for _ in range(r)]
        g[0][0] = 0; g[r - 1][c - 1] = 0
        cur.append([g])
    out["diag"] = cur
    cur = [[[[1, 2], [3, 4]]], [[[1, 1], [1, 1]]], [[[5]]], [[[1, 2, 3], [2, 3, 4]]]]
    for _ in range(20):
        r, c = R.randint(1, 4), R.randint(1, 4)
        g = [[R.randint(1, 6) for _ in range(c)] for _ in range(r)]
        cur.append([g])
    out["mono"] = cur
    cur = [["aaa", "aa"], ["aba", "aa"], ["aaaa", "aa"], ["", ""], ["a", "a"], ["abab", "ab"]]
    for _ in range(20):
        s = "".join(R.choice("ab") for _ in range(R.randint(0, 7)))
        t = "".join(R.choice("ab") for _ in range(R.randint(0, 3)))
        cur.append([s, t])
    out["gap"] = cur
    dicts = [["a", "aa"], ["ab", "a", "b"], ["cat", "cats", "and", "sand", "dog"]]
    cur = [["aaa", dicts[0], 2], ["aaa", dicts[0], 1], ["catsanddog", dicts[2], 3], ["ab", dicts[1], 2]]
    for _ in range(20):
        d = R.choice(dicts); s = "".join(R.choice(d) for _ in range(R.randint(0, 3)))
        cur.append([s, d, R.randint(1, 4)])
    out["kwords"] = cur
    cur = [["()[]"], ["([])"], ["(]"], [")("], ["()[]]"], ["[(])"], [""], ["(()[])"]]
    for _ in range(20):
        cur.append(["".join(R.choice("()[]") for _ in range(R.randint(0, 8)))])
    out["bracket"] = cur
    cur = [["a", "b", "c", "abc"], ["ab", "cd", "", "acbd"], ["", "", "", ""], ["a", "b", "c", "cba"], ["ab", "a", "", "aab"]]
    for _ in range(20):
        a = "".join(R.choice("ab") for _ in range(R.randint(0, 3)))
        b = "".join(R.choice("ab") for _ in range(R.randint(0, 3)))
        d = "".join(R.choice("ab") for _ in range(R.randint(0, 3)))
        if R.random() < 0.5:
            parts = list(a) + list(b) + list(d); R.shuffle(parts)  # not order-preserving -> usually False
            c = "".join(parts)
        else:
            ai = bi = di = 0; c = []
            while ai < len(a) or bi < len(b) or di < len(d):
                ch = R.choice([x for x, cond in (("a", ai < len(a)), ("b", bi < len(b)), ("d", di < len(d))) if cond])
                if ch == "a": c.append(a[ai]); ai += 1
                elif ch == "b": c.append(b[bi]); bi += 1
                else: c.append(d[di]); di += 1
            c = "".join(c)
        cur.append([a, b, d, c])
    out["int3"] = cur
    return out

_INP = _inputs()

PROBLEMS = {
    "diag": {"fn": "count_paths", "ref": ref_diag, "inputs": _INP["diag"],
             "spec": ("Write ONLY a Python function `count_paths(grid)`. grid is a 2D list of 0/1 (1=obstacle). "
                      "Count distinct paths from top-left to bottom-right. ALLOWED MOVES: right, down, AND "
                      "diagonal down-right (r+1,c+1). Never step on an obstacle. Return an int (0 if start/end blocked). "
                      "Example: [[0,0],[0,0]] -> 3 (right+down, down+right, or one diagonal).")},
    "mono": {"fn": "count_paths", "ref": ref_mono, "inputs": _INP["mono"],
             "spec": ("Write ONLY a Python function `count_paths(grid)`. grid is a 2D list of ints. Count paths "
                      "from top-left to bottom-right moving ONLY right or down, such that the cell values along "
                      "the path are STRICTLY INCREASING. Return an int. Example: [[1,2],[3,4]] -> 2.")},
    "gap": {"fn": "num_gap_subseq", "ref": ref_gap, "inputs": _INP["gap"],
            "spec": ("Write ONLY a Python function `num_gap_subseq(s, t)` returning the number of subsequences of "
                     "s that equal t and whose chosen indices are NON-ADJACENT (every two consecutive chosen "
                     "indices differ by at least 2). Return an int. Example: s='aaa', t='aa' -> 1 (only indices 0,2).")},
    "kwords": {"fn": "count_k_segmentations", "ref": ref_kwords, "inputs": _INP["kwords"],
               "spec": ("Write ONLY a Python function `count_k_segmentations(s, words, k)` returning the number of "
                        "ways to segment s into EXACTLY k words, each from the list `words` (words may repeat). "
                        "Return an int. Example: s='aaa', words=['a','aa'], k=2 -> 2 ('a'+'aa', 'aa'+'a').")},
    "bracket": {"fn": "longest_valid", "ref": ref_bracket, "inputs": _INP["bracket"],
                "spec": ("Write ONLY a Python function `longest_valid(s)` returning the length of the longest "
                         "substring of s that is a valid sequence of BOTH '()' and '[]' brackets (properly matched "
                         "and nested; '([)]' is NOT valid). Return an int. Example: '()[]' -> 4, '([)]' -> 0.")},
    "int3": {"fn": "is_interleave3", "ref": ref_int3, "inputs": _INP["int3"],
             "spec": ("Write ONLY a Python function `is_interleave3(a, b, d, c)` returning True iff c is formed by "
                      "interleaving the THREE strings a, b, d while preserving the relative order within each. "
                      "Return a bool. Example: a='ab', b='cd', d='', c='acbd' -> True.")},
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
    assert ref_diag([[0, 0], [0, 0]]) == 3 and ref_diag([[0, 1], [0, 0]]) == 2
    assert ref_mono([[1, 2], [3, 4]]) == 2 and ref_mono([[1, 1], [1, 1]]) == 0
    assert ref_gap("aaa", "aa") == 1 and ref_gap("aba", "aa") == 1 and ref_gap("aaaa", "aa") == 3
    assert ref_kwords("aaa", ["a", "aa"], 2) == 2 and ref_kwords("aaa", ["a", "aa"], 1) == 0
    assert ref_bracket("()[]") == 4 and ref_bracket("([])") == 4 and ref_bracket("([)]") == 0 and ref_bracket("(]") == 0
    assert ref_int3("ab", "cd", "", "acbd") is True and ref_int3("a", "b", "c", "abc") is True
    assert ref_int3("a", "a", "", "aa") is True and ref_int3("ab", "", "", "ba") is False
    # gold solutions pass; wrong fails
    gold_diag = ("def count_paths(grid):\n from functools import lru_cache\n R=len(grid);C=len(grid[0]) if R else 0\n"
                 " if not R or grid[0][0] or grid[R-1][C-1]: return 0\n @lru_cache(None)\n def go(r,c):\n"
                 "  if r==R-1 and c==C-1: return 1\n  t=0\n  for dr,dc in ((1,0),(0,1),(1,1)):\n"
                 "   nr,nc=r+dr,c+dc\n   if nr<R and nc<C and grid[nr][nc]==0: t+=go(nr,nc)\n  return t\n return go(0,0)")
    assert check("diag", gold_diag), "gold diag should pass"
    assert not check("diag", "def count_paths(grid): return 1"), "wrong diag should fail"
    print(f"code_twist self-check passed: {len(PROBLEMS)} novel problems, refs pinned, gold passes, wrong fails")
