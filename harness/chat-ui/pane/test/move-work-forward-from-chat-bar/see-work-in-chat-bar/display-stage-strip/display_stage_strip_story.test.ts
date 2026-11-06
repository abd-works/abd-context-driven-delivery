import { expect } from 'claude-code/testing'

import { agentCalls } from '../../../cdd-stub'
import { boardOf, checkoutFlow, SPECIFICATION } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, buttonKeys, drawn, markOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: See Work In Chat Bar
// Map: ../../../../../.context/story-map.md#s-chat-bar----display-stage-strip
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Chat Bar --> Display Stage Strip
story('Display Stage Strip', CHAT_BAR, () => {
  scenario('Show the active session as one line', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'The line reads left to right' and design/StageStrip.dc.html; no chat bar code draws it yet, so this is intended behaviour
    given('the [session](../../../../../../kanban/.context/kanban-model.md#session) checkout-flow is active and In progress in Specification', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlow())
    })
    when('the Chat Bar draws above the prompt')
    // Boot ui.render -> refreshChatBar($) -> $.mcp.call('board.show') -> Board.show()
    // Board <- to_json(): active, columns
    // Boot -> ChatBarView($, currentChatBar($))
    then('the line reads the health mark, checkout-flow ▾, the Specification fidelity dots, the action button, the five [stage](../../../../../../kanban/.context/kanban-model.md#stage--column) icons, then handoff, files and close', async ($, on, scene) => {
      expect(buttonKeys(await drawn(scene.ui, 'line'))).toEqual([
        'health-icon',
        'session-name-button',
        'session-list-button',
        'dot-stories-scenarios',
        'dot-ux-mockup',
        'dot-clean-engineering-model',
        'next-action',
        'action-picker',
        'stage-Backlog',
        'stage-Discovery',
        'stage-Specification',
        'stage-Implementation',
        'stage-Complete',
        'handoff',
        'files-button',
        'close-button',
      ])
    })
    and('Backlog and Discovery are drawn full, Specification is underlined, and Implementation and Complete are faint', async ($, on, scene) => {
      const inks = await Promise.all(['Backlog', 'Discovery', 'Specification', 'Implementation', 'Complete'].map(async stage => (await drawn(scene.ui, `stage-${stage}-mark`))?.children?.[0]?.props?.color))
      expect(inks).toEqual(['#E5531A', '#E5531A', '#E5531A', '#E5531A66', '#E5531A66'])
      expect((await markOf(scene.ui, 'stage-Specification-mark'))?.props?.underline).toBe(true)
      expect((await markOf(scene.ui, 'stage-Discovery-mark'))?.props?.underline).toBe(false)
    })
  })
  scenario('Redraw after the agent moves the session', ({ given, when, then }) => {
    // Evidence: inferred: refresh-on-engine-events in patterns-cdd-claude-mod; no chat bar code yet
    given('the Chat Bar shows checkout-flow with Specification done', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlow({ is_done: true, next: null }))
    })
    when("the agent's tool call moves checkout-flow into Implementation", async ($, on, scene) => {
      agentCalls(scene.world, 'ticket.move_next', { ticket: 'checkout-flow' })
      await $.tool.call({ tool: 'mcp__plugin_cdd_cdd__ticket_move_next' } as never)
    })
    // agent -> ticket.move_next -> Ticket.move_next(); Boot tool.call -> refreshChatBar($) -> $.mcp.call('board.show')
    then('the Chat Bar underlines Implementation and its dots show the Implementation fidelities', async ($, on, scene) => {
      expect((await markOf(scene.ui, 'stage-Implementation-mark'))?.props?.underline).toBe(true)
      expect(buttonKeys(await drawn(scene.ui, 'line')).filter(key => key.startsWith('dot-'))).toEqual(['dot-stories-acceptance-tests', 'dot-ux-front-end-code', 'dot-clean-engineering-code'])
      expect(buttonKeys(await drawn(scene.ui, 'line'))).not.toContain(`dot-${SPECIFICATION[0]}`)
    })
  })
})
