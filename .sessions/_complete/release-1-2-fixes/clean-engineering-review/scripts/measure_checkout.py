"""Validate one checkout's production code at the Clean Engineering code fidelity and write what its graph rules found.

Usage, with this repository on PYTHONPATH and lizard installed (pip install -e ".[measures]", or into a folder outside the
repository that is put on PYTHONPATH too):

    python measure_checkout.py <checkout folder> <out.json>

It adds no measuring of its own. It gives the checkout's `.context/config.json` a `code_measures` section when it has
none, so the checkout measures its code with the shipped tools and limits, then runs the Validate action on harness/,
space/, tools/, cdd_guidance/ and scripts/ of the checkout, as a person does. From the graph that validate leaves it
writes each function, class and module with the measures the reader kept on it as facts, and counts each limit rule's
violations. Only production code is counted: specs, fixtures, examples and templates are left out, and so is the
oss_portal_domain_driven pattern. A file in a language no tool is chosen for, such as JavaScript, is reported by the
rules as not measured; those reports are counted apart from the nodes past a limit.

The checkout is a throwaway worktree: the config section it gains is never committed.
"""
import json
import sys
from pathlib import Path

import cdd_guidance.actions  # noqa: F401 - registers the actions
import cdd_guidance.practices  # noqa: F401 - registers the practices
from cdd_guidance.actions.validate.validate import Validate
from cdd_guidance.actions.validate.validate_examples import working_in
from cdd_guidance.practices.clean_engineering.measures.code_measures import CONFIG_SECTION, MEASURES, NODE_TYPES
from cdd_guidance.practices.clean_engineering.rules.code_measure_limits import MEASURE_LIMIT_RULES
from cdd_guidance.practices.source_code import is_test_code
from harness.graph.saved_graph import SavedGraph
from space.session.spec_support.throwaway_project import ThrowawayProject

ROOTS = ("harness", "space", "tools", "cdd_guidance", "scripts")
EXCLUDED = {
    "_examples", "fixtures", "node_modules", ".claude", ".cursor", "catalog", ".sessions", "retired", ".retired", ".context",
    "templates", "test", "tests", "test-utils", "__pycache__", "dist", "build", ".venv", "venv", "oss_portal_domain_driven",
}
PRACTICE = "clean_engineering"
NOT_TAKEN = ("No tool is chosen", "The tool '")


def is_production(file: str) -> bool:
    parts = file.replace("\\", "/").split("/")
    return bool(file) and parts[0] in ROOTS and not EXCLUDED.intersection(parts) and not file.endswith(".d.ts") and not is_test_code(file)


def choose_shipped_measures(checkout: Path) -> None:
    config = checkout / ".context" / "config.json"
    held = json.loads(config.read_text(encoding="utf-8")) if config.is_file() else {}
    if CONFIG_SECTION not in held:
        held[CONFIG_SECTION] = {}
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(json.dumps(held, indent=2), encoding="utf-8")


def measures_read(nodes: list) -> list[dict]:
    """Each production function, class and module with every measure its node gives, read as the limit rules read it."""
    found = []
    for node in nodes:
        file = node.source.file or ""
        if not (is_production(file) or (node.type in NODE_TYPES["module"] and file.split("/")[0] in ROOTS and not EXCLUDED.intersection(file.split("/")))):
            continue
        read = {measure.name: measure.value_on(node) for measure in MEASURES if node.type in NODE_TYPES[measure.of]}
        kept = {name: value for name, value in read.items() if value is not None}
        if kept:
            found.append({"type": node.type, "name": node.name, "file": file, "line": node.source.start_line, "measures": kept})
    return found


def main(checkout: Path, out: Path) -> None:
    choose_shipped_measures(checkout)
    throwaway = ThrowawayProject()
    try:
        session = working_in(throwaway, checkout, checkout)
        Validate(session=session).validate(guidance=["clean-engineering-code"], paths=[root for root in ROOTS if (checkout / root).is_dir()])
        saved = SavedGraph.from_graph(session.graph)
        measured = measures_read(session.graph.practices.opened[PRACTICE].reading.in_graph.nodes())
    finally:
        throwaway.close()
    # The measured limits, and the one parameter limit, which limit-operation-parameters holds with its exemptions.
    slugs = [rule.slug for rule in MEASURE_LIMIT_RULES] + ["limit-operation-parameters"]
    findings, not_taken = dict.fromkeys(slugs, 0), dict.fromkeys(slugs, 0)
    for violation in saved.violations([PRACTICE]):
        if violation.rule in findings and is_production(violation.location):
            counted = not_taken if str(violation.message).startswith(NOT_TAKEN) else findings
            counted[violation.rule] += 1
    files = len({node["file"] for node in measured if node["type"] not in ("Module", "Package")})
    out.write_text(json.dumps({"checkout": str(checkout), "files": files, "measured": measured, "findings": findings, "not_taken": not_taken}, indent=1), encoding="utf-8")
    print(f"{files} files, {len(measured)} measured nodes, findings {findings}, not taken {not_taken}")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
