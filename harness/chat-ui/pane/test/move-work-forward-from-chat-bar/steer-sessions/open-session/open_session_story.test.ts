import { expect } from 'claude-code/testing'

import { called } from '../../../cdd-stub'
import { boardOf, checkoutFlow, paymentRetry } from '../../../examples/chat-bar.examples'
import { buttonKeys, CHAT_BAR, drawn, expectMarks, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Steer Sessions
// Map: ../../../../../.context/story-map.md#s-person----open-session
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Open Session
story('Open Session', CHAT_BAR, () => {
  scenario('Open a session from the list', ({ given, when, then }) => {
    // Evidence: inferred: story map 'picking a session ... then calls ticket.activate'; no chat bar code yet
    given('checkout-flow is the active [session](../../../../../../kanban/.context/kanban-model.md#session)', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlow(), paymentRetry())
    })
    when('the Person picks payment-retry and confirms the activation dialog', async ($, on, scene) => {
      await scene.ui.press({ key: 'session-list-button' })
      await scene.ui.press({ key: 'session-payment-retry' })
      await scene.ui.press({ key: 'activate-confirm' })
    })
    // session list press -> activateSession($, 'payment-retry') -> $.mcp.call('ticket.activate', { ticket: 'payment-retry', leaving: ['commit', 'push'], opening: ['branch', 'worktree'] }) -> Ticket.activate()
    then('the Chat Bar shows payment-retry with its Discovery dots', async ($, on, scene) => {
      await expectMarks(scene.ui, { 'session-name-button': 'payment-retry' })
      expect(buttonKeys(await drawn(scene.ui, 'line')).filter(key => key.startsWith('dot-'))).toEqual(['dot-stories-story-map', 'dot-ux-ia', 'dot-clean-engineering-modules'])
      expect(called(scene.world, 'ticket.activate')).toEqual({ ticket: 'payment-retry', leaving: ['commit', 'push'], opening: ['branch', 'worktree'] })
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
      expect(sessions).toEqual([['checkout-flow', 'Specification'], ['payment-retry', 'Discovery']])
    })
    and('a field to name a new session', async ($, on, scene) => {
      expect((await drawn(scene.ui, 'new-session'))?.props?.placeholder).toBe('New session name')
    })
  })
})
