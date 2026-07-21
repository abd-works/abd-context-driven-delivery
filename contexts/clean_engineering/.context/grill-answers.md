# Grill Answers

### clean_engineering Generator ? what it is

clean_engineering is a new generator (using generator/generator.py @concept_class_annotation) that owns the canonical OO theory ? class, responsibility, relationship, inheritance, subtypes. DDD and clean_code will later consume from it as a common base. Lives entirely in abd-context-driven-delivery. Not specific to business domains or ubiquitous language.

### One generator class with fidelity parameter

Single clean_engineering class using @concept_class_annotation. Constructor takes fidelity (language, model, specification) and format (python, typescript, etc). One invocation: action generate with context.fidelity and context.format. Rules, templates, and examples organized in fidelity-specific subdirectories.

### Code-first output with format defaults

Primary output is code at every fidelity except language. Defaults: language -> markdown, model -> code, specification -> code. User can override. Prose/intent goes into .context/domain-context.md alongside code folders, not as inline comments.

### Stories-style model/code/diagram architecture

Follow abd-skills/contexts/stories/src/stories architecture. model/ holds canonical OO nodes (Class, Property, Operation, Relationship). code/ holds per-language renderers (python/, typescript/, java/). diagram/ holds diagram renderers (drawio/). document/ holds markdown renderers. Each channel subclasses model nodes and overrides create_child_* factories. Uniform callable surface: parse, render, sync.

### Transform is a tool on the generator class

Transform is a @tool method on the clean_engineering generator (like scan and claim), not a separate CLI or agent. Does deterministic parse(format A) -> canonical model -> render(format B). Moves sideways between formats at the same fidelity. Fidelity upgrades are agent work via the generate action.

### Fidelity level outputs

Language (default md): named concepts with responsibilities and collaborations as prose. Simple class files with sentence comments when in code. Model (default code): classes with operations, relationships, methods ? not implemented (shells/stubs). Specification (default code): type-safe, relationships annotated on actual properties, public operations shelled out, internals as shells. Engineering is clean_code.

### Workflow ? transform then upgrade

When switching format during a fidelity upgrade (e.g. language in md to model in code): agent calls transform tool first (md -> code at language level), then runs generate at the new fidelity on the code output. Transform moves formats. Generate upgrades fidelity. They compose.

### Intent — clean_code as a consumer of clean_engineering

grill-answers.md already records: 'DDD and clean_code will later consume from it as a common base.' clean_engineering owns the OO theory (class identity, state, behavior, relationships, inheritance, invariants). CleanCode adds implementation discipline on top (naming, function discipline, error handling, comments). The boundary is: clean_engineering = structure of OO thought; CleanCode = how to write that structure cleanly.

### Whole file — why CleanCode cares about all of ooad.md

CleanCode operates at implementation fidelity, but every clean_engineering primitive has a direct implementation expression. Relationships -> use-explicit-dependencies (composition = owns lifecycle, pass in constructor; association = inject). Subtypes -> Liskov applies directly when writing inherited classes. Invariants -> enforce-encapsulation, what the constructor must guarantee. The model-level primitives are not irrelevant to clean code — they are the design layer that clean code implements. Loading all of ooad.md is correct.

### Function discipline = operation discipline — vocabulary fix, not restructuring

clean-code.md's 'Function discipline' section uses the wrong word. In clean_engineering, a function is an operation. Renaming the section and its rules (keep-operations-single-responsibility, keep-operations-small-focused, use-clear-operation-parameters, etc.) aligns it with ooad.md vocabulary. No ownership change needed — operation discipline belongs in clean-code.md, but expressed in clean_engineering terms. clean_engineering already models operations (verb phrase, stateless or stateful, has parameters and return type). CleanCode adds the implementation rules that constrain how operations are written.

### Engineering is the 4th fidelity — CleanCode is not a peer, it completes the progression

clean_engineering fidelity axis: language -> model -> specification -> engineering. At engineering fidelity, clean_engineering outputs fully implemented code with all bodies completed. Clean code discipline (operation size, naming, error handling, encapsulation) applies specifically at this fidelity because engineering is where implementations are written. Earlier fidelities produce structural artifacts (prose, shells, stubs). CleanCode is not a separate quality layer applied at all fidelities — it is the engineering fidelity itself.

### Mechanism — Option A with shared common areas

