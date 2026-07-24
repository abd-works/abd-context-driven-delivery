# Generate

1. Read the **`session`** resource from the toolset (constructor `context.session`). All outputs land under that root:
   - Documents and diagrams → `{session.path}/.context/`
   - Generated code / module folders → `{session.path}/{module}/`
   - Module-local docs → `{session.path}/{module}/.context/`
2. **MUST — prove-read before asking.** Before any grill/iterate question (and before inventing options or story/module names):
   - Identify **every relevant context file referenced or implied** by the decision — not one favorite type. Typical set: owning `*-segment.md`, `module-context.md`, session grill-answers / sketches / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Include index/overlay only for structure hints; **never** treat mid-epic stub columns as inventory.
   - **Read each of those files with the Read tool** (chunk through large ones). Grep, title lists, memory, or primer-only skims **do not count**.
   - **Prove it in the question turn:** name the path(s) read and ground options in concrete terms from them. If you cannot cite specifics from the relevant files, you have not read them — go read before asking.
   - Asking from a skim is a **defect**, same class as dumping a whole artifact in one iterate tick.
3. Apply all guidance and named rules in each **context** — each bullet is a requirement.
4. Match **examples** for shape, depth, and tone.
5. Fill the **template** scaffold and save the artifact under the session layout above.
6. Follow any extra build steps included in your instructions when present.
7. Run **validate**. If it fails, fix the artifact and **validate** again until it passes.
