/**
 * Validate Fidelity Outputs at the browser tier: the scenarios that only the board app's page shows.
 *
 * Scenarios: story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md. The Python tiers replay
 * the rest from validate-fidelity-outputs.story.shared.py.
 *
 * Each scenario runs against the board app built and served on the throwaway fixture project
 * (space/kanban/app/test-utils/fixture-repo.ts) with its real cdd server. A Given seeds the fixture project's
 * `.sessions/`, where Validate saves its reports and writes its validate lines; a chat is `FakeChat`, which checks in
 * through the board's server as the cdd-board mod does.
 */
import { readFileSync } from 'node:fs'
import { join } from 'node:path'

import { card, expect, FakeChat, fixtureRoot, generatedLine, openBoard, receivedBy, resetSessions, seedActive, step, test, validatedLine, waitForChat, writeInto, writeSession } from '../../../../space/kanban/app/tests/story-ui'
import type { Locator, Page } from '../../../../space/kanban/app/tests/story-ui'

const REPORTS = join(fixtureRoot, '.sessions', 'checkout-flow', 'validation-reports')
// The fixture's own report of checkout-flow's story map, with verb-noun-format on .context/story-map.md line 6.
const STORY_MAP_REPORT = 'stories-story-map-20261101T100000'
// A report Validate saves later, with the judgment the validating agent adds: a second rule broken on line 7.
const JUDGED_REPORT = '# Graph rule validation\n\n## Judgment — `.context/story-map.md`\n\n### `do-not-invent-requirements` — Fail\n- story-map.md:7 `Confirm Order`: no source names this story.\n'
const CLEAN_REPORT = 'stories-story-map-20261101T120000'
const CLEAN_STAMP = '2026-11-01T12:00:00Z'
// A graph validate saved with no hits, in the shape harness/graph/saved_graph.py writes (SAVED_SHAPE_VERSION 5).
const CLEAN_GRAPH = {
  version: 5,
  overlays: [],
  practices: { stories: { source_root: '', root_facts: {}, nodes: [{ node_id: 'node-1', name: '', type: 'Story', practice: 'stories', file: '.context/story-map.md', line: 6, end_line: 6, stage: '', facts: {} }], edges: [], violations: [] } },
}

// What the project keeps of the violations a person accepted (space/session/accepted_violations.py).
const ACCEPTED_FILE = join(fixtureRoot, '.context', 'violations-accepted.json')
const acceptedInProject = (): { rule: string; node_id: string; message: string }[] => JSON.parse(readFileSync(ACCEPTED_FILE, 'utf8')).accepted
// A later validate of the story map that finds the same rule on the same node, saying something else.
const REWORDED_REPORT = 'stories-story-map-20261101T120000'
const REWORDED_STAMP = '2026-11-01T12:00:00Z'
const REWORDED_GRAPH = {
  version: 5,
  overlays: [],
  practices: {
    stories: {
      source_root: '',
      root_facts: {},
      nodes: [{ node_id: 'node-1', name: '', type: 'Story', practice: 'stories', file: '.context/story-map.md', line: 6, end_line: 6, stage: '', facts: {} }],
      edges: [],
      violations: [{ rule: 'verb-noun-format', message: 'Name the story with a verb and a noun', practice: 'stories', node_id: 'node-1', location: '.context/story-map.md', line: 6, end_line: 6 }],
    },
  },
}

const report = (page: Page) => page.locator('[data-panel="report"]')
const storyMapTile = (page: Page) => page.locator('.details-body [data-tile="stories-story-map"]')

