"""BDD spec for practices/ddd/ddd.py — Ddd toolset CE delegation.
"""
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_false, be_true, equal, expect, have_key, raise_error
from mamba import after, before, context, description, it

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.ddd.ddd import Ddd
from harness.agent_tools.agent_tools import AgentInstructions
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from harness.guidance.practice_formats import Rendered


class _DddSpecSupport:
    """Shared arrange helpers kept on a class (not module-level functions)."""

    def expanded(self, ddd: Ddd, action_name: str) -> str:
        func = getattr(type(ddd), action_name)
        body = AgentInstructions.for_callable(func, ddd)
        return "\n".join(body.prompt)

    def ddd(self) -> Ddd:
        return PRACTICE_CATALOGUE.create("ddd", fidelity="bounded_context")


_support = _DddSpecSupport()


with description("a Ddd toolset"):
    with context("that is created"):
        with context("with its defaults"):
            with it("should work at bounded_context in the markdown format"):
                tool = Ddd()
                expect(tool.fidelities.current.name).to(equal("bounded_context"))
                expect(tool.format).to(equal("markdown"))

        with context("with model fidelity"):
            with it("should default to markdown format"):
                expect(Ddd(fidelity="model").format).to(equal("markdown"))

        with context("with tactics fidelity"):
            with it("should default to python format"):
                expect(Ddd(fidelity="tactics").format).to(equal("python"))

        with context("with an unsupported fidelity"):
            with it("should raise ValueError"):
                expect(lambda: Ddd(fidelity="modules")).to(raise_error(ValueError))

        with context("with an unsupported format"):
            with it("should raise ValueError"):
                expect(
                    lambda: Ddd(fidelity="bounded_context", format="yaml")
                ).to(raise_error(ValueError))

    with context("whose generate default working folder is src"):
        with it("should keep src as the generate default"):
            expect(Ddd().default_workspace_folder).to(equal("src"))

    with context("that provides a CleanEngineering companion"):
        with context("with bounded_context fidelity"):
            with it("should treat the modules fidelity as the companion"):
                companion = PRACTICE_CATALOGUE.create("ddd", fidelity="bounded_context").fidelities.current.clean_engineering
                expect(companion.name).to(equal("modules"))

        with context("with model fidelity"):
            with it("should treat the model fidelity as the companion"):
                companion = PRACTICE_CATALOGUE.create("ddd", fidelity="model").fidelities.current.clean_engineering
                expect(companion.name).to(equal("model"))

        with context("with tactics fidelity"):
            with it("should treat the code fidelity as the companion"):
                companion = PRACTICE_CATALOGUE.create("ddd", fidelity="tactics").fidelities.current.clean_engineering
                expect(companion.name).to(equal("code"))

    with context("whose contexts instruction is expanded"):
        with it("should include the experts-words-preferred rule slug"):
            prose = Ddd().scoped_markdown
            expect("experts-words-preferred" in prose).to(be_true)

        with it("should include the bc-by-lifecycle-not-ui-themes rule slug"):
            prose = Ddd().scoped_markdown
            expect("bc-by-lifecycle-not-ui-themes" in prose).to(be_true)

        with it("should include the repository-is-collection-lifecycle rule slug"):
            prose = Ddd().scoped_markdown
            expect("repository-is-collection-lifecycle" in prose).to(be_true)

        with it("should include the shared-identity-is-generalisation rule slug"):
            prose = Ddd().scoped_markdown
            expect("shared-identity-is-generalisation" in prose).to(be_true)

        with it("should include the hang-deps-on-owning-bc rule slug"):
            prose = Ddd().scoped_markdown
            expect("hang-deps-on-owning-bc" in prose).to(be_true)

        with it("should include the user-facing-system-first rule slug"):
            prose = Ddd().scoped_markdown
            expect("user-facing-system-first" in prose).to(be_true)

        with it("should include the context-tree-bc-aggregate-concept rule slug"):
            prose = Ddd().scoped_markdown
            expect("context-tree-bc-aggregate-concept" in prose).to(be_true)

        with it("should include the link-arrow-target rule slug"):
            prose = Ddd().scoped_markdown
            expect("link-arrow-target" in prose).to(be_true)

        with it("should name the bounded_context fidelity"):
            prose = Ddd().scoped_markdown
            expect("bounded_context" in prose).to(be_true)

    with context("that does not own kit lifecycle actions"):
        with it("should not expose generate, validate, satisfy, repair, grill, sketch, iterate, or document"):
            practice = _support.ddd()
            for name in (
                "generate",
                "validate",
                "satisfy",
                "repair",
                "grill",
                "sketch",
                "iterate",
                "document",
            ):
                expect(name in practice.tools).to(equal(False))

    with context("whose guidance action is expanded"):
        with it("should include the Clean Engineering companion's instructions"):
            prose = _support.expanded(_support.ddd(), "guidance")
            expect("independent modules" in prose).to(be_true)

        with it("should NOT inline CleanEngineering generate instructions"):
            prose = _support.expanded(_support.ddd(), "guidance")
            expect("Deepen OO design" in prose).to(equal(False))

    with context("whose transform tool is called"):
        with it("should delegate to CleanEngineering and return a dict"):
            result = Ddd().render("markdown", "class Foo:\n    pass\n", source="python")
            expect(result).to(be_a(Rendered))
            expect(result.format).to(equal("markdown"))

        with context("with a domain model read from python and rendered to typescript"):
            with it("should carry each python body commented out inside its method"):
                python = "class Cart:\n    def add(self, item: object) -> None:\n        self.items.append(item)\n"
                result = Ddd(fidelity="model").render("typescript", python, source="python")
                expect("    // self.items.append(item)" in result.content).to(be_true)


