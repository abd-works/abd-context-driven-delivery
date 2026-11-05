import { expect } from 'claude-code/testing'

import { boardOf, called, cdd, checkoutFlow, findText, openChatBar, paymentRetry, textOf } from '../../../chat-bar-world'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Steer Sessions
// Map: ../../../../../.context/story-map.md#s-person----create-new-session
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Create New Session
story('Create New Session', () => {
  scenario('Name a new session from the session list', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'Session name and session list'; no chat bar code yet
    given('the session list box is open on the Chat Bar', async ($, on, scene) => {
      scene.world = cdd(on)
      scene.ui = await openChatBar($)
      await scene.ui.press({ key: 'session-list-button' })
    })
    when('the Person creates the [session](../../../../../../kanban/.context/kanban-model.md#session) payment-retry', async ($, on, scene) => {
      scene.world.answers['ticket.create'] = paymentRetry()
      scene.world.board = boardOf('checkout-flow', checkoutFlow(), paymentRetry())
      await scene.ui.input({ key: 'new-session', text: 'payment-retry' })
    })
    // session list field -> createSession($, 'payment-retry') -> $.mcp.call('ticket.create', { title: 'payment-retry' }) -> Ticket.create()
    then('payment-retry is created', async ($, on, scene) => {
      expect(called(scene.world, 'ticket.create')).toEqual({ title: 'payment-retry' })
    })
    and('the activation dialog opens on it, offering LEAVE commit, push, merge and OPEN create branch, create worktree, as in Open Session', async ($, on, scene) => {
      const dialog = await Promise.all(['Open payment-retry', /^LEAVE/, /^OPEN/].map(async text => textOf(await findText(scene.ui, text))))
      expect(dialog).toEqual(['Open payment-retry', 'LEAVE ☑ commit ☑ push ☐ merge', 'OPEN ☑ create branch ☑ create worktree'])
      await scene.ui.unmount()
    })
  })
})
