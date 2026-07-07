# `/enforce` — Requirements

## Problem

A body of practice knowledge — behavior docs, generate-instructions, templates, rule checklists — accumulates over time. That knowledge exists as prose. An agent editing files in the workspace has no reliable way to discover or follow it without explicit prompt injection at every invocation.

The result: agents violate rules they would have followed had the rules been visible at the right moment and in the right form.

`/enforce` turns a prose corpus into three durable enforcement artefacts: **rule definitions**, **scanners**, and **AGENTS.md files**. Together these enforce the corpus without repeated prompt injection.

---

## Inputs

The corpus is any folder containing guidance documents. The skill recognises the following document types:

| Type | Signals | Examples |
|---|---|---|
| Behavior doc | prose rules, decision tables, guardrails | `behavior/*.md` |
| Generate instruction | step-by-step generation guidance per fidelity | `generate-instructions/*.md` |
| Template | canonical output shape | `templates/**` |
| Existing rule | already-extracted rule with scanner | `rules/<rule-name>/` |
| Checklist | rule checklist tied to a workflow | `behavior/rule-checklist.md` |

The user points at a root folder. `/enforce` reads the entire corpus under that root.

---

## Pipeline

### Step 1 — Parse: map the canonical structure

Read all corpus documents. Extract:

- **Canonical output shapes** — what a well-formed artefact looks like (file names, folder hierarchy, field names, section headings, value constraints)
- **Stated rules** — explicit "must", "never", "always", "do not" statements
- **Decision tables** — if/then producer or format decisions
- **Guardrails** — what the code path vs AI may touch; what is write-once
- **Fidelity markers** — what signals each fidelity level; what changes per level

Produce a structured **rule candidate list**: every candidate rule with its source document, quoted source text, and a short slug.

---

### Step 2 — Decompose: classify candidates

For each rule candidate, classify on two axes:

**Mechanically checkable?**
- Yes → add to scanner backlog
- No → encode as prose guidance only (AGENTS.md)
- Partially → split into a mechanical part (scanner) and a prose part (AGENTS.md)

**Scope — where does the rule apply?**
- Workspace root
- Specific folder type (e.g. any `tests/` subtree, any `evals/expected/` folder)
- Specific file type (e.g. `*-stories.ts`, `*.test.ts`)
- Specific fidelity level

Scope determines which AGENTS.md file the rule goes into and what glob pattern a scanner uses.

---

### Step 3 — Generate scanners

For each mechanically checkable rule, generate a scanner following the existing pattern in `rules/<rule-name>/`:

```
rules/
  <rule-slug>/
    <rule-slug>.md          ← rule prose: what, why, pass/fail examples
    <rule-slug>-scanner.py  ← mechanical check
    evals/
      pass/<artifact>       ← minimal passing fixture
      fail/<artifact>       ← minimal failing fixture
```

**Scanner requirements:**
- Reads a workspace path from `--workspace` argument
- Emits structured violations: `file`, `line` (where applicable), `rule`, `message`
- Exit 0 = clean; exit 1 = violations found
- Each scanner covers exactly one rule — no bundled multi-rule scanners
- Ships with at least one `pass/` and one `fail/` fixture so the scanner itself can be regression-tested

Scanner language follows the corpus language (Python for Python projects, TypeScript for TS projects). Default: Python.

---

### Step 4 — Generate AGENTS.md files

Place AGENTS.md files at the folder level that matches each rule's scope. Rules that share a scope are merged into one file.

**Placement logic:**

| Rule scope | AGENTS.md location |
|---|---|
| All files in the workspace | Root of the corpus folder |
| All files under a named subfolder type | That subfolder (e.g. `evals/AGENTS.md`) |
| A specific fidelity subtree | Deepest common ancestor of that subtree |
| A specific file extension | Deepest folder where those files live |

**AGENTS.md authoring rules:**
- Keep each file to the rules that cannot be inferred from the folder structure alone
- Do not repeat rules already stated in a parent AGENTS.md (inheritance is automatic)
- Use tables for decision rules; use code fences for naming conventions and import patterns
- Reference scanner names, not scanner paths — scanners move; names don't
- Cross-reference the source behavior doc when a rule needs more depth than a one-liner

---

## Outputs

At the end of a run `/enforce` produces:

```
<corpus-root>/
  enforce-report.md          ← what was found, what was generated, what needs human review
  rules/
    <new-rule-slug>/         ← one folder per new scanner (Step 3)
  AGENTS.md                  ← root-level guidance (created or updated)
  <subfolder>/
    AGENTS.md                ← scoped guidance (created or updated)
```

Existing `rules/` entries and existing AGENTS.md files are updated, not replaced. New content is additive. Conflicts (a rule already exists with a different definition) are flagged in `enforce-report.md` for human resolution — never silently overwritten.

---

## enforce-report.md

The report must include:

| Section | Content |
|---|---|
| Corpus summary | Documents read, rule candidates found, total count |
| Rules generated | New rule files created; scanners written |
| AGENTS.md changes | Files created or updated; rules added per file |
| Skipped candidates | Candidates that were too vague or ambiguous to encode — quoted source text, reason skipped |
| Conflicts | Existing rules that contradict a candidate — both versions shown side by side |
| Human review required | Anything that needs a decision before it can be enforced |

---

## Constraints

- `/enforce` never deletes existing rules or scanners — it only adds or updates
- It never edits the corpus source documents (`behavior/`, `generate-instructions/`, `templates/`) — those are inputs, not outputs
- It does not generate rules from a single sentence in isolation; a rule must appear in at least two places in the corpus (reinforced) or be clearly marked as a guardrail in one source to be encoded
- Scanners must be runnable in isolation — no dependency on the skill's generator or CLI

---

## Invocation

Proposed interface:

```bash
/enforce --corpus <path>          # required: root of the knowledge corpus
         [--scope <subfolder>]    # optional: limit to a subtree of the corpus
         [--dry-run]              # preview without writing anything
         [--skip-scanners]        # AGENTS.md only, no scanner generation
         [--skip-agents-md]       # scanners only, no AGENTS.md generation
         [--lang <py|ts>]         # scanner language; default: py
```

As a Cursor skill it would also accept the corpus root from the current open file's parent folder when no `--corpus` argument is given.
