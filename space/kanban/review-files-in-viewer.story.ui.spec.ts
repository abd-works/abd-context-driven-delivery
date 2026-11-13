/**
 * Review Files In Viewer at the browser tier: the scenarios that only the board app's page shows.
 *
 * Scenarios: harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-files-in-viewer/review_files_in_viewer_story.test.md.
 * The Python tiers replay the rest from review-files-in-viewer.story.shared.py.
 *
 * Each scenario runs against the board app built and served on the throwaway fixture project
 * (space/kanban/app/test-utils/fixture-repo.ts) with its real cdd server. checkout-flow's session works on the whole
 * fixture project, so its order.py is kept in its own session folder, where the files panel opens from the ticket's name
 * in the details; a Given seeds that folder: the file, the graph the session saved, or the comments it keeps.
 * A chat is `FakeChat`, which checks in through the board's server as the cdd-board mod does.
 */
import { readFileSync } from 'node:fs'
import { join } from 'node:path'

import { BOARD_POST_HEADERS, expect, FakeChat, fixtureRoot, openBoard, resetSessions, test, toast, waitForChat, writeInto } from './app/tests/story-ui'
import type { Locator, Page } from './app/tests/story-ui'

const SESSION = join(fixtureRoot, '.sessions', 'checkout-flow')
const ORDER = '.sessions/checkout-flow/order.py'
const ANCHOR = `${ORDER}:L12-L14`
const COMMENT = 'an empty cart should say which cart and why'
const LINE_14 = '            raise EmptyCartError(cart.id)'
const CHANGED_14 = '            raise EmptyCartError(cart.id, "a cart needs one item to be placed")'
// order.py: the class Order on lines 5 to 41, its operation place on lines 12 to 14.
const ORDER_LINES = [
  'from checkout.cart import Cart, EmptyCartError',
  '',
  '',
  '# An order placed from a cart.',
  'class Order:',
  '    def __init__(self, cart: Cart) -> None:',
  '        self.cart = cart',
  '',
  '    @classmethod',
  '    def empty(cls) -> "Order":',
  '        return cls(Cart())',
  '    def place(self, cart: Cart) -> Order:',
  '        if not cart.items:',
  LINE_14,
  ...Array.from({ length: 27 }, (_, index) => `        # step ${index + 15}`),
]
// The graph checkout-flow saved, in the shape harness/graph/saved_graph.py writes (SAVED_SHAPE_VERSION 3).
const ORDER_GRAPH = {
  version: 3,
  overlays: [],
  practices: {
    clean_engineering: {
      source_root: '',
      root_facts: {},
      nodes: [
        { node_id: 'order', name: 'Order', type: 'OoadClass', practice: 'clean_engineering', file: ORDER, line: 5, end_line: 41, stage: '', facts: {} },
        { node_id: 'place', name: 'place', type: 'Operation', practice: 'clean_engineering', file: ORDER, line: 12, end_line: 14, stage: '', facts: {} },
      ],
      edges: [],
      violations: [{ rule: 'vocabulary-traces-to-source', practice: 'clean_engineering', node_id: 'place', subject: 'place', location: ORDER, line: 12, end_line: 14, message: 'EmptyCartError should say which cart and why', severity: 'error', source: [] }],
    },
  },
}

const files = (page: Page) => page.locator('[data-panel="files"]')
const row = (page: Page, line: number): Locator => files(page).locator(`.code-row[data-line="${line}"]`)
const marker = (page: Page, line: number): Locator => row(page, line).locator('.comment-marker')

// Seed: order.py in checkout-flow's session folder; with comments, the session's file-comments.json, as FileComments keeps it.
type SeededComment = { start: number; end: number; text: string; chat?: string; message?: string; sent_text?: string }

function seedOrder(...comments: SeededComment[]): void {
  seedOrderAs(ORDER_LINES, ...comments)
}

// order.py reading `lines`, as a chat's turn left it; a sent comment keeps the file's text as it read when sent.
function seedOrderAs(lines: string[], ...comments: SeededComment[]): void {
  writeInto(join(SESSION, 'order.py'), `${lines.join('\n')}\n`)
  const records = comments.map(({ start, end, text, chat = '', message = '', sent_text = '' }) => ({ path: ORDER, start_line: start, end_line: end, selected_text: ORDER_LINES.slice(start - 1, end).join('\n'), text, chat, message, sent_text }))
  if (comments.length) writeInto(join(SESSION, 'file-comments.json'), JSON.stringify({ comments: records }))
}

