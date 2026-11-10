import { expect } from 'claude-code/testing'

import { called } from '../../../cdd-stub'
import { NEW_SESSION_NAME } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, findText, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Steer Sessions
// Map: ../../../../../.context/story-map.md#s-person----create-new-session
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Create New Session
story('Create New Session', CHAT_BAR, () => {
  scenario('Name a new session from the session list', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'Session name and session list'; no chat bar code yet
    given('the session list box is open on the Chat Bar', async ($, on, scene) => {
      await scene.ui.press({ key: 'session-list-button' })
    })
    when('the Person creates the [session](../../../../../../kanban/.context/kanban-model.md#session) payment-retry', async ($, on, scene) => {
      await scene.ui.input({ key: 'new-session', text: NEW_SESSION_NAME })
    })
    // session list field -> createSession($, 'payment-retry') -> $.mcp.call('ticket.create', { title: 'payment-retry' }) -> Ticket.create()
    then('payment-retry is created', async ($, on, scene) => {
      expect(called(scene.world, 'ticket.create')).toEqual({ title: NEW_SESSION_NAME })
    })
    and('the activation dialog opens on it, offering LEAVE commit, push, merge and OPEN create branch, create worktree, as in Open Session', async ($, on, scene) => {
      const dialog = await Promise.all(['Open payment-retry', /^LEAVE/, /^OPEN/].map(async text => textOf(await findText(scene.ui, text))))
      expect(dialog).toEqual(['Open payment-retry', 'LEAVE ☑ commit ☑ push ☐ merge', 'OPEN ☑ create branch ☑ create worktree'])
    })
  })
})
