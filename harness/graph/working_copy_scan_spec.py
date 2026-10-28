"""A working copy scan reads source, not build output, test-run output, or dot-folders."""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from expects import be_above, contain, equal, expect
from mamba import after, before, context, description, it

from graph import Graph

# Five parameters, over the three limit-operation-parameters allows.
_OVER_LIMIT = "export class {name} {{\n  place(a: string, b: string, c: string, d: string, e: string): void {{}}\n}}\n"
_WITHIN_LIMIT = "export class {name} {{\n  open(a: string): void {{}}\n}}\n"
_CARD = "# {name}\n\n- **Purpose:** {name}.\n- **Seam (terms):** `{cls}`\n\n## Constraint\n\nCallers go through `{cls}`.\n"


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _working_copy() -> Path:
    root = Path(tempfile.mkdtemp(prefix="cdd-scan-"))
    _write(root, "src/orders/order.ts", _OVER_LIMIT.format(name="Order"))
    _write(root, "src/orders/.context/modules.md", _CARD.format(name="orders", cls="Order"))
    _write(root, "src/billing/invoice.ts", _WITHIN_LIMIT.format(name="Invoice"))
    _write(root, "src/billing/.context/module-context.md", _CARD.format(name="billing", cls="Invoice"))
    _write(root, "src/shared/.examples/sample.ts", _WITHIN_LIMIT.format(name="Sample"))
    _write(root, "test-results/run-1/trace/resources/trace.js", _OVER_LIMIT.format(name="TraceBundle"))
    _write(root, "playwright-report/data/report.js", _OVER_LIMIT.format(name="ReportBundle"))
    _write(root, "packages/app/dist/bundle.js", _OVER_LIMIT.format(name="DistBundle"))
    _write(root, ".claude/worktrees/copy/src/orders/order.ts", _OVER_LIMIT.format(name="WorktreeOrder"))
    return root


def _class_names(graph: Graph) -> list[str]:
    practice = graph.practice("clean_engineering")
    return sorted(node.name for node in practice.nodes.get("OoadClass", []))


def _module_names(graph: Graph) -> list[str]:
    practice = graph.practice("clean_engineering")
    return sorted(node.name for node in practice.nodes.get("Module", []))


with description("a working copy scan") as self:
    with before.all:
        self.root = _working_copy()
        self.graph = Graph()
        self.graph.load_working_copy(str(self.root), {"clean_engineering": str(self.root)}, force=True)

    with after.all:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("over build and test-run output"):
        with it("should read the source classes"):
            expect(_class_names(self.graph)).to(contain("Order", "Invoice"))

        with it("should read classes under an .examples folder"):
            expect(_class_names(self.graph)).to(contain("Sample"))

        with it("should leave test-results, playwright-report, dist, and dot-folders out"):
            names = _class_names(self.graph)
            for skipped in ("TraceBundle", "ReportBundle", "DistBundle", "WorktreeOrder"):
                expect(skipped in names).to(equal(False))

    with context("over module cards"):
        with it("should make a module of a folder with .context/modules.md or module-context.md"):
            expect(_module_names(self.graph)).to(equal(["billing", "orders"]))

        with it("should pass named-seam-and-constraint on a modules.md card"):
            returned = json.loads(self.graph.return_nodes({"types": ["Module"], "name": "orders"}))
            rows = [rule for node in returned for rule in node["rules"] if rule["name"] == "named-seam-and-constraint"]
            expect(len(rows)).to(be_above(0))
            expect({rule["status"] for rule in rows}).to(equal({"passing"}))

    with context("returning violations"):
        with it("should return only failing rule rows when the filter asks for violations"):
            returned = json.loads(self.graph.return_nodes({"practice": "clean_engineering", "violations": True}))
            expect(len(returned)).to(be_above(0))
            statuses = {rule["status"] for node in returned for rule in node["rules"]}
            expect(statuses).to(equal({"violating"}))

        with it("should keep only nodes under the given path"):
            returned = json.loads(
                self.graph.return_nodes({"practice": "clean_engineering", "violations": True, "paths": ["src/billing"]})
            )
            expect("place" in [node["name"] for node in returned]).to(equal(False))
            returned = json.loads(
                self.graph.return_nodes({"practice": "clean_engineering", "violations": True, "paths": ["src/orders"]})
            )
            expect([node["name"] for node in returned]).to(contain("place"))

    with context("loaded with a relative practice root"):
        with before.all:
            self.relative = Graph()
            cwd = os.getcwd()
            os.chdir(_REPO)
            try:
                self.relative.load_working_copy(str(self.root), {"clean_engineering": "src"}, force=True)
            finally:
                os.chdir(cwd)

        with it("should resolve the root against the folder"):
            source_root = Path(self.relative.practice("clean_engineering").source_root)
            expect(source_root).to(equal((self.root / "src").resolve()))
