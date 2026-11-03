import { expect, test } from '@playwright/test'

import { ACCENT, card, openBoard, openCard, openCardOf, openTileBarOf } from './support'

// The signatures carried over from kanban_surface_heavy_spec.py: the surface measured where it landed. These press only
// what changes the view, and this file sorts first, before any spec connects a chat.
const SAME_LINE_PIXELS = 20
const PAGE_FOOTER_PIXELS = 160
// The canvas's stage is 24fr of 1488px with 10px gaps, and a stage's card is half of what the stage leaves inside.
const CANVAS_STAGE_PIXELS = 347
const CANVAS_CARD_PIXELS = 157
const CANVAS_HEADER_PIXELS = 58

test.describe('the session board on the page', () => {
  test.beforeEach(async ({ page }) => {
    await openBoard(page)
  })

  test.describe('with the board drawn', () => {
    test("should fill the pane's height", async ({ page }) => {
      const lowest = await page.locator('.details-region').boundingBox()
      const root = await page.locator('.board-root').boundingBox()
      expect(root!.height).toBe(900)
      expect(lowest!.y + lowest!.height).toBeGreaterThanOrEqual(900 - PAGE_FOOTER_PIXELS)
    })

    test("should keep a card's controls inside the card", async ({ page }) => {
      const overflowing = await page.locator('.ticket-card').evaluateAll(cards =>
        cards.flatMap(shown => {
          const right = shown.getBoundingClientRect().right
          return [...shown.querySelectorAll('button:not(.card-hit)')].filter(control => control.getBoundingClientRect().right > right).map(control => control.getAttribute('aria-label'))
        }),
      )
      expect(overflowing).toEqual([])
    })

    test("should keep a card's move buttons on one line", async ({ page }) => {
      const wrapped = await page.locator('.card-moves').evaluateAll((lines, tolerance) => lines.filter(line => [...line.children].some(move => Math.abs(move.getBoundingClientRect().top - line.children[0]!.getBoundingClientRect().top) > tolerance)).length, SAME_LINE_PIXELS)
      expect(wrapped).toBe(0)
    })

    test('should keep the sideways scrollbar on screen', async ({ page }) => {
      await page.setViewportSize({ width: 1000, height: 800 })
      const region = page.locator('.board-region')
      const box = await region.boundingBox()
      expect(box!.y + box!.height).toBeLessThanOrEqual(800)
      const hasOverflow = await region.evaluate(element => element.scrollWidth > element.clientWidth)
      expect(hasOverflow).toBe(true)
      await region.evaluate(element => element.scrollTo({ left: 300 }))
      expect(await region.evaluate(element => element.scrollLeft)).toBe(300)
    })

    test('should draw a card at the canvas width', async ({ page }) => {
      const stage = await page.locator('.board-column[data-column="Discovery"]').boundingBox()
      const shown = await card(page, 'checkout-flow').boundingBox()
      expect(stage!.width).toBeGreaterThanOrEqual(CANVAS_STAGE_PIXELS)
      expect(shown!.width).toBeGreaterThanOrEqual(CANVAS_CARD_PIXELS)
    })
  })

  test.describe('with a card opened', () => {
    test.beforeEach(async ({ page }) => {
      await openCardOf(page, 'checkout-flow')
    })

    test('should show its tiles with no action bar until a tile is pressed', async ({ page }) => {
      await expect(page.locator('.card-open .expansion')).toHaveCount(0)
    })

    test.describe('with a tile pressed on it', () => {
      test('should offer the action list and Run in that tile', async ({ page }) => {
        const bar = await openTileBarOf(openCard(page, 'checkout-flow'))
        await expect(bar.getByRole('combobox', { name: 'Action' })).toBeVisible()
      })
    })

    test('should show the whole opened card', async ({ page }) => {
      const opened = await page.locator('.card-open').boundingBox()
      const region = await page.locator('.board-region').boundingBox()
      expect(opened!.y).toBeGreaterThanOrEqual(region!.y)
      expect(opened!.y + opened!.height).toBeLessThanOrEqual(region!.y + region!.height)
      await expect(page.locator('.card-open .card-files').getByRole('button', { name: 'Close' })).toBeVisible()
    })
  })

  test.describe('with the files list pressed on a card', () => {
    test('should open the files list beside the board', async ({ page }) => {
      await card(page, 'checkout-flow').getByRole('button', { name: 'list' }).first().click()
      const panel = page.locator('[data-panel="files"]')
      await expect(panel.getByRole('button', { name: 'tests/story-map.md' })).toBeVisible()
      const board = await page.locator('.board-main').boundingBox()
      const beside = await panel.boundingBox()
      expect(beside!.x).toBeGreaterThanOrEqual(board!.x + board!.width - 1)
    })

    test('should keep the header on one line', async ({ page }) => {
      await card(page, 'checkout-flow').getByRole('button', { name: 'list' }).first().click()
      await expect(page.locator('[data-panel="files"]')).toBeVisible()
      const header = await page.locator('.board-header').boundingBox()
      expect(header!.height).toBeLessThanOrEqual(CANVAS_HEADER_PIXELS)
    })
  })

  test.describe('with the activation dialog open', () => {
    // The dialog's own Activate acts on the session, so it is only read here.
    test('should draw the primary action in the accent colour', async ({ page }) => {
      await card(page, 'billing-report').getByRole('button', { name: 'Activate' }).first().click()
      const confirm = page.getByRole('dialog').getByRole('button', { name: 'Activate' })
      await expect(confirm).toHaveCSS('background-color', ACCENT)
      await page.getByRole('dialog').getByRole('button', { name: 'Cancel' }).click()
      await expect(page.getByRole('dialog')).toHaveCount(0)
    })
  })

  test.describe('with no chat connected', () => {
    test('should say to load the mod and turn off what sends to a chat', async ({ page }) => {
      await expect(page.getByText('No chat connected: load the cdd-board mod in a chat to send commands')).toBeVisible()
      await expect(page.getByRole('button', { name: '+ Ticket' })).toBeDisabled()
      await expect(page.getByRole('button', { name: 'Satisfy' })).toBeDisabled()
      await expect(card(page, 'checkout-flow').getByRole('button', { name: 'Handoff' }).first()).toBeDisabled()
    })

    test('should keep local actions working', async ({ page }) => {
      await page.getByRole('button', { name: 'Refresh' }).click()
      await expect(page.getByRole('button', { name: 'Refresh' })).toBeEnabled()
      await card(page, 'checkout-flow').getByRole('button', { name: 'Run next: fix violations' }).first().click()
      await expect(page.locator('[data-panel="report"]')).toBeVisible()
    })
  })

  test.describe('at phone width', () => {
    test.use({ viewport: { width: 375, height: 812 } })

    test('should scroll the page sideways nowhere but in the board and details scrollers', async ({ page }) => {
      const width = await page.evaluate(() => document.documentElement.scrollWidth)
      expect(width).toBeLessThanOrEqual(375)
      const hasOverflow = await page.locator('.board-region').evaluate(element => element.scrollWidth > element.clientWidth)
      expect(hasOverflow).toBe(true)
    })

    test('should give an open panel the whole page, with no sideways scroll', async ({ page }) => {
      await card(page, 'checkout-flow').getByRole('button', { name: 'Run next: fix violations' }).first().click()
      const panel = await page.locator('[data-panel="report"]').boundingBox()
      expect(panel!.x).toBe(0)
      expect(panel!.width).toBe(375)
      expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375)
    })

    test('should keep the dialog inside the page', async ({ page }) => {
      await card(page, 'billing-report').getByRole('button', { name: 'Activate' }).first().click()
      const dialog = await page.getByRole('dialog').boundingBox()
      expect(dialog!.x).toBeGreaterThanOrEqual(0)
      expect(dialog!.x + dialog!.width).toBeLessThanOrEqual(375)
    })
  })
})
