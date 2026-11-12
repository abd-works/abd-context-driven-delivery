import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardOnProject, ticketOn, type Asked } from 'test-utils/board-page-support'

import { closingHeading } from './activation-client'

// checkout-flow is the active ticket; billing-report is the one a person activates.
const ACTIVE = 'checkout-flow'
const CHOSEN = 'billing-report'

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
  board.addOrigin()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

const activatePosts = (asked: Asked[]) => asked.filter(request => request.path === `/api/ticket/${CHOSEN}/activate`)

// One press opens the ticket in its own worktree: there is nothing to ask first, because no chat moves between folders.
describe('Activate Ticket', () => {
  describe('Open a ticket in its own worktree', () => {
    async function activated() {
      const { page, asked } = await board.page()
      const opened: string[] = []
      page.openLink = link => opened.push(link)
      await page.activation.activate(ticketOn(page, CHOSEN))
      return { page, asked, opened }
    }

    it('should send the ticket alone, with no choices', async () => {
      const { asked } = await activated()
      expect(activatePosts(asked).map(request => request.body)).toEqual([{}])
    })

    it('should open no dialog', async () => {
      const { page } = await activated()
      expect(page.store.state.closing).toBeNull()
    })

    it('should select the ticket', async () => {
      const { page } = await activated()
      expect(page.store.state.selected).toBe(ticketOn(page, CHOSEN).address)
    })

    // With no chat working in its worktree yet, Activate starts one there, so the person is left with the ticket's chat.
    it('should start a new chat on its worktree', async () => {
      const { page, opened } = await activated()
      expect(opened.map(link => new URL(link).searchParams.get('folder'))).toEqual([ticketOn(page, CHOSEN).worktree])
    })

    it("should show the ticket's chat as opening", async () => {
      const { page } = await activated()
      expect(page.chat.isOpeningFor(CHOSEN)).toBe(true)
    })

    it('should ask the person to confirm the new chat in the Claude app', async () => {
      const { page } = await activated()
      expect(page.store.state.toasts.at(-1)?.text).toBe(`Confirm the folder and send in the Claude app to start the chat of ${CHOSEN}`)
    })
  })

  describe('Work on the ticket from a chat in its worktree', () => {
    async function activated() {
      const { page } = await board.page()
      await board.connectChat(page, 'other-chat')
      const worktree = board.openWorktree(CHOSEN)
      await board.chat('ticket-chat', 'abd · first words', worktree).checkIn()
      await page.chat.refresh()
      await page.reader.refresh()
      await page.activation.activate(ticketOn(page, CHOSEN))
      return page
    }

    it("should send the board's commands to that chat", async () => {
      expect((await activated()).store.state.targetChat).toBe('ticket-chat')
    })

    it('should say its chat is chosen', async () => {
      expect((await activated()).store.state.toasts.at(-1)?.text).toMatch(/^Billing report is open in its worktree .* · its chat is chosen$/)
    })
  })
})

// The active ticket works on a branch of its own in its own worktree, so closing it can commit and push that branch.
describe('Close Active Session', () => {
  async function closing() {
    board.openWorktree(ACTIVE)
    const { page, asked } = await board.page()
    await page.activation.startClosing(ticketOn(page, ACTIVE))
    return { page, asked }
  }

  it('should ask what to do with its work', async () => {
    const { page } = await closing()
    expect(closingHeading(page.store.state.closing!)).toBe('Close session Checkout flow')
  })

  it('should offer what closing can do with its branch and worktree', async () => {
    const { page } = await closing()
    expect(page.store.state.closing?.offeredLeaving).toEqual(['handoff', 'commit', 'push', 'merge', 'delete_branch', 'delete_worktree'])
  })

  it('should send what a person has ticked', async () => {
    const { page, asked } = await closing()
    page.activation.toggleLeaving('handoff')
    await page.activation.confirm()
    expect(asked.find(request => request.path === `/api/ticket/${ACTIVE}/close`)?.body).toEqual({ leaving: ['handoff'] })
  })

  it('should select the ticket in Complete', async () => {
    const { page } = await closing()
    await page.activation.confirm()
    expect(page.store.state.selected).toBe('Complete/checkout-flow')
  })

  // A ticket open in its own worktree closes from the main board too, while no chat working on it is chosen.
  describe('that is open in its worktree with no chat of its own chosen', () => {
    async function pressed() {
      board.openWorktree(CHOSEN)
      const { page } = await board.page()
      await ticketOn(page, CHOSEN).startClose()
      return page
    }

    it('should say the ticket is open', async () => {
      board.openWorktree(CHOSEN)
      const { page } = await board.page()
      expect(ticketOn(page, CHOSEN).isOpen).toBe(true)
    })

    it('should ask what to do with its work', async () => {
      expect(closingHeading((await pressed()).store.state.closing!)).toBe('Close session Billing report')
    })
  })

  describe('that a person has cancelled', () => {
    async function cancelled() {
      const { page, asked } = await closing()
      page.activation.cancel()
      return { page, asked }
    }

    it('should close the dialog', async () => {
      const { page } = await cancelled()
      expect(page.store.state.closing).toBeNull()
    })

    it('should send nothing', async () => {
      const { asked } = await cancelled()
      expect(asked.filter(request => request.path === `/api/ticket/${ACTIVE}/close`)).toEqual([])
    })
  })
})
