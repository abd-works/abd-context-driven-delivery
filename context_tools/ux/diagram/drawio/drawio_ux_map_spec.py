"""Draw.io UX channel — CLI Detailed IA + Site Map against the UxMap sketch."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import before, description, it

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from context_tools.ux.diagram.drawio.nodes import DrawioUxMap
from context_tools.ux.ux_model.nodes import Screen, Transition


def _site_map() -> DrawioUxMap:
    ux_map = DrawioUxMap()
    ux_map.scope = "Play Core Mechanics"
    ux_map.story_references = [
        "../context_tools/stories/update_ability_rank_stories.js",
    ]
    ux_map.object_references = []

    sheet = Screen("Character Sheet", 0)
    sheet.apply_layout("sidebar")
    sheet.attach_story_name("Update Ability Rank")
    sheet.attach_domain_term("Character")

    abilities = Screen("Character Sheet — Abilities", 1, chrome_of="Character Sheet")
    abilities.inactive_tabs = ["Identities", "Movements"]

    ux_map.append_screen(sheet)
    ux_map.append_screen(abilities)
    ux_map.transitions.append(
        Transition(
            "selects Abilities tab",
            0,
            from_screen="Character Sheet",
            to_screen="Character Sheet — Abilities",
            trigger="selects Abilities tab",
            nav_type="action",
        )
    )
    return ux_map


with description("DrawioUxMap"):
    with before.each:
        self.source = _site_map()
        self.rendered = DrawioUxMap.render(self.source)
        self.parsed = DrawioUxMap.parse(self.rendered)

    with it("should emit drawio-ux two-page mxfile"):
        expect(self.rendered.startswith("<mxfile")).to(equal(True))
        expect('name="Detailed IA"' in self.rendered).to(equal(True))
        expect('name="Site Map"' in self.rendered).to(equal(True))
        expect("host=\"drawio-ux\"" in self.rendered).to(equal(True))

    with it("should hold story_references on the source map"):
        expect(self.source.story_references.as_list()).to(
            equal(["../context_tools/stories/update_ability_rank_stories.js"])
        )
        expect(self.source.find_screen("Character Sheet").domain_terms).to(
            equal(["Character"])
        )

    with it("should round-trip screen names from the Site Map page"):
        names = [screen.name for screen in self.parsed.screens]
        expect(names).to(equal(["Character Sheet", "Character Sheet — Abilities"]))

    with it("should round-trip layout-seeded region titles from Detailed IA"):
        sheet = next(s for s in self.parsed.screens if s.name == "Character Sheet")
        expect([region.name for region in sheet.regions]).to(equal(["panel", "body"]))

    with it("should round-trip transitions via the Transitions collection"):
        expect(len(self.parsed.transitions)).to(equal(1))
        expect(self.parsed.transitions[0].to_screen).to(
            equal("Character Sheet — Abilities")
        )
        expect(self.parsed.transitions[0].trigger).to(equal("selects Abilities tab"))
