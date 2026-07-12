---
fidelity: [specification]
artifact: [story-scenarios]
---

# Generate — Story Scenarios (specification)

## What a specification stories file is

Each `*-stories.ts` locks down the typed data contract for a story: all scenarios, all example rows, all step strings — as literal types. The tier class implementing tests is forced by TypeScript to implement every step key in `TierImpl<Scenarios>`.

One exported `const` per story, using `as const satisfies Story`. The const holds:
- `story` — English display name
- `actor` — primary actor
- `domainTerms` — key domain concepts sourced from `domain-language.md` (must not be empty)
- `evidence` — source references, e.g. `'<brief-title> §"<section-heading>"'`
- one scenario entry per logical outcome, keyed by camelCase description

## Schema (matches `story-types.ts`)

```typescript
import type { Story } from '<relative-path>/story-types'

export const <STORY_CONST>_EXAMPLES = [
  { scenario: 'Scenario 1', <param>: <value>, ... },
  { scenario: 'Scenario 2', <param>: <value>, ... },
] as const

export const <StoryPascalCase> = {
  story: '<Story verb–noun>',
  actor: '<Actor>',
  domainTerms: ['<Term>', '<Term>'],          // from domain-language.md
  evidence: ['<Source> §"<Section>"'],        // from brief / context files

  <outcomeKey>: {
    name: '<outcome description>',
    given: [
      '<precondition with {param} placeholder>',
      'And <additional precondition>',
    ],
    interactions: [
      {
        when: ['<triggering action>'],
        then: [
          '<observable outcome with {param} when {flag} is true>',
          'But <negative outcome> when {flag} is false',
        ],
      },
    ],
  },
} as const satisfies Story
```

## Scenario outline (data-driven) — the default at specification fidelity

Every scenario at specification fidelity is a scenario outline. Concrete example values (IDs, amounts, statuses, error messages) belong **only** in the `EXAMPLES` array — never inline in step strings. Use `{param}` placeholders in all step strings.

### Multiple EXAMPLES arrays when logical groups differ in shape

When valid and rejection scenarios require different columns, declare a separate named EXAMPLES array for each group:

```typescript
export const DRAFT_TRANSFER_VALID_EXAMPLES = [
  { scenario: 'Scenario 1', source_account: 'CHK-001', amount: '$50,000.00', transfer_id: 'T-001', transfer_status: 'Draft' },
] as const

export const DRAFT_TRANSFER_REJECTION_EXAMPLES = [
  { scenario: 'Scenario 2', source_account: 'CHK-001', amount: '$150,000.00', error_message: 'Amount exceeds daily transfer limit' },
  { scenario: 'Scenario 3', source_account: 'CHK-001', amount: '$50,000.00', destination_account: '', error_message: 'Destination account is required' },
] as const
```

## Full worked example

```typescript
// attach-memo-to-transfer-stories.ts — specification fidelity with scenario outlines.

import type { Story } from '../../../story-types'

export const ATTACH_MEMO_TO_TRANSFER_EXAMPLES = [
  {
    scenario: 'Scenario 1',
    existing_memo: '',
    memo_text: 'Q3 vendor settlement — invoice #4421',
    memo_saved: true,
    transfer_memo: 'Q3 vendor settlement — invoice #4421',
    error_message: '',
  },
  {
    scenario: 'Scenario 2',
    existing_memo: 'Original note',
    memo_text: 'Revised: Q3 vendor settlement — invoice #4421',
    memo_saved: true,
    transfer_memo: 'Revised: Q3 vendor settlement — invoice #4421',
    error_message: '',
  },
  {
    scenario: 'Scenario 3',
    existing_memo: '',
    memo_text: '501 characters',
    memo_saved: false,
    transfer_memo: '',
    error_message: 'Memo must not exceed 500 characters',
  },
] as const

export const AttachMemoToTransfer = {
  story: 'Attach memo to transfer',
  actor: 'Treasurer',
  domainTerms: ['Transfer', 'Memo', 'Audit Trail'],
  evidence: ['Treasury product brief §"Transfer memo and audit trail"'],

  memoAttachedOrUpdatedOnDraftTransfer: {
    name: 'Treasurer attaches or updates a memo on a draft transfer',
    given: [
      'Transfer T-001 has Memo {existing_memo}',
      'And a Memo text of {memo_text}',
    ],
    interactions: [
      {
        when: ['the Treasurer Alice attaches the Memo to Transfer T-001'],
        then: [
          'Transfer T-001 has Memo {transfer_memo} when {memo_saved} is true',
          'And Transfer T-001 remains in status Draft when {memo_saved} is true',
          'But no Memo is saved when {memo_saved} is false',
          'And a validation error {error_message} is shown when {memo_saved} is false',
        ],
      },
    ],
  },
} as const satisfies Story
```

## Naming rules

| What | Convention |
|------|-----------|
| File | `{epic-slug}/{sub-epic-slug}/{story-slug}/{story-slug}-stories.ts` |
| Story const | `PascalCase` matching the story name (e.g. `AttachMemoToTransfer`) |
| Scenario key | `camelCase` full description of the outcome |
| Examples array | `SCREAMING_SNAKE_EXAMPLES` — prefixed to describe the group (e.g. `DRAFT_TRANSFER_VALID_EXAMPLES`) |

The folder path must mirror the story map hierarchy exactly. Example: `move-money/compose-transfer/draft-transfer-details/draft-transfer-details-stories.ts`.

## domainTerms and evidence — must not be empty

- `domainTerms` — list every domain concept that appears in the scenario step strings. Source from `domain-language.md`. Non-negotiable: an empty array is a specification defect.
- `evidence` — cite at least one context document by title and section. Format: `'<document-title> §"<section-heading>"'`. Use the brief, product notes, or context files available in the `context/` folder.

## Input traps

- **Concrete enough to disagree** — if you showed these examples to a domain expert and a developer, would they argue about whether the output is correct? If not, the examples might be too vague to catch real misunderstandings.
- **Values from where** — are the example values representative of real domain data, or generic placeholders? Realistic values surface edge cases that "John Doe, $100" never will.
- **Missing state combinations** — what combinations of Given conditions have we not explored? The dangerous bugs live in states nobody thought to combine.
- **Assumed preconditions** — what has to be true before each scenario starts — and does everyone agree on that starting state, or are there hidden setup assumptions?
- **Boundary behaviors** — what happens at the edges — zero, one, many, max, just-over-max? Have we specified what the system does at the limits, or just in the comfortable middle?
- **Stubbed services** — if the scenario involves an external service or system whose response is hardcoded in a stub, is the stub declared in Given, the invocation and response expressed in When, and only the business outcome in Then? Or has the service response leaked into Then as though it were a business result?
