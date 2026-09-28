from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\dev\abd-context-driven-delivery")
OUT = ROOT / ".context" / "module-context.md"
SEAM_CSV = ROOT / ".sessions" / "default" / "public-seam.csv"
DEPS_CSV = ROOT / ".sessions" / "default" / "module-deps.csv"

PREFIXES = [
    "actions",
    "actions/grill_context",
    "actions/improvement",
    "actions/iterate",
    "actions/partition",
    "actions/sketch",
    "builders",
    "builders/create_agent_toolset",
    "builders/create_context_tool",
    "harness",
    "harness/agent_tools",
    "harness/hooks",
    "harness/knowledge_graph",
    "harness/markdown",
    "harness/mcp",
    "installation",
    "practices",
    "practices/agent_bdd",
    "practices/bdd",
    "practices/clean_engineering",
    "practices/clean_engineering/model",
    "practices/clean_engineering/model/drawio",
    "practices/ddd",
    "practices/kanban",
    "practices/stories",
    "practices/ux",
    "practices/ux/model",
    "practices/ux/model/drawio",
    "practices/ux/model/html",
    "practices/ux/model/json",
    "practices/ux/model/markdown",
    "practices/ux/scripts",
    "practices/ux/story-demo",
    "practices/ux/story-demo/play-dual-runner",
    "tools",
    "tools/catalog_generator",
    "tools/diagnose",
    "tools/echo",
    "tools/git",
    "tools/handoff",
    "tools/plan",
    "tools/prompt_echo",
    "tools/record_decisions",
    "tools/workflow",
]


def dotted(path: str) -> str:
    return path.replace("\\", "/").strip("/").replace("/", ".")


def load_seams() -> dict[str, list[str]]:
    by_mod: dict[str, set[str]] = defaultdict(set)
    with SEAM_CSV.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            prefix = row.get("prefix") or ""
            name = row.get("col1") or ""
            if prefix and name:
                by_mod[prefix.replace("\\", "/")].add(name)
    return {key: sorted(names) for key, names in by_mod.items()}


def load_deps() -> dict[str, list[str]]:
    by_mod: dict[str, set[str]] = defaultdict(set)
    with DEPS_CSV.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            caller = row["callerPrefix"].replace("\\", "/")
            callee = row["calleePrefix"].replace("\\", "/")
            if caller and callee and caller != callee:
                by_mod[caller].add(callee)
    return {key: sorted(names) for key, names in by_mod.items()}


def ordered_prefixes() -> list[str]:
    tops = [p for p in PREFIXES if "/" not in p]
    rest = [p for p in PREFIXES if "/" in p]
    # parents first, in PREFIXES order, then nested in PREFIXES order
    return [p for p in PREFIXES if p in tops] + [p for p in PREFIXES if p in rest]


def render_module(prefix: str, seams: dict[str, list[str]], deps: dict[str, list[str]]) -> str:
    heading = dotted(prefix)
    classes = seams.get(prefix, [])
    callees = deps.get(prefix, [])
    lines = [f"## {heading}", "### Public Seam"]
    if classes:
        for name in classes:
            lines.append(f"#### {name}")
            lines.append("")
    else:
        lines.append("")
        lines.append("*(no public classes in the graph)*")
        lines.append("")
    lines.append("### Dependencies")
    if callees:
        for callee in callees:
            lines.append(f" - `{dotted(callee)}` — moduleDependsOn")
    else:
        lines.append(" - *(none in the graph)*")
    lines.append("---")
    lines.append("")
    lines.append("### Constraint")
    lines.append("")
    lines.append("*(none in the graph)*")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    seams = load_seams()
    deps = load_deps()
    chunks = [
        "# Modules",
        "",
        "*Context-Driven Delivery* is how an agent installs practices, opens a work session, and runs generate, document, and scan from the markdown that sits beside the code. Public classes and dependencies below are the CodeQL first-class module prefixes and `moduleDependsOn` edges — not a curated seam.",
        "",
    ]
    for prefix in ordered_prefixes():
        chunks.append(render_module(prefix, seams, deps))
    OUT.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    class_count = sum(len(seams.get(p, [])) for p in PREFIXES)
    print(f"wrote {OUT} modules={len(PREFIXES)} public_classes={class_count}")


if __name__ == "__main__":
    main()
