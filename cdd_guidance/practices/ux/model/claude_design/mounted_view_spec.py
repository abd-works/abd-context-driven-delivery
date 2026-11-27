"""Mamba spec for a story's screen drawn by the product's own production view, mounted on the canvas from the
project's view bundle. The bundle built with esbuild and run in Node is in mounted_view_heavy_spec.py."""

import re
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.ux.model.claude_design.mounted_view import MountedViewBundle, MountedViewMarkup
from cdd_guidance.practices.ux.model.claude_design.screen_artboard import ScreenArtboard
from cdd_guidance.practices.ux.model.claude_design.story_screen import StoryScreen

BUNDLE = MountedViewBundle(project_root=Path("."), entry="packages/my-paradise/canvas-views.tsx", folder="paradise", namespace="Paradise")


with description("a story's screen mounting a production view") as self:
    with before.all:
        self.screen = StoryScreen(title="Add Line To Cart", story="Add Line To Cart", markup=MountedViewMarkup("PlanCatalogScreen", BUNDLE),
                                  positions={"Add one more line": [{"cartOpen": False}, {"cartOpen": True}]})
        self.html = self.screen.html

    with context("loading the views"):
        with it("should link the bundle's stylesheet from the version's design-system folder"):
            expect(self.html).to(contain('<link rel="stylesheet" href="../ds/paradise/paradise.css">'))

        with it("should load the bundle's script before the fixtures bundle"):
            expect(self.html).to(contain('<script src="../ds/paradise/paradise.js"></script>\n<script src="../fixtures/canvas-fixtures.js"></script>'))

    with context("drawing the view"):
        with it("should mount the project's view by name through the bundle's CanvasMount"):
            expect(self.html).to(contain('<x-import component-from-global-scope="Paradise.CanvasMount" view="PlanCatalogScreen"'))

        with it("should hand the view every object the scenario bound, the repositories, the position and the explorer's go"):
            mount = re.search(r"<x-import[^>]*>", self.html).group(0)
            given = re.findall(r'(bound|repositories|position|go)="\{\{ (\w+) \}\}"', mount)
            expect(given).to(equal([("bound", "bound"), ("repositories", "repositories"), ("position", "position"), ("go", "go")]))

        with it("should draw it inside the screen's frame, which the scoped stylesheet answers to"):
            expect(self.html).to(contain('<div class="canvas-screen" style="box-sizing: border-box; width: 390px;'))
            expect(re.search(r'<div class="canvas-screen"[^>]*>\n<div class="canvas-mount">\n<x-import', self.html)).not_to(equal(None))

        with it("should still load its scenario through the fixture bar"):
            expect(ScreenArtboard(self.html).loads_fixtures).to(equal(True))

    with context("drawn in the canvas's theme"):
        with it("should set the theme on the view's wrapper, where its scoped design tokens answer to it"):
            themed = StoryScreen(title="Cart", story="Cart", markup=MountedViewMarkup("PlanCatalogScreen", BUNDLE), positions={}, theme="dark").html
            expect(themed).to(contain('<div class="canvas-mount" data-theme="dark">'))

    with context("a bundle"):
        with it("should be drawn by its namespace's CanvasMount"):
            expect(BUNDLE.component).to(equal("Paradise.CanvasMount"))
