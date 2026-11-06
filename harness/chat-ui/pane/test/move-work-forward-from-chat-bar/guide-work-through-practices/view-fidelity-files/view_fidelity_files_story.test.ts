import { expect } from 'claude-code/testing'

import { called } from '../../../cdd-stub'
import { boardOf, checkoutFlowWith, VALIDATED } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, drawn, findText, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Guide Work Through Practices
// Map: ../../../../../.context/story-map.md#s-person----view-fidelity-files
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> View Fidelity Files
story('View Fidelity Files', CHAT_BAR, () => {
  scenario('Read a file into its tab', ({ given, when, then }) => {
    // Evidence: inferred: mirrors View Fidelity Files, kanban_tools_spec "should return the file's text"; no chat bar code yet
    given('the tab pane/hooks/chat-bar/chat-bar-client.ts is open', async ($, on, scene) => {
      scene.world.answers['ticket.files'] = { 'clean_engineering-model': { typescript: [{ path: 'pane/hooks/chat-bar/chat-bar-client.ts', exists: true }, { path: 'pane/hooks/chat-bar/fidelity-client.ts', exists: true }] } }
      scene.world.answers['ticket.read_file'] = { path: 'pane/hooks/chat-bar/chat-bar-client.ts', text: '// Model shell for the chat bar\nexport class ChatBarClient {}' }
      await scene.ui.press({ key: 'dot-clean_engineering-model' })
      await scene.ui.press({ key: 'files-button' })
    })
    when('the Person views the tab', async ($, on, scene) => {
      await scene.ui.press({ key: 'file-pane/hooks/chat-bar/chat-bar-client.ts' })
    })
    // file tab press -> showFile($, path) -> $.mcp.call('ticket.read_file', { ticket: 'checkout-flow', path: 'pane/hooks/chat-bar/chat-bar-client.ts' }) -> Ticket.read_file()
    then("the tab shows the file's text, starting // Model shell for the chat bar", async ($, on, scene) => {
      expect(textOf(await findText(scene.ui, /^\/\/ Model shell/))).toBe('// Model shell for the chat bar')
      expect(called(scene.world, 'ticket.read_file')).toEqual({ ticket: 'checkout-flow', path: 'pane/hooks/chat-bar/chat-bar-client.ts' })
    })
  })
  scenario('Refuse a file outside the repository', ({ given, when, then }) => {
    // Evidence: inferred: mirrors kanban_tools_spec 'should refuse a file outside the repository, naming the path and the ticket'
    given("checkout-flow's repository is the project folder", async ($, on, scene) => {
      scene.world.answers['ticket.files'] = { 'clean_engineering-model': { typescript: [{ path: '../secrets.txt', exists: false }] } }
      scene.world.refusals['ticket.read_file'] = '../secrets.txt is not a file in this repository'
    })
    when('a file outside the repository is asked for', async ($, on, scene) => {
      await scene.ui.press({ key: 'dot-clean_engineering-model' })
      await scene.ui.press({ key: 'files-button' })
    })
    // $.mcp.call('ticket.read_file', { ticket: 'checkout-flow', path: '../secrets.txt' }) <- FileOutsideRepositoryError
    then('the tab says ../secrets.txt is not a file in this repository', async ($, on, scene) => {
      expect(textOf(await findText(scene.ui, /secrets/))).toBe('../secrets.txt is not a file in this repository')
    })
  })
  scenario('Read the violations from their count', ({ given, when, then, and }) => {
    // Evidence: requested: a press on the red violation count opens the violations, as the board does
    given("checkout-flow's clean_engineering-model has 7 violations in its latest validation report", async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'clean_engineering-model': { ...VALIDATED, progress: 'violations', violations: 7 } }))
      scene.world.answers['ticket.report'] = { path: '.sessions/checkout-flow/validation-reports/clean-engineering-model.md', text: '# Validation\n\n## no-legacy-api-after-refactor\n\nFail', rules: [], has_saved_graph: false }
    })
    when('the Person presses the count 7', async ($, on, scene) => {
      await scene.ui.press({ key: 'violations-clean_engineering-model' })
    })
    // count press -> openReport($, fidelity) -> $.mcp.call('ticket.report', { ticket: 'checkout-flow', fidelity: 'clean_engineering-model' }) -> Ticket.report()
    then('the report opens in its own tab', async ($, on, scene) => {
      expect(called(scene.world, 'ticket.report')).toEqual({ ticket: 'checkout-flow', fidelity: 'clean_engineering-model' })
      expect(await drawn(scene.ui, 'file-.sessions/checkout-flow/validation-reports/clean-engineering-model.md')).toBeDefined()
    })
    and('its text is drawn as markdown', async ($, on, scene) => {
      expect((await drawn(scene.ui, 'file-markdown'))?.props?.text).toBe('# Validation\n\n## no-legacy-api-after-refactor\n\nFail')
    })
  })
})
