"""Symptom knowledge base: match error text against known localhost failures."""

import re
from functools import lru_cache
from pathlib import Path

import yaml

SYMPTOMS_PATH = Path(__file__).parent / "kb" / "symptoms.yaml"


@lru_cache(maxsize=1)
def load_entries() -> list[dict]:
    with open(SYMPTOMS_PATH, encoding="utf-8") as handle:
        entries = yaml.safe_load(handle) or []
    return entries


def explain(text: str) -> list[dict]:
    """Return knowledge-base entries whose patterns appear in `text`,
    ranked by how many patterns matched."""
    if not text:
        return []
    results = []
    for entry in load_entries():
        hits = [
            pattern
            for pattern in entry.get("match", [])
            if re.search(pattern, text, re.IGNORECASE)
        ]
        if hits:
            results.append(
                {
                    "id": entry["id"],
                    "stack": entry.get("stack"),
                    "title": entry["title"],
                    "matched": hits,
                    "causes": entry.get("causes", []),
                    "fixes": entry.get("fixes", []),
                }
            )
    results.sort(key=lambda item: -len(item["matched"]))
    return results
