import { expect } from 'claude-code/testing'

import { CHAT_BAR, labelOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: See Work In Chat Bar
// Map: ../../../../../.context/story-map.md#s-person----open-board
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Open Board
story('Open Board', CHAT_BAR, () => {
  scenario('Open the board on a fidelity', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'Fidelity dots'; design/StageStrip.dc.html openBoard sends /board with the session and the fidelity
    given('the Chat Bar shows checkout-flow with the clean-engineering-model dot')
    when('the Person opens the board on clean-engineering-model', async ($, on, scene) => {
      await scene.ui.press({ key: 'dot-clean-engineering-model' })
      await scene.ui.press({ key: 'dot-clean-engineering-model' })
    })
    // FidelityView press -> selectFidelity($, fidelity)
    // FidelityView second press -> openBoard($, fidelity) -> $.command.run({ command: 'board', args: 'checkout-flow clean-engineering-model' })
    then('the chat runs /board checkout-flow clean-engineering-model', async ($, on, scene) => {
      expect(scene.world.sent).toContain('/board checkout-flow clean-engineering-model')
    })
    and('clean-engineering-model is the fidelity the action button acts on', async ($, on, scene) => {
      expect(await labelOf(scene.ui, 'next-action')).toBe('generate clean-engineering-model')
    })
  })
})
