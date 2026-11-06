"""BDD spec for Sketch toolset + ActionExpander integration.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("sketch", None)

from expects import be_true, contain, equal, expect
from mamba import after, before, context, description, it

from harness.agent_tools.agent_tools import AgentInstructions
from space.session.throwaway_project import ThrowawayProject
from sketch import Sketch
from harness.agent_tools.agent_tools import AgentToolSet


with description("Sketch toolset") as self:
    with before.each:
        self.throwaway = ThrowawayProject()

    with after.each:
        self.throwaway.close()

    with context("with its tools listed"):
        with it("exposes find_template, save_sketch, list_sketches as tools"):
            tools = AgentToolSet.instantiate(Sketch).tools
            expect(tools["find_template"].kind).to(equal("tool"))
            expect(tools["save_sketch"].kind).to(equal("tool"))
            expect(tools["list_sketches"].kind).to(equal("tool"))

        with it("exposes sketch as an action with find_template and save_sketch"):
            sketch = AgentToolSet.instantiate(Sketch).tools["sketch"]
            expect(sketch.kind).to(equal("instructions"))
            expect("find_template" in sketch.tools).to(be_true)
            expect("save_sketch" in sketch.tools).to(be_true)
            expect("review_sketch" in sketch.tools).to(be_true)

    with context("sketch_template property"):
        with it("returns the default template when agent_dir was not set at construction"):
            sketcher = Sketch()
            content = sketcher.sketch_template
            expect(content).to(contain("heading-and-indent notation"))

        with it("returns the agent-dir template when agent_dir was set at construction"):
            import tempfile
            with tempfile.TemporaryDirectory() as agent_dir:
                templates_dir = Path(agent_dir) / "templates"
                templates_dir.mkdir()
                template_path = templates_dir / "test-sketch.md"
                template_path.write_text("# constructed agent template\n", encoding="utf-8")
                sketcher = Sketch(agent_dir=agent_dir)
                content = sketcher.sketch_template
                expect(content).to(contain("constructed agent template"))

    with context("find_template tool"):
        with it("falls back to the default template when no agent_dir template exists"):
            sketcher = Sketch()
            content = sketcher.find_template(agent_dir="")
            expect(content).to(contain("heading-and-indent notation"))

        with it("returns the agent's own *-sketch.* when the templates directory contains one"):
            import tempfile
            with tempfile.TemporaryDirectory() as agent_dir:
                templates_dir = Path(agent_dir) / "templates"
                templates_dir.mkdir()
                template_path = templates_dir / "demo-sketch.md"
                template_path.write_text("# demo agent template\nrough shape\n", encoding="utf-8")
                sketcher = Sketch()
                content = sketcher.find_template(agent_dir=agent_dir)
                expect(content).to(contain("demo agent template"))

        with it("falls back to the default when agent_dir is set but the directory is missing"):
            sketcher = Sketch()
            content = sketcher.find_template(agent_dir="does/not/exist")
            expect(content).to(contain("heading-and-indent notation"))

    with context("save_sketch tool"):
        with before.each:
            from space.session import Session

            self.session = Session.current()
            self.sketcher = Sketch(session=self.session)

        with it("writes the session's sketch in the .context folder under the session root"):
            path = Path(self.sketcher.save_sketch("rough\n"))
            expect(path).to(equal(self.session.root / ".context" / f"{self.session.name}-sketch.md"))

        with it("reads the sketch from a file when paths is set"):
            source = self.throwaway.root / "draft.md"
            source.write_text("from the file\n", encoding="utf-8")
            path = self.sketcher.save_sketch(paths=str(source))
            expect(Path(path).read_text(encoding="utf-8")).to(equal("from the file\n"))

        with it("writes a module's sketch in that module's .context folder"):
            path = Path(self.sketcher.save_sketch("rough\n", module="billing"))
            expect(path.parent).to(equal(self.session.root / "billing" / ".context"))

        with it("writes straight into a module that is already a .context folder"):
            path = Path(self.sketcher.save_sketch("rough\n", module="billing/.context"))
            expect(path.parent).to(equal(self.session.root / "billing" / ".context"))

        with it("overwrites the session's sketch when saved again"):
            self.sketcher.save_sketch("first draft\n")
            path = self.sketcher.save_sketch("second draft\n")
            expect(Path(path).read_text(encoding="utf-8")).to(equal("second draft\n"))

    with context("list_sketches tool"):
        with before.each:
            from space.session import Session

            self.session = Session.current()
            self.sketcher = Sketch(session=self.session)

        with it("returns no sketches when the .context directory does not exist"):
            expect(self.sketcher.list_sketches()).to(equal("no sketches"))

        with it("returns no sketches when the .context directory exists but is empty"):
            (self.session.root / ".context").mkdir(parents=True)
            expect(self.sketcher.list_sketches()).to(equal("no sketches"))

        with it("lists every *-sketch.md file in the session root's .context folder"):
            self.sketcher.save_sketch("a\n")
            (self.session.root / ".context" / "older-sketch.md").write_text("b\n", encoding="utf-8")
            expect(len(self.sketcher.list_sketches().splitlines())).to(equal(2))

        with it("lists a module's sketches when a module is named"):
            self.sketcher.save_sketch("a\n", module="billing")
            expect(self.sketcher.list_sketches(module="billing")).to(contain("billing"))

    with context("sketch action body"):
        with before.each:
            self.sketcher = Sketch()
            self.body = AgentInstructions.for_callable(
                Sketch.sketch, self.sketcher
            )

        with it("wires find_template and save_sketch as its tool steps"):
            expect("find_template" in self.body.tools).to(be_true)
            expect("save_sketch" in self.body.tools).to(be_true)

        with it("wires review_sketch after save_sketch as a hard review gate"):
            steps = list(self.body.tools)
            expect("review_sketch" in steps).to(be_true)
            expect("save_sketch" in steps).to(be_true)
            save_i = steps.index("save_sketch")
            expect("review_sketch" in steps[save_i:]).to(be_true)

        with it("expands prose that instructs the sketcher to persist drafts via save_sketch"):
            joined = "\n".join(self.body.prompt)
            expect(joined).to(contain("save_sketch"))

        with it("instructs pause, confirm correctness, and correct mistakes before the next question"):
            joined = "\n".join(self.body.prompt)
            expect(joined).to(contain("review_sketch"))
            expect(joined).to(contain("confirm"))
            expect(joined).to(contain("mistakes"))
            expect(joined).to(
                contain("Do not ask the next theme until that review confirms the sketch")
            )
            expect(joined).to(
                contain("save_sketch the shell in the same turn it is written")
            )

        with it("instructs carrying named review mistakes into the next sketch"):
            joined = "\n".join(self.body.prompt)
            expect(joined).to(contain("Carry forward"))
            expect(joined).to(
                contain("Do not regenerate as if those mistakes never happened")
            )
            expect(joined).to(contain("Correct the sketch"))

        with it("instructs grilling to validate the sketch rather than run disconnected"):
            joined = "\n".join(self.body.prompt)
            expect(joined).to(contain("validate what the sketch claimed"))
            expect(joined).to(contain("must not run disconnected"))

        with it("instructs batching similar questions so the loop does not run forever"):
            joined = "\n".join(self.body.prompt)
            expect(joined).to(contain("Batch similar questions"))
            expect(joined).to(contain("does not run forever"))

        with it("includes the grill_with_context body in sketch"):
            joined = "\n".join(self.body.prompt)
            expect(joined).to(contain("(Recommended)"))
            expect(joined).to(contain("save_sketch"))
            expect(joined).to(contain("Conduct a relentless grilling interview"))

        with it("inlines each listed practice's rules markdown_block"):
            from cdd_guidance.practices.bdd.bdd import Bdd

            sketcher = Sketch()
            sketcher.begin([Bdd(fidelity="behavior")], action="sketch")
            joined = "\n".join(
                AgentInstructions.for_callable(Sketch.sketch, sketcher).prompt
            )
            expect(joined).to(contain("observable-behavior"))
            expect(joined).to(contain("no-implementation"))
            expect(joined).to(contain("not a graph query"))


with description("a sketch action"):
    with context("that expands with context tools"):
        with it("should include the sketch session body in sketch"):
            expect("review_sketch" in Sketch().tools).to(be_true)
            expect(Sketch.review_sketch.__doc__).to(contain("Grill must validate the sketch"))

    with context("that pauses for sketch review"):
        with it("should return the sketch-review marker from review_sketch"):
            expect(Sketch().review_sketch()).to(equal("sketch-review"))

        with it("should expose review_sketch as a tool"):
            expect("review_sketch" in Sketch().tools).to(be_true)


with description("PracticeGuidance operations for sketch"):
    with it("should not expose sketch on practice Guidance"):
        cls = type(
            AgentToolSet.instantiate(
                "cdd_guidance.builders.create_context_tool._examples.car_chronicle.car_chronicle:CarChronicle"
            )
        )
        practice = cls()
        expect("sketch" in practice.tools).to(equal(False))
