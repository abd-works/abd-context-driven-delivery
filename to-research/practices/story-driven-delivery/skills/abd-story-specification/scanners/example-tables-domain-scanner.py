#!/usr/bin/env python3
"""Validate that scenario outline example-table columns match domain model attributes.

Reads ``domain.json`` from the workspace (written by the domain model, Domain Language,
or domain specification skills as a side-effect of producing their markdown output).
Falls back to ``domain-vocabulary.json`` if ``domain.json`` is absent.
Every column in every scenario outline's example table must resolve to an attribute
of some concept in the vocabulary — with inheritance walked transitively.
Unknown columns are **errors**.

If neither file is present the scanner emits one warning and exits clean.

Vocabulary shape::

    {
      "concepts": {
        "Product":            {"attributes": ["name", "sku", "price"], "inherits": null},
        "DigitalProduct":     {"attributes": ["downloadUrl"],          "inherits": "Product"}
      },
      "aliases": {"scenario": "*"}
    }
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

_ROOT = Path(__file__).resolve().parent.parent
_SKILLS = _ROOT.parent
_SKILLS_TOP = _SKILLS.parent
for _p in (
    _SKILLS / "story-graph-ops" / "scripts",
    _SKILLS_TOP / "skill-helpers" / "execute-skill-using-skills-rules" / "scripts",
    _ROOT / "scanners",
):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)

from scanner_runner import main_with_scanner, execute_scan_with_workspace, load_workspace_graph_json  # noqa: E402
from scanner_bases.violation import Violation  # noqa: E402
from scanner_bases.simple_rule import SimpleRule  # noqa: E402
from scanner_bases.resources.scan_context import FileCollection, ScanFilesContext  # noqa: E402
from story_map import Story, StoryMap  # noqa: E402
from story_scanner import StoryScanner  # noqa: E402


def _normalize(name: str) -> str:
    """Normalize a name for comparison: lowercase, underscores removed."""
    return re.sub(r"[_\s]+", "", name).lower()


def _resolve_all_attributes(
    concept_name: str,
    concepts: Dict[str, Dict[str, Any]],
    _seen: Optional[Set[str]] = None,
) -> Set[str]:
    """Return normalized attribute names for *concept_name*, walking inherits transitively."""
    if _seen is None:
        _seen = set()
    if concept_name in _seen:
        return set()
    _seen.add(concept_name)

    entry = concepts.get(concept_name)
    if not entry:
        return set()

    attrs = {_normalize(a) for a in entry.get("attributes", [])}
    parent = entry.get("inherits")
    if parent:
        attrs |= _resolve_all_attributes(parent, concepts, _seen)
    return attrs


def load_vocabulary(workspace: Path) -> Optional[Dict[str, Any]]:
    # domain.json is the primary output from domain model / UL / OM skills.
    # domain-vocabulary.json is the legacy name; check it as fallback.
    for candidate in ("domain.json", "domain-vocabulary.json"):
        vocab_path = workspace / candidate
        if vocab_path.is_file():
            return json.loads(vocab_path.read_text(encoding="utf-8"))
    return None


def build_valid_columns(vocab: Dict[str, Any]) -> Set[str]:
    """Build the set of all valid normalized column names from the vocabulary."""
    concepts = vocab.get("concepts", {})
    valid: Set[str] = set()
    for concept_name in concepts:
        valid |= _resolve_all_attributes(concept_name, concepts)
    aliases = vocab.get("aliases", {})
    for alias_name in aliases:
        valid.add(_normalize(alias_name))
    return valid


def build_per_concept_columns(vocab: Dict[str, Any]) -> Dict[str, Set[str]]:
    """Build {normalized_concept_name: set(normalized_attribute_names)} with inheritance."""
    concepts = vocab.get("concepts", {})
    result: Dict[str, Set[str]] = {}
    for concept_name in concepts:
        result[_normalize(concept_name)] = _resolve_all_attributes(concept_name, concepts)
    return result


DENORM_COLUMN_THRESHOLD = 8
NUMBERED_SUFFIX_RE = re.compile(r"^(.+?)_(\d+)_(.+)$")


def _detect_numbered_suffix_columns(columns: List[str]) -> List[str]:
    """Return columns that look like numbered denormalization (e.g. owner_1_name, owner_2_name)."""
    hits: List[str] = []
    for col in columns:
        if NUMBERED_SUFFIX_RE.match(col):
            hits.append(col)
    return hits


def _build_inheritance_roots(
    concepts: Dict[str, Dict[str, Any]],
) -> Dict[str, str]:
    """Map each normalized concept name to its root ancestor (normalized)."""
    roots: Dict[str, str] = {}
    for name in concepts:
        norm = _normalize(name)
        current = name
        while True:
            entry = concepts.get(current)
            parent = entry.get("inherits") if entry else None
            if not parent or parent not in concepts:
                break
            current = parent
        roots[norm] = _normalize(current)
    return roots


def _own_attributes(concept_name: str, concepts: Dict[str, Dict[str, Any]]) -> Set[str]:
    """Return only the directly declared attributes for a concept (no inheritance)."""
    entry = concepts.get(concept_name, {})
    return {_normalize(a) for a in entry.get("attributes", [])}


def _count_concept_families(
    columns: List[str],
    per_concept: Dict[str, Set[str]],
    aliases: Set[str],
    concepts_raw: Dict[str, Dict[str, Any]],
) -> Set[str]:
    """Return root-ancestor concept names whose own attributes appear in *columns*.

    When B inherits A, and a column matches an attribute declared on A,
    only A's root is counted — not B's as well.  This avoids false
    "multiple unrelated concepts" reports from inheritance chains.
    """
    roots = _build_inheritance_roots(concepts_raw)
    own_attrs: Dict[str, Set[str]] = {}
    for name in concepts_raw:
        own_attrs[_normalize(name)] = _own_attributes(name, concepts_raw)

    families: Set[str] = set()
    for col in columns:
        norm = _normalize(col)
        if norm in aliases:
            continue
        for concept_norm, own in own_attrs.items():
            if norm in own:
                families.add(roots.get(concept_norm, concept_norm))
    return families


class ExampleTablesDomainScanner(StoryScanner):

    def __init__(self, rule, vocab: Optional[Dict[str, Any]] = None):
        super().__init__(rule)
        self._vocab = vocab
        self._valid_columns: Optional[Set[str]] = None
        self._per_concept: Dict[str, Set[str]] = {}
        self._alias_set: Set[str] = set()
        self._concepts_raw: Dict[str, Dict[str, Any]] = {}
        if vocab:
            self._valid_columns = build_valid_columns(vocab)
            self._per_concept = build_per_concept_columns(vocab)
            self._alias_set = {_normalize(a) for a in vocab.get("aliases", {})}
            self._concepts_raw = vocab.get("concepts", {})

    def scan_with_context(self, context: ScanFilesContext) -> List[Dict[str, Any]]:
        if self._vocab is None:
            violations = [
                Violation(
                    rule=self.rule,
                    violation_message=(
                        "No domain.json (or domain-vocabulary.json) found in workspace; "
                        "skipping domain-table column check. "
                        "Denormalization heuristic still active."
                    ),
                    severity="warning",
                ).to_dict()
            ]
            violations.extend(super().scan_with_context(context))
            return violations
        return super().scan_with_context(context)

    def scan_story_node(self, node: Any) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        if not isinstance(node, Story):
            return violations

        for scenario in node.scenarios:
            if not scenario.has_examples:
                continue

            cols = scenario.examples_columns

            # --- Denormalization heuristic (always runs, even without vocab) ---

            numbered = _detect_numbered_suffix_columns(cols)
            if numbered:
                violations.append(
                    Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Story "{node.name}" outline "{scenario.name}": '
                            f"columns {numbered} look like numbered denormalization "
                            f"(e.g. owner_1_name, owner_2_name). One-to-many "
                            f"relationships belong in a separate table, not as "
                            f"extra columns."
                        ),
                        severity="error",
                    ).to_dict()
                )

            example_tables = scenario.examples or []
            table_count = len(example_tables)

            if table_count <= 1 and len(cols) > DENORM_COLUMN_THRESHOLD:
                violations.append(
                    Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Story "{node.name}" outline "{scenario.name}": '
                            f"single example table with {len(cols)} columns "
                            f"(threshold {DENORM_COLUMN_THRESHOLD}). "
                            f"Likely denormalized — check whether columns span "
                            f"multiple domain concepts that should be separate tables."
                        ),
                        severity="warning",
                    ).to_dict()
                )

            if self._per_concept and table_count <= 1:
                families = _count_concept_families(cols, self._per_concept, self._alias_set, self._concepts_raw)
                if len(families) > 1:
                    sorted_families = sorted(families)
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=(
                                f'Story "{node.name}" outline "{scenario.name}": '
                                f"single table mixes columns from {len(families)} "
                                f"unrelated concepts: {sorted_families}. "
                                f"Split into one table per concept with foreign-key "
                                f"references."
                            ),
                            severity="error",
                        ).to_dict()
                    )

            # --- Column validation (only with vocab) ---

            if self._valid_columns is None:
                continue

            for col in cols:
                norm = _normalize(col)
                if norm not in self._valid_columns:
                    loc = scenario.map_location("steps") if hasattr(scenario, "map_location") else None
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=(
                                f'Story "{node.name}" outline "{scenario.name}": '
                                f'column "{col}" does not match any attribute in the '
                                f"domain vocabulary. Update the domain model or remove "
                                f"the column."
                            ),
                            location=loc,
                            severity="error",
                        ).to_dict()
                    )
        return violations


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate example-table columns against domain vocabulary")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--story-graph", type=Path, default=None)
    parser.add_argument(
        "--domain-vocabulary",
        type=Path,
        default=None,
        help="Path to domain.json or domain-vocabulary.json. "
             "If omitted the scanner searches the workspace for domain.json first, "
             "then domain-vocabulary.json.",
    )
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    story_graph_path = args.story_graph.resolve() if args.story_graph else None

    vocab_path = args.domain_vocabulary
    if vocab_path is None:
        vocab = load_vocabulary(workspace)
    elif vocab_path.is_file():
        vocab = json.loads(vocab_path.read_text(encoding="utf-8"))
    else:
        vocab = None

    rule_path = _ROOT / "rules" / "example-tables-use-domain-language.md"
    rule_file = str(rule_path) if rule_path.is_file() else "example-tables-use-domain-language.md"
    rule = SimpleRule(name="example-tables-use-domain-language", rule_file=rule_file)

    graph_json = load_workspace_graph_json(workspace, story_graph_path)
    context = ScanFilesContext(story_graph=graph_json, files=FileCollection())

    scanner = ExampleTablesDomainScanner(rule, vocab=vocab)
    violations = scanner.scan_with_context(context)

    if not violations:
        sys.exit(0)
    for v in violations:
        print(v, file=sys.stderr)
    has_errors = any(v.get("severity") == "error" for v in violations)
    sys.exit(1 if has_errors else 0)
