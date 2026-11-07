"""Draw.io UX channel - CLI Detailed IA + Site Map against the UxMap sketch."""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.ux.model.drawio.nodes import DrawioUxMap
from cdd_guidance.practices.ux.model.nodes import Region, Screen, Transition


class SpecFixture:
    def site_map(self) -> DrawioUxMap:
        ux_map = DrawioUxMap.create()
        ux_map.scope = "Play Core Mechanics"
        ux_map.story_references = [
            "../practices/stories/update_ability_rank_stories.js",
        ]
        ux_map.object_references = []

        sheet = Screen("Character Sheet", 0)
        sheet.apply_layout("sidebar")
        sheet.append_region(Region("panel", 0, "panel"))
        sheet.append_region(Region("body", 1, "body"))
        sheet.attach_story_name("Update Ability Rank")
        sheet.attach_domain_term("Character")

        abilities = Screen("Character Sheet - Abilities", 1, chrome_of="Character Sheet")
        abilities.inactive_tabs = ["Identities", "Movements"]

        ux_map.append_screen(sheet)
        ux_map.append_screen(abilities)
        ux_map.transitions.append(
            Transition(
                "selects Abilities tab",
                0,
                from_screen="Character Sheet",
                to_screen="Character Sheet - Abilities",
                trigger="selects Abilities tab",
                nav_type="action",
            )
        )
        return ux_map


fixture = SpecFixture()


with description("DrawioUxMap"):
    with before.each:
        self.source = fixture.site_map()
        self.rendered = DrawioUxMap.create().render(self.source)
        self.parsed = DrawioUxMap.create().parse(self.rendered)

    with it("should emit drawio-ux two-page mxfile"):
        expect(self.rendered.startswith("<mxfile")).to(equal(True))
        expect('name="Detailed IA"' in self.rendered).to(equal(True))
        expect('name="Site Map"' in self.rendered).to(equal(True))
        expect("host=\"drawio-ux\"" in self.rendered).to(equal(True))

    with it("should hold story_references on the source map"):
        expect(self.source.story_references.as_list()).to(
            equal(["../practices/stories/update_ability_rank_stories.js"])
        )
        expect(self.source.find_screen("Character Sheet").domain_terms).to(
            equal(["Character"])
        )

    with it("should round-trip screen names from the Site Map page"):
        names = [screen.name for screen in self.parsed.screens]
        expect(names).to(equal(["Character Sheet", "Character Sheet - Abilities"]))

    with it("should round-trip region titles from Detailed IA"):
        sheet = next(s for s in self.parsed.screens if s.name == "Character Sheet")
        expect([region.name for region in sheet.regions]).to(equal(["panel", "body"]))

    with it("should round-trip transitions via the Transitions collection"):
        expect(len(self.parsed.transitions)).to(equal(1))
        expect(self.parsed.transitions[0].to_screen).to(
            equal("Character Sheet - Abilities")
        )
        expect(self.parsed.transitions[0].trigger).to(equal("selects Abilities tab"))

    with context("that holds three screens side by side with transitions between them"):
        with before.each:
            ux_map = DrawioUxMap.create()
            for order, name in enumerate(["Board", "Editor", "Explorer"]):
                screen = Screen(name, order)
                screen.append_region(Region("body", 0, "body"))
                ux_map.append_screen(screen)
            for order, (source, target) in enumerate([("Board", "Explorer"), ("Explorer", "Board"), ("Editor", "Explorer")]):
                ux_map.transitions.append(Transition(f"go {order}", order, from_screen=source, to_screen=target, trigger=f"go {order}", nav_type="action"))
            page = ET.fromstring(DrawioUxMap.create().render(ux_map)).find(".//diagram[@name='Detailed IA']")
            cells = page.findall(".//mxCell")
            self.screen_top = min(
                float(cell.find("mxGeometry").get("y"))
                for cell in cells if cell.get("value") in ("Board", "Editor", "Explorer")
            )
            self.lanes = [
                [float(point.get("y")) for point in cell.findall(".//mxPoint")]
                for cell in cells if cell.get("edge") == "1"
            ]

        with it("should route every transition above the screens"):
            expect(all(points and max(points) < self.screen_top for points in self.lanes)).to(equal(True))

        with it("should give each transition a lane of its own"):
            expect(len({points[0] for points in self.lanes if points})).to(equal(len(self.lanes)))
