// {lowest-sub-epic}-stories.ts — the story's typed data.
//
// One Story constant per story. `story`, `actor`, `domainTerms`, `evidence`
// are metadata. Each other key is a Scenario with `name` + `given` +
// `interactions`. `as const satisfies Story` locks each step-string as a
// literal-type key, so tier classes fail to compile if a step is missing.
//
// Author writes the FIRST step of each phase unprefixed. Continuation steps
// start with `And ` or `But ` — that prefix is part of the string and is
// used verbatim as the tier-class key.

import type { Story } from '<relative-path>/story-types'

export const <VerbNounStory> = {
  story:       '<Story Verb–Noun>',
  actor:       '<Actor Name>',
  domainTerms: ['<ConceptA>', '<ConceptB>'],
  evidence:    ['<source or workshop reference>'],

  // ── Scenario 1 — happy path (Exploration fidelity: only this scenario) ─────
  mainFlow: {
    name: '<happy-path scenario name>',
    given: [
      'a <ConceptA> "<value>"',
      'And a <ConceptB> "<value>"',
    ],
    interactions: [
      {
        when: ['the <Actor> <triggering action>'],
        then: [
          'the <observed concept> is <observable outcome>',
          'And <additional observable outcome>',
        ],
      },
    ],
  },

  // ── Scenario 2 — negative path (Specification fidelity) ────────────────────
  negativePath: {
    name: '<negative scenario name>',
    given: [
      'an <alternate precondition>',
    ],
    interactions: [
      {
        when: ['the <Actor> <alternate action>'],
        then: [
          '<negative outcome>',
          'But <state that does NOT change>',
        ],
      },
    ],
  },
} as const satisfies Story

// ── Stub story (no scenarios yet) ────────────────────────────────────────────
// A named card on the sub-epic row of the story map — title and actor only.
// Appears in walls and reports; nothing to run. Delete this block when the
// story graduates to Exploration.

export const <VerbNounStub> = {
  story:       '<Story Verb–Noun — stub>',
  actor:       '<Actor Name>',
  domainTerms: [],
  evidence:    [],
} as const satisfies Story
