# Instructions

## Purpose

`@instruction` turns a toolset method into an expandable content reference — a file, folder, or markdown section co-located with the package — that the AI receives as operational context when an action runs.

## Primary use case

Declare a method on a `@toolset` class and mark it `@instruction`. When an `@action` that calls the slot expands, the system resolves the label to a markdown file, a folder of assets, or a section heading inside `{slug}.md`, and injects that content into the AI's instructions. The method body is always `...`; the decorator replaces it with a slot.

## Constraint

**Any class that declares an `@instruction` (or is ever passed as a `host` to `Instruction.ref`) must define a `module_dir` property:**

```python
@property
def module_dir(self) -> Path:
    return Path(inspect.getfile(type(self))).resolve().parent
```

Asset lookup reads this via `getattr(host, "module_dir", Path("."))`. Without the property, that silently falls back to `Path(".")` — the process's current working directory, not the class's own folder. Classes with no `@instruction` slots do not need this property.

Three resolution forms exist — chosen automatically by the locator in order of priority:

| Priority | What matches | Resolved as |
|---|---|---|
| 1 | `module_dir / label /` is a directory | Folder — all markdown files merged |
| 2 | `module_dir / label.md` is a file | File — full content |
| 3 | `## Label` heading exists in `{slug}.md` | Section — content under that heading |
| — | `label=` kwarg on `@instruction` | Overrides the default (method name) |

An unresolvable label expands to empty string without raising.

## Rationale

1. **Content lives beside code** — instruction prose is in markdown files co-located with the toolset; no free-floating prompt files scattered elsewhere.
2. **Dynamic resolution** — slots discover files and sections by name at expand time; no hard-coded paths in action bodies.
3. **Separation of concerns** — `@instruction` slots decouple static reference material (frameworks, templates, guidelines) from the imperative step-by-step recipe in `@action` bodies.

## Seam

The seam is the path from a labeled `@instruction` slot to expanded text:

1. `AssetLocator(instance, label)` walks `module_dir` — folder → file → section.
2. `Instruction.ref(host, label)` builds the value object.
3. `Instruction.expand()` reads the resolved location and returns **raw text** — no substitution happens here.
4. Action expansion inlines each `self.slot_name()` call found in the `@action` body into the prose parts.
5. Placeholders `{{self.attr}}` and `{{param}}` are resolved when the action builds final instructions — not at file-read time.

| Placeholder | Resolved from | Raises when |
|---|---|---|
| `{{self.attr}}` | `getattr(instance, attr)` | attribute missing on instance |
| `{{param}}` | action `arguments` dict | argument missing AND `param` is a declared parameter |
| Unknown `{{token}}` | — | left as-is (treated as embedded template content) |

**`override=True` instructions:** When `@instruction(override=True)` is used, the method body runs as normal Python and returns a plain `str`. That str is treated identically — appended to prose parts and substituted with the other parts.

## Public API

**`@instruction`** — marks a method as a content-resolution slot. The method name becomes the label by default; pass `label=` to override (required when the on-disk name uses a hyphen, e.g. `label="story-bank"`).

**`Instruction`** — value object carrying `text` and `module_dir`. `expand()` reads the resolved location. `Instruction.ref(host, label)` builds a reference from a live toolset instance.

**`instruction_slot_names(toolset_cls)`** — returns `frozenset[str]` of all slot names on a toolset class; used by action expansion to distinguish slots from plain tools.

## Extend

| Form | Where the prose lives | How to declare |
|---|---|---|
| **A — Inline** | String literals in `@action` body | No `@instruction` slot; write prose directly |
| **B — Section** | `## Heading` in `{slug}.md` beside the package | `@instruction def name(self) -> Instruction: ...` (method name → heading) |
| **C — File** | `name.md` or `name/` beside the package | `@instruction def name` (or `label=` for hyphenated names) |

Resolution priority when the label is looked up: **folder → file → section**. If nothing matches, the slot expands to empty string (no error).

## Dependencies

**`primitives/assets`** — `AssetLocator`, `AssetCollection`, `Asset`, `markdown_extractor` own all lookup and reading logic.
