// {lowest-sub-epic}-{layer}.test.js — one tier = one file.
//
// Write-once. Each scenario gets its own `describe` block with explicit step
// calls in order — Given, When, Then — so any reader sees exactly what runs.

import { describe, it } from 'vitest'
import { VerbNoun } from './{lowest-sub-epic}-stories'

class VerbNounApi {
  given = {
    '<precondition>': async () => {
      // seed state / mock
    },
    'And <continuation precondition>': async () => {
      // additional setup
    },
  }

  when = {
    'the <Actor> <triggering action>': async () => {
      // call the API under test
    },
  }

  then = {
    '<observable outcome>': async () => {
      // assert on result
    },
    'And <continuation outcome>': async () => {
      // additional assertion
    },
  }

  async cleanup() {
    // reset state
  }
}

describe(VerbNoun.story, () => {
  describe(VerbNoun.mainFlow.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new VerbNounApi()
      // Given
      await tier.given['<precondition>']()
      await tier.given['And <continuation precondition>']()
      // When
      await tier.when['the <Actor> <triggering action>']()
      // Then
      await tier.then['<observable outcome>']()
      await tier.then['And <continuation outcome>']()
      await tier.cleanup()
    })
  })
})
