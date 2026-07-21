# Research: Multi-file fidelity vs commentary

**Date:** 2026-07-16  
**Question:** For AI agents generating design/code at multiple fidelity tiers, are separate per-fidelity instruction/example files justified, or is inline commentary in a single document enough?  
**Method:** Primary sources only (standards bodies, originators’ sites/specs, first-party vendor docs, source repos). Secondary blogs used only as discovery pointers, not as evidence.  
**Confidence key:** **Fetched** = retrieved and read from the owning URL in this session; **Known** = model knowledge of a well-established primary source, not re-fetched verbatim.

---

## Hypothesis

**H1 (under test):** A multi-file fidelity architecture (separate instruction/example files per fidelity tier that a generator selectively loads) will solve rendering the same design artifact at multiple levels of detail with consistent, machine-selectable rules for AI agents generating design/code.

**H2 (counter):** Commentary/annotations in a single document (“deploy / render this piece at fidelity X”) are enough — separate per-fidelity files are too much machinery.

**Subject under review (comparison only, not ground truth):** shared `clean_engineering.md` plus `fidelities/{language,modules,specification,code}/concepts.md` + `examples.*`, selected at runtime (e.g. `@focus(focus="fidelities")`).

---

## Problem Validation

### Is “multiple levels of fidelity / abstraction for the same model” a real problem?

**Yes. Established / near-commoditized in architecture description; actively re-framed for AI context packing.**

