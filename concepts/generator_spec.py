"""BDD spec for generator-behavior.md — action expansion via CarChronicle dummy (in-process)."""

from pathlib import Path
from typing import Any

from expects import be_true, equal, expect
from mamba import before, context, description, it

from agents.runner import ActionRunner
import generator  # noqa: F401 — generator package on path
from primitives.instruction import Instruction
from tools.tool import Toolset, ToolsetLoader

_REPO_ROOT = Path(__file__).resolve().parent.parent
_EXAMPLES_DIR = _REPO_ROOT / "generator" / "examples"
_CAR_CHRONICLE_DIR = _EXAMPLES_DIR / "car_chronicle"
_GENERATOR_DIR = _REPO_ROOT / "generator"
_CAR_CHRONICLE_TOOLSET = "generator.examples.car_chronicle.car_chronicle:CarChronicle"
_CHRONICLE_WITH_OUTPUT_TOOLSET = "generator.examples.car_chronicle.chronicle_with_output:ChronicleWithOutput"
_BASE_GENERATOR_TOOLSET = "generator.generator:Generator"
_GENERATE_OUTPUT_PROSE = "Append each trip entry to the driving log before validating."
_META_CONCEPT_MARKER = "scaffold-vs-patch"


def _load_car_chronicle() -> Toolset:
    toolset_cls = ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)
    return toolset_cls()


def _load_chronicle_with_output() -> Toolset:
    toolset_cls = ToolsetLoader.instance().load(_CHRONICLE_WITH_OUTPUT_TOOLSET)
    return toolset_cls()


