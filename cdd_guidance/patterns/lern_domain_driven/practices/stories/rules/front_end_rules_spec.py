import tempfile
from pathlib import Path
from types import SimpleNamespace

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.patterns.lern_domain_driven.practices.stories.rules.front_end_rules import UserStoriesHaveAFrontEnd


def _story(name: str, story_type: str = "user") -> SimpleNamespace:
    facts = {"story_type": story_type}
    return SimpleNamespace(node_id=f"stories:Story:{name}", name=name, source=SimpleNamespace(file="story-map.md"), get_fact=lambda key, default=None: facts.get(key, default))


class _Context:
    def __init__(self, root: Path, stories: list) -> None:
        self.source_root = root
        self._stories = stories

    def nodes(self, type: str | None = None) -> list:
        return self._stories


with description("user stories have a front end") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp())
        (self.root / "organize.story.ui.spec.ts").write_text("test.describe('Add Child Ticket', () => {})\n", encoding="utf-8")
        self.rule = UserStoriesHaveAFrontEnd()

    with context("with a user story a screen story describes"):
        with it("should pass it"):
            expect(self.rule.check_practice(_Context(self.root, [_story("Add Child Ticket")]))).to(equal([]))

    with context("with a user story no screen story describes"):
        with before.each:
            self.found = self.rule.check_practice(_Context(self.root, [_story("Reassign Ticket Parent")]))

        with it("should fail it"):
            expect(len(self.found)).to(equal(1))

        with it("should say it has no front end"):
            expect(self.found[0][1]).to(contain("has no front end"))

    with context("with a system story no screen story describes"):
        with it("should pass it, since only a person's story needs a screen"):
            expect(self.rule.check_practice(_Context(self.root, [_story("Store Each Screenshot", "system")]))).to(equal([]))

    with context("with a technical story no screen story describes"):
        with it("should pass it"):
            expect(self.rule.check_practice(_Context(self.root, [_story("Read Session File Once", "technical")]))).to(equal([]))
