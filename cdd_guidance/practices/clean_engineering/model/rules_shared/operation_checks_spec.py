"""Operation rules measure every operation a file defines: public and private methods, constructors, getters, and
module functions."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[5]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect, have_len
from mamba import context, description, it

from cdd_guidance.practices.clean_engineering.rules.rule_examples import (
    assert_rule_pair,
    ce_rule_by_slug,
    practice_from_source,
    violations_for_rule,
)


def _hits(slug: str, source: str, lang: str = "python") -> list[str]:
    return violations_for_rule(ce_rule_by_slug(slug), *practice_from_source(source, lang=lang))


def _long_body(lines: int, indent: str = "    ") -> str:
    return "".join(f"{indent}total = total + {index % 2}\n" for index in range(lines))


_NESTED = (
    "    for line in text:\n"
    "        if line:\n"
    "            for word in line:\n"
    "                if word:\n"
    "                    return word\n"
    "    return ''\n"
)
_FLAT = (
    "    words = [word for line in text for word in line if word]\n"
    "    return words[0] if words else ''\n"
)


with description("Operation rules over a file's operations"):
    with context("prefer-instance-operations"):
        with it("should flag a classmethod named current, the global accessor the rule replaces"):
            assert_rule_pair(
                "prefer-instance-operations",
                "class Board:\n    @classmethod\n    def current(cls) -> 'Board':\n        return cls()\n",
                "class Board:\n    def columns(self) -> list:\n        return []\n",
            )

        with it("should still accept a from_ mapping factory"):
            source = "class Board:\n    @classmethod\n    def from_folder(cls, folder: str) -> 'Board':\n        return cls()\n"
            expect(_hits("prefer-instance-operations", source)).to(equal([]))

    with context("keep-operations-small-focused"):
        with it("should flag a long module function in a file that also holds a class"):
            assert_rule_pair(
                "keep-operations-small-focused",
                "class Sketch:\n    def read(self) -> int:\n        return _parse_sketch(1)\n\n\n"
                "def _parse_sketch(total: int) -> int:\n" + _long_body(25) + "    return total\n",
                "class Sketch:\n    def read(self) -> int:\n        return _parse_sketch(1)\n\n\n"
                "def _parse_sketch(total: int) -> int:\n" + _long_body(5) + "    return total\n",
            )

        with it("should flag a long private method"):
            assert_rule_pair(
                "keep-operations-small-focused",
                "class Sketch:\n    def _parse(self, total: int) -> int:\n" + _long_body(25, "        ") + "        return total\n",
                "class Sketch:\n    def _parse(self, total: int) -> int:\n        return total\n",
            )

        with it("should measure a module function as its own operation"):
            source = "class Sketch:\n    def read(self) -> int:\n        return 1\n\n\ndef _parse(total: int) -> int:\n" + _long_body(25) + "    return total\n"
            expect(_hits("keep-operations-small-focused", source)).to(equal(["Operation '_parse' is 27 lines (max 20)."]))

        with it("should flag a long property getter"):
            source = "class Sketch:\n    @property\n    def total(self) -> int:\n        total = 0\n" + _long_body(25, "        ") + "        return total\n"
            expect(_hits("keep-operations-small-focused", source)).to(equal(["Property 'total' is 28 lines (max 20)."]))

        with it("should flag a long TypeScript constructor"):
            body = "".join(f"    this.total = this.total + {index % 2};\n" for index in range(25))
            source = "export class Sketch {\n  total = 0;\n  constructor() {\n" + body + "  }\n}\n"
            expect(_hits("keep-operations-small-focused", source, lang="typescript")).to(have_len(1))

        with it("should measure a public method once"):
            source = "class Sketch:\n    def parse(self, total: int) -> int:\n" + "".join(
                f"        total = total + {index % 2}\n" for index in range(25)
            ) + "        return total\n"
            expect(_hits("keep-operations-small-focused", source)).to(have_len(1))

    with context("simplify-control-flow"):
        with it("should flag a module function nested four levels deep"):
            assert_rule_pair(
                "simplify-control-flow",
                "class Sketch:\n    def read(self) -> str:\n        return _first_word([])\n\n\ndef _first_word(text: list) -> str:\n" + _NESTED,
                "class Sketch:\n    def read(self) -> str:\n        return _first_word([])\n\n\ndef _first_word(text: list) -> str:\n" + _FLAT,
            )

    with context("never-swallow-exceptions"):
        with it("should flag an except Exception that returns a fallback"):
            assert_rule_pair(
                "never-swallow-exceptions",
                "class Loader:\n    def load(self, path: str) -> str:\n        try:\n            return open(path).read()\n"
                "        except Exception:\n            return ''\n",
                "class Loader:\n    def load(self, path: str) -> str:\n        try:\n            return open(path).read()\n"
                "        except Exception as error:\n            raise CartUnreadable(path) from error\n",
            )

        with it("should flag a private helper whose except Exception substitutes a default"):
            assert_rule_pair(
                "never-swallow-exceptions",
                "class Loader:\n    def _load(self, path: str) -> str:\n        try:\n            text = open(path).read()\n"
                "        except Exception:\n            text = 'empty'\n        return text\n",
                "class Loader:\n    def _load(self, path: str) -> str:\n        return open(path).read()\n",
            )

        with it("should accept a specific exception handled with a quiet result"):
            source = "class Prices:\n    def price(self, sku: str) -> int:\n        try:\n            return self.table[sku]\n        except KeyError:\n            return 0\n"
            expect(_hits("never-swallow-exceptions", source)).to(equal([]))

        with it("should flag a TypeScript catch that returns a fallback value"):
            assert_rule_pair(
                "never-swallow-exceptions",
                "export class Loader {\n  load(path: string): string | null {\n    try { return read(path); } catch (err) { return null; }\n  }\n}\n",
                "export class Loader {\n  load(path: string): string {\n    try { return read(path); } catch (err) { throw new CartUnreadable(path); }\n  }\n}\n",
                lang="typescript",
            )

    with context("use-exceptions-properly"):
        with it("should flag an except Exception that never re-raises"):
            assert_rule_pair(
                "use-exceptions-properly",
                "class Loader:\n    def load(self, path: str) -> str:\n        try:\n            return open(path).read()\n"
                "        except Exception:\n            return ''\n",
                "class Loader:\n    def load(self, path: str) -> str:\n        try:\n            return open(path).read()\n"
                "        except OSError:\n            return ''\n",
            )

        with it("should accept an except Exception that converts to a domain exception"):
            source = (
                "class Loader:\n    def load(self, path: str) -> str:\n        try:\n            return open(path).read()\n"
                "        except Exception as error:\n            raise CartUnreadable(path) from error\n"
            )
            expect(_hits("use-exceptions-properly", source)).to(equal([]))
