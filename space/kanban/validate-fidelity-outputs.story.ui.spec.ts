/**
 * Validate Fidelity Outputs at the browser tier: the scenarios that only the board app's page shows.
 *
 * Scenarios: harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md. The Python tiers replay
 * the rest from validate-fidelity-outputs.story.shared.py.
 *
 * Each scenario runs against the board app built and served on the throwaway fixture project
 * (space/kanban/app/test-utils/fixture-repo.ts) with its real cdd server. A Given seeds the fixture project's
 * `.sessions/`, where Validate saves its reports and writes its validate lines; a chat is `FakeChat`, which checks in
 * through the board's server as the cdd-board mod does.
 */
import { join } from 'node:path'

import { card, expect, FakeChat, fixtureRoot, generatedLine, openBoard, receivedBy, resetSessions, seedActive, test, validatedLine, waitForChat, writeInto, writeSession } from './app/tests/story-ui'
import type { Locator, Page } from './app/tests/story-ui'

const REPORTS = join(fixtureRoot, '.sessions', 'checkout-flow', 'validation-reports')
// The fixture's own report of checkout-flow's story map, with verb-noun-format on .context/story-map.md line 6.
const STORY_MAP_REPORT = 'stories-story-map-20261101T100000'
// A report Validate saves later, with the judgment the validating agent adds: a second rule broken on line 7.
const JUDGED_REPORT = '# Graph rule validation\n\n## Judgment — `.context/story-map.md`\n\n### `do-not-invent-requirements` — Fail\n- story-map.md:7 `Confirm Order`: no source names this story.\n'
const CLEAN_REPORT = 'stories-story-map-20261101T120000'
const CLEAN_STAMP = '2026-11-01T12:00:00Z'
// A graph validate saved with no hits, in the shape harness/graph/saved_graph.py writes (version 2).
const CLEAN_GRAPH = {
  version: 2,
  overlays: [],
  practices: { stories: { source_root: '', root_facts: {}, nodes: [{ node_id: 'node-1', name: '', type: 'Story', practice: 'stories', file: '.context/story-map.md', line: 6, end_line: 6, stage: '', facts: {} }], edges: [], violations: [] } },
}

const report = (page: Page) => page.locator('[data-panel="report"]')

async function openStoryMapReport(page: Page): Promise<Locator> {
  await page.locator('.details-body [data-tile="stories-story-map"]').getByRole('button', { name: 'violations' }).click()
  await expect(report(page).getByRole('button', { name: /verb-noun-format/ })).toBeVisible()
  return report(page)
}

test.beforeEach(() => resetSessions(fixtureRoot))
test.afterAll(() => resetSessions(fixtureRoot))

test.describe('with no chat connected', () => {
  test.describe('Display Violations Band', () => {
    test.describe("Show the active ticket's violations in a band", () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
      })

      test("Then a band across the page top names checkout-flow's violations", async ({ page }) => {
        await expect(page.getByRole('status', { name: "Active ticket's violations" })).toHaveText('checkout-flow · Discovery · violations: stories-story-map')
      })
    })

    test.describe('Show no band when the active ticket is clean', () => {
      test.beforeEach(async ({ page }) => {
        seedActive('billing-report')
        await openBoard(page)
      })

      test('Then no violations band shows', async ({ page }) => {
        await expect(page.locator('.header-active')).toHaveText('Billing report')
        await expect(page.getByRole('status', { name: "Active ticket's violations" })).toHaveCount(0)
      })
    })
  })

  test.describe('Open Validation Report', () => {
    test.describe("Open a violation's file at its line", () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await (await openStoryMapReport(page)).getByRole('button', { name: '.context/story-map.md:6', exact: true }).click()
      })

      test('Then the files panel shows .context/story-map.md with line 6 marked', async ({ page }) => {
        const files = page.locator('[data-panel="files"]')
        await expect(files.getByRole('tab', { name: 'story-map.md' })).toBeVisible()
        await expect(files.locator('.code-line.is-failing .line-number')).toHaveText('6')
      })
    })
  })

  test.describe('Fix Report Violations', () => {
    test.describe('Read an open report again after the fix', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await openStoryMapReport(page)
        // What Validate writes when it finds no violations: a clean report with its graph, and a clean validate line.
        writeInto(join(REPORTS, `${CLEAN_REPORT}.md`), '# Graph rule validation\n')
        writeInto(join(REPORTS, `${CLEAN_REPORT}.json`), JSON.stringify(CLEAN_GRAPH))
        writeSession(fixtureRoot, { name: 'checkout-flow', title: 'Checkout flow', log: [generatedLine('stories', 'story_map'), validatedLine('Stories', 'story_map', CLEAN_STAMP)] })
      })

      test('Then the open report lists no rules', async ({ page }) => {
        await expect(report(page).getByText('No open violations. The fidelity is done.')).toBeVisible({ timeout: 8_000 })
      })
    })
  })
})

