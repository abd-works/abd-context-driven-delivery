"""Run a pack's graphQuery files in one CodeQL process."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

from harness.knowledge_graph.model.vocabulary_helper import VocabularyHelper
from harness.knowledge_graph.model.codeql import CodeQL, Rows
from harness.knowledge_graph.model.codeql_layout import extractor_language

_VAGUE_VERBS = {"handle", "process", "manage", "do", "perform"}
_GENERIC_NOUNS = {"request", "data", "record", "item", "thing", "info"}


def _story_words(label: str) -> List[str]:
    return [part.lower() for part in (label or "").replace("_", " ").split() if part]


def _rows_for_verb_noun(rows: Iterable[dict]) -> List[dict]:
    refined: List[dict] = []
    seen = set()
    for row in rows:
        label = row.get("message") or ""
        if label in seen:
            continue
        words = _story_words(label)
        if not words:
            continue
        first = words[0]
        rest = words[1:]
        vocabulary = VocabularyHelper()
        gerund, _ = vocabulary.is_gerund(first)
        verb = vocabulary.is_verb(first)
        noun = any(vocabulary.is_noun(word) for word in rest)
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


def _rows_for_vague_mechanic(rows: Iterable[dict]) -> List[dict]:
    refined: List[dict] = []
    seen = set()
    for row in rows:
        label = row.get("message") or ""
        if label in seen:
            continue
        words = _story_words(label)
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


def refine_rows(slug: str, rows: List[dict]) -> List[dict]:
    if slug == "keep-classes-single-responsibility":
        from practices.clean_engineering.model.responsibilities import Responsibilities

        return Responsibilities().hits_for_keep_classes(rows)
    if slug == "verb-noun-format":
        return _rows_for_verb_noun(rows)
    if slug == "story-name-captures-system-mechanic":
        return _rows_for_vague_mechanic(rows)
    if slug == "domain-concepts-not-technical-names":
        from practices.ddd.model.technical_names import rows_for_technical_names

        return rows_for_technical_names(rows)
    from practices.clean_engineering.model.module_context_files import ModuleContextFiles

    files = ModuleContextFiles()
    if slug == "missing-module-context":
        return files.rows_for_missing_module_context(rows)
    if slug == "language-modules-one-section":
        return files.rows_for_language_modules_one_section(rows)
    if slug == "public-seam-only":
        return files.rows_for_public_seam_only(rows)
    if slug == "modules-not-model-blocks":
        return files.rows_for_modules_not_model_blocks(rows)
    return rows

Refine = Callable[[str, List[dict]], List[dict]]


def write_match_all_filter(pack: Path, language: str) -> None:
    if extractor_language(language) == "javascript":
        pack.joinpath("subject_filter.qll").write_text(
            "import javascript\n\n"
            'predicate subjectFilterPrefix(string prefix) { prefix = "" }\n\n'
            'predicate firstClassModulePrefix(string prefix) { none() }\n\n'
            "predicate inSubject(AstNode n) { exists(n.getLocation()) }\n\n"
            "predicate inSubjectPath(string path) { exists(File f | path = f.getRelativePath()) }\n",
            encoding="utf-8",
        )
        return
    pack.joinpath("subject_filter.qll").write_text(
        "import python\n\n"
        'predicate subjectFilterPrefix(string prefix) { prefix = "" }\n\n'
        "predicate inSubject(AstNode n) { exists(n.getLocation()) }\n\n"
        "predicate inSubjectFilter(Class cls) { inSubject(cls) }\n\n"
        "predicate inSubjectPath(string path) { exists(File f | path = f.getRelativePath()) }\n\n"
        "predicate firstClassModulePrefix(string prefix) {\n"
        "  exists(File init |\n"
        '    init.getBaseName() = "__init__.py" and\n'
        "    prefix = init.getParentContainer().getRelativePath().replaceAll(\"\\\\\", \"/\")\n"
        "  )\n"
        "}\n",
        encoding="utf-8",
    )


def ensure_examples_db(examples: Path, language: str) -> Path:
    import shutil
    import subprocess

    codeql = CodeQL(examples)
    database = examples / ".codeql" / f"{language}-db"
    if codeql._database_ready(database):
        return database
    if database.exists():
        shutil.rmtree(database, ignore_errors=True)
    database.parent.mkdir(parents=True, exist_ok=True)

    run = subprocess.run(
        [
            codeql.executable(),
            "database",
            "create",
            str(database),
            f"--language={extractor_language(language)}",
            f"--source-root={examples}",
            "--overwrite",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if run.returncode != 0 or not codeql._database_ready(database):
        raise RuntimeError(run.stderr or run.stdout)
    return database


def hit(rows: Iterable[dict], expected: str) -> bool:
    for row in rows:
        blob = " ".join(str(row.get(key) or "") for key in ("name", "message"))
        if expected in blob:
            return True
    return False


def _rule_query_path(pack: Path, slug: str) -> Path:
    from harness.knowledge_graph.model.codeql_layout import locate_rule_query

    found = locate_rule_query(pack, slug)
    if found is not None:
        return found
    return pack / f"{slug}.ql"


def assert_pack_hits(
    pack: Path,
    examples: Path,
    language: str,
    rules: Dict[str, str],
    *,
    tests: Optional[Dict[str, str]] = None,
    refine: Optional[Refine] = None,
) -> List[str]:
    database = ensure_examples_db(examples, language)
    write_match_all_filter(pack, language)
    codeql = CodeQL(examples)
    combined = pack / "rules.ql"
    if combined.is_file() and (pack / "rule_hits.qll").is_file():
        batch = codeql.run_rules(
            combined, list(rules), database=database, write_filter=False
        )
    else:
        queries = [_rule_query_path(pack, slug) for slug in rules]
        batch = codeql.run_queries(queries, database=database, write_filter=False)
    if tests:
        test_queries = [pack / "tests" / f"{name}.ql" for name in tests]
        batch.update(codeql.run_queries(test_queries, database=database, write_filter=False))
    misses: List[str] = []
    for slug, expected in rules.items():
        rows = Rows.from_tuples(batch.get(slug) or [])
        rows = (refine or refine_rows)(slug, rows)
        if not hit(rows, expected):
            misses.append(f"{slug} expected {expected}")
    for name, expected in (tests or {}).items():
        rows = Rows.from_tuples(batch.get(name) or [])
        if not hit(rows, expected):
            misses.append(f"{name} expected {expected}")
    return misses
