"""A refresh of the files an edit changed leaves the graph a fresh build of the edited working copy gives: the same
nodes with the same facts, the same edges, and the same violations, practice by practice. This is the differential spec
of CDR 0005 (harness/graph/.context/cdr/0005-session-graph-is-cached-and-filters-never-build.md), run against today's
``Graph.refresh``: a session graph kept between changes is only safe once each edit refreshes to what a full build reads.

Each edit runs on a throwaway copy of its project: the copy is built whole, edited, refreshed with the files the edit
changed, and built whole again from nothing; the refreshed graph must equal the second build. Every build and refresh
runs in a worker, as the cdd server runs them for a chat, so the edits run side by side."""

import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from harness.agent_tools.tool_call import ToolCall, ToolRequest
from harness.graph.graph import Graph
from harness.graph.spec_support import graph_state, state_differences
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.patterns  # noqa: F401 - registers the patterns with the graph's overlays

_REPOSITORY = Path(__file__).resolve().parents[2]
# Every practice, each read from the project's root, as a session that has them all reads them.
_EVERY_PRACTICE = {key: "." for key in ("stories", "ddd", "ux", "clean_engineering", "bdd")}
# A build for a chat's call runs in a worker process.
_IN_A_WORKER = ToolCall(request=ToolRequest(answers_a_chat=True))
# The edits run side by side, each in workers of its own.
_EDITS_AT_ONCE = 4


class _Project:
    """A project the edits are made on, copied for each edit from where it is kept, with the overlays its graph
    applies."""

    def __init__(self, copies: dict[str, str], overlays: tuple[str, ...] = (), left_out: tuple[str, ...] = ()) -> None:
        # Each path to copy, from the repository's root, by the path it takes in the copy.
        self._copies = copies
        self.overlays = list(overlays)
        # The folders, by name, a copied folder is copied without; never a cache or a saved graph.
        self._left_out = shutil.ignore_patterns("__pycache__", "node_modules", "graph.json", *left_out)

    def copied(self) -> Path:
        """A throwaway copy of the project, its folder new."""
        root = Path(tempfile.mkdtemp(prefix="cdd-graph-incremental-")) / "project"
        for target, source in self._copies.items():
            origin = _REPOSITORY / source
            if origin.is_dir():
                shutil.copytree(origin, root / target, ignore=self._left_out)
            else:
                (root / target).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(origin, root / target)
        return root

    def built(self, root: Path) -> Graph:
        """The graph of the copy at root, built whole from nothing."""
        graph = Graph()
        graph.load_working_copy(str(root), _EVERY_PRACTICE, overlays=self.overlays, force=True, call=_IN_A_WORKER)
        return graph


# The LERN sample every practice reads: TypeScript code, a markdown story test with its examples, and a server spec.
_SAMPLE = _Project({".": "harness/graph/_examples/input"}, ("lern_domain_driven",))
# A slice of this repository: a sub-epic's scenario files and Python story tests, the graph's Python code with its specs
# and its model documents, the story map, and the information architecture drawn in draw.io; the graph's app, samples,
# fixtures, and decision records are left out.
_SLICE = _Project({
    "story_tests/review-generated-work-in-file-viewer": "story_tests/review-generated-work-in-file-viewer",
    "harness/graph": "harness/graph",
    ".context/story-map.md": ".context/story-map.md",
    "harness/.context/information-architecture.drawio": "harness/.context/information-architecture.drawio",
}, left_out=("app", "_examples", "fixtures", "cdr"))


class _Edit:
    """One edit of a project's files: the text replaced in a file, a file written, a file deleted, or a file renamed;
    each names the files a refresh is given, as an action that made the edit names them."""

    def __init__(self, project: _Project, kind: str, file: str, replaced: str = "", by: str = "", renamed_to: str = "") -> None:
        self.project = project
        self.kind = kind
        self._file = file
        self._replaced = replaced
        self._by = by
        self._renamed_to = renamed_to
        # Where the refreshed graph differed from a fresh build, once the edit has run.
        self.found: dict[str, dict] = {}

    def make(self, root: Path) -> list[str]:
        """Make the edit in the copy at root; answer the files it changed, from the root."""
        path = root / self._file
        if self._renamed_to:
            path.rename(root / self._renamed_to)
            return [self._file, self._renamed_to]
        if not self._by:
            path.unlink()
            return [self._file]
        if not self._replaced:
            path.write_text(self._by, encoding="utf-8")
            return [self._file]
        text = path.read_text(encoding="utf-8")
        if self._replaced not in text:
            raise AssertionError(f"{self._file} no longer holds {self._replaced!r}; the edit '{self.kind}' needs a new place")
        path.write_text(text.replace(self._replaced, self._by), encoding="utf-8")
        return [self._file]

    def run(self) -> None:
        """Build a copy of the project whole, make the edit, refresh the graph with the files it changed, and keep where
        the refreshed graph differs from a fresh build of the edited copy, practice by practice."""
        root = self.project.copied()
        try:
            held = self.project.built(root)
            held.refresh(self.make(root), _IN_A_WORKER)
            self.found = state_differences(graph_state(held), graph_state(self.project.built(root)))
        finally:
            shutil.rmtree(root.parent, ignore_errors=True)


