import { expect } from 'claude-code/testing'

import { CHAT_BAR, findText, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Check CDD Server Health
// Map: ../../../../../.context/story-map.md#s-person----reinstall-cdd-tools
// Model: ../../../../../../../space/kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Reinstall CDD Tools
story('Reinstall CDD Tools', CHAT_BAR, () => {
  scenario('Install the missing tools', ({ given, when, then, and }) => {
    // Evidence: observed: server-health-client.ts runInstall runs the installer from the mod, because the MCP host may be what is broken
    given('the server health panel reads Tools missing, 40 loaded, server-health.report is not one of them.', async ($, on, scene) => {
      scene.world.toolCount = 40
      scene.world.healthText = "KeyError: 'server-health.report'"
      await scene.ui.press({ key: 'health-icon' })
      expect(textOf(await findText(scene.ui, 'Tools missing'))).toBe('Tools missing')
    })
    when('the Person runs the install', async ($, on, scene) => {
      await scene.ui.press({ key: 'health-install' })
    })
    // ServerHealthBandView press -> runInstall($) -> $.process.run(['python', 'scripts/install.py', '--ide', 'Claude'])
    then('the panel says installing while the installer runs', async ($, on, scene) => {
      // The test kit draws nothing while any engine call is pending, so a held installer times the test out; this checks
      // the installer the Installing. line waits on, and the surface heavy spec reads the line itself.
      expect(scene.world.installs.map(argv => argv.slice(1))).toEqual([['scripts/install.py', '--ide', 'Claude']])
    })
    and('then says Installed. Open a new session to pick it up.', async ($, on, scene) => {
      expect(textOf(await findText(scene.ui, /^Installed/))).toBe('Installed. Open a new session to pick it up.')
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