def _expand_action(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
    context: dict[str, Any] | None = None,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return ActionRunner.instance().run(
        {"toolset": toolset_path, "context": context or {}},
        toolset_path=toolset_path,
        action_name=action_name,
        context=context or {},
        arguments=arguments or {},
        instance=instance,
    )


def _load_action_prose(action: str) -> str:
    return Instruction(f"base-generator/{action}", _GENERATOR_DIR).expand()


def _load_meta_concepts() -> str:
    return Instruction("§ Concepts", _GENERATOR_DIR).expand()


def _load_generator_templates() -> str:
    from primitives.asset_collection import AssetCollection
    from primitives.asset_location import AssetLocation

    location = AssetLocation(
        "folder",
        _GENERATOR_DIR,
        "generator",
        folder=_GENERATOR_DIR / "templates",
    )
    return AssetCollection(location).merged()


def _load_base_generator() -> Toolset:
    toolset_cls = ToolsetLoader.instance().load(_BASE_GENERATOR_TOOLSET)
    return toolset_cls()


def _load_car_concepts() -> str:
    return Instruction("§ Concepts", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle").expand()


def _load_car_examples() -> str:
    return Instruction("examples", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle").expand()


def _load_car_template() -> str:
    return Instruction("car_chronicle-templates", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle").expand()


def _assert_text_inlined(instructions: str, source: str) -> None:
    expect(source in instructions).to(be_true)


def _assert_concepts_inlined(instructions: str, concepts_text: str) -> None:
    from primitives.clean_code_ground_truth import concept_bullet_lines, concept_rule_slugs

    _assert_text_inlined(instructions, concepts_text)
    slugs = concept_rule_slugs(concepts_text)
    bullets = concept_bullet_lines(concepts_text)
    instruction_slugs = [
        slug for slug in concept_rule_slugs(instructions) if slug not in {"scan"}
    ]
    expect(len(slugs)).to(equal(len(bullets)))
    expect(len(slugs)).to(equal(len(instruction_slugs)))
    for slug in slugs:
        expect(slug in instructions).to(be_true)
    for bullet in bullets:
        expect(bullet in instructions).to(be_true)


with description("Action expansion"):
    with context("a CarChronicle generator in generator/examples"):
        with before.all:
            self.chronicle = _load_car_chronicle()
            self.concepts = _load_car_concepts()
            self.examples = _load_car_examples()
            self.template = _load_car_template()

        with context("the generate action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.chronicle,
                    "generate",
                    toolset_path=_CAR_CHRONICLE_TOOLSET,
                )

            with it("should set action to generate"):
                expect(self.response["action"]).to(equal("generate"))

            with it("should name no tools on generate"):
                expect(self.response["tools"]).to(equal([]))

            with it("should inline the full Concepts section from car_chronicle.md"):
                _assert_concepts_inlined(self.response["instructions"], self.concepts)

            with it("should inline the full examples.md file"):
                _assert_text_inlined(self.response["instructions"], self.examples)

            with it("should inline the full car_chronicle templates file"):
                _assert_text_inlined(self.response["instructions"], self.template)

            with it("should inline generate.md from the generator module"):
                _assert_text_inlined(self.response["instructions"], _load_action_prose("generate"))

            with it("should not inline meta concepts from generator.md"):
                expect(_META_CONCEPT_MARKER in self.response["instructions"]).to(equal(False))

            with it("should not inline prose from a subclass generate_output override"):
                expect(_GENERATE_OUTPUT_PROSE in self.response["instructions"]).to(equal(False))

        with context("the validate action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.chronicle,
                    "validate",
                    toolset_path=_CAR_CHRONICLE_TOOLSET,
                )

            with it("should set action to validate"):
                expect(self.response["action"]).to(equal("validate"))

            with it("should name scan on tools"):
                expect(self.response["tools"]).to(equal(["scan"]))

            with it("should inline the full Concepts section as rubric"):
                _assert_concepts_inlined(self.response["instructions"], self.concepts)

            with it("should inline validate.md from the generator module"):
                _assert_text_inlined(self.response["instructions"], _load_action_prose("validate"))

        with context("the satisfy action is expanded"):
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

            with it("should inline the full Concepts section"):
                _assert_concepts_inlined(self.response["instructions"], self.concepts)

            with it("should inline the full car_chronicle templates file"):
                _assert_text_inlined(self.response["instructions"], self.template)

            with it("should inline satisfy.md from the generator module"):
                _assert_text_inlined(self.response["instructions"], _load_action_prose("satisfy"))

        with context("the repair action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.chronicle,
                    "repair",
                    toolset_path=_CAR_CHRONICLE_TOOLSET,
                    arguments={
                        "asset": "generator/examples/car_chronicle/output/driving-log.md",
                        "violation": "Scanner: use-driving-voice — chronicle reads like a spec sheet",
                    },
                )

            with it("should set action to repair"):
                expect(self.response["action"]).to(equal("repair"))

            with it("should name scan on tools"):
                expect(self.response["tools"]).to(equal(["scan"]))

            with it("should inline repair.md from the generator module"):
                expect("Iterate until **validate** passes" in self.response["instructions"]).to(be_true)
                expect("<domain>/examples/<descriptive-folder>/" in self.response["instructions"]).to(be_true)
                expect("Delete `runs/` when the repair is done" in self.response["instructions"]).to(be_true)

            with it("should inline generator-fix prose from repair.md"):
                instructions = self.response["instructions"]
                expect("Fix the generator" in instructions).to(be_true)
                expect("Do not hand-edit" in instructions).to(be_true)
                expect("Re-run **generate**" in instructions).to(be_true)

            with it("should inline concepts examples and template for root cause"):
                _assert_concepts_inlined(self.response["instructions"], self.concepts)
                _assert_text_inlined(self.response["instructions"], self.examples)
                _assert_text_inlined(self.response["instructions"], self.template)

            with it("should substitute asset and violation arguments"):
                instructions = self.response["instructions"]
                expect("generator/examples/car_chronicle/output/driving-log.md" in instructions).to(be_true)
                expect("use-driving-voice" in instructions).to(be_true)

            with it("should inline validate.md from the generator module"):
                _assert_text_inlined(self.response["instructions"], _load_action_prose("validate"))

    with context("the base Generator toolset in generator/generator.py"):
        with before.all:
            self.generator = _load_base_generator()
            self.meta_concepts = _load_meta_concepts()
            self.template = _load_generator_templates()

        with context("the generate action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.generator,
                    "generate",
                    toolset_path=_BASE_GENERATOR_TOOLSET,
                )

            with it("should set action to generate"):
                expect(self.response["action"]).to(equal("generate"))

            with it("should inline meta concepts from generator.md"):
                _assert_text_inlined(self.response["instructions"], self.meta_concepts)

            with it("should inline all files from generator/templates/"):
                _assert_text_inlined(self.response["instructions"], self.template)
                expect("@generator" in self.response["instructions"]).to(be_true)
                expect("# Instructions" in self.response["instructions"]).to(be_true)
                expect("# Worked examples" in self.response["instructions"]).to(be_true)

            with it("should inline generate.md action prose"):
                _assert_text_inlined(self.response["instructions"], _load_action_prose("generate"))

            with it("should inline worked samples from generator/examples"):
                expect("use-driving-voice" in self.response["instructions"]).to(be_true)

    with context("a generator subclass that overrides generate_output in generator/examples"):
        with before.all:
            self.chronicle = _load_chronicle_with_output()

        with context("the generate action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.chronicle,
                    "generate",
                    toolset_path=_CHRONICLE_WITH_OUTPUT_TOOLSET,
                )

            with it("should inline prose from the subclass generate_output action"):
                _assert_text_inlined(self.response["instructions"], _GENERATE_OUTPUT_PROSE)

            with it("should name add_epic from nested generate_output on tools"):
                expect(self.response["tools"]).to(equal(["add_epic"]))