// A comment sent in a message its chat no longer has counts as processed (FileComment.state).
const PROCESSED = { chat: 'gone-chat', message: 'gone-message' }

async function viewOrder(page: Page): Promise<void> {
  await openBoard(page)
  await page.locator('.details-bar').getByRole('button', { name: 'checkout-flow', exact: true }).click()
  await files(page).getByRole('tab', { name: 'order.py', exact: true }).click()
  await expect(row(page, 12)).toBeVisible()
}

async function selectLines(page: Page, start: number, end: number): Promise<void> {
  await row(page, start).getByRole('button', { name: `Line ${start}`, exact: true }).click()
  await row(page, end).getByRole('button', { name: `Line ${end}`, exact: true }).click({ modifiers: ['Shift'] })
}

async function addComment(page: Page, text: string): Promise<void> {
  await files(page).locator('.selection-bar').getByRole('button', { name: 'Comment' }).click()
  await files(page).getByRole('textbox', { name: 'Comment' }).fill(text)
  await files(page).getByRole('button', { name: 'Add comment' }).click()
}

test.beforeEach(() => resetSessions(fixtureRoot))
test.afterAll(() => resetSessions(fixtureRoot))

test.describe('View Files In Rich Viewer', () => {
  test.describe('Show a code file in the viewer with its lines numbered', () => {
    test.beforeEach(async ({ page }) => {
      seedOrder()
      await viewOrder(page)
    })

    test('Then the viewer shows order.py as Python, with line 12 reading def place(self, cart: Cart) -> Order:', async ({ page }) => {
      await expect(files(page).locator('.file-viewer')).toHaveAttribute('data-language', 'python')
      await expect(row(page, 12).locator('.line-text')).toHaveText('    def place(self, cart: Cart) -> Order:')
    })

    test('And the viewer is read-only', async ({ page }) => {
      await expect(files(page).locator('.file-editor')).toHaveCount(0)
    })

    test('And the Person can Add Comment To File Selection or Save Edited File from there', async ({ page }) => {
      await expect(files(page).getByRole('button', { name: 'Edit', exact: true })).toBeVisible()
      await selectLines(page, 12, 14)
      await expect(files(page).locator('.selection-bar').getByRole('button', { name: 'Comment' })).toBeVisible()
    })
  })

  test.describe('Render a markdown file as the page it describes', () => {
    test.beforeEach(async ({ page }) => {
      writeInto(join(SESSION, 'README.md'), '# Checkout\n\nPlace an order from a cart.\n')
      await openBoard(page)
      await page.locator('.details-bar').getByRole('button', { name: 'checkout-flow', exact: true }).click()
      await files(page).getByRole('tab', { name: 'README.md', exact: true }).click()
    })

    test('Then the viewer shows Checkout rendered as a heading, not as # Checkout', async ({ page }) => {
      await expect(files(page).locator('.markdown-page').getByRole('heading', { name: 'Checkout' })).toBeVisible()
      await expect(files(page).getByText('# Checkout')).toHaveCount(0)
    })
  })

  test.describe("Fold the file's class and its operations", () => {
    test.beforeEach(async ({ page }) => {
      seedOrder()
      writeInto(join(SESSION, 'graph.json'), JSON.stringify(ORDER_GRAPH))
      await viewOrder(page)
    })

    test('Then the viewer offers a fold of Order over lines 5 to 41, and a fold of place over lines 12 to 14', async ({ page }) => {
      await expect(row(page, 5).getByRole('button', { name: 'Fold Order, lines 5 to 41' })).toBeVisible()
      await expect(row(page, 12).getByRole('button', { name: 'Fold place, lines 12 to 14' })).toBeVisible()
    })

    test('And folding Order hides its lines below its first', async ({ page }) => {
      await row(page, 5).getByRole('button', { name: 'Fold Order, lines 5 to 41' }).click()
      await expect(row(page, 12)).toHaveCount(0)
      await expect(row(page, 5).getByRole('button', { name: 'Unfold Order, lines 5 to 41' })).toBeVisible()
    })
  })

  test.describe('Mark the lines a broken rule names', () => {
    test.beforeEach(async ({ page }) => {
      seedOrder()
      writeInto(join(SESSION, 'graph.json'), JSON.stringify(ORDER_GRAPH))
      await viewOrder(page)
    })

    test('Then the viewer marks lines 12 to 14 with vocabulary-traces-to-source: EmptyCartError should say which cart and why', async ({ page }) => {
      for (const line of [12, 13, 14]) await expect(row(page, line).locator('.code-line')).toHaveClass(/is-violated/)
      await expect(row(page, 11).locator('.code-line')).not.toHaveClass(/is-violated/)
      await expect(row(page, 12).getByRole('note')).toHaveText('vocabulary-traces-to-source: EmptyCartError should say which cart and why')
    })
  })
})

