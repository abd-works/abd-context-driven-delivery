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

from harness.catalog_generator.catalog_generator import CatalogPractice, LifecycleAction, SkillSlashName, Utility
from harness.installation.destination import NoCatalog, noCatalog
from harness.guidance.action_catalogue import Action
from harness.agent_tools import agent_instructions, agent_toolset
from harness.installation.files import Skill, skill
from harness.installation.repository_toolsets import RepositoryToolsets
from cdd_guidance.practices.ddd.ddd import Ddd


with description("noCatalog"):
    with description("a class or operation marked not ready for the catalog"):
        with it("drops the toolset from the utilities"):
            names = [utility.toolset_class.__name__ for utility in Utility.load_all()]
            expect("Echo" in names).to(be_false)

        with it("drops the operation from the lifecycle actions"):
            @agent_toolset
            class Toolset:
                @agent_instructions
                @noCatalog
                def sketch(self):
                    """Sketch the plan."""

                @agent_instructions
                def generate(self):
                    """Generate the artifact."""

            module = types.ModuleType("catalog_toolset_probe")
            module.Toolset = Toolset
            sys.modules[module.__name__] = module
            shown = [
                action.name
                for action in (LifecycleAction(Action(name, Toolset)) for name in ("sketch", "generate"))
                if action.tool is not None
            ]
            expect(shown).to(equal(["generate"]))

        with it("leaves the skill mark in place so install still deploys it"):
            @noCatalog
            @skill
            def sketch(self):
                """Sketch the plan."""
                return None

            expect(NoCatalog.marks(sketch)).to(be_true)
            expect(Skill.marks(sketch)).to(be_true)
            source = ast.parse(
                "@agent_toolset\n"
                "class Toolset:\n"
                "    @Skill\n"
                "    @noCatalog\n"
                "    def sketch(self):\n"
                "        pass\n"
            )
            toolsets = RepositoryToolsets(Path.cwd())
            expect(toolsets._class_is_installable(source.body[0])).to(be_true)


with description("Load Context Tool And Utility Registry"):
    with description("given the practice catalogue and the toolsets the installer finds"):
        with before.all:
            self.practices = CatalogPractice.load_all()
            self.utilities = Utility.load_all()

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

        with it("shows the toolsets in space and tools as utilities"):
            names = [utility.toolset_class.__name__ for utility in self.utilities]
            expect(names).to(contain("Repo", "Session", "Board", "Chat", "FileManager"))

        with it("names each utility in kebab case for its page"):
            expect([utility.href for utility in self.utilities]).to(contain("tools/file-manager.html"))

        with it("leaves the harness's own toolsets out"):
            names = {utility.toolset_class.__name__ for utility in self.utilities}
            expect(names & {"Graph", "Catalog", "Guidance", "GuidanceAction"}).to(equal(set()))

        with it("omits utilities marked noCatalog"):
            names = {utility.toolset_class.__name__ for utility in self.utilities}
            expect(names & {"Installer", "Echo"}).to(equal(set()))

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


with description("Resolve Lifecycle Actions From The Toolsets That Define Them"):
    with description("given the action folders' toolsets"):
        with before.all:
            self.actions = LifecycleAction.load_all()
            self.by_name = {action.name: action for action in self.actions}

        with it("lists each skill of each action folder's toolset, folder by folder"):
            listed = ["document", "generate", "grill", "repair", "verify_fix", "iterate", "partition", "render", "satisfy", "sketch", "validate"]
            expect([action.name for action in self.actions if action.name in listed]).to(equal(listed))

        with it("leaves out a toolset's tools that are not skills"):
            expect("generate_fixes_from_validate" in [action.name for action in self.actions]).to(equal(False))

        with it("leaves out a toolset marked noCatalog"):
            expect("diagnose" in [action.name for action in self.actions]).to(equal(False))

        with it("resolves partition to its folder under actions/partition/"):
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

        with it("gives each action its toolset's live tool of the same name"):
            for action in self.actions:
                expect(action.tool.name).to(equal(action.name))

        with it("resolves generate/document/validate/satisfy to their own folders"):
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
