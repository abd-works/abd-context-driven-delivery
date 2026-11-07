import { expect } from 'claude-code/testing'

import { called } from '../../../cdd-stub'
import { boardOf, checkoutFlowWith, DONE, GENERATED } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, markOf, stateOf, textOf, tipOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Guide Work Through Practices
// Map: ../../../../../.context/story-map.md#s-person----move-session-to-next-stage
// Model: ../../../../../../../space/kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Move Session To Next Stage
story('Move Session To Next Stage', CHAT_BAR, () => {
  scenario('Move on once every fidelity is reviewed', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'When every fidelity of the stage is reviewed, the button moves the session to the next stage'; no chat bar code yet
    given('checkout-flow is In progress in Specification with stories-scenarios, ux-mockup and clean-engineering-model reviewed', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'stories-scenarios': DONE, 'ux-mockup': DONE, 'clean-engineering-model': DONE }, { is_done: true, next: null }))
    })
    when('the Person moves checkout-flow to the next [stage](../../../../../../../space/kanban/.context/kanban-model.md#stage--column)', async ($, on, scene) => {
      expect(await tipOf(scene.ui, 'action')).toBe('move checkout-flow on')
      await scene.ui.press({ key: 'next-action' })
    })
    // ChatBarView press -> moveNext($, chatBar) -> $.mcp.call('ticket.move_next', { ticket: 'checkout-flow' }) -> Ticket.move_next()
    // Ticket -> Ticket.record('move Implementation')
    then('the Chat Bar underlines Implementation', async ($, on, scene) => {
      expect((await markOf(scene.ui, 'stage-Implementation-mark'))?.props?.underline).toBe(true)
      expect(called(scene.world, 'ticket.move_next')).toEqual({ ticket: 'checkout-flow' })
    })
    and('its dots show the Implementation fidelities, not started', async ($, on, scene) => {
      const slugs = ['stories-acceptance-tests', 'ux-front-end-code', 'clean-engineering-code']
      expect(await Promise.all(slugs.map(slug => tipOf(scene.ui, `fidelity-${slug}`)))).toEqual(slugs)
      const states = await Promise.all(slugs.map(slug => stateOf(scene.ui, slug)))
      expect(states).toEqual(['○ to do', '○ to do', '○ to do'])
    })
  })
  scenario('Keep acting on fidelities until the stage is reviewed', ({ given, when, then, but }) => {
    // Evidence: inferred: CDR 0001 'Action button and ▾ picker'
    given('checkout-flow is In progress in Specification with ux-mockup selected', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'ux-mockup': GENERATED }))
      await scene.ui.press({ key: 'dot-ux-mockup' })
    })
    but('ux-mockup is not reviewed')
    when('the Chat Bar draws checkout-flow', async ($, on, scene) => {
      await $.prompt.submit({ text: 'again' })
    })
    then("the button shows ux-mockup's next action", async ($, on, scene) => {
      expect(await tipOf(scene.ui, 'action')).toBe('validate ux-mockup')
    })
    but('not the move to Implementation', async ($, on, scene) => {
      expect(textOf(await markOf(scene.ui, 'next-action-mark'))).not.toBe('➜')
    })
  })
})