test.describe('Save Edited File', () => {
  test.describe('Save the edited text to the file on disk', () => {
    test.beforeEach(async ({ page }) => {
      seedOrder()
      await viewOrder(page)
      await files(page).getByRole('button', { name: 'Edit', exact: true }).click()
      const editor = files(page).getByRole('textbox', { name: `Edit ${ORDER}` })
      await editor.fill((await editor.inputValue()).replace(LINE_14, CHANGED_14))
      await files(page).getByRole('button', { name: 'Save', exact: true }).click()
    })

    test('Then order.py on disk reads that line 14', async ({ page }) => {
      await expect(files(page).locator('.file-editor')).toHaveCount(0)
      expect(readFileSync(join(SESSION, 'order.py'), 'utf-8').split('\n')[13]).toBe(CHANGED_14)
    })

    test('And the viewer is read-only again, showing the saved text', async ({ page }) => {
      await expect(files(page).locator('.file-editor')).toHaveCount(0)
      await expect(row(page, 14).locator('.line-text')).toHaveText(CHANGED_14)
    })
  })
})

test.describe('Add Comment To File Selection', () => {
  test.describe("Mark a comment beside the selection's first line", () => {
    test.beforeEach(async ({ page }) => {
      seedOrder()
      await viewOrder(page)
      await selectLines(page, 12, 14)
      await addComment(page, COMMENT)
    })

    test('Then a comment marker shows beside line 12, not sent', async ({ page }) => {
      await expect(marker(page, 12)).toHaveAccessibleName(`Comment on ${ANCHOR}, not sent`)
    })

    test(`And checkout-flow's file comments hold ${ANCHOR} with that comment`, async ({ page }) => {
      await expect(marker(page, 12)).toBeVisible()
      const { comments: kept } = JSON.parse(readFileSync(join(SESSION, 'file-comments.json'), 'utf-8')) as { comments: { start_line: number; end_line: number; text: string }[] }
      expect(kept.map(comment => [comment.start_line, comment.end_line, comment.text])).toEqual([[12, 14, COMMENT]])
    })
  })

  test.describe('Open a file comment from its marker', () => {
    test.beforeEach(async ({ page }) => {
      seedOrder({ start: 12, end: 14, text: COMMENT })
      await viewOrder(page)
      await marker(page, 12).click()
    })

    test(`Then the viewer shows ${COMMENT} under lines 12 to 14`, async ({ page }) => {
      await expect(files(page).getByRole('group', { name: `Comment on ${ANCHOR}` })).toContainText(COMMENT)
    })
  })

  test.describe('Delete a file comment', () => {
    test.beforeEach(async ({ page }) => {
      seedOrder({ start: 12, end: 14, text: COMMENT })
      await viewOrder(page)
      await marker(page, 12).click()
      await files(page).getByRole('button', { name: 'Delete' }).click()
    })

    test('Then no comment marker shows beside line 12', async ({ page }) => {
      await expect(marker(page, 12)).toHaveCount(0)
    })
  })

  test.describe('Keep file comments when the page reloads', () => {
    test.beforeEach(async ({ page }) => {
      seedOrder()
      await viewOrder(page)
      await selectLines(page, 12, 14)
      await addComment(page, COMMENT)
      await expect(marker(page, 12)).toBeVisible()
      await page.reload()
      await page.locator('.details-bar').getByRole('button', { name: 'checkout-flow', exact: true }).click()
      await files(page).getByRole('tab', { name: 'order.py', exact: true }).click()
    })

    test('Then the comment marker still shows beside line 12', async ({ page }) => {
      await expect(marker(page, 12)).toHaveAccessibleName(`Comment on ${ANCHOR}, not sent`)
    })
  })
})

