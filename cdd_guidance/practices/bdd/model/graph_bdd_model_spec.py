"""A BDD realization rendered from a saved knowledge graph: the spec tree, and the model's interactions under each call."""

import json
import shutil
import sys
import tempfile
from pathlib import Path

from expects import contain, equal, expect, have_key
from mamba import after, before, context, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.graph.graph import Graph  # noqa: E402
from harness.graph.saved_graph import SavedGraph  # noqa: E402

from cdd_guidance.practices.bdd.bdd import Bdd  # noqa: E402

_CART = """\
export class Cart {
  add(item: string): void {}
}
"""

_CART_SPEC = """\
import { beforeEach, describe, it } from 'vitest'

describe('a cart', () => {
  it('should start empty', () => {})

  describe('with an item added', () => {
    beforeEach(() => cart.add('apple'))

    it('should keep the item', () => {})
  })
})
"""

_CART_MODEL = """\
# shop

## Cart

------
----
+ add(item: str): Cart
	-> Ledger.record

## Ledger

------
----
+ record(entry: str): str
"""


with description("a saved graph of a spec and the code it tests"):
    with before.all:
        self.folder = Path(tempfile.mkdtemp())
        (self.folder / "src" / ".context").mkdir(parents=True)
        (self.folder / "src" / "cart.ts").write_text(_CART, encoding="utf-8")
        (self.folder / "src" / "cart.spec.ts").write_text(_CART_SPEC, encoding="utf-8")
        (self.folder / "src" / ".context" / "cart-model.md").write_text(_CART_MODEL, encoding="utf-8")
        graph = Graph()
        graph.load_files(str(self.folder), ["bdd", "clean_engineering"], ["src"])
        self.clean = graph.practice("clean_engineering")
        self.saved = SavedGraph.from_graph(graph).text

    with after.all:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("with a Clean Engineering model beside the code"):
        with it("should give the code's operation the model's interactions"):
            expect(self.clean.reading.model_documents.described_member("Cart", "add").callees).to(equal(["Ledger.record"]))

        with it("should keep every member the model describes, the ones with no code too"):
            expect(self.clean.reading.model_documents.described_member("Ledger", "record").return_type).to(equal("str"))

        with it("should save no copy of the model's members beside the code's nodes"):
            root_facts = json.loads(self.saved)["practices"]["clean_engineering"]["root_facts"]
            expect(root_facts).not_to(have_key("model_members"))

    with context("that is rendered as a bdd realization"):
        with before.all:
            self.rendered = Bdd(fidelity="realization").render("markdown", self.saved, source="graph")["content"]

        with it("should draw the setup's call, then the interaction the model gives it, then what each returns"):
            expect(self.rendered).to(
                contain("    -> Cart.add(item: str)\n      -> Ledger.record(entry: str)\n      <- str\n    <- Cart\n    it should keep the item")
            )

        with it("should say so on an observation that invokes nothing"):
            expect(self.rendered).to(contain("  // the graph holds no operation this observation calls\n  it should start empty"))
