"""BDD spec for BaseContextTool - domain host face, lifecycle prose, and fidelity system.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd

Peer-kit expansion lives with the kits:
- ``context_tools/actions/workspace/workspace_session_spec.py``
- ``context_tools/actions/partition/partition_spec.py``
- ``context_tools/actions/repair/repair_spec.py``

Meta generator face (scaffold templates / create_context_tool.md) lives in
``create_context_tool/create_context_tool_spec.py``.
"""

import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

from expects import be_false, be_true, equal, expect, raise_error
from mamba import before, context, description, it

from primitives.actions.action import _ActionRunRequest, _ActionRunner
import context_tools  # noqa: F401 - generator package on path
from primitives.instructions import Instruction
from primitives.instructions import _path_for_name
from tools.tool import Toolset, _ToolsetLoader

from context_tools.base.base_context_tool import BaseContextTool
from context_tools.bdd.bdd import Bdd
from context_tools.clean_engineering.clean_engineering import CleanEngineering
from context_tools.ddd.ddd import Ddd
from context_tools.stories.stories import Stories
from context_tools.ux.ux import Ux

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in [str(_REPO_ROOT), *[str(_REPO_ROOT / c) for c in ("context_tools", "primitives", "utilities")]]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
_BASE_DIR = _REPO_ROOT / "context_tools" / "base"
_CAR_CHRONICLE_DIR = (
    _REPO_ROOT / "context_tools" / "create_context_tool" / "examples" / "car_chronicle"
)
_CAR_CHRONICLE_TOOLSET = (
    "context_tools.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle"
)
_CHRONICLE_WITH_OUTPUT_TOOLSET = (
    "context_tools.create_context_tool.examples.car_chronicle.chronicle_with_output:ChronicleWithOutput"
)
_BASE_TOOLSET = "context_tools.base.base_context_tool:BaseContextTool"
_GENERATE_OUTPUT_PROSE = "Append each trip entry to the driving log before validating."
_META_CONTEXT_MARKER = "scaffold-vs-patch"


def _load_car_chronicle() -> Toolset:
    return _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)()


def _load_chronicle_with_output() -> Toolset:
    return _ToolsetLoader.instance().load(_CHRONICLE_WITH_OUTPUT_TOOLSET)()


def _expand_action(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
) -> dict[str, Any]:
    return _ActionRunner.instance().invoke_action(
        _ActionRunRequest(
            request={"toolset": toolset_path, "context": {}},
            toolset_path=toolset_path,
            action_name=action_name,
            context={},
            arguments={},
            instance=instance,
        )
    )


def _section(name: str) -> str:
    # _path_for_name emits "stem § Heading"; Instruction._split_section only
    # understands "stem # Heading" (or bare "# Heading" via domain_slug).
    text = _path_for_name(_BASE_DIR, name).replace(" \u00a7 ", " # ", 1)
    return Instruction(text, _BASE_DIR, domain_slug="base_context_tool").expand()


def _load_car_contexts() -> str:
    return Instruction(
        "# Contexts", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle"
    ).expand()


def _load_car_examples() -> str:
    return Instruction(
        "examples", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle"
    ).expand()


def _load_car_template() -> str:
    return Instruction(
        "car_chronicle-templates", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle"
    ).expand()


def _assert_text_inlined(instructions: str, source: str) -> None:
    expect(source in instructions).to(equal(True))


def _context_rule_slugs(concepts_text: str) -> list[str]:
    import re

    return re.findall(r"\*\*`([^`]+)`\*\*", concepts_text)


def _concept_bullet_lines(concepts_text: str) -> list[str]:
    import re

    pattern = re.compile(r"\*\*`([^`]+)`\*\*")
    return [
        line.strip()
        for line in concepts_text.splitlines()
        if pattern.search(line)
    ]


def _assert_contexts_inlined(instructions: str, concepts_text: str) -> None:
    _assert_text_inlined(instructions, concepts_text)
    slugs = _context_rule_slugs(concepts_text)
    bullets = _concept_bullet_lines(concepts_text)
    expect(len(slugs)).to(equal(len(bullets)))
    for slug in slugs:
        expect(slug in instructions).to(equal(True))
    for bullet in bullets:
        expect(bullet in instructions).to(equal(True))


