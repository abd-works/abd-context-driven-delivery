"""Draw.io UX channel - CLI Detailed IA + Site Map against the UxMap sketch."""

import sys
from pathlib import Path

from expects import be, equal, expect, raise_error
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.ux.model.drawio.nodes import DrawioCliTimedOut, DrawioUxMap, UnreadableDrawio
from cdd_guidance.practices.ux.model.nodes import Region, Screen, Transition


class SpecFixture:
    def site_map(self) -> DrawioUxMap:
        ux_map = DrawioUxMap.create()
        ux_map.scope = "Play Core Mechanics"
        ux_map.story_references = [
            "../practices/stories/update_ability_rank_stories.js",
        ]

        sheet = Screen("Character Sheet", 0)
        sheet.apply_layout("sidebar")
        sheet.append_region(Region("panel", 0, "panel"))
        sheet.append_region(Region("body", 1, "body"))
        sheet.show_story("Update Ability Rank")
        sheet.attach_domain_term("Character")

        abilities = Screen("Character Sheet - Abilities", 1, chrome_of=sheet)
        abilities.inactive_tabs = ["Identities", "Movements"]

        ux_map.append_screen(sheet)
        ux_map.append_screen(abilities)
        ux_map.transitions.append(
            Transition("selects Abilities tab", 0, sheet, abilities, "selects Abilities tab", "action")
        )
        return ux_map


fixture = SpecFixture()


with description("a UX map drawn as a draw.io information architecture"):
    with before.each:
        self.source = fixture.site_map()
        self.rendered = DrawioUxMap.create().render(self.source)

    with it("should emit drawio-ux two-page mxfile"):
        expect(self.rendered.startswith("<mxfile")).to(equal(True))
        expect('name="Detailed IA"' in self.rendered).to(equal(True))
        expect('name="Site Map"' in self.rendered).to(equal(True))
        expect("host=\"drawio-ux\"" in self.rendered).to(equal(True))

    with context("that is read back"):
        with before.each:
            self.parsed = DrawioUxMap.create().parse(self.rendered)

        with it("should read back the screen names from the Site Map page"):
            names = [screen.name for screen in self.parsed.screens]
            expect(names).to(equal(["Character Sheet", "Character Sheet - Abilities"]))

        with it("should read back the region titles from Detailed IA"):
            expect([region.name for region in self.parsed.find_screen("Character Sheet").regions]).to(
                equal(["panel", "body"])
            )

        with it("should read back the transition trigger"):
            expect([transition.trigger for transition in self.parsed.transitions]).to(equal(["selects Abilities tab"]))

        with it("should link the transition to the screens on the read map"):
            expect(self.parsed.transitions[0].to_screen).to(be(self.parsed.find_screen("Character Sheet - Abilities")))

        with it("should keep the regions on the read map's graph"):
            expect(self.parsed.find_screen("Character Sheet").regions[0].graph).to(be(self.parsed.graph))

    with context("that is not XML"):
        with it("should refuse it as an unreadable diagram"):
            expect(lambda: DrawioUxMap.create().parse("<mxfile><diagram>")).to(raise_error(UnreadableDrawio))

    with context("with a command line that runs past its timeout"):
        with before.each:
            self.writer = DrawioUxMap.create()
            self.writer.cli_timeout_seconds = 0.001

        with it("should stop it and say it timed out"):
            expect(lambda: self.writer.render(self.source)).to(raise_error(DrawioCliTimedOut))
