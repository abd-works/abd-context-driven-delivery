from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\dev\abd-context-driven-delivery")
DOC = (ROOT / ".context" / "module-context.md").read_text(encoding="utf-8")
SEAM_CSV = ROOT / ".sessions" / "default" / "public-seam.csv"
DEPS_CSV = ROOT / ".sessions" / "default" / "module-deps.csv"


def dotted(path: str) -> str:
    return path.replace("\\", "/").strip("/").replace("/", ".")


def graph_seams() -> dict[str, set[str]]:
    by_mod: dict[str, set[str]] = defaultdict(set)
    with SEAM_CSV.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            prefix = row.get("prefix") or row.get("col0")
            name = row.get("col1")
            if not prefix or not name:
                continue
            by_mod[dotted(prefix)].add(name)
    return by_mod


def graph_deps() -> dict[str, set[str]]:
    by_mod: dict[str, set[str]] = defaultdict(set)
    with DEPS_CSV.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            caller = dotted(row["callerPrefix"])
            callee = dotted(row["calleePrefix"])
            if caller and callee and caller != callee:
                by_mod[caller].add(callee)
    return by_mod


def parse_doc() -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    seams: dict[str, set[str]] = defaultdict(set)
    deps: dict[str, set[str]] = defaultdict(set)
    current = None
    in_deps = False
    for line in DOC.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            name = heading.group(1).strip()
            if name.lower() == "modules":
                current = None
                in_deps = False
                continue
            current = name
            in_deps = False
            continue
        if current is None:
            continue
        if re.match(r"^###\s+Dependencies\b", line):
            in_deps = True
            continue
        if re.match(r"^###\s+", line):
            in_deps = False
            continue
        concept = re.match(r"^####\s+(.+?)\s*$", line)
        if concept and not in_deps:
            seams[current].add(concept.group(1).strip())
            continue
        if in_deps:
            bullet = re.match(r"^\s*-\s+`([^`]+)`", line)
            if bullet:
                deps[current].add(dotted(bullet.group(1)))
    return seams, deps


def main() -> None:
    g_seams = graph_seams()
    g_deps = graph_deps()
    d_seams, d_deps = parse_doc()

    graph_mods = set(g_seams) | set(g_deps)
    doc_mods = set(d_seams) | set(d_deps)
    parents = {"Harness", "Actions", "Practices", "Installation", "Builders", "Tools"}
    doc_leaves = {m for m in doc_mods if m not in parents}

    print("## First-class modules (graph prefixes vs documented ## headings)")
    print(f"graph={len(graph_mods)} documented_leaves={len(doc_leaves)}")
    missing_in_doc = sorted(graph_mods - {m.lower() for m in doc_leaves} - {m.lower() for m in parents})
    extra_in_doc = sorted({m.lower() for m in doc_leaves} - graph_mods)
    print("in graph, not a ## heading:", ", ".join(missing_in_doc) or "(none)")
    print("## heading, not a graph prefix:", ", ".join(extra_in_doc) or "(none)")
    print()

    print("## Public classes vs #### seam terms (leaf modules only)")
    for mod in sorted(graph_mods):
        doc_key = next((k for k in doc_leaves if k.lower() == mod.lower()), None)
        graph_names = g_seams.get(mod, set())
        doc_names = d_seams.get(doc_key, set()) if doc_key else set()
        # nested module names listed as seam on parents are not classes
        class_like = {n for n in doc_names if "." not in n}
        only_doc = sorted(class_like - graph_names)
        if only_doc:
            print(f"  {mod}: documented #### not a public class: {', '.join(only_doc)}")
    print()
    print("## Documented dependencies missing from moduleDependsOn")
    for mod, callees in sorted(d_deps.items()):
        key = mod.lower() if mod not in parents else (
            {"Harness": "harness", "Actions": "actions", "Practices": "practices",
             "Installation": "installation", "Builders": "builders", "Tools": "tools"}[mod]
        )
        graph_callees = {c.lower() for c in g_deps.get(key, set())}
        missing = sorted(c for c in callees if c.lower() not in graph_callees and c != "*(none)*")
        if missing:
            print(f"  {mod} -> {', '.join(missing)}")
    print()
    print("## Graph dependency count (noisy call-by-name predicate)")
    for mod in sorted(g_deps, key=lambda m: (-len(g_deps[m]), m)):
        print(f"  {mod}: {len(g_deps[mod])} callees")


if __name__ == "__main__":
    main()
