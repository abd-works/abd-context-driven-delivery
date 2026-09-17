# Partition

Reads source material, builds an index of what matters for this context tool, extracts the relevant passages as chunk files, and checks that nothing was missed.

Read `partition_guidance.md` before indexing — it references `{slug}.md § Scaffold` and `{slug}.md § Contexts` for what to look for. If those don't exist, use the user's description or the surrounding material.

**Parameters**

- `context` — path to the source material (markdown and/or code).
- `mode` — `one_go` (default) | `pause` | `index_only`.
- `out_root` — where to write output. Defaults to the current session folder. Set this only when you need a second distinct partition rooted somewhere else.

**Output**

- Index → `{session.path}/.context/{subject}-index.md`
- Chunks → `{session.path}/{artifact}/.context/{artifact}-segment.md` (folder name = the top-level artifact defined in `{slug}.md § Scaffold`)

`{subject}` = the source file or folder name (e.g. `HeroesHandbook.md` → `HeroesHandbook-index.md`). Not the context tool name.

---

# Step 1 — Index

Build or update an index of what's in the source material.

1. Read the source.
2. If `{subject}-index.md` already exists, **open it and add to it — do not replace it.** See **Multi-pass** below.
3. Read `partition_guidance.md` (filled in with `{slug}.md § Contexts` and `§ Scaffold`). The things the context tool cares about — epics, subjects, screens, modules — **must** appear as entries in the index. Ignoring them or just copying the source's headings as entries is a hard fail.
4. Let the context tool determine the structure, not the source's table of contents. Source chapters and files tell you where the material lives — they don't decide what the entries are.
5. **Anti-mirror check:** if your entry count matches the number of top-level headings or chapters in the source, you've mirrored it. Regroup before writing.
6. Write the index to `{session.path}/.context/{subject}-index.md` (or `{out_root}/.context/{subject}-index.md` when `out_root` is set). All context tools write to the same index file — not one file each. Each tool adds its own columns. Keep it shallow: one entry per epic, module, screen, or subject — not full stories or APIs. **See the example at the bottom of this file for the expected structure and column order.**
7. Do **not** write chunk files yet — that happens in Step 2.
8. **Config** — Some sources use ALL-CAPS labels like `NAME`, `COST`, or `DESCRIPTION` as column headers inside entries, not as entry names themselves. Without telling the tool about these, the completeness check in Step 3 will treat them as missing entries and fail. If your source has this pattern, add a `## Config` section to the index:

```markdown
## Config

<!-- partition-config
non-entry-headers:
  - NAME
  - COST
  - DESCRIPTION
short-body-pattern: \bRANKS?\b|\bPOINT
min-body-chars: 120
-->
```

- `non-entry-headers` — ALL-CAPS lines that are column labels inside entries, not entry names
- `short-body-pattern` — regex; entries with short bodies still count when this matches
- `min-body-chars` — minimum body length to count as a complete entry (default 120)

**Next step by mode:**

- `one_go` — continue to Step 2.
- `pause` — stop here; wait for the user.
- `index_only` — stop here; do not extract chunks.

---

# Step 2 — Segment

Copy the relevant passages from the source into chunk files. **Skip for `pause` / `index_only` modes.**

**Additive rule (hard):** see **Multi-pass** below. Never delete or rewrite existing chunk files. Only create new ones for passages not yet covered. Starting over requires an explicit user request.

1. Read `{session.path}/.context/{subject}-index.md`.
2. If the needed passages are already chunked, skip extraction and make sure the index links to those existing files.
3. Open the source. Use `partition_guidance.md` only to decide which passages still need a chunk file — do not start writing code or expanding the design.
4. For each new chunk, write it under the path from the index entry. The folder name comes from the top-level artifact defined in `{slug}.md § Scaffold` — an epic, subject, screen, module, or bounded context, depending on which tool you're running:
  - Default: `{session.path}/{artifact}/.context/{artifact}-segment.md`
  - e.g. `checks` → `checks/.context/checks-segment.md`
  - e.g. `powers/attack` → `powers/attack/.context/attack-segment.md` (create parent folders as needed)
  - When a later context tool adds chunks, use the same naming rules and never overwrite an existing chunk.
5. **Copy the actual text word for word.** Do not paraphrase, summarize, or sketch APIs. A short header with the source location is fine; the rest must be the original text.
6. If the same passage covers multiple index entries, either copy it into each chunk or (better) link multiple entries to the same chunk file.
7. Create the artifact folder (according to top level artifacts as named in `{slug}.md § Scaffold`) and its `.context/` subfolder as needed. Do not write code, APIs, or design notes here — only the chunk file.
8. TODOs for unclear or missing passages are fine. Do not replace missing text with invented content.
9. **Update the index** so every entry that has a chunk file links to it. Keep all existing columns. Fail if a working link was removed or a required chunk file is missing.

---

# Step 3 — Verify

Call `verify_segment_completeness` on any chunk that covers a list of named entries — things like powers, items, rules, or abilities where accidentally skipping one would leave a gap in the work downstream.

- List expected entry names in the chunk (`<!-- expected-entries … -->`) or pass them as `expected_names`.
- Layout noise configuration belongs in the `<!-- partition-config -->` block in the index — not hardcoded in the tool.
- **A chunk that covers the right length of text can still be missing entries.** Completeness failure is a hard fail — fix the chunk before running the context tool's generate step.
- After verification, update the index so every entry with a chunk links to it.

---

