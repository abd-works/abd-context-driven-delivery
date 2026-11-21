"""A front-end view rendered onto a view file that is already there: the file takes the new shape and loses nothing.

The model is one Checkout view, written here in TypeScript, and each change to it (a handler added, removed, renamed;
a prop or a hook gained or lost; a component gained). The view file already there is that model as an earlier render
wrote it in the file's own language, with what a person then wrote into it. Every example after that is shared, and
run for a file in TypeScript and for a file in JavaScript: it names no language."""

import sys
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, included_context, it, shared_context

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.ux.model.view.view_formats import JavaScriptView, TypeScriptView  # noqa: E402

_MARK = "no longer in the model"

_MODEL = '''import { useState } from "react";
import { bookshop } from "./api";

export function CheckoutView({ cart, onPaid }: CheckoutProps) {
  const [city, setCity] = useState<string>("");

  const handleCity = (event: ChangeEvent) => setCity(event.target.value);

  async function handlePay(): Promise<void> {
    onPaid(await bookshop.checkOut({ city }));
  }

  return (
    <main>
      <input value={city} onChange={handleCity} />
      <button onClick={handlePay}>Pay {cart.total}</button>
    </main>
  );
}
'''
_RETURN = "  return (\n    <main>"
_CLEAR = '  function handleClear(): void {\n    setCity("");\n  }\n\n'
_COUNTRY = '  const [country, setCountry] = useState<string>("Canada");\n'
_EMPTY_CART = '\n/** Screen: Empty Cart. */\nexport function EmptyCartView({ onBrowse }: EmptyCartProps) {\n  return <button onClick={onBrowse}>Browse</button>;\n}\n'


class ViewFile:
    """The Checkout view's file in one language: what an earlier render of the model wrote, with what a person wrote
    into it since, and the same model rendered onto it again after a change."""

    def __init__(self, format) -> None:
        self.format = format
        self.text = self._written_by_a_person(self.rendered(_MODEL))

    def rendered(self, model: str) -> str:
        """The model as a render writes it in this file's language."""
        return self.format.render(TypeScriptView().parse(model))

    def _written_by_a_person(self, text: str) -> str:
        """The file with a helper above the component, a note between two members, and a line in a handler's body."""
        text = text.replace("export function CheckoutView", "function track(what) {\n  console.log(what);\n}\n\nexport function CheckoutView", 1)
        text = text.replace("  async function handlePay", "  // paying is the last step of the checkout\n  async function handlePay", 1)
        return text.replace("    onPaid(await", '    track("paid");\n    onPaid(await', 1)

    def after(self, model: str):
        """What the file becomes when the model, changed, is rendered onto it."""
        return self.format.reshape(self.rendered(model), self.text)

    def lines_lost_by(self, reshaped) -> list[str]:
        """Each line of the file that carried content and is nowhere in the reshaped text, whole or inside a line."""
        held = reshaped.text.splitlines()
        return [line for line in self.text.splitlines() if line.strip() and not any(line.strip() in kept for kept in held)]


