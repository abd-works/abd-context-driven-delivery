# Module: Context-Driven Delivery — Generator Framework

Scope: `@generator_class_annotation` extends `@toolset` / `@action` — `Toolset` → agent actions → **Generator** with `@instruction` slots, nested `@action` calls, and `@tool` steps (v1: `CleanCode`). One manifest, one runner (`tools/`).

**Depends on existing** *(reused, not modeled here)*: `Action`, `ActionExpander`, `ActionValidator`, `ActionRunner`, `Tool`.

**Depends on primitives** *(see `primitives/domain-model.md`)*: `Instruction`, `@instruction`, `instruction_slot.inline`, `AssetLocator`.

**Core terms** *(generator-specific)*:
- **Generator** — `@generator_class_annotation` merges `(UserClass, Generator)`; declares `@instruction` slots and `@action` recipes; subclasses override **action bodies** only. Put the `.py` module inside the domain folder — **do not** override `module_dir` to point at a sibling folder.
- **Format** — instance variable `self.format`; when `formats/` exists on disk, selects `formats/{format}/` for template and scanners.

**Key Abstractions** *(this document)*:
- **ScannerCollection**: internal — disk discovery for **`@tool scan`**
- **KnowledgeGenerator**: Generator

---

# Core Domain

### **ScannerCollection**

Internal to **`@tool scan`** — not an instruction slot.

ScannerCollection(moduleDir, rootPath)
------
moduleDir: ModuleDir
rootPath: Path
----
discover(): dict[ScannerSlug, ScannerClass]
catalog(): str
get(ScannerSlug): ScannerClass
run(root: Path, files: list[Path]): ScannerReport

**Root path** — `formats/{format}/scanners/` when `formats/` exists and `self.format` is set; else flat `scanners/`. Discover by **fileStems**; slug `-` → `_`; strip `_scanner` suffix. **Violation `rule`** uses hyphenated concept slug.

Spec: `scanners/scanner_spec.py`.

---

### **Generator : Toolset**

Generator(format: FormatName | null)
------
format: FormatName | null
----
concepts(): Instruction
examples(): Instruction
template(): Instruction
generate_output(): ExpandedInstruction
generate(): ExpandedInstruction
validate(): ExpandedInstruction
satisfy(): ExpandedInstruction
repair(asset: FilePath, violation: InstructionText): ExpandedInstruction
@tool scan(files: list[FilePath]): ScannerReport
_scannerCollection(): ScannerCollection

**Class annotation** — domain classes use `@generator_class_annotation`, not direct subclass of `Generator`.

### **@instruction slots (base Generator)**

| slot | group | filter_key | resolves to |
|------|-------|------------|-------------|
| `concepts` | — | — | `{domain-slug}.md` § Concepts, or `concepts/` folder |
| `examples` | — | — | `examples/examples.md` (worked samples) and `examples/<descriptive-folder>/` (repair fixtures) |
| `template` | `formats` | `format` | `formats/{format}/{domain-slug}-template.*` when `formats/` exists |

When **`formats/`** is absent, `template` falls back to flat `{domain-slug}-template.*` at domain root. **`@tool scan`** loads from `formats/{format}/scanners/` or flat `scanners/`.

**Domain slug** — package folder name (`clean-code` → `clean-code-template.py`).

### **@action recipes (base Generator)**

| action | body references | tools |
|--------|-----------------|-------|
| `generate` | `generate`, `concepts`, `examples`, `template`, `generate_output()` | — |
| `validate` | `validate`, `concepts`, `scan()` | `scan` |
| `satisfy` | `satisfy`, `concepts`, `template` | — |
| `repair` | `repair`, `scan()`, `concepts`, `examples`, `template`, `validate()` | `scan` |

Action bodies are expanded, not executed. `@instruction` references inline prose; nested `@action` calls expand that recipe; `@tool` calls appear in the tools list. See `agents/action.py` and `primitives/instruction_slot.py`.

Action docstrings that are a **single word** resolve like `@instruction` slots — `{word}.md`, `{word}/`, then `§ {Word}` in domain markdown. Domain `module_dir` is tried first; the defining module is the fallback. Multi-word docstrings stay literal prose.

---

# Boundary Domain

### **CleanCode : Generator**

CleanCode(format: FormatName)
------
format: FormatName

On disk: `formats/python/clean-code-template.py`, `formats/python/scanners/`, etc. Only **`format`** constructor arg wired; `@instruction` defaults from base `Generator`.

### **FormatName**

Subfolder name under `formats/` (e.g. `python`, `javascript`, `markdown`). Must match a directory under `formats/`.

---

# Extensions to existing code

| Existing | Extension |
|----------|-----------|
| `Toolset` | `@generator_class_annotation` merges `(UserClass, Generator)`; `_is_generator` and `_is_toolset` set on merged class |
| `ActionExpander` | When `instance` provided: `@instruction` → `instruction_slot.inline`; nested `@action` → recursive walk; `@tool` → tool steps |
| `ActionValidator` | Permit `@instruction`, `@action`, and `@tool` references in action bodies |
| `ActionRunner` | unchanged — `python -m tools run` for tools and actions on generator classes |

| Package | Contents |
|---------|----------|
| `primitives/` | see `primitives/domain-model.md` |
| `scanners/` | `ScannerCollection`, scanner base class |
| `generator/` | `Generator`, `generator_class_annotation`, action prose (`base-generator/generate.md`, `base-generator/repair.md`, …) |

---

# Typed primitives

| Name | Meaning |
|------|---------|
| `ConceptSlug` | Hyphenated slug in concept markdown (e.g. `maintain-abstraction-levels`) |
| `ScannerSlug` | File stem in scanners root; concept slug with `-` → `_`; strip `_scanner` suffix |
| `ScannerClass` | One deterministic checker subclass of `scanner.Scanner` |
| `ScannerReport` | Deterministic scanner output |
| `ExpandedInstruction` | Expanded operation or action — prose + tool invoke steps |
| `DomainSlug` | Package folder name; `{domain-slug}-template` filename stem |
| `FormatName` | One subfolder name under `formats/`; active value from `self.format` |

Shared types (`ModuleDir`, `FilePath`, `InstructionText`, …): see `primitives/domain-model.md`.
