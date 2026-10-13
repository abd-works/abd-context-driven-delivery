"""Story graph rules — language-agnostic (map / graph shape)."""

from practices.stories.rules.four_to_nine_children import FourToNineChildren
from practices.stories.rules.scenarios_shape import ScenariosShape
from practices.stories.rules.verb_noun_format import VerbNounFormat

RULES: tuple = (
    FourToNineChildren(),
    VerbNounFormat(),
    ScenariosShape(),
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
