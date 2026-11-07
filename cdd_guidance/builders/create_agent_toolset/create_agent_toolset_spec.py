"""CreateAgentToolset and the car example it tells agents to copy.

The car example sits under ``_examples/``, which the installer and the suite runner skip, so this spec is what keeps
the shape the builder teaches loadable by the framework as it is now."""

from expects import equal, expect
from mamba import before, context, description, it

from harness.agent_tools.agent_tools import AgentInstructions
from cdd_guidance.builders.create_agent_toolset.create_agent_toolset import CreateAgentToolset
from cdd_guidance.builders.create_agent_toolset._examples.car.car import Car


with description("a CreateAgentToolset"):
    with context("that has been created"):
        with it("should work from the repository's root"):
            expect(type(CreateAgentToolset()).default_workspace_folder).to(equal("."))

    with context("whose car example is decorated as the builder teaches"):
        with before.each:
            self.car = Car("Volkswagen", "Beetle", 1967, "cheerful")
            self.recipe = AgentInstructions.for_callable(Car.travel_to, self.car)

        with it("should list the tools its travel_to recipe calls, in order"):
            expect(self.recipe.tools).to(equal(["start", "speak", "stop"]))

        with it("should run its start tool on the car it was made as"):
            self.car.start()
            expect(self.car.running).to(equal(True))
