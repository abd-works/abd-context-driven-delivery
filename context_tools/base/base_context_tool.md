# Instructions

**BaseContextTool** is the shared base for every concrete domain (subclass it): peer-kit composer + artifact lifecycle (`generate` / `validate` / `satisfy` / `document` / `createRule`, plus `grill` / `sketch` / `iterate`).

---
# Open

One tool before lifecycle work — ensures sprint, loads context index, records root when keyed. See **Session Guidance** (`session_guidance`). Do not chain `read_context_index` or `record_context_root` when `open` is in the tool list.

```yaml
tool: open
```

---
# Generate

1. Call **`open`**. Confirm sprint slug with the user when run context has no `session=`; pass `name` / `goal` / `fidelities` on first create if needed. Follow **`session_guidance`**; use the **`active`** resource for `active.path` / `active.folder`.
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

Satisfy runs in **tool mode**: it does not inline a recipe. It hands you two tool calls to make yourself, in order — first find the problems, then fix them.

1. **`validate`** — run this first. Judge the artifact under the generator **`active`** root against the **contexts** and every named rule, and call **`scan`** on the session-rooted paths. Produce the full list of violations and coverage gaps. Do not fix anything in this step.
2. **`generate_fixes_from_validate`** — run this second, once you hold the validate report. Follow **`session_guidance`** and edit only under that layout. Generate any missing artifacts (a missing `.context/module-context.md` IS a violation — create it at the current fidelity: thin at modules with Purpose, Seam, Dependencies; full at model with + Primary use case, Rationale, Public API), then fix every reported violation in the same paths — do not invent a divergent folder.

When done, run **`validate`** again and repeat the two-call loop until it passes.

---
# Document

Take the persona of a **neutral observer** — describe what exists, do not prescribe what should exist.

1. Follow **`session_guidance`**. Observe and write under the session layout.
2. Read the **contexts** to understand the vocabulary and structure of the domain.
3. Fill the **template** scaffold with observed content — describe current state only.
4. Do not apply, suggest, or imply rules or best practices in the generated output.
5. Call **`scan`** and append all violations to the document as-is — flag them, do not correct them.
6. Save the artifact under the session layout from `session_guidance`.
7. **Live-app wraps.** DDD `/document` defaults the working area to `domain/` (overridable via `path` or `default_workspace_folder`). Put wraps under `{bounded-context}/{aggregate}/` as `{class}.ts` + `{class}.{tier}.ts` + `stubs/{system}/`. **Generate** may still use `src/`.

---
# Create Rule

One action. Do not call this if **scan** already reports a failure that matches the mistake.

Take **failed** (what went wrong on the asset) and **wanted** (what should have happened). Using **contexts**, **examples**, and **template**, evaluate a new named rule and a matching scanner that can detect that failure deterministically.

Write the rule and the scanner into **this tool** (the context tool's own guidance and `scanners/`). Then **run that rule** via **scan** on the asset and **detect a failure that matches the mistake**. If scan is clean, or the failures are not this mistake, the rule/scanner is not done.