with description("BaseContextTool lifecycle prose"):
    with it("should resolve generate / validate / satisfy from base markdown"):
        expect("# Generate" in _section("generate")).to(be_true)
        expect("# Validate" in _section("validate")).to(be_true)
        expect("# Satisfy" in _section("satisfy")).to(be_true)


with description("BaseContextTool composer"):
    with context("a CarChronicle domain host"):
        with before.all:
            self.chronicle = _load_car_chronicle()
            self.contexts = _load_car_contexts()
            self.examples = _load_car_examples()
            self.template = _load_car_template()

        with context("generate expands domain slots"):
            with before.each:
                self.response = _expand_action(
                    self.chronicle,
                    "generate",
                    toolset_path=_CAR_CHRONICLE_TOOLSET,
                )

            with it("should inline the full Contexts section from car_chronicle.md"):
                _assert_contexts_inlined(self.response["instructions"], self.contexts)

            with it("should inline the full examples.md file"):
                _assert_text_inlined(self.response["instructions"], self.examples)

            with it("should inline the full car_chronicle templates file"):
                _assert_text_inlined(self.response["instructions"], self.template)

            with it("should not inline meta contexts from create_context_tool.md"):
                expect(
                    _META_CONTEXT_MARKER in self.response["instructions"]
                ).to(equal(False))

            with it("should not inline prose from a subclass generate_output override"):
                expect(
                    _GENERATE_OUTPUT_PROSE in self.response["instructions"]
                ).to(equal(False))

            with it("should inline generate prose"):
                expect(_section("generate") in self.response["instructions"]).to(
                    be_true
                )

        with context("validate expands domain contexts as rubric"):
            with before.each:
                self.response = _expand_action(
                    self.chronicle,
                    "validate",
                    toolset_path=_CAR_CHRONICLE_TOOLSET,
                )

            with it("should inline the full Contexts section as rubric"):
                _assert_contexts_inlined(self.response["instructions"], self.contexts)

            with it("should name open session tools then scan"):
                expect(self.response["tools"]).to(
                    equal(
                        [
                            "ensure_session",
                            "read_context_index",
                            "record_context_root",
                            "scan",
                        ]
                    )
                )
            with it("should inline validate prose"):
                expect(_section("validate") in self.response["instructions"]).to(
                    be_true
                )

        with context("satisfy"):
            with before.each:
                self.response = _expand_action(
                    self.chronicle,
                    "satisfy",
                    toolset_path=_CAR_CHRONICLE_TOOLSET,
                )

            with it("should set action to satisfy"):
                expect(self.response["action"]).to(equal("satisfy"))

            with it("should name validate then generate_fixes_from_validate"):
                expect(self.response["tools"]).to(
                    equal(["validate", "generate_fixes_from_validate"])
                )

            with it("should inline satisfy prose"):
                expect(_section("satisfy") in self.response["instructions"]).to(
                    be_true
                )

            with it("should not inline the domain template in tool mode"):
                expect(self.template in self.response["instructions"]).to(be_false)

    with context("BaseContextTool generate"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_BASE_TOOLSET)
            self.host = cls()
            self.response = _expand_action(
                self.host, "generate", toolset_path=_BASE_TOOLSET
            )

        with it("should inline generate prose on the composer"):
            expect(_section("generate") in self.response["instructions"]).to(be_true)

    with context("a subclass that overrides generate_output"):
        with before.all:
            self.chronicle = _load_chronicle_with_output()
            self.response = _expand_action(
                self.chronicle,
                "generate",
                toolset_path=_CHRONICLE_WITH_OUTPUT_TOOLSET,
            )

        with it("should inline prose from the subclass generate_output action"):
            _assert_text_inlined(self.response["instructions"], _GENERATE_OUTPUT_PROSE)


