"""limit-operation-parameters counts the values an operation takes, however they are packed."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import context, description, it

from harness.graph.ce_rule_eval_harness import (
    assert_rule_pair,
    ce_rule_by_slug,
    practice_from_source,
    violations_for_rule,
)


def _hits(source: str) -> list[str]:
    return violations_for_rule(ce_rule_by_slug("limit-operation-parameters"), *practice_from_source(source))


with description("an operation's parameters"):
    with context("that pack real values into a tuple the body unpacks"):
        with it("should count each unpacked value"):
            assert_rule_pair(
                "limit-operation-parameters",
                "class Diagram:\n    def _set_geometry(self, cell, _rest):\n        x, y, w, h = _rest\n        return cell, x, y, w, h\n",
                "class Diagram:\n    def _set_geometry(self, cell, bounds):\n        return cell, bounds\n",
            )

        with it("should report the real count"):
            source = "class Diagram:\n    def place(self, cell, _rest):\n        x, y, w, h = _rest\n        return cell, x, y, w, h\n"
            expect(_hits(source)).to(contain("Operation 'place' takes 5 parameters (maximum 3, excluding self). A packed tuple or *args counts each value it carries."))

    with context("that pack real values into *args"):
        with it("should count each value the body unpacks from it"):
            assert_rule_pair(
                "limit-operation-parameters",
                "class Diagram:\n    def place(self, cell, *parts):\n        x, y, w = parts\n        return cell, x, y, w\n",
                "class Diagram:\n    def place(self, cell, *cells):\n        return cell, cells\n",
            )

    with context("with three named parameters"):
        with it("should accept them"):
            expect(_hits("class Diagram:\n    def place(self, cell, column, row):\n        return cell, column, row\n")).to(equal([]))
