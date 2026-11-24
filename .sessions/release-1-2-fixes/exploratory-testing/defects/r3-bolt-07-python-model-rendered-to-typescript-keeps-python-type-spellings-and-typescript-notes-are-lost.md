# A model or building block rendered from Python to TypeScript keeps Python's type spellings (`list[CartLine]`, `Collection[Cart]`), from TypeScript to Python keeps TypeScript's (`-> boolean`), and loses the relationship marks; operation notes are lost from TypeScript to markdown

- **Charter:** Round 3 - DDD (bounded_context, model, tactics), checks 1, 2 and 4
- **Tester:** Bolt
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers a trip between the two code formats of DDD model and tactics.
- **Module and class:** `cdd_guidance/practices/clean_engineering/model/python/python_class_model.py` `PythonCleanEngineeringModel` and `model/typescript/typescript_class_model.py` `TypeScriptCleanEngineeringModel`, reached through `ddd/ddd_formats.py`.
- **Severity:** wrong result
- **Related:** widget-20 reported the markdown to Python and back losses (association and its note, `-> OrderLine.price` to `-> price`, `Collection<Order>` to `Collection[Order]`); those still fail on this build and are not repeated here.

## Steps
Sandbox `C:\dev\_et\round3\bolt\work` (commit `0330958`), session `main`, throwaway cdd server (`C:\dev\_et\round3\bolt\drv\run.py`, calls in `drv\c2.json`, `drv\c3.json`; answers in `drv\out\c2-py-ts.json`, `c2-ts-py.json`, `c2-tac-py-ts.json`, `c2-tac-ts-py.json`; markdown kept in `C:\dev\_et\round3\bolt\trips\domain-model--md-py-md.md` and `--md-ts-md.md`).

1. `ordering/cart/cart.py` and the three other aggregates, as render wrote them from the model: `# << composition >>` over `lines: list[CartLine]`, `# << association >>` and `# held by identity — Book lives in Catalogue · Book` over `bookId: BookId`, `carts: Collection[Cart]`.
2. `render.render {"guidance": "ddd-model", "format": "typescript", "paths": [the four .py]}`; `{"format": "python", "paths": [the four .ts]}`; the same two at `ddd-tactics` on the five building-block files (`order_paid`, `order_factory`, `checkout`, `paid_order_specification`, `cart_checked_out`).
3. `render.render {"guidance": "ddd-model", "format": "markdown", "paths": [the four .ts]}`, then the four `.py`.

## Expected
The same classes, members and relationships in the other language's own spelling, as the render from markdown writes them (`lines: CartLine[];`, `carts: Collection<Cart>;` in TypeScript).

## Actual
- **Python to TypeScript:** `lines: list[CartLine];`, `carts: Collection[Cart];`, `search(...): list[Order]`, in the constructor's parameters too; none is TypeScript. The comments `// << composition >>`, `// << association >>`, `// << aggregation >>` and the held-by-identity note, which the render from markdown writes, are gone (104 lines differ from markdown to TypeScript).
- **TypeScript to Python:** `def isSatisfiedBy(self, order: Order) -> boolean:` and `-> void`; every operation's docstring is gone (`"""the title and price cross at the moment the book is added"""`).
- **Both:** each body becomes a comment (`// python body to translate:`), above a second copy of the assignments in a constructor. This part may be intended.
- **TypeScript to markdown:** every operation note is gone (`// the Customer looks up their own orders`, five in all), though the TypeScript holds each as `/** ... */`; Python to markdown keeps them. Calls lose their arguments either way (`-> BookRepository.load(bookId)` comes back `-> BookRepository.load` from TypeScript and `-> load` from Python).

## Tier that should catch it
Unit (`ddd/model/code_round_trip_spec.py`): no example renders one code format to the other with a collection, an array and a boolean among the types, or checks an operation's note after TypeScript.

## Status: fixed (2026-11-23)
- Type spellings were already translated by the one translation every code writer uses, `CodeLanguage.type_name` (`cdd_guidance/practices/source_code/code_body.py`): `list[CartLine]` is `CartLine[]` in TypeScript, `Collection[Cart]` is `Collection<Cart>`, `boolean` is `bool` in Python; the relationship marks are written in both languages.
- Fixed now: an operation's body that is only what a render wrote from the model (its notes as comments, its calls, then the line that fails until it is written) is read as no body (`CodeLanguage.scaffold_calls`, `OperationSourceFacts.take_body`). The operation keeps its notes and its calls, with their arguments, so a render into the other language writes them in that language (`// the Customer looks up their own orders`, `BookRepository.load(bookId);`) instead of a body to translate, and the markdown gets `-> BookRepository.load(bookId)` and the note back. A TypeScript method's doc comment `/** ... */` is read as the operation's description (`CFamilyParse._doc_comment_above`), so a Python docstring survives Python to TypeScript and back.
- Covered by `cdd_guidance/practices/ddd/model/code_round_trip_spec.py`, "a domain model rendered from one code format to the other": Python to TypeScript (array, generic, relationship mark, note, call with its arguments, no Python body to translate), TypeScript back to Python (`-> bool`, no TypeScript body to translate, the docstring), and TypeScript to markdown (each note, each call with its arguments).
- Left as it is: an operation whose body holds real code is still carried into the other language as that code under a "body to translate" comment; translating statements from one language to another is out of reach of a format adapter. A call made inside real code is read by name only (`-> load`), since the reader keeps what a body calls, not the arguments of each call.
