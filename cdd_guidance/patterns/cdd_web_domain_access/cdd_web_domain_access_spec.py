"""The CDD web domain access pattern: guidance, rules, and templates."""

import re
from pathlib import Path

from expects import be_a, be_true, contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.patterns.cdd_web_domain_access.cdd_web_domain_access import CddWebDomainAccess
from harness.guidance.rule import RulesCollection

_MODULE_DIR = Path(__file__).resolve().parent
_MARKDOWN = (_MODULE_DIR / "cdd_web_domain_access.md").read_text(encoding="utf-8")
_RULE_SLUGS = re.findall(r"^- \*\*`([a-z0-9-]+)`\*\*", _MARKDOWN, re.M)
_TEMPLATES = (
    "src/cdd/cdd-routes.ts",
    "src/{context}/{object}/{object}-client.tsx",
)


with description("a CDD web domain access pattern"):
    with context("that has been constructed"):
        with before.all:
            self.pattern = CddWebDomainAccess()

        with it("should default format to typescript"):
            expect(self.pattern.format).to(equal("typescript"))

        with it("should key context_index on cdd_web_domain_access"):
            expect(self.pattern.pattern).to(equal("cdd_web_domain_access"))

    with context("whose guidance has been read"):
        with it("should keep the domain in Python"):
            expect(_MARKDOWN).to(contain("The domain, its rules, and its state stay in Python"))

        with it("should make every MCP call on the server"):
            expect(_MARKDOWN).to(contain("**Every MCP call is made on the server.**"))

        with it("should give each object its own classes, with no god connector"):
            expect(_MARKDOWN).to(contain("Each domain object has its own classes"))

        with it("should name every layer from the domain to the connection"):
            for layer in ("| Domain |", "| Tool |", "| Contract |", "| Mark |", "| Language adapter |", "| Connection |"):
                expect(_MARKDOWN).to(contain(layer))

        with it("should deploy the adapter as an installer channel"):
            expect(_MARKDOWN).to(contain("### The language adapter is a deployment target"))

        with it("should keep lowdb for what CDD does not own"):
            expect(_MARKDOWN).to(contain("**lowdb is for state CDD does not own.**"))

    with context("whose rules collection injects on matching paths"):
        with before.all:
            self.rules = CddWebDomainAccess().rules

        with it("should load shared rules as a RulesCollection"):
            expect(self.rules).to(be_a(RulesCollection))

        with it("should load every rule the markdown states"):
            expect(len(list(self.rules))).to(equal(len(_RULE_SLUGS)))

    with context("whose templates are scaffolded"):
        with it("should have every template the guidance names"):
            for template in _TEMPLATES:
                expect((_MODULE_DIR / "templates" / template).is_file()).to(be_true)
