# Instructions

**BaseContextTool** is the shared base for every concrete domain (subclass it): peer-kit composer + artifact lifecycle (`generate` / `validate` / `satisfy` / `document`, plus `grill` / `sketch` / `iterate`).
---
# Generate

1. Follow **`session_guidance`** and the session tools (`read_context_index`, `record_context_root`, `create_session` when needed). Resolve workspace + tool root, then use the **`active`** resource for `active.path` / `active.folder`.
2. **MUST — prove-read before asking.** Before any grill/iterate question (and before inventing options or story/module names):
   - Identify **every relevant context file referenced or implied** by the decision — not one favorite type. Typical set: `{workspace}/.context/context-index.md`, owning `*-segment.md`, `module-context.md`, session grill-answers / sketches / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Include index/overlay only for structure hints; **never** treat mid-epic stub columns as inventory.
   - **Read each of those files with the Read tool** (chunk through large ones). Grep, title lists, memory, or primer-only skims **do not count**.
   - **Prove it in the question turn:** name the path(s) read and ground options in concrete terms from them. If you cannot cite specifics from the relevant files, you have not read them — go read before asking.
   - Asking from a skim is a **defect**, same class as dumping a whole artifact in one iterate tick.
2b. **`do-not-invent-requirements`** — Do not invent requirements, status/maintenance signals, or competing command surfaces absent from source / the ask. Prefer the existing gap/fallback (or the already-specified invoke surface) over minting a new state or a second co-equal how-to-call block.
3. **`sources-scoped-to-generated-context`** — Hang `**Sources / context:**` on the node they ground: epic / sub-epic / feature / module, or a lower item (scenario, class, screen, component, …). Root or parent-level Sources are fine when those files apply to the **entire** artifact or subtree.
4. Apply all guidance and named rules in each **context** — each bullet is a requirement.
5. Match **examples** for shape, depth, and tone.
6. Fill the **template** scaffold and save the artifact under the session layout from `session_guidance`.
7. Follow any extra build steps included in your instructions when present.
8. Run **validate**. If it fails, fix the artifact and **validate** again until it passes.

---
# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Follow **`session_guidance`**. Scope judgment to artifacts under `session.path` / the session layout.
2. Use **contexts** as the rubric — report pass/fail per named context and named rule with brief evidence.
3. Call **`scan`** on the session-rooted paths under review.
4. Do not fix. Report failures for fixing, then **validate** again when ready.

---
# Satisfy

Find and fix every problem in the artifact you wrote under the generator **`active`** root — including generating any missing artifacts.

1. Follow **`session_guidance`**. Edit only under that layout.
2. **Generate missing artifacts first.** Before validate, check each module folder under `path` for a missing `.context/module-context.md`. A missing context file IS a violation — create it at the current fidelity (thin at modules: Purpose, Seam, Dependencies; full at model: + Primary use case, Rationale, Public API) before running validate. Do not skip this step.
3. Run **validate** against those session-rooted artifacts.
4. Fix every reported violation in the artifact (same paths — do not invent a divergent folder).
5. When done, run **validate** again until it passes.

---
# Document

Take the persona of a **neutral observer** — describe what exists, do not prescribe what should exist.

1. Follow **`session_guidance`**. Observe and write under the session layout.
2. Read the **contexts** to understand the vocabulary and structure of the domain.
3. Fill the **template** scaffold with observed content — describe current state only.
4. Do not apply, suggest, or imply rules or best practices in the generated output.
5. Call **`scan`** and append all violations to the document as-is — flag them, do not correct them.
6. Save the artifact under the session layout from `session_guidance`.
