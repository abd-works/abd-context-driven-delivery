"""A working copy scan reads source, not build output, test-run output, or dot-folders."""

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
from harness.installation.destination import data_of  # noqa: E402
from mamba import after, before, context, description, it

from graph import Graph

# Five parameters, over the three limit-operation-parameters allows.
_OVER_LIMIT = "export class {name} {{\n  place(a: string, b: string, c: string, d: string, e: string): void {{}}\n}}\n"
_WITHIN_LIMIT = "export class {name} {{\n  open(a: string): void {{}}\n}}\n"
_CARD = "# {name}\n\n- **Purpose:** {name}.\n- **Seam (terms):** `{cls}`\n\n## Constraint\n\nCallers go through `{cls}`.\n"
_STORY_MAP = (
    "# Story Map — Board\n\n"
    "# (E) Move Work On Board\n\n"
    "## (E) Display Board\n\n"
    "### (S) Person --> Open Board\n\n"
    "### (S) Board Pane --> Draw Columns\n"
)
_OTHER_STORY_MAP = "# (E) Ship Parcels\n\n## (E) Pack Parcels\n\n### (S) Packer --> Pack Parcel\n"
# One sub-epic's story test, in its epic's folder below the story map: every Story of the sub-epic in one file.
_STORY_TEST = (
    "from story_test import and_, but_, given, scenario, story, then, when\n"
    "\n"
    "# Epic: Display Board\n"
    "\n"
    "# Story: Open Board\n"
    'with story("Open Board"):\n'
    '    with scenario("Open the board from a chat"):\n'
    '        with given("the board is running"):\n'
    "            pass\n"
    '        with when("the Person opens the board"):\n'
    "            pass\n"
    '        with then("the board shows its columns"):\n'
    "            pass\n"
    "\n"
    "# Story: Draw Columns\n"
    'with story("Draw Columns"):\n'
    '    with scenario("Draw the five columns"):\n'
    '        with when("the Board Pane reads the board"):\n'
    "            pass\n"
    '        with then("it draws Backlog, Discovery, Specification, Implementation, and Complete"):\n'
    "            pass\n"
)
_STORY_TEST_PATH = "board/.context/move-work-on-board/display_board_story.test.py"
_STORY_MAP_DIAGRAM = (
    '<mxfile><diagram name="Story Map"><mxGraphModel><root>\n'
    '<mxCell id="0"/>\n<mxCell id="1" parent="0"/>\n'
    '<mxCell id="e1" value="Move Work On Board" style="epic;" parent="1" vertex="1"><mxGeometry x="0" y="0" width="200" height="60" as="geometry"/></mxCell>\n'
    '<mxCell id="e2" value="Display Board" style="subepic:0;" parent="1" vertex="1"><mxGeometry x="0" y="80" width="200" height="60" as="geometry"/></mxCell>\n'
    '<mxCell id="s1" value="Open Board" style="story:user;" parent="1" vertex="1"><mxGeometry x="0" y="160" width="50" height="50" as="geometry"/></mxCell>\n'
    "</root></mxGraphModel></diagram></mxfile>\n"
)


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
    _write(root, "board/.context/story-map.md", _STORY_MAP)
    _write(root, "board/.context/story-map.drawio", _STORY_MAP_DIAGRAM)
    _write(root, "parcels/.context/story-map.md", _OTHER_STORY_MAP)
    _write(root, _STORY_TEST_PATH, _STORY_TEST)
    return root


