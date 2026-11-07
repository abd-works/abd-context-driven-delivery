import { expect } from 'claude-code/testing'

import { boardOf, checkoutFlow, checkoutFlowWith, GENERATED } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, findText, markOf, textOf, tipOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Guide Work Through Practices
// Map: ../../../../../.context/story-map.md#s-person----invoke-next-fidelity-action
// Model: ../../../../../../../space/kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Invoke Next Fidelity Action
story('Invoke Next Fidelity Action', CHAT_BAR, () => {
  scenario('Run the next action on the selected fidelity', ({ given, when, then }) => {
    // Evidence: inferred: CDR 0001 'Action button and ▾ picker' and 'Actions run on one fidelity at a time'; no chat bar code yet
    given("checkout-flow's ux-mockup is generated and is the selected fidelity", async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'ux-mockup': GENERATED }))
      await scene.ui.press({ key: 'dot-ux-mockup' })
    })
    when('the Person runs the next action', async ($, on, scene) => {
      await scene.ui.press({ key: 'next-action' })
    })
    // ChatBarView press -> runAction($, fidelity, 'validate') -> promptCommand -> $.prompt.fill({ text: '/actions-validate ux-mockup session=.sessions/checkout-flow/session.json', mode: 'append' })
    then("/actions-validate ux-mockup in checkout-flow's session waits in the prompt box for the Person to send", async ($, on, scene) => {
      expect(scene.world.fills).toEqual(['/actions-validate ux-mockup session=.sessions/checkout-flow/session.json'])
      expect(scene.world.sent).toEqual([])
    })
  })
  scenario("Generate in the stage's default format", ({ given, when, then }) => {
    // Evidence: Stage.default_formats; the generate action renders the earlier fidelity first when its file is missing
    given("checkout-flow's clean-engineering-model is not started and is the selected fidelity", async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlow())
      await scene.ui.press({ key: 'dot-clean-engineering-model' })
    })
    when('the Person runs the next action', async ($, on, scene) => {
      await scene.ui.press({ key: 'next-action' })
    })
    // ChatBarView press -> runAction($, fidelity, 'generate') -> promptCommand -> $.prompt.fill({ text: '/actions-generate clean-engineering-model format=typescript session=...', mode: 'append' })
    then("/actions-generate clean-engineering-model in typescript, in checkout-flow's session, waits in the prompt box", async ($, on, scene) => {
      expect(scene.world.fills).toEqual(['/actions-generate clean-engineering-model format=typescript session=.sessions/checkout-flow/session.json'])
    })
  })
  scenario('Show the next action before it runs', ({ given, when, then }) => {
    // Evidence: inferred: CDR 0001 'The button shows the next action for one fidelity as an icon'
    given("checkout-flow's ux-mockup is generated and is the selected fidelity", async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'ux-mockup': GENERATED }))
      await scene.ui.press({ key: 'dot-ux-mockup' })
    })
    when('the Chat Bar draws checkout-flow', async ($, on, scene) => {
      await $.prompt.submit({ text: 'again' })
    })
    then('the button shows the validate icon, with validate ux-mockup on hover', async ($, on, scene) => {
      expect(textOf(await markOf(scene.ui, 'next-action-mark'))).toBe('✓')
      expect(await tipOf(scene.ui, 'action')).toBe('validate ux-mockup')
      expect(textOf(await findText(scene.ui, 'validate ux-mockup'))).toBe('validate ux-mockup')
    })
  })
})
