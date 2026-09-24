"""WordNet checks for story names.

CodeQL emits the story label. NLTK WordNet decides whether the first word is a
base-form verb and whether a later word is a noun.
"""

from __future__ import annotations

from typing import Iterable, List

from harness.knowledge_graph.model.vocabulary_helper import VocabularyHelper

_VAGUE_VERBS = {"handle", "process", "manage", "do", "perform"}
_GENERIC_NOUNS = {"request", "data", "record", "item", "thing", "info"}


def _words(label: str) -> List[str]:
    return [part.lower() for part in (label or "").replace("_", " ").split() if part]


def rows_for_verb_noun(rows: Iterable[dict]) -> List[dict]:
    refined: List[dict] = []
    seen = set()
    for row in rows:
        label = row.get("message") or ""
        if label in seen:
            continue
        words = _words(label)
        if not words:
            continue
        first = words[0]
        rest = words[1:]
        words = VocabularyHelper()
        gerund, _ = words.is_gerund(first)
        verb = words.is_verb(first)
        noun = any(words.is_noun(word) for word in rest)
        if len(words) >= 2 and verb and noun and not gerund:
            continue
        seen.add(label)
        refined.append(
            {
                "name": row.get("name") or "",
                "message": f"Story '{label}' is not verb-noun format.",
                "contributor": row.get("contributor") or "",
            }
        )
    return refined


def rows_for_vague_mechanic(rows: Iterable[dict]) -> List[dict]:
    refined: List[dict] = []
    seen = set()
    for row in rows:
        label = row.get("message") or ""
        if label in seen:
            continue
        words = _words(label)
        if len(words) < 2:
            continue
        first = words[0]
        rest = words[1:]
        if not VocabularyHelper().is_verb(first) or first not in _VAGUE_VERBS:
            continue
        if not any(word in _GENERIC_NOUNS for word in rest):
            continue
        seen.add(label)
        refined.append(
            {
                "name": row.get("name") or "",
                "message": f"Story '{label}' does not name a system mechanic.",
                "contributor": row.get("contributor") or "",
            }
        )
    return refined
