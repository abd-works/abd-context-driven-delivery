// {lowest-sub-epic}-{layer}.test.tsx — one tier = one file.
//
// Write-once. Each scenario gets its own `describe` block with explicit step
// calls in order — Given, When, Then — so any reader sees exactly what runs.
// If the story evolves, TypeScript flags missing / stale keys via
// `TierImpl<Scenarios>` and the human reconciles.

import { describe, it } from 'vitest'
import type { TierImpl } from '<relative-path>/story-types'
import { <VerbNounStory> } from './{lowest-sub-epic}-stories'
import { render, screen, waitFor } from '@testing-library/react'
// import { <ApiName> } from '<path-to-client-api>'
// import { <ViewComponent> } from '<path-to-view>'

// vi.mock('<path-to-client-api>', () => ({
//   <ApiName>: { load: vi.fn(), submit: vi.fn() },
// }))

type Scenarios = typeof <VerbNounStory>.mainFlow

export class <VerbNounStory>Client implements TierImpl<Scenarios> {
  given = {
    'a <ConceptA> "<value>"': () => {
      // arrange: mock API responses, session, feature flags
    },
    'And a <ConceptB> "<value>"': () => {
      // arrange: further mocks / context providers
    },
  }

  when = {
    'the <Actor> <triggering action>': () => {
      // render the component tree and drive the interaction
      // render(<<ViewComponent> />)
    },
  }

  then = {
    'the <observed concept> is <observable outcome>': async () => {
      // await waitFor(() => expect(screen.getByRole(...)).toBeVisible())
    },
    'And <additional observable outcome>': () => {
      // additional DOM / a11y assertion
    },
  }

  cleanup(): void {
    // vi.clearAllMocks()
  }
}

describe(<VerbNounStory>.story, () => {
  describe(<VerbNounStory>.mainFlow.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new <VerbNounStory>Client()
      // Given
      tier.given['a <ConceptA> "<value>"']()
      tier.given['And a <ConceptB> "<value>"']()
      // When
      tier.when['the <Actor> <triggering action>']()
      // Then
      await tier.then['the <observed concept> is <observable outcome>']()
      tier.then['And <additional observable outcome>']()
      tier.cleanup()
    })
  })
})