with description("BaseContextTool linear kit delegation"):
    with context("sketch expands providers in-method (no @ chain)"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_BASE_TOOLSET)
            self.host = cls()
            self.entry = self.host.actions["sketch"].signature_entry
            self.response = _expand_action(
                self.host, "sketch", toolset_path=_BASE_TOOLSET
            )

        with it("should have no decorator chain on sketch"):
            expect("chain" in self.entry).to(equal(False))

        with it("should inline workspace open prose"):
            expect(
                "Open the workspace session" in self.response["instructions"]
                or "Workspace open" in self.response["instructions"]
                or "# Session Guidance" in self.response["instructions"]
            ).to(be_true)

        with it("should inline sketch_session cadence (save_sketch)"):
            expect("save_sketch" in self.response["tools"]).to(be_true)

        with it("should inline grill via sketcher (explore_context_files)"):
            expect("explore_context_files" in self.response["tools"]).to(be_true)

    with context("generate expands providers in-method (no @ chain)"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_BASE_TOOLSET)
            self.host = cls()
            self.entry = self.host.actions["generate"].signature_entry

        with it("should have no decorator chain on generate"):
            expect("chain" in self.entry).to(equal(False))

    with context("grill expands GrillContext in-method (no @ chain)"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_BASE_TOOLSET)
            self.host = cls()
            self.entry = self.host.actions["grill"].signature_entry
            self.response = _expand_action(
                self.host, "grill", toolset_path=_BASE_TOOLSET
            )

        with it("should have no decorator chain on grill"):
            expect("chain" in self.entry).to(equal(False))

        with it("should name explore_context_files from GrillContext"):
            expect("explore_context_files" in self.response["tools"]).to(be_true)

    with context("iterate expands Iterator in-method (no @ chain)"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_BASE_TOOLSET)
            self.host = cls()
            self.entry = self.host.actions["iterate"].signature_entry
            self.response = _expand_action(
                self.host, "iterate", toolset_path=_BASE_TOOLSET
            )

        with it("should have no decorator chain on iterate"):
            expect("chain" in self.entry).to(equal(False))

    with context("document expands providers in-method (no @ chain)"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_BASE_TOOLSET)
            self.host = cls()
            self.entry = self.host.actions["document"].signature_entry
            self.response = _expand_action(
                self.host, "document", toolset_path=_BASE_TOOLSET
            )

        with it("should have no decorator chain on document"):
            expect("chain" in self.entry).to(equal(False))

        with it("should inline document prose"):
            expect(_section("document") in self.response["instructions"]).to(be_true)


with description("BaseContextTool public host face"):
    with before.all:
        cls = _ToolsetLoader.instance().load(_BASE_TOOLSET)
        self.host = cls()

    with it("should resolve module_dir to the base package folder"):
        expect(self.host.module_dir).to(equal(_BASE_DIR.resolve()))

    with it("should default default_workspace_folder to the workspace root"):
        expect(type(self.host).default_workspace_folder).to(equal("."))

    with it("should default context_index_key to empty"):
        expect(type(self.host).context_index_key).to(equal(""))

    with it("should hold a Session as workspace"):
        from workspace.workspace_session import Session

        expect(isinstance(self.host.workspace, Session)).to(be_true)

    with it("should hold a Scan as scanner"):
        from scanners.scan import Scan

        expect(isinstance(self.host.scanner, Scan)).to(be_true)

    with it("should hold a Sketcher as sketcher"):
        from sketch.sketch import Sketcher

        expect(isinstance(self.host.sketcher, Sketcher)).to(be_true)

    with it("should hold a GrillContext as grill_context"):
        from grill_context.grill_context import GrillContext

        expect(isinstance(self.host.grill_context, GrillContext)).to(be_true)

    with it("should hold an Iterator as iterator"):
        from iterate.iterate import Iterator

        expect(isinstance(self.host.iterator, Iterator)).to(be_true)

    with it("should hold RecordDecisions as decisions"):
        from record_decisions.record_decisions import RecordDecisions

        expect(isinstance(self.host.decisions, RecordDecisions)).to(be_true)

    with it("should expose active as the workspace Session"):
        expect(self.host.active).to(equal(self.host.workspace))

    with it("should delegate session_guidance to the workspace kit"):
        guidance = self.host.session_guidance()
        expect(isinstance(guidance, Instruction)).to(be_true)
        expect("Session Guidance" in guidance.expand() or "session" in guidance.expand().lower()).to(
            be_true
        )

    with it("should expose create_session and close_session as host tools"):
        expect("create_session" in self.host.tools).to(be_true)
        expect("close_session" in self.host.tools).to(be_true)

    with it("should prepend a BDD-capable generate header"):
        header = self.host.add_generate_header_to_generated()
        expect("@toolset-manifest" in header).to(be_true)
        expect("invoke-edit: action satisfy" in header).to(be_true)


# ---------------------------------------------------------------------------
# Repair-to-eval loop: log_mistake/log_correction auto-injection, improve,
# regression, archive
# ---------------------------------------------------------------------------