Engineering fidelity is added directly to clean_engineering: _VALID_FIDELITIES gains 'engineering', contexts/clean_engineering/fidelities/engineering/ holds the guide and rules. Common areas (class design rules, operation discipline vocabulary) are shared across fidelities — not duplicated in the engineering folder. CleanCode's clean-code.md content migrates into engineering fidelity files. CleanCode generator becomes an alias or is retired. Sharing mechanism for common areas is TBD — could be a shared instruction base loaded by all fidelities, or an engineering guide that references/includes the common sections.

### Sharing via Concepts — ooad.md is the shared base, not a folder

ooad.md already has a Contexts section. That is the shared base loaded by every fidelity. Class design rules, properties, operations, relationships, inheritance — all in Concepts. No _shared/ folder, no specification-as-base inheritance. Each fidelity guide adds only what is specific to it. Engineering adds: operation discipline, naming, error handling, comments, full implementation bodies. Common concepts are shared by default because they live in ooad.md Concepts.

### Rules that move to ooad.md Concepts from engineering

Four rules move from engineering fidelity to ooad.md Concepts because they shape the object model signature: keep-operations-single-responsibility (splits reveal missing operations or classes), use-clear-operation-parameters (3+ params reveal a missing value object class), use-intention-revealing-names (design constraint on all clean_engineering elements), use-consistent-naming (domain vocabulary discipline). separate-concerns, maintain-abstraction-levels, and use-exceptions-properly stay in engineering — they are implementation practices, not model-shaping design rules.

### Template strategy — fidelity guides + annotated engineering templates

No per-format examples needed for language/model/specification. One fidelity guide per fidelity (format-agnostic, already done). Engineering is the exception: one template per format, annotated with which fidelity introduced each element (language / model / specification / engineering). The engineering template is the complete reference — the AI reads fidelity annotations and includes only elements at or below the requested fidelity. Collapses 4x7=28 to 4 fidelity guides + 7 annotated engineering templates = 11 files. Existing clean_engineering-examples.* per format become redundant.

### CE partition ? code-research ? grilling started

Plan under grill ? abd-code-research Pass 1 feeds clean_engineering index; Pass 2 deep-dives replace raw markdown segments per module. Sketch at contexts/clean_engineering/.context/partition-code-research-sketch.md.

### Index entries are CE modules (Pass 1 informs)

Index rows are clean_engineering modules, not 1:1 research paths. Pass 1 Explorer (research-paths + sources) informs naming and evidence; the CE lens groups/names modules (purpose, seam, rough public API). Research paths may span or split across modules.

### Research paths contribute to modules; segment per module

Pass 1 research paths are contributed/mapped onto CE modules (many paths may feed one module). Segment is one Pass-2-shaped file per module that synthesizes the contributing paths ? not one file per research path.

### Index path is always .context/{concept}-index.md

Index naming/location does not change for code-research. Always write .context/{concept}-index.md (e.g. .context/clean_engineering-index.md). Not research-paths.md as the index; Pass 1 informs that file. Naming stays the Context.partition convention.

### Index path always .context/{concept}-index.md

Index naming/location does not change for code-research. Always write .context/{concept}-index.md (e.g. .context/clean_engineering-index.md). Pass 1 informs that file; do not rename to research-paths.md or park the index under code-research/.

### Code-research instructions live in CE partition.md

Put Pass 1 ? index and Pass 2 ? per-module segment guidance in contexts/clean_engineering/partition.md. Base Context index/segment prose stays generic.

### Segment naming same as all concepts

No CE-special segment names. Use the same convention as every concept ? files named from the guiding structure (e.g. {name}-segment.md per base segment guidance). Only the content process differs (Pass 2 deep-dive shape via CE partition.md).

### CE partition.md updated for code-research

Wrote Pass 1?index and Pass 2?per-module segment guidance into contexts/clean_engineering/partition.md. Sketch closed.

### I{Class} public seam — modules / specification / code

modules creates I{Class} only (empty public props/ops as interfaces). specification adds Class(IClass) in the same file: public members filled, private members empty interfaces on Class only, invariants as comments, interactions as @interaction abstracts on Class. code fills remaining empties on Class, drops interactions, keeps invariant comments, leaves I{Class} for the seam and hand-written fakes. Java uses interface for I{Class}. Empty vs filled inferred from body — no abstract flag on the model. Enforce in class_model renderers + docs/templates.
