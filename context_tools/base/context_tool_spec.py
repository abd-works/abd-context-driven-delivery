"""BDD spec for ContextTool composer face — domain slots, templates, meta contexts.

Peer-kit expansion lives with the kits:
- ``utilities/sessions/workspace_session_spec.py``
- ``utilities/partition_pipeline/partition_pipeline_spec.py``
- ``utilities/repair/repair_spec.py``
- ``context_tools/base/artifact_lifecycle/artifact_lifecycle_spec.py``
"""

from pathlib import Path
from typing import Any

from expects import equal, expect
from mamba import before, context, description, it

from primitives.actions.action import _ActionRunRequest, _ActionRunner
import context_tools  # noqa: F401 — generator package on path
from primitives.instructions import Instruction
from tools.tool import Toolset, _ToolsetLoader

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EXAMPLES_DIR = _REPO_ROOT / "context_tools" / "base" / "examples"
_CAR_CHRONICLE_DIR = _EXAMPLES_DIR / "car_chronicle"
_GENERATOR_DIR = _REPO_ROOT / "context_tools" / "base"
_CAR_CHRONICLE_TOOLSET = (
    "context_tools.base.examples.car_chronicle.car_chronicle:CarChronicle"
)
_CHRONICLE_WITH_OUTPUT_TOOLSET = (
    "context_tools.base.examples.car_chronicle.chronicle_with_output:ChronicleWithOutput"
)
_BASE_GENERATOR_TOOLSET = "context_tools.base.context_tool:ContextTool"
_GENERATE_OUTPUT_PROSE = "Append each trip entry to the driving log before validating."
_META_CONTEXT_MARKER = "scaffold-vs-patch"


def _load_car_chronicle() -> Toolset:
    return _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)()


def _load_chronicle_with_output() -> Toolset:
    return _ToolsetLoader.instance().load(_CHRONICLE_WITH_OUTPUT_TOOLSET)()


def _load_base_generator() -> Toolset:
    return _ToolsetLoader.instance().load(_BASE_GENERATOR_TOOLSET)()


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


def _load_meta_concepts() -> str:
    return Instruction(
        "\u00a7 Contexts", _GENERATOR_DIR, domain_slug="context_tool"
    ).expand()


def _load_generator_templates() -> str:
    from primitives.assets import AssetCollection
    from primitives.assets import AssetLocation

    location = AssetLocation(
        "folder",
        _GENERATOR_DIR,
        "context_tool",
        folder=_GENERATOR_DIR / "templates",
    )
    return AssetCollection(location).merged()


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


with description("ContextTool composer"):
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

            with it("should not inline meta contexts from context_tool.md"):
                expect(
                    _META_CONTEXT_MARKER in self.response["instructions"]
                ).to(equal(False))

            with it("should not inline prose from a subclass generate_output override"):
                expect(
                    _GENERATE_OUTPUT_PROSE in self.response["instructions"]
                ).to(equal(False))

        with context("validate expands domain contexts as rubric"):
            with before.each:
                self.response = _expand_action(
                    self.chronicle,
                    "validate",
                    toolset_path=_CAR_CHRONICLE_TOOLSET,
                )

            with it("should inline the full Contexts section as rubric"):
                _assert_contexts_inlined(self.response["instructions"], self.contexts)

    with context("the base ContextTool toolset"):
        with before.all:
            self.generator = _load_base_generator()
            self.meta_concepts = _load_meta_concepts()
            self.template = _load_generator_templates()

        with context("generate expands meta face"):
            with before.each:
                self.response = _expand_action(
                    self.generator,
                    "generate",
                    toolset_path=_BASE_GENERATOR_TOOLSET,
                )

            with it("should inline meta contexts from context_tool.md"):
                _assert_text_inlined(self.response["instructions"], self.meta_concepts)

            with it("should inline all files from context_tools/base/templates/"):
                _assert_text_inlined(self.response["instructions"], self.template)
                expect("@context_tool" in self.response["instructions"]).to(equal(True))
                expect("# Instructions" in self.response["instructions"]).to(
                    equal(True)
                )
                expect("# Worked examples" in self.response["instructions"]).to(
                    equal(True)
                )

            with it("should inline worked samples from context_tools/examples"):
                expect("use-driving-voice" in self.response["instructions"]).to(
                    equal(True)
                )

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
