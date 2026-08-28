"""BDD spec for utilities/handoff/handoff.py – Handoff toolset.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""

import json
import sys
import tempfile
from datetime import date
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("handoff", None)

from expects import be_none, contain, equal, expect
from mamba import before, context, description, it

from handoff.handoff import Handoff
from primitives.actions.action import _ActionExpander

# Module-level helper for pure-function tests
_h = Handoff()


_SAMPLE_CDD = """\
fidelity: explore
scope: Increment 1 - place order

flow:
  status: in-progress
  recommend: more-same-stage
  next: explore
  note: screens and stories still need to match
  open:
    - TODO delivery picker layout  #theme-place-order
    - doing instruct ux mockup     #instruct-ux
  done:
    - pass #instruct-ddd-bc

=========
theme: Place New Order
=========

## log
- explore / Increment 1 / Place New Order / pass #instruct-ddd-bc
"""


with description("a handoff archive path"):
    with it("should resolve .context under destination"):
        expect(str(_h._context_dir("sandbox/play"))).to(equal(str(Path("sandbox/play") / ".context")))

    with it("should write handoff files into a sprint folder not parent .context"):
        sprint = Path("/work/.context/sessions/my-sprint")
        expect(str(_h._write_dir(str(sprint)))).to(equal(str(sprint)))
        expect(str(_h._latest_handoff_path(str(sprint)))).to(
            equal(str(sprint / "handoff-latest.md"))
        )

    with it("should resolve dated archive under .context/handoffs"):
        expect(str(_h._handoff_path("sandbox/play", "handoff-2026-07-22-modules"))).to(
            equal(
                str(
                    Path("sandbox/play")
                    / ".context"
                    / "handoffs"
                    / "handoff-2026-07-22-modules.md"
                )
            )
        )

    with it("should build archive slug from date and focus"):
        expect(_h._archive_slug("model fidelity", today=date(2026, 7, 22))).to(
            equal("handoff-2026-07-22-model-fidelity")
        )
        expect(_h._archive_slug("", today=date(2026, 7, 22))).to(equal("handoff-2026-07-22"))

    with it("should resolve a reserved slug into a dated archive"):
        expect(_h._resolve_archive_slug(slug="handoff", today=date(2026, 7, 22))).to(
            equal("handoff-2026-07-22")
        )
        expect(_h._resolve_archive_slug(focus="modules", today=date(2026, 7, 22))).to(
            equal("handoff-2026-07-22-modules")
        )


with description("a CDD sketch summary"):
    with it("should extract fidelity, scope, flow, open, done, and log tail"):
        summary = _h._summarize_cdd_sketch(_SAMPLE_CDD)
        expect(summary["fidelity"]).to(equal("explore"))
        expect(summary["scope"]).to(equal("Increment 1 - place order"))
        expect(summary["flow_status"]).to(equal("in-progress"))
        expect(summary["flow_recommend"]).to(equal("more-same-stage"))
        expect(summary["flow_next"]).to(equal("explore"))
        expect(summary["open"]).to(contain("TODO delivery picker layout  #theme-place-order"))
        expect(summary["done"]).to(contain("pass #instruct-ddd-bc"))
        expect(summary["log_tail"]).to(
            contain("explore / Increment 1 / Place New Order / pass #instruct-ddd-bc")
        )


with description("a grill-answers heading list"):
    with it("should list ### headings"):
        text = "# Grill Answers\n\n### First\n\nbody\n\n### Second\n\nmore\n"
        expect(_h._grill_headings(text)).to(equal(["First", "Second"]))


with description("the Handoff compact action"):
    with context("that has its manifest loaded"):
        with it("should expose resolve, collect, write, compact tools and the handoff_session action"):
            sig = Handoff.manifest.signature
            expect(sig["resolve_working_folder"]["kind"]).to(equal("tool"))
            expect(sig["collect_session_state"]["kind"]).to(equal("tool"))
            expect(sig["write_handoff"]["kind"]).to(equal("tool"))
            expect(sig["compact_handoff"]["kind"]).to(equal("tool"))
            expect(sig["handoff_session"]["kind"]).to(equal("action"))

        with it("should call compact_handoff when compacting a session"):
            tools = Handoff.manifest.signature["handoff_session"]["tools"]
            expect(tools).to(equal(["compact_handoff"]))

        with it("should not expose lifecycle begin or end"):
            sig = Handoff.manifest.signature
            expect("begin" in sig).to(equal(False))
            expect("end" in sig).to(equal(False))

        with it("should tell the agent not to open a session"):
            toolset = Handoff()
            prose = "\n".join(
                _ActionExpander.instance().parse_body(type(toolset).handoff_session, toolset).prose_parts
            )
            expect(prose).to(contain("Do not open a session"))

    with context("that is asked to resolve, collect, or write"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.destination = self.tmp.name
            self.toolset = Handoff()

        with it("should create .context and return its path when resolving the working folder"):
            path = Path(self.toolset.resolve_working_folder(self.destination))
            expect(path.is_dir()).to(equal(True))
            expect(path.name).to(equal(".context"))

        with it("should report sketches, grill headings, and cdd summary when collecting state"):
            context_dir = Path(self.destination) / ".context"
            context_dir.mkdir()
            (context_dir / "ux-sketch.md").write_text("ux draft", encoding="utf-8")
            (context_dir / "grill-answers.md").write_text(
                "# Grill Answers\n\n### Seam ownership\n\nOwned by ordering.\n",
                encoding="utf-8",
            )
            (context_dir / "cdd-sketch.md").write_text(_SAMPLE_CDD, encoding="utf-8")
            state = json.loads(self.toolset.collect_session_state(self.destination))
            expect(state["grill_answers_exists"]).to(equal(True))
            expect(state["grill_headings"]).to(contain("Seam ownership"))
            expect(state["cdd"]["fidelity"]).to(equal("explore"))
            expect(any(p.endswith("ux-sketch.md") for p in state["sketches"])).to(equal(True))

        with it("should persist a dated archive under handoffs/ and update handoff-latest when writing"):
            path = Path(
                self.toolset.write_handoff(
                    self.destination,
                    "# Handoff\n\nResume here.\n",
                    focus="modules",
                )
            )
            expect(path.is_file()).to(equal(True))
            expect(path.parent.name).to(equal("handoffs"))
            expect(path.name.startswith("handoff-")).to(equal(True))
            expect(path.name).to(contain("modules"))
            expect(path.name).not_to(equal("handoff.md"))
            latest = Path(self.destination) / ".context" / "handoff-latest.md"
            expect(latest.is_file()).to(equal(True))
            expect(latest.parent.name).not_to(equal("handoffs"))
            expect(latest.read_text(encoding="utf-8")).to(contain("Resume here"))

        with it("should use a dated archive slug even without focus when writing"):
            path = Path(
                self.toolset.write_handoff(
                    self.destination,
                    "# Handoff\n\nDated only.\n",
                )
            )
            expect(path.parent.name).to(equal("handoffs"))
            expect(path.name).to(equal(f"handoff-{date.today().isoformat()}.md"))

        with it("should return None for cdd when sketch is missing"):
            state = self.toolset._collect_state(self.destination)
            expect(state["cdd"]).to(equal(None))

        with it("should find cdd-sketch in parent .context when destination is a sprint folder"):
            sprint = Path(self.destination) / ".context" / "sessions" / "my-sprint"
            sprint.mkdir(parents=True)
            parent_ctx = sprint.parent.parent
            (parent_ctx / "cdd-sketch.md").write_text(_SAMPLE_CDD, encoding="utf-8")
            state = self.toolset._collect_state(str(sprint))
            expect(state["cdd"]["fidelity"]).to(equal("explore"))

        with it("should render and write a structured handoff in one compact_handoff call"):
            context_dir = Path(self.destination) / ".context"
            context_dir.mkdir()
            (context_dir / "cdd-sketch.md").write_text(_SAMPLE_CDD, encoding="utf-8")
            path = Path(self.toolset.compact_handoff(self.destination, next_focus="modules"))
            expect(path.is_file()).to(equal(True))
            content = path.read_text(encoding="utf-8")
            expect("## Resume" in content).to(equal(True))
            expect("## CDD progress" in content).to(equal(True))
            expect("modules" in path.name).to(equal(True))
            latest = context_dir / "handoff-latest.md"
            expect(latest.is_file()).to(equal(True))
            expect(latest.read_text(encoding="utf-8")).to(equal(content))

        with it("should not open a work session when none is open"):
            expect(self.toolset.workspace.current_work_session).to(be_none)
