"""A front-end view rendered between TypeScript and JavaScript: the type annotations go, the view stays."""

import sys
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.ux.model.view.front_end_view import ViewSyntaxNotConverted  # noqa: E402
from cdd_guidance.practices.ux.model.view.view_formats import JavaScriptView, TypeScriptView  # noqa: E402

_TYPED = '''import React, { useState } from "react";
import type { Order } from "./api";
import { type Cart, Country, bookshop } from "./api";

interface CheckoutProps {
  cart: Cart;
  onPaid: (order: Order) => void;
  note?: string;
}

type Step = "address" | "payment";

const COUNTRIES: Country[] = ["Canada", "France"];

/** Screen: Checkout. Stories: Pay For Order. */
export function CheckoutView({ cart, onPaid, note = "Total: due" }: CheckoutProps): JSX.Element {
  const [city, setCity] = useState<string>("");
  const [country, setCountry] = useState<Country>(COUNTRIES[0]);
  const cityMissing: boolean = city.trim() === "";

  const handleCity = (event: React.ChangeEvent<HTMLInputElement>): void => setCity(event.target.value);

  async function handlePay(): Promise<void> {
    const order = (await bookshop.checkOut({ city, country })) as Order;
    onPaid(order!);
  }

  return (
    <main data-screen="Checkout">
      <p>Total: {cart.total} as charged, {note}</p>
      <label className={cityMissing ? "error" : ""}>City <input type="text" value={city} onChange={handleCity} /></label>
      <select value={country} onChange={(e) => setCountry(e.target.value as Country)}>
        {COUNTRIES.map((name: Country) => (<option key={name} value={name}>{name}</option>))}
      </select>
      <button type="button" disabled={cityMissing} onClick={handlePay}>Pay</button>
    </main>
  );
}
'''

_UNTYPED = '''import React, { useState } from "react";
import { bookshop } from "./api";

const COUNTRIES = ["Canada", "France"];

/** Screen: Checkout. Stories: Pay For Order. */
export function CheckoutView({ cart, onPaid, note = "Total: due" }) {
  const [city, setCity] = useState("");
  const [country, setCountry] = useState(COUNTRIES[0]);
  const cityMissing = city.trim() === "";

  const handleCity = (event) => setCity(event.target.value);

  async function handlePay() {
    const order = (await bookshop.checkOut({ city, country }));
    onPaid(order);
  }

  return (
    <main data-screen="Checkout">
      <p>Total: {cart.total} as charged, {note}</p>
      <label className={cityMissing ? "error" : ""}>City <input type="text" value={city} onChange={handleCity} /></label>
      <select value={country} onChange={(e) => setCountry(e.target.value)}>
        {COUNTRIES.map((name) => (<option key={name} value={name}>{name}</option>))}
      </select>
      <button type="button" disabled={cityMissing} onClick={handlePay}>Pay</button>
    </main>
  );
}
'''

_ARROW_VIEW = '''export const CartView = (props: CartProps) => {
  const remove = (id: string) => props.onRemove(id);
  return <ul onClick={() => props.onOpen()}>{props.lines.map((line) => <li key={line.id}>{line.title}</li>)}</ul>;
};
'''


def outline(view) -> tuple:
    return (view.components, view.props, view.handlers)


