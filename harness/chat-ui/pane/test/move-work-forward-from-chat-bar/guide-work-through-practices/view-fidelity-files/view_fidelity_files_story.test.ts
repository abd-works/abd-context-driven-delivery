import { expect } from 'claude-code/testing'

import { called } from '../../../cdd-stub'
import { CHAT_BAR, findText, textOf } from '../../../chat-bar-screen'
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
      scene.world.answers['fidelity-progress.files'] = { typescript: [{ path: 'pane/hooks/chat-bar/chat-bar-client.ts', exists: true }, { path: 'pane/hooks/chat-bar/fidelity-client.ts', exists: true }] }
      scene.world.answers['session.read_file'] = { path: 'pane/hooks/chat-bar/chat-bar-client.ts', text: '// Model shell for the chat bar\nexport class ChatBarClient {}' }
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
  scenario('Refuse a file outside the repository', ({ given, when, then }) => {
    // Evidence: inferred: mirrors kanban_tools_spec 'should refuse a file outside the repository, naming the path and the ticket'
    given("checkout-flow's repository is the project folder", async ($, on, scene) => {
      scene.world.answers['fidelity-progress.files'] = { typescript: [{ path: '../secrets.txt', exists: false }] }
      scene.world.refusals['session.read_file'] = '../secrets.txt is not a file in this repository'
    })
    when('a file outside the repository is asked for', async ($, on, scene) => {
      await scene.ui.press({ key: 'dot-clean-engineering-model' })
      await scene.ui.press({ key: 'files-button' })
    })
    // $.mcp.call('session.read_file', { session: '.sessions/checkout-flow/session.json', path: '../secrets.txt' }) <- FileOutsideRepositoryError
    then('the tab says ../secrets.txt is not a file in this repository', async ($, on, scene) => {
      expect(textOf(await findText(scene.ui, /secrets/))).toBe('../secrets.txt is not a file in this repository')
    })
  })
})
