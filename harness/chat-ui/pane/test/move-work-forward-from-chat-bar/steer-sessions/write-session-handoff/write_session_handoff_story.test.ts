import { expect } from 'claude-code/testing'

import { cdd, openChatBar } from '../../../chat-bar-world'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Steer Sessions
// Map: ../../../../../.context/story-map.md#s-person----write-session-handoff
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Write Session Handoff
story('Write Session Handoff', () => {
  scenario('Ask the chat to write a handoff', ({ given, when, then }) => {
    // Evidence: inferred: mirrors Write Ticket Handoff, ticket-client.spec 'should fill the prompt with the handoff command'; no chat bar code yet
    given('checkout-flow is the active [session](../../../../../../kanban/.context/kanban-model.md#session)', async ($, on, scene) => {
      scene.world = cdd(on)
      scene.ui = await openChatBar($)
    })
    when('the Person asks for a handoff on checkout-flow', async ($, on, scene) => {
      await scene.ui.press({ key: 'handoff' })
    })
    // ChatBarView press -> runHandoff($, chatBar) -> $.prompt.fill
    then("the chat's prompt holds Write a handoff for ticket checkout-flow with /space-handoff-handoff-session.", async ($, on, scene) => {
      expect(scene.world.fills).toEqual(['Write a handoff for ticket checkout-flow with /space-handoff-handoff-session.'])
      await scene.ui.unmount()
    })
  })
})
