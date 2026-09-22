"""WordNet checks for DDD type names.

CodeQL emits the class name. NLTK WordNet decides whether a CamelCase token is an
agent noun (Manager, Helper, Processor). Leftover technical suffixes from the
rule stay in Python because they are not parts of speech.
"""

from __future__ import annotations

import re
from typing import Iterable, List

from actions.scan.vocabulary_helper import VocabularyHelper

_TECHNICAL_SUFFIXES = {"result", "response", "dto", "request"}
_CAMEL = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])")


def ident_tokens(name: str) -> List[str]:
    return [token.lower() for token in _CAMEL.findall(name or "") if token]


def rows_for_technical_names(rows: Iterable[dict]) -> List[dict]:
    refined: List[dict] = []
    seen = set()
    for row in rows:
        class_name = row.get("name") or ""
        if class_name in seen:
            continue
        tokens = ident_tokens(class_name)
        agent = any(VocabularyHelper.is_agent_noun(token)[0] for token in tokens)
        suffix = bool(tokens) and tokens[-1] in _TECHNICAL_SUFFIXES
        if not agent and not suffix:
            continue
        seen.add(class_name)
        refined.append(
            {
                "name": class_name,
                "message": (
                    f"Class '{class_name}' uses a technical name instead of a domain concept."
                ),
                "contributor": row.get("contributor") or class_name,
            }
        )
    return refined
