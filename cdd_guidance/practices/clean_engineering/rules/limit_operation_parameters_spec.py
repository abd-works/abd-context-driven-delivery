"""limit-operation-parameters counts the values an operation takes, however they are packed."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.rules.rule_examples import (
    ce_rule_by_slug,
    practice_from_source,
    rule_pair,
)


def _hits(fixture) -> list[str]:
    return fixture.hits(ce_rule_by_slug("limit-operation-parameters"))


with description("an operation's parameters"):
    # Each fixture builds a graph, so every context builds its fixtures once, before its examples, which only run the rule.
    with context("that pack real values into a tuple the body unpacks"):
        with before.all:
            self.pair = rule_pair(
                "limit-operation-parameters",
                "class Diagram:\n    def _set_geometry(self, cell, _rest):\n        x, y, w, h = _rest\n        return cell, x, y, w, h\n",
                "class Diagram:\n    def _set_geometry(self, cell, bounds):\n        return cell, bounds\n",
            )
            self.place = practice_from_source(
                "class Diagram:\n    def place(self, cell, _rest):\n        x, y, w, h = _rest\n        return cell, x, y, w, h\n"
            )

        with it("should count each unpacked value"):
            self.pair.check()

        with it("should report the real count"):
            expect(_hits(self.place)).to(contain("Operation 'place' takes 5 parameters (maximum 3, excluding self). A packed tuple or *args counts each value it carries."))

    with context("that pack real values into *args"):
        with before.all:
            self.pair = rule_pair(
                "limit-operation-parameters",
                "class Diagram:\n    def place(self, cell, *parts):\n        x, y, w = parts\n        return cell, x, y, w\n",
                "class Diagram:\n    def place(self, cell, *cells):\n        return cell, cells\n",
            )

        with it("should count each value the body unpacks from it"):
            self.pair.check()

    with context("with three named parameters"):
        with before.all:
            self.three = practice_from_source("class Diagram:\n    def place(self, cell, column, row):\n        return cell, column, row\n")

        with it("should accept them"):
            expect(_hits(self.three)).to(equal([]))
