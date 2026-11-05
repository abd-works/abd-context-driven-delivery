/**
 * Generate Fidelity Outputs at the browser tier: the scenarios, and the Thens of the Python tiers' scenarios, that
 * only the board app's page shows.
 *
 * Scenarios: move-work-forward-on-session-board/generate-fidelity-outputs/*\/*_story.test.py. The Python tiers replay
 * the rest from generate-fidelity-outputs.story.shared.py.
 *
 * Each scenario runs against the board app built and served on the throwaway fixture project
 * (harness/kanban/app/test-utils/fixture-repo.ts) with its real cdd server. A Given seeds the fixture project's
 * `.sessions/` or a fidelity's output file; a chat is `FakeChat`, which checks in through the board's server as the
 * cdd-board mod does. A tile is opened in the details, where a press opens its action bar.
 *
 * The scenarios name billing-report's story map `tests/story-map.md`, which the fixture holds. The story_map fidelity
 * declares its markdown at `.context/story-map.md` (cdd_guidance/practices/stories/stories.md), so the board does not
 * count tests/story-map.md as the story map; the Thens that need it counted fail until the two agree.
 */
import { rmSync } from 'node:fs'
import { join } from 'node:path'

import { card, expect, FakeChat, fixtureRoot, openBoard, receivedBy, resetSessions, seedActive, test, toast, turnOffActiveSessionOnly, waitForChat, waitForNoChat, writeInto } from './app/tests/story-ui'
import type { Locator, Page } from './app/tests/story-ui'

const CHAT_CHECKED_IN_MILLISECONDS = 10_000
// Where the story_map fidelity declares its markdown, under the session's workpath (the fixture's root).
const DECLARED_STORY_MAP = join(fixtureRoot, '.context', 'story-map.md')
const OTHER_PRACTICES_OFF = { ux: { enabled: false }, clean_engineering: { enabled: false }, bdd: { enabled: false } }

const details = (page: Page) => page.locator('.details-body')
const barOf = (page: Page, slug: string) => details(page).locator(`[data-tile="${slug}"] .expansion`)
const chip = (bar: Locator, label: string) => bar.getByRole('button', { name: new RegExp(`^${label}:`) })
const runOf = (bar: Locator) => bar.getByRole('button', { name: 'Run', exact: true })

async function selectBillingReport(page: Page): Promise<void> {
  await card(page, 'billing-report').getByRole('button', { name: 'Show Billing report' }).click({ position: { x: 4, y: 4 } })
  await expect(page.locator('.details-title h2')).toHaveText('Billing report')
}

async function openStoryMapTile(page: Page): Promise<Locator> {
  await selectBillingReport(page)
  await details(page).locator('[data-tile="stories-story_map"] .tile-name').click()
  await expect(barOf(page, 'stories-story_map')).toBeVisible()
  return barOf(page, 'stories-story_map')
}

test.beforeEach(() => resetSessions(fixtureRoot))
test.afterEach(() => rmSync(join(fixtureRoot, '.context'), { recursive: true, force: true }))
test.afterAll(() => resetSessions(fixtureRoot))