with description("BaseContextTool.log_mistake tool/fidelity auto-injection"):
    with before.each:
        import shutil
        import tempfile

        self.tmp_dir = Path(tempfile.mkdtemp())
        self.host = Stories(fidelity="story_map", path=str(self.tmp_dir), session="test")
        self.log_path = self.tmp_dir / ".context" / "sessions" / "test" / "mistakes.log"
        self._shutil = shutil

    with it("should tag the entry with the host class name and current fidelity"):
        self.host.log_mistake(
            artifact="some/file.md",
            rule="test-rule",
            wrong="bad thing happened",
            original="old",
        )
        content = self.log_path.read_text(encoding="utf-8")
        expect("tool: Stories" in content).to(be_true)
        expect("fidelity: story_map" in content).to(be_true)
        self._shutil.rmtree(str(self.tmp_dir), ignore_errors=True)

    with it("should re-tag with the fidelity in effect at call time, not construction time"):
        self.host._set_fidelity("scenarios")
        self.host.log_mistake(
            artifact="some/file.md",
            rule="test-rule",
            wrong="bad thing happened",
            original="old",
        )
        content = self.log_path.read_text(encoding="utf-8")
        expect("fidelity: scenarios" in content).to(be_true)
        self._shutil.rmtree(str(self.tmp_dir), ignore_errors=True)

    with it("should complete the entry via log_correction, forwarded to the repairer"):
        entry_id = self.host.log_mistake(
            artifact="some/file.md",
            rule="test-rule",
            wrong="bad thing happened",
            original="old",
        )
        self.host.log_correction(entry_id=entry_id, improved="new")
        content = self.log_path.read_text(encoding="utf-8")
        expect("status: fixed" in content).to(be_true)
        self._shutil.rmtree(str(self.tmp_dir), ignore_errors=True)


with description("BaseContextTool.improve action"):
    with before.all:
        cls = _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)
        self.host = cls()
        self.response = _ActionRunner.instance().invoke_action(
            _ActionRunRequest(
                request={"toolset": _CAR_CHRONICLE_TOOLSET, "context": {}},
                toolset_path=_CAR_CHRONICLE_TOOLSET,
                action_name="improve",
                context={},
                arguments={},
                instance=self.host,
            )
        )

    with it("should set action to improve"):
        expect(self.response["action"]).to(equal("improve"))

    with it("should inline the improve.md roadmap via the repairer"):
        instructions = self.response["instructions"]
        expect("Log the mistake, the moment it's spotted" in instructions).to(be_true)
        expect("Offer to archive, once satisfied" in instructions).to(be_true)


with description("BaseContextTool regression and archive forwarding"):
    with before.each:
        import shutil
        import tempfile

        self.tmp_dir = Path(tempfile.mkdtemp())
        self.host = Stories(fidelity="story_map", path=str(self.tmp_dir), session="test")
        self._shutil = shutil

    with it("should forward verify_regression to the repairer"):
        examples_root = self.tmp_dir / "empty-examples"
        summary = self.host.verify_regression(str(examples_root))
        expect(f"No regression examples found under {examples_root}." in summary).to(be_true)
        self._shutil.rmtree(str(self.tmp_dir), ignore_errors=True)

    with it("should forward archive_mistakes to the repairer"):
        entry_id = self.host.log_mistake(
            artifact="a.md", rule="r1", wrong="w1", original="o1"
        )
        self.host.log_correction(entry_id=entry_id, improved="i1")
        repo_root = self.tmp_dir / "repo"
        destination = self.host.archive_mistakes(str(repo_root))
        expect(Path(destination).is_file()).to(be_true)
        self._shutil.rmtree(str(self.tmp_dir), ignore_errors=True)

    with it("should discover repair, verify_regression, and archive_mistakes as non-blocking sub-agents on the host"):
        from sub_agent.sub_agent import discover_sub_agent_tools

        discovered = discover_sub_agent_tools(self.host)
        for name in ("repair", "verify_regression", "archive_mistakes"):
            expect(name in discovered).to(be_true)
            expect(discovered[name].signature_entry["kind"]).to(equal("sub_agent"))
        self._shutil.rmtree(str(self.tmp_dir), ignore_errors=True)


# ---------------------------------------------------------------------------
# Stage constants
# ---------------------------------------------------------------------------

