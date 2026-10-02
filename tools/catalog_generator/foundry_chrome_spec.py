"""BDD specs for Foundry brand overlay on catalog commons."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from installation.installer import Installer  # noqa: F401 — load Destination before Catalog
from catalog_generator.foundry_chrome import (
    Brand,
    _drawio_frame_viewport,
    _drawio_iframe,
    approach_principle_grid,
    catalog_examples_html,
    ddd_class_fold_ranges,
    markdown_to_html,
    scenario_step_fold_ranges,
    step_fold_ranges,
)


with description("foundry chrome brand"):
    with before.each:
        self._tmp = tempfile.TemporaryDirectory()
        self.out = Path(self._tmp.name)

    with after.each:
        self._tmp.cleanup()

    with context("that copies commons with the bundled brand"):
        with it("should place abd.works wordmarks under commons/brand"):
            dest = Brand().copy_commons(self.out)
            expect((dest / "brand" / "abd.works.wordmark.black.svg").is_file()).to(
                equal(True)
            )

    with context("that applies a brand folder from elsewhere"):
        with it("should overlay that folder onto commons/brand"):
            other = self.out / "other-brand"
            other.mkdir()
            (other / "mark.txt").write_text("alt", encoding="utf-8")
            commons = Brand().copy_commons(self.out / "catalog")
            Brand(folder=other).apply(commons)
            expect((commons / "brand" / "mark.txt").read_text(encoding="utf-8")).to(
                equal("alt")
            )


with description("a catalog brands collection"):
    with before.each:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.client = self.root / "brands" / "acme"
        self.client.mkdir(parents=True)
        (self.client / "mark.txt").write_text("acme", encoding="utf-8")
        self.out_root = self.root / "catalog"
        Brand().copy_commons(self.out_root)

    with after.each:
        self._tmp.cleanup()

    with context("that has named brand folders"):
        with it("should list each folder name"):
            expect("acme" in Brand(collection=self.root / "brands").folders()).to(equal(True))

        with it("should include the bundled abd-works brand"):
            expect("abd-works" in Brand(collection=self.root / "brands").folders()).to(equal(True))

    with context("with apply_brand given a collection name"):
        with it("should copy that folder onto the catalog commons brand"):
            Brand(collection=self.root / "brands").apply_named(self.out_root, "acme")
            expect(
                (self.out_root / "commons" / "brand" / "mark.txt").read_text(
                    encoding="utf-8"
                )
            ).to(equal("acme"))

    with context("with Catalog apply_brand given a collection name"):
        with it("should overlay that brand onto the catalog out_root commons"):
            from catalog_generator.catalog_generator import Catalog

            catalog = Catalog(
                out_root=str(self.out_root),
                brands_root=self.root / "brands",
            )
            catalog.apply_brand("acme")
            expect(
                (self.out_root / "commons" / "brand" / "mark.txt").read_text(
                    encoding="utf-8"
                )
            ).to(equal("acme"))

        with it("should list known brands when apply_brand is given an empty name"):
            from catalog_generator.catalog_generator import Catalog

            catalog = Catalog(
                out_root=str(self.out_root),
                brands_root=self.root / "brands",
            )
            expect(catalog.apply_brand("")).to(contain("acme"))
            expect(catalog.apply_brand("")).to(contain("abd-works"))


with description("catalog examples"):
    with it("renders a png as an image instead of source text"):
        folder = Path(tempfile.mkdtemp())
        examples = folder / "catalog-examples"
        examples.mkdir()
        png = bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
            "0000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"
        )
        (examples / "story_map.png").write_bytes(png)
        html = catalog_examples_html(folder, "story_map")
        expect("<img" in html).to(equal(True))
        expect("data:image/png;base64," in html).to(equal(True))
        expect("<pre>" in html).to(equal(False))


with description("markdown hard breaks"):
    with it("renders trailing double spaces as line breaks inside a paragraph"):
        html = markdown_to_html("*When* one step  \n*Then* another step")
        expect("<br>" in html).to(equal(True))
        expect("*When*" in html).to(equal(False))
        expect("*Then*" in html).to(equal(False))

    with it("renders scenario steps on separate lines in the catalog example"):
        source = (
            _REPO_ROOT / "practices" / "stories" / "catalog-examples" / "scenarios.md"
        ).read_text(encoding="utf-8")
        html = markdown_to_html(source.split("---", 2)[-1])
        expect(html.count("<br>") > 5).to(equal(True))


with description("step fold ranges"):
    with it("folds a multi-line Given When Then callback and leaves a one-line step open"):
        folded = "when('go', () => {\n  doIt();\n});\n"
        expect(step_fold_ranges(folded)).to(equal([(1, 3)]))
        expect(step_fold_ranges("when('go', () => { doIt(); });\n")).to(equal([]))

    with it("folds And and But bodies as steps"):
        source = (
            "then('a', () => {\n  one();\n})\n"
            "  .and('b', () => {\n    two();\n  });\n"
        )
        expect(step_fold_ranges(source)).to(equal([(1, 3), (4, 6)]))

    with it("folds each step in the acceptance test example"):
        source = (
            _REPO_ROOT / "practices" / "stories" / "catalog-examples" / "acceptance_tests.ts"
        ).read_text(encoding="utf-8")
        ranges = step_fold_ranges(source)
        lines = source.splitlines()
        expect(len(ranges)).to(equal(3))
        expect("Display Create Account" in source).to(equal(False))
        expect("Create Unconfirmed User" in source).to(equal(True))
        start, end = ranges[0]
        expect("given(" in lines[start - 1]).to(equal(True))
        expect(end > start).to(equal(True))

    with it("also folds scenario scaffolding in the acceptance test example"):
        source = (
            _REPO_ROOT / "practices" / "stories" / "catalog-examples" / "acceptance_tests.ts"
        ).read_text(encoding="utf-8")
        ranges = scenario_step_fold_ranges(source)
        expect(len(ranges)).to(equal(4))
        expect(step_fold_ranges(source)).to(equal([(6, 8), (9, 12), (13, 26)]))
        expect((2, 5) in ranges).to(equal(True))
        expect((3, 5) in ranges).to(equal(False))
        expect((33, 34) in ranges).to(equal(False))


with description("ddd class folds"):
    with it("expands the root to operations and collapses every other class"):
        source = (
            _REPO_ROOT / "practices" / "ddd" / "catalog-examples" / "tactics.ts"
        ).read_text(encoding="utf-8")
        lines = source.splitlines()
        ranges = ddd_class_fold_ranges(source)
        starts = {start for start, _end in ranges}

        def line_no(fragment):
            for number, line in enumerate(lines, start=1):
                if fragment in line:
                    return number
            return 0

        customer = line_no("export class Customer")
        identity = line_no("export class Identity")
        operation = line_no("confirmIdentity()")
        customer_operation = line_no("export const CustomerOperation")
        credentials = line_no("export class AccountCredentials")
        credential_errors = line_no("export interface AccountCredentialsErrors")
        expect(customer in starts).to(equal(False))
        expect(identity in starts).to(equal(True))
        expect(operation in starts).to(equal(True))
        expect(customer_operation in starts).to(equal(True))
        expect(credentials in starts).to(equal(False))
        expect(credential_errors in starts).to(equal(True))


with description("story map viewport"):
    with it("frames diagram cells on the top-left page edge without removing content"):
        source = (
            _REPO_ROOT / "practices" / "stories" / "catalog-examples" / "story_map.drawio"
        ).read_text(encoding="utf-8")
        framed = _drawio_frame_viewport(source)
        expect("create-unconfirmed-user" in framed).to(equal(True))
        page_h = int(framed.split('pageHeight="', 1)[1].split('"', 1)[0])
        expect(page_h >= 450).to(equal(True))
        expect('x="20"' in framed).to(equal(True))
        expect(int(framed.split('pageHeight="', 1)[1].split('"', 1)[0]) < 500).to(equal(True))


with description("bounded context viewport"):
    with it("embeds the original diagram page and magnifies in the panel"):
        source = (
            _REPO_ROOT / "practices" / "ddd" / "catalog-examples" / "bounded-context.drawio"
        )
        html = _drawio_iframe(source)
        expect('approach-stage-drawio--framed' in html).to(equal(True))
        expect('data-page-w="1080"' in html).to(equal(True))
        expect('data-page-h="920"' in html).to(equal(True))
        expect('data-zoom-min=' in html).to(equal(False))


with description("building blocks viewport"):
    with it("embeds the original class diagram without rewriting cells"):
        source = (
            _REPO_ROOT / "practices" / "ddd" / "catalog-examples" / "building-blocks.drawio"
        )
        original = source.read_text(encoding="utf-8")
        html = _drawio_iframe(source)
        expect('data-page-w="1654"' in html).to(equal(True))
        expect('data-page-h="1169"' in html).to(equal(True))
        expect('data-zoom-min=' in html).to(equal(False))
        expect("CustomerRepository" in original).to(equal(True))


with description("information architecture viewport"):
    with it("embeds the original journey diagram without rewriting cells"):
        source = (
            _REPO_ROOT
            / "practices"
            / "ux"
            / "catalog-examples"
            / "information-architecture.drawio"
        )
        html = _drawio_iframe(source)
        expect('data-page-w="2400"' in html).to(equal(True))
        expect('data-page-h="680"' in html).to(equal(True))
        expect('data-zoom-min=' in html).to(equal(False))
        expect("Create Account" in source.read_text(encoding="utf-8")).to(equal(True))


with description("product engineering grid"):
    with it("renders one refine row per practice with rewind and play"):
        html = approach_principle_grid(
            [
                {"toolset_name": "stories", "href": "context-tools/stories.html"},
                {"toolset_name": "ddd", "href": "context-tools/ddd.html"},
                {"toolset_name": "ux", "href": "context-tools/ux.html"},
                {"toolset_name": "clean_engineering", "href": "context-tools/clean_engineering.html"},
                {"toolset_name": "bdd", "href": "context-tools/bdd.html"},
            ],
            "descriptions",
        )
        expect('class="pe-tab' in html).to(equal(False))
        expect("Click Discovery, Specification, or Implementation." in html).to(equal(False))
        expect('id="pe-stage-examples"' in html).to(equal(False))
        expect('data-pe-stage="' in html).to(equal(False))
        expect('class="pe-practice__title"' in html).to(equal(False))
        expect("Example coming soon." in html).to(equal(False))
        expect('id="refine-row-stories"' in html).to(equal(True))
        expect('id="refine-row-ddd"' in html).to(equal(True))
        expect('id="refine-row-ux"' in html).to(equal(True))
        expect('id="refine-row-clean_engineering"' in html).to(equal(True))
        expect('id="refine-row-bdd"' in html).to(equal(True))
        expect(html.count('data-refine-nav="1"')).to(equal(5))
        expect(html.count('data-refine-nav="-1"')).to(equal(5))
        expect('class="approach-window__context-label">stories<' in html).to(equal(True))
        expect('class="approach-window__context-label">Domain-driven design<' in html).to(equal(True))
        expect('class="approach-window__context-label">ux<' in html).to(equal(True))
        expect("approach-grid__label--sdd" in html).to(equal(True))
        expect("approach-grid__label--ddd" in html).to(equal(True))
        expect("approach-grid__label--uxd" in html).to(equal(True))
        expect("approach-grid__label--arc" in html).to(equal(True))
        expect("approach-grid__label--bdd" in html).to(equal(True))
        expect("a simple graph is easier to change, compare, and reorganize" in html).to(equal(True))
        expect("catalog-drawio-frame" in html).to(equal(True))
        expect("monaco-ddd-tactics-ts" in html).to(equal(True))
        expect("information-architecture" in html).to(equal(True))
        expect("examples/ux/mockup.png" in html).to(equal(True))
        expect("mockup.html" in html).to(equal(False))
        expect("approach-stage-column" in html).to(equal(True))
        expect("approach-refine__heads" in html).to(equal(True))
        expect("approach-refine__openings" in html).to(equal(True))
        expect("approach-refine__examples" in html).to(equal(True))
        expect("is-open" in html).to(equal(False))