def _story_nodes(graph: Graph, name: str) -> list:
    practice = graph.practice("stories")
    return [node for node in practice.by_id.values() if node.name == name]


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
        data_of(self.graph.load_working_copy(str(self.root), {"clean_engineering": str(self.root)}, force=True))

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
            returned = data_of(self.graph.return_nodes({"types": ["Module"], "name": "orders"}))
            rows = [rule for node in returned for rule in node["rules"] if rule["name"] == "named-seam-and-constraint"]
            expect(len(rows)).to(be_above(0))
            expect({rule["status"] for rule in rows}).to(equal({"passing"}))

    with context("returning violations"):
        with it("should return only failing rule rows when the filter asks for violations"):
            returned = data_of(self.graph.return_nodes({"practice": "clean_engineering", "violations": True}))
            expect(len(returned)).to(be_above(0))
            statuses = {rule["status"] for node in returned for rule in node["rules"]}
            expect(statuses).to(equal({"violating"}))

        with it("should keep only nodes under the given path"):
            returned = data_of(self.graph.return_nodes({"practice": "clean_engineering", "violations": True, "paths": ["src/billing"]}))
            expect("place" in [node["name"] for node in returned]).to(equal(False))
            returned = data_of(self.graph.return_nodes({"practice": "clean_engineering", "violations": True, "paths": ["src/orders"]}))
            expect([node["name"] for node in returned]).to(contain("place"))

    with context("limited to the edited files"):
        with before.all:
            self.saved = self.root / ".context" / "graph.json"
            self.saved_stamp = self.saved.stat().st_mtime
            self.scoped = Graph()
            data_of(self.scoped.load_files(str(self.root), ["clean_engineering"], ["src/orders/order.ts", "src/billing"]))

        with it("should read only the classes in those files and folders"):
            expect(_class_names(self.scoped)).to(equal(["Invoice", "Order"]))

        with it("should make modules only of the folders that hold those files"):
            expect(_module_names(self.scoped)).to(equal(["billing", "orders"]))

        with it("should run the rules on those files"):
            returned = data_of(self.scoped.return_nodes({"practice": "clean_engineering", "violations": True}))
            expect([node["name"] for node in returned]).to(contain("place"))

        with it("should leave the saved graph alone"):
            expect(self.saved.stat().st_mtime).to(equal(self.saved_stamp))

    with context("limited to the loaded folder itself, named as ."):
        with before.all:
            self.whole = Graph()
            data_of(self.whole.load_files(str(self.root), ["clean_engineering"], ["."]))

        with it("should read every class in the folder"):
            expect(_class_names(self.whole)).to(equal(_class_names(self.graph)))

    with context("limited to an edited story map markdown file"):
        with before.all:
            self.story_map = Graph()
            data_of(self.story_map.load_files(str(self.root), ["stories"], ["board/.context/story-map.md"]))

        with it("should keep the story map's path from the folder on each story"):
            expect([node.source.file for node in _story_nodes(self.story_map, "Draw Columns")]).to(
                equal(["board/.context/story-map.md"])
            )

        with it("should keep the line the story's heading sits on"):
            expect([node.source.start_line for node in _story_nodes(self.story_map, "Draw Columns")]).to(equal([9]))

        with it("should keep the line the sub-epic's heading sits on"):
            expect([node.source.start_line for node in _story_nodes(self.story_map, "Display Board")]).to(equal([5]))

        with it("should read only that story map"):
            expect(_story_nodes(self.story_map, "Pack Parcel")).to(equal([]))

    with context("limited to an edited story map diagram"):
        with before.all:
            self.diagram = Graph()
            data_of(self.diagram.load_files(str(self.root), ["stories"], ["board/.context/story-map.drawio"]))

        with it("should keep the diagram's path from the folder on each story"):
            expect([node.source.file for node in _story_nodes(self.diagram, "Open Board")]).to(
                equal(["board/.context/story-map.drawio"])
            )

        with it("should keep the line the story's cell sits on"):
            expect([node.source.start_line for node in _story_nodes(self.diagram, "Open Board")]).to(equal([6]))

    # A sub-epic's story test holds its Stories' scenarios; the story map above it says which epic each Story sits under.
    with context("limited to an edited Python story test"):
        with before.all:
            self.story_test = Graph()
            data_of(self.story_test.load_files(str(self.root), ["stories"], [_STORY_TEST_PATH]))
            self.scenarios = _story_nodes(self.story_test, "Open the board from a chat")

        with it("should read its scenario under the story of the same name on the story map in a folder above it"):
            expect(len(self.scenarios)).to(equal(1))

        with it("should read the scenarios of every story in the file"):
            expect(len(_story_nodes(self.story_test, "Draw the five columns"))).to(equal(1))

        with it("should keep the story test's path on the scenario"):
            expect([node.source.file for node in self.scenarios]).to(equal([_STORY_TEST_PATH]))

        with it("should keep the line the scenario opens on"):
            expect([node.source.start_line for node in self.scenarios]).to(equal([7]))

        with it("should count the scenario on its story"):
            expect([node.get_fact("scenario_count") for node in _story_nodes(self.story_test, "Open Board")]).to(equal([1]))

    # The markdown and the diagram are two formats of one story map, so a story test's scenarios belong to both.
    with context("limited to a story map in both formats and its story test"):
        with before.all:
            self.both_formats = Graph()
            data_of(self.both_formats.load_files(
                str(self.root),
                ["stories"],
                ["board/.context/story-map.md", "board/.context/story-map.drawio", _STORY_TEST_PATH],
            ))

        with it("should count the scenario on the story in each format"):
            expect(
                sorted(node.get_fact("scenario_count") for node in _story_nodes(self.both_formats, "Open Board"))
            ).to(equal([1, 1]))

    with context("loaded with a relative practice root"):
        with before.all:
            self.relative = Graph()
            cwd = os.getcwd()
            os.chdir(_REPO)
            try:
                data_of(self.relative.load_working_copy(str(self.root), {"clean_engineering": "src"}, force=True))
            finally:
                os.chdir(cwd)

        with it("should resolve the root against the folder"):
            source_root = Path(self.relative.practice("clean_engineering").source_root)
            expect(source_root).to(equal((self.root / "src").resolve()))
