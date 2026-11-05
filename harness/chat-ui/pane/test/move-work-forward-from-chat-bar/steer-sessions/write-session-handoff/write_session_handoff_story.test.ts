import { expect } from 'claude-code/testing'

import { CHAT_BAR } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Steer Sessions
// Map: ../../../../../.context/story-map.md#s-person----write-session-handoff
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Write Session Handoff
story('Write Session Handoff', CHAT_BAR, () => {
  scenario('Ask the chat to write a handoff', ({ given, when, then }) => {
    // Evidence: inferred: mirrors Write Ticket Handoff, ticket-client.spec 'should fill the prompt with the handoff command'; no chat bar code yet
    given('checkout-flow is the active [session](../../../../../../kanban/.context/kanban-model.md#session)')
    when('the Person asks for a handoff on checkout-flow', async ($, on, scene) => {
      await scene.ui.press({ key: 'handoff' })
    })
    // ChatBarView press -> runHandoff($, chatBar) -> $.prompt.fill
    then("the chat's prompt holds Write a handoff for ticket checkout-flow with /space-handoff-handoff-session.", async ($, on, scene) => {
      expect(scene.world.fills).toEqual(['Write a handoff for ticket checkout-flow with /space-handoff-handoff-session.'])
    })
  })
})
