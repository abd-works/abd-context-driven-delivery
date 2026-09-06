// <slug>-stories.ts
//
// Source of truth for stories in this sub-epic.
// Each exported const is one story.  Spec files import from here — NOT from a
// separate *-scenarios file.
//
// TYPES (declared once, imported everywhere):
//   import type { Step, AcceptanceCriterion, Background } from '../../story-types'
//   (adjust relative depth as needed)
//
// BACKGROUND (optional, file-level):
//   Shared Given setup that applies to every story in this sub-epic.
//   export const BACKGROUND = [...] as const satisfies Background
//
// ACCEPTANCE CRITERIA:
//   Always an array of AcceptanceCriteria, even when there is only one.
//   Each AcceptanceCriterion is a Step[].  Keywords: given / when / then / and / but.
//   Multiple When–Then pairs in one story → multiple entries in the array.
//
// SCENARIOS:
//   Each scenario key is a camelCase description of the behaviour.
//   Steps use the same Step type: { given }, { when }, { then }, { and }, { but }.
//   One scenario per AC (or per notable path within an AC).
//
// SCENARIO OUTLINES (data-driven):
//   1. Export a top-level EXAMPLES array above the story const.
//   2. Use {param} placeholders inside step strings.
//   3. Spec drives with: it.each(EXAMPLES)(`${STORY.key.name} – $scenario`, ...)
//
// Domain terms → **bold**.  Literals / values → *italic*.

import type { Step, AcceptanceCriterion, Background } from '../../story-types'

// =============================================================================
// FIXTURE CONSTANTS
// =============================================================================

export const ROUTE = '/<path>'

export const EXPECTED_ELEMENTS = {
  heading: '<heading text>',
  submitButton: '<button label>',
} as const

// =============================================================================
// BACKGROUND  (optional — shared Given context for every story in this file)
// =============================================================================

export const BACKGROUND = [
  { given: '<shared precondition that applies to all stories in this sub-epic>' },
] as const satisfies Background

// =============================================================================
// STORY: <First Story Display Name>  (plain scenario)
// =============================================================================

export const STORY_EXPORT_NAME = {
  story: '<Story Display Name>',
  actor: '<Actor Name>',

  // Each inner array is one acceptance criterion (one When–Then sequence).
  // Use multiple inner arrays when the story has multiple ACs or paths.
  acceptance_criteria: [
    [
      { when: 'the **<actor>** <triggering condition>' },
      { then: 'the **<term>** <observable outcome>' },
      { and: '<additional observable outcome>' },
    ],
  ] as const satisfies readonly AcceptanceCriterion[],

  domain_terms: ['<term 1>', '<term 2>'] as const,
  evidence: ['<source file>', '<research doc>'] as const,

  // Scenario for AC[0] — happy path
  methodNamedScenarioKey: {
    name: '<scenario name in plain words>',
    steps: [
      { given: '<precondition>' },
      { when: '<action>' },
      { then: '<observable outcome 1>' },
      { and: '<observable outcome 2>' },
    ] as const satisfies readonly Step[],
  },

  // Scenario for AC[0] — negative path (if applicable)
  negativeScenarioKey: {
    name: '<negative scenario name>',
    steps: [
      { given: '<alternate precondition>' },
      { when: '<alternate action>' },
      { then: '<negative outcome>' },
      { but: '<state that does NOT change>' },
    ] as const satisfies readonly Step[],
  },
} as const

// =============================================================================
// STORY: <Second Story Display Name>  (scenario outline — data-driven)
// =============================================================================

export const SECOND_STORY_EXAMPLES = [
  { scenario: 'Scenario 1', param_a: '<value>', param_b: true,  expected_result: '<outcome 1>' },
  { scenario: 'Scenario 2', param_a: '<value>', param_b: false, expected_result: '<outcome 2>' },
] as const

export const SECOND_STORY_EXPORT_NAME = {
  story: '<Second Story Display Name>',
  actor: '<Actor Name>',

  acceptance_criteria: [
    [
      { when: 'the **<actor>** sets {param_a}' },
      { then: 'result is {expected_result}' },
    ],
    [
      { when: 'the **<actor>** sets a different {param_a}' },
      { then: 'a different result is {expected_result}' },
    ],
  ] as const satisfies readonly AcceptanceCriterion[],

  domain_terms: ['<term>'] as const,
  evidence: ['<source>'] as const,

  // Outline scenario — one per EXAMPLES row; use {param} placeholders
  outlineScenarioKey: {
    name: '<scenario outline name>',
    steps: [
      { given: '<shared Given from BACKGROUND or explicit here>' },
      { when: '<action with {param_a}>' },
      { then: 'result: {expected_result}' },
    ] as const satisfies readonly Step[],
  },
} as const