test.describe('with no chat connected', () => {
  test.describe('Choose Action And Formats', () => {
    test.describe("Pick the fidelity's default format", () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
      })

      test('Then the generate action is chosen with the markdown chip picked', async ({ page }) => {
        const bar = await openStoryMapTile(page)
        await expect(bar.getByRole('combobox', { name: 'Action' })).toHaveValue('generate')
        await expect(chip(bar, 'markdown')).toHaveAttribute('aria-pressed', 'true')
      })
    })

    test.describe('Leave a generated format unpicked', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
      })

      // Fails today: the fixture's tests/story-map.md is not where the story_map fidelity declares its markdown.
      test('Then the markdown chip is green and not picked', async ({ page }) => {
        const bar = await openStoryMapTile(page)
        await expect(chip(bar, 'markdown')).toHaveAttribute('aria-label', 'markdown: done')
        await expect(chip(bar, 'markdown')).toHaveAttribute('aria-pressed', 'false')
      })
    })

    test.describe('Stand one chip for a group of formats', () => {
      test.beforeEach(async ({ page }) => {
        writeInto(DECLARED_STORY_MAP, '# Check Out Order\n')
        // The stage head names story_map and bounded_context alone, so billing-report works on Stories and DDD alone.
        writeInto(join(fixtureRoot, '.sessions', 'billing-report', 'session.json'), JSON.stringify({ name: 'billing-report', title: 'Billing report', scope: 'feature', workpath: fixtureRoot, repo_path: fixtureRoot, practices: OTHER_PRACTICES_OFF }))
        await openBoard(page)
        await selectBillingReport(page)
        await details(page).getByRole('button', { name: 'Actions for Discovery' }).click()
      })

      test('Then the bar shows a diagram chip and a markdown chip', async ({ page }) => {
        const bar = details(page).locator('.expansion').first()
        await expect(bar.locator('.format-icon')).toHaveCount(2)
        await expect(chip(bar, 'diagram')).toBeVisible()
        await expect(chip(bar, 'markdown')).toBeVisible()
      })

      test('And the markdown chip reads 1 of 2 with the hint markdown: 1 of 2 done', async ({ page }) => {
        const markdown = chip(details(page).locator('.expansion').first(), 'markdown')
        await expect(markdown).toHaveText('1 of 2')
        await expect(markdown).toHaveAttribute('title', 'markdown: 1 of 2 done')
      })
    })

    test.describe('Keep Run off with no chat', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await waitForNoChat(page)
      })

      test('Then Run is off', async ({ page }) => {
        const bar = await openStoryMapTile(page)
        await expect(chip(bar, 'markdown')).toHaveAttribute('aria-pressed', 'true')
        await expect(runOf(bar)).toBeDisabled()
      })
    })
  })
})

