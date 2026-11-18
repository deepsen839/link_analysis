"""Competitor evidence policy helpers.

Actual competitor verification requires an independent research/search provider.
This starter intentionally does not claim that LLM-generated candidates are verified.
"""

def mark_ai_candidates_unverified(candidates: list[dict]) -> list[dict]:
    for candidate in candidates:
        candidate["evidence_status"] = "ai_suggested_unverified"
        candidate["source_urls"] = candidate.get("source_urls", [])
    return candidates
