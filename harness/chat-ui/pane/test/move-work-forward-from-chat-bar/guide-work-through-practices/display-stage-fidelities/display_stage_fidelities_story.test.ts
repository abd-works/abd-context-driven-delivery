import { expect } from 'claude-code/testing'

import { boardOf, checkoutFlowWith, DONE } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, drawn, markOf, textOf, tipOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Guide Work Through Practices
// Map: ../../../../../.context/story-map.md#s-person----display-stage-fidelities
// Model: ../../../../../../kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Display Stage Fidelities
story('Display Stage Fidelities', CHAT_BAR, () => {
  scenario("Show an earlier stage's fidelities", ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 "Clicking a stage shows that stage's fidelities"; no chat bar code yet
    given("the Chat Bar shows checkout-flow's Specification dots with ux-mockup selected")
    and('its Discovery [fidelity progress](../../../../../../kanban/.context/kanban-model.md#fidelityprogress) is stories-story-map done, ux-ia not started and clean-engineering-modules done', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'stories-story-map': DONE, 'clean-engineering-modules': DONE }))
      await scene.ui.press({ key: 'dot-ux-mockup' })
    })
    when('the Person shows the Discovery [stage](../../../../../../kanban/.context/kanban-model.md#stage--column)', async ($, on, scene) => {
      await scene.ui.press({ key: 'stage-Discovery' })
    })
    // StageView press -> selectStage($, stage)
    then('the dots show stories-story-map done, ux-ia not started and clean-engineering-modules done', async ($, on, scene) => {
      const slugs = ['stories-story-map', 'ux-ia', 'clean-engineering-modules']
      expect(await Promise.all(slugs.map(slug => tipOf(scene.ui, `fidelity-${slug}`)))).toEqual(slugs)
      const states = await Promise.all(slugs.map(async slug => textOf((await drawn(scene.ui, `card-cell-${slug}`))?.children?.[2])))
      expect(states).toEqual(['✓ done', '○ to do', '✓ done'])
    })
    and('no dot is selected, because ux-mockup is not a Discovery fidelity', async ($, on, scene) => {
      const marks = await Promise.all(['dot-stories-story-map', 'dot-ux-ia', 'dot-clean-engineering-modules'].map(async key => textOf(await markOf(scene.ui, `${key}-mark`))))
      expect(marks).toEqual(['■', '■', '■'])
    })
  })
})
