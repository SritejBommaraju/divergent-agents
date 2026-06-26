"""
recheck_methodology.py — independent re-verification of the benchmarking-methodology citations.
S2 batch for arXiv ids; Crossref for the DOI-based (PNAS / journal) papers. ponytail: stdlib only.
"""
import json, os, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
papers = json.load(open(os.path.join(HERE, "methodology_papers.json"), encoding="utf-8"))
S2 = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,year,externalIds"
DOIS = {  # non-arXiv papers -> DOI
    "10.1073/pnas.2022340118": "Divergent Association Task (PNAS)",
    "10.3758/s13428-020-01453-w": "SemDis",
    "10.1080/10400419.2022.2025720": "Semantic Distance & AUT (Beaty)",
    "10.1016/j.tsc.2023.101356": "Ocsai",
}
UA = {"User-Agent": "divergent-agents/1.0 (sritejbommaraju@berkeley.edu)"}


def s2_batch(ids):
    body = json.dumps({"ids": ids}).encode()
    for a in range(6):
        try:
            req = urllib.request.Request(S2, data=body, headers={**UA, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(6 * (a + 1))
            else:
                raise
    raise RuntimeError("s2 retries exhausted")


def crossref(doi):
    req = urllib.request.Request("https://api.crossref.org/works/" + doi, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["message"].get("title", ["?"])[0]


arxiv_ids = sorted({(p.get("arxiv_id") or "").strip() for p in papers
                    if (p.get("arxiv_id") or "").strip() and "N/A" not in (p.get("arxiv_id") or "")})
print(f"Re-checking {len(arxiv_ids)} arXiv ids (Semantic Scholar) + {len(DOIS)} DOIs (Crossref)\n")
res = s2_batch([f"ARXIV:{a}" for a in arxiv_ids])
resolved, missing = {}, []
for a, rec in zip(arxiv_ids, res):
    (resolved.__setitem__(a, rec["title"]) if rec and rec.get("title") else missing.append(a))
print(f"arXiv via S2: {len(resolved)}/{len(arxiv_ids)} resolved" + (f"  MISSING={missing}" if missing else "  (all real)"))
doi_ok = {}
for doi, name in DOIS.items():
    try:
        doi_ok[doi] = crossref(doi); print(f"  DOI ok: {doi} -> {doi_ok[doi][:70]}")
    except Exception as e:
        print(f"  DOI FAIL: {doi} ({name}): {e}")
json.dump({"arxiv_resolved": resolved, "arxiv_missing": missing, "doi_resolved": doi_ok},
          open(os.path.join(HERE, "methodology_recheck.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"\nTOTAL confirmed real: {len(resolved) + len(doi_ok)} / {len(arxiv_ids) + len(DOIS)}")
