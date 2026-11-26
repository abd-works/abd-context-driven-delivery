// Reported 2026-11-19: after a dev lane repin and /reload-plugins neither the chat bar nor the queue showed above the
// prompt, and no red "chat bar failed to draw" line showed. The bar's draw read the server health, the CDD version and
// the push state before its guard, so a read that threw there left no bar and no reason. Every read of the draw is now
// inside the guard.
import { expect, test } from 'claude-code/testing'

const BAND = {
  plugin: 'cdd-board',
  component: 'AbovePrompt',
  requestId: 'above-prompt',
  props: { hasSurvey: false, isCollapsed: false, isWorking: false, maxRows: 24, bodyColumns: 120, scroll: { offset: 0, bodyRows: 24 }, view: {} },
} as const

// The stored values the CDD version is read from, refused as a read the engine cannot answer.
const REFUSED_KEY = 'cddVersion'

test('a chat bar whose stored CDD version cannot be read shows why in red, in place of the bar', async ($, on) => {
  on('session.root', () => ({ value: 'C:/work/notes' }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('state.get', (_, e) => {
    if ((e as { key: string }).key === REFUSED_KEY) return { deny: 'the stored CDD version could not be read' }
    return { value: { value: undefined, version: 0 } }
  })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect((await ui.find({ type: 'Text', text: /^chat bar failed to draw: / }))?.text).toContain('the stored CDD version could not be read')
  await ui.unmount()
})
