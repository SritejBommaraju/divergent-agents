"""
code_twist2.py — six MORE novel twisted problems for the robustness benchmark (Benchmark 6).

Same contract as code_twist.py: each problem has fn, spec, a trivially-correct brute `ref`, frozen fixed
inputs, and a `fuzz(n, seed)` generator. References are exhaustive recursions/enumerations whose
correctness is obvious and pinned by hand-verified cases + cross-validation. ponytail: stdlib only.
"""
import sys, os, json, subprocess, tempfile, random
from functools import lru_cache
from itertools import combinations

def ref_inck(arr, k):                                  # # strictly-increasing subsequences of length exactly k
    if k <= 0: return 1
    return sum(1 for combo in combinations(range(len(arr)), k)
               if all(arr[combo[i]] < arr[combo[i + 1]] for i in range(k - 1)))

def ref_pp(s):                                         # # ways to partition s into palindromic substrings
    @lru_cache(None)
    def go(i):
        if i == len(s): return 1
        return sum(go(j) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1])
    return go(0)

def ref_bal(s):                                        # # contiguous substrings with equal #a and #b
    cnt = 0
    for i in range(len(s)):
        a = b = 0
        for j in range(i, len(s)):
            if s[j] == 'a': a += 1
            else: b += 1
            if a == b: cnt += 1
    return cnt

def ref_jump(arr):                                     # min jumps 0->last (arr[i]=max step); -1 if unreachable
    n = len(arr)
    if n <= 1: return 0
    from collections import deque
    dist = [-1] * n; dist[0] = 0; dq = deque([0])
    while dq:
        i = dq.popleft()
        for j in range(i + 1, min(n, i + arr[i] + 1)):
            if dist[j] == -1:
                dist[j] = dist[i] + 1; dq.append(j)
    return dist[n - 1]

def ref_kgap(s, t, g):                                 # # subsequences == t with consecutive indices >= g apart
    @lru_cache(None)
    def go(i, j, last):
        if j == len(t): return 1
        if i == len(s): return 0
        r = go(i + 1, j, last)
        if s[i] == t[j] and (last < 0 or i - last >= g): r += go(i + 1, j + 1, i)
        return r
    return go(0, 0, -10)

def ref_dst(s):                                        # # distinct non-empty subsequences of s
    subs = set()
    n = len(s)
    for mask in range(1, 1 << n):
        subs.add("".join(s[i] for i in range(n) if mask >> i & 1))
    return len(subs)


def _fixed():
    R = random.Random(99)
    out = {}
    out["inck"] = [[[1, 2, 3], 2], [[3, 2, 1], 2], [[1, 2, 3, 4], 3], [[5], 1], [[1, 1, 1], 2], [[1, 3, 2, 4], 2]]
    for _ in range(18):
        out["inck"].append([[R.randint(1, 5) for _ in range(R.randint(1, 7))], R.randint(1, 4)])
    out["pp"] = [["aab"], ["a"], ["aba"], [""], ["aaa"], ["abc"]]
    for _ in range(18):
        out["pp"].append(["".join(R.choice("ab") for _ in range(R.randint(0, 8)))])
    out["bal"] = [["aabb"], ["ab"], [""], ["abab"], ["aaa"], ["baab"]]
    for _ in range(18):
        out["bal"].append(["".join(R.choice("ab") for _ in range(R.randint(0, 10)))])
    out["jump"] = [[[2, 3, 1, 1, 4]], [[3, 2, 1, 0, 4]], [[0]], [[2, 0, 0]], [[1, 1, 1]], [[5, 0, 0, 0, 0]]]
    for _ in range(18):
        out["jump"].append([[R.randint(0, 4) for _ in range(R.randint(1, 7))]])
    out["kgap"] = [["aaa", "aa", 2], ["aaa", "aa", 1], ["aaaa", "aa", 3], ["abab", "ab", 2], ["a", "a", 1], ["", "", 2]]
    for _ in range(18):
        s = "".join(R.choice("ab") for _ in range(R.randint(0, 8)))
        t = "".join(R.choice("ab") for _ in range(R.randint(0, 3)))
        out["kgap"].append([s, t, R.randint(1, 4)])
    out["dst"] = [["aa"], ["ab"], [""], ["aba"], ["abc"], ["aaa"]]
    for _ in range(18):
        out["dst"].append(["".join(R.choice("ab") for _ in range(R.randint(0, 10)))])
    return out

_INP = _fixed()

