"""Noun clusters for keep-classes-single-responsibility.

CodeQL emits identifier tokens. NLTK WordNet decides which are nouns; operations
that share a noun sit in one responsibility cluster. A stray singleton noun is
not a second job — only several distinct clusters on a large public surface count.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Mapping, Set

from nltk.corpus import wordnet as wn

_MIN_PUBLIC_OPERATIONS = 8
_MIN_NOUN_CLUSTERS = 4


class Responsibilities:
    def hits_for_keep_classes(self, hits: Iterable[dict]) -> List[dict]:
        refined: List[dict] = []
        for class_name, tokens_by_operation in self._tokens_by_class(hits).items():
            if not self._mixed_responsibilities(tokens_by_operation):
                continue
            clusters = self._cluster_operations(tokens_by_operation)
            message = (
                f"Class '{class_name}' has {len(tokens_by_operation)} public operations "
                f"whose nouns cluster into {len(clusters)} responsibilities."
            )
            for operation in tokens_by_operation:
                refined.append(
                    {"name": class_name, "message": message, "contributor": operation}
                )
        return refined

    def nouns_in(self, tokens: Iterable[str]) -> Set[str]:
        words = [token.lower() for token in tokens if token]
        nouns: Set[str] = set()
        for index, word in enumerate(words):
            as_noun = bool(wn.synsets(word, wn.NOUN))
            as_verb = bool(wn.synsets(word, wn.VERB))
            if as_verb and (not as_noun or index == 0):
                continue
            if as_noun:
                nouns.add(self._stem_noun(word))
        return nouns

    def _stem_noun(self, token: str) -> str:
        lemma = wn.morphy(token.lower(), wn.NOUN)
        return lemma or token.lower()

    def _cluster_operations(self, tokens_by_operation: Mapping[str, Set[str]]) -> List[Set[str]]:
        parent = {name: name for name in tokens_by_operation}

        def find(name: str) -> str:
            while parent[name] != name:
                parent[name] = parent[parent[name]]
                name = parent[name]
            return name

        def union(left: str, right: str) -> None:
            root_left, root_right = find(left), find(right)
            if root_left != root_right:
                parent[root_right] = root_left

        nouns_by_op = {
            name: self.nouns_in(tokens) for name, tokens in tokens_by_operation.items()
        }
        named = [name for name, nouns in nouns_by_op.items() if nouns]
        for index, left in enumerate(named):
            for right in named[index + 1 :]:
                if nouns_by_op[left] & nouns_by_op[right]:
                    union(left, right)
        clusters: Dict[str, Set[str]] = defaultdict(set)
        for name in named:
            clusters[find(name)].add(name)
        return list(clusters.values())

    def _tokens_by_class(self, hits: Iterable[dict]) -> Dict[str, Dict[str, Set[str]]]:
        by_class: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
        for hit in hits:
            class_name = hit.get("name") or ""
            operation = hit.get("contributor") or ""
            token = hit.get("message") or ""
            if class_name and operation:
                by_class[class_name][operation].add(token)
        return by_class

    def _mixed_responsibilities(self, tokens_by_operation: Mapping[str, Set[str]]) -> bool:
        if len(tokens_by_operation) <= _MIN_PUBLIC_OPERATIONS:
            return False
        return len(self._cluster_operations(tokens_by_operation)) >= _MIN_NOUN_CLUSTERS
