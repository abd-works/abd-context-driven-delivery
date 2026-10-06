"""Specs for project-specific approach slide generation."""
import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect
from mamba import description, it

from catalog_generator.project_approach import (
    ApproachExampleSlot,
    classify_example_path,
    discover_project_examples,
    merge_example_sources,
    ProjectApproach,
)


with description("classify_example_path"):
    with it("should map story map drawio to stories discovery"):
        slot = classify_example_path("stories/story-map.drawio")
        expect(slot).to(equal(ApproachExampleSlot("stories", "discovery")))

    with it("should map story scenarios markdown to stories specification"):
        slot = classify_example_path("stories/qualify/story-scenarios.md")
        expect(slot).to(equal(ApproachExampleSlot("stories", "specification")))

    with it("should map story tests to stories implementation"):
        slot = classify_example_path("stories/qualify/qualify_cross_sell_offer_story.test.ts")
        expect(slot).to(equal(ApproachExampleSlot("stories", "implementation")))

    with it("should map bounded context drawio to ddd discovery"):
        slot = classify_example_path("domain/bounded-context.drawio")
        expect(slot).to(equal(ApproachExampleSlot("ddd", "discovery")))

    with it("should map building blocks markdown to ddd specification"):
        slot = classify_example_path("domain/single-client-view/building-blocks.md")
        expect(slot).to(equal(ApproachExampleSlot("ddd", "specification")))

    with it("should map client model typescript to ddd implementation"):
        slot = classify_example_path("domain/single-client-view/client/client-model.ts")
        expect(slot).to(equal(ApproachExampleSlot("ddd", "implementation")))

    with it("should map information architecture drawio to ux discovery"):
        slot = classify_example_path("ux/information-architecture.drawio")
        expect(slot).to(equal(ApproachExampleSlot("ux", "discovery")))

    with it("should map mockup html to ux specification"):
        slot = classify_example_path("ux/mockup/index.html")
        expect(slot).to(equal(ApproachExampleSlot("ux", "specification")))


with description("ProjectApproach.generate"):
    with it("should write cdd-approach.html with staged project examples"):
        with tempfile.TemporaryDirectory() as project_dir, tempfile.TemporaryDirectory() as out_dir:
            root = Path(project_dir)
            (root / "stories").mkdir()
            (root / "domain").mkdir()
            (root / "ux").mkdir()
            (root / "stories" / "story-map.drawio").write_text("<mxfile></mxfile>", encoding="utf-8")
            (root / "stories" / "story-scenarios.md").write_text("# Story\n", encoding="utf-8")
            (root / "stories" / "qualify_story.test.ts").write_text(
                "story('Qualify', () => {});\n", encoding="utf-8"
            )
            (root / "domain" / "bounded-context.drawio").write_text("<mxfile></mxfile>", encoding="utf-8")
            (root / "domain" / "building-blocks.md").write_text("# Blocks\n", encoding="utf-8")
            (root / "domain" / "client-model.ts").write_text("export class Client {}\n", encoding="utf-8")
            (root / "ux" / "information-architecture.drawio").write_text("<mxfile></mxfile>", encoding="utf-8")
            (root / "ux" / "mockup.html").write_text("<html></html>", encoding="utf-8")

            examples = discover_project_examples(root)
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
