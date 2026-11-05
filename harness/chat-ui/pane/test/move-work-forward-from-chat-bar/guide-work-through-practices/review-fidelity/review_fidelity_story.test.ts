import { expect } from 'claude-code/testing'

import { boardOf, called, cdd, checkoutFlowWith, DONE, drawn, labelOf, openChatBar, textOf, VALIDATED } from '../../../chat-bar-world'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Guide Work Through Practices
// Map: ../../../../../.context/story-map.md#s-person----review-fidelity
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Review Fidelity
story('Review Fidelity', () => {
  scenario('Review a fidelity after a clean validate', ({ given, when, then }) => {
    // Evidence: inferred: mirrors Review Fidelity 'Review a fidelity after a clean validate'; no chat bar code yet
    given("checkout-flow's ux-mockup is the selected fidelity and its latest validate passed", async ($, on, scene) => {
      scene.world = cdd(on, boardOf('checkout-flow', checkoutFlowWith({ 'ux-mockup': VALIDATED })))
      scene.ui = await openChatBar($)
      await scene.ui.press({ key: 'dot-ux-mockup' })
    })
    when('the Person reviews ux-mockup', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'ux-mockup': DONE }))
      scene.world.answers['ticket.finish_review'] = checkoutFlowWith({ 'ux-mockup': DONE })
      expect(await labelOf(scene.ui, 'next-action')).toBe('review ux-mockup')
      await scene.ui.press({ key: 'next-action' })
    })
    // ChatBarView press -> reviewFidelity($, fidelity) -> $.mcp.call('ticket.finish_review', { ticket: 'checkout-flow', fidelities: ['ux-mockup'] }) -> Ticket.finish_review()
    // Ticket -> Ticket.record('review UX mockup')
    then('the UX dot shows reviewed', async ($, on, scene) => {
      expect(await labelOf(scene.ui, 'dot-ux-mockup')).toBe('ux-mockup done')
      expect(called(scene.world, 'ticket.finish_review')).toEqual({ ticket: 'checkout-flow', fidelities: ['ux-mockup'] })
      await scene.ui.unmount()
    })
  })
  scenario('Refuse a review before a clean validate', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'which needs its latest Validate to have passed'
    given("checkout-flow's clean_engineering-model has 7 violations in its latest validation report", async ($, on, scene) => {
      scene.world = cdd(on, boardOf('checkout-flow', checkoutFlowWith({ 'clean_engineering-model': { ...VALIDATED, progress: 'violations', violations: 7 } })))
      scene.world.refusals['ticket.finish_review'] = 'clean_engineering-model cannot be reviewed: its latest validation report has 7 violations'
    })
    when('the Person reviews clean_engineering-model', async ($, on, scene) => {
      scene.ui = await openChatBar($)
      await scene.ui.press({ key: 'dot-clean_engineering-model' })
      await scene.ui.press({ key: 'next-action' })
    })
    // reviewFidelity($, fidelity) -> $.mcp.call('ticket.finish_review', ...) <- ReviewRefused with the server's text
    then("the Chat Bar shows the server's reason", async ($, on, scene) => {
      expect(scene.world.toasts).toContain('clean-engineering-model not reviewed: clean_engineering-model cannot be reviewed: its latest validation report has 7 violations')
    })
    and('the Clean Engineering dot still shows 7 in red', async ($, on, scene) => {
      const count = (await drawn(scene.ui, 'fidelity-clean_engineering-model'))?.children?.[1]
      expect([textOf(count), count?.props?.color]).toEqual(['7', '#EF4444'])
      await scene.ui.unmount()
    })
  })
})
