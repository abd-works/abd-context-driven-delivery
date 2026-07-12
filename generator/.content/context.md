# Generator

Inheritance: **Toolset** → **agent** (`@action`, `@tool`, `@resource`) → **Generator** (`@generator`).

`@generator` merges `(YourClass, Generator)` where `Generator : Toolset`. Same **`@toolset-manifest`**, same **`python -m tools manifest`** and **`python -m tools run`**.

### Which decorator, where

| Kind of class | Class decorator | Member decorators |
|---------------|-----------------|-------------------|
| Toolset (e.g. Car) | `@toolset` | `@tool`, `@resource`, `@action` on methods |
| Generator (e.g. CleanCode) | `@generator` | `@concepts`, `@template`, … on wired targets; `@tool`, `@resource`, `@action` as needed |

**Why `@generator` on the class?** Generator subclasses rely on **DeclaredProperty** defaults (`defaultRoot`, `keyDiscovery`, `activeKey`) — CleanCode only wires `@resource format`. The class still needs `@generator` so the framework routes `self.concepts()`, `defaultFor`, and base generate/validate/satisfy.

**No `@toolset` on generator domain classes** — `@generator` already merges in Toolset. Use the decorator that matches what the class is.

Class name = domain name (`CleanCode`, not `CleanCodeGenerator`).

---

## Path refs

No `@` prefix on path refs. No `./`. Paths resolve **relative to the module directory of the class that owns the string** — move the package folder and all refs still work.

**Which module dir?** The `.py` file where the value lives. Base `@action` bodies on `Generator` resolve from `generator/`; property targets and docstrings on `CleanCode` resolve from `clean-code/`.

### Same directory

**Canonical md** — `{folder-name}.md` next to the class module:

| Ref (from `clean-code/`) | Resolves to |
|--------------------------|-------------|
| `§ Instructions` | `clean-code.md` § Instructions |
| `§ Concepts` | `clean-code.md` § Concepts |

**Sibling files** — `.md` appended when no extension given:

| Ref | Resolves to |
|-----|-------------|
| `examples` | `examples/examples.md` plus repair fixture folders under `examples/<descriptive-folder>/` |

### Subfolders (common)

| Ref (from `clean-code/`) | Resolves to |
|--------------------------|-------------|
| `formats/python/clean-code-template.py` | one template file per format |
| `formats/python/scanners/` | scanner modules for `python` format |
| `formats/` | subfolder names = format list (`python`, `javascript`, …) |
| `concepts/domain-language` | `concepts/domain-language.md` |
| `concepts/` | every `*.md` in `concepts/`; stem = concept slug |
| `{domain-slug}-template` | single template at domain root when no `formats/` |
| `scanners/` | flat scanner folder when no `formats/` |

Paths compose: `concepts/use-domain-language § Rule`, `formats/python/clean-code-template.py`.

**Template naming** — one file per format folder: `{domain-slug}-template` with extension (e.g. `clean-code-template.py`). **Domain slug** = package folder name (`clean-code`). No `templates/` subfolder.

### Cross-package (rare)

Sibling packages only — use `../` from module dir. Domain classes should not need this — base `Generator` actions already live in `generator/`.

**§ Section** — optional; extracts that heading block from the resolved markdown file.

**Instruction.expand** applies to **Instruction** properties and other instruction-bearing strings — class docstrings, action prose, tool docstrings.

---

## Instruction

An **Instruction** is a typed value — path ref or plain prose. `expand()` loads file/folder content or leaves text unchanged.

```
Instruction(text, moduleDir).expand():
  if text matches a file or folder → load and inline content
  else → leave text as-is
```

---

## Declarations

Base **Generator** declares named slots. Each slot is either a **DeclaredProperty** or **DeclaredOperation**. Neither holds a value — each **routes** a base name to a **label** on the extending class and a **target** member.

### DeclaredProperty

Routes to a target. Resolves from **defaultRoot**, **keyDiscovery**, and **activeKey** when no wired target. Yield type is **memberType**.

```
DeclaredProperty
  name: concepts | examples | template | formats | …
  memberType: Instruction
  defaultRoot: PathRef | null
  keyDiscovery: none | fileStems | subfolderNames
  activeKey: @resource name | null
```

| name | memberType | defaultRoot | keyDiscovery | activeKey |
|------|------------|-------------|--------------|-----------|
| `concepts` | Instruction | `concepts/` if folder exists, else `§ Concepts` | `fileStems` when folder | null |
| `examples` | Instruction | `examples` | `none` | null |
| `formats` | Instruction | `formats/` | `subfolderNames` | null |
| `template` | Instruction | `{domain-slug}-template` or `formats/{activeKey}/{domain-slug}-template` | `none` | `format` when `formats/` exists |

**Key discovery**

| Mode | What disk provides |
|------|-------------------|
| `none` | Single path — no key index |
| `fileStems` | Keys from filenames in **defaultRoot** (e.g. `concepts/*.md`, scanner `*.py`) |
| `subfolderNames` | Keys from immediate subdirectories (e.g. `formats/python`, `formats/javascript`, `formats/typescript`) |

**Instruction** properties: route → resolve root → `Instruction.expand()` (or catalog for `formats`).

**Scanners** — not a DeclaredProperty. Base **Generator** always exposes **`@tool scanners`** and **`@tool scan`**. **`ScannerCollection`** discovers modules under `formats/{activeKey}/scanners/` or flat `scanners/` and runs when the CLI invokes those tools. Action bodies call **`self.scanners()`** / **`self.scan()`** — tool steps like any other **`@tool`**.

