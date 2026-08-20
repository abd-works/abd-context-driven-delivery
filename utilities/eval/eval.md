# Eval

Separate tool — run after repair. Repair does not call eval.

1. Fail **scan** on the before version of the Mistake's asset (`expect_scan_fails`).
2. Pass **scan** on the after version (`expect_scan_passes`).
3. Pass the AI judge.
4. Generate a similar successful result (`generate_and_judge` on the pass file) and **hold that last generate for human review**.
5. If you need to confirm with the user, ask via **AskQuestion**.

Those two lanes live on **Bdd** and **AgentBdd** spec helpers — not a new eval spec package.

The before/after pair lives under `{session.folder}/repairs/{theme}/` (sibling of `mistakes/`). `{theme}` is a concise kebab-case name of the **root-cause improvement** — what changed in the tool — not the mistake rule or the nested mistake-folder name.

If repair has not opened a WorkspaceSession on the CDD clone, eval opens one.
