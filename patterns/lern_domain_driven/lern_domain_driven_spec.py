"""BDD spec for LernDomainDriven — construction, companion wiring, contexts,
and end-to-end scanning of its rules/scanners (development fidelity)."""

import sys
from pathlib import Path

_MODULE_DIR = Path(__file__).resolve().parent
_REPO_ROOT = Path(__file__).resolve().parents[2]
_root = str(_REPO_ROOT)
_foreign = str(Path.home() / "OneDrive - abd.works" / "personal" / "paradise-mobile" / "abd-context-driven-delivery")
sys.path[:] = [
    p
    for p in sys.path
    if not (p.replace("/", "\\").lower().startswith(_foreign.lower()) and ".venv" not in p.lower())
]
if _root in sys.path:
    sys.path.remove(_root)
sys.path.insert(0, _root)
for _cat in ("tools", "practices", "actions", "patterns"):
    _p = str(_REPO_ROOT / _cat)
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)
sys.path.insert(0, _root)
for _name in list(sys.modules):
    if (
        _name in {"harness", "scan", "lifecycle", "workspace", "practices", "patterns", "tools"}
        or _name.startswith("harness.")
        or _name.startswith("scan.")
        or _name.startswith("practices.")
        or _name.startswith("patterns.")
        or _name.startswith("tools.")
    ):
        del sys.modules[_name]

from expects import be_a, be_true, contain, equal, expect
from mamba import before, context, description, it

from practices.clean_engineering.specifications._scan_kit import (
    DOMAIN_MODULE_RULE_GLOBS,
    ScannerCollection,
)
from patterns.lern_domain_driven.lern_domain_driven import (
    LernDomainDriven,
)
from practices.stories.stories import Stories
from harness.knowledge_graph.model.graph_rules import GraphRule, GraphRulesCollection

_ALL_RULE_SLUGS = (
    "epic-package-screens-only",
    "domain-core-file-matches-folder-slug",
    "node-tier-uses-node-suffix",
    "client-subtypes-domain-hosts-browser-logic",
    "node-decides-next-page",
    "router-asks-the-node",
    "views-render-only",
    "share-domain-logic",
    "maintain-layer-purity",
    "use-ubiquitous-language",
    "cross-layer-method-naming",
    "preserve-arg-names-across-layers",
    "property-casing-transform",
    "consistent-view-naming",
    "ensure-type-safe-routes",
    "standard-mutation-response",
    "implement-domain-entities-correctly",
    "implement-full-interfaces",
    "use-valid-package-names",
    "include-all-external-dependencies",
    "test-story-driven",
    "scaffold-test-scripts",
    "use-thorough-e2e-tests",
    "one-json-store-per-aggregate",
    "repository-owns-aggregate-lifecycle",
    "ask-cross-aggregate-sync",
)

