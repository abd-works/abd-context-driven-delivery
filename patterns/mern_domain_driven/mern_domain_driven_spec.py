"""BDD spec for MernDomainDriven - construction, companion wiring, and contexts."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions", "patterns"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_true, contain, equal, expect
from mamba import before, context, description, it

from patterns.mern_domain_driven.mern_domain_driven import (
    MernDomainDriven,
)
from practices.stories.stories import Stories
from harness.guidance.rule import RulesCollection

_MODULE_DIR = Path(__file__).resolve().parent

_ALL_RULE_SLUGS = (
    "organize-by-domain-module",
    "share-domain-logic",
    "maintain-layer-purity",
    "use-ubiquitous-language",
    "cross-layer-method-naming",
    "preserve-arg-names-across-layers",
    "property-casing-transform",
    "consistent-view-naming",
    "delegate-routes-to-domain-server",
    "ensure-type-safe-routes",
    "standard-mutation-response",
    "implement-domain-entities-correctly",
    "implement-full-interfaces",
    "use-valid-package-names",
    "include-all-external-dependencies",
    "test-story-driven",
    "scaffold-test-scripts",
    "use-thorough-e2e-tests",
)

with description("a MernDomainDriven generator"):
    with before.each:
        self.tool = MernDomainDriven()

    with context("that has been constructed"):
        with it("should default format to typescript"):
            expect(self.tool.format).to(equal("typescript"))

        with it("should default workspace folder to packages"):
            expect(self.tool.default_workspace_folder).to(equal("packages"))

        with it("should key context_index on mern_domain_driven"):
            expect(self.tool.context_index_key).to(equal("mern_domain_driven"))

        with it("should resolve module_dir to this package"):
            expect(self.tool.module_dir).to(equal(_MODULE_DIR))

        with it("should not expose generate, iterate, or satisfy"):
            for name in ("generate", "iterate", "satisfy"):
                expect(name in self.tool.agent_tools).to(equal(False))

    with context("whose _stories() companion is resolved"):
        with before.each:
            self.stories = self.tool._stories()

        with it("should be a Stories instance"):
            expect(isinstance(self.stories, Stories)).to(be_true)

        with it("should pin fidelity to acceptance_tests"):
            expect(self.stories.fidelities.current.fidelity).to(equal("acceptance_tests"))

        with it("should pin format to typescript"):
            expect(self.stories.format).to(equal("typescript"))

        with it("should carry that format through to the Clean Engineering companion"):
            companion = self.stories.fidelities.current.clean_engineering
            expect(companion.practice_guidance.format).to(equal("typescript"))

    with context("whose contexts slot is expanded"):
        with before.each:
            self.rendered = self.tool.scoped_markdown()

        with it("should return non-empty prose"):
            expect(len(self.rendered) > 0).to(be_true)

        with it("should name every ported rule slug"):
            for slug in _ALL_RULE_SLUGS:
                expect(slug in self.rendered).to(equal(True))

    with context("whose rules collection injects on matching package paths"):
        with before.each:
            self.rules = self.tool.rules
            self.payload = {
                "tool_name": "Write",
                "tool_input": {"path": "packages/onboard-a-customer/carts/cart-server.ts"},
            }

        with it("should load shared rules as a RulesCollection"):
            expect(self.rules).to(be_a(RulesCollection))
            expect(len(list(self.rules))).to(equal(len(_ALL_RULE_SLUGS)))

        with it("should scope inject globs to packages feature layout"):
            expect("packages/" in self.rules.glob).to(equal(True))
            expect("src/" in self.rules.glob).to(equal(False))

        with it("should match domain-module server files under packages"):
            expect(self.rules.matches("packages/onboard-a-customer/carts/cart-server.ts")).to(
                equal(True)
            )

        with it("should not match legacy flat src server files"):
            expect(self.rules.matches("src/customer/customer-server.ts")).to(equal(False))

        with it("should inject rules markdown when a matching package file is written"):
            result = self.rules.inject_rules(self.payload)
            expect(result.get("additional_context") or "").to(contain("organize-by-domain-module"))

        with it("should list inject_rules on tools so hook install can enroll it"):
            expect("inject_rules" in self.tool.tools).to(equal(True))
            expect("inject_rules" in self.rules.tools).to(equal(True))
