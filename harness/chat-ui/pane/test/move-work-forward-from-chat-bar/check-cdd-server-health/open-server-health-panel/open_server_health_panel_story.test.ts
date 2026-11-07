import { expect } from 'claude-code/testing'

import { cdd } from '../../../cdd-stub'
import { HEALTHY } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, drawn, findText, labelOf, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Check CDD Server Health
// Map: ../../../../../.context/story-map.md#s-person----open-server-health-panel
// Model: ../../../../../../../space/kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Open Server Health Panel
story('Open Server Health Panel', CHAT_BAR, () => {
  scenario('Show every part running on one line', ({ given, when, then, and }) => {
    // Evidence: observed: server-health-view.tsx lists MCP host, Tools, Kanban app, Graph app, Hook server; register.test.ts
    given('cdd is connected with 116 tools loaded, the Kanban app on port 8778 and the Graph app on port 5173')
    and('the hook server is not running', async ($, on, scene) => {
      scene.world.health = { ...HEALTHY, is_hook_server_running: false }
    })
    when('the Person opens the server health panel', async ($, on, scene) => {
      await scene.ui.press({ key: 'health-icon' })
    })
    // ServerHealthBandView -> ExpandedView(elements, health)
    then('the panel opens above the mark with MCP host, Tools, Kanban app and Graph app green', async ($, on, scene) => {
      const colours = await Promise.all(['running', '116 loaded', 'running :8778', 'running :5173'].map(async text => (await findText(scene.ui, text))?.props?.color))
      expect(colours).toEqual(['#22C55E', '#22C55E', '#22C55E', '#22C55E'])
      expect((await drawn(scene.ui, 'server-health'))?.children?.[0]?.props?.display).toBeUndefined()
    })
    and('Tools reads 116 loaded, Kanban app 8778 and Graph app 5173', async ($, on, scene) => {
      const values = await Promise.all(['116 loaded', 'running :8778', 'running :5173'].map(async text => textOf(await findText(scene.ui, text))))
      expect(values).toEqual(['116 loaded', 'running :8778', 'running :5173'])
    })
    and('Hook server is grey', async ($, on, scene) => {
      expect((await findText(scene.ui, 'not installed'))?.props?.color).toBe('#9B9BA8')
    })
    and("each part's name shows on hover", async ($, on, scene) => {
      const names = await Promise.all(['MCP host', 'Tools', 'Kanban app', 'Graph app', 'Hook server'].map(async part => (await drawn(scene.ui, part))?.children?.[2]))
      expect(names.map(name => [name?.props?.display, name?.hover?.display])).toEqual(Array(5).fill(['none', 'flex']))
    })
  })
  scenario('Pin the panel open', ({ given, when, then }) => {
    // Evidence: observed: server-health-client.ts togglePin
    given('the server health panel is open over the mark')
    when('the Person pins the panel', async ($, on, scene) => {
      await scene.ui.press({ key: 'health-icon' })
    })
    // ServerHealthBandView press -> togglePin($)
    then('the panel stays open after the pointer leaves the mark', async ($, on, scene) => {
      expect((await drawn(scene.ui, 'server-health'))?.children?.[0]?.props?.display).toBeUndefined()
    })
  })
  scenario('Say what is wrong when cdd is down', ({ given, when, then, and }) => {
    // Evidence: observed: server-health-view.tsx headlineOf and the Details, Run install, Reconnect buttons
    given('plugin:cdd:cdd does not answer', async ($, on, scene) => {
      scene.world.serverLost = true
    })
    when('the Person opens the server health panel', async ($, on, scene) => {
      await scene.ui.press({ key: 'health-icon' })
    })
    then('the headline reads Disconnected, plugin:cdd:cdd stopped.', async ($, on, scene) => {
      expect(textOf(await findText(scene.ui, 'Disconnected'))).toBe('Disconnected')
      expect(textOf(await findText(scene.ui, 'plugin:cdd:cdd stopped.'))).toBe('plugin:cdd:cdd stopped.')
    })
    and('Details, Run install and Reconnect are offered', async ($, on, scene) => {
      const offered = await Promise.all(['health-details', 'health-install', 'health-reconnect'].map(key => labelOf(scene.ui, key)))
      expect(offered).toEqual(['Details', 'Run install', 'Reconnect'])
    })
  })
})
