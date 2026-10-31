"""BDD spec — the outputs each fidelity declares in its practice markdown."""
from pathlib import Path

from expects import be_empty, equal, expect
from mamba import before, context, description, it

from harness.installation.installer import Installer

Installer(repo=Path(__file__).resolve().parents[2]).ensure_import_path()

from bdd.bdd import Bdd  # noqa: E402
from clean_engineering.clean_engineering import CleanEngineering  # noqa: E402
from ddd.ddd import Ddd  # noqa: E402
from stories.stories import Stories  # noqa: E402
from ux.ux import Ux  # noqa: E402


with description("a fidelity's declared outputs") as self:
    with context("with the story map loaded from its practice"):
        with before.each:
            self.outputs = Stories().fidelities["story_map"].outputs

        with it("should name the file for each format"):
            expect(self.outputs).to(equal({"markdown": ".context/story-map.md", "drawio": ".context/story-map.drawio"}))

        with it("should give the file of its default format"):
            expect(Stories().fidelities["story_map"].default_output).to(equal(".context/story-map.md"))

    with context("with a fidelity that writes several files for one format"):
        with before.each:
            self.outputs = Stories().fidelities["acceptance_tests"].outputs

        with it("should list every file pattern for that format"):
            expect(len(self.outputs["python"])).to(equal(3))

    with context("with every practice loaded"):
        with before.each:
            self.practices = [Stories(), Ddd(), Ux(), CleanEngineering(), Bdd()]

        with it("should leave no fidelity without declared outputs"):
            missing = [
                f"{type(practice).__name__}.{name}"
                for practice in self.practices
                for name, fidelity in practice.fidelities.entries.items()
                if not fidelity.outputs
            ]
            expect(missing).to(be_empty)

        with it("should leave every fidelity without a root folder"):
            rooted = [
                f"{type(practice).__name__}.{name}"
                for practice in self.practices
                for name, fidelity in practice.fidelities.entries.items()
                if "root" in fidelity.outputs
            ]
            expect(rooted).to(be_empty)

        with it("should keep every markdown and drawio output in the .context folder"):
            outside = [
                f"{type(practice).__name__}.{name}.{label}"
                for practice in self.practices
                for name, fidelity in practice.fidelities.entries.items()
                for label, path in fidelity.outputs.items()
                if label in ("markdown", "drawio", "realization") and not path.startswith(".context/")
            ]
            expect(outside).to(be_empty)

        with it("should give every specification and implementation fidelity a code format"):
            without_code = [
                f"{type(practice).__name__}.{name}"
                for practice in self.practices
                for name, fidelity in practice.fidelities.entries.items()
                if fidelity.stage != "discovery"
                and not set(fidelity.outputs) & {"python", "typescript", "html"}
            ]
            expect(without_code).to(be_empty)

    with context("with a mockup and the front end it becomes"):
        with before.each:
            self.ux = Ux()

        with it("should write mockups as html beside the front end's code"):
            expect(self.ux.fidelities["mockup"].outputs["html"]).to(equal("{epic}/{user_goal}.html"))
