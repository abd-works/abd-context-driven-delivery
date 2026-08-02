"""BDD spec for CarChronicle and ChronicleWithOutput example domain."""

from pathlib import Path
from typing import Any

from expects import equal, expect
from mamba import before, context, description, it

import context_tools  # noqa: F401
from primitives.actions.action import _ActionRunRequest, _ActionRunner
from tools.tool import Toolset, _ToolsetLoader

_CAR_DIR = Path(__file__).resolve().parent
_CAR_TOOLSET = (
    "context_tools.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle"
)
_WITH_OUTPUT_TOOLSET = (
    "context_tools.create_context_tool.examples.car_chronicle"
    ".chronicle_with_output:ChronicleWithOutput"
)
_LIFECYCLE = ("generate", "validate", "satisfy", "repair")


class _CarChronicleSpecSupport:
    """Load and expand car chronicle toolsets for the package specs."""

    def load(self, toolset_path: str) -> Toolset:
        return _ToolsetLoader.instance().load(toolset_path)()

    def expand(
        self,
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


with description("a CarChronicle domain"):
    with before.all:
        self.support = _CarChronicleSpecSupport()
        self.chronicle = self.support.load(_CAR_TOOLSET)

    with context("that has been created"):
        with it("should resolve module_dir to the car_chronicle package"):
            expect(self.chronicle.module_dir).to(equal(_CAR_DIR.resolve()))

        with it("should expose generate, validate, satisfy, and repair"):
            for name in _LIFECYCLE:
                expect(name in self.chronicle.actions).to(equal(True))


with description("a ChronicleWithOutput domain"):
    with before.all:
        self.support = _CarChronicleSpecSupport()
        self.chronicle = self.support.load(_WITH_OUTPUT_TOOLSET)

    with context("that has a generate_output target wired"):
        with it("should not declare its own generate action"):
            expect("generate" in type(self.chronicle).__dict__).to(equal(False))

        with it("should not declare its own validate action"):
            expect("validate" in type(self.chronicle).__dict__).to(equal(False))

        with it("should not declare its own satisfy action"):
            expect("satisfy" in type(self.chronicle).__dict__).to(equal(False))

        with it("should not declare its own repair action"):
            expect("repair" in type(self.chronicle).__dict__).to(equal(False))

        with it("should name the toolset car_chronicle"):
            expect(self.chronicle.toolset_name).to(equal("car_chronicle"))

        with it("should add an epic through the nested tool"):
            expect(self.chronicle.add_epic()).to(equal("epic added"))

        with it("should save chronicle entries from generate_output"):
            expect(self.chronicle.generate_output()).to(
                equal("Chronicle entries saved.")
            )

    with context("generate expands nested output tools"):
        with before.all:
            self.response = self.support.expand(
                self.chronicle,
                "generate",
                toolset_path=_WITH_OUTPUT_TOOLSET,
            )

        with it("should name add_epic on the generate tools list"):
            expect("add_epic" in self.response["tools"]).to(equal(True))
