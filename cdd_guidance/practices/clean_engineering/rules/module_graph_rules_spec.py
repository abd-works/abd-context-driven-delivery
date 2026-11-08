"""A folder of classes and the module card that covers it."""

from expects import equal, expect
from mamba import context, description, it

from cdd_guidance.practices.clean_engineering.rules.rule_examples import ce_rule_by_slug, practice_from_files

_CLASS = "class Cart:\n    def add(self) -> None:\n        return None\n"


def _missing_card_hits(files: dict[str, str]) -> list[str]:
    return practice_from_files(files).hits(ce_rule_by_slug("missing-module-context"))


with description("a folder of classes"):
    with context("with no module card of its own or above it"):
        with it("should be missing its module card"):
            expect(len(_missing_card_hits({"shop/cart/cart.py": _CLASS}))).to(equal(1))

    with context("with a module card of its own"):
        with it("should have its card"):
            files = {"shop/cart/.context/module-context.md": "# shop/cart\n", "shop/cart/cart.py": _CLASS}
            expect(_missing_card_hits(files)).to(equal([]))

    with context("nested in a folder that has a module card"):
        with it("should roll up to that enclosing module"):
            files = {"shop/.context/module-context.md": "# shop\n", "shop/cart/cart.py": _CLASS}
            expect(_missing_card_hits(files)).to(equal([]))

    with context("under only the project's root card"):
        with it("should still be missing its module card"):
            files = {".context/module-context.md": "# project\n", "shop/cart/cart.py": _CLASS}
            expect(len(_missing_card_hits(files))).to(equal(1))
