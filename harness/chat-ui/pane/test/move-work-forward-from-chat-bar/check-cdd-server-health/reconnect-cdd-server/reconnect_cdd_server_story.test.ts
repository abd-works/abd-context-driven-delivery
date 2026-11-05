import { expect } from 'claude-code/testing'

import { called, cdd, dueTimers, findText, labelOf, markOf, openChatBar, textOf } from '../../../chat-bar-world'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Check CDD Server Health
// Map: ../../../../../.context/story-map.md#s-person----reconnect-cdd-server
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Reconnect CDD Server
story('Reconnect CDD Server', () => {
  scenario('Reconnect and read the session again', ({ given, when, then, and }) => {
    // Evidence: observed: server-health-client.ts reconnect; onRestored reads the active session again
    given('the server health panel says Disconnected', async ($, on, scene) => {
      scene.world = cdd(on)
      scene.world.serverLost = true
      scene.ui = await openChatBar($)
      await scene.ui.press({ key: 'health-icon' })
    })
    when('the Person reconnects cdd', async ($, on, scene) => {
      await scene.ui.press({ key: 'health-reconnect' })
    })
    // ServerHealthBandView press -> reconnect($, onRestored)
    // reconnect -> refreshHealth($) -> $.mcp.call('server-health.report')
    then('the mark shows ⟳ and the headline reads Reconnecting, Try 1 of 3.', async ($, on, scene) => {
      const mark = await markOf(scene.ui, 'health-icon')
      expect([textOf(mark), mark?.props?.color]).toEqual(['⟳', '#F59E0B'])
      expect(textOf(await findText(scene.ui, 'Reconnecting'))).toBe('Reconnecting')
      expect(textOf(await findText(scene.ui, /Try 1 of 3/))).toBe('Waiting for plugin:cdd:cdd to answer. Try 1 of 3.')
    })
    and('once cdd answers, the mark shows ✓ and the Chat Bar shows checkout-flow again, as in Display Stage Strip', async ($, on, scene) => {
      scene.world.serverLost = false
      await dueTimers(scene.world)
      const mark = await markOf(scene.ui, 'health-icon')
      expect([textOf(mark), mark?.props?.color]).toEqual(['✓', '#22C55E'])
      expect(textOf(await markOf(scene.ui, 'session-name-button'))).toBe('checkout-flow')
      expect(called(scene.world, 'board.show')).toEqual({})
      await scene.ui.unmount()
    })
    // onRestored -> refreshChatBar($) -> $.mcp.call('board.show') -> Board.show()
  })
  scenario('Stop after three tries', ({ given, when, then, and }) => {
    // Evidence: observed: server-health-client.ts RECONNECT_TRIES is 3
    given('the server health panel says Disconnected', async ($, on, scene) => {
      scene.world = cdd(on)
      scene.world.serverLost = true
      scene.ui = await openChatBar($)
      await scene.ui.press({ key: 'health-icon' })
    })
    when('the Person reconnects cdd and it does not answer three times', async ($, on, scene) => {
      await scene.ui.press({ key: 'health-reconnect' })
      await dueTimers(scene.world)
      await dueTimers(scene.world)
    })
    // reconnect($, onRestored, attempt 1..3)
    then('after Try 3 of 3 the headline reads Disconnected again', async ($, on, scene) => {
      const mark = await markOf(scene.ui, 'health-icon')
      expect([textOf(mark), mark?.props?.color]).toEqual(['✕', '#EF4444'])
      expect(textOf(await findText(scene.ui, 'Disconnected'))).toBe('Disconnected')
    })
    and('Reconnect and Run install are still offered', async ($, on, scene) => {
      const offered = await Promise.all(['health-reconnect', 'health-install'].map(key => labelOf(scene.ui, key)))
      expect(offered).toEqual(['Reconnect', 'Run install'])
      await scene.ui.unmount()
    })
  })
})
