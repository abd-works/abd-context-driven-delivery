"""BDD spec for @record_decisions decorator + RecordDecisions toolset + manifest chain."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("record_decisions", None)

from expects import be_true, contain, equal, expect, raise_error
from mamba import before, context, description, it

from primitives.actions.action import _ActionExpander, _action_wrapper_names
from record_decisions import RecordDecisions, record_decisions
from record_decisions.examples.demo import DemoRecord, DemoStack


with description("@record_decisions decorator"):
    with context("applied to an @action method"):
        with it("marks the function with _record_decisions_wrapped"):
            expect(getattr(DemoRecord.generate, "_record_decisions_wrapped", False)).to(be_true)

        with it("registers the wrapper name in _action_wrappers"):
            names = _action_wrapper_names(DemoRecord.generate)
            expect(list(names)).to(equal(["record_decisions"]))

    with context("applied to a non-@action function"):
        with it("raises TypeError with a helpful message"):
            def _bare(): pass
            expect(lambda: record_decisions(_bare)).to(
                raise_error(TypeError, contain("must decorate an @action method"))
            )


with description("_ActionExpander integration for @record_decisions"):
    with it("prepends record_decisions_session's real instructions before the base action"):
        demo = DemoRecord()
        body = _ActionExpander.instance().parse_body(DemoRecord.generate, demo)
        joined = "\n".join(body.prose_parts)
        expect(joined).to(contain("Context Decision Record"))
        cdr_pos = joined.find("Context Decision Record")
        base_pos = joined.find("Demo record_decisions base body")
        expect(cdr_pos < base_pos).to(be_true)

    with it("preserves the original action docstring after the chained action instructions"):
        demo = DemoRecord()
        body = _ActionExpander.instance().parse_body(DemoRecord.generate, demo)
        joined = "\n".join(body.prose_parts)
        expect(joined).to(contain("Demo record_decisions base body"))


with description("stacked decorators"):
    with context("when two wrappers are declared in top-down order"):
        with it("lists wrapper names in declaration order (outermost first)"):
            names = _action_wrapper_names(DemoStack.generate)
            expect(list(names)).to(equal(["stub_outer", "record_decisions"]))

        with it("expands the outermost wrapper's instructions before the inner wrapper's"):
            demo = DemoStack()
            body = _ActionExpander.instance().parse_body(DemoStack.generate, demo)
            joined = "\n".join(body.prose_parts)
            outer_pos = joined.find("Stub outer wrapper")
            cdr_pos = joined.find("Context Decision Record")
            expect(outer_pos < cdr_pos).to(be_true)


with description("manifest chain field"):
    with it("exposes wrapper names on a decorated action"):
        entry = DemoStack.manifest.signature["generate"]
        expect(entry["kind"]).to(equal("action"))
        expect(entry.get("chain")).to(equal(["stub_outer", "record_decisions"]))

    with it("omits the chain field when no wrappers are declared"):
        entry = DemoRecord.manifest.signature["ping"]
        expect(entry["kind"]).to(equal("action"))
        expect(entry.get("chain")).to(equal(None))


with description("RecordDecisions toolset"):
    with context("manifest signature"):
        with it("exposes read_cdr_format, list_cdrs, write_cdr as tools"):
            sig = RecordDecisions.manifest.signature
            expect(sig["read_cdr_format"]["kind"]).to(equal("tool"))
            expect(sig["list_cdrs"]["kind"]).to(equal("tool"))
            expect(sig["write_cdr"]["kind"]).to(equal("tool"))

        with it("exposes record_decisions_session as an action referencing its inner tools"):
            entry = RecordDecisions.manifest.signature["record_decisions_session"]
            expect(entry["kind"]).to(equal("action"))
            expect(entry["tools"]).to(equal(["read_cdr_format", "list_cdrs", "write_cdr"]))

    with context("write_cdr tool"):
        with before.each:
            import tempfile
            self.tmp = tempfile.TemporaryDirectory()
            self.root = self.tmp.name
            self.recorder = RecordDecisions()

        with it("writes to .context/cdr/0001-{slug}.md under the root"):
            path = self.recorder.write_cdr(
                root=self.root,
                slug="event-sourced-orders",
                content="# Event-sourced orders\n\nWe chose event sourcing for the write model.\n",
            )
            resolved = Path(path)
            expect(resolved.is_file()).to(be_true)
            expect(resolved.name).to(equal("0001-event-sourced-orders.md"))
            expect(resolved.parent.name).to(equal("cdr"))
            expect(resolved.parent.parent.name).to(equal(".context"))
            expect(resolved.read_text(encoding="utf-8")).to(contain("event sourcing"))

        with it("creates .context/cdr/ lazily"):
            cdr_dir = Path(self.root) / ".context" / "cdr"
            expect(cdr_dir.exists()).to(equal(False))
            self.recorder.write_cdr(self.root, "first-decision", "# First\n\nBody.\n")
            expect(cdr_dir.is_dir()).to(be_true)

        with it("increments the sequential number for subsequent CDRs"):
            self.recorder.write_cdr(self.root, "alpha", "# Alpha\n\nA.\n")
            path = self.recorder.write_cdr(self.root, "bravo", "# Bravo\n\nB.\n")
            expect(Path(path).name).to(equal("0002-bravo.md"))

    with context("list_cdrs tool"):
        with before.each:
            import tempfile
            self.tmp = tempfile.TemporaryDirectory()
            self.root = self.tmp.name
            self.recorder = RecordDecisions()

        with it("returns an empty string when .context/cdr does not exist"):
            expect(self.recorder.list_cdrs(self.root)).to(equal(""))

        with it("lists every CDR markdown file"):
            self.recorder.write_cdr(self.root, "alpha", "# Alpha\n\nA.\n")
            self.recorder.write_cdr(self.root, "bravo", "# Bravo\n\nB.\n")
            lines = self.recorder.list_cdrs(self.root).splitlines()
            expect(len(lines)).to(equal(2))
            expect(any("0001-alpha.md" in line for line in lines)).to(be_true)
            expect(any("0002-bravo.md" in line for line in lines)).to(be_true)

    with context("read_cdr_format tool"):
        with it("returns the CDR format guidance"):
            content = RecordDecisions().read_cdr_format()
            expect(content).to(contain("When to offer a CDR"))
            expect(content).to(contain(".context/cdr/"))