test.describe('with a chat connected', () => {
  let chat: FakeChat

  test.beforeAll(async ({ playwright, baseURL }) => {
    chat = new FakeChat(await playwright.request.newContext({ baseURL }), 'generate-chat', 'Generate chat')
    await chat.start()
  })

  test.afterAll(() => chat.stop())

  async function openWithChat(page: Page): Promise<void> {
    await openBoard(page)
    await waitForChat(page, chat)
  }

  test.describe('Choose Action And Formats', () => {
    test.describe('Keep Run off with no format picked', () => {
      test.beforeEach(async ({ page }) => {
        writeInto(DECLARED_STORY_MAP, '# Check Out Order\n')
        await openWithChat(page)
      })

      test('Then Run is off', async ({ page }) => {
        const bar = await openStoryMapTile(page)
        await expect(bar.locator('[aria-pressed="true"]')).toHaveCount(0)
        await expect(runOf(bar)).toBeDisabled()
      })
    })

    test.describe('Keep Run off on a render with nothing to render', () => {
      test.beforeEach(async ({ page }) => {
        await openWithChat(page)
        // A bar's action is off on a ticket that is not the active session while Active session only is on.
        await turnOffActiveSessionOnly(page)
        await (await openStoryMapTile(page)).getByRole('combobox', { name: 'Action' }).selectOption('render')
      })

      test('Then Run is off', async ({ page }) => {
        await expect(runOf(barOf(page, 'stories-story_map'))).toBeDisabled()
      })
    })

    test.describe('Keep Run off on a locked ticket', () => {
      test.beforeEach(async ({ page }) => {
        await openWithChat(page)
        await expect(page.getByRole('switch', { name: 'Active session only' })).toBeChecked()
      })

      test('Then Run is off', async ({ page }) => {
        const bar = await openStoryMapTile(page)
        await expect(chip(bar, 'markdown')).toHaveAttribute('aria-pressed', 'true')
        await expect(runOf(bar)).toBeDisabled()
      })
    })
  })

  test.describe('Generate Fidelity Output', () => {
    test.describe('Send the generate command from a tile', () => {
      test.beforeEach(async ({ page }) => {
        seedActive('billing-report')
        await openWithChat(page)
        const bar = await openStoryMapTile(page)
        await expect(chip(bar, 'markdown')).toHaveAttribute('aria-pressed', 'true')
        await runOf(bar).click()
      })

      test("And the bar's picks are cleared", async ({ page }) => {
        await expect.poll(() => receivedBy(chat)).toContain('/actions-generate stories-story-map format=markdown session=.sessions/billing-report/session.json')
        await expect(barOf(page, 'stories-story_map').locator('[aria-pressed="true"]')).toHaveCount(0)
      })
    })
  })

  test.describe('Render Fidelity Format', () => {
    test.describe('Render existing output into another format', () => {
      test.beforeEach(async ({ page }) => {
        seedActive('billing-report')
        await openWithChat(page)
        const bar = await openStoryMapTile(page)
        await bar.getByRole('combobox', { name: 'Action' }).selectOption('render')
        await chip(bar, 'diagram').click()
        await runOf(bar).click({ timeout: 5_000 }).catch(() => undefined)
      })

      // Fails today: tests/story-map.md is not the story map's declared markdown, so there is nothing to render and Run stays off.
      test('Then the chat receives the command /actions-render stories-story-map format=drawio', async () => {
        await expect.poll(() => receivedBy(chat)).toContain('/actions-render stories-story-map format=drawio session=.sessions/billing-report/session.json')
      })
    })

    test.describe('Keep render off with nothing to render', () => {
      test.beforeEach(async ({ page }) => {
        await openWithChat(page)
        // A bar's action is off on a ticket that is not the active session while Active session only is on.
        await turnOffActiveSessionOnly(page)
        await (await openStoryMapTile(page)).getByRole('combobox', { name: 'Action' }).selectOption('render')
      })

      test('Then Run is off', async ({ page }) => {
        await expect(runOf(barOf(page, 'stories-story_map'))).toBeDisabled()
      })
    })
  })

  test.describe('Send Tile Action To Chat', () => {
    test.describe('Send sketch, iterate, or document as its own command', () => {
      async function runAction(page: Page, action: string): Promise<void> {
        const bar = barOf(page, 'stories-story_map')
        await bar.getByRole('combobox', { name: 'Action' }).selectOption(action)
        await runOf(bar).click()
      }

      test.beforeEach(async ({ page }) => {
        seedActive('billing-report')
        await openWithChat(page)
        await openStoryMapTile(page)
        await runAction(page, 'sketch')
      })

      // Each command also names the ticket's session.json, because a command runs in whichever chat it is sent to.
      test('Then the chat receives the command /actions-sketch stories-story-map', async () => {
        await expect.poll(() => receivedBy(chat)).toContain('/actions-sketch stories-story-map session=.sessions/billing-report/session.json')
      })

      test.describe('the Person runs iterate on story_map', () => {
        test.beforeEach(async ({ page }) => {
          await runAction(page, 'iterate')
        })

        test('Then the chat receives the command /actions-iterate stories-story-map', async () => {
          await expect.poll(() => receivedBy(chat)).toContain('/actions-iterate stories-story-map session=.sessions/billing-report/session.json')
        })

        test.describe('the Person runs document on story_map', () => {
          test.beforeEach(async ({ page }) => {
            await runAction(page, 'document')
          })

          test('Then the chat receives the command /actions-document stories-story-map', async () => {
            await expect.poll(() => receivedBy(chat)).toContain('/actions-document stories-story-map session=.sessions/billing-report/session.json')
          })
        })
      })
    })

    test.describe('Tell the person which chat got the command', () => {
      let other: FakeChat

      test.beforeAll(async ({ playwright, baseURL }) => {
        other = new FakeChat(await playwright.request.newContext({ baseURL }), 'generate-chat-2', 'Generate chat 2')
        await other.start()
      })

      test.afterAll(() => other.stop())

      test.beforeEach(async ({ page }) => {
        seedActive('billing-report')
        await openBoard(page)
        await expect(page.getByRole('option', { name: 'Generate chat 2' })).toBeAttached({ timeout: CHAT_CHECKED_IN_MILLISECONDS })
        const bar = await openStoryMapTile(page)
        await bar.getByRole('combobox', { name: 'Action' }).selectOption('sketch')
        await runOf(bar).click()
      })

      // Fails today: ChatClient.refresh chooses the first connected chat when the person has picked none, so sketch
      // is sent to Generate chat; chat-client.spec's 'should choose none among several' describes the page before that.
      test('Then nothing is sent', async ({ page }) => {
        await expect(page.getByRole('combobox', { name: 'Chat to send commands to' })).toHaveValue('')
        await expect(toast(page, /^Sent to/)).toHaveCount(0)
      })

      test.describe('the Person picks a chat and runs sketch again', () => {
        test.beforeEach(async ({ page }) => {
          await page.getByRole('combobox', { name: 'Chat to send commands to' }).selectOption(chat.id)
          await runOf(barOf(page, 'stories-story_map')).click()
        })

        // The toast names the chat and the whole command, the session it runs on included.
        test('Then a toast says Sent to the chat: /actions-sketch stories-story-map', async ({ page }) => {
          await expect(toast(page, 'Sent to Generate chat: /actions-sketch stories-story-map session=.sessions/billing-report/session.json')).toBeVisible()
        })
      })
    })
  })
})
