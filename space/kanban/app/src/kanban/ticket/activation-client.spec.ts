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
  it('should offer a handoff, commit and push on leaving and open with merge off', async () => {
    const { page, chosen } = await switchingPage()
    await page.activation.start(chosen, false)
    expect(page.store.state.activation?.leaving).toEqual(['handoff', 'commit', 'push'])
  })

  // Python chooses each open choice at first; the dialog offers those the ticket does not have yet.
  it('should offer a branch and a worktree to a ticket that has neither', async () => {
    const { page, chosen } = await switchingPage()
    await page.activation.start(chosen, false)
    expect(page.store.state.activation?.opening).toEqual(['branch', 'worktree'])
  })

  // The fixture project is checked out on main, so the active session's work is on main, which leaving commits and pushes.
  it('should offer a handoff, commit and push of main when the session has no branch of its own', async () => {
    const { page } = await board.page()
    await page.activation.start(ticketOn(page, CHOSEN), false)
    expect([page.store.state.activation?.leavingBranch, page.store.state.activation?.leaving]).toEqual(['main', ['handoff', 'commit', 'push']])
  })

  // Leaving never merges the default branch, so the dialog offers no merge there.
  it('should offer no merge when the session being left works on main', async () => {
    const { page } = await board.page()
    await page.activation.start(ticketOn(page, CHOSEN), false)
    expect(page.store.state.activation?.offeredLeaving).toEqual(['handoff', 'commit', 'push'])
  })

  it('should offer a merge and a delete of the branch when the session being left works on its own branch', async () => {
    const { page, chosen } = await switchingPage()
    await page.activation.start(chosen, false)
    expect(page.store.state.activation?.offeredLeaving).toEqual(['handoff', 'commit', 'push', 'merge', 'delete_branch'])
  })

  it('should leave only the handoff chosen once a person unchooses commit and push', async () => {
    const { page, chosen } = await switchingPage()
    await page.activation.start(chosen, false)
    page.activation.toggleLeaving('commit')
    page.activation.toggleLeaving('push')
    expect(page.store.state.activation?.leaving).toEqual(['handoff'])
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
      expect(activatePosts(asked)[0]?.body).toEqual({ leaving: ['handoff', 'commit', 'push', 'merge'], opening: ['branch', 'worktree'] })
    })

    it('should report it', async () => {
      const { page } = await confirmed()
      expect(page.store.state.toasts.at(-1)?.text).toBe('Checkout flow: handoff written, committed, pushed, merged to main · Billing report: branch created, worktree created · Billing report is now active')
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
    expect(asked.find(request => request.path === `/api/ticket/${ACTIVE}/close`)?.body).toEqual({ leaving: ['handoff', 'commit', 'push'] })
  })

  it('should select the ticket in Complete', async () => {
    const { page } = await closing()
    await page.activation.confirm()
    expect(page.store.state.selected).toBe('Complete/checkout-flow')
  })
})
