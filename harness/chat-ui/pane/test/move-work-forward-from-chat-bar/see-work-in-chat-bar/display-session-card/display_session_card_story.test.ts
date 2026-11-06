import { expect } from 'claude-code/testing'

import { boardOf, checkoutFlowWith, DONE } from '../../../examples/chat-bar.examples'
import { CHAT_BAR, drawn, findText, markOf, textOf } from '../../../chat-bar-screen'
import { scenario, story } from '../../../story-test'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: See Work In Chat Bar
// Map: ../../../../../.context/story-map.md#s-person----display-session-card
// Model: ../../../../../../kanban/.context/kanban-model.md
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
    then("the card opens over the strip with each fidelity's colour, name and state over its dot, such as Scenarios done over the Stories dot", async ($, on, scene) => {
      const rows = await Promise.all(['card-stories-scenarios', 'card-ux-mockup', 'card-clean-engineering-model'].map(async key => (await drawn(scene.ui, key))?.children?.map(textOf)))
      expect(rows).toEqual([['✓', 'Scenarios done', 'harness/chat-ui/.context'], ['○', 'Mockup to do', 'harness/chat-ui/design'], ['○', 'Model to do', 'harness/chat-ui/pane']])
      expect((await markOf(scene.ui, 'card-stories-scenarios'))?.props?.color).toBe('#6BCB77')
    })
    and("each fidelity starts in its own dot's column, and Specification in its stage icon's", async ($, on, scene) => {
      // checkout-flow: health mark, gap, 13 letters, gap, ▾, gap, │, gap puts the first dot at column 20; the card's
      // border and padding take 2. Each dot then takes 2 with its gap. stories-scenarios, which the button follows, is
      // done, so no action button is drawn; │ takes 2 and the stage icons Backlog and Discovery 2 each, so the outlined
      // Specification starts at column 32.
      const indents = await Promise.all(['card-stories-scenarios', 'card-ux-mockup', 'card-clean-engineering-model', 'card-stage'].map(async key => (await drawn(scene.ui, key))?.props?.marginLeft))
      expect(indents).toEqual([18, 20, 22, 30])
      expect((await findText(scene.ui, 'Specification'))?.props?.color).toBe('#E5531A')
    })
    and("each fidelity's folders sit beside it", async ($, on, scene) => {
      expect(textOf(await findText(scene.ui, 'harness/chat-ui/pane'))).toBe('harness/chat-ui/pane')
    })
  })
  scenario('Show the card while the pointer is on the session name', ({ given, when, then }) => {
    // Evidence: inferred: CDR 0001 'Hovering the name opens the session card'
    given('the Chat Bar shows checkout-flow')
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
    given('cdd is connected')
    when('the Person opens the session card for checkout-flow', async ($, on, scene) => {
      await scene.ui.press({ key: 'session-name-button' })
    })
    then('the server health panel sits on top of the session card', async ($, on, scene) => {
      const card = (await drawn(scene.ui, 'session-card'))?.children?.[0]
      expect([card?.props?.display, card?.children?.[0]?.props?.key]).toEqual([undefined, 'card-health'])
    })
    and('it shows the same parts as the panel over the mark', async ($, on, scene) => {
      const parts = await Promise.all(['card-MCP host', 'card-Tools', 'card-Kanban app'].map(async key => (await drawn(scene.ui, key))?.children?.[1]))
      expect(parts.map(textOf)).toEqual(['running', '116 loaded', 'running :8778'])
    })
  })
})
