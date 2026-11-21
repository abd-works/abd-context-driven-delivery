from types import SimpleNamespace

from expects import contain, equal, expect
from mamba import context, description, it

from cdd_guidance.patterns.lern_domain_driven.practices.stories.rules.shared_story_rules import PlaywrightTestsBrowserInteraction


def _node(name: str, **facts) -> SimpleNamespace:
    return SimpleNamespace(node_id=f"stories:Story:{name}", name=name, source=SimpleNamespace(file="story-map.md"),
                           get_fact=lambda key, default=None: facts.get(key, default))


class _Context:
    def __init__(self, stories: list) -> None:
        self._stories = stories

    def nodes(self, type: str | None = None) -> list:
        return self._stories if type == "Story" else []


with description("every story has a screen story"):
    with context("with a story the overlay's read found a screen story file describing"):
        with it("should pass it"):
            found = PlaywrightTestsBrowserInteraction().check_practice(_Context([_node("Add Child Ticket", has_screen_story=True)]))
            expect(found).to(equal([]))

    with context("with a story no screen story file describes"):
        with it("should fail it, saying it has no screen story"):
            found = PlaywrightTestsBrowserInteraction().check_practice(_Context([_node("Reassign Ticket Parent", has_screen_story=False)]))
            expect(found[0].message).to(contain("has no screen story"))
