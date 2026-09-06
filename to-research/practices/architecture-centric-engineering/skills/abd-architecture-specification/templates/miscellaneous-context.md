<!--
  Template: miscellaneous-tier architecture-context.md
  Use for FOLDERS that are small enough to describe in a sentence or two, OR
  grab-bags of unrelated utilities where each entry deserves a one-liner.

  PLACEMENT: lives in the folder it documents. Referenced by the main spec
  using a workspace-root link.

  USE WHEN:
   - The package is a one-class singleton or thin SDK wrapper with no meaningful
     surface area (e.g. a Logger, a Date helper).
   - The folder contains unrelated files with no shared abstraction — a true
     grab-bag (e.g. src/helpers/).
   - Some entries inside are legacy / dead code and you want the next reader to
     know that without spelunking.

  USE A DIFFERENT TEMPLATE WHEN:
   - There is a templated pattern → mechanism-context.md
   - The package has real surface area with multiple consumers → package-context.md

  Two flavours are shown below. Keep ONE; delete the other and the leading
  "Template:" instruction block before shipping.
-->

---
generating-skill: abd-architecture-specification
type: utility
fidelity: specification
---                       -->
<!-- ============================================================ -->

# {{PackageName}}

{{One or two sentences. What it is, what it does, who uses it. Done.}}

<!-- ============================================================ -->
<!-- FLAVOUR 2: grab-bag of unrelated utilities                   -->
<!-- ============================================================ -->

# {{FolderName}}

{{One sentence framing: e.g. "Grab-bag of utility modules. Each folder (and
loose file) is independent -- there is no shared abstraction across them."}}

---

**`{{subfolderOrFile1}}`**
{{One sentence on what it does. If it is legacy / dead code / deprecated, say
so explicitly. If it points to a deeper context file, link to it.}}

**`{{subfolderOrFile2}}`**
{{...}}

**`{{subfolderOrFile3}}`**
{{...}}

{{...one bold-name entry per subfolder or loose file. Order: active code first,
legacy last. Do not invent groupings unless the folder genuinely has them.}}
