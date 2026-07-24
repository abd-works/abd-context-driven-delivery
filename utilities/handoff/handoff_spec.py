"""BDD spec for handoff — Handoff toolset helpers and tools."""

import json
import sys
import tempfile
from datetime import date
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "contexts"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("handoff", None)

from expects import contain, equal, expect
from mamba import before, context, description, it

from handoff.handoff import (
    Handoff,
    _archive_slug,
    _collect_state,
    _context_dir,
    _grill_headings,
    _handoff_path,
    _resolve_archive_slug,
    _summarize_cdd_sketch,
)


_SAMPLE_CDD = """\
fidelity: explore
scope: Increment 1 — place order

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


with description("handoff path helpers"):
    with it("resolves .context under destination"):
        expect(str(_context_dir("sandbox/play"))).to(equal(str(Path("sandbox/play") / ".context")))

    with it("resolves dated archive under .context/handoffs"):
        expect(str(_handoff_path("sandbox/play", "handoff-2026-07-22-modules"))).to(
            equal(
                str(
                    Path("sandbox/play")
                    / ".context"
                    / "handoffs"
                    / "handoff-2026-07-22-modules.md"
                )
            )
        )

    with it("builds archive slug from date and focus"):
        expect(_archive_slug("model fidelity", today=date(2026, 7, 22))).to(
            equal("handoff-2026-07-22-model-fidelity")
        )
        expect(_archive_slug("", today=date(2026, 7, 22))).to(equal("handoff-2026-07-22"))

    with it("resolves reserved slug handoff into dated archive"):
        expect(_resolve_archive_slug(slug="handoff", today=date(2026, 7, 22))).to(
            equal("handoff-2026-07-22")
        )
        expect(_resolve_archive_slug(focus="modules", today=date(2026, 7, 22))).to(
            equal("handoff-2026-07-22-modules")
        )


with description("_summarize_cdd_sketch"):
    with it("extracts fidelity, scope, flow, open, done, and log tail"):
        summary = _summarize_cdd_sketch(_SAMPLE_CDD)
        expect(summary["fidelity"]).to(equal("explore"))
        expect(summary["scope"]).to(equal("Increment 1 — place order"))
        expect(summary["flow_status"]).to(equal("in-progress"))
        expect(summary["flow_recommend"]).to(equal("more-same-stage"))
        expect(summary["flow_next"]).to(equal("explore"))
        expect(summary["open"]).to(contain("TODO delivery picker layout  #theme-place-order"))
        expect(summary["done"]).to(contain("pass #instruct-ddd-bc"))
        expect(summary["log_tail"]).to(
            contain("explore / Increment 1 / Place New Order / pass #instruct-ddd-bc")
        )


with description("_grill_headings"):
    with it("lists ### headings"):
        text = "# Grill Answers\n\n### First\n\nbody\n\n### Second\n\nmore\n"
        expect(_grill_headings(text)).to(equal(["First", "Second"]))


with description("Handoff toolset"):
    with context("manifest signature"):
        with it("exposes resolve, collect, write tools and handoff_session action"):
            sig = Handoff.manifest.signature
            expect(sig["resolve_working_folder"]["kind"]).to(equal("tool"))
            expect(sig["collect_session_state"]["kind"]).to(equal("tool"))
            expect(sig["write_handoff"]["kind"]).to(equal("tool"))
            expect(sig["handoff_session"]["kind"]).to(equal("action"))

    with context("tools"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.destination = self.tmp.name
            self.toolset = Handoff()

        with it("resolve_working_folder creates .context and returns it"):
            path = Path(self.toolset.resolve_working_folder(self.destination))
            expect(path.is_dir()).to(equal(True))
            expect(path.name).to(equal(".context"))

        with it("collect_session_state reports sketches, grill, and cdd summary"):
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

        with it("write_handoff persists dated archive under handoffs/ and handoff-latest"):
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

        with it("write_handoff without focus still uses dated archive not handoff.md"):
            path = Path(
                self.toolset.write_handoff(
                    self.destination,
                    "# Handoff\n\nDated only.\n",
                )
            )
            expect(path.parent.name).to(equal("handoffs"))
            expect(path.name).to(equal(f"handoff-{date.today().isoformat()}.md"))

        with it("_collect_state returns None cdd when sketch missing"):
            state = _collect_state(self.destination)
            expect(state["cdd"]).to(equal(None))