async function acceptStoryMapViolation(page: Page): Promise<Locator> {
  const opened = await openStoryMapReport(page)
  await opened.getByRole('button', { name: 'Accept .context/story-map.md:6' }).click()
  await expect(opened.getByText('1 accepted violation left out')).toBeVisible()
  return opened
}

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

      test("Then the chat's prompt is filled with one message, for the person to edit and send, naming the verb-noun-format rule, the error at .context/story-map.md:6, and the content that failed, with instructions to fix it", async () => {
        await expect.poll(() => sentSince(before).length).toBe(1)
        const [message] = sentSince(before)
        for (const part of ['verb-noun-format', '.context/story-map.md:6', 'Handle Payment']) expect(message).toContain(part)
      })
    })

    test.describe('Fix every violation of a rule', () => {
      let before = 0

      test.beforeEach(async ({ page }) => {
        await openWithChat(page)
        before = chat.received.length
        await (await openStoryMapReport(page)).locator('.rule-head').getByRole('button', { name: 'Fix all', exact: true }).click()
      })

      test("Then the chat's prompt is filled with one message, for the person to edit and send: Fix all violations of verb-noun-format found in this report, naming checkout-flow's story_map report", async () => {
        await expect.poll(() => sentSince(before).length).toBe(1)
        const [message] = sentSince(before)
        expect(message).toContain(`Fix all violations of verb-noun-format found in this report: .sessions/checkout-flow/validation-reports/${STORY_MAP_REPORT}.md`)
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

      test("Then the chat's prompt is filled with one message, for the person to edit and send: Fix all violations found in this report, naming checkout-flow's report", async () => {
        await expect.poll(() => sentSince(before).length).toBe(1)
        const [message] = sentSince(before)
        expect(message).toContain(`Fix all violations found in this report: .sessions/checkout-flow/validation-reports/${STORY_MAP_REPORT}.md`)
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
      // Opening a ticket shows its own chat at the top, and none while it has none, so the chat is picked with
      // billing-report open, which makes it billing-report's chat.
      test.beforeEach(async ({ page }) => {
        seedActive('billing-report')
        await openBoard(page)
        const bar = await openBillingStoryMap(page)
        await waitForChat(page, chat)
        await bar.getByRole('button', { name: 'validate', exact: true }).click()
      })

      // The command names the ticket's session.json.
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

// Accepting needs no chat: the board's Python keeps the acceptance, and the page draws the report it answers.
test.describe('Accept Report Violation', () => {
  test('Accept a violation as it is', async ({ page }) => {
    let opened: Locator
    await step(page, "Given checkout-flow's story_map report lists verb-noun-format at .context/story-map.md line 6, on the story node-1, saying Name the story with a verb", async () => {
      await openBoard(page)
      opened = await openStoryMapReport(page)
      await expect(opened.locator('.violation-actions').getByRole('button')).toHaveText(['Fix', 'False', 'Accept'])
    })
    await step(page, 'When the Person accepts that violation', async () => {
      await opened.getByRole('button', { name: 'Accept .context/story-map.md:6' }).click()
    })
    await step(page, 'Then .context/violations-accepted.json keeps verb-noun-format on node-1 with the message Name the story with a verb', async () => {
      await expect.poll(() => acceptedInProject().map(entry => [entry.rule, entry.node_id, entry.message])).toEqual([['verb-noun-format', 'node-1', 'Name the story with a verb']])
    })
    await step(page, 'And the story_map report lists no rules and says it leaves out 1 accepted violation', async () => {
      await expect(opened.getByText('No open violations. The fidelity is done.')).toBeVisible()
      await expect(opened.locator('.report-rule')).toHaveCount(0)
      await expect(opened.getByText('1 accepted violation left out')).toBeVisible()
    })
    await step(page, 'And the story_map tile marks Validate ✓ with no violations', async () => {
      await expect(storyMapTile(page).getByRole('button', { name: 'violations' })).toHaveCount(0)
      await expect(page.getByRole('status', { name: "Active ticket's violations" })).toHaveCount(0)
    })
  })

  test('Show an accepted violation again once its finding changes', async ({ page }) => {
    let opened: Locator
    await step(page, 'Given the Person accepted verb-noun-format on node-1 saying Name the story with a verb', async () => {
      await openBoard(page)
      opened = await acceptStoryMapViolation(page)
    })
    await step(page, 'When Claude Code validates the story map again and finds verb-noun-format on node-1 saying Name the story with a verb and a noun', () => {
      writeInto(join(REPORTS, `${REWORDED_REPORT}.md`), '# Graph rule validation\n')
      writeInto(join(REPORTS, `${REWORDED_REPORT}.json`), JSON.stringify(REWORDED_GRAPH))
      writeSession(fixtureRoot, { name: 'checkout-flow', title: 'Checkout flow', log: [generatedLine('stories', 'story_map'), `${REWORDED_STAMP} validate Stories story_map graph-rule verb-noun-format .context/story-map.md:6 no-chat`] })
    })
    await step(page, 'Then the story_map report lists verb-noun-format with one violation again', async () => {
      await expect(opened.getByText('Name the story with a verb and a noun')).toBeVisible({ timeout: 10_000 })
      await expect(opened.getByText('accepted violation left out')).toHaveCount(0)
    })
    await step(page, 'And the story_map tile marks Validate as violations', async () => {
      await expect(storyMapTile(page).getByRole('button', { name: 'violations' })).toBeVisible()
    })
  })

  test('Take an acceptance back', async ({ page }) => {
    let opened: Locator
    await step(page, 'Given the Person accepted verb-noun-format on node-1 saying Name the story with a verb', async () => {
      await openBoard(page)
      opened = await acceptStoryMapViolation(page)
    })
    await step(page, 'And the story_map report lists that violation among the accepted ones', async () => {
      await opened.getByText('1 accepted violation left out').click()
      await expect(opened.locator('.accepted-violation')).toContainText('Name the story with a verb')
    })
    await step(page, 'When the Person takes that acceptance back', async () => {
      await opened.getByRole('button', { name: 'Take back verb-noun-format .context/story-map.md:6' }).click()
    })
    await step(page, 'Then the story_map report lists verb-noun-format with one violation again', async () => {
      await expect(opened.getByRole('button', { name: 'Accept .context/story-map.md:6' })).toBeVisible()
      await expect(opened.getByText('accepted violation left out')).toHaveCount(0)
    })
    await step(page, 'And .context/violations-accepted.json keeps no acceptance', async () => {
      await expect.poll(() => acceptedInProject()).toEqual([])
    })
  })
})
