import { expect } from 'claude-code/testing'

import { CHAT_BAR, buttonKeys, drawn, markOf, textOf, tipOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Guide Work Through Practices
// Map: ../../../../../.context/story-map.md#s-person----choose-fidelity-action
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Choose Fidelity Action
story('Choose Fidelity Action', CHAT_BAR, () => {
  scenario('Pick another action for the fidelity', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'The picker offers every builder action'; no chat bar code yet
    given("checkout-flow's ux-mockup is the selected fidelity", async ($, on, scene) => {
      await scene.ui.press({ key: 'dot-ux-mockup' })
    })
    and("the ux-mockup dot sits on the selected tint", async ($, on, scene) => {
      expect((await drawn(scene.ui, 'fidelity-ux-mockup'))?.props?.backgroundColor).toBe('#FFFFFF33')
      expect((await drawn(scene.ui, 'fidelity-stories-scenarios'))?.props?.backgroundColor).toBeUndefined()
    })
    when('the Person opens the action picker', async ($, on, scene) => {
      await scene.ui.press({ key: 'action-picker' })
    })
    then('it offers generate, validate, review, iterate, sketch, render and document', async ($, on, scene) => {
      expect(buttonKeys(await drawn(scene.ui, 'picker'))).toEqual(['pick-generate', 'pick-validate', 'pick-review', 'pick-iterate', 'pick-sketch', 'pick-render', 'pick-document'])
    })
    when('the Person chooses iterate', async ($, on, scene) => {
      await scene.ui.press({ key: 'pick-iterate' })
    })
    // picker press -> chooseAction($, 'iterate') puts iterate on the button
    then('the action button shows iterate, with iterate ux-mockup on hover', async ($, on, scene) => {
      expect(textOf(await markOf(scene.ui, 'next-action-mark'))).toBe('↻')
      expect(await tipOf(scene.ui, 'action')).toBe('iterate ux-mockup')
      expect(await drawn(scene.ui, 'picker')).toBeUndefined()
      expect(scene.world.sent).not.toContain('/actions-iterate ux-mockup')
    })
    when('the Person runs the action', async ($, on, scene) => {
      await scene.ui.press({ key: 'next-action' })
    })
    // action button press -> runAction($, fidelity, 'iterate') -> $.command.run({ command: 'actions-iterate', args: 'ux-mockup' })
    then('the chat runs /actions-iterate ux-mockup, and the button shows the next action again', async ($, on, scene) => {
      expect(scene.world.sent).toContain('/actions-iterate ux-mockup')
      expect(await tipOf(scene.ui, 'action')).not.toBe('iterate ux-mockup')
    })
  })
})
