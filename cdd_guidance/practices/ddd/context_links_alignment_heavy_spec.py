"""The callouts of a domain's files against its graph, on a real project: each bounded context's own file beside the
domain model, diagnosed by the session as the Files app's graph view reads them. Heavy: every example reads the real
graph of a git project made for it."""
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect  # noqa: E402
from mamba import after, before, context, description, it  # noqa: E402

import cdd_guidance.actions  # noqa: E402, F401 - registers the actions with the action catalogue
import cdd_guidance.practices  # noqa: E402, F401 - registers the practices with the practice catalogue
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap  # noqa: E402
from space.session import Sessions  # noqa: E402
from cdd_guidance.align.format_alignment import SessionAlignment  # noqa: E402
from space.session.spec_support.throwaway_project import ExampleHome  # noqa: E402

_MODEL = ".context/domain-model.md"
_MODEL_LINKED = "../../.context/domain-model.md"
_DOMAIN_MODEL = """# Domain Model — Bookshop

## Ordering | custom

### Cart

A cart holds one line per book.

#### Cart <<Aggregate Root>> <<Entity>>

------
+ cartId: CartId
----
+ total(): Money

### Order

An order is a cart a customer submitted.

#### Order <<Aggregate Root>> <<Entity>>

------
+ orderId: OrderId
----
+ submit(): void

## Catalogue | custom

### Book

#### Book <<Aggregate Root>> <<Entity>>

------
+ isbn: Isbn
----
+ price(): Money
"""
# Each context's own file as it was written before the link: its aggregates named in plain words.
_CONTEXT_FILES = {
    "ordering": "# Ordering\n\nWhere a customer fills a cart and checks out an order.\n\nAggregates:\n- Cart\n- Order\n\nCart → Catalogue · Book\n",
    "catalogue": "# Catalogue\n\nThe books the shop sells.\n\nAggregates:\n- Book\n",
}


def _project() -> Path:
    """A git project holding the domain model and each context's own file."""
    project = Path(tempfile.mkdtemp(prefix="cdd-context-links-"))
    subprocess.run(["git", "init", "-b", "main"], cwd=project, capture_output=True, text=True, check=True)
    (project / ".context").mkdir()
    (project / _MODEL).write_text(_DOMAIN_MODEL, encoding="utf-8")
    for folder, text in _CONTEXT_FILES.items():
        (project / folder / ".context").mkdir(parents=True)
        (project / folder / ".context" / "bounded-context.md").write_text(text, encoding="utf-8")
    return project


def _link_aggregates(project: Path) -> None:
    """Write each context's own file again from the domain model, naming its aggregates as links."""
    model = MarkdownBoundedContextMap().parse((project / _MODEL).read_text(encoding="utf-8"))
    for described in model.every_context:
        file = project / described.name.lower() / ".context" / "bounded-context.md"
        file.write_text(described.context_file(_MODEL_LINKED, file.read_text(encoding="utf-8")), encoding="utf-8")


def _gaps(alignment: SessionAlignment, kind: str) -> list[str]:
    return sorted(gap.file for gap in alignment.diagnose().gaps if gap.kind == kind)


with description("a session's diagnosis of a domain whose bounded contexts each have their own file") as self:
    with before.each:
        self.home = ExampleHome()
        self.project = _project()
        Sessions(self.project).switch("bookshop", self.project)
        session = Sessions(self.project).current()
        for practice in session.own_practices.values():
            practice.enable(practice.name == "ddd")
        self.alignment = SessionAlignment(session)

    with after.each:
        self.home.close()

    with context("that name their aggregates in plain words"):
        with it("should report each edge from a context's file to the domain model as one no callout shows: a context to each aggregate, a mapping to each side"):
            ordering, catalogue = "ordering/.context/bounded-context.md", "catalogue/.context/bounded-context.md"
            expect(_gaps(self.alignment, "edge_without_callout")).to(equal([catalogue, ordering, ordering, ordering, ordering]))

    with context("that name each aggregate as a link to its heading in the domain model"):
        with before.each:
            _link_aggregates(self.project)

        with it("should report no edge without a callout"):
            expect(_gaps(self.alignment, "edge_without_callout")).to(equal([]))

        with it("should report no callout that opens nothing"):
            expect(_gaps(self.alignment, "callout_target_missing")).to(equal([]))

        with it("should report no callout the graph has no edge for"):
            expect(_gaps(self.alignment, "callout_without_edge")).to(equal([]))