with description("BaseContextTool stage constants"):
    with it("should define SHAPING as 'shaping'"):
        expect(BaseContextTool.SHAPING).to(equal("shaping"))

    with it("should define DISCOVERY as 'discovery'"):
        expect(BaseContextTool.DISCOVERY).to(equal("discovery"))

    with it("should define SPEC as 'spec'"):
        expect(BaseContextTool.SPEC).to(equal("spec"))

    with it("should define ENGINEER as 'engineer'"):
        expect(BaseContextTool.ENGINEER).to(equal("engineer"))


# ---------------------------------------------------------------------------
# resolve_fidelity — stage command names → concrete fidelities
# ---------------------------------------------------------------------------

with description("BaseContextTool.resolve_fidelity"):
    with context("on Stories"):
        with it("should map discovery to story_map"):
            expect(Stories.resolve_fidelity("discovery")).to(equal("story_map"))

        with it("should map specification to scenarios"):
            expect(Stories.resolve_fidelity("specification")).to(equal("scenarios"))

        with it("should map engineering to acceptance_tests"):
            expect(Stories.resolve_fidelity("engineering")).to(equal("acceptance_tests"))

        with it("should leave a concrete fidelity unchanged"):
            expect(Stories.resolve_fidelity("story_map")).to(equal("story_map"))

    with context("on CleanEngineering"):
        with it("should map discovery to modules"):
            expect(CleanEngineering.resolve_fidelity("discovery")).to(equal("modules"))

        with it("should map specification to model"):
            expect(CleanEngineering.resolve_fidelity("specification")).to(equal("model"))

        with it("should map engineering to code"):
            expect(CleanEngineering.resolve_fidelity("engineering")).to(equal("code"))

    with context("constructors accepting stage names"):
        with it("should construct Stories with fidelity discovery"):
            expect(Stories(fidelity="discovery").fidelity).to(equal("story_map"))

        with it("should construct CleanEngineering with fidelity specification"):
            expect(CleanEngineering(fidelity="specification").fidelity).to(equal("model"))

        with it("should construct Ux with fidelity engineering"):
            expect(Ux(fidelity="engineering").fidelity).to(equal("front_end_code"))


# ---------------------------------------------------------------------------
# fidelities class variable — per tool
# ---------------------------------------------------------------------------

with description("BaseContextTool.fidelities class variable"):
    with context("on Stories"):
        with it("should map DISCOVERY to story_map"):
            expect(Stories.fidelities[BaseContextTool.DISCOVERY]).to(equal("story_map"))

        with it("should map SPEC to scenarios"):
            expect(Stories.fidelities[BaseContextTool.SPEC]).to(equal("scenarios"))

        with it("should map ENGINEER to acceptance_tests"):
            expect(Stories.fidelities[BaseContextTool.ENGINEER]).to(equal("acceptance_tests"))

    with context("on Bdd"):
        with it("should map DISCOVERY to modules"):
            expect(Bdd.fidelities[BaseContextTool.DISCOVERY]).to(equal("modules"))

        with it("should map SPEC to behavior"):
            expect(Bdd.fidelities[BaseContextTool.SPEC]).to(equal("behavior"))

        with it("should map ENGINEER to development"):
            expect(Bdd.fidelities[BaseContextTool.ENGINEER]).to(equal("development"))

    with context("on Ddd"):
        with it("should map DISCOVERY to bounded_context"):
            expect(Ddd.fidelities[BaseContextTool.DISCOVERY]).to(equal("bounded_context"))

        with it("should map SPEC to building_blocks"):
            expect(Ddd.fidelities[BaseContextTool.SPEC]).to(equal("building_blocks"))

        with it("should map ENGINEER to code"):
            expect(Ddd.fidelities[BaseContextTool.ENGINEER]).to(equal("tactics"))

    with context("on Ux"):
        with it("should map DISCOVERY to ia"):
            expect(Ux.fidelities[BaseContextTool.DISCOVERY]).to(equal("ia"))

        with it("should map SPEC to mockup"):
            expect(Ux.fidelities[BaseContextTool.SPEC]).to(equal("mockup"))

        with it("should map ENGINEER to code"):
            expect(Ux.fidelities[BaseContextTool.ENGINEER]).to(equal("front_end_code"))

    with context("on CleanEngineering"):
        with it("should map DISCOVERY to modules"):
            expect(CleanEngineering.fidelities[BaseContextTool.DISCOVERY]).to(equal("modules"))

        with it("should map SPEC to model"):
            expect(CleanEngineering.fidelities[BaseContextTool.SPEC]).to(equal("model"))

        with it("should map ENGINEER to code"):
            expect(CleanEngineering.fidelities[BaseContextTool.ENGINEER]).to(equal("code"))