test.describe('Send File Comments To Chat', () => {
  let chat: FakeChat

  test.afterEach(() => chat?.stop())

  test.describe("Add a comment to the chat's queue", () => {
    test.beforeEach(async ({ page, request }) => {
      chat = new FakeChat(request, 'checkout-chat', 'checkout-chat')
      await chat.start()
      seedOrder({ start: 12, end: 14, text: COMMENT })
      await viewOrder(page)
      await waitForChat(page, chat)
      await marker(page, 12).click()
      await files(page).getByRole('button', { name: 'Send', exact: true }).click()
    })

    test('Then the checkout-chat queue holds a fill naming the lines and the comment', async () => {
      await expect.poll(() => chat.received.map(command => command.text).join('\n')).toContain(`${ORDER}:12-14: ${COMMENT}`)
    })

    test('And the comment marker beside line 12 shows the comment as sent', async ({ page }) => {
      await expect(marker(page, 12)).toHaveAccessibleName(`Comment on ${ANCHOR}, sent`)
    })
  })

  test.describe('Send every open comment at once', () => {
    test.beforeEach(async ({ page, request }) => {
      chat = new FakeChat(request, 'checkout-chat', 'checkout-chat')
      await chat.start()
      seedOrder({ start: 12, end: 14, text: COMMENT }, { start: 30, end: 31, text: 'say what this step does' })
      await viewOrder(page)
      await waitForChat(page, chat)
      await files(page).getByRole('button', { name: 'Send all open comments' }).click()
    })

    test('Then the markers beside lines 12 and 30 show their comments as sent', async ({ page }) => {
      await expect(marker(page, 12)).toHaveAccessibleName(`Comment on ${ANCHOR}, sent`)
      await expect(marker(page, 30)).toHaveAccessibleName(`Comment on ${ORDER}:L30-L31, sent`)
    })
  })

  test.describe('Keep the comment unsent when the chat is not connected', () => {
    test.beforeEach(async ({ page }) => {
      seedOrder({ start: 12, end: 14, text: COMMENT })
      await viewOrder(page)
      await marker(page, 12).click()
      await files(page).getByRole('button', { name: 'Send', exact: true }).click()
    })

    test("Then a toast says the chat is not connected: is the cdd-board mod loaded in it?", async ({ page }) => {
      await expect(toast(page, /is not connected: is the cdd-board mod loaded in it\?/)).toBeVisible()
    })

    test('And the comment marker beside line 12 shows the comment as not sent', async ({ page }) => {
      await expect(marker(page, 12)).toHaveAccessibleName(`Comment on ${ANCHOR}, not sent`)
    })
  })
})

test.describe('Show Changed File In Viewer', () => {
  let chat: FakeChat

  test.afterEach(() => chat?.stop())

  test.describe("Show the agent's change to the open file", () => {
    test.beforeEach(async ({ page, request }) => {
      chat = new FakeChat(request, 'checkout-chat', 'checkout-chat')
      await chat.start()
      seedOrder({ start: 12, end: 14, text: COMMENT })
      await viewOrder(page)
      await waitForChat(page, chat)
      await marker(page, 12).click()
      await files(page).getByRole('button', { name: 'Send', exact: true }).click()
      await expect(marker(page, 12)).toHaveAccessibleName(`Comment on ${ANCHOR}, sent`)
      // The chat takes the message, shows it, changes line 14, and its turn ends, as the cdd-board mod reports them.
      await expect.poll(() => (chat.received as { message?: string }[]).some(command => command.message)).toBe(true)
      const message = (chat.received as { message?: string }[]).find(command => command.message)!.message!
      await request.post(`/api/chat/${chat.id}/confirm`, { headers: BOARD_POST_HEADERS, data: { message, is_shown: true } })
      writeInto(join(SESSION, 'order.py'), `${ORDER_LINES.map(line => (line === LINE_14 ? CHANGED_14 : line)).join('\n')}\n`)
      await request.post(`/api/chat/${chat.id}/finish`, { headers: BOARD_POST_HEADERS, data: { message } })
    })

    test(`Then the viewer shows line 14 as ${CHANGED_14.trim()}`, async ({ page }) => {
      await expect(row(page, 14).locator('.line-text')).toHaveText(CHANGED_14)
    })

    test('And the comment marker still shows beside line 12, processed', async ({ page }) => {
      await expect(marker(page, 12)).toHaveAccessibleName(`Comment on ${ANCHOR}, processed`)
    })
  })
})

