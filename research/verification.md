# Verification Ledger

Every citation in this repo was checked for existence **twice, by independent means**. The user's
requirement was explicit: *link each paper and check if they are real.* This is the audit trail.

## Result

| Metric | Count |
|---|---|
| Papers surfaced across 10 themes | **78** |
| Confirmed real | **78 / 78 (100%)** |
| Fabricated / unresolved | **0** |
| On arXiv (verified by id) | 75 (70 unique ids; some shared across themes) |
| Real but not on arXiv (verified by DOI/publisher) | 3 |

## Two independent passes

**Pass 1 — in-pipeline verifier agents.** After each theme's research scout returned candidates, a
*separate* strict-verifier agent re-fetched every paper from the arXiv API
(`http://export.arxiv.org/api/query?id_list=…`) or Semantic Scholar and confirmed the returned
title/authors matched. A paper was kept only if a matching record was actually retrieved. (318 tool
calls across the run.)

**Pass 2 — my own ground-truth re-check** (independent of the agents, scripted, reproducible):

- `src/recheck_s2.py` → **Semantic Scholar batch API**, one POST for all 70 arXiv ids + DOIs.
  Result: **71/72 resolved** (every arXiv id + FunSearch's *Nature* DOI). Output: `s2_recheck.json`.
- The one Semantic-Scholar miss (the Ocsai paper, an Elsevier journal article often absent from S2)
  plus the Novelty-Search paper were confirmed via the **Crossref API**:
  - `10.1016/j.tsc.2023.101356` → *Beyond semantic distance: Automated scoring of divergent thinking…* (Thinking Skills and Creativity, 2023) ✅
  - `10.1162/EVCO_a_00025` → *Abandoning Objectives: Evolution Through the Search for Novelty Alone* (Evolutionary Computation, 2011) ✅
- `src/recheck_arxiv.py` re-queries the arXiv API directly; note arXiv returned **HTTP 429** during
  this session (the 20 research/verify agents had just hammered it), which is why the authoritative
  second pass uses the Semantic Scholar batch endpoint + Crossref instead. The script is included and
  will run once arXiv's per-IP cooldown clears.

## The 3 non-arXiv papers (and how each was verified)

| Paper | Where it lives | Verified via |
|---|---|---|
| FunSearch — *Mathematical discoveries from program search with LLMs* | Nature 2024 (`10.1038/s41586-023-06924-6`) | Semantic Scholar DOI |
| *Abandoning Objectives: Evolution Through the Search for Novelty Alone* (Lehman & Stanley) | Evolutionary Computation 2011 (`10.1162/EVCO_a_00025`) | Crossref DOI |
| Ocsai — *Beyond semantic distance: Automated scoring of divergent thinking…* | Thinking Skills & Creativity 2023 (`10.1016/j.tsc.2023.101356`) | Crossref DOI |

## Reproduce it

```bash
python src/recheck_s2.py     # Semantic Scholar batch re-check -> research/s2_recheck.json
python src/recheck_arxiv.py  # direct arXiv API re-check       -> research/arxiv_recheck.json (needs arXiv not rate-limiting)
```

Machine-readable record of every paper (with the per-paper `exists`, `verified_title`,
`verification_method`, `verification_note` fields) is in [`papers.json`](papers.json).
