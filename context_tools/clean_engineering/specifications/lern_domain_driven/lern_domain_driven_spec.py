"""BDD spec for LernDomainDriven — construction, companion wiring, contexts,
and end-to-end scanning of its rules/scanners (development fidelity)."""

import sys
from pathlib import Path

_MODULE_DIR = Path(__file__).resolve().parent
_REPO_ROOT = Path(__file__).resolve().parents[4]
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
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)
sys.path.insert(0, _root)
for _name in list(sys.modules):
    if (
        _name in {"primitives", "scan", "lifecycle", "workspace", "context_tools", "tools"}
        or _name.startswith("primitives.")
        or _name.startswith("scan.")
        or _name.startswith("context_tools.")
        or _name.startswith("tools.")
    ):
        del sys.modules[_name]

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

from context_tools.clean_engineering.specifications.lern_domain_driven.lern_domain_driven import (
    LernDomainDriven,
)
from context_tools.stories.stories import Stories
from scan.scanner_collection import ScannerCollection

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
            expect(self.stories.fidelity).to(equal("acceptance_tests"))

        with it("should pin format to typescript"):
            expect(self.stories.format).to(equal("typescript"))

        with it("should carry that format through to its own ce() companion"):
            expect(self.stories.ce().format).to(equal("typescript"))

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

    with context("whose scanners are discovered from its own scanners/ folder"):
        with before.each:
            self.discovered = ScannerCollection(module_dir=_MODULE_DIR).discover()

        with it("should register exactly the architecture rules, one scanner each"):
            expect(sorted(self.discovered)).to(equal(sorted(_ALL_RULE_SLUGS)))

    with context("whose ported scanners run end-to-end against its own templates/"):
        with before.each:
            collection = ScannerCollection(module_dir=_MODULE_DIR)
            self.report = collection.run(_MODULE_DIR, [_MODULE_DIR / "templates"])

        with it("should report violations for the tool's own folder shape (no scripts/ or playwright/vitest config)"):
            rules = {v.rule for v in self.report.violations}
            expect(rules).to(equal({"scaffold-test-scripts"}))

        with it("should not flag the route template for calling the repository directly"):
            rules = {v.rule for v in self.report.violations}
            expect("delegate-routes-to-domain-server" in rules).to(equal(False))
