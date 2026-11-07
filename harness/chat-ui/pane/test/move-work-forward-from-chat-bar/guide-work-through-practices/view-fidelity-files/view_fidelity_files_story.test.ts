import { expect } from 'claude-code/testing'

import { called } from '../../../cdd-stub'
import { boardOf, CHAT_BAR_CLIENT_TEXT, checkoutFlowWith, MODEL_FILES, MODEL_REPORT, VALIDATED } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, drawn, findText, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Guide Work Through Practices
// Map: ../../../../../.context/story-map.md#s-person----view-fidelity-files
// Model: ../../../../../../../space/kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> View Fidelity Files
story('View Fidelity Files', CHAT_BAR, () => {
  scenario('Read a file into its tab', ({ given, when, then }) => {
    // Evidence: inferred: mirrors View Fidelity Files, kanban_tools_spec "should return the file's text"; no chat bar code yet
    given('the tab pane/hooks/chat-bar/chat-bar-client.ts is open', async ($, on, scene) => {
      scene.world.declared['clean-engineering-model'] = MODEL_FILES
      scene.world.texts = CHAT_BAR_CLIENT_TEXT
      await scene.ui.press({ key: 'dot-clean-engineering-model' })
      await scene.ui.press({ key: 'files-button' })
    })
    when('the Person views the tab', async ($, on, scene) => {
      await scene.ui.press({ key: 'file-pane/hooks/chat-bar/chat-bar-client.ts' })
    })
    // file tab press -> showFile($, path) -> $.mcp.call('session.read_file', { session: '.sessions/checkout-flow/session.json', path: 'pane/hooks/chat-bar/chat-bar-client.ts' }) -> Session.read_file()
    then("the tab shows the file's text, starting // Model shell for the chat bar", async ($, on, scene) => {
      expect(textOf(await findText(scene.ui, /^\/\/ Model shell/))).toBe('// Model shell for the chat bar')
      expect(called(scene.world, 'session.read_file')).toEqual({ session: '.sessions/checkout-flow/session.json', path: 'pane/hooks/chat-bar/chat-bar-client.ts' })
    })
  })
  scenario("Refuse a file outside the session's roots", ({ given, when, then }) => {
    // Evidence: inferred: mirrors kanban_tools_spec 'should refuse a file outside the repository'
    given("checkout-flow's clean-engineering-model declares ../secrets.txt, outside the session's roots", async ($, on, scene) => {
      scene.world.declared['clean-engineering-model'] = { typescript: [{ path: '../secrets.txt', exists: false }] }
    })
    when('the Person opens the files of clean-engineering-model', async ($, on, scene) => {
      await scene.ui.press({ key: 'dot-clean-engineering-model' })
      await scene.ui.press({ key: 'files-button' })
    })
    // $.mcp.call('session.read_file', { session: '.sessions/checkout-flow/session.json', path: '../secrets.txt' }) <- PathOutsideRootsError
    then("the tab says ../secrets.txt is outside the session's roots", async ($, on, scene) => {
      expect(textOf(await findText(scene.ui, /secrets/))).toBe("../secrets.txt is outside the session's roots")
    })
  })
  scenario('Read the violations from their count', ({ given, when, then, and }) => {
    // Evidence: requested: a press on the red violation count opens the violations, as the board does
    given("checkout-flow's clean-engineering-model has 7 violations in its latest validation report", async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'clean-engineering-model': { ...VALIDATED, progress: 'violations', violations: 7 } }))
      scene.world.reports['clean-engineering-model'] = MODEL_REPORT
    })
    when('the Person presses the count 7', async ($, on, scene) => {
      await scene.ui.press({ key: 'violations-clean-engineering-model' })
    })
    // count press -> openReport($, fidelity) -> $.mcp.call('fidelity-progress.report', { ticket: 'checkout-flow', fidelity: 'clean-engineering-model' }) -> FidelityProgress.report()
    then('the report opens in its own tab', async ($, on, scene) => {
      expect(called(scene.world, 'fidelity-progress.report')).toEqual({ ticket: 'checkout-flow', fidelity: 'clean-engineering-model' })
      expect(await drawn(scene.ui, `file-${MODEL_REPORT.path}`)).toBeDefined()
    })
    and('its text is drawn as markdown', async ($, on, scene) => {
      expect((await drawn(scene.ui, 'file-markdown'))?.props?.text).toBe(MODEL_REPORT.text)
    })
  })
})
