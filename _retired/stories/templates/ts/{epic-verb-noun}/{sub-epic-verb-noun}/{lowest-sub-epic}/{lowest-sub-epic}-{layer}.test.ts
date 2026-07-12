// {lowest-sub-epic}-{layer}.test.ts — one tier = one file.
//
// Write-once. The skill scaffolds this once from the sibling `-stories.ts`
// file. Each scenario gets its own `describe` block with explicit step calls
// in order — Given, When, Then — so any reader can see exactly what runs
// without needing to know how a runner works.
//
// If the story evolves, TypeScript flags missing / stale keys via
// `TierImpl<Scenarios>` and the human reconciles.

import { describe, it } from 'vitest'
import type { TierImpl } from '<relative-path>/story-types'
import { <VerbNounStory> } from './{lowest-sub-epic}-stories'
// Named destructured imports only — never `import * as H` or `import * as helpers`
import {
  seed<ConceptA>,
  seed<ConceptB>,
  call<Action>,
  reset<EpicSlug>State,
} from '../<sub-epic-slug>-helpers'

type Scenarios = typeof <VerbNounStory>.mainFlow

export class <VerbNounStory>Server implements TierImpl<Scenarios> {
  // per-scenario state goes here (tokens, response captures, seeded rows, ...)

  given = {
    'a <ConceptA> "<value>"': async () => {
      // seed database / fixtures for this precondition
    },
    'And a <ConceptB> "<value>"': async () => {
      // seed additional precondition
    },
  }

  when = {
    'the <Actor> <triggering action>': async () => {
      // fire the HTTP request / event / queue message under test
    },
  }

  then = {
    'the <observed concept> is <observable outcome>': async () => {
      // assert on captured response / persisted state / emitted event
    },
    'And <additional observable outcome>': async () => {
      // additional observable assertion
    },
  }

  async cleanup(): Promise<void> {
    // reset any state seeded in `given`
  }
}

describe(<VerbNounStory>.story, () => {
  describe(<VerbNounStory>.mainFlow.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new <VerbNounStory>Server()
      // Given
      await tier.given['a <ConceptA> "<value>"']()
      await tier.given['And a <ConceptB> "<value>"']()
      // When
      await tier.when['the <Actor> <triggering action>']()
      // Then
      await tier.then['the <observed concept> is <observable outcome>']()
      await tier.then['And <additional observable outcome>']()
      await tier.cleanup()
    })
  })
})
