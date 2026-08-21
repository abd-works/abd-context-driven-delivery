# @toolset-manifest python -m tools manifest catalog_generator.catalog_generator:CatalogGenerator
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Acceptance tests for catalog_generator - one `it` per sketch story's
single main-flow scenario. See catalog/cdd-catalog-sketch.md, epic
"Assemble Catalog Page Data".
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("context_tools", "primitives", "utilities", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_none, be_true, contain, equal, expect
from mamba import before, description, it

from catalog_generator.catalog_generator import (
    CONTEXT_TOOL_REGISTRY,
    UTILITY_REGISTRY,
    build_run_request,
    load_registry,
    resolve_lifecycle_actions,
    scrape_fidelities,
    skill_slash_name,
)
from context_tools.ddd.ddd import Ddd
from context_tools.stories.stories import Stories
from partition.partition import Partition


with description("Build Run Request From Live Toolset Manifest"):
    with description("given a context tool class and an action name"):
        with it("fills toolset, constructor context, action, and action arguments from Cls.manifest"):
            req = build_run_request(Partition, action="partition")
            expect(req["toolset"]).to(equal("partition.partition:Partition"))
            expect(req["action"]).to(equal("partition"))
            expect("context" in req["arguments"]).to(be_true)
            expect("mode" in req["arguments"]).to(be_true)

        with it("omits arguments when the action declares none"):
            req = build_run_request(Ddd, action="generate", fidelity="tactics")
            expect(req["action"]).to(equal("generate"))
            expect("arguments" in req).to(equal(False))


with description("Load Context Tool And Utility Registry"):
    with description("given the hardcoded registry lists"):
        with before.all:
            self.context_tools, self.utilities = load_registry()

        with it("resolves every context tool to a real class with nothing missing"):
            expect(len(self.context_tools)).to(equal(len(CONTEXT_TOOL_REGISTRY)))
            for entry in self.context_tools:
                expect(isinstance(entry.cls, type)).to(be_true)

        with it("resolves every utility to a real class with nothing missing"):
            expect(len(self.utilities)).to(equal(len(UTILITY_REGISTRY)))
            for entry in self.utilities:
                expect(isinstance(entry.cls, type)).to(be_true)

        with it("resolves CDD as the header-row entry, first in the list"):
            expect(self.context_tools[0].display_name).to(equal("Context-driven delivery"))
            expect(self.context_tools[0].class_name).to(equal("Cdd"))


with description("Scrape Fidelity Keys, Format Defaults, And Guidance Sections"):
    with description("given DDD's fidelities ClassVar, its format defaults, and ddd.md"):
        with before.all:
            self.guidances = scrape_fidelities(Ddd)

        with it("resolves each fidelity to its key and default format"):
            keys = [g.key for g in self.guidances]
            expect(keys).to(equal(["scaffold", "bounded_context", "building_blocks", "tactics"]))
            formats = {g.key: g.default_format for g in self.guidances}
            expect(formats["bounded_context"]).to(equal("markdown"))
            expect(formats["tactics"]).to(equal("python"))

        with it("resolves the matching ## {fidelity} guidance body from ddd.md"):
            tactics = next(g for g in self.guidances if g.key == "tactics")
            expect(tactics.guidance).not_to(equal("Guidance missing"))
            expect(len(tactics.guidance) > 0).to(be_true)

    with description("given a fidelity with no matching ## heading in {tool}.md"):
        with before.all:
            class _NoHeading:
                __module__ = "context_tools.bdd.bdd"
                fidelities = {"discovery": "modules"}  # BDD has no ## modules section
                _fidelity_format_defaults = {}

            self.stub_guidances = scrape_fidelities(_NoHeading)

        with it("resolves to a Guidance missing stub instead of failing"):
            expect(self.stub_guidances[0].guidance).to(equal("Guidance missing"))


with description("Resolve Lifecycle Action Source Dir And Calls Via AST Walk"):
    with description("given BaseContextTool's lifecycle-actions section"):
        with before.all:
            self.resolutions = resolve_lifecycle_actions()
            self.by_name = {r.name: r for r in self.resolutions}

        with it("walks host @actions in source order plus kit-owned lifecycle actions"):
            names = [r.name for r in self.resolutions]
            expect(names).to(equal([
                "partition", "grill", "sketch", "generate", "document",
                "iterate", "validate", "satisfy", "repair", "createRule",
            ]))
            expect("generate_fixes_from_validate" in names).to(equal(False))

        with it("resolves partition to its delegate kit dir under context_tools/actions/partition/"):
            expect(self.by_name["partition"].source_dir.name).to(equal("partition"))
            expect(self.by_name["partition"].source_dir.parent.name).to(equal("actions"))

        with it("resolves grill to context_tools/actions/grill_context/ and a call to generate"):
            expect(self.by_name["grill"].source_dir.name).to(equal("grill_context"))
            expect(self.by_name["grill"].calls).to(contain("generate"))

        with it("resolves sketch to context_tools/actions/sketch/ and a call to generate"):
            expect(self.by_name["sketch"].source_dir.name).to(equal("sketch"))
            expect(self.by_name["sketch"].calls).to(contain("generate"))

        with it("resolves iterate to context_tools/actions/iterate/ and a call to generate"):
            expect(self.by_name["iterate"].source_dir.name).to(equal("iterate"))
            expect(self.by_name["iterate"].calls).to(contain("generate"))

        with it("resolves repair to context_tools/actions/eval/ with no same-instance action call"):
            expect(self.by_name["repair"].source_dir.name).to(equal("eval"))
            expect(self.by_name["repair"].calls).to(equal([]))

        with it("falls back createRule to context_tools/base/"):
            expect(self.by_name["createRule"].source_dir.name).to(equal("base"))
            expect(self.by_name["createRule"].calls).to(equal([]))

        with it("falls back generate/document/validate/satisfy to context_tools/base/"):
            for name in ("generate", "document", "validate", "satisfy"):
                resolution = self.by_name[name]
                expect(resolution.source_dir.name).to(equal("base"))
                expect(str(resolution.source_dir.parent.name)).to(equal("context_tools"))


with description("Collect Skill Slash-Command Map From SKILL Frontmatter"):
    with description("given a .cursor/skills/*/SKILL.md file per context tool"):
        with it("resolves stories to its own snake_case skill name"):
            expect(skill_slash_name("stories")).to(equal("stories"))

        with it("resolves clean_engineering to the hyphenated clean-engineering skill name"):
            expect(skill_slash_name("clean_engineering")).to(equal("clean-engineering"))

        with it("resolves cdd to its own skill name"):
            expect(skill_slash_name("cdd")).to(equal("cdd"))

        with it("resolves an unknown module dir to nothing rather than guessing"):
            expect(skill_slash_name("not_a_real_skill")).to(be_none)
