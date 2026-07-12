# Module: Primitives

Scope: shared types for **Instruction** expansion and **declaration** routing. Used by `@instruction` slots, `ActionExpander`, and `@generator_class_annotation` toolsets.

**Key Abstractions**:
- **Instruction**: Instruction
- **Declaration**: DeclaredProperty, DeclaredOperation

---

# Core Domain

### **Instruction**

Instruction(text, moduleDir)
------
text: InstructionText
moduleDir: ModuleDir
----
expand(): InstructionText
matchesFileOrFolder(): Boolean
loadFile(FilePath): InstructionText
loadFolder(Path): InstructionText
loadSection(FilePath, SectionHeading): InstructionText

**Instruction** — typed value; path ref or plain prose; `expand()` loads file/folder content or leaves text unchanged. `@instruction` slots return `Instruction.ref(host, label)`; `ActionExpander` calls `inline()` from `instruction_slot` when an action body references the slot.

---

### **DeclaredProperty**

DeclaredProperty(name)
------
name: MemberName
label: MemberLabel
target: MemberName | null
memberType: MemberType
defaultRoot: PathRef | null
keyDiscovery: KeyDiscovery
activeKey: ResourceName | null
----
route(instance): Instruction
resolveRoot(instance): Path
discoverKeys(instance): list[str] | null

**Declared property** — routes a base name to **label** + **target**; resolves defaults from **defaultRoot**, **keyDiscovery**, and **activeKey**; yields **Instruction**.

**Routing only** — no value on the declaration. Wired target on subclass overrides path resolution; otherwise **defaultFor** uses **defaultRoot**, **keyDiscovery**, and **activeKey**.

*Note:* Generator v2 uses `@instruction` slots and `AssetLocator` instead of DeclaredProperty for `concepts`, `examples`, and `template`. DeclaredProperty remains in the primitives package for legacy specs and routing helpers.

---

### **KeyDiscovery**

Constrained enum: `none`, `fileStems`, `subfolderNames`

**Key discovery** — how keys under **defaultRoot** are discovered on disk.

| Mode | Reads from **defaultRoot** |
|------|----------------------------|
| `none` | Single path or file — no key index |
| `fileStems` | Immediate `*` files; stem = key (e.g. `concepts/*.md`, scanner `*.py`) |
| `subfolderNames` | Immediate child directory names = keys (e.g. `formats/python`, `formats/javascript`) |

---

### **MemberType**

Constrained enum: `Instruction`

---

### **DeclaredOperation**

DeclaredOperation(name)
------
name: MemberName
label: MemberLabel
target: MemberName | null
----
route(instance): TargetOperation | null

**Declared operation** — routes a base name to a **label** on the extending class and its **target** operation. Superseded in Generator v2 by nested `@action` expansion (`self.generate_output()`).

---

# Typed primitives

| Name | Meaning |
|------|---------|
| `MemberName` | Name declared on base; Python call name (`concepts`, `generate_output`) |
| `MemberLabel` | Tag on extending class — may differ from name (`@generate_output`) |
| `TargetOperation` | Method the label is on — may differ from name (`generate_code`) |
| `MemberType` | `Instruction` |
| `KeyDiscovery` | `none`, `fileStems`, or `subfolderNames` |
| `ResourceName` | Instance attribute supplying active key (e.g. `format`) |
| `RawPath` | Unexpanded path ref before wrapped as Instruction |
| `ModuleDir` | Directory containing the owning class module |
| `FilePath` | Resolved filesystem path |
| `SectionHeading` | Markdown heading title after `§` |
| `InstructionText` | Expanded prose fed to the agent |
| `PathRef` | Raw path + optional section before resolution |

---

# Package layout

| Module | Contents |
|--------|----------|
| `instruction.py` | `Instruction` type, `expand()`, asset ref pipeline |
| `instruction_slot.py` | `@instruction` decorator, `inline()`, `expand_docstring()` |
| `instruction_routing.py` | path resolution, format keys, active resource |
| `asset_location.py` | `AssetLocator`, `AssetLocation` |
| `asset.py` / `asset_collection.py` | single asset and folder merge |
| `markdown_extractor.py` | file, section, folder read |
| `declared_property.py` | DeclaredProperty routing (legacy) |
| `declared_operation.py` | DeclaredOperation routing (legacy) |
| `declared_member.py` | shared declaration base |

Spec: `primitives/primitives_spec.py`. Behavior: `primitives/primitives-behavior.md`.
