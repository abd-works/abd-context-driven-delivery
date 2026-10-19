### Example factories (Fake / Isolated / Production **modes**)

When a type is used from **Stories** (helpers / scenario setup), the factory lives in a sibling file, separate from the production family:

| File | Contents |
|---|---|
| `{family}.{ext}` | (optionally **`I{Type}`** +) production **`{Type}`** (+ subtypes / peers) — production family only |
| `{type}_example_factory.{ext}` | (optionally **`I{Type}ExampleFactory`** +) **`{Type}ExampleFactory`** + `examples[{example_key}]` |

`I{Type}` and `I{Type}ExampleFactory` follow the same **opt-in** rule as any other interface (see § Interfaces) — default to the concrete `{Type}` / `{Type}ExampleFactory` directly; only introduce the interface pair when requested or genuinely needed for abstraction. The two decisions are independent: a domain type can skip its interface while its factory keeps one (or vice versa).

Do **not** put factory wiring in the production family file. Do **not** generate `Fake{Type}` / `Isolated{Type}` / `Production{Type}` subclasses — those are **usage modes**, not an inheritance tree.

**PATTERN** (see also `templates/clean_engineering-sketch.md` and templates):