_CHANGE_TYPESCRIPT_CLASS = _Edit(_SAMPLE, "change a TypeScript class", "src/account-credentials/account-credentials.ts",
                                 "  async register(): Promise<void> {", "  forget(): void {}\n\n  async register(): Promise<void> {")
_RENAME_TYPESCRIPT_OPERATION_STEPS_INVOKE = _Edit(_SAMPLE, "rename an operation a story's steps invoke", "src/account-credentials/account-credentials.ts",
                                                  "  async register(): Promise<void> {", "  async signUp(): Promise<void> {")
_ADD_TYPESCRIPT_FILE = _Edit(_SAMPLE, "add a TypeScript file", "src/customer/loyalty.ts",
                             by="export class Loyalty {\n  points(customer: string): string { return customer; }\n}\n")
_DELETE_TYPESCRIPT_FILE = _Edit(_SAMPLE, "delete a TypeScript file", "src/onboarding/onboarding-step.ts")
_RENAME_TYPESCRIPT_FILE = _Edit(_SAMPLE, "rename a TypeScript file", "src/customer/customer.ts", renamed_to="src/customer/client.ts")
_CHANGE_BOUNDED_CONTEXT_HEADING = _Edit(_SAMPLE, "change a bounded context's heading", "src/.context/bounded-context.md", "# bounded context", "# onboarding")
_CHANGE_SAMPLE_SCENARIO_FILE = _Edit(_SAMPLE, "change a story's scenario file", "tests/onboard-a-customer/authenticate-user/authenticate_user_story.test.md",
                                     "| account credentials | missing email |", "| account credentials | blank email |")
_CHANGE_OBSERVED_EXAMPLES = _Edit(_SAMPLE, "change the examples a story's steps observe",
                                  "tests/onboard-a-customer/authenticate-user/examples/account-credentials.examples.ts", "missing email", "blank email")

_CHANGE_PYTHON_CLASS = _Edit(_SLICE, "change a Python class", "harness/graph/load_scope.py",
                             "    def also_naming(", "    def is_empty(self) -> bool:\n        return not self.named\n\n    def also_naming(")
_ADD_PYTHON_FILE = _Edit(_SLICE, "add a Python file", "harness/graph/graph_cache.py",
                         by='"""A cache."""\n\n\nclass GraphCache:\n    def keep(self, graph: str) -> str:\n        return graph\n')
_DELETE_PYTHON_FILE = _Edit(_SLICE, "delete a Python file", "harness/graph/node_metric.py")
_RENAME_PYTHON_FILE = _Edit(_SLICE, "rename a Python file", "harness/graph/location.py", renamed_to="harness/graph/located.py")
_CHANGE_MODEL_HEADING_CODE_LINKS_TO = _Edit(_SLICE, "change a class heading code links to in a model document", "harness/graph/.context/graph-model.md",
                                            "## ModelChildren : list", "## ModelKids : list")
_RENAME_PYTHON_OPERATION_STEPS_INVOKE = _Edit(_SLICE, "rename an operation a story's steps invoke", "harness/graph/graph_reads.py",
                                              "    def load(self, force: bool, apart: bool)", "    def load_all(self, force: bool, apart: bool)")
_CHANGE_SLICE_SCENARIO_FILE = _Edit(_SLICE, "change a story's scenario file",
                                    "story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md",
                                    "*Then* the file bar is 420 pixels wide\n", "*Then* the file bar is 420 pixels wide and its folders stay open\n")
_CHANGE_PYTHON_SPEC = _Edit(_SLICE, "change a Python spec", "harness/graph/file_lines_spec.py",
                            'with it("should close where the file closes it now in a later build"):',
                            'with it("should close where the file closes the call now in a later build"):')