with description("a front-end view written in TypeScript"):
    with before.all:
        self.view = TypeScriptView().parse(_TYPED)

    with it("should name its components"):
        expect(self.view.components).to(equal(["CheckoutView"]))

    with it("should name the props each component takes"):
        expect(self.view.props).to(equal({"CheckoutView": ["cart", "onPaid", "note"]}))

    with it("should name the handler each event is handed, and the event itself for a function written in place"):
        expect(self.view.handlers).to(equal(["handleCity", "onChange", "handlePay"]))

    with context("that is rendered to JavaScript"):
        with before.all:
            self.rendered = JavaScriptView().render(self.view)

        with it("should be the same view with every type annotation dropped"):
            expect(self.rendered).to(equal(_UNTYPED))

        with it("should keep the view's components, props and handlers"):
            expect(outline(JavaScriptView().parse(self.rendered))).to(equal(outline(self.view)))

        with it("should keep the words a screen shows, though they read like a type annotation"):
            expect(self.rendered).to(contain("<p>Total: {cart.total} as charged, {note}</p>"))

        with context("and back to TypeScript"):
            with before.all:
                self.back = TypeScriptView().render(JavaScriptView().parse(self.rendered))

            with it("should be the JavaScript as it is, with no type annotation made up for it"):
                expect(self.back).to(equal(_UNTYPED))

            with it("should still have the view's components, props and handlers"):
                expect(outline(TypeScriptView().parse(self.back))).to(equal(outline(self.view)))

    with context("that is rendered to TypeScript"):
        with it("should be as it was written, types and all"):
            expect(TypeScriptView().render(self.view)).to(equal(_TYPED))

    with context("whose component is an arrow function that takes its props whole"):
        with before.all:
            self.view = TypeScriptView().parse(_ARROW_VIEW)

        with it("should name the props the component reads"):
            expect(self.view.props).to(equal({"CartView": ["onRemove", "onOpen", "lines"]}))

        with it("should drop the annotations of its parameters in JavaScript"):
            expect(JavaScriptView().render(self.view)).to(contain("export const CartView = (props) => {\n  const remove = (id) => props.onRemove(id);"))

    with context("whose code holds what reads like an annotation and is none"):
        with before.all:
            def javascript_of(typed: str) -> str:
                return JavaScriptView().render(TypeScriptView().parse(typed))

            self.javascript_of = javascript_of

        with it("should keep a choice between two calls, whose colon follows a call's brackets"):
            choice = "const press = isHeld ? () => openReport(ticket.next ?? '') : () => runNext(ticket);\n"
            expect(self.javascript_of(choice)).to(equal(choice))

        with it("should keep a choice between a call and a tag"):
            choice = "const shown = found ? TicketView(found, { page }) : <Text color={muted}>None</Text>;\n"
            expect(self.javascript_of(choice)).to(equal(choice))

        with it("should keep a choice that ends its line, before a declaration that takes a value apart"):
            lines = "const published = entry ? publishedOf(entry) : null\nconst { x, y } = canvas.frame\n"
            expect(self.javascript_of(lines)).to(equal(lines))

        with it("should keep a value read from an object, though an import of the same name is dropped"):
            typed = "import { Code, Operation } from './codes';\nconst sent = (code: Code) => Operation.Code;\n"
            expect(self.javascript_of(typed)).to(equal("import { Operation } from './codes';\nconst sent = (code) => Operation.Code;\n"))

    with context("whose functions are written in other ways"):
        with before.all:
            def javascript_of(typed: str) -> str:
                return JavaScriptView().render(TypeScriptView().parse(typed))

            self.javascript_of = javascript_of

        with it("should drop the annotations of a function that answers a function"):
            typed = "export const iconOf = (count: number) => (colour: string): string => draw(colour, count);\n"
            expect(self.javascript_of(typed)).to(equal("export const iconOf = (count) => (colour) => draw(colour, count);\n"))

        with it("should drop the annotation of an async function's result and keep its arrow"):
            typed = "const run = async (): Promise<void> => {\n  await send();\n};\n"
            expect(self.javascript_of(typed)).to(equal("const run = async () => {\n  await send();\n};\n"))

        with it("should drop a type written as words in quotes"):
            typed = "const choose = (next: '' | 'engineering') => setTheme(next);\n"
            expect(self.javascript_of(typed)).to(equal("const choose = (next) => setTheme(next);\n"))

        with it("should drop type arguments that hold a function's type"):
            typed = "const presses = useRef<((event: { line: number | null; }) => void)[]>([]);\n"
            expect(self.javascript_of(typed)).to(equal("const presses = useRef([]);\n"))

        with it("should drop what a class writes for its types: its type arguments, who may reach a member, and each annotation"):
            typed = (
                "export class FailureView extends Component<{ page: Page }, { failure: string }> implements Shown {\n"
                "  private state: { failure: string } = { failure: '' };\n"
                "  get shown(): boolean { return this.state.failure !== ''; }\n"
                "  render(): ReactNode {\n    return <p>{this.state.failure}</p>;\n  }\n}\n"
            )
            expect(self.javascript_of(typed)).to(equal(
                "export class FailureView extends Component {\n"
                "  state = { failure: '' };\n"
                "  get shown() { return this.state.failure !== ''; }\n"
                "  render() {\n    return <p>{this.state.failure}</p>;\n  }\n}\n"
            ))

    with context("whose constructor declares a member in its parameters, which JavaScript has no way to write"):
        with it("should refuse the render, naming the parameter"):
            view = TypeScriptView().parse("export class CartClient {\n  constructor(private readonly page: Page) {}\n}\n")
            expect(lambda: JavaScriptView().render(view)).to(raise_error(ViewSyntaxNotConverted, contain("private readonly page")))

    with context("that declares an enum, which has no JavaScript without its type"):
        with it("should refuse the render, naming the enum"):
            view = TypeScriptView().parse("enum Step { Address, Payment }\nexport function CheckoutView() {\n  return <main>{Step.Address}</main>;\n}\n")
            expect(lambda: JavaScriptView().render(view)).to(raise_error(ViewSyntaxNotConverted, contain("enum Step")))


with description("a front-end view written in JavaScript"):
    with context("that is rendered to TypeScript"):
        with it("should be as it was written"):
            expect(TypeScriptView().render(JavaScriptView().parse(_UNTYPED))).to(equal(_UNTYPED))

    with context("that is rendered to JavaScript"):
        with it("should be as it was written"):
            expect(JavaScriptView().render(JavaScriptView().parse(_UNTYPED))).to(equal(_UNTYPED))