with shared_context("a view file a changed model is rendered onto"):
    with context("with the model unchanged"):
        with it("should be left exactly as it is"):
            expect(self.file.after(_MODEL).text).to(equal(self.file.text))

        with it("should say nothing was kept apart or added"):
            reshaped = self.file.after(_MODEL)
            expect((reshaped.kept, reshaped.added)).to(equal(([], [])))

    with context("with a handler added to the model"):
        with before.all:
            self.reshaped = self.file.after(_MODEL.replace(_RETURN, _CLEAR + _RETURN))

        with it("should name the handler as added"):
            expect(self.reshaped.added).to(equal(["CheckoutView.handleClear"]))

        with it("should write the handler empty, before what the component returns"):
            expect(self.reshaped.text).to(contain("{}\n\n  return ("))

        with it("should not bring the body the model's handler has"):
            expect('setCity("")' in self.reshaped.text).to(equal(False))

        with it("should lose no line the file held"):
            expect(self.file.lines_lost_by(self.reshaped)).to(equal([]))

        with it("should keep the line a person wrote in another handler's body"):
            expect(self.reshaped.text).to(contain('    track("paid");\n    onPaid(await'))

        with it("should keep the note a person wrote between two members, above the member it was written for"):
            expect(self.reshaped.text).to(contain("  // paying is the last step of the checkout\n  async function handlePay"))

        with it("should keep the helper a person wrote above the component where it was"):
            expect(self.reshaped.text).to(contain("function track(what) {\n  console.log(what);\n}\n\nexport function CheckoutView"))

        with it("should change nothing when the same model is rendered onto it again"):
            again = self.file.format.reshape(self.file.rendered(_MODEL.replace(_RETURN, _CLEAR + _RETURN)), self.reshaped.text)
            expect(again.text).to(equal(self.reshaped.text))

    with context("with a handler removed from the model"):
        with before.all:
            self.model = _MODEL.replace("  const handleCity = (event: ChangeEvent) => setCity(event.target.value);\n\n", "").replace(" onChange={handleCity}", "")
            self.reshaped = self.file.after(self.model)

        with it("should name the handler as kept"):
            expect(self.reshaped.kept).to(equal(["CheckoutView.handleCity"]))

        with it("should keep the handler where it was, under a line that says it is no longer in the model"):
            marked = [index for index, line in enumerate(self.reshaped.text.splitlines()) if _MARK in line and "CheckoutView.handleCity" in line]
            expect(self.reshaped.text.splitlines()[marked[0] + 1]).to(contain("const handleCity ="))

        with it("should lose no line the file held"):
            expect(self.file.lines_lost_by(self.reshaped)).to(equal([]))

        with it("should change nothing, and still name the handler as kept, when the same model is rendered onto it again"):
            again = self.file.format.reshape(self.file.rendered(self.model), self.reshaped.text)
            expect((again.text, again.kept)).to(equal((self.reshaped.text, ["CheckoutView.handleCity"])))

    with context("with a handler renamed in the model"):
        with before.all:
            self.reshaped = self.file.after(_MODEL.replace("handlePay", "handleCheckout"))

        with it("should name the handler under its old name as kept"):
            expect(self.reshaped.kept).to(equal(["CheckoutView.handlePay"]))

        with it("should name the handler under its new name as added"):
            expect(self.reshaped.added).to(equal(["CheckoutView.handleCheckout"]))

        with it("should keep the old handler's body, with the line a person wrote in it, for its move to the new one"):
            expect(self.reshaped.text).to(contain('  async function handlePay'))
            expect(self.reshaped.text).to(contain('    track("paid");'))

        with it("should lose no line the file held"):
            expect(self.file.lines_lost_by(self.reshaped)).to(equal([]))

    with context("with a prop added to the model"):
        with before.all:
            self.reshaped = self.file.after(_MODEL.replace("{ cart, onPaid }", "{ cart, onPaid, note }"))

        with it("should name the prop as added"):
            expect(self.reshaped.added).to(equal(["CheckoutView.note"]))

        with it("should have the component take the prop beside the ones it took"):
            expect(self.reshaped.text).to(contain("export function CheckoutView({ cart, onPaid, note }"))

        with it("should lose no line the file held, the component's opening line kept as a comment above the new one"):
            expect(self.file.lines_lost_by(self.reshaped)).to(equal([]))

        with it("should change nothing when the same model is rendered onto it again"):
            again = self.file.format.reshape(self.file.rendered(_MODEL.replace("{ cart, onPaid }", "{ cart, onPaid, note }")), self.reshaped.text)
            expect(again.text).to(equal(self.reshaped.text))

    with context("with a prop removed from the model"):
        with before.all:
            self.model = _MODEL.replace("{ cart, onPaid }", "{ cart }")
            self.reshaped = self.file.after(self.model)

        with it("should name the prop as kept"):
            expect(self.reshaped.kept).to(equal(["CheckoutView.onPaid"]))

        with it("should leave the component taking the prop, under a line that says the prop is no longer in the model"):
            lines = self.reshaped.text.splitlines()
            marked = next(index for index, line in enumerate(lines) if _MARK in line and "CheckoutView.onPaid" in line)
            expect(lines[marked + 1]).to(contain("export function CheckoutView({ cart, onPaid }"))

        with it("should change nothing when the same model is rendered onto it again"):
            expect(self.file.format.reshape(self.file.rendered(self.model), self.reshaped.text).text).to(equal(self.reshaped.text))

    with context("with a hook added to the model"):
        with before.all:
            self.reshaped = self.file.after(_MODEL.replace("\n  const handleCity", _COUNTRY + "\n  const handleCity"))

        with it("should name the hook as added, by the first name it declares"):
            expect(self.reshaped.added).to(equal(["CheckoutView.country"]))

        with it("should declare the hook after the hooks the component had"):
            expect(self.reshaped.text).to(contain('  const [country, setCountry] = useState'))
            expect(self.reshaped.text.index("[city, setCity]") < self.reshaped.text.index("[country, setCountry]") < self.reshaped.text.index("const handleCity")).to(equal(True))

        with it("should lose no line the file held"):
            expect(self.file.lines_lost_by(self.reshaped)).to(equal([]))

    with context("with a component added to the model"):
        with before.all:
            self.reshaped = self.file.after(_MODEL + _EMPTY_CART)

        with it("should name the component as added"):
            expect(self.reshaped.added).to(equal(["EmptyCartView"]))

        with it("should write the component after the ones the file holds, with the comment above it"):
            expect(self.reshaped.text).to(contain("}\n\n/** Screen: Empty Cart. */\nexport function EmptyCartView("))

        with it("should leave the file's own component as it was, above it"):
            expect(self.reshaped.text.startswith(self.file.text)).to(equal(True))

    with context("that holds a component the model does not"):
        with before.all:
            self.own = self.file.text + "\nexport function ReceiptView() {\n  return <p>Paid</p>;\n}\n"
            self.reshaped = self.file.format.reshape(self.file.rendered(_MODEL), self.own)

        with it("should be left as it is, since a file often holds a component its model does not"):
            expect((self.reshaped.text, self.reshaped.kept)).to(equal((self.own, [])))


