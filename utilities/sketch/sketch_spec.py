"""BDD spec for Sketcher toolset + ActionExpander integration."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("sketch", None)

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

from primitives.actions.action import _ActionExpander
from sketch import Sketcher


with description("Sketcher toolset"):
    with context("manifest signature"):
        with it("exposes find_template, save_sketch, list_sketches as tools"):
            sig = Sketcher.manifest.signature
            expect(sig["find_template"]["kind"]).to(equal("tool"))
            expect(sig["save_sketch"]["kind"]).to(equal("tool"))
            expect(sig["list_sketches"]["kind"]).to(equal("tool"))

        with it("exposes sketch_session as an action with find_template and save_sketch"):
            entry = Sketcher.manifest.signature["sketch_session"]
            expect(entry["kind"]).to(equal("action"))
            expect(entry["tools"]).to(equal(["find_template", "save_sketch"]))
            expect(entry.get("chain")).to(equal(None))

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
            self.destination = self.tmp.name
            self.sketcher = Sketcher()

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
            self.sketcher = Sketcher()

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

    with context("sketch_session action body"):
        with before.each:
            self.sketcher = Sketcher()
            self.body = _ActionExpander.instance().parse_body(
                Sketcher.sketch_session, self.sketcher
            )

        with it("wires find_template and save_sketch as its tool steps"):
            expect("find_template" in self.body.tool_steps).to(be_true)
            expect("save_sketch" in self.body.tool_steps).to(be_true)

        with it("expands prose that instructs the sketcher to persist drafts via save_sketch"):
            joined = "\n".join(self.body.prose_parts)
            expect(joined).to(contain("save_sketch"))

        with it("calls grill_with_context in-method then owns sketch show/persist cadence"):
            joined = "\n".join(self.body.prose_parts)
            expect(joined).to(contain("(Recommended)"))
            expect(joined).to(contain("save_sketch"))
            expect(joined).to(contain("Grill the sketch plan"))
