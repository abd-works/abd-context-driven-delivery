"""Same loader/rule stems in python, javascript, and typescript packs."""

from pathlib import Path

from expects import equal, expect
from mamba import description, it

from harness.knowledge_graph.model.codeql_layout import (
    SOURCE_LANGUAGES,
    codeql_pack,
    listed_practices,
)

_SKIP = {"rules.ql"}


def _stems(pack: Path, folder: str) -> set[str]:
    root = pack / folder
    if not root.is_dir():
        return set()
    return {path.stem for path in root.glob("*.ql") if path.name not in _SKIP}


with description("CodeQL language pack parity"):
    with it("should keep the same loader and rule files for python, javascript, and typescript"):
        misses = []
        for practice in listed_practices():
            packs = {lang: codeql_pack(practice, lang) for lang in SOURCE_LANGUAGES}
            for folder in ("loaders", "rules"):
                by_lang = {lang: _stems(pack, folder) for lang, pack in packs.items()}
                expected = set.union(*by_lang.values()) if any(by_lang.values()) else set()
                for lang, stems in by_lang.items():
                    missing = sorted(expected - stems)
                    if missing:
                        misses.append(f"{practice}/{lang}/{folder}: {missing}")
        expect(misses).to(equal([]))
