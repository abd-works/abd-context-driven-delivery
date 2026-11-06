"""Acceptance tests for catalog_generator - one `it` per sketch story's
single main-flow scenario. See catalog/cdd-catalog-sketch.md, epic
"Assemble Catalog Page Data".
"""
import ast
import shutil
import sys
import types
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_false, be_none, be_true, contain, equal, expect
from mamba import after, before, description, it

from harness.catalog_generator.catalog_generator import (
    UTILITY_REGISTRY,
    LifecycleAction,
    RegistryEntry,
    SkillSlashName,
    build_run_request,
    catalog_practices,
    catalog_utilities,
    keep_in_catalog,
    noCatalog,
    omitted_from_catalog,
    resolve_lifecycle_actions,
)
from harness.agent_tools import agent_instructions, agent_toolset
from harness.installation.files import skill
from harness.installation.installer import Installer
from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.stories.stories import Stories
from generate.generate import Generate
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
            req = build_run_request(Ddd, action="guidance", fidelity="tactics")
            expect(req["action"]).to(equal("guidance"))
            expect("arguments" in req).to(equal(False))

        with it("fills Generate kit generate with a guidance argument"):
            req = build_run_request(Generate, action="generate")
            expect(req["toolset"]).to(equal("generate.generate:Generate"))
            expect(req["action"]).to(equal("generate"))
            expect("guidance" in req["arguments"]).to(be_true)

        with it("routes Stories generate through the Generate kit so action generate is live"):
            req = build_run_request(Stories, action="generate", fidelity="story_map")
            expect(req["toolset"]).to(equal("generate.generate:Generate"))
            expect(req["action"]).to(equal("generate"))
            host = req["arguments"]["guidance"][0]
            expect(host["toolset"]).to(equal("cdd_guidance.practices.stories.stories:Stories"))
            expect(host["context"]["fidelity"]).to(equal("story_map"))


with description("noCatalog"):
    with description("a class or operation marked not ready for the catalog"):
        with it("drops the class from registry resolution"):
            @noCatalog
            class LaterUtility:
                pass

            class ShownUtility:
                pass

            hidden = RegistryEntry("later", "later", "LaterUtility", LaterUtility)
            shown = RegistryEntry("shown", "shown", "ShownUtility", ShownUtility)
            expect(keep_in_catalog(hidden)).to(equal(False))
            expect(keep_in_catalog(shown)).to(be_true)

        with it("drops the operation from the lifecycle actions"):
            @agent_toolset
            class Kit:
                @agent_instructions
                @noCatalog
                def sketch(self):
                    """Sketch the plan."""

                @agent_instructions
                def generate(self):
                    """Generate the artifact."""

            module = types.ModuleType("catalog_kit_probe")
            module.Kit = Kit
            sys.modules[module.__name__] = module
            shown = [
                action.name
                for action in (LifecycleAction(name, module.__name__, "Kit") for name in ("sketch", "generate"))
                if action.tool is not None
            ]
            expect(shown).to(equal(["generate"]))

        with it("leaves the skill mark in place so install still deploys it"):
            @noCatalog
            @skill
            def sketch(self):
                """Sketch the plan."""
                return None

            expect(omitted_from_catalog(sketch)).to(be_true)
            expect(getattr(sketch, "_skill", False)).to(be_true)
            expect("noCatalog" in Installer._ANNOTATIONS).to(equal(False))
            expect("Skill" in Installer._ANNOTATIONS).to(be_true)
            source = ast.parse(
                "@agent_toolset\n"
                "class Kit:\n"
                "    @Skill\n"
                "    @noCatalog\n"
                "    def sketch(self):\n"
                "        pass\n"
            )
            installer = object.__new__(Installer)
            expect(installer._class_is_installable(source.body[0])).to(be_true)


with description("Load Context Tool And Utility Registry"):
    with description("given the hardcoded registry lists"):
        with before.all:
            self.practices = catalog_practices()
            self.utilities = catalog_utilities()

        with it("shows each practice in the practice catalogue that has a fidelity on the board"):
            for practice in self.practices:
                expect(practice.on_board).to(be_true)
            expect([type(practice.practice).__name__ for practice in self.practices]).to(
                equal(["Stories", "CleanEngineering", "Ux", "Bdd", "Ddd"])
            )

        with it("leaves out patterns and builders"):
            names = {type(practice.practice).__name__ for practice in self.practices}
            expect("AgentBdd" in names).to(be_false)
            expect("LernDomainDriven" in names).to(be_false)
            expect("CreatePracticeGuidance" in names).to(be_false)

        with it("omits utilities marked noCatalog"):
            expect(len(UTILITY_REGISTRY) > 0).to(be_true)
            expect([entry.class_name for entry in self.utilities]).to(equal(["Repo"]))

        with it("names and orders each context tool from its own catalog card"):
            expect([practice.display_name for practice in self.practices]).to(
                equal([
                    "Stories",
                    "Clean Engineering",
                    "User Experience",
                    "Behavior-Driven Development",
                    "Domain-Driven Design",
                ])
            )