with description("a LernDomainDriven generator"):
    with before.each:
        self.tool = LernDomainDriven()

    with context("that has been constructed"):
        with it("should default format to typescript"):
            expect(self.tool.format).to(equal("typescript"))

        with it("should default workspace folder to packages"):
            expect(self.tool.default_workspace_folder).to(equal("packages"))

        with it("should key context_index on lern_domain_driven"):
            expect(self.tool.context_index_key).to(equal("lern_domain_driven"))

        with it("should resolve module_dir to this package"):
            expect(self.tool.module_dir).to(equal(_MODULE_DIR))

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
            self.rendered = (_MODULE_DIR / "lern_domain_driven.md").read_text(encoding="utf-8")

        with it("should return non-empty prose"):
            expect(len(self.rendered) > 0).to(be_true)

        with it("should name every ported rule slug"):
            for slug in _ALL_RULE_SLUGS:
                expect(slug in self.rendered).to(equal(True))

        with it("should specify lowdb as the persistence adapter"):
            expect("lowdb" in self.rendered.lower()).to(be_true)

        with it("should cite the DDD building-blocks markdown"):
            expect(self.rendered).to(contain("ddd.md"))
            expect(self.rendered).to(contain("Aggregate Root"))
            expect(self.rendered).to(contain("Repository"))

        with it("should require one JSON store per aggregate"):
            expect(self.rendered).to(contain("one-json-store-per-aggregate"))

        with it("should require repositories to load create search and update the aggregate root"):
            expect(self.rendered).to(contain("repository-owns-aggregate-lifecycle"))
            expect("load" in self.rendered.lower()).to(be_true)
            expect("create" in self.rendered.lower()).to(be_true)
            expect("search" in self.rendered.lower()).to(be_true)
            expect("update" in self.rendered.lower()).to(be_true)

        with it("should require AskQuestion for cross-aggregate sync when generating stories"):
            expect(self.rendered).to(contain("AskQuestion"))
            expect(self.rendered).to(contain("ask-cross-aggregate-sync"))
            expect("event" in self.rendered.lower()).to(be_true)

    with context("whose CodeQL packs list the architecture rules"):
        with before.each:
            self.discovered = ScannerCollection(module_dir=_MODULE_DIR).discover()

        with it("should resolve a typescript query pack per attributed practice"):
            for practice in ("clean_engineering", "ddd", "stories"):
                pack = _MODULE_DIR / "practices" / practice / "model" / "typescript" / "codeql"
                expect((pack / "qlpack.yml").is_file()).to(equal(True))
                expect((pack / "rules").is_dir()).to(equal(True))
                expect((pack / "loaders").is_dir()).to(equal(True))

        with it("should register exactly the architecture rules, one query each"):
            expect(sorted(self.discovered)).to(equal(sorted(_ALL_RULE_SLUGS)))

        with it("should not ship javascript or python query packs"):
            expect((_MODULE_DIR / "model" / "javascript").exists()).to(equal(False))
            expect((_MODULE_DIR / "model" / "python").exists()).to(equal(False))

        with it("should keep rule queries flat under each practice rules folder"):
            for practice in ("clean_engineering", "ddd", "stories"):
                rules_root = _MODULE_DIR / "practices" / practice / "model" / "typescript" / "codeql" / "rules"
                expect(any(rules_root.glob("*.ql"))).to(be_true)
                expect(list(rules_root.glob("*/*.ql"))).to(equal([]))

    with context("whose graph rules carry pattern and parent-practice metadata"):
        with before.each:
            self.rules = self.tool.rules

        with it("should tag every graph rule with the lern_domain_driven pattern"):
            for rule in self.rules:
                if not isinstance(rule, GraphRule):
                    continue
                expect(getattr(rule, "pattern", None)).to(equal("lern_domain_driven"))

        with it("should attribute layout rules to clean_engineering"):
            expect(self.rules["epic-package-screens-only"].practice).to(equal("clean_engineering"))
            expect(self.rules["epic-package-screens-only"].fidelity).to(equal("code"))

        with it("should attribute aggregate rules to ddd"):
            expect(self.rules["one-json-store-per-aggregate"].practice).to(equal("ddd"))
            expect(self.rules["one-json-store-per-aggregate"].fidelity).to(equal("tactics"))

        with it("should attribute story-test rules to stories"):
            expect(self.rules["test-story-driven"].practice).to(equal("stories"))
            expect(self.rules["test-story-driven"].fidelity).to(equal("acceptance_tests"))

    with context("whose rules collection injects on matching paths"):
        with before.each:
            self.rules = self.tool.rules
            self.payload = {
                "tool_name": "Write",
                "tool_input": {"path": "src/customer/customer-node.ts"},
            }

        with it("should load shared rules as a GraphRulesCollection"):
            expect(self.rules).to(be_a(GraphRulesCollection))
            expect(len(list(self.rules))).to(equal(len(_ALL_RULE_SLUGS)))

        with it("should scope inject globs to src domains and epic packages"):
            expect(self.rules.glob).to(equal(DOMAIN_MODULE_RULE_GLOBS))

        with it("should match domain node files under src"):
            expect(self.rules.matches("src/customer/customer-node.ts")).to(equal(True))

        with it("should match epic screen files under packages"):
            expect(self.rules.matches("packages/wire-pay/send-wire/send-wire.tsx")).to(equal(True))

        with it("should not match unrelated files outside src or packages"):
            expect(self.rules.matches("actions/validate/validate.py")).to(equal(False))

        with it("should upgrade rules with graph queries to GraphRule"):
            expect(self.rules["epic-package-screens-only"]).to(be_a(GraphRule))
            expect(self.rules["epic-package-screens-only"].graphQuery.is_file()).to(equal(True))

        with it("should inject rules markdown when a matching src file is written"):
            result = self.rules.inject_rules(self.payload)
            expect(result.get("additional_context") or "").to(contain("node-tier-uses-node-suffix"))

        with it("should list inject_rules on tools so hook install can enroll it"):
            expect("inject_rules" in self.tool.tools).to(equal(True))
            expect("inject_rules" in self.rules.tools).to(equal(True))
