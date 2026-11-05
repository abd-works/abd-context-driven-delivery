import { expect } from 'claude-code/testing'

import { boardOf, checkoutFlowWith, GENERATED } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, expectMarks, findText, labelOf, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Guide Work Through Practices
// Map: ../../../../../.context/story-map.md#s-person----invoke-next-fidelity-action
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Invoke Next Fidelity Action
story('Invoke Next Fidelity Action', CHAT_BAR, () => {
  scenario('Run the next action on the selected fidelity', ({ given, when, then }) => {
    // Evidence: inferred: CDR 0001 'Action button and ▾ picker' and 'Actions run on one fidelity at a time'; no chat bar code yet
    given("checkout-flow's ux-mockup is generated and is the selected fidelity", async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'ux-mockup': GENERATED }))
      await scene.ui.press({ key: 'dot-ux-mockup' })
    })
    when('the Person runs the next action', async ($, on, scene) => {
      await scene.ui.press({ key: 'next-action' })
    })
    // ChatBarView press -> runAction($, fidelity, 'validate')
    // runAction -> $.command.run({ command: 'actions-validate', args: 'ux-mockup' }); only generate asks ticket.generate_commands for its commands
    then('the chat runs /actions-validate ux-mockup', async ($, on, scene) => {
      expect(scene.world.sent).toContain('/actions-validate ux-mockup')
    })
  })
  scenario('Show the next action before it runs', ({ given, when, then }) => {
    // Evidence: inferred: CDR 0001 'The button shows the next action for one fidelity as an icon'
    given("checkout-flow's ux-mockup is generated and is the selected fidelity", async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'ux-mockup': GENERATED }))
      await scene.ui.press({ key: 'dot-ux-mockup' })
    })
    when('the Chat Bar draws checkout-flow', async ($, on, scene) => {
      await $.prompt.submit({ text: 'again' })
    })
    then('the button shows the validate icon, with validate ux-mockup on hover', async ($, on, scene) => {
      await expectMarks(scene.ui, { 'next-action': '◎' })
      expect(await labelOf(scene.ui, 'next-action')).toBe('validate ux-mockup')
      expect(textOf(await findText(scene.ui, 'validate ux-mockup'))).toBe('validate ux-mockup')
    })
  })
})