| Claim | Owning primary source | Evidence |
|---|---|---|
| Mixing levels of abstraction in one diagram is a named failure mode | C4 Model (Simon Brown) | Official intro lists “Levels of abstraction are mixed” among common diagramming problems, and motivates hierarchical maps “at various levels of detail.” ([c4model.com/introduction](https://c4model.com/introduction)) **Fetched** |
| Architecture needs multiple concurrent views for stakeholder concerns | Philippe Kruchten, IEEE Software 1995 | “4+1” view model: multiple concurrent views address separate stakeholder concerns. ([IEEE Xplore DOI](https://doi.org/10.1109/52.469759); author PDF mirrors e.g. [UBC copy](https://www.cs.ubc.ca/~gregor/teaching/papers/4%2B1view-architecture.pdf)) **Fetched (PDF mirror)** |
| Architecture descriptions are organized as viewpoints + views | ISO/IEC/IEEE 42010 | Standard specifies architecture viewpoints and views; FAQ: multiple views because notations differ and separation of concerns manages complexity. ([ISO catalogue](https://www.iso.org/standard/74393.html); [iso-architecture.org FAQ](http://www.iso-architecture.org/42010/faq.html)) **Fetched** |
| Hierarchical zoom levels are first-class documentation products | arc42 | Building-block view is a hierarchy of white/black boxes; tip: “You will not have the hierarchy in a single diagram.” ([docs.arc42.org/section-5](https://docs.arc42.org/section-5/); [Tip 5-2](https://docs.arc42.org/tips/5-2/)) **Fetched** |
| Distinct abstraction models (CIM / PIM / PSM) are normative MDA concepts | OMG MDA Guide 1.0.1 | Defines Computation Independent, Platform Independent, and Platform Specific viewpoints/models as separate views of a system. ([OMG MDA Guide PDF](https://www.omg.org/news/meetings/workshops/UML_2003_Manual/00-2_MDA_Guide_v1.0.1.pdf); [OMG MDA specs index](https://www.omg.org/mda/specs.htm)) **Fetched** |

**Who owns the canonical framing?**

- **Abstraction / zoom for software structure:** C4 Model (Brown) — “maps of your code” at Context / Container / Component / Code.  
- **Stakeholder views (not the same as zoom fidelity, but same family of problem):** Kruchten 4+1; ISO/IEC/IEEE 42010.  
- **Transformable abstraction layers for generation:** OMG MDA (CIM → PIM → PSM).  
- **AI instruction load / context:** Anthropic Agent Skills + Agent Skills open standard (progressive disclosure); Cursor Rules (selective attach).

**Counter-arguments (problem is overstated for this use case):**

- ISO 42010 explicitly does **not** prescribe format or media for an architecture description — multiple views need not mean multiple files. ([ISO 42010:2022 scope summary](https://www.iso.org/standard/74393.html)) **Fetched**
- MDA also documents **marking** a model (annotations that drive transformation) as a legitimate path, not only separate model files. (MDA Guide §3.4.4 “Marking Models”, same PDF) **Fetched**
- Cursor’s own rules docs urge **starting simple** and splitting only when mistakes repeat — implying machinery can be premature. ([cursor.com/docs/rules](https://cursor.com/docs/rules)) **Fetched**

**Maturity:** For human architecture documentation — **Established → Commoditized**. For AI-agent selective instruction loading — **Growing** (2025–2026 product standards: Agent Skills, Cursor nested rules).

---

## Solution Landscape

### Category A — Separate artifacts / views per level

**Idea:** Each fidelity/zoom is its own product (diagram, section, or file). Readers/generators consume one level at a time.

| Source | Stance |
|---|---|
| C4 Model | Four hierarchical diagram types; each zooms into the previous. ([c4model.com/introduction](https://c4model.com/introduction)) |
| arc42 | Explicit Level 1 / 2 / 3 building-block sections; hierarchy must not be one diagram. ([Tip 5-2](https://docs.arc42.org/tips/5-2/)) |
| Kruchten 4+1 | Concurrent views as separate architectural blueprints. ([1995 paper](https://doi.org/10.1109/52.469759)) |

**Adoption signals:** C4 and arc42 are widely used industry templates; Structurizr markets itself as the C4 reference tooling. ([structurizr.com](https://structurizr.com/)) **Fetched**

**Trade-offs:**

- **Strengths:** Hard separation prevents mixed abstraction; machine selection is trivial (load file/view N).  
- **Weaknesses:** Duplication and drift across levels unless there is a shared underlying model (see Category C). Cognitive overhead of “which file owns the truth?”

---

### Category B — Single artifact with progressive disclosure / selective loading

**Idea:** One package or workspace; load only the slice needed now.

| Source | Stance |
|---|---|
| Anthropic Agent Skills | Filesystem skills with three load stages: metadata always → SKILL.md when triggered → resources on demand. Explicit goal: avoid consuming context upfront. ([platform.claude.com Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)) **Fetched** |
| Agent Skills open standard | Same progressive disclosure stages (discovery → activation → execution). ([agentskills.io](https://agentskills.io/home); [github.com/agentskills/agentskills](https://github.com/agentskills/agentskills)) **Fetched** |
| Microsoft Agent Framework | Documents progressive disclosure for skills (advertise → load → resources → scripts). ([learn.microsoft.com Agent Skills](https://learn.microsoft.com/en-us/agent-framework/agents/skills)) **Fetched** |
| Cursor Rules | `alwaysApply` / `globs` / description-based / `@`-mention attach modes; nested `AGENTS.md` scoped by directory; “Keep rules under 500 lines; Split large rules into multiple, composable rules”; “Start simple.” ([cursor.com/docs/rules](https://cursor.com/docs/rules)) **Fetched** |
| OpenAI prompt engineering | Prefer structured, labeled instruction sections; `instructions` vs input roles; keep guidance clear and avoid conflicting repetition. Does **not** prescribe multi-file fidelity tiers. ([OpenAI Prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering); [GPT-4.1 Prompting Guide](https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide)) **Fetched** |

**Trade-offs:**

- **Strengths:** Matches AI context economics; first-party agent platforms treat selective loading as the design principle.  
- **Weaknesses:** Requires a loader/router (globs, descriptions, focus tags). Over-splitting creates navigation tax. OpenAI guidance still works fine as **one well-structured prompt** when size is modest.

---

### Category C — Model-driven / transformation pipelines (one model, many renderings)

**Idea:** Shared semantic model; transformations or view definitions produce each fidelity.

| Source | Stance |
|---|---|
| OMG MDA | CIM / PIM / PSM as viewpoints; mappings and transformations produce platform-specific artifacts; “marking” can annotate the PIM for transformation. ([MDA Guide 1.0.1](https://www.omg.org/news/meetings/workshops/UML_2003_Manual/00-2_MDA_Guide_v1.0.1.pdf)) |
| Structurizr DSL | **Single model**, multiple `views` (systemContext, container, component, …) rendered from the same elements/relationships. ([structurizr.com](https://structurizr.com/); [DSL tutorial](https://docs.structurizr.com/dsl/tutorial)) **Fetched** |

**Trade-offs:**

- **Strengths:** Consistency across levels; closest analogue to “same design, different fidelity.” Avoids copy-paste of concepts into four nearly identical files.  
- **Weaknesses:** Requires a model + view/transform machinery (higher upfront cost). Full MDA-style tooling historically failed many teams when overbuilt — the *problem* of multiple abstractions remained; the *heavy toolchain* did not always pay off. (**Known** industry history; MDA itself is primary; adoption failure rates are not quantified in OMG docs.)

---

### Category D — Comment / annotation-driven generation

**Idea:** One source document/codebase; tags steer generators; tooling ignores unknown tags.

| Source | Stance |
|---|---|
| Oracle Javadoc | Documentation comments + `@` tags are parsed to generate structured API docs from a single source tree. ([Documentation Comment Spec, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/specs/javadoc/doc-comment-spec.html)) **Fetched** |
| OpenAPI Specification | `x-` specification extensions add generator/tool metadata inside one OpenAPI document; tools may ignore unsupported extensions. ([OAS 3.1.0 §4.9](https://spec.openapis.org/oas/v3.1.0.html#specification-extensions)) **Fetched** |
| MDA marking | Marks on a model supply transformation parameters without necessarily forking the entire model. (MDA Guide §3.4.4) **Fetched** |

**Trade-offs:**

- **Strengths:** Single source of truth; commentary is enough when deltas are local (“omit this at language fidelity”). Extremely high adoption (Javadoc, OpenAPI).  
- **Weaknesses:** Annotations that encode *large* divergent generation rules become unreadable; generators must implement filter semantics reliably; AI models may still “see” annotations for other fidelities unless a preprocessor strips them.

---

### Category E — AI-agent instruction packing (AGENTS.md vs layered rules)

| Pattern | Primary guidance |
|---|---|
| Single `AGENTS.md` | Cursor: “simple alternative… without the overhead of structured rules.” Nested files for area-specific guidance. ([cursor.com/docs/rules](https://cursor.com/docs/rules)) |
| Layered / composable rules | Cursor: split large rules; attach by glob/description/`@`; reference files instead of inlining. Same page. |
| Skill packages | Anthropic / agentskills.io: metadata cheap; body and references deferred. |

**Adoption signals:** Cursor Project Rules + AGENTS.md are first-party product surfaces; Agent Skills is an open standard with Anthropic origin and Microsoft adoption. **Fetched**

---

## Approach Comparison

### When separate files / views per level win

Evidence supports separation when **at least one** of these holds:

1. **Output shape diverges** (C4: different diagram types; MDA: different model kinds; arc42: separate level sections).  
2. **Mixing levels is a documented failure mode** you must hard-prevent (C4 lists mixed abstraction as a problem).  
3. **Context must exclude wrong-tier rules** — Agent Skills and Cursor attach modes exist specifically so irrelevant instructions do not occupy the window.  
4. **Examples differ enough** that one shared example file would teach the wrong shape (Cursor: provide concrete examples / referenced files; Anthropic: resources loaded only when needed).

For a generator that must emit **language vs modules vs specification vs code**, if each tier has different required sections, typing rules, and example idioms, selective multi-file loading is the pattern first-party AI platforms endorse.

### When inline commentary wins

Evidence supports commentary when:

1. **Deltas are local omit/add rules** on a shared structure (OpenAPI `x-`, Javadoc tags, MDA marks) — one document, many tool interpretations.  
2. **Total instruction volume is small** — Cursor: start simple; prefer one readable AGENTS.md until pain appears.  
3. **Human editability of “the whole story”** matters more than token isolation — ISO 42010 does not require multiple files.  
4. **You lack a reliable loader** — annotations without a strip/filter step still put all fidelities in the model’s context, which **does not** solve instruction conflict for LLMs (unlike Javadoc’s deterministic parser).

Critical caveat for AI: annotation-driven generation works in Javadoc/OpenAPI because a **deterministic tool** interprets tags. An LLM given “at language fidelity omit types; at specification add signatures” in one blob can still bleed rules across tiers. Commentary is “enough” only if you also **preprocess** (strip non-selected annotations) or the rule set is tiny and non-conflicting.

### Modeling standards: separate products or annotations?

| Standard / practice | Separate products? | Annotations on one product? |
|---|---|---|
| C4 | Separate diagrams per level | Not primary; zoom metaphor implies distinct diagrams |
| arc42 | Separate hierarchical sections/levels | Same doc *template*, not one mixed diagram |
| ISO 42010 | Multiple views | Format unconstrained — could be one AD with multiple views |
| MDA | Separate CIM/PIM/PSM *views* | Marks as annotations for transformation |
| Structurizr | Multiple **views** | One **model** — hybrid |

**Closest primary-source analogue to the subject under review:** Structurizr’s *shared model + per-view selectors*, not four fully duplicated concept trees, and not a single annotated mega-prompt without filtering.

### Evidence on context-window / instruction selection (AI)

| Vendor/standard | Selective loading? | Implication for H1 vs H2 |
|---|---|---|
| Anthropic Skills | Yes — progressive disclosure by design | Favors multi-file / multi-resource packaging |
| Agent Skills standard | Yes — discovery/activation/execution | Same |
| Cursor Rules | Yes — always / glob / intelligent / mention; nested AGENTS.md | Favors split when scoped; also endorses simple single file |
| OpenAI prompting docs | Structured sections in one prompt; no first-party “fidelity tiers” API | Neutral — does not require multi-file; does require clear, non-conflicting structure |

No primary source found that says “put all fidelity rules in one file with prose conditionals and load everything.” Progressive disclosure is the explicit opposite.

---

## Recommendation

**Verdict: Hybridize — do not double down on four fully separate concept+example trees, and do not simplify to commentary alone.**

### Against pure H1 (full multi-file machinery)

- Duplicating *shared* concepts into four fidelity folders recreates the consistency problem C4/Structurizr solved with **one model, many views**.  
- Cursor’s “start simple / split when needed” and the sunk-cost risk of MDA-era over-tooling both warn against building a four-tier file lattice before measuring failure modes.  
- If language→code deltas are mostly “omit X / add Y,” four `concepts.md` files are **too much machinery** relative to annotated shared rules plus a strip/select step.

### Against pure H2 (commentary-only)

- For AI generators, commentary without **mechanical exclusion** of non-selected tiers is weaker than Javadoc/OpenAPI’s deterministic tag processors. LLMs are not guaranteed to ignore “at code fidelity…” lines while emitting language-fidelity output.  
- First-party agent platforms (Anthropic Skills, Cursor Rules, agentskills.io) converge on **selective loading of separate instruction units**, not mega-files with inline conditionals.  
- When examples and required shapes diverge by tier, mixed instructions recreate C4’s “levels of abstraction are mixed” failure — but inside the prompt.

### Recommended shape (maps to primary analogues)

```
clean_engineering.md          # shared model / vocabulary (Structurizr "model", MDA PIM-ish core)
fidelities/
  <tier>/
    render-rules.md           # view-specific omit/add/shape rules (Structurizr "views")
    examples.*                # only if examples diverge; else one examples/ with tags + filter
```

Generator loads: **shared + exactly one tier**. Shared content is not duplicated. Commentary/tags may appear *inside* the shared file for tiny deltas, but **tier-specific rule blocks that conflict must live in the selected file** (or be stripped by a preprocessor before the LLM sees them).

### Decision rule (pragmatic)

| Signal | Move |
|---|---|
| Tier rules fit on one page of omit/add deltas; examples identical | Commentary + preprocess (or even one file + `@focus` section extract) |
| Tier outputs differ in structure; examples conflict; agents mix fidelities | Separate render-rule (+ example) files, selective load |
| Already invested in four full concept trees with duplicated prose | Treat as **sunk cost** unless drift/eval failures justify it — collapse shared concepts upward |

**Recommendation label:** **Hybridize** (shared concepts + selectively loaded per-fidelity render rules/examples).  
Not “double down” on full per-tier concept duplication.  
Not “simplify to commentary” as the sole mechanism for conflicting generation rules.

**Confidence:** High on problem existence and AI progressive-disclosure trend (**Fetched** primary docs). Medium on exact file layout for *this* clean-engineering subject (subject is defendant; layout is engineering judgment informed by Structurizr/MDA/Cursor patterns).

---

## Sources

### Architecture / modeling (primary)

1. Simon Brown — C4 Model Introduction. https://c4model.com/introduction  
2. Philippe Kruchten — “Architectural Blueprints—The ‘4+1’ View Model of Software Architecture,” *IEEE Software* 12(6), 1995. https://doi.org/10.1109/52.469759 (PDF mirror used: https://www.cs.ubc.ca/~gregor/teaching/papers/4%2B1view-architecture.pdf)  
3. ISO/IEC/IEEE 42010:2022 — Architecture description. https://www.iso.org/standard/74393.html  
4. ISO/IEC/IEEE 42010 FAQ. http://www.iso-architecture.org/42010/faq.html  
5. arc42 — Building block view. https://docs.arc42.org/section-5/  
6. arc42 — Tip 5-2. https://docs.arc42.org/tips/5-2/  
7. OMG — MDA Guide Version 1.0.1. https://www.omg.org/news/meetings/workshops/UML_2003_Manual/00-2_MDA_Guide_v1.0.1.pdf  
8. OMG — MDA Specifications index. https://www.omg.org/mda/specs.htm  
9. Structurizr — product home (single model, multiple views). https://structurizr.com/  
10. Structurizr — DSL tutorial. https://docs.structurizr.com/dsl/tutorial  

### Annotation / generation (primary)

11. Oracle — Documentation Comment Specification for the Standard Doclet (JDK 21). https://docs.oracle.com/en/java/javase/21/docs/specs/javadoc/doc-comment-spec.html  
12. OpenAPI Initiative — OpenAPI Specification 3.1.0 §4.9 Specification Extensions. https://spec.openapis.org/oas/v3.1.0.html#specification-extensions  

### AI agent instruction packing (primary)

13. Cursor — Rules. https://cursor.com/docs/rules  
14. Anthropic — Agent Skills overview. https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview  
15. Agent Skills open standard — Home. https://agentskills.io/home  
16. agentskills/agentskills — GitHub. https://github.com/agentskills/agentskills  
17. Microsoft Learn — Agent Skills. https://learn.microsoft.com/en-us/agent-framework/agents/skills  
18. OpenAI — Prompt engineering. https://developers.openai.com/api/docs/guides/prompt-engineering  
19. OpenAI Cookbook — GPT-4.1 Prompting Guide. https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide  

### Explicitly not used as evidence

- Secondary tutorial/blog summaries of C4, MDA, or Cursor “progressive disclosure” (except as discovery).  
- The subject `clean_engineering/` tree (defendant only).
