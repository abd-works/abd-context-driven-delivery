import { expect } from 'claude-code/testing'

import { called } from '../../../cdd-stub'
import { boardOf, checkoutFlowWith, VALIDATED } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, drawn, textOf, tipOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Guide Work Through Practices
// Map: ../../../../../.context/story-map.md#s-person----review-fidelity
// Model: ../../../../../../kanban/.context/kanban-model.md
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
      expect(await tipOf(scene.ui, 'action')).toBe('review ux-mockup')
      await scene.ui.press({ key: 'next-action' })
    })
    // ChatBarView press -> reviewFidelity($, fidelity) -> $.mcp.call('ticket.finish_review', { ticket: 'checkout-flow', fidelities: ['ux-mockup'] }) -> Ticket.finish_review()
    // Ticket -> Ticket.record('review UX mockup')
    then('the UX dot shows reviewed', async ($, on, scene) => {
      expect(await tipOf(scene.ui, 'fidelity-ux-mockup')).toBe('ux-mockup ✓ done')
      expect(called(scene.world, 'ticket.finish_review')).toEqual({ ticket: 'checkout-flow', fidelities: ['ux-mockup'] })
    })
  })
  scenario('Review the violations before a clean validate', ({ given, when, then, and }) => {
    // Evidence: requested: a person reviews the violations and tells the agent to fix them
    given("checkout-flow's clean_engineering-model has 7 violations in its latest validation report", async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'clean_engineering-model': { ...VALIDATED, progress: 'violations', violations: 7 } }))
    })
    when('the Person reviews clean_engineering-model', async ($, on, scene) => {
      // With violations the Ticket names review next.
      await scene.ui.press({ key: 'dot-clean_engineering-model' })
      expect(await tipOf(scene.ui, 'action')).toBe('review clean-engineering-model')
      await scene.ui.press({ key: 'next-action' })
    })
    // action button press -> openBoard($, fidelity) -> /board checkout-flow clean_engineering-model
    then('the board opens on clean_engineering-model, where its report shows the violations to fix', async ($, on, scene) => {
      expect(scene.world.sent).toContain('/board checkout-flow clean_engineering-model')
      expect(scene.world.calls).not.toContain('ticket.finish_review')
    })
    and('the Clean Engineering dot still shows 7 in red', async ($, on, scene) => {
      const count = (await drawn(scene.ui, 'fidelity-clean_engineering-model'))?.children?.[1]
      expect([textOf(count), count?.props?.color]).toEqual(['7', '#EF4444'])
    })
  })
})
