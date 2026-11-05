import { expect } from 'claude-code/testing'

import { called } from '../../../cdd-stub'
import { CHAT_BAR, expectMarks, findText, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Steer Sessions
// Map: ../../../../../.context/story-map.md#s-person----close-active-session
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Close Active Session
story('Close Active Session', CHAT_BAR, () => {
  scenario('Close the session with its work committed', ({ given, when, then, and }) => {
    // Evidence: inferred: mirrors Close Active Session 'Complete the active ticket with its work committed'; no chat bar code yet
    given('checkout-flow is the active [session](../../../../../../kanban/.context/kanban-model.md#session), on its own branch', async ($, on, scene) => {
      scene.world.answers['ticket.workspace'] = { has_branch: true, has_worktree: true, leaving_has_branch: true }
    })
    when('the Person closes checkout-flow', async ($, on, scene) => {
      await scene.ui.press({ key: 'close-button' })
    })
    then('a dialog headed Close session Checkout flow offers commit and push, chosen', async ($, on, scene) => {
      expect(textOf(await findText(scene.ui, 'Close session Checkout flow'))).toBe('Close session Checkout flow')
      expect(textOf(await findText(scene.ui, /^LEAVE/))).toBe('LEAVE ☑ commit ☑ push')
    })
    when('the Person confirms', async ($, on, scene) => {
      await scene.ui.press({ key: 'close-confirm' })
    })
    // ChatBarView press -> closeSession($, chatBar) -> $.mcp.call('ticket.close', { ticket: 'checkout-flow', leaving: ['commit', 'push'] }) -> Ticket.close()
    // Ticket -> Session.close()
    then('a toast says Checkout flow: committed, pushed · Session Checkout flow closed', async ($, on, scene) => {
      expect(scene.world.toasts).toContain('Checkout flow: committed, pushed · Session Checkout flow closed')
    })
    and('no session is active', async ($, on, scene) => {
      await expectMarks(scene.ui, { 'session-name-button': 'no session' })
      expect(called(scene.world, 'ticket.close')).toEqual({ ticket: 'checkout-flow', leaving: ['commit', 'push'] })
    })
  })
  scenario('Close a session that has no branch of its own', ({ given, when, then, but }) => {
    // Evidence: inferred: mirrors Close Active Session 'Complete a ticket that has no branch of its own'
    given('checkout-flow is the active [session](../../../../../../kanban/.context/kanban-model.md#session)')
    but('it has no branch of its own', async ($, on, scene) => {
      scene.world.answers['ticket.workspace'] = { has_branch: false, has_worktree: false, leaving_has_branch: false }
    })
    when('the Person closes checkout-flow and confirms', async ($, on, scene) => {
      await scene.ui.press({ key: 'close-button' })
      await scene.ui.press({ key: 'close-confirm' })
    })
    // closeSession($, chatBar) -> $.mcp.call('ticket.close', { ticket: 'checkout-flow', leaving: [] })
    then('no session is active', async ($, on, scene) => {
      await expectMarks(scene.ui, { 'session-name-button': 'no session' })
    })
    but('nothing is committed', async ($, on, scene) => {
      expect(called(scene.world, 'ticket.close')).toEqual({ ticket: 'checkout-flow', leaving: [] })
      expect(scene.world.toasts).toContain('Session Checkout flow closed')
    })
  })
})
