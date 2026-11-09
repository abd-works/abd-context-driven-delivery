"""Operations whose bodies are nearly the same: the copy-and-adjust duplication an exact match misses.

Each body is read as overlapping runs of three tokens (its shingles); two bodies are near copies when most of their runs
are shared (their Jaccard similarity). Comparing every pair is quadratic on a repository, so each body is first placed
in the buckets of its few smallest run hashes, and only bodies that share a bucket are compared.
"""

from __future__ import annotations

import re
import zlib
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from harness.graph.graph import Node

# A body of fewer tokens is a guard or a delegation; two such bodies look alike without being a copy worth a function.
# Tokens, not lines, measure it, because an operation's lines count its docstring.
MIN_TOKENS = 24
# An operation of fewer lines, its head included, is one expression; two that read alike are an idiom, not a copy worth a
# function. The exact-copy check counts an operation's lines against the same floor.
MIN_LINES = 3
# A near copy shares most of at least this many statements. Two shorter bodies that differ in one call are each one's
# own job said in the same words, such as two three-step operations that differ in the step that is their job.
MIN_STATEMENTS = 4
# The share of three-token runs two bodies must have in common to be one body written twice.
MIN_SHARED = 0.7
_RUN = 3
# How many of a body's smallest run hashes place it in buckets.
_SKETCH = 8
# A bucket every body falls into is boilerplate; comparing all of it would be the quadratic scan this avoids.
_MAX_BUCKET = 40
_TOKEN = re.compile(r"[A-Za-z_]\w*|\d+|\S")
_COMMENT_LINE = re.compile(r"^\s*(#|//).*$", re.M)
_DOCSTRING = re.compile(r'"""[\s\S]*?"""|' + r"'''[\s\S]*?'''")


class NearCopies:
    """The operations of one check, each read once into its runs, and the near-copy pairs among them."""

    def __init__(self, operations: list["Node"]) -> None:
        self._runs: list[tuple["Node", frozenset[int]]] = []
        for operation in operations:
            runs = _runs_of(operation)
            if runs:
                self._runs.append((operation, runs))

    def pairs(self) -> Iterator[tuple["Node", "Node", float]]:
        """Each near copy with the operation it copies (the one read first) and the share of their code they have in
        common; each operation is reported once."""
        reported: set[int] = set()
        for later, earlier in self._candidates():
            if later in reported:
                continue
            copy, copy_runs = self._runs[later]
            original, original_runs = self._runs[earlier]
            shared = len(copy_runs & original_runs) / len(copy_runs | original_runs)
            if shared >= MIN_SHARED:
                reported.add(later)
                yield copy, original, shared

    def _candidates(self) -> list[tuple[int, int]]:
        buckets: dict[int, list[int]] = {}
        for index, (_operation, runs) in enumerate(self._runs):
            for run in sorted(runs)[:_SKETCH]:
                buckets.setdefault(run, []).append(index)
        pairs: set[tuple[int, int]] = set()
        for members in buckets.values():
            if len(members) > _MAX_BUCKET:
                continue
            pairs.update((later, earlier) for position, later in enumerate(members) for earlier in members[:position])
        return sorted(pairs)


def _runs_of(operation: "Node") -> frozenset[int]:
    """The checksums of the body's three-token runs, comments left out; none for a body under the token or line floor.
    The body is the text the operation saves with the graph, and a checksum, never ``hash``, which Python salts per
    process, places each body in the same buckets in every process that checks the graph."""
    code = _COMMENT_LINE.sub("", _DOCSTRING.sub("", str(operation.get_fact("body_text") or "")))
    tokens = _TOKEN.findall(code)
    statements = sum(1 for line in code.splitlines() if line.strip())
    if len(tokens) < MIN_TOKENS or statements + 1 < MIN_LINES or statements < MIN_STATEMENTS:
        return frozenset()
    runs = (" ".join(tokens[start : start + _RUN]) for start in range(len(tokens) - _RUN + 1))
    return frozenset(zlib.crc32(run.encode("utf-8")) for run in runs)
