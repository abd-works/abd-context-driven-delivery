"""BDD spec for CarChronicle and ChronicleWithOutput example domain."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from builders.create_context_tool.examples.car_chronicle.car_chronicle import (
    CarChronicle,
)
from builders.create_context_tool.examples.car_chronicle.chronicle_with_output import (
    ChronicleWithOutput,
)

_CAR_DIR = Path(__file__).resolve().parent
_LIFECYCLE = ("generate", "validate", "satisfy", "repair")


with description("a CarChronicle domain"):
    with before.all:
        self.chronicle = CarChronicle()

    with context("that has been created"):
        with it("should resolve module_dir to the car_chronicle package"):
            expect(self.chronicle.module_dir).to(equal(_CAR_DIR.resolve()))

        with it("should not expose generate, validate, satisfy, or repair"):
            signature = self.chronicle.tools
            for name in _LIFECYCLE:
                expect(name in signature).to(equal(False))


with description("a ChronicleWithOutput domain"):
    with before.all:
        self.chronicle = ChronicleWithOutput()

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