PROBLEMS = {
    "inck": {"fn": "count_inc_subseq", "ref": ref_inck, "inputs": _INP["inck"],
             "spec": ("Write ONLY a Python function `count_inc_subseq(arr, k)` returning the number of STRICTLY "
                      "INCREASING subsequences of arr of length EXACTLY k (subsequences need not be contiguous). "
                      "Return an int. Example: arr=[1,2,3], k=2 -> 3.")},
    "pp": {"fn": "count_palindrome_partitions", "ref": ref_pp, "inputs": _INP["pp"],
           "spec": ("Write ONLY a Python function `count_palindrome_partitions(s)` returning the number of ways "
                    "to partition s into contiguous substrings that are ALL palindromes. Return an int "
                    "(1 for the empty string). Example: s='aab' -> 2 ('a|a|b', 'aa|b').")},
    "bal": {"fn": "count_balanced", "ref": ref_bal, "inputs": _INP["bal"],
            "spec": ("Write ONLY a Python function `count_balanced(s)` (s over 'a'/'b') returning the number of "
                     "CONTIGUOUS substrings containing an equal number of 'a' and 'b'. Return an int. "
                     "Example: s='aabb' -> 2.")},
    "jump": {"fn": "min_jumps", "ref": ref_jump, "inputs": _INP["jump"],
             "spec": ("Write ONLY a Python function `min_jumps(arr)` where arr[i] is the max forward jump length "
                      "from index i. Return the MINIMUM number of jumps to reach the last index from index 0, or "
                      "-1 if it is unreachable. Return 0 if the array has length <= 1. Example: [2,3,1,1,4] -> 2, "
                      "[3,2,1,0,4] -> -1.")},
    "kgap": {"fn": "count_kgap_subseq", "ref": ref_kgap, "inputs": _INP["kgap"],
             "spec": ("Write ONLY a Python function `count_kgap_subseq(s, t, g)` returning the number of "
                      "subsequences of s equal to t whose consecutive chosen indices differ by AT LEAST g. "
                      "Return an int. Example: s='aaa', t='aa', g=2 -> 1; g=1 -> 3.")},
    "dst": {"fn": "count_distinct_subseq", "ref": ref_dst, "inputs": _INP["dst"],
            "spec": ("Write ONLY a Python function `count_distinct_subseq(s)` returning the number of DISTINCT "
                     "non-empty subsequences of s (duplicates counted once). Return an int. Example: s='aa' -> 2 "
                     "('a', 'aa'); s='ab' -> 3.")},
}


def fuzz(key, n, seed=13):
    R = random.Random(seed)
    out = []
    for _ in range(n):
        if key == "inck":
            out.append([[R.randint(1, 6) for _ in range(R.randint(1, 8))], R.randint(1, 5)])
        elif key == "pp":
            out.append(["".join(R.choice("ab") for _ in range(R.randint(0, 9)))])
        elif key == "bal":
            out.append(["".join(R.choice("ab") for _ in range(R.randint(0, 12)))])
        elif key == "jump":
            out.append([[R.randint(0, 5) for _ in range(R.randint(1, 9))]])
        elif key == "kgap":
            s = "".join(R.choice("ab") for _ in range(R.randint(0, 10)))
            t = "".join(R.choice("ab") for _ in range(R.randint(0, 4)))
            out.append([s, t, R.randint(1, 4)])
        elif key == "dst":
            out.append(["".join(R.choice("ab") for _ in range(R.randint(0, 11)))])
    return out


def check(key, code, timeout=12):
    p = PROBLEMS[key]
    expected = [p["ref"](*[json.loads(json.dumps(a)) for a in args]) for args in p["inputs"]]
    runner = (code + "\n\nimport json\n"
              f"_inp=json.loads(r'''{json.dumps(p['inputs'])}''')\n"
              f"_exp=json.loads(r'''{json.dumps(expected)}''')\n"
              "ok=True\n"
              "for a,e in zip(_inp,_exp):\n"
              f"    try:\n        r={p['fn']}(*a)\n        if r!=e: ok=False;break\n"
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
    assert ref_inck([1, 2, 3], 2) == 3 and ref_inck([3, 2, 1], 2) == 0 and ref_inck([1, 2, 3, 4], 3) == 4
    assert ref_pp("aab") == 2 and ref_pp("a") == 1 and ref_pp("aba") == 2 and ref_pp("") == 1
    assert ref_bal("aabb") == 2 and ref_bal("ab") == 1 and ref_bal("") == 0
    assert ref_jump([2, 3, 1, 1, 4]) == 2 and ref_jump([3, 2, 1, 0, 4]) == -1 and ref_jump([0]) == 0 and ref_jump([2, 0, 0]) == 1
    assert ref_kgap("aaa", "aa", 2) == 1 and ref_kgap("aaa", "aa", 1) == 3 and ref_kgap("aaaa", "aa", 3) == 1
    assert ref_dst("aa") == 2 and ref_dst("ab") == 3 and ref_dst("") == 0 and ref_dst("aba") == 6
    # cross-validate kgap against an independent combinations brute
    def brute_kgap(s, t, g):
        c = 0
        for combo in combinations(range(len(s)), len(t)):
            if "".join(s[i] for i in combo) == t and all(combo[i + 1] - combo[i] >= g for i in range(len(combo) - 1)):
                c += 1
        return c
    R = random.Random(3)
    for _ in range(300):
        s = "".join(R.choice("ab") for _ in range(R.randint(0, 7))); t = "".join(R.choice("ab") for _ in range(R.randint(0, 3))); g = R.randint(1, 4)
        assert ref_kgap(s, t, g) == brute_kgap(s, t, g), (s, t, g)
    # gold passes, wrong fails
    gold_bal = "def count_balanced(s):\n c=0\n for i in range(len(s)):\n  a=b=0\n  for j in range(i,len(s)):\n   if s[j]=='a': a+=1\n   else: b+=1\n   if a==b: c+=1\n return c"
    assert check("bal", gold_bal) and not check("bal", "def count_balanced(s): return len(s)")
    print(f"code_twist2 self-check passed: {len(PROBLEMS)} problems, refs pinned + kgap cross-validated")
