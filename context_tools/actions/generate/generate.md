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
6b. **Large job — several turns.** Decide the source from the **ask** and what this session already produced (a sketch, a model, a format to transform — not a locked default). If that source is a whole model, sketch, or similarly large artifact, implement **one slice** in this invoke, then stop. `finish_turn` closes this turn. Continue in later generate or iterate turns — even if the user asked for everything once. Filling the whole artifact in one generate is a defect (same class as dumping a map in one iterate tick). A small implied source may finish in one turn. Do not treat a red full-tree **validate** as permission to finish the rest in this invoke; validate the slice you wrote.
7. Follow any extra build steps included in your instructions when present.
8. Run **validate** on what this turn wrote. If the job is one slice, a remaining gap in the rest of the source is the next turn, not this one. If the implied source was small enough for one turn and validate fails, fix the artifact and **validate** again until it passes.
