# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for primitives/tools/examples/car/car.py — Car toolset example."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_false, be_true, contain, equal, expect
from mamba import before, context, description, it

from tools.examples.car.car import Car


def _default_car() -> Car:
    """Minimal valid Car for tests."""
    return Car(
        make="Toyota",
        model="Camry",
        year=2020,
        personality="calm and practical",
    )


with description("a car"):
    with context("that has been created"):
        with it("should expose make"):
            # Arrange / Act
            car = _default_car()
            # Assert
            expect(car.make).to(equal("Toyota"))

        with it("should expose model"):
            # Arrange / Act
            car = _default_car()
            # Assert
            expect(car.model).to(equal("Camry"))

        with it("should expose year"):
            # Arrange / Act
            car = _default_car()
            # Assert
            expect(car.year).to(equal(2020))

        with it("should expose personality"):
            # Arrange / Act
            car = _default_car()
            # Assert
            expect(car.personality).to(equal("calm and practical"))

        with it("should not be running"):
            # Arrange / Act
            car = _default_car()
            # Assert
            expect(car.running).to(be_false)

    with context("that has been started"):
        with before.each:
            self.car = _default_car()
            self.car.start()

        with it("should be running"):
            # Assert
            expect(self.car.running).to(be_true)

        with context("that is stopped"):
            with it("should not be running"):
                # Act
                self.car.stop()
                # Assert
                expect(self.car.running).to(be_false)

            with it("should stop at zero speed"):
                # Arrange
                self.car.accelerate(30.0)
                # Act
                self.car.stop()
                # Assert — drive at 0 speed reflects stopped state
                result = self.car.drive(1.0)
                expect(result).to(contain("cannot drive"))

        with context("that is driven"):
            with it("should return a drove message"):
                # Act
                result = self.car.drive(10.0)
                # Assert
                expect(result).to(contain("Drove 10.0 miles"))

        with context("that is accelerated"):
            with it("should return an accelerated message"):
                # Act
                result = self.car.accelerate(50.0)
                # Assert
                expect(result).to(contain("50 mph"))

            with it("should accumulate speed across calls"):
                # Act
                self.car.accelerate(30.0)
                result = self.car.accelerate(20.0)
                # Assert
                expect(result).to(contain("50 mph"))

        with context("that is decelerated"):
            with it("should return a decelerated message"):
                # Arrange
                self.car.accelerate(60.0)
                # Act
                result = self.car.decelerate(20.0)
                # Assert
                expect(result).to(contain("40 mph"))

            with it("should not go below zero speed"):
                # Arrange
                self.car.accelerate(10.0)
                # Act
                result = self.car.decelerate(50.0)
                # Assert — clamped at 0
                expect(result).to(contain("0 mph"))

        with context("that speaks"):
            with it("should return speech in character"):
                # Act
                result = self.car.speak("Hello!")
                # Assert
                expect(result).to(contain("Hello!"))

    with context("that has not been started"):
        with before.each:
            self.car = _default_car()

        with context("that is asked to drive"):
            with it("should refuse with engine off message"):
                # Act
                result = self.car.drive(5.0)
                # Assert
                expect(result).to(contain("cannot drive"))

        with context("that is asked to accelerate"):
            with it("should refuse with engine off message"):
                # Act
                result = self.car.accelerate(10.0)
                # Assert
                expect(result).to(contain("cannot accelerate"))

        with context("that is asked to decelerate"):
            with it("should refuse with engine off message"):
                # Act
                result = self.car.decelerate(10.0)
                # Assert
                expect(result).to(contain("cannot decelerate"))