test.describe('Clear Processed File Comments', () => {
  test.describe('Clear the processed comments, keeping the rest', () => {
    test.beforeEach(async ({ page }) => {
      seedOrder({ start: 12, end: 14, text: COMMENT, ...PROCESSED }, { start: 40, end: 41, text: 'say what this step does' })
      await viewOrder(page)
      await expect(marker(page, 12)).toHaveAccessibleName(`Comment on ${ANCHOR}, processed`)
      await files(page).getByRole('button', { name: 'Clear processed comments' }).click()
    })

    test('Then no comment marker shows beside line 12', async ({ page }) => {
      await expect(marker(page, 12)).toHaveCount(0)
    })

    test('And the marker beside line 40 still shows, not sent', async ({ page }) => {
      await expect(marker(page, 40)).toHaveAccessibleName(`Comment on ${ORDER}:L40-L41, not sent`)
    })
  })
})

// The comment the chat processed, sent while order.py read ORDER_LINES; each Given seeds order.py as the turn left it.
const PROCESSED_ON_SENT = { start: 12, end: 14, text: COMMENT, ...PROCESSED, sent_text: `${ORDER_LINES.join('\n')}\n` }
const CHANGED_LINES = ORDER_LINES.map(line => (line === LINE_14 ? CHANGED_14 : line))
const ADDED_LINES = [...ORDER_LINES.slice(0, 14), '            # a cart needs one item', '            # to be placed', ...ORDER_LINES.slice(14)]
const changedRows = (page: Page): Locator => files(page).locator('.code-row[data-change]')
const lineOf = (page: Page, line: number): Locator => row(page, line).locator('.code-line')

test.describe('Show AI Changes As Diff', () => {
  test.describe('Mark the line the chat changed, with the line it replaced', () => {
    test.beforeEach(async ({ page }) => {
      seedOrderAs(CHANGED_LINES, PROCESSED_ON_SENT)
      await viewOrder(page)
    })

    test('Then the viewer marks line 14 as changed by the chat', async ({ page }) => {
      await expect(lineOf(page, 14)).toHaveAttribute('title', /Changed by the chat/)
      await expect(changedRows(page)).toHaveCount(1)
    })

    test(`And shows the line it replaced, ${LINE_14.trim()}, as removed above it`, async ({ page }) => {
      await expect(row(page, 14).getByRole('group', { name: 'Lines removed above line 14' }).locator('.line-text')).toHaveText([LINE_14])
    })
  })

  test.describe('Mark the lines the chat added', () => {
    test.beforeEach(async ({ page }) => {
      seedOrderAs(ADDED_LINES, PROCESSED_ON_SENT)
      await viewOrder(page)
    })

    test('Then the viewer marks lines 15 and 16 as added by the chat', async ({ page }) => {
      await expect(lineOf(page, 15)).toHaveAttribute('title', /Added by the chat/)
      await expect(lineOf(page, 16)).toHaveAttribute('title', /Added by the chat/)
    })

    test('But marks no line before them as changed', async ({ page }) => {
      await expect(changedRows(page)).toHaveCount(2)
      await expect(files(page).locator('.removed-lines')).toHaveCount(0)
    })
  })

  test.describe('Mark nothing when the chat left the file as it was', () => {
    test.beforeEach(async ({ page }) => {
      seedOrderAs(ORDER_LINES, PROCESSED_ON_SENT)
      await viewOrder(page)
      await expect(marker(page, 12)).toHaveAccessibleName(`Comment on ${ANCHOR}, processed`)
    })

    test('Then the viewer marks no line of order.py as changed', async ({ page }) => {
      await expect(changedRows(page)).toHaveCount(0)
    })
  })

  test.describe('Stop marking the changes once the processed comment is cleared', () => {
    test.beforeEach(async ({ page }) => {
      seedOrderAs(CHANGED_LINES, PROCESSED_ON_SENT)
      await viewOrder(page)
      await expect(changedRows(page)).toHaveCount(1)
      await files(page).getByRole('button', { name: 'Clear processed comments' }).click()
    })

    test('Then the viewer marks no line of order.py as changed', async ({ page }) => {
      await expect(changedRows(page)).toHaveCount(0)
    })

    test(`And line 14 still reads ${CHANGED_14.trim()}`, async ({ page }) => {
      await expect(lineOf(page, 14).locator('.line-text')).toHaveText(CHANGED_14)
    })
  })
})
