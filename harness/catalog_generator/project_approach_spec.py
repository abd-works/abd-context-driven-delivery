"""Specs for project-specific approach slide generation."""
import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect
from mamba import context, description, it

from harness.catalog_generator.catalog_generator import Catalog, CatalogPractice
from harness.catalog_generator.project_approach import ExampleClassifier, ProjectApproach, ProjectFiles

_PRACTICES = CatalogPractice.load_all()


def _place_of(shown) -> tuple[str, str] | None:
    return (shown.fidelity.practice_guidance.key, shown.stage) if shown is not None else None


def _place(path: str) -> tuple[str, str] | None:
    """The practice and stage of the board fidelity that declares a file at path."""
    return _place_of(ExampleClassifier(_REPO_ROOT, _PRACTICES).place_of(path))


with description("a project file's place on the approach page"):
    with context("with a file a board fidelity declares in its outputs"):
        with it("should map the story map drawio to stories discovery"):
            expect(_place("stories/.context/story-map.drawio")).to(equal(("stories", "discovery")))

        with it("should map a story's scenario test to stories specification"):
            expect(_place("qualify/offer/cross-sell-offer/cross_sell_offer_story.test.ts")).to(equal(("stories", "specification")))

        with it("should map a sub-epic's shared story steps to stories implementation"):
            expect(_place("qualify/qualify-offer.story.shared.ts")).to(equal(("stories", "implementation")))

        with it("should map the bounded context map to ddd discovery"):
            expect(_place("domain/.context/bounded-context-map.md")).to(equal(("ddd", "discovery")))

        with it("should map the domain model markdown to ddd specification"):
            expect(_place("domain/.context/domain-model.md")).to(equal(("ddd", "specification")))

        with it("should map an aggregate named for its folder to ddd specification"):
            expect(_place("sales/client/client.ts")).to(equal(("ddd", "specification")))

        with it("should map the information architecture drawio to ux discovery"):
            expect(_place("qualify/.context/information-architecture.drawio")).to(equal(("ux", "discovery")))

        with it("should map a user goal's html to ux specification"):
            expect(_place("qualify/review-offer.html")).to(equal(("ux", "specification")))

        with it("should map a view component to ux implementation"):
            expect(_place("src/offers/OfferView.tsx")).to(equal(("ux", "implementation")))

    with context("with a file no fidelity declares"):
        with it("should leave it unmapped"):
            expect(_place("notes/readme.txt")).to(equal(None))

        with it("should leave a typescript file not named for its folder unmapped"):
            expect(_place("sales/client/helpers.ts")).to(equal(None))


with description("a project's approach page"):
    with it("should write cdd-approach.html with staged project examples"):
        with tempfile.TemporaryDirectory() as project_dir, tempfile.TemporaryDirectory() as out_dir:
            root = Path(project_dir)
            files = {
                "stories/.context/story-map.drawio": "<mxfile></mxfile>",
                "qualify/offer/cross-sell/cross_sell_story.test.ts": "story('Qualify', () => {});\n",
                "domain/.context/bounded-context-map.md": "# Bounded contexts\n",
                "domain/.context/domain-model.md": "# Domain Model\n",
                "sales/client/client.ts": "export class Client {}\n",
                "ux/.context/information-architecture.drawio": "<mxfile></mxfile>",
                "ux/review-offer.html": "<html></html>",
            }
            for relative, text in files.items():
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
                (root / relative).write_text(text, encoding="utf-8")

            catalog = Catalog(repo_url="https://example.com/demo", ref="abc", out_root=out_dir, project=root)
            message = catalog.generate_project_approach(project_title="Demo Project")
            page = Path(out_dir) / "cdd-approach.html"
            expect(page.is_file()).to(be_true)
            expect(message).to(contain("cdd-approach.html"))
            html = page.read_text(encoding="utf-8")
            expect("approach-page" in html).to(be_true)
            expect("story-map.drawio" in html or "catalog-drawio-frame" in html).to(be_true)

    with it("should link no repository for a project that is not a git checkout"):
        with tempfile.TemporaryDirectory() as project_dir:
            expect(ProjectApproach.for_project(ProjectFiles(project_dir, _PRACTICES)).repo_url).to(equal(""))

    with it("should take its title from the project's folder when none is saved"):
        with tempfile.TemporaryDirectory() as parent:
            project = Path(parent) / "demo-shop"
            project.mkdir()
            expect(ProjectApproach.for_project(ProjectFiles(project, _PRACTICES)).project_title).to(equal("Demo Shop"))

    with it("should put the examples a JSON mapping names over the ones it found"):
        with tempfile.TemporaryDirectory() as project_dir:
            chosen = ProjectApproach.for_project(ProjectFiles(project_dir, _PRACTICES)).with_examples_json('{"examples": {"ddd": {"discovery": "map.md"}}}')
            placed = {_place_of(shown): path for shown, path in chosen.examples.items()}
            expect(placed[("ddd", "discovery")]).to(equal((Path(project_dir) / "map.md").resolve()))
