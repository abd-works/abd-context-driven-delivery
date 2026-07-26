"""BDD spec for BaseContextTool — domain host face + lifecycle prose.

Peer-kit expansion lives with the kits:
- ``utilities/sessions/workspace_session_spec.py``
- ``utilities/partition_pipeline/partition_pipeline_spec.py``
- ``utilities/repair/repair_spec.py``

Meta generator face (scaffold templates / create_context_tool.md) lives in
``create_context_tool/create_context_tool_spec.py``.
"""

from pathlib import Path
from typing import Any

from expects import be_true, equal, expect
from mamba import before, context, description, it

from primitives.actions.action import _ActionRunRequest, _ActionRunner
import context_tools  # noqa: F401 — generator package on path
from primitives.instructions import Instruction
from primitives.instructions import _path_for_name
from tools.tool import Toolset, _ToolsetLoader

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BASE_DIR = _REPO_ROOT / "context_tools" / "base"
_CAR_CHRONICLE_DIR = (
    _BASE_DIR / "create_context_tool" / "examples" / "car_chronicle"
)
_CAR_CHRONICLE_TOOLSET = (
    "context_tools.base.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle"
)
_CHRONICLE_WITH_OUTPUT_TOOLSET = (
    "context_tools.base.create_context_tool.examples.car_chronicle.chronicle_with_output:ChronicleWithOutput"
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
    return _ActionRunner.instance().run(
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
    return Instruction(_path_for_name(_BASE_DIR, name), _BASE_DIR).expand()


def _load_car_contexts() -> str:
    return Instruction(
        "\u00a7 Contexts", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle"
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

            with it("should name scan on tools"):
                expect(self.response["tools"]).to(equal(["scan"]))

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

            with it("should name no tools on satisfy"):
                expect(self.response["tools"]).to(equal([]))

            with it("should inline satisfy prose"):
                expect(_section("satisfy") in self.response["instructions"]).to(
                    be_true
                )

            with it("should inline the domain template"):
                expect(self.template in self.response["instructions"]).to(be_true)

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
