import { expect } from 'claude-code/testing'

import { called } from '../../../cdd-stub'
import { boardOf, checkoutFlow, paymentRetry } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, buttonKeys, drawn, expectMarks, labelOf, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Steer Sessions
// Map: ../../../../../.context/story-map.md#s-person----open-session
// Model: ../../../../../../../space/kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// The activation dialog's choices, as their toggles read.
const SWITCH_CHOICES = ['leave-handoff', 'leave-commit', 'leave-push', 'leave-merge', 'open-branch', 'open-worktree']

// (S) Person --> Open Session
story('Open Session', CHAT_BAR, () => {
  scenario('Open a session from the list', ({ given, when, then }) => {
    // Evidence: inferred: story map 'picking a session ... then calls ticket.activate'; no chat bar code yet
    given('checkout-flow is the active [session](../../../../../../../space/kanban/.context/kanban-model.md#session)', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlow(), paymentRetry())
    })
    when('the Person picks payment-retry and confirms the activation dialog', async ($, on, scene) => {
      await scene.ui.press({ key: 'session-list-button' })
      await scene.ui.press({ key: 'session-payment-retry' })
      await scene.ui.press({ key: 'activate-confirm' })
    })
    // session list press -> activateSession($, 'payment-retry') -> $.mcp.call('ticket.activate', { ticket: 'payment-retry', leaving: ['handoff', 'commit', 'push'], opening: ['branch', 'worktree'] }) -> Ticket.activate()
    then('the Chat Bar shows payment-retry with its Discovery dots', async ($, on, scene) => {
      await expectMarks(scene.ui, { 'session-name-button': 'payment-retry' })
      expect(buttonKeys(await drawn(scene.ui, 'line')).filter(key => key.startsWith('dot-'))).toEqual(['dot-stories-story-map', 'dot-ux-ia', 'dot-clean-engineering-modules'])
      expect(called(scene.world, 'ticket.activate')).toEqual({ ticket: 'payment-retry', leaving: ['handoff', 'commit', 'push'], opening: ['branch', 'worktree'] })
    })
  })
  scenario('Choose what switching does', ({ given, when, then, and }) => {
    // Evidence: observed: chat-ui-defects backlog item — the switch dialog's LEAVE commit / push / merge and OPEN create
    // branch / create worktree checkboxes could not be clicked, and it needs a Create handoff checkbox, on by default
    given('the activation dialog for payment-retry is open, leaving checkout-flow', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlow(), paymentRetry())
      await scene.ui.press({ key: 'session-list-button' })
      await scene.ui.press({ key: 'session-payment-retry' })
      scene.before = await Promise.all(SWITCH_CHOICES.map(key => labelOf(scene.ui, key)))
    })
    when('the Person chooses merge, unchooses the worktree, and confirms', async ($, on, scene) => {
      await scene.ui.press({ key: 'leave-merge' })
      await scene.ui.press({ key: 'open-worktree' })
      scene.after = await Promise.all(SWITCH_CHOICES.map(key => labelOf(scene.ui, key)))
      await scene.ui.press({ key: 'activate-confirm' })
    })
    // choice press -> toggleLeaving($, 'merge') / toggleOpening($, 'worktree'); confirm -> $.mcp.call('ticket.activate', ...)
    then('the dialog first offered Create handoff, commit and push chosen, merge not, and a branch and worktree chosen', async ($, on, scene) => {
      expect(scene.before).toEqual(['☑ Create handoff', '☑ commit', '☑ push', '☐ merge', '☑ create branch', '☑ create worktree'])
    })
    and('each press changed its own choice', async ($, on, scene) => {
      expect(scene.after).toEqual(['☑ Create handoff', '☑ commit', '☑ push', '☑ merge', '☑ create branch', '☐ create worktree'])
    })
    and('ticket.activate was asked for those choices', async ($, on, scene) => {
      expect(called(scene.world, 'ticket.activate')).toEqual({ ticket: 'payment-retry', leaving: ['handoff', 'commit', 'push', 'merge'], opening: ['branch'] })
    })
  })
  scenario('List the sessions with their stages', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'A ▾ opens a list box of the sessions with their stages, plus a field to type a new session'
    given('the sessions checkout-flow in Specification and payment-retry in Discovery', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlow(), paymentRetry())
    })
    when('the Person opens the session list', async ($, on, scene) => {
      await scene.ui.press({ key: 'session-list-button' })
    })
    // ChatBarView paints the list from the board.show answer
    then('the list box shows checkout-flow Specification and payment-retry Discovery', async ($, on, scene) => {
      const sessions = await Promise.all(['session-row-checkout-flow', 'session-row-payment-retry'].map(async key => (await drawn(scene.ui, key))?.children?.map((child: any) => textOf(child.type === 'Button' ? child.children?.[0] : child))))
      expect(sessions).toEqual([['▤', 'checkout-flow'], ['⌕', 'payment-retry']])
    })
    and('a field to name a new session', async ($, on, scene) => {
      expect((await drawn(scene.ui, 'new-session'))?.props?.placeholder).toBe('New session name')
    })
  })
})
