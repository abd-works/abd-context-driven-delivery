import { expect } from 'claude-code/testing'

import { boardOf, checkoutFlow, checkoutFlowWith, DONE, HEALTHY } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, drawn, findText, markOf, stateOf, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: See Work In Chat Bar
// Map: ../../../../../.context/story-map.md#s-person----display-session-card
// Model: ../../../../../../../space/kanban/.context/kanban-model.md
// Realizations: inline under each step, along the mod's line: view -> action($, client) -> MCP tool -> domain

// (S) Person --> Display Session Card
story('Display Session Card', CHAT_BAR, () => {
  scenario('Lay the session card over the strip', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'Session name and session list'; no chat bar code yet
    given('the Chat Bar shows checkout-flow In progress in Specification with stories-scenarios done', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlowWith({ 'stories-scenarios': DONE }))
    })
    when('the Person opens the session card for checkout-flow', async ($, on, scene) => {
      await scene.ui.press({ key: 'session-name-button' })
    })
    // ChatBarView paints the session card from the same ChatBarClient
    then("the card opens with each fidelity's colour, name and state, such as Scenarios done in the Stories colour", async ($, on, scene) => {
      const slugs = ['stories-scenarios', 'ux-mockup', 'clean-engineering-model']
      const names = await Promise.all(slugs.map(async slug => textOf(await markOf(scene.ui, `card-pick-${slug}-mark`))))
      expect(names).toEqual(['Scenarios', 'Mockup', 'Model'])
      const states = await Promise.all(slugs.map(slug => stateOf(scene.ui, slug)))
      expect(states).toEqual(['✓ done', '○ to do', '○ to do'])
      expect((await markOf(scene.ui, 'card-cell-stories-scenarios'))?.props?.color).toBe('#6BCB77FF')
      expect((await findText(scene.ui, 'Specification'))?.props?.color).toBe('#E5531A')
    })
    and('the fidelities start over the first dot, and the folders in one column after the widest row', async ($, on, scene) => {
      // checkout-flow is 13 letters; ▾, │ and their gaps take 5 more. The widest row, ■ Scenarios ✓ done, takes 18, and
      // 3 more set the folders apart.
      const indents = await Promise.all(['card-stories-scenarios', 'card-ux-mockup', 'card-clean-engineering-model'].map(async key => (await drawn(scene.ui, key))?.props?.marginLeft))
      expect(indents).toEqual([18, 18, 18])
      const header = (await drawn(scene.ui, 'card-header'))?.children?.map((cell: any) => cell?.props?.width)
      expect(header?.slice(0, 2)).toEqual([18, 21])
    })
    and("each fidelity's folders sit beside it", async ($, on, scene) => {
      expect(textOf(await markOf(scene.ui, 'card-folder-clean-engineering-model-mark'))).toBe('▸ harness/chat-ui/pane')
    })
  })
  scenario('Close the pinned session card', ({ given, when, then }) => {
    // Evidence: requested: the person could not collapse the pinned card
    given('the session card for checkout-flow is pinned open', async ($, on, scene) => {
      await scene.ui.press({ key: 'session-name-button' })
    })
    when('the Person closes the card', async ($, on, scene) => {
      await scene.ui.press({ key: 'card-close' })
    })
    then('the card shows only while the pointer is on the session name', async ($, on, scene) => {
      expect((await drawn(scene.ui, 'session-card'))?.children?.[0]?.props?.display).toBe('none')
    })
  })
  scenario('Show the card while the pointer is on the session name', ({ given, when, then }) => {
    // Evidence: inferred: CDR 0001 'Hovering the name opens the session card'
    given('the Chat Bar shows checkout-flow', async ($, on, scene) => {
      scene.world.board = boardOf('checkout-flow', checkoutFlow())
    })
    // The surface applies a hover without calling the mod, so the drawn tree says what the hover reveals.
    when('the Person rests the pointer on checkout-flow')
    then('the session card shows, and stays while the pointer is on the card or the name', async ($, on, scene) => {
      const card = (await drawn(scene.ui, 'session-card'))?.children?.[0]
      expect([card?.props?.display, card?.hover]).toEqual(['none', { display: 'flex', scope: 'session-card' }])
      const name = (await drawn(scene.ui, 'session-name'))?.children?.[1]
      expect(name?.hover).toEqual({ scope: 'session-card' })
    })
  })
  scenario('Stack the health panel on the card', ({ given, when, then, and }) => {
    // Evidence: inferred: CDR 0001 'Hovering the session name stacks the same panel on top of the session card'
    given('cdd is connected', async ($, on, scene) => {
      scene.world.health = HEALTHY
    })
    when('the Person opens the session card for checkout-flow', async ($, on, scene) => {
      await scene.ui.press({ key: 'session-name-button' })
    })
    then('the server health panel sits on top of the session card', async ($, on, scene) => {
      const card = (await drawn(scene.ui, 'session-card'))?.children?.[0]
      expect([card?.props?.display, card?.children?.[0]?.props?.key]).toEqual([undefined, 'card-health'])
    })
    and('it shows the same parts as the panel over the mark', async ($, on, scene) => {
      const parts = await Promise.all(['MCP host', 'Tools', 'Kanban app'].map(async key => (await drawn(scene.ui, key))?.children?.[1]))
      expect(parts.map(textOf)).toEqual(['running', '116 loaded', 'running :8778'])
    })
  })
})
