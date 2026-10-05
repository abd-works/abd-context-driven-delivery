"""A CodeQL graph checked against each practice rule's faulty and repaired examples."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import contain, equal, expect
from mamba import before, context, description, it

from graph import CodeQLGraph, CodeQLNode, CodeQLPracticeGraph, RuleResult, Source, query_pack

_CASES: dict[tuple[str, str], dict] = {}


def rule_names(examples: Path) -> list[str]:
    names = []
    for path in sorted(examples.iterdir()):
        if path.is_dir() and (path / "faulty").is_dir() and (path / "repaired").is_dir():
            names.append(path.name)
    return names


def packs() -> dict[str, list[tuple[str, Path]]]:
    found: dict[str, list[tuple[str, Path]]] = {}
    for language in ("python", "typescript"):
        for practice in ("bdd", "clean_engineering", "ddd", "stories", "ux"):
            examples = query_pack(practice, language) / ".examples"
            rules = query_pack(practice, language) / "rules"
            if examples.is_dir() and rule_names(examples) and rules.is_dir() and any(rules.glob("*.ql")):
                found.setdefault(practice, []).append((language, examples))
    return found


def query_paths(practice: str, language: str) -> list[Path]:
    folder = query_pack(practice, language) / "rules"
    if not folder.is_dir():
        return []
    return sorted(folder.glob("*.ql"))


def example_file(examples: Path, rule: str, side: str) -> Path | None:
    folder = examples / rule / side
    files = sorted(path for path in folder.rglob("*") if path.suffix in {".py", ".ts", ".tsx", ".js"})
    return files[0] if files else None


def split_node_id(node_id: str) -> tuple[str, str, str]:
    practice, kind, rest = node_id.split(":", 2)
    path, name = rest.rsplit(":", 1)
    return kind, path, name


def side_of(node_id: str, rule: str) -> str | None:
    path = node_id.replace("\\", "/")
    for side in ("faulty", "repaired"):
        marker = f"{rule}/{side}/"
        if f"/{marker}" in path or f":{marker}" in path:
            return side
    return None


def node_from_id(practice: CodeQLPracticeGraph, practice_name: str, node_id: str, examples: Path) -> CodeQLNode:
    kind, path, name = split_node_id(node_id)
    node = CodeQLNode(practice, kind, node_id, name, Source(path, 1, 1, str(examples)))
    node.details = ""
    practice.by_id[node_id] = node
    practice.nodes.setdefault(kind, []).append(node)
    return node


def load_rule_cases(practice_name: str, language: str, examples: Path) -> dict:
    rules = rule_names(examples)
    graph = CodeQLGraph()
    graph.create_database(str(examples), {practice_name: str(examples)}, database=str(examples))
    database = graph._working_copy(practice_name)
    queries = query_paths(practice_name, language)
    decoded = graph.run_queries([str(path) for path in queries], database, reuse=True)
    practice = CodeQLPracticeGraph(practice_name)
    practice.source_root = str(examples)
    hits: dict[str, dict[str, list[tuple[str, str]]]] = {}
    for rows in decoded.values():
        for row in rows:
            if len(row) < 3 or row[0] not in rules or not row[2]:
                continue
            rule, node_id, violation = row[0], row[1], row[2]
            side = side_of(node_id, rule)
            if side is None:
                continue
            hits.setdefault(rule, {}).setdefault(side, []).append((node_id, violation))
    cases = {}
    for rule in rules:
        flagged = []
        for node_id, violation in hits.get(rule, {}).get("faulty", []):
            node = node_from_id(practice, practice_name, node_id, examples)
            prefix = f"{rule} violation suspected at {node_id} "
            node.details = violation[len(prefix) :] if violation.startswith(prefix) else violation
            node.rules.append(RuleResult(rule, violation))
            flagged.append(node)
        repaired_hits = hits.get(rule, {}).get("repaired", [])
        if repaired_hits:
            node_id, violation = repaired_hits[0]
            repaired = node_from_id(practice, practice_name, node_id, examples)
            for hit_id, hit_violation in repaired_hits:
                target = repaired if hit_id == node_id else node_from_id(practice, practice_name, hit_id, examples)
                target.rules.append(RuleResult(rule, hit_violation))
                if target is not repaired:
                    repaired.rules.extend(target.rules)
        else:
            repaired_path = example_file(examples, rule, "repaired") or (examples / rule / "repaired")
            relative = repaired_path.relative_to(examples).as_posix() if repaired_path.is_file() else f"{rule}/repaired"
            repaired = node_from_id(
                practice, practice_name, f"{practice_name}:Node:{relative}:{repaired_path.stem}", examples
            )
        if flagged:
            faulty = flagged[0]
        else:
            faulty_path = example_file(examples, rule, "faulty") or (examples / rule / "faulty")
            relative = faulty_path.relative_to(examples).as_posix() if faulty_path.is_file() else f"{rule}/faulty"
            faulty = node_from_id(
                practice, practice_name, f"{practice_name}:Node:{relative}:{faulty_path.stem}", examples
            )
            faulty.details = "the faulty example produced no row"
        cases[rule] = {"faulty": faulty, "flagged": flagged, "repaired": repaired}
    return cases

def faulty_violation(practice, language, rule):
    node = _CASES[(practice, language)][rule]["faulty"]
    expect([hit.violation for hit in node.rules]).to(
        contain(f"{rule} violation suspected at {node.node_id} {node.details}")
    )


def each_violation(practice, language, rule):
    flagged = _CASES[(practice, language)][rule]["flagged"] or [_CASES[(practice, language)][rule]["faulty"]]
    expect(
        all(
            f"{rule} violation suspected at {node.node_id} {node.details}"
            in [hit.violation for hit in node.rules]
            for node in flagged
        )
    ).to(equal(True))


def repaired_clear(practice, language, rule):
    node = _CASES[(practice, language)][rule]["repaired"]
    expect([hit.violation for hit in node.rules]).to(equal([]))

with description("a CodeQL graph"):
    with context("with clean engineering"):
        with context("with python"):
            with before.all:
                _CASES[("clean_engineering", "python")] = load_rule_cases("clean_engineering", "python", query_pack("clean_engineering", "python") / ".examples")
            with context("with avoid-vague-parameter-names"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "avoid-vague-parameter-names")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "avoid-vague-parameter-names")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "avoid-vague-parameter-names")
            with context("with deep-module"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "deep-module")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "deep-module")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "deep-module")
            with context("with do-not-invent-parallel-object-models"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "do-not-invent-parallel-object-models")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "do-not-invent-parallel-object-models")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "do-not-invent-parallel-object-models")
            with context("with eliminate-duplication"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "eliminate-duplication")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "eliminate-duplication")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "eliminate-duplication")
            with context("with extensions-live-with-the-domain"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "extensions-live-with-the-domain")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "extensions-live-with-the-domain")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "extensions-live-with-the-domain")
            with context("with hide-inner-details"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "hide-inner-details")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "hide-inner-details")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "hide-inner-details")
            with context("with keep-classes-single-responsibility"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "keep-classes-single-responsibility")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "keep-classes-single-responsibility")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "keep-classes-single-responsibility")
            with context("with keep-operations-small-focused"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "keep-operations-small-focused")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "keep-operations-small-focused")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "keep-operations-small-focused")
            with context("with language-modules-one-section"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "language-modules-one-section")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "language-modules-one-section")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "language-modules-one-section")
            with context("with layer-separation"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "layer-separation")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "layer-separation")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "layer-separation")
            with context("with limit-comments"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "limit-comments")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "limit-comments")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "limit-comments")
            with context("with limit-operation-parameters"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "limit-operation-parameters")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "limit-operation-parameters")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "limit-operation-parameters")
            with context("with low-coupling"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "low-coupling")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "low-coupling")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "low-coupling")
            with context("with missing-module-context"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "missing-module-context")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "missing-module-context")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "missing-module-context")
            with context("with modules-not-model-blocks"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "modules-not-model-blocks")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "modules-not-model-blocks")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "modules-not-model-blocks")
            with context("with named-seam-and-constraint"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "named-seam-and-constraint")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "named-seam-and-constraint")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "named-seam-and-constraint")
            with context("with never-swallow-exceptions"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "never-swallow-exceptions")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "never-swallow-exceptions")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "never-swallow-exceptions")
            with context("with one-way-deps"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "one-way-deps")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "one-way-deps")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "one-way-deps")
            with context("with prefer-class-operations"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "prefer-class-operations")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "prefer-class-operations")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "prefer-class-operations")
            with context("with prefer-instance-operations"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "prefer-instance-operations")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "prefer-instance-operations")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "prefer-instance-operations")
            with context("with provide-meaningful-context"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "provide-meaningful-context")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "provide-meaningful-context")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "provide-meaningful-context")
            with context("with public-seam-only"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "public-seam-only")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "public-seam-only")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "public-seam-only")
            with context("with put-logic-on-the-owning-resource"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "put-logic-on-the-owning-resource")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "put-logic-on-the-owning-resource")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "put-logic-on-the-owning-resource")
            with context("with shape-classes-around-resources"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "shape-classes-around-resources")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "shape-classes-around-resources")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "shape-classes-around-resources")
            with context("with simplify-control-flow"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "simplify-control-flow")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "simplify-control-flow")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "simplify-control-flow")
            with context("with use-consistent-naming"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "use-consistent-naming")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "use-consistent-naming")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "use-consistent-naming")
            with context("with use-exceptions-properly"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "use-exceptions-properly")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "use-exceptions-properly")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "use-exceptions-properly")
            with context("with use-explicit-dependencies"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "use-explicit-dependencies")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "use-explicit-dependencies")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "use-explicit-dependencies")
            with context("with use-intention-revealing-names"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "use-intention-revealing-names")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "use-intention-revealing-names")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "use-intention-revealing-names")
            with context("with use-property-not-accessor"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "use-property-not-accessor")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "use-property-not-accessor")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "use-property-not-accessor")
            with context("with use-typed-signatures"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "python", "use-typed-signatures")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "python", "use-typed-signatures")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "python", "use-typed-signatures")
        with context("with typescript"):
            with before.all:
                _CASES[("clean_engineering", "typescript")] = load_rule_cases("clean_engineering", "typescript", query_pack("clean_engineering", "typescript") / ".examples")
            with context("with constants-not-magic-strings"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "typescript", "constants-not-magic-strings")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "typescript", "constants-not-magic-strings")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "typescript", "constants-not-magic-strings")
            with context("with cross-layer-method-naming"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "typescript", "cross-layer-method-naming")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "typescript", "cross-layer-method-naming")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "typescript", "cross-layer-method-naming")
            with context("with domain-core-file-matches-folder-slug"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "typescript", "domain-core-file-matches-folder-slug")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "typescript", "domain-core-file-matches-folder-slug")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "typescript", "domain-core-file-matches-folder-slug")
            with context("with ensure-type-safe-routes"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "typescript", "ensure-type-safe-routes")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "typescript", "ensure-type-safe-routes")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "typescript", "ensure-type-safe-routes")
            with context("with implement-full-interfaces"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "typescript", "implement-full-interfaces")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "typescript", "implement-full-interfaces")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "typescript", "implement-full-interfaces")
            with context("with include-all-external-dependencies"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "typescript", "include-all-external-dependencies")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "typescript", "include-all-external-dependencies")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "typescript", "include-all-external-dependencies")
            with context("with no-screen-map-banner-comments"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "typescript", "no-screen-map-banner-comments")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "typescript", "no-screen-map-banner-comments")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "typescript", "no-screen-map-banner-comments")
            with context("with node-decides-next-page"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "typescript", "node-decides-next-page")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "typescript", "node-decides-next-page")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "typescript", "node-decides-next-page")
            with context("with prefix-own-class-member"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "typescript", "prefix-own-class-member")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "typescript", "prefix-own-class-member")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "typescript", "prefix-own-class-member")
            with context("with property-casing-transform"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "typescript", "property-casing-transform")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "typescript", "property-casing-transform")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "typescript", "property-casing-transform")
            with context("with share-domain-logic"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "typescript", "share-domain-logic")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "typescript", "share-domain-logic")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "typescript", "share-domain-logic")
            with context("with standard-mutation-response"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "typescript", "standard-mutation-response")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "typescript", "standard-mutation-response")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "typescript", "standard-mutation-response")
            with context("with views-render-only"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("clean_engineering", "typescript", "views-render-only")
                    with it("should record the violation on each flagged node"):
                        each_violation("clean_engineering", "typescript", "views-render-only")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("clean_engineering", "typescript", "views-render-only")
    with context("with ddd"):
        with context("with python"):
            with before.all:
                _CASES[("ddd", "python")] = load_rule_cases("ddd", "python", query_pack("ddd", "python") / ".examples")
            with context("with building-blocks-fidelity-requires-tactical-stereotype"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "python", "building-blocks-fidelity-requires-tactical-stereotype")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "python", "building-blocks-fidelity-requires-tactical-stereotype")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "python", "building-blocks-fidelity-requires-tactical-stereotype")
            with context("with domain-concepts-not-technical-names"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "python", "domain-concepts-not-technical-names")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "python", "domain-concepts-not-technical-names")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "python", "domain-concepts-not-technical-names")
            with context("with flaccid-data-object-no-behavior"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "python", "flaccid-data-object-no-behavior")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "python", "flaccid-data-object-no-behavior")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "python", "flaccid-data-object-no-behavior")
            with context("with load-with-identity-in-hand"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "python", "load-with-identity-in-hand")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "python", "load-with-identity-in-hand")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "python", "load-with-identity-in-hand")
            with context("with no-orphaned-objects"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "python", "no-orphaned-objects")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "python", "no-orphaned-objects")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "python", "no-orphaned-objects")
            with context("with private-method-naming"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "python", "private-method-naming")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "python", "private-method-naming")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "python", "private-method-naming")
            with context("with repository-is-collection-lifecycle"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "python", "repository-is-collection-lifecycle")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "python", "repository-is-collection-lifecycle")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "python", "repository-is-collection-lifecycle")
            with context("with screen-interface-not-a-domain-object"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "python", "screen-interface-not-a-domain-object")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "python", "screen-interface-not-a-domain-object")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "python", "screen-interface-not-a-domain-object")
            with context("with service-is-homeless"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "python", "service-is-homeless")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "python", "service-is-homeless")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "python", "service-is-homeless")
        with context("with typescript"):
            with before.all:
                _CASES[("ddd", "typescript")] = load_rule_cases("ddd", "typescript", query_pack("ddd", "typescript") / ".examples")
            with context("with aggregate-lives-in-its-own-folder"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "aggregate-lives-in-its-own-folder")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "aggregate-lives-in-its-own-folder")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "aggregate-lives-in-its-own-folder")
            with context("with aggregate-owns-operation-repo-is-crud"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "aggregate-owns-operation-repo-is-crud")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "aggregate-owns-operation-repo-is-crud")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "aggregate-owns-operation-repo-is-crud")
            with context("with arrange-with-empty-and-seed"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "arrange-with-empty-and-seed")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "arrange-with-empty-and-seed")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "arrange-with-empty-and-seed")
            with context("with ask-cross-aggregate-sync"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "ask-cross-aggregate-sync")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "ask-cross-aggregate-sync")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "ask-cross-aggregate-sync")
            with context("with caller-orchestrates-cross-aggregate-flow"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "caller-orchestrates-cross-aggregate-flow")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "caller-orchestrates-cross-aggregate-flow")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "caller-orchestrates-cross-aggregate-flow")
            with context("with construct-repository-at-the-caller"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "construct-repository-at-the-caller")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "construct-repository-at-the-caller")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "construct-repository-at-the-caller")
            with context("with domain-objects-own-their-attributes"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "domain-objects-own-their-attributes")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "domain-objects-own-their-attributes")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "domain-objects-own-their-attributes")
            with context("with fluent-operation-returns-next-aggregate"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "fluent-operation-returns-next-aggregate")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "fluent-operation-returns-next-aggregate")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "fluent-operation-returns-next-aggregate")
            with context("with implement-domain-entities-correctly"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "implement-domain-entities-correctly")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "implement-domain-entities-correctly")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "implement-domain-entities-correctly")
            with context("with one-json-store-per-aggregate"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "one-json-store-per-aggregate")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "one-json-store-per-aggregate")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "one-json-store-per-aggregate")
            with context("with one-repository-per-aggregate"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "one-repository-per-aggregate")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "one-repository-per-aggregate")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "one-repository-per-aggregate")
            with context("with operation-verb-matches-scenario"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "operation-verb-matches-scenario")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "operation-verb-matches-scenario")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "operation-verb-matches-scenario")
            with context("with private-cross-aggregate-step"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "private-cross-aggregate-step")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "private-cross-aggregate-step")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "private-cross-aggregate-step")
            with context("with repository-owns-aggregate-lifecycle"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "repository-owns-aggregate-lifecycle")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "repository-owns-aggregate-lifecycle")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "repository-owns-aggregate-lifecycle")
            with context("with repository-stores-related-aggregate-by-id"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "repository-stores-related-aggregate-by-id")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "repository-stores-related-aggregate-by-id")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "repository-stores-related-aggregate-by-id")
            with context("with throw-typed-exception-with-message"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "throw-typed-exception-with-message")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "throw-typed-exception-with-message")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "throw-typed-exception-with-message")
            with context("with use-ctx-repository-directly"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "use-ctx-repository-directly")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "use-ctx-repository-directly")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "use-ctx-repository-directly")
            with context("with use-ubiquitous-language"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("ddd", "typescript", "use-ubiquitous-language")
                    with it("should record the violation on each flagged node"):
                        each_violation("ddd", "typescript", "use-ubiquitous-language")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("ddd", "typescript", "use-ubiquitous-language")
    with context("with stories"):
        with context("with typescript"):
            with before.all:
                _CASES[("stories", "typescript")] = load_rule_cases("stories", "typescript", query_pack("stories", "typescript") / ".examples")
            with context("with browser-then-asserts-screen-widgets"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "browser-then-asserts-screen-widgets")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "browser-then-asserts-screen-widgets")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "browser-then-asserts-screen-widgets")
            with context("with domain-fixture-example-files"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "domain-fixture-example-files")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "domain-fixture-example-files")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "domain-fixture-example-files")
            with context("with domain-operation-in-the-step"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "domain-operation-in-the-step")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "domain-operation-in-the-step")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "domain-operation-in-the-step")
            with context("with example-role-names"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "example-role-names")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "example-role-names")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "example-role-names")
            with context("with examples-export-data-not-repository"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "examples-export-data-not-repository")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "examples-export-data-not-repository")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "examples-export-data-not-repository")
            with context("with four-to-nine-children"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "four-to-nine-children")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "four-to-nine-children")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "four-to-nine-children")
            with context("with gwt-steps-trace-to-domain-operations"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "gwt-steps-trace-to-domain-operations")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "gwt-steps-trace-to-domain-operations")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "gwt-steps-trace-to-domain-operations")
            with context("with initialize-from-fixture-then-seed"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "initialize-from-fixture-then-seed")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "initialize-from-fixture-then-seed")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "initialize-from-fixture-then-seed")
            with context("with kebab-case-paths"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "kebab-case-paths")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "kebab-case-paths")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "kebab-case-paths")
            with context("with originating-sub-epic-examples"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "originating-sub-epic-examples")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "originating-sub-epic-examples")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "originating-sub-epic-examples")
            with context("with plain-english-gwt-steps"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "plain-english-gwt-steps")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "plain-english-gwt-steps")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "plain-english-gwt-steps")
            with context("with pml-artifact-layout"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "pml-artifact-layout")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "pml-artifact-layout")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "pml-artifact-layout")
            with context("with right-size-story-nodes"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "right-size-story-nodes")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "right-size-story-nodes")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "right-size-story-nodes")
            with context("with scaffold-test-scripts"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "scaffold-test-scripts")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "scaffold-test-scripts")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "scaffold-test-scripts")
            with context("with story-name-captures-system-mechanic"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "story-name-captures-system-mechanic")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "story-name-captures-system-mechanic")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "story-name-captures-system-mechanic")
            with context("with test-story-driven"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "test-story-driven")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "test-story-driven")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "test-story-driven")
            with context("with use-thorough-e2e-tests"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "use-thorough-e2e-tests")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "use-thorough-e2e-tests")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "use-thorough-e2e-tests")
            with context("with verb-noun-format"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "verb-noun-format")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "verb-noun-format")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "verb-noun-format")
            with context("with vocabulary-traces-to-domain-source"):
                with context("with the faulty example"):
                    with it("should record a violation on the node"):
                        faulty_violation("stories", "typescript", "vocabulary-traces-to-domain-source")
                    with it("should record the violation on each flagged node"):
                        each_violation("stories", "typescript", "vocabulary-traces-to-domain-source")
                with context("with the repaired example"):
                    with it("should record no violation on the node"):
                        repaired_clear("stories", "typescript", "vocabulary-traces-to-domain-source")
