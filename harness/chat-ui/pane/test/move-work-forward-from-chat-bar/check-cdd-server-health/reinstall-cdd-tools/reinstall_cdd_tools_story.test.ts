import { expect } from 'claude-code/testing'

import { CHAT_BAR, findText, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Check CDD Server Health
// Map: ../../../../../.context/story-map.md#s-person----reinstall-cdd-tools
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Reinstall CDD Tools
story('Reinstall CDD Tools', CHAT_BAR, () => {
  scenario('Install the missing tools', ({ given, when, then, and }) => {
    // Evidence: observed: server-health-client.ts runInstall runs the installer from the mod, because the MCP host may be what is broken
    given('cdd is connected with 40 tools loaded, server-health.report not one of them', async ($, on, scene) => {
      scene.world.toolCount = 40
      scene.world.healthText = "KeyError: 'server-health.report'"
    })
    and('the server health panel is open', async ($, on, scene) => {
      await scene.ui.press({ key: 'health-icon' })
    })
    when('the Person runs the install', async ($, on, scene) => {
      await scene.ui.press({ key: 'health-install' })
    })
    // ServerHealthBandView press -> runInstall($) -> $.process.run(['python', 'scripts/install.py', '--ide', 'Claude'])
    // The test kit draws nothing while an engine call is pending, so the Installing. line drawn while the installer runs
    // is read by the surface heavy spec, not here.
    then('the panel says Installed. Open a new session to pick it up.', async ($, on, scene) => {
      expect(textOf(await findText(scene.ui, /^Installed/))).toBe('Installed. Open a new session to pick it up.')
    })
    and('the installer that ran is scripts/install.py --ide Claude', async ($, on, scene) => {
      expect(scene.world.installs.map(argv => argv.slice(1))).toEqual([['scripts/install.py', '--ide', 'Claude']])
    })
  })
  scenario('Show why the install failed', ({ given, when, then }) => {
    // Evidence: observed: server-health-client.ts keeps the installer's last lines when the install fails; server-health-view.tsx detailsOf
    given('the server health panel says Disconnected', async ($, on, scene) => {
      scene.world.serverLost = true
      await scene.ui.press({ key: 'health-icon' })
    })
    when('the Person runs the install and the installer exits with an error', async ($, on, scene) => {
      scene.world.installExit = { exitCode: 1, stderr: 'ModuleNotFoundError: No module named harness' }
      await scene.ui.press({ key: 'health-install' })
    })
    // runInstall($) <- exit code 1 and the installer's error
    then('the panel says Install failed. See the error in Details.', async ($, on, scene) => {
      expect(textOf(await findText(scene.ui, /^Install failed/))).toBe('Install failed. See the error in Details.')
    })
    when('the Person opens Details', async ($, on, scene) => {
      await scene.ui.press({ key: 'health-details' })
    })
    // ServerHealthBandView press -> openDetails($)
    then("Details shows the tool server-health.report, the installer's error, the server plugin:cdd:cdd and the fix Press Reconnect. If that fails, press Run install.", async ($, on, scene) => {
      const details = await Promise.all(['server-health.report', /ModuleNotFoundError/, /^plugin:cdd:cdd$/, /^Press Reconnect/].map(async text => textOf(await findText(scene.ui, text))))
      expect(details).toEqual(['server-health.report', 'ModuleNotFoundError: No module named harness', 'plugin:cdd:cdd', 'Press Reconnect. If that fails, press Run install.'])
    })
  })
})