with description("a front-end view rendered onto a view file already there"):
    with context("written in TypeScript"):
        with before.all:
            self.file = ViewFile(TypeScriptView())

        with included_context("a view file a changed model is rendered onto"):
            pass

        with it("should keep the types the file's own handler was written with"):
            expect(self.file.after(_MODEL.replace("handlePay", "handleCheckout")).text).to(contain("async function handlePay(): Promise<void> {"))

    with context("written in JavaScript"):
        with before.all:
            self.file = ViewFile(JavaScriptView())

        with included_context("a view file a changed model is rendered onto"):
            pass

        with it("should write an added handler with no type annotation"):
            reshaped = self.file.after(_MODEL.replace(_RETURN, _CLEAR + _RETURN))
            expect(reshaped.text).to(contain("  function handleClear() {}\n"))

    with context("whose component lists its props one to a line"):
        with before.all:
            self.existing = "export function CartView({\n  lines,\n  onOpen\n}) {\n  return <ul onClick={onOpen}>{lines.length}</ul>;\n}\n"
            self.rendered = "export function CartView({ lines, onOpen, onRemove }) {\n  return <ul onClick={onOpen}>{lines.length}</ul>;\n}\n"
            self.reshaped = JavaScriptView().reshape(self.rendered, self.existing)

        with it("should give the added prop a line of its own after the others"):
            expect(self.reshaped.text).to(contain("  lines,\n  onOpen,\n  onRemove,\n}) {"))

        with it("should change nothing when the same view is rendered onto it again"):
            expect(JavaScriptView().reshape(self.rendered, self.reshaped.text).text).to(equal(self.reshaped.text))

    with context("that holds no component, only values"):
        with it("should keep the file's lines and add the component the render holds after them"):
            existing = "export const COUNTRIES = [\"Canada\"];\n"
            rendered = "export function CartView() {\n  return <p>Cart</p>;\n}\n"
            expect(JavaScriptView().reshape(rendered, existing).text).to(equal(existing + "\n" + rendered))
