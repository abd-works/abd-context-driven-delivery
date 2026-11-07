"""BDD spec for ClaudeDesignUxMap - prototype screens placed on the canvas, never read back."""

import json
import sys
from pathlib import Path

from expects import equal, expect, raise_error
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.ux.model.claude_design.nodes import ClaudeDesignScreensNotReadable, ClaudeDesignUxMap
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.model.ux_map_spec_fixture import OrderingMap


with description("a UX map placed as Claude Design screens"):
    with before.each:
        self.source = OrderingMap().build(UxMap.create())
        self.boards = json.loads(ClaudeDesignUxMap.create().render(self.source))

    with it("should place each screen's prototype once, on its own page"):
        expect(self.boards).to(equal({
            "screens/catalog.dc.html": {
                "x": 0, "y": 0, "w": 1600, "h": 1100, "page": "screen-catalog", "title": "Catalog",
                "is_interactive": True,
            },
        }))

    with context("that is read back"):
        with it("should refuse, since the canvas owns the screens"):
            expect(lambda: ClaudeDesignUxMap.create().parse("{}")).to(raise_error(ClaudeDesignScreensNotReadable))