## Multi-pass / multi-context — ADD, do not replace

Running partition again with a different context tool adds to what's already there. It never wipes it.

### Hard fails


| Do not                                                                             | Do instead                                                                             |
| ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Delete or overwrite `{subject}-index.md` and start fresh                           | Open it and add new columns for the new context tool                                   |
| Delete or re-extract existing chunk files                                          | Leave them; map the new context tool's entries onto the chunk files that already exist |
| Replace a CE module index with a Stories-only view                                 | Keep existing columns; add Epic / Screen / Subject columns alongside them              |
| Re-extract the whole source into a new set of chunk files for the new context tool | Map new entries to existing chunks; only extract passages that aren't covered yet      |
| Create a new `out_root` just to avoid touching the existing index                  | Use the same index; `out_root` only when you genuinely need a separate partition       |


### What a later pass does

1. If `{subject}-index.md` or chunk files already exist, you're adding to them — not starting over.
2. Read `{slug}.md § Contexts` to understand what the new context tool cares about (epics, screens, subjects, modules, …).
3. Add columns for the new context tool. Link each new entry to the chunk files that already exist. One chunk may serve multiple entries; one entry may span multiple chunks. Keep all existing columns and links.
4. Go to Step 2 only for passages not yet covered by an existing chunk.
5. When done: existing chunk links still work; new columns are filled in; nothing was removed.

### Example — three passes on the same index

Each pass adds to the index without touching existing chunks.

**After CE (pass 1):** CE scaffold produces a thin module index — module path, chunk file, rough seam terms, and thin deps. Nested folders show parent/child relationships naturally (`loans/processing` depends on `loans`).

| Chunk | Module | Seam terms | Deps |
|-------|--------|------------|------|
| `catalog/.context/catalog-segment.md` | `catalog` | `Book`, `Edition`, `Search` | — |
| `loans/.context/loans-segment.md` | `loans` | `Loan`, `Return`, `Renewal` | `catalog`, `members` |
| `loans/processing/.context/processing-segment.md` | `loans/processing` | `FeeCalculator`, `RenewalPolicy` | `loans` |
| `members/.context/members-segment.md` | `members` | `Member`, `Card`, `Hold` | — |

**After Stories (pass 2):** Stories scaffold produces a thin epic index — verb–noun epics + mid-level story stubs. It adds an `Epic` column to the main table and a separate overlay mapping each epic to the chunks that cover it (because one epic typically spans multiple modules).

| Chunk | Module | Seam terms | Deps | Epic |
|-------|--------|------------|------|------|
| `catalog/.context/catalog-segment.md` | `catalog` | `Book`, `Edition`, `Search` | — | `Search Catalog` |
| `loans/.context/loans-segment.md` | `loans` | `Loan`, `Return`, `Renewal` | `catalog`, `members` | `Borrow Item`, `Return Item` |
| `loans/processing/.context/processing-segment.md` | `loans/processing` | `FeeCalculator`, `RenewalPolicy` | `loans` | `Return Item` |
| `members/.context/members-segment.md` | `members` | `Member`, `Card`, `Hold` | — | `Register Member` |

**Stories overlay**

| Chunks | Epic | Sub-epics |
|--------|------|-----------|
| `catalog/.context/catalog-segment.md` | `Search Catalog` | `Search by Title`, `Filter by Genre` |
| `loans/.context/loans-segment.md`, `catalog/.context/catalog-segment.md` | `Borrow Item` | `Check Out Item`, `Renew Loan` |
| `loans/.context/loans-segment.md`, `loans/processing/.context/processing-segment.md` | `Return Item` | `Return Book`, `Pay Fine` |
| `members/.context/members-segment.md` | `Register Member` | `Create Account`, `Issue Card` |

**After UX (pass 3):** UX scaffold produces a thin screen index — screens in domain/user language, interactions, and transitions. It adds a `Screen` column to the main table and a separate overlay. One chunk can feed more than one screen (`loans` feeds both `Loan Desk` and `My Loans`).

| Chunk | Module | Seam terms | Deps | Epic | Screen |
|-------|--------|------------|------|------|--------|
| `catalog/.context/catalog-segment.md` | `catalog` | `Book`, `Edition`, `Search` | — | `Search Catalog` | `Catalog Search` |
| `loans/.context/loans-segment.md` | `loans` | `Loan`, `Return`, `Renewal` | `catalog`, `members` | `Borrow Item`, `Return Item` | `Loan Desk`, `My Loans` |
| `loans/processing/.context/processing-segment.md` | `loans/processing` | `FeeCalculator`, `RenewalPolicy` | `loans` | `Return Item` | `Loan Desk` |
| `members/.context/members-segment.md` | `members` | `Member`, `Card`, `Hold` | — | `Register Member` | `Member Profile` |

**UX overlay**

| Chunks | Screen | Interactions | Transitions |
|--------|--------|--------------|-------------|
| `catalog/.context/catalog-segment.md` | `Catalog Search` | Search, filter | → `Item Detail` |
| `catalog/.context/catalog-segment.md`, `loans/.context/loans-segment.md` | `Item Detail` | View, check out | → `Loan Desk` |
| `loans/.context/loans-segment.md` | `Loan Desk` | Check out, return | → `My Loans` |
| `loans/.context/loans-segment.md`, `members/.context/members-segment.md` | `My Loans` | View, renew | → `Loan Desk` |
| `members/.context/members-segment.md` | `Member Profile` | View, edit | → `My Loans` |