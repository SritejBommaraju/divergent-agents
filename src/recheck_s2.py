"""
recheck_s2.py — independent re-verification via the Semantic Scholar batch API.

One POST checks all cited arXiv ids + DOI-based non-arXiv papers and returns title/year/authors,
so we can confirm each id resolves to a real record (second source, independent of arXiv's API).
ponytail: stdlib only (urllib, json, time).
"""
import json, os, time, urllib.request, urllib.error

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS = os.path.join(REPO, "research", "papers.json")
URL = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,year,externalIds"
# real-but-not-on-arXiv papers, addressed by DOI
EXTRA_DOIS = {
    "DOI:10.1038/s41586-023-06924-6": "FunSearch (Nature)",
    "DOI:10.1016/j.tsc.2023.101356": "Ocsai divergent-thinking scoring (Thinking Skills & Creativity)",
}


def post(ids):
    body = json.dumps({"ids": ids}).encode()
    for attempt in range(6):
        try:
            req = urllib.request.Request(
                URL, data=body,
                headers={"Content-Type": "application/json",
                         "User-Agent": "divergent-agents/1.0 (sritejbommaraju@berkeley.edu)"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                wait = 6 * (attempt + 1)
                print(f"  {e.code} — backing off {wait}s")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("exhausted retries")


def main():
    papers = json.load(open(PAPERS, encoding="utf-8"))
    arxiv_ids = sorted({(p.get("arxiv_id") or "").strip() for p in papers if (p.get("arxiv_id") or "").strip()})
    ids = [f"ARXIV:{a}" for a in arxiv_ids] + list(EXTRA_DOIS)
    print(f"Batch-verifying {len(ids)} ids via Semantic Scholar ({len(arxiv_ids)} arXiv + {len(EXTRA_DOIS)} DOI)\n")
    res = post(ids)
    resolved, missing = {}, []
    for key, rec in zip(ids, res):
        if rec and rec.get("title"):
            resolved[key] = {"title": rec["title"], "year": rec.get("year"),
                             "externalIds": rec.get("externalIds", {})}
        else:
            missing.append(key)
    print(f"RESOLVED: {len(resolved)}/{len(ids)}")
    print("MISSING:", missing if missing else "none — every id resolves to a real Semantic Scholar record.")
    json.dump({"resolved": resolved, "missing": missing},
              open(os.path.join(REPO, "research", "s2_recheck.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print("\nSample resolved:")
    for k in list(resolved)[:8]:
        print(f"  {k} -> {resolved[k]['title']} ({resolved[k]['year']})")


if __name__ == "__main__":
    main()
