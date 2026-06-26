"""
novelty.py — the measurement substrate for the divergence harness.

You cannot make an agent "think outside the box" unless you can *measure* how far outside the box
a given candidate is. This module gives the harness three primitives, all from the
Novelty-Search / Quality-Diversity literature:

  1. novelty_vs_archive(c, archive)  — how new is candidate c relative to everything tried so far?
                                        (Novelty Search: reward distance-to-k-nearest in behavior space.)
  2. set_diversity(candidates)        — how structurally spread-out is a *set* of candidates?
                                        (Are stage-1's N ideas actually different, or N paraphrases?)
  3. select_diverse(candidates, k)    — greedy max-min pick of k maximally-different candidates.
                                        (MAP-Elites-style: keep a spread, not k near-duplicates.)

ponytail: distance is LEXICAL (character n-gram Jaccard) — zero dependencies, runs anywhere.
          Ceiling: it measures *surface* novelty, not *semantic* novelty ("a heap" vs "a priority
          queue" look different lexically but a paraphrase can fool it). Upgrade path: swap
          `distance()` for `1 - cosine(embed(a), embed(b))` using any sentence-embedding model;
          every other function is distance-agnostic and needs no change.
"""

from __future__ import annotations
from itertools import combinations


def _ngrams(text: str, n: int = 4) -> set[str]:
    """Character n-grams. Character-level is robust to tokenization and tiny inputs."""
    t = " ".join(text.lower().split())  # normalize whitespace
    if len(t) < n:
        return {t} if t else set()
    return {t[i:i + n] for i in range(len(t) - n + 1)}


def distance(a: str, b: str, n: int = 4) -> float:
    """1 - Jaccard(n-grams). 0.0 == identical, 1.0 == no shared n-grams. The single swap point
    for a semantic upgrade (replace with embedding cosine distance)."""
    ga, gb = _ngrams(a, n), _ngrams(b, n)
    if not ga and not gb:
        return 0.0
    inter = len(ga & gb)
    union = len(ga | gb)
    return 1.0 - (inter / union if union else 0.0)


def novelty_vs_archive(candidate: str, archive: list[str], k: int = 3, n: int = 4) -> float:
    """Novelty Search score: mean distance to the k nearest neighbors in the archive.
    High == candidate sits in a sparse, under-explored region (genuinely new).
    Empty archive == maximally novel by definition (1.0)."""
    if not archive:
        return 1.0
    dists = sorted(distance(candidate, a, n) for a in archive)
    knn = dists[:k] if len(dists) >= k else dists
    return sum(knn) / len(knn)


def set_diversity(candidates: list[str], n: int = 4) -> float:
    """Mean pairwise distance across a set. The stage-1 gate: if generation produced N ideas but
    set_diversity is low, they are paraphrases of the mode — regenerate with harder constraints."""
    if len(candidates) < 2:
        return 0.0
    pairs = list(combinations(candidates, 2))
    return sum(distance(a, b, n) for a, b in pairs) / len(pairs)


def select_diverse(candidates: list[str], k: int, n: int = 4) -> list[int]:
    """Greedy max-min diversity selection (farthest-point sampling). Returns indices of k
    candidates chosen to maximize the minimum pairwise distance — a spread, not a cluster.
    Seeds with the single most-novel-vs-the-rest item, then repeatedly adds the item farthest
    from everything already chosen."""
    if k >= len(candidates):
        return list(range(len(candidates)))
    if k <= 0 or not candidates:
        return []
    # seed: the candidate with the highest mean distance to all others
    seed = max(range(len(candidates)),
               key=lambda i: novelty_vs_archive(candidates[i],
                                                 [c for j, c in enumerate(candidates) if j != i], n=n))
    chosen = [seed]
    while len(chosen) < k:
        rest = [i for i in range(len(candidates)) if i not in chosen]
        # pick the item whose nearest already-chosen neighbor is farthest away (max-min)
        nxt = max(rest, key=lambda i: min(distance(candidates[i], candidates[c], n) for c in chosen))
        chosen.append(nxt)
    return chosen


if __name__ == "__main__":
    # Runnable self-check (ponytail: one assert-based check, no framework).
    obvious = "use a for loop to iterate over the list and sum the values"
    paraphrase = "use a loop to go through the list and add up the values"
    novel = "exploit the closed-form n(n+1)/2 and skip iteration entirely"
    wild = "offload the reduction to the GPU with a parallel scan kernel"

    # paraphrase must be closer to obvious than the novel approach is
    assert distance(obvious, paraphrase) < distance(obvious, novel), "paraphrase should be near-duplicate"

    # novelty vs an archive containing only the obvious answer: paraphrase low, wild high
    arch = [obvious]
    assert novelty_vs_archive(paraphrase, arch) < novelty_vs_archive(wild, arch), "wild idea must read as more novel"

    # a set of distinct ideas is more diverse than a set of paraphrases
    distinct_set = [obvious, novel, wild]
    paraphrase_set = [obvious, paraphrase, "iterate the list and total the values up"]
    assert set_diversity(distinct_set) > set_diversity(paraphrase_set), "distinct set should score higher"

    # select_diverse should never return the two closest items together when it can avoid it
    pool = [obvious, paraphrase, novel, wild]
    picks = select_diverse(pool, 2)
    assert 0 not in picks or 1 not in picks, "should not pick both obvious+paraphrase as the diverse-2"
    assert len(picks) == 2 and len(set(picks)) == 2

    print("novelty.py self-check passed:",
          f"div(distinct)={set_diversity(distinct_set):.3f}",
          f"div(paraphrase)={set_diversity(paraphrase_set):.3f}",
          f"diverse-2 picks={picks}")
