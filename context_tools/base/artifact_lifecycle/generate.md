# Generate

1. Follow **`session_guidance`** and the session tools (`read_context_index`, `record_context_root`, `create_session` when needed). Resolve workspace + tool root, then use the **`session`** resource for `session.path` / `session.folder`.
2. **MUST — prove-read before asking.** Before any grill/iterate question (and before inventing options or story/module names):
   - Identify **every relevant context file referenced or implied** by the decision — not one favorite type. Typical set: `{workspace}/.context/context-index.md`, owning `*-segment.md`, `module-context.md`, session grill-answers / sketches / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Include index/overlay only for structure hints; **never** treat mid-epic stub columns as inventory.
   - **Read each of those files with the Read tool** (chunk through large ones). Grep, title lists, memory, or primer-only skims **do not count**.
   - **Prove it in the question turn:** name the path(s) read and ground options in concrete terms from them. If you cannot cite specifics from the relevant files, you have not read them — go read before asking.
   - Asking from a skim is a **defect**, same class as dumping a whole artifact in one iterate tick.
3. **`sources-scoped-to-generated-context`** — Hang `**Sources / context:**` on the node they ground: epic / sub-epic / feature / module, or a lower item (scenario, class, screen, component, …). Root or parent-level Sources are fine when those files apply to the **entire** artifact or subtree.
4. Apply all guidance and named rules in each **context** — each bullet is a requirement.
5. Match **examples** for shape, depth, and tone.
6. Fill the **template** scaffold and save the artifact under the session layout from `session_guidance`.
7. Follow any extra build steps included in your instructions when present.
8. Run **validate**. If it fails, fix the artifact and **validate** again until it passes.
