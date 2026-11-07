import { expect } from 'claude-code/testing'

import { cdd } from '../../../cdd-stub'
import { buttonKeys, CHAT_BAR, drawn, expectMarkLooks, expectMarks } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Check CDD Server Health
// Map: ../../../../../.context/story-map.md#s-chat-bar----display-server-health-mark
// Model: ../../../../../../../space/kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Chat Bar --> Display Server Health Mark
story('Display Server Health Mark', CHAT_BAR, () => {
  scenario('Show the connected mark', ({ given, when, then }) => {
    // Evidence: observed: pane/hooks/health/server-health-view.tsx draws ✓ for connected; register.test.ts
    given('cdd answers server-health.report with 116 tools loaded')
    when('the Chat Bar draws the active [session](../../../../../../../space/kanban/.context/kanban-model.md#session) checkout-flow')
    // Boot ui.render -> ChatBarView($, chatBar) -> ServerHealthBandView(elements, band)
    // refreshHealth($) -> $.mcp.call('server-health.report')
    then('a green ✓ sits left of checkout-flow', async ($, on, scene) => {
      await expectMarkLooks(scene.ui, { 'health-icon': ['✓', '#22C55E'] })
      expect(buttonKeys(await drawn(scene.ui, 'line')).slice(0, 2)).toEqual(['health-icon', 'session-name-button'])
      await expectMarks(scene.ui, { 'session-name-button': 'checkout-flow' })
    })
  })
  scenario('Show the disconnected mark', ({ given, when, then, but }) => {
    // Evidence: observed: server-health-view.tsx draws ✕ in the error colour for disconnected
    given('the Chat Bar shows checkout-flow', async ($, on, scene) => {
      await expectMarks(scene.ui, { 'session-name-button': 'checkout-flow' })
    })
    but('plugin:cdd:cdd does not answer', async ($, on, scene) => {
      scene.world.serverLost = true
    })
    when('the Chat Bar draws', async ($, on, scene) => {
      await $.prompt.submit({ text: 'again' })
    })
    // refreshHealth($) -> $.mcp.call('server-health.report') <- no connected MCP tool on a server named plugin:cdd:cdd
    then('a red ✕ sits left of checkout-flow', async ($, on, scene) => {
      await expectMarkLooks(scene.ui, { 'health-icon': ['✕', '#EF4444'] })
      await expectMarks(scene.ui, { 'session-name-button': 'checkout-flow' })
    })
  })
  scenario('Show the tools missing mark', ({ given, when, then, but }) => {
    // Evidence: observed: server-health-view.tsx draws ! in the warning colour for tools-missing
    given('cdd is connected with 40 tools loaded', async ($, on, scene) => {
      scene.world.toolCount = 40
    })
    but('server-health.report is not one of them', async ($, on, scene) => {
      scene.world.healthText = "KeyError: 'server-health.report'"
    })
    when('the Chat Bar draws')
    // refreshHealth($) -> $.tool.list() <- 40 cdd tools, no server-health.report
    then('an amber ! sits left of checkout-flow', async ($, on, scene) => {
      await expectMarkLooks(scene.ui, { 'health-icon': ['!', '#F59E0B'] })
      await expectMarks(scene.ui, { 'session-name-button': 'checkout-flow' })
    })
  })
})
