import { expect } from 'claude-code/testing'

import { boardOf, buttonKeys, cdd, checkoutFlowWith, DONE, drawn, GENERATED, markOf, openChatBar, textOf, VALIDATED } from '../../../chat-bar-world'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: See Work In Chat Bar
// Map: ../../../../../.context/story-map.md#s-chat-bar----display-fidelity-progress
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Chat Bar --> Display Fidelity Progress
story('Display Fidelity Progress', () => {
  scenario('Shade each dot by its progress', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'Fidelity dots'; no chat bar code yet
    given('checkout-flow is In progress in Specification with the practices Stories, UX and Clean Engineering', async ($, on, scene) => {
      scene.world = cdd(on)
    })
    and('its [fidelity progress](../../../../../../kanban/.context/kanban-model.md#fidelityprogress) is stories-scenarios done, ux-mockup in progress and clean_engineering-model not started', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'stories-scenarios': DONE, 'ux-mockup': GENERATED }))
    })
    when('the Chat Bar draws checkout-flow', async ($, on, scene) => {
      scene.ui = await openChatBar($)
    })
    // ChatBarView -> FidelityView($, fidelity) for each FidelityClient; FidelityClient.status <- TicketData.progress
    then('three dots show in the Stories, UX and Clean Engineering colours, shaded done, in progress and not started as on the board', async ($, on, scene) => {
      expect(buttonKeys(await drawn(scene.ui, 'line')).filter(key => key.startsWith('dot-'))).toEqual(['dot-stories-scenarios', 'dot-ux-mockup', 'dot-clean_engineering-model'])
      const shades = await Promise.all(['dot-stories-scenarios', 'dot-ux-mockup', 'dot-clean_engineering-model'].map(async key => (await markOf(scene.ui, key))?.props?.color))
      expect(shades).toEqual(['#6BCB77FF', '#E8439380', '#4FC3F740'])
      await scene.ui.unmount()
    })
  })
  scenario('Show a violation count in red', ({ given, when, then }) => {
    // Evidence: inferred: CDR 0001 'A fidelity with violations keeps its colour and shows its count in red'
    given("checkout-flow's clean_engineering-model has 7 violations in its latest validation report", async ($, on, scene) => {
      scene.world = cdd(on, boardOf('checkout-flow', checkoutFlowWith({ 'clean_engineering-model': { ...VALIDATED, progress: 'violations', violations: 7 } })))
    })
    when('the Chat Bar draws checkout-flow', async ($, on, scene) => {
      scene.ui = await openChatBar($)
    })
    // FidelityClient.violationCount <- TicketData.violation_counts
    then('the Clean Engineering dot keeps its colour and shows 7 in red', async ($, on, scene) => {
      expect((await markOf(scene.ui, 'dot-clean_engineering-model'))?.props?.color).toBe('#4FC3F7FF')
      const count = (await drawn(scene.ui, 'fidelity-clean_engineering-model'))?.children?.[1]
      expect([textOf(count), count?.props?.color]).toEqual(['7', '#EF4444'])
      await scene.ui.unmount()
    })
  })
})
