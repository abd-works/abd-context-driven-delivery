import { expect } from 'claude-code/testing'

import { called } from '../../../cdd-stub'
import { boardOf, checkoutFlow } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, expectMarks, findText, labelOf, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Steer Sessions
// Map: ../../../../../.context/story-map.md#s-person----close-active-session
// Model: ../../../../../../../space/kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain
// Scenarios: ../../../../../../.context/move-work-forward-from-chat-bar/steer-sessions/steer_sessions_story.test.md

// The close dialog's choices, as their toggles read: each a Button whose label leads with ☑ or ☐.
const choicesOf = (ui: any) => Promise.all(['close-handoff', 'close-commit', 'close-push'].map(key => labelOf(ui, key)))

// (S) Person --> Close Active Session
story('Close Active Session', CHAT_BAR, () => {
  scenario('Close the session with its work committed', ({ given, when, then, and }) => {
    // Evidence: inferred: mirrors Close Active Session 'Complete the active ticket with its work committed'; no chat bar code yet
    given('checkout-flow is the active [session](../../../../../../../space/kanban/.context/kanban-model.md#session), on its own branch', async ($, on, scene) => {
      scene.world.branches['checkout-flow'] = { name: 'checkout-flow', exists: true, is_checked_out: true }
    })
    when('the Person closes checkout-flow', async ($, on, scene) => {
      await scene.ui.press({ key: 'close-button' })
    })
    // close press -> openClose($, chatBar) -> $.mcp.call('ticket.work_branch', { ticket: 'checkout-flow' }) -> Ticket.work_branch()
    then('a dialog headed Close session Checkout flow offers Create handoff, commit and push on checkout-flow, all chosen', async ($, on, scene) => {
      expect(textOf(await findText(scene.ui, 'Close session Checkout flow'))).toBe('Close session Checkout flow')
      expect(await choicesOf(scene.ui)).toEqual(['☑ Create handoff', '☑ commit checkout-flow', '☑ push checkout-flow'])
    })
    when('the Person confirms', async ($, on, scene) => {
      await scene.ui.press({ key: 'close-confirm' })
    })
    // ChatBarView press -> closeSession($, chatBar) -> $.mcp.call('ticket.close', { ticket: 'checkout-flow', leaving: ['handoff', 'commit', 'push'] }) -> Ticket.close()
    then('a toast says Checkout flow: handoff written, committed, pushed · Session Checkout flow closed', async ($, on, scene) => {
      expect(scene.world.toasts).toContain('Checkout flow: handoff written, committed, pushed · Session Checkout flow closed')
    })
    and('no session is active', async ($, on, scene) => {
      await expectMarks(scene.ui, { 'session-name-button': 'no session' })
      expect(called(scene.world, 'ticket.close')).toEqual({ ticket: 'checkout-flow', leaving: ['handoff', 'commit', 'push'] })
    })
  })
  scenario('Close a session whose work is on main', ({ given, when, then, and }) => {
    // Evidence: observed: chat-ui-defects backlog item — closing a session on main commits and pushes main, as switching
    // a branch does, and does not try to delete a worktree; main has no worktree to delete
    given('checkout-flow is the active [session](../../../../../../../space/kanban/.context/kanban-model.md#session), its work on main', async ($, on, scene) => {
      scene.world.branches['checkout-flow'] = { name: 'main', exists: true, is_checked_out: true }
    })
    when('the Person closes checkout-flow and confirms', async ($, on, scene) => {
      await scene.ui.press({ key: 'close-button' })
      scene.choices = await choicesOf(scene.ui)
      await scene.ui.press({ key: 'close-confirm' })
    })
    then('the dialog offered to commit and push main', async ($, on, scene) => {
      expect(scene.choices).toEqual(['☑ Create handoff', '☑ commit main', '☑ push main'])
    })
    and('ticket.close was asked to commit and push, and to merge nothing', async ($, on, scene) => {
      expect(called(scene.world, 'ticket.close')).toEqual({ ticket: 'checkout-flow', leaving: ['handoff', 'commit', 'push'] })
    })
  })
  scenario('Choose what closing does', ({ given, when, then }) => {
    // Evidence: observed: chat-ui-defects backlog item — the dialog's checkboxes could not be clicked
    given('the close dialog for checkout-flow, on its own branch, is open', async ($, on, scene) => {
      scene.world.branches['checkout-flow'] = { name: 'checkout-flow', exists: true, is_checked_out: true }
      await scene.ui.press({ key: 'close-button' })
    })
    when('the Person unchooses Create handoff and push, and confirms', async ($, on, scene) => {
      await scene.ui.press({ key: 'close-handoff' })
      await scene.ui.press({ key: 'close-push' })
      scene.choices = await choicesOf(scene.ui)
      await scene.ui.press({ key: 'close-confirm' })
    })
    then('the dialog showed only commit chosen, and ticket.close was asked only to commit', async ($, on, scene) => {
      expect(scene.choices).toEqual(['☐ Create handoff', '☑ commit checkout-flow', '☐ push checkout-flow'])
      expect(called(scene.world, 'ticket.close')).toEqual({ ticket: 'checkout-flow', leaving: ['commit'] })
    })
  })
  scenario('Close a session whose branch is not checked out', ({ given, when, then, but }) => {
    // Evidence: inferred: mirrors Close Active Session 'Complete a ticket that has no branch of its own'
    given('checkout-flow is the active [session](../../../../../../../space/kanban/.context/kanban-model.md#session)', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlow())
    })
    but('the checkout is on a branch that is not its own', async ($, on, scene) => {
      scene.world.branches['checkout-flow'] = { name: 'checkout-flow', exists: false, is_checked_out: false }
    })
    when('the Person closes checkout-flow and confirms', async ($, on, scene) => {
      await scene.ui.press({ key: 'close-button' })
      await scene.ui.press({ key: 'close-confirm' })
    })
    // closeSession($, chatBar) -> $.mcp.call('ticket.close', { ticket: 'checkout-flow', leaving: ['handoff'] })
    then('no session is active', async ($, on, scene) => {
      await expectMarks(scene.ui, { 'session-name-button': 'no session' })
    })
    but('nothing is committed, and only the handoff is written', async ($, on, scene) => {
      expect(called(scene.world, 'ticket.close')).toEqual({ ticket: 'checkout-flow', leaving: ['handoff'] })
      expect(scene.world.toasts).toContain('Checkout flow: handoff written · Session Checkout flow closed')
    })
  })
})
