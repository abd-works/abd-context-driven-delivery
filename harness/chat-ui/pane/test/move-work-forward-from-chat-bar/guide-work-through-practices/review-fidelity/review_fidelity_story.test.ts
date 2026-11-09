import { expect } from 'claude-code/testing'

import { called } from '../../../cdd-stub'
import { boardOf, checkoutFlowWith, VALIDATED } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, expectStates, markOf, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Guide Work Through Practices
// Map: ../../../../../.context/story-map.md#s-person----review-fidelity
// Model: ../../../../../../../space/kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Review Fidelity
story('Review Fidelity', CHAT_BAR, () => {
  scenario('Review a fidelity after a clean validate', ({ given, when, then }) => {
    // Evidence: inferred: mirrors Review Fidelity 'Review a fidelity after a clean validate'; no chat bar code yet
    given("checkout-flow's ux-mockup is the selected fidelity and its latest validate passed", async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'ux-mockup': VALIDATED }))
      await scene.ui.press({ key: 'dot-ux-mockup' })
    })
    when('the Person reviews ux-mockup', async ($, on, scene) => {
      await scene.ui.press({ key: 'next-action' })
    })
    // ChatBarView press -> reviewFidelity($, fidelity) -> $.mcp.call('fidelity-progress.finish_review', { ticket: 'checkout-flow', fidelity: 'ux-mockup' }) -> FidelityProgress.finish_review()
    // Ticket -> TicketWork.record('review UX mockup')
    then('the UX dot shows reviewed', async ($, on, scene) => {
      await expectStates(scene.ui, { 'ux-mockup': '✓ done' })
      expect(called(scene.world, 'fidelity-progress.finish_review')).toEqual({ ticket: 'checkout-flow', fidelity: 'ux-mockup' })
    })
  })
  scenario('Refuse a review before a clean validate', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'which needs its latest Validate to have passed'
    given("checkout-flow's clean-engineering-model is the selected fidelity, with 7 violations in its latest validation report", async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'clean-engineering-model': { ...VALIDATED, progress: 'violations', violations: 7 } }))
      scene.world.refusals['fidelity-progress.finish_review'] = 'clean-engineering-model cannot be reviewed: its latest validation report has 7 violations'
      await scene.ui.press({ key: 'dot-clean-engineering-model' })
    })
    when('the Person reviews clean-engineering-model', async ($, on, scene) => {
      // With violations the Ticket names review next.
      await scene.ui.press({ key: 'next-action' })
    })
    // action button press -> reviewFidelity($, fidelity) -> $.mcp.call('fidelity-progress.finish_review', ...) <- ReviewRefused with the server's text
    then("the Chat Bar shows the server's reason", async ($, on, scene) => {
      expect(scene.world.toasts).toContain('clean-engineering-model not reviewed: clean-engineering-model cannot be reviewed: its latest validation report has 7 violations')
    })
    and('the Clean Engineering dot still shows 7 in red', async ($, on, scene) => {
      const count = await markOf(scene.ui, 'violations-clean-engineering-model-mark')
      expect([textOf(count), count?.props?.color]).toEqual(['7', '#EF4444'])
    })
  })
})
