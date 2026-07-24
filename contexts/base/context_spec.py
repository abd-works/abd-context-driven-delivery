"""BDD spec for context-behavior.md — action expansion via CarChronicle dummy (in-process)."""

from pathlib import Path
from typing import Any

from expects import be_true, equal, expect
from mamba import before, context, description, it

from primitives.actions.action import _ActionRunRequest, _ActionRunner
import contexts  # noqa: F401 — generator package on path
from primitives.instructions import Instruction
from tools.tool import Toolset, _ToolsetLoader

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EXAMPLES_DIR = _REPO_ROOT / "contexts" / "base" / "examples"
_CAR_CHRONICLE_DIR = _EXAMPLES_DIR / "car_chronicle"
_CONTEXTS_DIR = _REPO_ROOT / "contexts"
_GENERATOR_DIR = _CONTEXTS_DIR / "base"
_CAR_CHRONICLE_TOOLSET = "contexts.base.examples.car_chronicle.car_chronicle:CarChronicle"
_CHRONICLE_WITH_OUTPUT_TOOLSET = "contexts.base.examples.car_chronicle.chronicle_with_output:ChronicleWithOutput"
_BASE_GENERATOR_TOOLSET = "contexts.base.context:Context"
_STORIES_TOOLSET = "contexts.stories.stories:Stories"
_GENERATE_OUTPUT_PROSE = "Append each trip entry to the driving log before validating."
_META_CONTEXT_MARKER = "scaffold-vs-patch"
_DEFAULT_PARTITION_SNIPPET = "Determine top-level structure based on user suggestion"
_STORIES_PARTITION_SNIPPET = "**Epics**"


def _load_car_chronicle() -> Toolset:
    toolset_cls = _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)
    return toolset_cls()


def _load_chronicle_with_output() -> Toolset:
    toolset_cls = _ToolsetLoader.instance().load(_CHRONICLE_WITH_OUTPUT_TOOLSET)
    return toolset_cls()


