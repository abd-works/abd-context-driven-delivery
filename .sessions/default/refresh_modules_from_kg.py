from __future__ import annotations

import csv
import subprocess
import textwrap
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\dev\abd-context-driven-delivery")
PACK = ROOT / "practices" / "clean_engineering" / "model" / "codeql"
FILTER = PACK / "subject_filter.qll"
SEAM_QL = PACK / "public-seam-classes.ql"
DEPS_QL = PACK / "first-class-module-depends-on.ql"
SESSION = ROOT / ".sessions" / "default"
SKIP = {"examples", "node_modules", ".git", "__pycache__", ".venv", "venv"}


def first_class_prefixes() -> list[str]:
    prefixes: list[str] = []
    for context in ROOT.rglob("module-context.md"):
        if context.parent.name != ".context":
            continue
        try:
            relative = context.resolve().relative_to(ROOT.resolve())
        except ValueError:
            continue
        if any(part in SKIP for part in relative.parts):
            continue
        folder = context.parent.parent
        try:
            prefix = folder.resolve().relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            continue
        if prefix in (".", "") or prefix == ".":
            continue
        if prefix not in prefixes:
            prefixes.append(prefix)
    return sorted(prefixes, key=lambda p: (p.count("/"), p))


def write_subject_filter(prefixes: list[str]) -> None:
    clauses = " or\n  ".join(f'prefix = "{item}"' for item in prefixes)
    FILTER.write_text(
        "import python\n\n"
        'predicate subjectFilterPrefix(string prefix) { prefix = "" }\n\n'
        "predicate firstClassModulePrefix(string prefix) {\n"
        f"  {clauses}\n"
        "}\n\n"
        "predicate inSubject(AstNode n) {\n"
        '  inSubjectPath(n.getLocation().getFile().getRelativePath().replaceAll("\\\\", "/"))\n'
        "}\n\n"
        "predicate inSubjectFilter(Class cls) {\n"
        "  inSubject(cls)\n"
        "}\n\n"
        "bindingset[path]\n"
        "predicate inSubjectPath(string path) {\n"
        "  any()\n"
        "}\n",
        encoding="utf-8",
    )


def write_queries() -> None:
    SEAM_QL.write_text(
        textwrap.dedent(
            """\
            /**
             * @kind problem
             * @id cdd/practice-graph/verify/public-seam-classes
             * @problem.severity warning
             */

            import python
            import subject_filter
            import model

            from Class cls, string prefix
            where
              inSource(cls) and
              not skippedModulePath(normalizedPath(cls.getLocation().getFile())) and
              prefix = enclosingFirstClassPrefix(normalizedPath(cls.getLocation().getFile())) and
              publicName(cls.getName())
            select prefix, cls.getName()
            """
        ),
        encoding="utf-8",
    )
    DEPS_QL.write_text(
        textwrap.dedent(
            """\
            /**
             * @kind problem
             * @id cdd/practice-graph/verify/first-class-module-depends-on
             * @problem.severity warning
             */

            import python
            import subject_filter
            import model

            from Module caller, Module callee, string callerPrefix, string calleePrefix
            where
              moduleDependsOn(caller, callee) and
              not skippedModulePath(normalizedPath(caller.getFile())) and
              not skippedModulePath(normalizedPath(callee.getFile())) and
              callerPrefix = enclosingFirstClassPrefix(normalizedPath(caller.getFile())) and
              calleePrefix = enclosingFirstClassPrefix(normalizedPath(callee.getFile())) and
              callerPrefix != calleePrefix
            select callerPrefix, calleePrefix
            """
        ),
        encoding="utf-8",
    )


def run_query(ql: Path, bqrs: Path, csv_path: Path, database: Path) -> None:
    subprocess.run(
        ["codeql", "query", "run", "--database", str(database), "--output", str(bqrs), str(ql)],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [
            "codeql",
            "bqrs",
            "decode",
            "--format=csv",
            f"--output={csv_path}",
            str(bqrs),
        ],
        cwd=ROOT,
        check=True,
    )


def load_seams(csv_path: Path) -> dict[str, list[str]]:
    by_mod: dict[str, set[str]] = defaultdict(set)
    with csv_path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            prefix = (row.get("prefix") or "").replace("\\", "/")
            name = row.get("col1") or ""
            if prefix and name:
                by_mod[prefix].add(name)
    return {key: sorted(names) for key, names in by_mod.items()}


def load_deps(csv_path: Path) -> dict[str, list[str]]:
    by_mod: dict[str, set[str]] = defaultdict(set)
    with csv_path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            caller = row["callerPrefix"].replace("\\", "/")
            callee = row["calleePrefix"].replace("\\", "/")
            if caller and callee and caller != callee:
                by_mod[caller].add(callee)
    return {key: sorted(names) for key, names in by_mod.items()}


def dotted(path: str) -> str:
    return path.replace("\\", "/").strip("/").replace("/", ".")


def render_module(prefix: str, seams: dict[str, list[str]], deps: dict[str, list[str]]) -> str:
    heading = dotted(prefix)
    classes = seams.get(prefix, [])
    callees = deps.get(prefix, [])
    lines = [f"## {heading}"]
    if classes:
        lines.append("### Public Seam")
        for name in classes:
            lines.append(f"#### {name}")
            lines.append("")
    if callees:
        lines.append("### Dependencies")
        for callee in callees:
            lines.append(f" - `{dotted(callee)}` — moduleDependsOn")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def write_document(prefixes: list[str], seams: dict[str, list[str]], deps: dict[str, list[str]]) -> None:
    tops = [p for p in prefixes if "/" not in p]
    nested = [p for p in prefixes if "/" in p]
    ordered = tops + nested
    chunks = [
        "# Modules",
        "",
        "*Context-Driven Delivery* is how an agent installs practices, opens a work session, and runs generate, document, and scan from the markdown that sits beside the code. Public classes and dependencies below are the latest CodeQL first-class prefixes and `moduleDependsOn` edges.",
        "",
    ]
    for prefix in ordered:
        chunks.append(render_module(prefix, seams, deps))
    out = ROOT / ".context" / "module-context.md"
    out.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {out} modules={len(ordered)} classes={sum(len(seams.get(p, [])) for p in ordered)}")


def main() -> None:
    prefixes = first_class_prefixes()
    print("prefixes:")
    for prefix in prefixes:
        print(f"  {prefix}")
    write_subject_filter(prefixes)
    seam_csv = SESSION / "public-seam.csv"
    deps_csv = SESSION / "module-deps.csv"
    if not (seam_csv.exists() and deps_csv.exists()):
        write_queries()
        SESSION.mkdir(parents=True, exist_ok=True)
        database = ROOT / ".codeql" / "python-master"
        run_query(SEAM_QL, SESSION / "public-seam.bqrs", seam_csv, database)
        run_query(DEPS_QL, SESSION / "module-deps.bqrs", deps_csv, database)
        SEAM_QL.unlink(missing_ok=True)
        DEPS_QL.unlink(missing_ok=True)
    write_document(prefixes, load_seams(seam_csv), load_deps(deps_csv))


if __name__ == "__main__":
    main()
