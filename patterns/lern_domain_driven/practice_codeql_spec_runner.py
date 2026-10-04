"""Faulty vs repaired CodeQL trees for each LERN practice-pack query that has .examples."""

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
    lern_codeql_packs,
    locate_rule_query,
)
from harness.knowledge_graph.model.graph_query_spec import (
    ensure_examples_db,
    write_match_all_filter,
)

_LERN = Path(__file__).resolve().parent


def _faulty_repaired_misses(pack: Path) -> list[str]:
    root = pack / ".examples"
    if not root.is_dir():
        return []
    misses: list[str] = []
    write_match_all_filter(pack, "javascript")
    for slug_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        slug = slug_dir.name
        query = locate_rule_query(pack, slug)
        if query is None:
            misses.append(f"{slug} missing query")
            continue
        faulty = slug_dir / "faulty"
        repaired = slug_dir / "repaired"
        if faulty.is_dir():
            database = ensure_examples_db(faulty, "javascript")
            batch = CodeQL(faulty).run_queries(
                [query], database=database, write_filter=False
            )
            rows = Rows.from_tuples(batch.get(slug) or [])
            if not rows:
                misses.append(f"{slug} silent on faulty")
        if repaired.is_dir():
            database = ensure_examples_db(repaired, "javascript")
            try:
                batch = CodeQL(repaired).run_queries(
                    [query], database=database, write_filter=False
                )
                rows = Rows.from_tuples(batch.get(slug) or [])
            except CodeQLRunError as error:
                if "no bqrs" not in str(error):
                    raise
                rows = []
            if rows:
                misses.append(f"{slug} noisy on repaired")
    return misses


with description("LERN practice CodeQL runner"):
    with it("should report faulty examples and stay quiet on repaired examples"):
        misses: list[str] = []
        for pack in lern_codeql_packs("typescript"):
            misses.extend(_faulty_repaired_misses(pack))
        expect(misses).to(equal([]))
