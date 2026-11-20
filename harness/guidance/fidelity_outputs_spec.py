"""BDD spec — the outputs each fidelity declares in its practice markdown."""
from pathlib import Path

from expects import be_empty, equal, expect
from mamba import before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from cdd_guidance.practices.bdd.bdd import Bdd  # noqa: E402
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering  # noqa: E402
from cdd_guidance.practices.ddd.ddd import Ddd  # noqa: E402
from cdd_guidance.practices.stories.stories import Stories  # noqa: E402
from cdd_guidance.practices.ux.ux import Ux  # noqa: E402


with description("a fidelity's declared outputs") as self:
    with context("with the story map loaded from its practice"):
        with before.each:
            self.outputs = Stories().fidelities["story_map"].outputs

        with it("should name the file for each format"):
            expect(self.outputs).to(equal({
                "markdown": ".context/story-map.md", "drawio": ".context/story-map.drawio",
                "whiteboard": ".context/story-map.whiteboard",
                "thin_slice": [".context/thin-slice.md", ".context/thin-slice.drawio"],
            }))

    with context("with a fidelity that writes several files for one format"):
        with before.each:
            self.outputs = Stories().fidelities["acceptance_tests"].outputs

        with it("should list every file pattern for that format: the sub-epic's three tier files, a story's one runnable file, and an epic's own stories' file"):
            expect(len(self.outputs["python"])).to(equal(5))

    with context("with a story that sits directly under an epic, and an epic with a sub-epic"):
        with before.each:
            self.scenarios = Stories().fidelities["scenarios"].declared
            self.acceptance_tests = Stories().fidelities["acceptance_tests"].declared

        with it("should declare the markdown scenarios an epic holds for its own stories, in the epic's folder"):
            expect(self.scenarios.includes("story_tests/increase-credit-limit/increase_credit_limit_story.test.md", "markdown")).to(equal(True))

        with it("should declare the code scenarios an epic holds for its own stories, in the epic's folder"):
            expect(all(self.scenarios.includes(f"story_tests/increase-credit-limit/increase_credit_limit_story.test.{ext}", label)
                       for label, ext in (("python", "py"), ("typescript", "ts")))).to(equal(True))

        with it("should declare the story test an epic holds for its own stories, in the epic's folder"):
            expect(self.acceptance_tests.includes("story_tests/increase-credit-limit/increase_credit_limit_story.test.py", "python")).to(equal(True))

        with it("should still declare a sub-epic's scenarios in the sub-epic's folder"):
            expect(self.scenarios.includes("story_tests/fill-cart/add-books/add_books_story.test.md", "markdown")).to(equal(True))

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

        with it("should keep every markdown and drawio output in a .context folder, or a scenario file in story_tests"):
            outside = [
                f"{type(practice).__name__}.{name}.{label}"
                for practice in self.practices
                for name, fidelity in practice.fidelities.entries.items()
                for label, paths in fidelity.outputs.items()
                for path in ([paths] if isinstance(paths, str) else paths)
                if label in ("markdown", "drawio", "realization") and ".context/" not in path and not path.startswith("story_tests/")
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

        with it("should also offer the mockup as a Claude Design canvas, each version's canvas.json in its root"):
            expect(self.ux.fidelities["mockup"].outputs["claude_design"]).to(equal("design-canvas/{version}/project/canvas.json"))