_RENAME_DRAWIO_SCREEN = _Edit(_SLICE, "rename a screen stories are shown on, in draw.io", "harness/.context/information-architecture.drawio",
                              'value="Chat Bar"', 'value="Chat Strip"')

# Every edit, each made on a copy of its own.
_EDITS = (
    _CHANGE_TYPESCRIPT_CLASS, _RENAME_TYPESCRIPT_OPERATION_STEPS_INVOKE, _ADD_TYPESCRIPT_FILE, _DELETE_TYPESCRIPT_FILE,
    _RENAME_TYPESCRIPT_FILE, _CHANGE_BOUNDED_CONTEXT_HEADING, _CHANGE_SAMPLE_SCENARIO_FILE, _CHANGE_OBSERVED_EXAMPLES,
    _CHANGE_PYTHON_CLASS, _ADD_PYTHON_FILE, _DELETE_PYTHON_FILE, _RENAME_PYTHON_FILE, _CHANGE_MODEL_HEADING_CODE_LINKS_TO,
    _RENAME_PYTHON_OPERATION_STEPS_INVOKE, _CHANGE_SLICE_SCENARIO_FILE, _CHANGE_PYTHON_SPEC, _RENAME_DRAWIO_SCREEN,
)


with description("a graph refreshed with the files an edit changed"):
    with before.all:
        with ThreadPoolExecutor(_EDITS_AT_ONCE) as editing:
            list(editing.map(_Edit.run, _EDITS))

    with context("of the LERN sample, which every practice reads in TypeScript and markdown"):
        with it("should hold what a fresh build holds after a TypeScript class changes"):
            expect(_CHANGE_TYPESCRIPT_CLASS.found).to(equal({}))

        with it("should hold what a fresh build holds after an operation a story's steps invoke is renamed"):
            expect(_RENAME_TYPESCRIPT_OPERATION_STEPS_INVOKE.found).to(equal({}))

        with it("should hold what a fresh build holds after a TypeScript file is added"):
            expect(_ADD_TYPESCRIPT_FILE.found).to(equal({}))

        with it("should hold what a fresh build holds after a TypeScript file is deleted"):
            expect(_DELETE_TYPESCRIPT_FILE.found).to(equal({}))

        with it("should hold what a fresh build holds after a TypeScript file is renamed"):
            expect(_RENAME_TYPESCRIPT_FILE.found).to(equal({}))

        with it("should hold what a fresh build holds after a bounded context's heading changes"):
            expect(_CHANGE_BOUNDED_CONTEXT_HEADING.found).to(equal({}))

        with it("should hold what a fresh build holds after a story's scenario file changes"):
            expect(_CHANGE_SAMPLE_SCENARIO_FILE.found).to(equal({}))

        with it("should hold what a fresh build holds after the examples a story's steps observe change"):
            expect(_CHANGE_OBSERVED_EXAMPLES.found).to(equal({}))

    with context("of a slice of this repository, read in Python, markdown, and draw.io"):
        with it("should hold what a fresh build holds after a Python class changes"):
            expect(_CHANGE_PYTHON_CLASS.found).to(equal({}))

        with it("should hold what a fresh build holds after a Python file is added"):
            expect(_ADD_PYTHON_FILE.found).to(equal({}))

        with it("should hold what a fresh build holds after a Python file is deleted"):
            expect(_DELETE_PYTHON_FILE.found).to(equal({}))

        with it("should hold what a fresh build holds after a Python file is renamed"):
            expect(_RENAME_PYTHON_FILE.found).to(equal({}))

        with it("should hold what a fresh build holds after a class heading code links to changes in a model document"):
            expect(_CHANGE_MODEL_HEADING_CODE_LINKS_TO.found).to(equal({}))

        with it("should hold what a fresh build holds after an operation a story's steps invoke is renamed"):
            expect(_RENAME_PYTHON_OPERATION_STEPS_INVOKE.found).to(equal({}))

        with it("should hold what a fresh build holds after a story's scenario file changes"):
            expect(_CHANGE_SLICE_SCENARIO_FILE.found).to(equal({}))

        with it("should hold what a fresh build holds after a Python spec changes"):
            expect(_CHANGE_PYTHON_SPEC.found).to(equal({}))

        with it("should hold what a fresh build holds after a screen stories are shown on is renamed in draw.io"):
            expect(_RENAME_DRAWIO_SCREEN.found).to(equal({}))
