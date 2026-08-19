# Eval

Separate tool — run after repair. Repair does not call eval.

1. Fail **scan** on the before version of the Mistake's asset.
2. Pass **scan** on the after version.
3. Pass the AI judge.
4. Generate a similar successful result and **hold that last generate for human review**.
5. If you need to confirm with the user, ask via **AskQuestion**.

If repair has not opened a WorkspaceSession on the CDD clone, eval opens one.
