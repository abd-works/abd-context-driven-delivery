import { expect } from 'claude-code/testing'

import { called } from '../../../cdd-stub'
import { MODEL_FILES } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, filesPaneOf, labelOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Guide Work Through Practices
// Map: ../../../../../.context/story-map.md#s-person----list-session-files
// Model: ../../../../../../../space/kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> List Session Files
story('List Session Files', CHAT_BAR, () => {
  scenario('Open a tab per file of the selected fidelity', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 "Files opens the board's files view for the selected fidelity only"; no chat bar code yet
    given("checkout-flow's clean-engineering-model is the selected fidelity", async ($, on, scene) => {
      await scene.ui.press({ key: 'dot-clean-engineering-model' })
    })
    and('it declares pane/hooks/chat-bar/chat-bar-client.ts and pane/hooks/chat-bar/fidelity-progress-client.ts', async ($, on, scene) => {
      scene.world.declared['clean-engineering-model'] = MODEL_FILES
    })
    when('the Person lists the files', async ($, on, scene) => {
      await scene.ui.press({ key: 'files-button' })
    })
    // ChatBarView press -> openFiles($, fidelity) -> $.mcp.call('fidelity-progress.files', { ticket: 'checkout-flow', fidelity: 'clean-engineering-model' }) -> FidelityProgress.files()
    then('a tab opens for chat-bar-client.ts and one for fidelity-progress-client.ts, as in View Fidelity Files', async ($, on, scene) => {
      const pane = await filesPaneOf($)
      const tabs = await Promise.all(['file-pane/hooks/chat-bar/chat-bar-client.ts', 'file-pane/hooks/chat-bar/fidelity-progress-client.ts'].map(key => labelOf(pane, key)))
      await pane.unmount()
      expect(tabs).toEqual(['chat-bar-client.ts', 'fidelity-progress-client.ts'])
      expect(called(scene.world, 'fidelity-progress.files')).toEqual({ ticket: 'checkout-flow', fidelity: 'clean-engineering-model' })
    })
  })
})
