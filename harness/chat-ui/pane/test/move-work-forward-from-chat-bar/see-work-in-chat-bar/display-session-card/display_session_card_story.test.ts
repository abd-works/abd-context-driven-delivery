import { expect } from 'claude-code/testing'

import { boardOf, cdd, checkoutFlowWith, DONE, drawn, findText, markOf, openChatBar, textOf } from '../../../chat-bar-world'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: See Work In Chat Bar
// Map: ../../../../../.context/story-map.md#s-person----display-session-card
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Display Session Card
story('Display Session Card', () => {
  scenario('Lay the session card over the strip', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'Session name and session list'; no chat bar code yet
    given('the Chat Bar shows checkout-flow In progress in Specification with stories-scenarios done', async ($, on, scene) => {
      scene.world = cdd(on, boardOf('checkout-flow', checkoutFlowWith({ 'stories-scenarios': DONE })))
      scene.ui = await openChatBar($)
    })
    when('the Person opens the session card for checkout-flow', async ($, on, scene) => {
      await scene.ui.press({ key: 'session-name-button' })
    })
    // ChatBarView paints the session card from the same ChatBarClient
    then("the card opens over the strip with each fidelity's colour, name and state over its dot, such as Scenarios done over the Stories dot", async ($, on, scene) => {
      const rows = await Promise.all(['card-stories-scenarios', 'card-ux-mockup', 'card-clean_engineering-model'].map(async key => (await drawn(scene.ui, key))?.children?.map(textOf)))
      expect(rows).toEqual([['✓', 'Scenarios done', 'harness/chat-ui/.context'], ['○', 'Mockup to do', 'harness/chat-ui/design'], ['○', 'Model to do', 'harness/chat-ui/pane']])
      expect((await markOf(scene.ui, 'card-stories-scenarios'))?.props?.color).toBe('#6BCB77')
    })
    and('Specification sits over the stage icons', async ($, on, scene) => {
      expect((await findText(scene.ui, 'Specification'))?.props?.color).toBe('#E5531A')
    })
    and("each fidelity's folders sit beside it", async ($, on, scene) => {
      expect(textOf(await findText(scene.ui, 'harness/chat-ui/pane'))).toBe('harness/chat-ui/pane')
      await scene.ui.unmount()
    })
  })
  scenario('Stack the health panel on the card', ({ given, when, then }) => {
    // Evidence: inferred: CDR 0001 'Hovering the session name stacks the same panel on top of the session card'
    given('cdd is connected', async ($, on, scene) => {
      scene.world = cdd(on)
    })
    when('the Person opens the session card for checkout-flow', async ($, on, scene) => {
      scene.ui = await openChatBar($)
      await scene.ui.press({ key: 'session-name-button' })
    })
    then('the server health panel sits on top of the session card', async ($, on, scene) => {
      expect(await drawn(scene.ui, 'session-card')).toBeDefined()
      expect(textOf(await markOf(scene.ui, 'health-icon'))).toBe('✓')
      await scene.ui.unmount()
    })
  })
})
