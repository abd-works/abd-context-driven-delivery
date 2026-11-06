import { expect } from 'claude-code/testing'

import { boardOf, checkoutFlow } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, tipOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: See Work In Chat Bar
// Map: ../../../../../.context/story-map.md#s-person----select-fidelity
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Select Fidelity
story('Select Fidelity', CHAT_BAR, () => {
  scenario('A dot selects its fidelity and sends nothing to the chat', ({ given, when, then, and }) => {
    // Evidence: requested: a dot press only sets the fidelity the action button acts on
    given('the Chat Bar shows checkout-flow with the clean-engineering-model dot', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlow())
    })
    when('the Person presses the clean-engineering-model dot twice', async ($, on, scene) => {
      await scene.ui.press({ key: 'dot-clean-engineering-model' })
      await scene.ui.press({ key: 'dot-clean-engineering-model' })
    })
    // FidelityView press -> selectFidelity($, fidelity)
    then('nothing is sent to the chat', async ($, on, scene) => {
      expect(scene.world.sent).toEqual([])
    })
    and('clean-engineering-model is the fidelity the action button acts on', async ($, on, scene) => {
      expect(await tipOf(scene.ui, 'action')).toBe('generate clean-engineering-model')
    })
  })
})
