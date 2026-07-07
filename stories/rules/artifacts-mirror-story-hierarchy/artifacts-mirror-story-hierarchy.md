---
fidelity: [discovery, exploration, specification, engineering]
artifact: [story-map, thin-slice, story-scenarios, story-tests]
scanner: hierarchy-mirror
kind: shape

---

# Rule: Artifacts mirror the story hierarchy

The **story map is the canonical shape**. Everything downstream — thin slice, scenarios, tests, and any code artifacts that reference stories — organises itself along the same shape.

Applies to **expanded mode** (folders and files). Consolidated mode uses sections instead of folders, but the section order and nesting still follow the map. Flat mode is exempt (it's one file).

Rule:

- **Folder / section hierarchy** follows outcome → activity → story
- **File / block per story** at the leaf — one file for the story's context, one for its scenarios, one (or a folder) for its tests
- **Every leaf under a story is *about* that story** — no orphan scenarios, no orphan tests, no stray files
- **Every story in the map has its leaves** — a story with no scenario file (past exploration) or no test file (past engineering) is a gap

## DO

- Match folder names to the verb-noun stories from the map (kebab-cased, deterministic)
- Put a `story-context.md` at any folder level that holds cross-cutting context (see `stories/templates/md/story-context.md`)
- Keep scenarios for a story in that story's folder — not in a shared `scenarios/` pile at the top
- Keep tests for a story adjacent to its scenarios — folder or sibling files

## DON'T

- Group by artifact type at the top (`all-scenarios/`, `all-tests/`) — that flattens the story hierarchy
- Split one story's scenarios across multiple folders
- Create folders for organisational convenience that don't correspond to a map node ("common", "utils" for scenarios)
- Leave a story in the map with no scenario / test folder past its fidelity — that's a coverage gap, log it (see `document-observed-quirks.md`)

## Expanded mode — folder shape

The map's outcome → activity → story chain becomes the folder chain:

```
stories/
  {outcome-verb-noun}/                    ← outcome
    story-context.md                       ← outcome-level context (optional)
    {activity-verb-noun}/                  ← activity
      story-context.md                     ← activity-level context (optional)
      {story-verb-noun}/                   ← story
        story-context.md                   ← story-level context
        scenarios/                         ← spec+ fidelity
          main-flow.md
          rejection-over-limit.md
          rejection-blocked-recipient.md
          examples-table.md
        tests/                             ← engineering fidelity
          main-flow.test.ts
          rejection-over-limit.test.ts
          stubs.ts
```

Rules:

- The folder name at each level is the verb-noun name of the map node, kebab-cased
- Rename in the map → rename the folder — never let them drift
- A story with sub-stories becomes a folder holding those sub-story folders, plus its own `story-context.md`

## Consolidated mode — section shape

Consolidated documents (one `story-map.md`, one `scenarios.md`, one `tests.md`) organise by section, and the section order mirrors the map:

```markdown
# Scenarios — Payments outcome

## Submit payment  ← activity
### Customer submits payment from web  ← story
#### Main flow  ← scenario
#### Rejection — over daily limit  ← scenario

## Refund payment  ← activity
### Merchant issues a partial refund
#### Main flow
```

Rules:

- Heading level matches the map depth (outcome = `#`, activity = `##`, story = `###`, scenario = `####`)
- Order matches the map's left-to-right / top-to-bottom order
- No scenario section without a story ancestor

## Code mirroring (engineering)

In expanded code layout, test folders match story folders:

```
src/payments/
  submit-payment/
    submit-payment.ts
    submit-payment.test.ts       ← Given/When/Then covering scenarios in
                                  stories/…/submit-payment/scenarios/
```

Rules:

- Every test file's `describe` block names the story it covers
- Every test file's `it` blocks name the scenarios / example rows it covers (verbatim, see `tests-implement-specification.md`)
- No test file that doesn't map to a story — either the story is missing from the map or the test is testing something else

## Drift check

When two representations coexist (`drawio` map + `md` scenarios, or `md` map + expanded code), check the shape on the *other* side before adding a node. Mismatches:

- Story in map, no folder → gap (fix by creating folder)
- Folder, no story in map → orphan (fix by adding to map or removing folder)
- Scenario file, no scenario in the corresponding scenario section → orphan
- Test file's `describe` doesn't match any story name → orphan

## Cross-references

- `story-map-discipline.md` — the map that everything else mirrors
- `right-size-story-nodes.md` — a story that grew a sub-tree becomes a folder-with-children
- `tests-implement-specification.md` — the engineering-fidelity version of mirroring at the test level