test.describe('with a chat connected', () => {
  let chat: FakeChat

  test.beforeAll(async ({ playwright, baseURL }) => {
    chat = new FakeChat(await playwright.request.newContext({ baseURL }), 'validate-chat', 'Validate chat')
    await chat.start()
  })

  test.afterAll(() => chat.stop())

  async function openWithChat(page: Page): Promise<void> {
    await openBoard(page)
    await waitForChat(page, chat)
  }

  const sentSince = (before: number) => chat.received.slice(before).map(command => command.text)

  test.describe('Fix Report Violations', () => {
    test.describe('Fix one violation at its line', () => {
      let before = 0

      test.beforeEach(async ({ page }) => {
        await openWithChat(page)
        before = chat.received.length
        await (await openStoryMapReport(page)).getByRole('button', { name: 'Fix .context/story-map.md:6' }).click()
      })

      test('Then the chat receives one message naming the verb-noun-format rule, the error at .context/story-map.md:6, and the content that failed, with instructions to fix it', async () => {
        await expect.poll(() => sentSince(before).length).toBe(1)
        const [message] = sentSince(before)
        expect(['verb-noun-format', '.context/story-map.md:6', 'Handle Payment'].every(part => message!.includes(part))).toBe(true)
      })
    })

    test.describe('Fix every violation of a rule', () => {
      let before = 0

      test.beforeEach(async ({ page }) => {
        await openWithChat(page)
        before = chat.received.length
        await (await openStoryMapReport(page)).locator('.rule-head').getByRole('button', { name: 'Fix all', exact: true }).click()
      })

      test('Then the chat receives one message with every verb-noun-format violation, each at its file and line with the content that failed, and instructions to fix them', async () => {
        await expect.poll(() => sentSince(before).length).toBe(1)
        const [message] = sentSince(before)
        expect(['verb-noun-format', '.context/story-map.md:6', 'Handle Payment'].every(part => message!.includes(part))).toBe(true)
      })
    })

    test.describe('Fix every violation in the report', () => {
      let before = 0

      test.beforeEach(async ({ page }) => {
        writeInto(join(REPORTS, `${STORY_MAP_REPORT}.md`), JUDGED_REPORT)
        await openWithChat(page)
        before = chat.received.length
        const opened = await openStoryMapReport(page)
        await expect(opened.getByRole('button', { name: /do-not-invent-requirements/ })).toBeVisible()
        await opened.getByRole('button', { name: 'Fix all violations' }).click()
      })

      test('Then the chat receives one message naming each rule with every violation of it, each at its file and line with the content that failed, and instructions to fix them all', async () => {
        await expect.poll(() => sentSince(before).length).toBe(1)
        const [message] = sentSince(before)
        expect(['verb-noun-format', '.context/story-map.md:6', 'Handle Payment', 'do-not-invent-requirements', '.context/story-map.md:7', 'Confirm Order'].every(part => message!.includes(part))).toBe(true)
      })
    })
  })

  test.describe('Validate Fidelity', () => {
    async function openBillingStoryMap(page: Page): Promise<Locator> {
      await card(page, 'billing-report').getByRole('button', { name: 'Show Billing report' }).click({ position: { x: 4, y: 4 } })
      await page.locator('.details-body [data-tile="stories-story-map"] .tile-name').click()
      const bar = page.locator('.details-body [data-tile="stories-story-map"] .expansion')
      await expect(bar).toBeVisible()
      return bar
    }

    test.describe('Send the fidelity to validate', () => {
      test.beforeEach(async ({ page }) => {
        seedActive('billing-report')
        await openWithChat(page)
        await (await openBillingStoryMap(page)).getByRole('button', { name: 'validate', exact: true }).click({ timeout: 5_000 }).catch(() => undefined)
      })

      // Fails today: the fixture's .context/story-map.md is not where the story_map fidelity declares its markdown
      // (.context/story-map.md), so with nothing recorded the bar has nothing to validate and keeps validate off.
      // The command also names the ticket's session.json.
      test('Then the chat receives the command /actions-validate stories-story-map', async () => {
        await expect.poll(() => receivedBy(chat)).toContain('/actions-validate stories-story-map session=.sessions/billing-report/session.json')
      })
    })

    test.describe('Keep Validate off with nothing to check', () => {
      test.beforeEach(async ({ page }) => {
        await openWithChat(page)
      })

      test('Then validate is off', async ({ page }) => {
        await expect((await openBillingStoryMap(page)).getByRole('button', { name: 'validate', exact: true })).toBeDisabled()
      })
    })
  })
})
