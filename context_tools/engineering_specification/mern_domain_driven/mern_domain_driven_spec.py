"""BDD spec for MernDomainDriven - construction, companion wiring, contexts,
and end-to-end scanning of its own ported rules/scanners (development fidelity)."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("context_tools", "primitives", "utilities"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

from context_tools.engineering_specification.mern_domain_driven.mern_domain_driven import (
    MernDomainDriven,
)
from context_tools.stories.stories import Stories

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

        with it("should expose generate, iterate, and satisfy"):
            for name in ("generate", "iterate", "satisfy"):
                expect(name in self.tool.actions).to(equal(True))

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
            self.rendered = self.tool.contexts().expand()

        with it("should return non-empty prose"):
            expect(len(self.rendered) > 0).to(be_true)

        with it("should name every ported rule slug"):
            for slug in _ALL_RULE_SLUGS:
                expect(slug in self.rendered).to(equal(True))

    with context("whose scanners are discovered from its own scanners/ folder"):
        with before.each:
            from utilities.scanners.scanner_collection import ScannerCollection

            self.discovered = ScannerCollection(module_dir=_MODULE_DIR).discover()

        with it("should register exactly the 18 ported rules, one scanner each"):
            expect(sorted(self.discovered)).to(equal(sorted(_ALL_RULE_SLUGS)))

    with context("whose ported scanners run end-to-end against its own templates/"):
        with before.each:
            from utilities.scanners.scanner_collection import ScannerCollection

            collection = ScannerCollection(module_dir=_MODULE_DIR)
            self.report = collection.run(_MODULE_DIR, [_MODULE_DIR / "templates"])

        with it("should report violations for the tool's own folder shape (no scripts/ or playwright/vitest config)"):
            rules = {v.rule for v in self.report.violations}
            expect(rules).to(equal({"scaffold-test-scripts"}))

        with it("should not flag the route template for calling the repository directly"):
            rules = {v.rule for v in self.report.violations}
            expect("delegate-routes-to-domain-server" in rules).to(equal(False))
