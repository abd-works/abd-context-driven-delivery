# Instructions

## Purpose

`@instruction` turns a toolset method into an expandable content reference — a file, folder, or markdown section co-located with the package — that the AI receives as operational context when an action runs.

## Primary use case

Declare a method on a `@toolset` class and mark it `@instruction`. When an `@action` that calls the slot expands, the system resolves the label to a markdown file, a folder of assets, or a section heading inside `{slug}.md`, and injects that content into the AI's instructions. The method body is always `...`; the decorator replaces it with a slot.

Three resolution forms exist — chosen automatically by the locator in order of priority:

| Priority | What matches | Resolved as |
|---|---|---|
| 1 | `module_dir / label /` is a directory | Folder — all markdown files merged |
| 2 | `module_dir / label.md` is a file | File — full content |
| 3 | `## Label` heading exists in `{slug}.md` | Section — content under that heading |
| — | `label=` kwarg on `@instruction` | Overrides the default (method name) |

## Rationale

1. **Content lives beside code** — instruction prose is in markdown files co-located with the toolset; no free-floating prompt files scattered elsewhere.
2. **Dynamic resolution** — slots discover files and sections by name at expand time; no hard-coded paths in action bodies.
3. **Separation of concerns** — `@instruction` slots decouple static reference material (frameworks, templates, guidelines) from the imperative step-by-step recipe in `@action` bodies.

## Seam

The seam is the path from a labeled `@instruction` slot to expanded text:

1. `AssetLocator(instance, label)` walks `module_dir` — folder → file → section.
2. `Instruction.ref(host, label)` builds the value object.
3. `Instruction.expand()` reads the resolved location and returns **raw text** — no substitution happens here.
4. Action expansion calls `_inline(instance, member)` for each `self.slot_name()` call found in the `@action` body; the result is appended to `prose_parts`.
5. `_ActionExpander._build_instructions()` iterates every prose part (including text that came from instruction files) through `_substitute()` — **this is where `{{self.attr}}` and `{{param}}` placeholders are resolved**.

**Substitution contract (step 5):**

| Placeholder | Resolved from | Raises when |
|---|---|---|
| `{{self.attr}}` | `getattr(instance, attr)` | attribute missing on instance |
| `{{param}}` | action `arguments` dict | argument missing AND `param` is a declared parameter |
| Unknown `{{token}}` | — | left as-is (not a declared parameter, treated as embedded template content) |

`Instruction.expand()` does **not** touch `{{...}}` placeholders — they survive raw into the prose part and are only resolved at step 5. Do not add `{{self.attr}}` to instruction content expecting it to resolve at file-read time.

**Constraint:** An unresolvable label expands to empty string without raising. Validate slot resolution with `_instruction_ref_resolves(instance, label)`.

**`override=True` instructions:** When `@instruction(override=True)` is used, the method body runs as normal Python and returns a plain `str`. That str is treated identically — appended to `prose_parts` and substituted at step 5. This is how `partition_guidance()` in `partition_pipeline.py` injects `{{self.domain_slug}}`: the method assembles the string, returns it, and the action expander resolves the placeholder against the live instance.

## Public API

**`@instruction`** — marks a method as a content-resolution slot. The method name becomes the label by default; pass `label=` to override (required when the on-disk name uses a hyphen, e.g. `label="story-bank"`).

**`Instruction`** — value object carrying `text` and `module_dir`. `expand()` reads the resolved location. `Instruction.ref(host, label)` builds a reference from a live toolset instance.

**`instruction_slot_names(toolset_cls)`** — returns `frozenset[str]` of all slot names on a toolset class; used by the action expander to distinguish slots from plain tools.

## Three forms of instruction content (summary)

All three forms end up as entries in `prose_parts`. Every entry goes through `_substitute()` at expand time — `{{self.attr}}` and `{{param}}` work in all three.

**Form A — Inline prose (no `@instruction` slot needed)**

```python
@action
def brainstorm(self, theme: str) -> str:
    """List 5 ideas for {{theme}} in the style of {{self.cuisine}}."""
    """For each idea write a one-sentence description."""
    self.add_draft()
    return "done"
```
Each string literal in the `@action` body is injected as instruction prose. `{{theme}}` → resolved from action arguments; `{{self.cuisine}}` → resolved from instance attribute at expansion time.

---

**Form B — Named slot → section in `{slug}.md`**

```python
@instruction
def technique(self) -> Instruction: ...
```
Resolves to the `## Technique` section in `recipe_guide.md` because the method name (`technique`) matches a heading in the kit doc. Any `{{self.attr}}` placeholders in that section are substituted at expansion time — `Instruction.expand()` returns raw text; substitution happens later when the prose part is processed by `_substitute()`.

---

**Form C — Named slot → standalone file**

```python
@instruction(label="plating-rules")
def plating(self) -> Instruction: ...
```
Resolves to `plating-rules.md` beside the package. The `label=` override is needed when the on-disk name would not be a valid Python identifier. Same substitution rule as Form B — placeholders in the file content are resolved at expansion time, not at file-read time.

---

Slots are consumed inside `@action` bodies:

```python
@action
def draft_recipe(self, name: str) -> str:
    """Draft a recipe called {{name}}."""
    self.technique()  # expands to § Technique in recipe_guide.md; {{self.attr}} in that section resolves here
    self.plating()    # expands to plating-rules.md; same
    self.add_draft()
    return f"Drafted: {name}"
```

## Quick reference

| Form | Where the prose lives | How to declare |
|---|---|---|
| **A — Inline** | String literals in `@action` body | No `@instruction` slot; write prose directly |
| **B — Section** | `## Heading` in `{slug}.md` beside the package | `@instruction def name(self) -> Instruction: ...` (method name → heading) |
| **C — File** | `name.md` or `name/` beside the package | `@instruction def name` (or `label=` for hyphenated names) |

Resolution priority when the label is looked up: **folder → file → section**. If nothing matches, the slot expands to empty string (no error).

## Dependencies

**`primitives/assets`** — `AssetLocator`, `AssetCollection`, `Asset`, `markdown_extractor` own all lookup and reading logic.

## Scan violations

- **deep-module** — cleared.
- **information-hiding** — cleared.
