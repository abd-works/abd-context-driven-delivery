"""A Claude Code mod pattern: construction, its rules, its overlay, and its templates."""

import re
from pathlib import Path

import yaml
from expects import be_a, be_true, contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.patterns.cdd_claude_mod.cdd_claude_mod import CddClaudeMod
from harness.guidance.rule import RulesCollection

_MODULE_DIR = Path(__file__).resolve().parent
_MARKDOWN = (_MODULE_DIR / "cdd_claude_mod.md").read_text(encoding="utf-8")
_RULE_SLUGS = re.findall(r"^- \*\*`([a-z0-9-]+)`\*\*", _MARKDOWN, re.M)
_TEMPLATES = (
    "{domain}/pane/.claude-plugin/plugin.json",
    "{domain}/pane/types/index.d.ts",
    "{domain}/pane/hooks/hooks.json",
    "{domain}/pane/hooks/register.tsx",
    "{domain}/pane/hooks/{domain}/{object}-client.ts",
    "{domain}/pane/hooks/{domain}/{screen}-view.tsx",
)


with description("a Claude Code mod pattern"):
    with before.each:
        self.tool = CddClaudeMod()

    with context("that has been constructed"):
        with it("should default format to typescript"):
            expect(self.tool.format).to(equal("typescript"))

        with it("should default workspace folder to harness"):
            expect(self.tool.default_workspace_folder).to(equal("harness"))

        with it("should key context_index on cdd_claude_mod"):
            expect(self.tool.context_index_key).to(equal("cdd_claude_mod"))

        with it("should resolve module_dir to this package"):
            expect(self.tool.module_dir).to(equal(_MODULE_DIR))

    with context("whose guidance has been read"):
        with it("should name every layer of a domain component"):
            for layer in ("| Domain |", "| Tool |", "| Generated |", "| Contract |", "| Client |", "| View |", "| Boot |", "| Manifest |"):
                expect(_MARKDOWN).to(contain(layer))

        with it("should keep the domain in Python"):
            expect(_MARKDOWN).to(contain("domain-lives-in-python"))

        with it("should trace one action from the client to the domain"):
            expect(_MARKDOWN).to(contain("`moveNext($, ticket)` | `ticket.move_next` | `Ticket.move_next()`"))

        with it("should name each client after the object it mirrors"):
            expect(_MARKDOWN).to(contain("`TicketClient` for `Ticket`"))

        with it("should keep $ out of the client, which only displays"):
            expect(_MARKDOWN).to(contain("client-only-displays"))

        with it("should make every action and view a plain function that takes $"):
            expect(_MARKDOWN).to(contain("actions-are-plain-functions"))

        with it("should build the client and view from any class with MCP operations"):
            expect(_MARKDOWN).to(contain("**The input is any class with MCP operations.**"))

        with it("should map each LERN piece to its counterpart"):
            expect(_MARKDOWN).to(contain("patterns-lern-domain-driven"))

        with it("should test through the mounted pane and keep no browser tests"):
            expect("Playwright" in _MARKDOWN).to(equal(False))

    with context("whose rules collection injects on matching paths"):
        with before.each:
            self.rules = self.tool.rules

        with it("should load shared rules as a RulesCollection"):
            expect(self.rules).to(be_a(RulesCollection))

        with it("should load every rule the markdown states"):
            expect(len(list(self.rules))).to(equal(len(_RULE_SLUGS)))

        with it("should match a mod's hooks"):
            expect(self.rules.matches("harness/report/pane/hooks/register.tsx")).to(be_true)

        with it("should not match Python outside a mod"):
            expect(self.rules.matches("harness/kanban/board.py")).to(equal(False))

    with context("whose graph overlay has been read"):
        with before.each:
            self.overlay = yaml.safe_load((_MODULE_DIR / "practices/ddd/model/rules.yaml").read_text(encoding="utf-8"))

        with it("should name only rules the markdown states"):
            named = {slug for node in self.overlay.values() for slug in node["rules"]}
            expect(sorted(named - set(_RULE_SLUGS))).to(equal([]))

        with it("should give rules only to types its schema declares"):
            schema = yaml.safe_load((_MODULE_DIR / "practices/ddd/model/schema.yaml").read_text(encoding="utf-8"))
            expect(sorted(set(self.overlay) - set(schema))).to(equal([]))

    with context("whose templates have been read"):
        with it("should scaffold every piece of a mod"):
            for template in _TEMPLATES:
                expect((_MODULE_DIR / "templates" / template).is_file()).to(be_true)

        with it("should give the client constructor no $"):
            client = (_MODULE_DIR / "templates" / "{domain}/pane/hooks/{domain}/{object}-client.ts").read_text(encoding="utf-8")
            expect(client).to(contain("constructor(private readonly json: {Object}Data) {}"))

        with it("should pass $ to the view, which is a plain function"):
            view = (_MODULE_DIR / "templates" / "{domain}/pane/hooks/{domain}/{screen}-view.tsx").read_text(encoding="utf-8")
            expect(view).to(contain("export function {Screen}View($: EngineInterface,"))
