# Rule: Track layer completion with track_task

Every **testing tier** and **production layer** named in the test-helpers package-tier `architecture-context.md` (corroborated by **`<context-file>`** Testing references and by **`<spec-root>/templates/tests/`**) must appear as an explicit checkbox in the engagement **`progress/`** tree. Session progress lives in those files — not in chat alone, and not by editing normative skill or spec sources.

## DO

- Resolve **`active_skill_workspace`** ( **`skill-config.json` → `workspace.active_skill_workspace`**, **`python skill-helpers/scripts/get_workspace.py`**, or user path) **before** creating checklists.

- After step **1b** (test scaffolds on disk), run **`track_task`**: create **`<workspace>/abd-architecture-code/progress/`** when missing.

- Derive checklist rows **only** from the joint authority of **`<context-file>`** (Testing references + § File Structure tier mapping), the test-helpers package-tier context file (tier names + helper layout), and **`<spec-root>`** (`rules/`, `templates/tests/`, `template/`). Do not hardcode MERN, hero-vtt, or another stack when `<spec-root>` differs.

- Write **`process-checklist.md`** — one `- [ ]` line per workflow phase (inputs → context/inventory → scaffold → layer generation → deploy/verify → validate).

- Write **`<scope-slug>-layers-checklist.md`** — for **each lowest-level sub-epic in scope**, in **spec layer order**, **three checkboxes per layer**:

  - **Scenarios** — each scenario in that tier **executed** RED then GREEN (not merely written).
  - **Tier suite** — **full test run executed** for that tier; all tests pass.
  - **Production** — minimum code for those scenarios green in the layer `<context-file>` § File Structure assigns (domain/shared, server, client, etc.); files copied from `<spec-root>/template/`.

  Add **Test execution — all tiers in scope** at the end — one line per distinct test runner or tier `<spec-root>/rules/` or `<context-file>` § Rules mandates; tick only after a **full run** passes.

  **Example (pass):** Spec lists Domain → Server → Client → E2E; sub-epic `open-account-transfer` in scope → twelve layer lines (four layers × three checkboxes) plus four scope-level execution lines with commands from the spec.

- After **each** completed layer gate in step **3**, flip **all three** lines for that sub-epic × layer to `- [x]` in **`progress/`** before starting the next layer.

- After step **4**, flip every **Test execution — all tiers in scope** line and **`- [ ] 4a`** in **`process-checklist.md`** — only after **executing** each listed suite with all tests passing.

- When resuming, open **`progress/`** first; **next work** = first unchecked line in scope ( **`track_task`** contract).

## DO NOT

- Start step **3** (first RED scenario) before **`progress/`** checklists exist with every spec layer listed.

- Mark a **test** layer done while any scenario in that tier is still failing, untested, or **not executed**.

- Mark a **tier suite** or **Test execution — all tiers in scope** line done without running the **full** test command the spec requires.

- Mark a **production** layer done while tests for that layer are not all green **and executed**.

- Advance to the next spec layer while any scenario-run, tier-executed, or production checkbox for the current layer is still `- [ ]`.

- Declare step **4** or **5** done while **Test execution — all tiers in scope** or **`- [ ] 4a`** is still unchecked.

- Skip a testing tier or production layer the joint authority of `<context-file>` / `<spec-root>` / helpers context file mandates — even when that tier has zero scenarios in the current story scope (tick with note `N/A — no scenarios in scope` only when the inventory proves zero scenarios, not to avoid scaffolding).

- Track layer completion only in chat when the user is running **`abd-architecture-code`** across sessions.
