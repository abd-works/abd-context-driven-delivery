"""BDD spec for Sketch toolset + ActionExpander integration.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("sketch", None)

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

from primitives.actions.action import _ActionExpander
from sketch import Sketch
from tools.tool import _ToolsetLoader


with description("Sketch toolset"):
    with context("manifest signature"):
        with it("exposes find_template, save_sketch, list_sketches as tools"):
            sig = Sketch.manifest.signature
            expect(sig["find_template"]["kind"]).to(equal("tool"))
            expect(sig["save_sketch"]["kind"]).to(equal("tool"))
            expect(sig["list_sketches"]["kind"]).to(equal("tool"))

        with it("exposes sketch as an action with find_template and save_sketch"):
            entry = Sketch.manifest.signature["sketch"]
            expect(entry["kind"]).to(equal("action"))
            expect("find_template" in entry["tools"]).to(be_true)
            expect("save_sketch" in entry["tools"]).to(be_true)
            expect("complete_tick" in entry["tools"]).to(be_true)
            expect(entry.get("chain")).to(equal(None))

    with context("sketch_template property"):
        with it("returns the default template when agent_dir was not set at construction"):
            sketcher = Sketch()
            content = sketcher.sketch_template
            expect(content).to(contain("terse-indent notation"))

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
            expect(content).to(contain("terse-indent notation"))

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
            expect(content).to(contain("terse-indent notation"))

    with context("save_sketch tool"):
        with before.each:
            import tempfile
            self.tmp = tempfile.TemporaryDirectory()
            self.destination = self.tmp.name
            self.sketcher = Sketch()

        with it("writes a sprint-folder destination up into path/.context"):
            sprint = Path(self.destination) / ".context" / "sessions" / "my-sprint"
            sprint.mkdir(parents=True)
            path = Path(
                self.sketcher.save_sketch(
                    destination=str(sprint),
                    slug="engagement",
                    content="rough\n",
                )
            )
            expect(path.parent).to(equal(Path(self.destination) / ".context"))
            expect(path.name).to(equal("engagement-sketch.md"))
            expect((sprint / "engagement-sketch.md").exists()).to(equal(False))

        with it("writes to .context/{slug}-sketch.md under the destination"):
            path = self.sketcher.save_sketch(
                destination=self.destination,
                slug="demo-class",
                content="thing : base thing\n  sub thing\n",
            )
            resolved = Path(path)
            expect(resolved.is_file()).to(be_true)
            expect(resolved.name).to(equal("demo-class-sketch.md"))
            expect(resolved.parent.name).to(equal(".context"))
            expect(resolved.read_text(encoding="utf-8")).to(contain("thing : base thing"))

        with it("creates the .context/ directory when it does not exist"):
            context_dir = Path(self.destination) / ".context"
            expect(context_dir.exists()).to(equal(False))

            self.sketcher.save_sketch(
                destination=self.destination,
                slug="fresh-class",
                content="rough shape\n",
            )

            expect(context_dir.is_dir()).to(be_true)

        with it("overwrites an existing sketch at the same slug"):
            self.sketcher.save_sketch(
                destination=self.destination,
                slug="mutable-class",
                content="first draft\n",
            )
            path = self.sketcher.save_sketch(
                destination=self.destination,
                slug="mutable-class",
                content="second draft\n",
            )
            expect(Path(path).read_text(encoding="utf-8")).to(equal("second draft\n"))

        with it("returns the resolved sketch path as a string"):
            path = self.sketcher.save_sketch(
                destination=self.destination,
                slug="typed-class",
                content="typed shape\n",
            )
            expect(isinstance(path, str)).to(be_true)
            expect(path).to(contain("typed-class-sketch.md"))

    with context("list_sketches tool"):
        with before.each:
            import tempfile
            self.tmp = tempfile.TemporaryDirectory()
            self.destination = self.tmp.name
            self.sketcher = Sketch()

        with it("returns an empty string when the .context directory does not exist"):
            result = self.sketcher.list_sketches(destination=self.destination)
            expect(result).to(equal(""))

        with it("returns an empty string when the .context directory exists but is empty"):
            (Path(self.destination) / ".context").mkdir(parents=True)

            result = self.sketcher.list_sketches(destination=self.destination)

            expect(result).to(equal(""))

        with it("lists every *-sketch.md file when no slug filter is given"):
            self.sketcher.save_sketch(self.destination, "alpha", "a\n")
            self.sketcher.save_sketch(self.destination, "bravo", "b\n")

            result = self.sketcher.list_sketches(destination=self.destination)

            lines = result.splitlines()
            expect(len(lines)).to(equal(2))
            expect(any("alpha-sketch.md" in line for line in lines)).to(be_true)
            expect(any("bravo-sketch.md" in line for line in lines)).to(be_true)

        with it("filters by slug when a slug is provided"):
            self.sketcher.save_sketch(self.destination, "alpha", "a\n")
            self.sketcher.save_sketch(self.destination, "bravo", "b\n")

            result = self.sketcher.list_sketches(destination=self.destination, slug="alpha")

            lines = result.splitlines()
            expect(len(lines)).to(equal(1))
            expect(all("alpha-sketch.md" in line for line in lines)).to(be_true)

    with context("sketch action body"):
        with before.each:
            self.sketcher = Sketch()
            self.body = _ActionExpander.instance().parse_body(
                Sketch.sketch, self.sketcher
            )

        with it("wires find_template and save_sketch as its tool steps"):
            expect("find_template" in self.body.tool_steps).to(be_true)
            expect("save_sketch" in self.body.tool_steps).to(be_true)

        with it("wires complete_tick after save_sketch so each sketch tick finishes a Turn"):
            steps = list(self.body.tool_steps)
            expect("complete_tick" in steps).to(be_true)
            expect("save_sketch" in steps).to(be_true)
            save_i = steps.index("save_sketch")
            expect("complete_tick" in steps[save_i:]).to(be_true)

        with it("expands prose that instructs the sketcher to persist drafts via save_sketch"):
            joined = "\n".join(self.body.prose_parts)
            expect(joined).to(contain("save_sketch"))

        with it("instructs complete_tick after every save_sketch so each tick is a Turn"):
            joined = "\n".join(self.body.prose_parts)
            expect(joined).to(contain("complete_tick"))
            expect(joined).to(contain("One save_sketch = one Turn"))
            expect(joined).to(contain("Persisting without complete_tick is a defect"))

        with it("includes the grill_with_context body in sketch"):
            joined = "\n".join(self.body.prose_parts)
            expect(joined).to(contain("(Recommended)"))
            expect(joined).to(contain("save_sketch"))
            expect(joined).to(contain("Grill the sketch plan"))


with description("a sketch action"):
    with context("that expands with context tools"):
        with it("should include the sketch session body in sketch"):
            body = _ActionExpander.instance().parse_body(Sketch.sketch, Sketch())
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("Grill the sketch plan"))
            expect(joined).to(contain("save_sketch"))

    with context("that completes a turn after every sketch tick"):
        with it("should expose complete_tick as a tool"):
            expect("complete_tick" in Sketch().tools).to(be_true)

        with it("should finish the open turn and open the next with the same action"):
            import tempfile

            from workspace.git_repo import NullGitRepo
            from workspace.workspace import ContextToolHost, Workspace

            tmp = Path(tempfile.mkdtemp(prefix="sketch-tick-"))
            git = NullGitRepo()
            workspace = Workspace(str(tmp))
            host = ContextToolHost(workspace, git=git)
            session = host.run_action("sketch-tick", goal="turn per tick", action="sketch")
            git.set_dirty(True)
            sketcher = Sketch(path=str(tmp), session="sketch-tick")
            sketcher.workspace = workspace
            before = session.open_turn.id
            result = sketcher.complete_tick(result="saved sketch draft")
            expect(result).to(equal("tick-complete"))
            expect(session.open_turn).not_to(equal(None))
            expect(session.open_turn.id).not_to(equal(before))
            expect(session.open_turn.action).to(equal("sketch"))
            expect(len(session.turns)).to(equal(1))
            expect(git.commits[0][1]).to(contain("sketch"))


with description("BaseContextTool host face for sketch"):
    with it("should not expose sketch on the host composer"):
        from context_tools.base.base_context_tool import BaseContextTool

        cls = _ToolsetLoader.instance().load(
            "context_tools.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle"
        )
        host = cls()
        expect("sketch" in host.actions).to(equal(False))
