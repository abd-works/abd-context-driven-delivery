import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardOnProject, ticketOn, type Asked } from 'test-utils/board-page-support'

import { activationHeading } from './activation-client'

// checkout-flow is the active ticket; billing-report is the one a person switches to.
const ACTIVE = 'checkout-flow'
const CHOSEN = 'billing-report'

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
  board.addOrigin()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

// The active ticket works on a branch of its own, pushed to an origin, so leaving it can commit, push, and merge.
async function switchingPage() {
  board.checkOutBranch(ACTIVE)
  const { page, asked } = await board.page()
  return { page, asked, active: ticketOn(page, ACTIVE), chosen: ticketOn(page, CHOSEN) }
}

const activatePosts = (asked: Asked[]) => asked.filter(request => request.path === `/api/ticket/${CHOSEN}/activate`)

describe('Activate Ticket', () => {
  it('should offer commit and push on leaving and open with merge off', async () => {
    const { page, chosen } = await switchingPage()
    await page.activation.start(chosen, false)
    expect(page.store.state.activation?.leaving).toEqual(['commit', 'push'])
  })

  it('should offer a branch to a ticket that has none', async () => {
    const { page, chosen } = await switchingPage()
    await page.activation.start(chosen, false)
    expect(page.store.state.activation?.opening).toEqual(['branch'])
  })

  it('should choose nothing to leave when the session has no branch', async () => {
    const { page } = await board.page()
    await page.activation.start(ticketOn(page, CHOSEN), false)
    expect(page.store.state.activation?.leaving).toEqual([])
  })

  it('should say what it switches from and to', async () => {
    const { page, chosen } = await switchingPage()
    await page.activation.start(chosen, false)
    expect(activationHeading(page.store.state.activation!)).toBe('Switch from Checkout flow to Billing report')
  })

  describe('that a person has confirmed with merge chosen', () => {
    async function confirmed() {
      const { page, asked, chosen } = await switchingPage()
      await page.activation.start(chosen, false)
      page.activation.toggleLeaving('merge')
      await page.activation.confirm()
      return { page, asked }
    }

    it('should send what was chosen', async () => {
      const { asked } = await confirmed()
      expect(activatePosts(asked)[0]?.body).toEqual({ leaving: ['commit', 'push', 'merge'], opening: ['branch'] })
    })

    it('should report it', async () => {
      const { page } = await confirmed()
      expect(page.store.state.toasts.at(-1)?.text).toBe('Checkout flow: committed, pushed, merged to main · Billing report: branch created · Billing report is now active')
    })
  })

  describe('that a person has cancelled', () => {
    async function cancelled() {
      const { page, asked, chosen } = await switchingPage()
      await page.activation.start(chosen, false)
      page.activation.cancel()
      return { page, asked }
    }

    it('should close the dialog', async () => {
      const { page } = await cancelled()
      expect(page.store.state.activation).toBeNull()
    })

    it('should send nothing', async () => {
      const { asked } = await cancelled()
      expect(activatePosts(asked)).toEqual([])
    })
  })
})

describe('Close Active Session', () => {
  async function closing() {
    const { page, asked, active } = await switchingPage()
    await page.activation.start(active, true)
    return { page, asked }
  }

  it('should ask what to do with its work', async () => {
    const { page } = await closing()
    expect(activationHeading(page.store.state.activation!)).toBe('Close session Checkout flow')
  })

  it('should send what to do with its work', async () => {
    const { page, asked } = await closing()
    await page.activation.confirm()
    expect(asked.find(request => request.path === `/api/ticket/${ACTIVE}/close`)?.body).toEqual({ leaving: ['commit', 'push'] })
  })

  it('should select the ticket in Complete', async () => {
    const { page } = await closing()
    await page.activation.confirm()
    expect(page.store.state.selected).toBe('Complete/checkout-flow')
  })
})