# ---------------------------------------------------------------------------
# _set_fidelity helper
# ---------------------------------------------------------------------------

with description("BaseContextTool._set_fidelity"):
    with context("on a Stories instance starting at story_map"):
        with before.each:
            self.stories = Stories(fidelity="story_map")

        with it("should update fidelity to scenarios"):
            self.stories._set_fidelity("scenarios")
            expect(self.stories.fidelity).to(equal("scenarios"))

        with it("should update format to markdown when set to scenarios"):
            self.stories._set_fidelity("scenarios")
            expect(self.stories.format).to(equal("markdown"))

        with it("should update fidelity to acceptance_tests"):
            self.stories._set_fidelity("acceptance_tests")
            expect(self.stories.fidelity).to(equal("acceptance_tests"))

    with context("on a CleanEngineering instance starting at modules"):
        with before.each:
            self.ce = CleanEngineering(fidelity="modules")

        with it("should update fidelity to model"):
            self.ce._set_fidelity("model")
            expect(self.ce.fidelity).to(equal("model"))

        with it("should update format to python when set to model"):
            self.ce._set_fidelity("model")
            expect(self.ce.format).to(equal("python"))


# ---------------------------------------------------------------------------
# Generated fidelity lifecycle methods
# ---------------------------------------------------------------------------

with description("BaseContextTool generated fidelity methods"):
    with context("on Stories class"):
        with it("should have generate_story_map method"):
            expect(callable(getattr(Stories, "generate_story_map", None))).to(be_true)

        with it("should have generate_scenarios method"):
            expect(callable(getattr(Stories, "generate_scenarios", None))).to(be_true)

        with it("should have generate_acceptance_tests method"):
            expect(callable(getattr(Stories, "generate_acceptance_tests", None))).to(be_true)

        with it("should have validate_story_map method"):
            expect(callable(getattr(Stories, "validate_story_map", None))).to(be_true)

        with it("should have satisfy_story_map method"):
            expect(callable(getattr(Stories, "satisfy_story_map", None))).to(be_true)

    with context("on Bdd class"):
        with it("should have generate_modules method"):
            expect(callable(getattr(Bdd, "generate_modules", None))).to(be_true)

        with it("should have generate_behavior method"):
            expect(callable(getattr(Bdd, "generate_behavior", None))).to(be_true)

        with it("should have generate_development method"):
            expect(callable(getattr(Bdd, "generate_development", None))).to(be_true)

    with context("on CleanEngineering class"):
        with it("should have generate_modules method"):
            expect(callable(getattr(CleanEngineering, "generate_modules", None))).to(be_true)

        with it("should have generate_model method"):
            expect(callable(getattr(CleanEngineering, "generate_model", None))).to(be_true)

        with it("should have generate_code method"):
            expect(callable(getattr(CleanEngineering, "generate_code", None))).to(be_true)

    with context("calling generate_story_map on a Stories instance starting at scenarios"):
        with before.each:
            self.stories = Stories(fidelity="scenarios")

        with it("should set fidelity to story_map before calling generate"):
            captured = []
            with patch.object(type(self.stories), "generate", lambda s: captured.append(s.fidelity)):
                self.stories.generate_story_map()
            expect(captured[0]).to(equal("story_map"))

        with it("should set format to markdown before calling generate"):
            captured = []
            with patch.object(type(self.stories), "generate", lambda s: captured.append(s.format)):
                self.stories.generate_story_map()
            expect(captured[0]).to(equal("markdown"))

    with context("calling validate_scenarios on a Stories instance starting at story_map"):
        with before.each:
            self.stories = Stories(fidelity="story_map")

        with it("should set fidelity to scenarios before calling validate"):
            captured = []
            with patch.object(type(self.stories), "validate", lambda s: captured.append(s.fidelity)):
                self.stories.validate_scenarios()
            expect(captured[0]).to(equal("scenarios"))