def _expand_action(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
    context: dict[str, Any] | None = None,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _ActionRunner.instance().run(
        _ActionRunRequest(
            request={"toolset": toolset_path, "context": context or {}},
            toolset_path=toolset_path,
            action_name=action_name,
            context=context or {},
            arguments=arguments or {},
            instance=instance,
        )
    )


def _load_action_prose(action: str) -> str:
    return Instruction(f"base-context/{action}", _GENERATOR_DIR).expand()


def _load_meta_concepts() -> str:
    return Instruction("§ Contexts", _GENERATOR_DIR, domain_slug="context").expand()


def _load_generator_templates() -> str:
    from primitives.assets import AssetCollection
    from primitives.assets import AssetLocation

    location = AssetLocation(
        "folder",
        _GENERATOR_DIR,
        "context",
        folder=_GENERATOR_DIR / "templates",
    )
    return AssetCollection(location).merged()


def _load_base_generator() -> Toolset:
    toolset_cls = _ToolsetLoader.instance().load(_BASE_GENERATOR_TOOLSET)
    return toolset_cls()


def _load_car_contexts() -> str:
    return Instruction("§ Contexts", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle").expand()


def _load_car_examples() -> str:
    return Instruction("examples", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle").expand()


def _load_car_template() -> str:
    return Instruction("car_chronicle-templates", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle").expand()


def _assert_text_inlined(instructions: str, source: str) -> None:
    expect(source in instructions).to(be_true)


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
    instruction_slugs = [
        slug for slug in _context_rule_slugs(instructions) if slug not in {"scan"}
    ]
    expect(len(slugs)).to(equal(len(bullets)))
    expect(len(slugs)).to(equal(len(instruction_slugs)))
    for slug in slugs:
        expect(slug in instructions).to(be_true)
    for bullet in bullets:
        expect(bullet in instructions).to(be_true)


with description("Action expansion"):
    with context("a CarChronicle generator in contexts/examples"):
        with before.all:
            self.chronicle = _load_car_chronicle()
            self.contexts = _load_car_contexts()
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

            with it("should inline the full Contexts section from car_chronicle.md"):
                _assert_contexts_inlined(self.response["instructions"], self.contexts)

            with it("should inline the full examples.md file"):
                _assert_text_inlined(self.response["instructions"], self.examples)

            with it("should inline the full car_chronicle templates file"):
                _assert_text_inlined(self.response["instructions"], self.template)

            with it("should inline generate.md from the generator module"):
                _assert_text_inlined(self.response["instructions"], _load_action_prose("generate"))

            with it("should not inline meta contexts from context.md"):
                expect(_META_CONTEXT_MARKER in self.response["instructions"]).to(equal(False))

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

            with it("should inline the full Contexts section as rubric"):
                _assert_contexts_inlined(self.response["instructions"], self.contexts)

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

            with it("should inline the full Contexts section"):
                _assert_contexts_inlined(self.response["instructions"], self.contexts)

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
                        "asset": "contexts/base/examples/car_chronicle/output/driving-log.md",
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

            with it("should inline contexts examples and template for root cause"):
                _assert_contexts_inlined(self.response["instructions"], self.contexts)
                _assert_text_inlined(self.response["instructions"], self.examples)
                _assert_text_inlined(self.response["instructions"], self.template)

            with it("should substitute asset and violation arguments"):
                instructions = self.response["instructions"]
                expect("contexts/base/examples/car_chronicle/output/driving-log.md" in instructions).to(be_true)
                expect("use-driving-voice" in instructions).to(be_true)

            with it("should inline validate.md from the generator module"):
                _assert_text_inlined(self.response["instructions"], _load_action_prose("validate"))

    with context("the base Context toolset in contexts/base/context.py"):
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

            with it("should inline meta contexts from context.md"):
                _assert_text_inlined(self.response["instructions"], self.meta_concepts)

            with it("should inline all files from contexts/base/templates/"):
                _assert_text_inlined(self.response["instructions"], self.template)
                expect("@context" in self.response["instructions"]).to(be_true)
                expect("# Instructions" in self.response["instructions"]).to(be_true)
                expect("# Worked examples" in self.response["instructions"]).to(be_true)

            with it("should inline base-context/generate.md action prose"):
                _assert_text_inlined(self.response["instructions"], _load_action_prose("generate"))

            with it("should inline worked samples from contexts/examples"):
                expect("use-driving-voice" in self.response["instructions"]).to(be_true)

    with context("a generator subclass that overrides generate_output in contexts/examples"):
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

    with context("partition index and segment on Context"):
        with before.all:
            self.chronicle = _load_car_chronicle()
            self.stories = _ToolsetLoader.instance().load(_STORIES_TOOLSET)()

        with context("the partition action is expanded on CarChronicle"):
            with before.each:
                self.response = _expand_action(
                    self.chronicle,
                    "partition",
                    toolset_path=_CAR_CHRONICLE_TOOLSET,
                    arguments={"context": "corpus/", "mode": "one_go"},
                )

            with it("should set action to partition"):
                expect(self.response["action"]).to(equal("partition"))

            with it("should inline base-context/partition.md"):
                expect("# Partition" in self.response["instructions"]).to(be_true)
                expect("thin partition of source material" in self.response["instructions"]).to(be_true)

            with it("should nest index and segment prose"):
                expect("# Index" in self.response["instructions"]).to(be_true)
                expect("# Segment" in self.response["instructions"]).to(be_true)
                expect("named segment files" in self.response["instructions"]).to(be_true)

            with it("should inline default partition guidance when domain has no partition.md"):
                expect(_DEFAULT_PARTITION_SNIPPET in self.response["instructions"]).to(be_true)

            with it("should name the index file after the corpus subject"):
                expect("{subject}-index.md" in self.response["instructions"]).to(be_true)
                expect("corpus basename" in self.response["instructions"]).to(be_true)
                expect("car_chronicle-index.md" in self.response["instructions"]).to(be_false)

        with context("the index action is expanded on Stories"):
            with before.each:
                self.response = _expand_action(
                    self.stories,
                    "index",
                    toolset_path=_STORIES_TOOLSET,
                    arguments={"context": "corpus/"},
                )

            with it("should inline stories partition.md guidance"):
                expect(_STORIES_PARTITION_SNIPPET in self.response["instructions"]).to(be_true)

            with it("should name the index after the corpus subject not the skill"):
                expect("{subject}-index.md" in self.response["instructions"]).to(be_true)
                expect("corpus basename" in self.response["instructions"]).to(be_true)
                expect("stories-index.md" in self.response["instructions"]).to(be_false)
