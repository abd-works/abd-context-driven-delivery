import { expect } from 'claude-code/testing'

import { boardOf, checkoutFlowWith, DONE, GENERATED, VALIDATED } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, buttonKeys, drawn, expectMarkColours, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: See Work In Chat Bar
// Map: ../../../../../.context/story-map.md#s-chat-bar----display-fidelity-progress
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Chat Bar --> Display Fidelity Progress
story('Display Fidelity Progress', CHAT_BAR, () => {
  scenario('Shade each dot by its progress', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'Fidelity dots'; no chat bar code yet
    given('checkout-flow is In progress in Specification with the practices Stories, UX and Clean Engineering')
    and('its [fidelity progress](../../../../../../kanban/.context/kanban-model.md#fidelityprogress) is stories-scenarios done, ux-mockup in progress and clean_engineering-model not started', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'stories-scenarios': DONE, 'ux-mockup': GENERATED }))
    })
    when('the Chat Bar draws checkout-flow')
    // ChatBarView -> FidelityView($, fidelity) for each FidelityClient; FidelityClient.status <- TicketData.progress
    then('three dots show in the Stories, UX and Clean Engineering colours, shaded done, in progress and not started as on the board', async ($, on, scene) => {
      expect(buttonKeys(await drawn(scene.ui, 'line')).filter(key => key.startsWith('dot-'))).toEqual(['dot-stories-scenarios', 'dot-ux-mockup', 'dot-clean_engineering-model'])
      await expectMarkColours(scene.ui, { 'dot-stories-scenarios-mark': '#6BCB77FF', 'dot-ux-mockup-mark': '#E8439380', 'dot-clean_engineering-model-mark': '#4FC3F740' })
    })
  })
  scenario('Show a violation count in red', ({ given, when, then }) => {
    // Evidence: inferred: CDR 0001 'A fidelity with violations keeps its colour and shows its count in red'
    given("checkout-flow's clean_engineering-model has 7 violations in its latest validation report", async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'clean_engineering-model': { ...VALIDATED, progress: 'violations', violations: 7 } }))
    })
    when('the Chat Bar draws checkout-flow')
    // FidelityClient.violationCount <- TicketData.violation_counts
    then('the Clean Engineering dot keeps its colour and shows 7 in red', async ($, on, scene) => {
      await expectMarkColours(scene.ui, { 'dot-clean_engineering-model-mark': '#4FC3F7FF' })
      const count = (await drawn(scene.ui, 'fidelity-clean_engineering-model'))?.children?.[1]
      expect([textOf(count), count?.props?.color]).toEqual(['7', '#EF4444'])
    })
  })
})