with description("Read Fidelity Names, Default Formats, And Sections From The Live Practice"):
    with description("given DDD's fidelities and ddd.md"):
        with before.all:
            self.fidelities = list(Ddd().fidelities.entries.values())

        with it("names each fidelity with its default format"):
            expect([fidelity.name for fidelity in self.fidelities]).to(
                equal(["bounded_context", "model", "tactics"])
            )
            formats = {fidelity.name: fidelity.default_format for fidelity in self.fidelities}
            expect(formats["bounded_context"]).to(equal("markdown"))
            expect(formats["tactics"]).to(equal("python"))

        with it("gives the fidelity's whole ### block from ddd.md as its section"):
            tactics = next(fidelity for fidelity in self.fidelities if fidelity.name == "tactics")
            expect(tactics.section).to(contain("#### Overview"))
            expect(tactics.section).to(contain("#### Rules"))


with description("Resolve Lifecycle Actions From Their Action Kits"):
    with description("given lifecycle action kits"):
        with before.all:
            self.actions = resolve_lifecycle_actions()
            self.by_name = {action.name: action for action in self.actions}

        with it("lists each kit's lifecycle action in catalog order"):
            names = [action.name for action in self.actions]
            expect(names).to(equal([
                "partition", "grill", "sketch", "generate", "document",
                "iterate", "validate", "satisfy", "repair", "createRule",
            ]))
            expect("generate_fixes_from_validate" in names).to(equal(False))

        with it("resolves partition to its delegate kit dir under actions/partition/"):
            expect(self.by_name["partition"].source_dir.name).to(equal("partition"))
            expect(self.by_name["partition"].source_dir.parent.name).to(equal("actions"))

        with it("resolves grill to actions/grill_context/"):
            expect(self.by_name["grill"].source_dir.name).to(equal("grill_context"))

        with it("resolves sketch to actions/sketch/"):
            expect(self.by_name["sketch"].source_dir.name).to(equal("sketch"))

        with it("resolves iterate to actions/iterate/"):
            expect(self.by_name["iterate"].source_dir.name).to(equal("iterate"))

        with it("resolves repair to actions/improvement/"):
            expect(self.by_name["repair"].source_dir.name).to(equal("improvement"))

        with it("resolves createRule to actions/validate/"):
            expect(self.by_name["createRule"].source_dir.name).to(equal("validate"))

        with it("gives each action the kit's live tool of the same name"):
            for action in self.actions:
                expect(action.tool.name).to(equal(action.name))

        with it("resolves generate/document/validate/satisfy to their action kits"):
            for name in ("generate", "document", "validate", "satisfy"):
                resolution = self.by_name[name]
                expect(resolution.source_dir.name).to(equal(name))
                expect(str(resolution.source_dir.parent.name)).to(equal("actions"))


with description("Collect Skill Slash-Command Map From SKILL Frontmatter"):
    with description("given a .claude/skills/{category}-{skill}/SKILL.md file per practice"):
        with before.each:
            self.skills_root = Path(tempfile.mkdtemp()) / ".claude" / "skills"
            for folder in (
                "practices-stories",
                "practices-stories-stories-story-map",
                "practices-clean-engineering",
                "practices-ddd",
                "practices-agent-bdd",
            ):
                skill_md = self.skills_root / folder / "SKILL.md"
                skill_md.parent.mkdir(parents=True)
                skill_md.write_text(f"---\nname: {folder}\n---\n", encoding="utf-8")
            self.slash = SkillSlashName([self.skills_root])

        with after.each:
            shutil.rmtree(self.skills_root.parents[1], ignore_errors=True)

        with it("resolves stories to its practices-stories skill name"):
            expect(self.slash.resolve("stories")).to(equal("practices-stories"))

        with it("resolves clean_engineering to the hyphenated practices-clean-engineering skill name"):
            expect(self.slash.resolve("clean_engineering")).to(equal("practices-clean-engineering"))

        with it("resolves ddd to its practices-ddd skill name"):
            expect(self.slash.resolve("ddd")).to(equal("practices-ddd"))

        with it("resolves an unknown module dir to nothing rather than guessing"):
            expect(self.slash.resolve("not_a_real_skill")).to(be_none)
