# Satisfy

Find and fix every problem in the artifact you wrote under the generator **`session`** root.

1. Read the **`session`** resource. Edit only under that layout:
   - Documents and diagrams → `{session.path}/.context/`
   - Generated code / module folders → `{session.path}/{module}/`
   - Module-local docs → `{session.path}/{module}/.context/`
2. Run **validate** against those session-rooted artifacts.
3. Fix every reported violation in the artifact (same paths — do not invent a divergent folder).
4. When done, run **validate** again until it passes.
