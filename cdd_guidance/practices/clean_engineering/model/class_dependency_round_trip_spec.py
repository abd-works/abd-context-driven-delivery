"""A class's dependencies, each labelled by the interaction it names, survive markdown and draw.io and read back."""

import re

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property

# The guillemets a dependency's interaction is written in on its arrow.
OPEN, CLOSE = chr(0xAB), chr(0xBB)


def _processes() -> CleanEngineeringModel:
    """A stoppable process that stops and reads a running process, and a launcher that owns one stoppable process."""
    running = OoadClass("RunningProcess", 1, intent="One process by its id.", operations=[Operation(name="alive", return_type="bool")])
    stoppable = OoadClass("StoppableProcess", 2, intent="Ends a process by its id.", operations=[Operation(name="stop", return_type="None")])
    stoppable.depend_on("RunningProcess", "stops")
    stoppable.depend_on("RunningProcess", "reads pid of")
    launcher = OoadClass("Launcher", 3, intent="Starts and ends one server.", properties=[Property("process", type_hint="StoppableProcess")])
    launcher.properties[0].stereotype = "composition"
    launcher.properties[0].derive_relationship()
    launcher.depend_on("StoppableProcess", "asks to stop")
    module = Module("process", 1)
    module.classes = [running, stoppable, launcher]
    model = CleanEngineeringModel("process")
    model.modules.append(module)
    return model


def _named(model: CleanEngineeringModel, name: str) -> OoadClass:
    return next(oclass for oclass in model.every_class() if oclass.name == name)


def _labels(oclass: OoadClass) -> list:
    return [(item.kind, item.label, item.target) for item in oclass.dependencies]


with description("a class that depends on another, labelled by the interaction"):
    with context("written as markdown"):
        with before.each:
            self.text = MarkdownCleanEngineeringModel().render(_processes())

        with it("should write each dependency as a dashed arrow line naming the interaction"):
            expect(self.text).to(contain("---<<stops>>--> RunningProcess"))

        with it("should write the dependency after the class's operations"):
            card = self.text.split("## StoppableProcess", 1)[1].split("## ", 1)[0]
            expect(card.index("+ stop(): None") < card.index("---<<stops>>")).to(equal(True))

    with context("written as markdown and read back"):
        with before.each:
            channel = MarkdownCleanEngineeringModel()
            self.model = channel.parse(channel.render(_processes()))

        with it("should keep every dependency of the class in order with its label"):
            expect(_labels(_named(self.model, "StoppableProcess"))).to(
                equal([("dependency", "stops", "RunningProcess"), ("dependency", "reads pid of", "RunningProcess")])
            )

        with it("should keep the operation the dependency line follows"):
            expect([op.name for op in _named(self.model, "StoppableProcess").operations]).to(contain("stop"))

        with it("should keep a composition and a dependency on the same pair apart"):
            launcher = _named(self.model, "Launcher")
            expect((launcher.relationships[0].kind, _labels(launcher))).to(
                equal(("composition", [("dependency", "asks to stop", "StoppableProcess")]))
            )

    with context("drawn in draw.io"):
        with before.each:
            self.xml = DrawIOCleanEngineeringModel().render(_processes())
            self.edges = re.findall(r'<mxCell id="\d+" value="([^"]*)" style="([^"]*)" edge="1" source="([^"]+)" target="([^"]+)"', self.xml)

        with it("should draw a dependency-only pair as a dashed arrow with an open head"):
            style = next(style for _v, style, source, target in self.edges if source.endswith("stoppableprocess") and target.endswith("runningprocess"))
            expect(("dashed=1" in style, "endArrow=open" in style)).to(equal((True, True)))

        with it("should write every interaction of the pair on the arrow in guillemets"):
            value = next(value for value, _s, source, target in self.edges if source.endswith("stoppableprocess"))
            expect(value).to(equal(f"{OPEN}stops{CLOSE} {OPEN}reads pid of{CLOSE}"))

        with it("should add the interaction to the label of a stronger arrow on the same pair"):
            value = next(value for value, _s, source, _t in self.edges if source.endswith("launcher"))
            expect(value).to(equal(f"process {OPEN}asks to stop{CLOSE}"))

    with context("drawn in draw.io and read back"):
        with before.each:
            channel = DrawIOCleanEngineeringModel()
            self.model = channel.parse(channel.render(_processes()))

        with it("should keep every dependency with its label"):
            expect(_labels(_named(self.model, "StoppableProcess"))).to(
                equal([("dependency", "stops", "RunningProcess"), ("dependency", "reads pid of", "RunningProcess")])
            )

        with it("should keep the composition the dependency shares an arrow with"):
            launcher = _named(self.model, "Launcher")
            expect((launcher.relationships[0].kind, _labels(launcher))).to(
                equal(("composition", [("dependency", "asks to stop", "StoppableProcess")]))
            )

    with context("copied into another model"):
        with it("should keep its dependencies in the clone"):
            expect(_labels(_named(_processes(), "StoppableProcess").clone())[0]).to(equal(("dependency", "stops", "RunningProcess")))

        with it("should keep its dependencies when another model is brought up to date from it"):
            target = CleanEngineeringModel("process")
            target.translate_from(_processes())
            expect(_labels(_named(target, "StoppableProcess"))[0]).to(equal(("dependency", "stops", "RunningProcess")))

        with it("should keep its dependencies in its record"):
            expect(_named(_processes(), "StoppableProcess").as_record()["dependencies"][0]["label"]).to(equal("stops"))
