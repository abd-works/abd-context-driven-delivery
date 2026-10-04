"""Every practice CodeQL rule has a failing example and a passing example."""

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions", "patterns"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

from harness.knowledge_graph.model.codeql import CodeQL, CodeQLRunError, Rows
from harness.knowledge_graph.model.codeql_layout import (
    codeql_pack,
    extractor_language,
    lern_codeql_pack,
    locate_rule_query,
    rule_stems_in_pack,
)
from harness.knowledge_graph.model.graph_query_spec import refine_rows, write_match_all_filter

_DB_ROOT = _REPO_ROOT / ".cq"
_PRACTICES = ("clean_engineering", "ddd", "stories")
_EXAMPLE_HOMES = {
    "clean_engineering": _REPO_ROOT / "practices" / "clean_engineering" / "examples",
    "ddd": _REPO_ROOT / "practices" / "ddd" / "model" / "codeql" / ".examples",
    "stories": _REPO_ROOT / "practices" / "stories" / "model" / "codeql" / ".examples",
}


def _rmtree(path: Path) -> None:
    text = str(path.resolve())
    if not text.startswith("\\\\?\\"):
        text = "\\\\?\\" + text
    shutil.rmtree(text, ignore_errors=True)


def _source_stamp(examples: Path) -> str:
    times = [
        str(item.stat().st_mtime_ns)
        for item in examples.rglob("*")
        if item.is_file() and ".codeql" not in item.parts
    ]
    return hashlib.sha1("\n".join(times).encode("utf-8")).hexdigest()


def _ensure_db(examples: Path, language: str) -> Path:
    digest = hashlib.sha1(str(examples.resolve()).encode("utf-8")).hexdigest()[:16]
    database = _DB_ROOT / digest
    stamp_file = database / "source-stamp.txt"
    stamp = _source_stamp(examples)
    codeql = CodeQL(examples)
    if codeql._database_ready(database) and stamp_file.is_file() and stamp_file.read_text(encoding="utf-8") == stamp:
        return database
    if database.exists():
        _rmtree(database)
    _DB_ROOT.mkdir(parents=True, exist_ok=True)
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
    stamp_file.write_text(stamp, encoding="utf-8")
    return database


def _rows(codeql: CodeQL, query: Path, database: Path, slug: str) -> list:
    try:
        batch = codeql.run_queries([query], database=database, write_filter=False)
    except CodeQLRunError as error:
        if "no bqrs" in str(error):
            return []
        raise
    rows = Rows.from_tuples(batch.get(slug) or [])
    if slug in {
        "verb-noun-format",
        "story-name-captures-system-mechanic",
        "domain-concepts-not-technical-names",
        "keep-classes-single-responsibility",
        "missing-module-context",
        "language-modules-one-section",
        "public-seam-only",
        "modules-not-model-blocks",
    }:
        return refine_rows(slug, rows)
    return rows


def _example_language(folder: Path) -> str:
    suffixes = {item.suffix.lower() for item in folder.rglob("*") if item.is_file()}
    if suffixes & {".ts", ".tsx", ".js", ".jsx"}:
        return "javascript"
    return "python"


def _slugs(practice: str) -> set[str]:
    slugs: set[str] = set()
    lern = lern_codeql_pack(practice, "typescript")
    if (lern / "qlpack.yml").is_file():
        slugs |= rule_stems_in_pack(lern)
    for language in ("python", "javascript", "typescript"):
        pack = codeql_pack(practice, language)
        if (pack / "qlpack.yml").is_file():
            slugs |= rule_stems_in_pack(pack)
    return slugs


def _pack_for(practice: str, slug: str, language: str) -> Path | None:
    if language == "javascript":
        lern = lern_codeql_pack(practice, "typescript")
        if locate_rule_query(lern, slug) is not None:
            return lern
        for pack_language in ("javascript", "typescript"):
            pack = codeql_pack(practice, pack_language)
            if locate_rule_query(pack, slug) is not None:
                return pack
        return None
    pack = codeql_pack(practice, "python")
    if locate_rule_query(pack, slug) is not None:
        return pack
    return None


def _jobs() -> list[tuple[str, str, Path | None, str]]:
    jobs: list[tuple[str, str, Path | None, str]] = []
    for practice in _PRACTICES:
        for slug in sorted(_slugs(practice)):
            faulty = _EXAMPLE_HOMES[practice] / slug / "faulty"
            language = _example_language(faulty) if faulty.is_dir() else "javascript"
            jobs.append((practice, slug, _pack_for(practice, slug, language), language))
    return jobs


def _check(practice: str, slug: str, pack: Path | None, language: str) -> list[str]:
    misses: list[str] = []
    examples = _EXAMPLE_HOMES[practice]
    faulty = examples / slug / "faulty"
    repaired = examples / slug / "repaired"
    label = f"{practice}/{slug}"
    if pack is None:
        return [f"{label} missing query"]
    query = locate_rule_query(pack, slug)
    if query is None:
        return [f"{label} missing query"]
    if not faulty.is_dir():
        return [f"{label} missing failing example"]
    if not repaired.is_dir():
        return [f"{label} missing passing example"]
    write_match_all_filter(pack, language)
    try:
        if not _rows(CodeQL(faulty), query, _ensure_db(faulty, language), slug):
            misses.append(f"{label} silent on failing example")
        if _rows(CodeQL(repaired), query, _ensure_db(repaired, language), slug):
            misses.append(f"{label} noisy on passing example")
    except Exception as error:
        misses.append(f"{label} {type(error).__name__}: {error}")
    return misses


with description("practice CodeQL runner"):
    with it("should fail the failing example and pass the passing example for every rule"):
        misses: list[str] = []
        for practice, slug, pack, language in _jobs():
            misses.extend(_check(practice, slug, pack, language))
        expect(misses).to(equal([]))
