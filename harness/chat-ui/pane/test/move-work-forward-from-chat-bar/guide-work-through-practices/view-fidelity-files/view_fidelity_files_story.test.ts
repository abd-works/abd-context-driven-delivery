import { expect } from 'claude-code/testing'

import { called } from '../../../cdd-stub'
import { boardOf, CHAT_BAR_CLIENT_TEXT, checkoutFlowWith, MODEL_DIAGRAM_FILES, MODEL_FILES, MODEL_REPORT, VALIDATED } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, drawn, filesPaneOf, findText, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Guide Work Through Practices
// Map: ../../../../../.context/story-map.md#s-person----view-fidelity-files
// Model: ../../../../../../../space/kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain
// Scenarios: ../../../../../../.context/move-work-forward-from-chat-bar/guide-work-through-practices/guide_work_through_practices_story.test.md

// (S) Person --> View Fidelity Files
story('View Fidelity Files', CHAT_BAR, () => {
  scenario('Read a file into its tab', ({ given, when, then }) => {
    // Evidence: inferred: mirrors View Fidelity Files, kanban_tools_spec "should return the file's text"; no chat bar code yet
    given('the tab pane/hooks/chat-bar/chat-bar-client.ts is open', async ($, on, scene) => {
      scene.world.declared['clean-engineering-model'] = MODEL_FILES
      scene.world.texts = CHAT_BAR_CLIENT_TEXT
      await scene.ui.press({ key: 'dot-clean-engineering-model' })
      await scene.ui.press({ key: 'files-button' })
      scene.pane = await filesPaneOf($)
    })
    when('the Person views the tab', async ($, on, scene) => {
      await scene.pane.press({ key: 'file-pane/hooks/chat-bar/chat-bar-client.ts' })
    })
    // file tab press -> showFile($, path) -> $.mcp.call('session.read_file', { session: '.sessions/checkout-flow/session.json', path: 'pane/hooks/chat-bar/chat-bar-client.ts' }) -> Session.read_file()
    then("the tab shows the file's text, starting // Model shell for the chat bar", async ($, on, scene) => {
      expect(textOf(await findText(scene.pane, /^\/\/ Model shell/))).toBe('// Model shell for the chat bar')
      expect(called(scene.world, 'session.read_file')).toEqual({ session: '.sessions/checkout-flow/session.json', path: 'pane/hooks/chat-bar/chat-bar-client.ts' })
      await scene.pane.unmount()
    })
  })
  scenario('Open the files beside the chat, never in it', ({ given, when, then, and }) => {
    // Evidence: observed: chat-ui-defects backlog item — the Files button drew story-map.md and story-map.drawio over a
    // 96,711 character session.read_file answer inside the chat; files open in a window of their own, as the board's do
    given("checkout-flow's clean-engineering-model declares chat-bar-model.md and chat-bar-model.drawio", async ($, on, scene) => {
      scene.world.declared['clean-engineering-model'] = MODEL_DIAGRAM_FILES
    })
    when('the Person opens the files of clean-engineering-model', async ($, on, scene) => {
      await scene.ui.press({ key: 'dot-clean-engineering-model' })
      await scene.ui.press({ key: 'files-button' })
    })
    // files press -> openFiles($, fidelity) -> $.ui.open({ id: 'cdd-files', title: 'clean-engineering-model files' })
    then('the files pane opens beside the chat, titled clean-engineering-model files', async ($, on, scene) => {
      expect(scene.world.panes).toEqual([{ id: 'cdd-files', title: 'clean-engineering-model files' }])
    })
    and('the chat bar above the prompt draws no file tab', async ($, on, scene) => {
      expect(await drawn(scene.ui, 'file-pane/.context/chat-bar-model.md')).toBeUndefined()
    })
    and('the diagram is never read as text', async ($, on, scene) => {
      const pane = await filesPaneOf($)
      await pane.press({ key: 'file-pane/.context/chat-bar-model.drawio' })
      expect(scene.world.calls.filter(call => call.tool === 'session.read_file').map(call => call.args.path)).toEqual(['pane/.context/chat-bar-model.md'])
      await pane.unmount()
    })
  })
  scenario('Open a diagram in the draw.io editor', ({ given, when, then, and }) => {
    // Evidence: requested: a button that loads a .drawio file shown in the chat bar's files into the draw.io viewer
    given('the tab pane/.context/chat-bar-model.drawio is open', async ($, on, scene) => {
      scene.world.declared['clean-engineering-model'] = MODEL_DIAGRAM_FILES
      await scene.ui.press({ key: 'dot-clean-engineering-model' })
      await scene.ui.press({ key: 'files-button' })
      scene.pane = await filesPaneOf($)
      await scene.pane.press({ key: 'file-pane/.context/chat-bar-model.drawio' })
    })
    when('the Person opens the diagram in draw.io', async ($, on, scene) => {
      await scene.pane.press({ key: 'file-drawio' })
    })
    // Open in draw.io press -> openInDrawio($, path) -> $.prompt.submit; the agent follows the drawio-viewer rule
    then('the chat is asked to open pane/.context/chat-bar-model.drawio in the draw.io viewer', async ($, on, scene) => {
      expect(scene.world.submits).toContain('Open pane/.context/chat-bar-model.drawio in the draw.io viewer.')
    })
    and('a markdown tab offers no draw.io button', async ($, on, scene) => {
      await scene.pane.press({ key: 'file-pane/.context/chat-bar-model.md' })
      expect(await drawn(scene.pane, 'file-drawio')).toBeUndefined()
      await scene.pane.unmount()
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
      const pane = await filesPaneOf($)
      expect(textOf(await findText(pane, /secrets/))).toBe("../secrets.txt is outside the session's roots")
      await pane.unmount()
    })
  })
  scenario('Read the violations from their count', ({ given, when, then, and }) => {
    // Evidence: requested: a press on the red violation count opens the violations, as the board does; observed:
    // chat-ui-defects backlog item — the report opened inside the chat, and belongs in the side panel
    given("checkout-flow's clean-engineering-model has 7 violations in its latest validation report", async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'clean-engineering-model': { ...VALIDATED, progress: 'violations', violations: 7 } }))
      scene.world.reports['clean-engineering-model'] = MODEL_REPORT
    })
    when('the Person presses the count 7', async ($, on, scene) => {
      await scene.ui.press({ key: 'violations-clean-engineering-model' })
      scene.pane = await filesPaneOf($)
    })
    // count press -> openReport($, fidelity) -> $.mcp.call('fidelity-progress.report', { ticket: 'checkout-flow', fidelity: 'clean-engineering-model' }) -> FidelityProgress.report()
    //   -> $.ui.open({ id: 'cdd-files', title: 'clean-engineering-model report' })
    then('the report opens in its own tab of the side panel', async ($, on, scene) => {
      expect(called(scene.world, 'fidelity-progress.report')).toEqual({ ticket: 'checkout-flow', fidelity: 'clean-engineering-model' })
      expect(scene.world.panes).toEqual([{ id: 'cdd-files', title: 'clean-engineering-model report' }])
      expect(await drawn(scene.pane, `file-${MODEL_REPORT.path}`)).toBeDefined()
    })
    and('its text is drawn as markdown there, not in the chat', async ($, on, scene) => {
      expect((await drawn(scene.pane, 'file-markdown'))?.props?.text).toBe(MODEL_REPORT.text)
      expect(await drawn(scene.ui, 'file-markdown')).toBeUndefined()
      await scene.pane.unmount()
    })
  })
})
