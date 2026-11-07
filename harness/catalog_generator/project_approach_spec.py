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

from harness.catalog_generator.project_approach import ExampleClassifier, PracticeStage, ProjectApproach, ProjectFiles


with description("a project file's place on the approach page"):
    with context("with a file a board fidelity declares in its outputs"):
        with it("should map the story map drawio to stories discovery"):
            place = ExampleClassifier().place_of("stories/.context/story-map.drawio")
            expect(place).to(equal(PracticeStage("stories", "discovery")))

        with it("should map a story's scenario test to stories specification"):
            place = ExampleClassifier().place_of("qualify/offer/cross-sell-offer/cross_sell_offer_story.test.ts")
            expect(place).to(equal(PracticeStage("stories", "specification")))

        with it("should map a sub-epic's shared story steps to stories implementation"):
            place = ExampleClassifier().place_of("qualify/qualify-offer.story.shared.ts")
            expect(place).to(equal(PracticeStage("stories", "implementation")))

        with it("should map the bounded context map to ddd discovery"):
            place = ExampleClassifier().place_of("domain/.context/bounded-context-map.md")
            expect(place).to(equal(PracticeStage("ddd", "discovery")))

        with it("should map the domain model markdown to ddd specification"):
            place = ExampleClassifier().place_of("domain/.context/domain-model.md")
            expect(place).to(equal(PracticeStage("ddd", "specification")))

        with it("should map an aggregate named for its folder to ddd specification"):
            place = ExampleClassifier().place_of("sales/client/client.ts")
            expect(place).to(equal(PracticeStage("ddd", "specification")))

        with it("should map the information architecture drawio to ux discovery"):
            place = ExampleClassifier().place_of("qualify/.context/information-architecture.drawio")
            expect(place).to(equal(PracticeStage("ux", "discovery")))

        with it("should map a user goal's html to ux specification"):
            place = ExampleClassifier().place_of("qualify/review-offer.html")
            expect(place).to(equal(PracticeStage("ux", "specification")))

        with it("should map a view component to ux implementation"):
            place = ExampleClassifier().place_of("src/offers/OfferView.tsx")
            expect(place).to(equal(PracticeStage("ux", "implementation")))

    with context("with a file no fidelity declares"):
        with it("should leave it unmapped"):
            expect(ExampleClassifier().place_of("notes/readme.txt")).to(equal(None))

        with it("should leave a typescript file not named for its folder unmapped"):
            expect(ExampleClassifier().place_of("sales/client/helpers.ts")).to(equal(None))


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

            examples = ProjectFiles(root).discovered
            approach = ProjectApproach(
                project_root=root,
                project_title="Demo Project",
                repo_url="https://example.com/demo",
                examples=examples,
            )
            message = approach.generate(out_dir)
            page = Path(out_dir) / "cdd-approach.html"
            expect(page.is_file()).to(be_true)
            expect(message).to(contain("cdd-approach.html"))
            html = page.read_text(encoding="utf-8")
            expect("approach-page" in html).to(be_true)
            expect("story-map.drawio" in html or "catalog-drawio-frame" in html).to(be_true)

    with it("should link no repository for a project that is not a git checkout"):
        with tempfile.TemporaryDirectory() as project_dir:
            expect(ProjectApproach.for_project(project_dir).repo_url).to(equal(""))

    with it("should take its title from the project's folder when none is saved"):
        with tempfile.TemporaryDirectory() as parent:
            project = Path(parent) / "demo-shop"
            project.mkdir()
            expect(ProjectApproach.for_project(project).project_title).to(equal("Demo Shop"))

    with it("should put the examples a JSON mapping names over the ones it found"):
        with tempfile.TemporaryDirectory() as project_dir:
            chosen = ProjectApproach.for_project(project_dir).with_examples_json('{"examples": {"ddd": {"discovery": "map.md"}}}')
            expect(chosen.examples[("ddd", "discovery")]).to(equal((Path(project_dir) / "map.md").resolve()))