with description("a Ddd practice made in a set with the Clean Engineering practice it extends"):
    with it("should read a plain class model through that same Clean Engineering practice"):
        from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE

        practices = {type(item).__name__: item for item in PRACTICE_CATALOGUE.create_all(fidelity=None)}
        practices["Ddd"].render("markdown", "## Cart\n\n------\n+ total: int\n----\n", source="markdown")
        expect(practices["Ddd"].working_set.extended.formats._made).to(have_key("markdown"))


# (E) Review Generated Work In File Viewer
# (S) Person --> Review Files In Files App
with description("a file the DDD practice claims as its own, so a page filtering on DDD lists it"):
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="ddd-claims-"))
        self.ddd = _support.ddd()

        def written(name: str, text: str) -> Path:
            file = self.folder / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(text, encoding="utf-8")
            return file

        self.written = written

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    with it("should claim code whose class carries a DDD stereotype"):
        expect(self.ddd.claims(self.written("cart.py", "@aggregate_root\nclass Cart:\n    pass\n"))).to(be_true)

    with it("should claim a domain model by its name"):
        expect(self.ddd.claims(self.written("domain-model.md", "# Orders\n"))).to(be_true)

    with it("should claim a bounded context map by its name"):
        expect(self.ddd.claims(self.written("bounded-context-map.drawio", "<mxfile/>\n"))).to(be_true)

    with it("should leave code with neither to the other practices"):
        expect(self.ddd.claims(self.written("chat_bar.py", "class ChatBarClient:\n    pass\n"))).to(be_false)

    with context("with a class named for a building block"):
        with context("in a bounded context's folder"):
            with it("should claim it"):
                self.written("ordering/.context/bounded-context.md", "# Ordering\n")
                expect(self.ddd.claims(self.written("ordering/ordering.ts", "export class OrderRepository {}\n"))).to(be_true)

        with context("in an aggregate, a folder under a bounded context"):
            with it("should claim it"):
                self.written("ordering/.context/bounded-context.md", "# Ordering\n")
                expect(self.ddd.claims(self.written("ordering/carts/carts.ts", "export class CartRepository {}\n"))).to(be_true)

        with context("in a folder where a class carries a DDD stereotype"):
            with it("should claim it"):
                self.written("carts/cart.py", "@aggregate_root\nclass Cart:\n    pass\n")
                expect(self.ddd.claims(self.written("carts/carts.py", "class CartRepository:\n    pass\n"))).to(be_true)

        with context("in a folder that holds no domain"):
            with it("should leave it to the other practices, its name saying nothing about the business"):
                expect(self.ddd.claims(self.written("agent_tools/agent_tools.py", "class AgentOperation:\n    pass\n"))).to(be_false)


# (S) Person --> Choose Action And Formats
with description("the DDD bounded_context fidelity's formats"):
    with before.all:
        self.outputs = PRACTICE_CATALOGUE.create("ddd", fidelity="bounded_context").fidelities.current.outputs

    with it("should save the map as draw.io beside its markdown and whiteboard"):
        expect(self.outputs).to(equal({
            "markdown": [".context/bounded-context-map.md", "{bounded_context}/.context/bounded-context.md"],
            "drawio": ".context/bounded-context-map.drawio",
            "whiteboard": ".context/bounded-context-map.whiteboard",
        }))

    # A file list and the graph tree show the files a fidelity declares, and a context's mappings are read from the
    # file that marks its folder.
    with it("should hold the bounded-context.md that marks each context's folder as its own file"):
        declared = PRACTICE_CATALOGUE.create("ddd", fidelity="bounded_context").fidelities.current.declared
        expect(declared.includes("ordering/.context/bounded-context.md", "markdown")).to(equal(True))

    with it("should still name the map's drawing for a render of the map"):
        declared = PRACTICE_CATALOGUE.create("ddd", fidelity="bounded_context").fidelities.current.declared
        expect(declared.file_name_beside(".context/bounded-context-map.md", "drawio")).to(equal("bounded-context-map.drawio"))

    with it("should read and write draw.io through the map's draw.io adapter"):
        expect(Ddd.format_adapters["drawio"][1]).to(equal("DrawIOBoundedContextMap"))
