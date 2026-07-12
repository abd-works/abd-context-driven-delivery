# Skill Workflow

**You were sent here from a practice skill's `SKILL.md`.** Read this file **in its entirety** before generating, grilling, or validating. Order: **bootstrap** (engagement context) → **read-gates** (skill package) → generate → validate ([`rule-checklist.md`](./rule-checklist.md)).



## Bootstrap (engagement context)

**Hard gate before skill read-gates.** The skill package defines *how* to work; the engagement defines *what already exists*.

1. **`generating-skill` front matter** — if opening an existing artifact file, check for `generating-skill` in its YAML front matter ([`generating-skill-front-matter.md`](./generating-skill-front-matter.md)). If present, that key names the skill package to read in the steps below — load it even if the user did not explicitly name the skill.
2. **`cdd-context-index.md`** at the workspace root — artifact paths when present ([`folder-conventions.md`](./folder-conventions.md) § Non-standard locations).
3. **Existing deliverables** for this scope — upstream phase output and peer-perspective artifacts (filenames in [`skill-index.md`](./skill-index.md)).
4. **Decision records** — read every **`DR-*.md`** / **`ADR-*.md`** under decision folders relevant to the active skill's practice context ([`decision-record.md`](./decision-record.md)). Read **Accepted** records in full; respect **Superseded** / **Deprecated**; treat **Proposed** as unsettled. Check at minimum:
   - `docs/decisions/` (project-wide)
   - Practice folder when applicable: `docs/stories/decisions/`, `docs/domain/decisions/`, `docs/architecture/decisions/`, `docs/ux/decisions/`
   - `docs/sessions/<session>/decisions/` when working in a named session

When a choice meets DR criteria during this run, write a new record per [`decision-record.md`](./decision-record.md) — do not bury major decisions in chat or deliverable prose only.



## Output file resolution (deliverables)

**Where to write** — resolve `<deliverables-folder>` in this order:

1. **The path the user told you to use.** If the user names a file or folder, use exactly that.
2. **`cdd-context-index.md` at the workspace root.** If this file lists a path for this artifact, use that path. Update the row if it changes.
3. **Where the engagement already keeps deliverables.** Write next to existing phase output in the **same** folder.
4. **Canonical scaffold path** from [`folder-conventions.md`](./folder-conventions.md) for the active skill.
5. **The workspace root.** Last resort only.

**File name** — after the folder is resolved:

1. If the active skill has **`reference/output.md`**, read it for file name, naming pattern, or non-`docs/` rules (e.g. project test folder).
2. Otherwise use the file name in [`folder-conventions.md`](./folder-conventions.md) for this skill (typically `<artifact-stem>.md`).
3. Add a `<name>-` prefix only when disambiguation is needed.

Most skills need no `reference/output.md` — `folder-conventions.md` is enough. Add `reference/output.md` only when the skill breaks the default (tests in project tree, multiple named outputs, non-`.md` deliverable).



## Read-gates

Before authoring any artifact — **hard gate, no exceptions.** Read in this order:

1. **`rules/`** — **every** file for the active skill, **read in full**.
2. **`reference/`** — **every** file in the skill's `reference/` folder, **read in full**, including **`grill-me.md`**.
3. **`templates/`** — **every** file in the skill's `templates/` folder, **read in full** (layout contracts and filled examples — do not copy `## Instructions` blocks into deliverables).
4. **Practice family `reference/`** — read **every** file in the practice `<family>-perspective.md` shared-reference table, plus **every** practice file linked from **any** file in this skill's `reference/` folder, **read in full**.
5. **Grill mode (default — opt out only when explicitly told to skip).** Read [`grill-me-with-practice-skill.md`](./grill-me-with-practice-skill.md) and the active skill's **`reference/grill-me.md`** in full. Then run **two grilling passes**:
   1. **Grill the context** — ask each question visibly, then answer it yourself by reading the available sources (codebase, deliverables, decision records, design docs). Show the question and the answer so the user can see your reasoning.
   2. **Grill the user** — for any question the context cannot answer, surface it to the user one at a time. Every answer or assumption made in lieu of an answer must be stated back to the user before generation begins.

   Only skip grill mode when the user explicitly says so (e.g. "skip grilling", "no grill", "just generate").

**Read each file in full** — no skimming, no summarizing from memory, no skipping sections. Do not rely on the SKILL body alone. Complete **§ Bootstrap** first, then steps 1–5. No main task starts until bootstrap and read-gates are done.



## Generate (deliverables)

After read-gates, generate the artifact:

1. **Follow every rule.** Re-read each file in **`rules/`** and let every **DO**, **DO NOT**, and **Example (pass)** / **Example (fail)** direct what you write. Each rule is a shape contract — apply it line by line; do not improvise structure a rule forbids or skip a constraint a rule requires.
2. **Fill every template.** For each file in **`templates/`**, produce **one deliverable** that matches that template's headings, tables, fields, and layout **exactly**. Copy the template structure; replace placeholders and example content with engagement-specific content. Never paste template **`## Instructions`** or other maintainer-only sections into project files.
3. **Orchestration.** When the skill ships **`reference/generate.md`**, read it for workflow order, fidelity branching, and pre-scanners — run those steps before or during generation.

Deliverables contain **stakeholder-facing content only**. Do not duplicate rule or template shape in `SKILL.md`.



## Validate output

After generating, run [`rule-checklist.md`](./rule-checklist.md) in full.



## Diagram workflow (non-blocking)

After the scanner pass, check whether the active skill has **`reference/diagram-workflow.md`**. If it does, launch a **background sub-agent** (Task tool, `run_in_background: true`) with that file's contents and enough context (deliverables folder, output paths) for it to execute the CLI command independently. Do not wait for the sub-agent before returning to the user.



## Correction process

When something is wrong: identify → log → re-generate → iterate on the output until correct, then optionally improve the source skill. See `skill-helpers/instructions/log-and-fix-skill-errors` for the full loop. Put the log under the engagement tree — not inside the skill package.



## Repair loops

When the output has definitive failures (scanner violations, rule breaches, or
user-reported problems), use the appropriate repair loop:

- **[`agentic-repair-loop.md`](./agentic-repair-loop.md)** — scanners found
  violations (or the user found a gap that needs a scanner fix first); run the
  iterative fix loop as a background sub-agent until all checks pass.
- **[`manual-repair-loop.md`](./manual-repair-loop.md)** — the user already
  fixed the problem themselves; capture the original bad output and the
  corrected output as fail/pass fixtures and update `eval/cases.json`.

Both loops write fixtures to `eval/fail/` and `eval/pass/` inside the skill
package and register them in `eval/cases.json`. If the fix reveals a systematic
generator problem, improve the generator script and document in
`evals/SUMMARY.md`.
