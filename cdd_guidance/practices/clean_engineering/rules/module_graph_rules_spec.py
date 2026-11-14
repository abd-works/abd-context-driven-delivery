"""A folder of classes and the module card that covers it."""

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.rules.rule_examples import ce_rule_by_slug, practice_from_files

_CLASS = "class Cart:\n    def add(self) -> None:\n        return None\n"


def _missing_card_hits(fixture) -> list[str]:
    return fixture.hits(ce_rule_by_slug("missing-module-context"))


with description("a folder of classes"):
    # Each fixture builds a graph, so every context builds its folder once, before its example, which only runs the rule.
    with context("with no module card of its own or above it"):
        with before.all:
            self.folder = practice_from_files({"shop/cart/cart.py": _CLASS})

        with it("should be missing its module card"):
            expect(len(_missing_card_hits(self.folder))).to(equal(1))

    with context("with a module card of its own"):
        with before.all:
            self.folder = practice_from_files({"shop/cart/.context/module-context.md": "# shop/cart\n", "shop/cart/cart.py": _CLASS})

        with it("should have its card"):
            expect(_missing_card_hits(self.folder)).to(equal([]))

    with context("nested in a folder that has a module card"):
        with before.all:
            self.folder = practice_from_files({"shop/.context/module-context.md": "# shop\n", "shop/cart/cart.py": _CLASS})

        with it("should roll up to that enclosing module"):
            expect(_missing_card_hits(self.folder)).to(equal([]))

    with context("under only the project's root card"):
        with before.all:
            self.folder = practice_from_files({".context/module-context.md": "# project\n", "shop/cart/cart.py": _CLASS})

        with it("should still be missing its module card"):
            expect(len(_missing_card_hits(self.folder))).to(equal(1))
