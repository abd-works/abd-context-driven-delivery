"""BDD spec for sketch — @sketch decorator + Sketcher toolset + ActionExpander integration."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
sys.modules.pop("sketch", None)

from expects import be_true, contain, equal, expect, raise_error
from mamba import before, context, description, it

from action.action import ActionExpander, action
from sketch import Sketcher, sketch
from sketch.examples.demo import Demo
from tools.tool import tool, toolset


with description("@sketch decorator"):
    with context("applied to an @action method"):
        with it("marks the function with _sketch_wrapped"):
            expect(getattr(Demo.generate, "_sketch_wrapped", False)).to(be_true)

        with it("registers 'sketch' as the wrapper name for manifest chain exposure"):
            from action.action import action_wrapper_names
            names = action_wrapper_names(Demo.generate)
            expect(list(names)).to(equal(["sketch"]))

        with it("captures the module directory as agent_dir and surfaces it in the manifest chain entry"):
            entry = Demo.manifest.signature["generate"]
            chain = entry["chain"]
            sketch_entry = next((c for c in chain if isinstance(c, dict) and c.get("name") == "sketch"), None)
            expect(sketch_entry).not_to(equal(None))
            expect("agent_dir" in sketch_entry).to(be_true)
            expect(sketch_entry["agent_dir"]).to(contain("sketch"))

    with context("applied to a non-@action function"):
        with it("raises TypeError with a helpful message"):
            def _bare(): pass
            expect(lambda: sketch(_bare)).to(
                raise_error(TypeError, contain("must decorate an @action method"))
            )


with description("ActionExpander integration"):
    with context("when expanding a @sketch-wrapped @action"):
        with it("prepends sketch_session's real instructions before the base action"):
            demo = Demo()
            body = ActionExpander.instance().parse_body(Demo.generate, demo)
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("sketch"))
            sketch_pos = joined.find("sketch")
            base_pos = joined.find("Base generate action body")
            expect(sketch_pos < base_pos).to(be_true)

        with it("preserves the original action docstring after the chained action instructions"):
            demo = Demo()
            body = ActionExpander.instance().parse_body(Demo.generate, demo)
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("Base generate action body"))

        with it("preserves original tool steps on the base action"):
            demo = Demo()
            body = ActionExpander.instance().parse_body(Demo.generate, demo)
            expect("do_thing" in body.tool_steps).to(be_true)


with description("Sketcher toolset"):
    with context("manifest signature"):
        with it("exposes find_template, save_sketch, list_sketches as tools"):
            sig = Sketcher.manifest.signature
            expect(sig["find_template"]["kind"]).to(equal("tool"))
            expect(sig["save_sketch"]["kind"]).to(equal("tool"))
            expect(sig["list_sketches"]["kind"]).to(equal("tool"))

        with it("exposes sketch_session as an action referencing its inner tools"):
            entry = Sketcher.manifest.signature["sketch_session"]
            expect(entry["kind"]).to(equal("action"))
            expect(entry["tools"]).to(equal(["find_template", "save_sketch"]))

    with context("find_template tool"):
        with it("falls back to the default template when no agent_dir template exists"):
            sketcher = Sketcher()
            content = sketcher.find_template(agent_dir="")
            expect(content).to(contain("terse-indent notation"))

        with it("returns the agent's own sketch-template.* when the directory contains one"):
            import tempfile
            with tempfile.TemporaryDirectory() as agent_dir:
                template_path = Path(agent_dir) / "sketch-template.md"
                template_path.write_text("# demo agent template\nrough shape\n", encoding="utf-8")
                sketcher = Sketcher()
                content = sketcher.find_template(agent_dir=agent_dir)
                expect(content).to(contain("demo agent template"))

        with it("falls back to the default when agent_dir is set but the directory is missing"):
            sketcher = Sketcher()
            content = sketcher.find_template(agent_dir="does/not/exist")
            expect(content).to(contain("terse-indent notation"))

    with context("save_sketch tool"):
        with before.each:
            import tempfile
            self.tmp = tempfile.TemporaryDirectory()
            self.workspace = self.tmp.name
            self.sketcher = Sketcher()

        with it("writes to .context/sketches/{slug}-{fidelity}.sketch.md under the workspace root"):
            path = self.sketcher.save_sketch(
                workspace_root=self.workspace,
                slug="demo-class",
                fidelity="language",
                content="thing : base thing\n  sub thing\n",
            )
            resolved = Path(path)
            expect(resolved.is_file()).to(be_true)
            expect(resolved.name).to(equal("demo-class-language.sketch.md"))
            expect(resolved.parent.name).to(equal("sketches"))
            expect(resolved.read_text(encoding="utf-8")).to(contain("thing : base thing"))

        with it("creates the .context/sketches/ directory when it does not exist"):
            sketches_dir = Path(self.workspace) / ".context" / "sketches"
            expect(sketches_dir.exists()).to(equal(False))

            self.sketcher.save_sketch(
                workspace_root=self.workspace,
                slug="fresh-class",
                fidelity="language",
                content="rough shape\n",
            )

            expect(sketches_dir.is_dir()).to(be_true)

        with it("overwrites an existing sketch at the same slug and fidelity"):
            self.sketcher.save_sketch(
                workspace_root=self.workspace,
                slug="mutable-class",
                fidelity="model",
                content="first draft\n",
            )
            path = self.sketcher.save_sketch(
                workspace_root=self.workspace,
                slug="mutable-class",
                fidelity="model",
                content="second draft\n",
            )
            expect(Path(path).read_text(encoding="utf-8")).to(equal("second draft\n"))

        with it("returns the resolved sketch path as a string"):
            path = self.sketcher.save_sketch(
                workspace_root=self.workspace,
                slug="typed-class",
                fidelity="specification",
                content="typed shape\n",
            )
            expect(isinstance(path, str)).to(be_true)
            expect(path).to(contain("typed-class-specification.sketch.md"))

    with context("list_sketches tool"):
        with before.each:
            import tempfile
            self.tmp = tempfile.TemporaryDirectory()
            self.workspace = self.tmp.name
            self.sketcher = Sketcher()

        with it("returns an empty string when the sketches directory does not exist"):
            result = self.sketcher.list_sketches(workspace_root=self.workspace)
            expect(result).to(equal(""))

        with it("returns an empty string when the sketches directory exists but is empty"):
            (Path(self.workspace) / ".context" / "sketches").mkdir(parents=True)

            result = self.sketcher.list_sketches(workspace_root=self.workspace)

            expect(result).to(equal(""))

        with it("lists every *.sketch.md file when no slug filter is given"):
            self.sketcher.save_sketch(self.workspace, "alpha", "language", "a\n")
            self.sketcher.save_sketch(self.workspace, "bravo", "model", "b\n")

            result = self.sketcher.list_sketches(workspace_root=self.workspace)

            lines = result.splitlines()
            expect(len(lines)).to(equal(2))
            expect(any("alpha-language.sketch.md" in line for line in lines)).to(be_true)
            expect(any("bravo-model.sketch.md" in line for line in lines)).to(be_true)

        with it("filters by slug prefix when a slug is provided"):
            self.sketcher.save_sketch(self.workspace, "alpha", "language", "a\n")
            self.sketcher.save_sketch(self.workspace, "alpha", "model", "am\n")
            self.sketcher.save_sketch(self.workspace, "bravo", "language", "b\n")

            result = self.sketcher.list_sketches(workspace_root=self.workspace, slug="alpha")

            lines = result.splitlines()
            expect(len(lines)).to(equal(2))
            expect(all("alpha-" in line for line in lines)).to(be_true)

    with context("sketch_session action body"):
        with before.each:
            self.sketcher = Sketcher()
            self.body = ActionExpander.instance().parse_body(
                Sketcher.sketch_session, self.sketcher
            )

        with it("wires find_template and save_sketch as its tool steps"):
            expect(list(self.body.tool_steps)).to(equal(["find_template", "save_sketch"]))

        with it("expands prose that describes the interactive grill loop"):
            joined = "\n".join(self.body.prose_parts)
            expect(joined).to(contain("grill"))

        with it("expands prose that instructs the sketcher to persist only after user confirmation"):
            joined = "\n".join(self.body.prose_parts)
            expect(joined).to(contain("save_sketch"))
