// <slug>-stories.js
//
// Source of truth for stories in this sub-epic.
// Each exported const is one story. Spec files import from here.
//
// PLAIN SCENARIO: one named key per scenario, containing { name, steps: [...] }
//
// SCENARIO OUTLINE (data-driven):
//   1. Export a top-level EXAMPLES array above the story const
//   2. Use {param_name} placeholders in step strings
//   3. Spec drives with: it.each(EXAMPLES)(`${STORY.key.name} — $scenario`, ...)

// =============================================================================
// FIXTURE CONSTANTS
// =============================================================================

export const ROUTE = '/<path>'

export const EXPECTED_ELEMENTS = {
  heading: '<heading text>',
  submitButton: '<button label>',
}

// =============================================================================
// STORY: <Story Display Name>  (plain scenario)
// =============================================================================

export const STORY_EXPORT_NAME = {
  story: '<Story Display Name>',
  actor: '<Actor Name>',

  acceptance_criteria: [
    [
      { when: 'the *<actor>* <triggering condition>' },
      { then: 'the **<term>** <observable outcome>' },
      { and:  '<additional observable outcome>' },
    ],
    [
      { when: 'the *<actor>* <alternate condition>' },
      { then: '<negative outcome>' },
      { but:  '<state that does NOT change>' },
    ],
  ],

  domain_terms: ['<term 1>', '<term 2>'],
  evidence: ['<source file>', '<research doc>'],

  methodNamedScenarioKey: {
    name: '<scenario name in plain words>',
    steps: [
      { given: '<precondition>' },
      { when:  '<action>' },
      { then:  '<observable outcome 1>' },
      { and:   '<observable outcome 2>' },
    ],
  },

  negativeScenarioKey: {
    name: '<negative scenario name>',
    steps: [
      { given: '<alternate precondition>' },
      { when:  '<alternate action>' },
      { then:  '<negative outcome>' },
      { but:   '<state that does NOT change>' },
    ],
  },
}

// =============================================================================
// STORY: <Second Story Display Name>  (scenario outline — data-driven)
// =============================================================================

export const SECOND_STORY_EXAMPLES = [
  { scenario: 'Scenario 1', param_a: '<value>', param_b: true,  expected_result: '<outcome 1>' },
  { scenario: 'Scenario 2', param_a: '<value>', param_b: false, expected_result: '<outcome 2>' },
]

export const SECOND_STORY_EXPORT_NAME = {
  story: '<Second Story Display Name>',
  actor: '<Actor Name>',

  acceptance_criteria: [
    [
      { when: 'the *<actor>* sets {param_a}' },
      { then: 'result is {expected_result}' },
    ],
  ],

  domain_terms: ['<term>'],
  evidence: ['<source>'],

  outlineScenarioKey: {
    name: '<scenario outline name>',
    examples: SECOND_STORY_EXAMPLES,
    steps: [
      { given: '<shared Given from BACKGROUND or explicit here>' },
      { when:  '<action with {param_a}>' },
      { then:  'result: {expected_result}' },
    ],
  },
}