**Concept slug ↔ scanner file** — hyphenated slug in markdown; underscore form in filename; optional `_scanner` suffix stripped.

**Template path** — `formats/{format}/{domain-slug}-template.{ext}`. **One template file per format folder.** `@resource format` selects the folder; **Instruction.expand** loads the single file whose name matches `{domain-slug}-template.*` in that folder. Flat fallback (no `formats/`): `{domain-slug}-template.{ext}` at domain root.

Layout per format key:

```
{domain}/
  formats/
    {format}/
      {domain-slug}-template.{ext}   ← one template file
      scanners/                      ← scanner fileStems
```

No `formats/` folder → `{domain-slug}-template` and `scanners/` at domain root.

### DeclaredOperation

Routes to a target **operation** — expander handles it like an `@action` body: prose inline, property calls expand, **tool calls invoked** (not inlined).

| Base name (call) | Label | Target (example) |
|------------------|-------|------------------|
| `generate_output` | `@generate_output` | `generate_code` |

Discovery binds each **label** on the extending class to its **target** member. Label and target may differ from the declared base name — that is what the annotation routes.

When action body calls `self.formats()`, expander resolves **`formats`** DeclaredProperty — catalog of **subfolderNames** under `formats/`, or skip when folder absent. **No wired target → use defaultRoot + keyDiscovery.**

When action body calls `self.generate_output()`, expander routes via `generate_output: DeclaredOperation`. **No target wired → skip silently** — base `generate()` keeps the call; expander emits nothing for that step.

Use `@generate_output` only when the domain needs steps beyond concepts, examples, template, and scanners — e.g. story-map orchestration. **CleanCode** has no target; generate builds from properties only.

One `@generate_output` target per class when wired — one artifact type per generator.

---

## Instructions map

Where prose lives — Python stays thin refs only.

### Framework (`generator/`)

| Section in `generator.md` | Used by |
|---------------------------|---------|
| § Purpose | `Generator` class docstring |
| § Generate | `@action generate` |
| § Validate | `@action validate` |
| § Satisfy | `@action satisfy` |
| § Scanners | `@tool scanners` |
| § Scan | `@tool scan` |

Not in v1: Bootstrap, read-gates, grill-me, diagram-workflow, correction process.

### Domain (`clean-code/`)

| Section / file | DeclaredProperty | defaultRoot | keyDiscovery | activeKey |
|----------------|------------------|-------------|--------------|-----------|
| `clean-code.md` § Instructions | class docstring | `§ Instructions` | `none` | null |
| `clean-code.md` § Concepts | `concepts` | `§ Concepts` (no `concepts/` folder) | `none` | null |
| `examples.md` | `examples` | `examples` | `none` | null |
| `formats/` subfolders | `formats` | `formats/` | `subfolderNames` | null |
| `formats/{format}/{domain-slug}-template` | `template` | `formats/{format}/{domain-slug}-template` | `none` | `format` |
| `formats/{format}/scanners/` | *(tools)* | `formats/{format}/scanners/` | — | `format` |
| `{domain-slug}-template` | `template` | `{domain-slug}-template` | `none` | null |
| `scanners/` | *(tools)* | `scanners/` | — | null |

Concepts carry named criteria (no separate rules slot).

---

## Base Generator

Subclasses wire declared properties with `@concepts`, `@examples`, `@template` where defaults are not enough. **No `@scanners`** — scanner tools are built into base **Generator**.
Optional `@generate_output` on a target operation when the domain needs extra build steps.

```python
@generator
class Generator:
    """§ Purpose"""

    @action
    def generate(self) -> str:
        """§ Generate"""
        self.concepts()
        self.examples()
        self.formats()
        self.template()
        self.scanners()
        self.generate_output()
        self.scan()
        return "When done, run satisfy, then validate."

    @action
    def validate(self) -> str:
        """§ Validate"""
        self.concepts()
        self.scanners()
        self.scan()
        return "Validation report."

    @action
    def satisfy(self) -> str:
        """§ Satisfy"""
        self.concepts()
        self.template()
        self.scanners()
        self.scan()
        return "All concepts pass."

    @tool
    def scanners(self) -> str:
        """§ Scanners"""
        ...

    @tool
    def scan(self, paths: list[str]) -> str:
        """§ Scan"""
        ...
```

**`@action`** bodies call **`self.concepts()`**, **`self.template()`**, etc. — expander inlines **Instruction** content. **`self.scanners()`** and **`self.scan()`** are **`@tool`** steps — expander lists them for the CLI like any other tool.

---

## Artifact lifecycle

1. **generate** — expand concepts, examples, template, scanners; optionally expand `generate_output`; agent builds artifact, writes to disk, calls **scan**.
2. **satisfy** — expand concepts, template, scanners; fix violations, call **scan** during the fix loop.
3. **validate** — judge persona; expand concepts and scanners; evaluate; call **scan**.
4. When validate fails → **satisfy** again → **validate** until pass.

Framework does not track artifact path or content.

---

## Example — CleanCode

```python
@generator
class CleanCode:
    """§ Instructions"""

    def __init__(self, format: str = "python") -> None:
        self._format = format
        super().__init__()

    @resource
    def format(self) -> str:
        """Active format — must be a subfolder of formats/."""
        return self._format
```

`formats/` on disk → keys via **subfolderNames**; **`@resource format`** is **activeKey** for `template` and scanner tool paths. No property overrides on CleanCode — all from DeclaredProperty defaults.

No `@generate_output` target — generate builds from **concepts**, **examples**, **template**, plus **`scanners`** / **`scan`** tools.
