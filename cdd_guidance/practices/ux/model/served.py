"""What a screen or a control serves, in the one notation every text format lists it in, and the kind of navigation a
transition is."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List

if TYPE_CHECKING:
    from cdd_guidance.practices.ux.model.nodes import ServesStories
    from cdd_guidance.practices.ux.model.story_link import StoryLink


class Served:
    """The stories, scenarios, and steps one screen or control serves, as a format lists them: a line for each kind
    that has any, `Stories: Browse Books · Check Out`, under its heading, the things joined by ` · `."""

    # The heading each kind is listed under, in the order the lines list them, and the kind it names.
    KINDS = (("Stories", "Story"), ("Scenarios", "Scenario"), ("Steps", "Step"))
    BESIDE = " · "

    def __init__(self, node: "ServesStories") -> None:
        self._node = node

    @property
    def stories(self) -> List["StoryLink"]:
        return self._node.links_of("Story")

    @property
    def scenarios(self) -> List["StoryLink"]:
        return self._node.links_of("Scenario")

    @property
    def steps(self) -> List["StoryLink"]:
        return self._node.links_of("Step")

    def kind_headed(self, heading: str) -> str:
        """The kind a heading lists, whatever its case: `Story` for `stories`; none for any other heading."""
        return next((kind for written, kind in self.KINDS if written.lower() == heading.strip().lower()), "")

    def serve(self, kind: str, shown: str) -> None:
        """Serve each thing of kind one line lists in shown, the things joined by ` · `."""
        for item in (item.strip() for item in shown.split(self.BESIDE)):
            if item:
                self._node.show(kind, item)

    def as_lines(self, link_text: Callable[["StoryLink"], str]) -> List[str]:
        """A line for each kind it serves any of, `Stories: ...`, each thing written as link_text writes its link."""
        listed = ((heading, [link_text(link) for link in self._node.links_of(kind)]) for heading, kind in self.KINDS)
        return [f"{heading}: {self.BESIDE.join(items)}" for heading, items in listed if items]

    def read_lines(self, lines: List[str]) -> None:
        """Serve what lines list under each kind's heading; a line under no such heading is no part of it."""
        for heading, kind in self.KINDS:
            start = f"{heading.lower()}:"
            line = next((line.strip() for line in lines if line.strip().lower().startswith(start)), "")
            self.serve(kind, line[len(start):])


class NavType(str):
    """The kind of navigation a transition is, saved as the string it is written as: an action (``action``), the kind
    a transition is made with, a tab (``tab``), which a drawing draws dashed, or any other kind a sketch names, such as
    ``top nav``, which a drawing writes before the trigger."""

    ACTION: "NavType"
    TAB: "NavType"

    @property
    def is_tab(self) -> bool:
        return self == NavType.TAB

    @property
    def is_named_on_label(self) -> bool:
        """Whether a drawing names it before the trigger: every kind but an action and a tab, which its line shows."""
        return self not in (NavType.ACTION, NavType.TAB, "")

    @classmethod
    def from_drawn(cls, kept: str, dashed: bool) -> "NavType":
        """The kind a drawn transition is: the one it keeps by name, else a tab for a dashed line, else an action."""
        return cls(kept) if kept else (cls.TAB if dashed else cls.ACTION)


NavType.ACTION = NavType("action")
NavType.TAB = NavType("tab")
