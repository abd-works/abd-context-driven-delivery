import { describe, expect, it } from 'vitest'

import { activationHeading } from './activation-client'
import { boardJson, discovery, ticketJson } from 'test-utils/board-examples'
import { pageOn } from 'test-utils/board-page-support'

const CHECKED_OUT = { has_branch: false, has_worktree: false, leaving_has_branch: true }

function switchingPage() {
  const active = ticketJson('sign-up', { title: 'Sign up' })
  const chosen = ticketJson('pet-visits', { title: 'Pet visits' })
  const { page, server } = pageOn(boardJson([discovery([active, chosen])], 'sign-up'))
  server.answer('GET /api/tickets/pet-visits/workspace', CHECKED_OUT)
  server.answer('GET /api/tickets/sign-up/workspace', CHECKED_OUT)
  return { page, server, active: page.ticket(active), chosen: page.ticket(chosen) }
}

describe('Activate Ticket', () => {
  it('should offer commit and push on leaving and open with merge off', async () => {
    const { page, chosen } = switchingPage()
    await page.activation.start(chosen, false)
    expect(page.store.state.activation?.leaving).toEqual(['commit', 'push'])
  })

  it('should offer a branch to a ticket that has none', async () => {
    const { page, chosen } = switchingPage()
    await page.activation.start(chosen, false)
    expect(page.store.state.activation?.opening).toEqual(['branch'])
  })

  it('should choose nothing to leave when the session has no branch', async () => {
    const { page, server, chosen } = switchingPage()
    server.answer('GET /api/tickets/pet-visits/workspace', { ...CHECKED_OUT, leaving_has_branch: false })
    await page.activation.start(chosen, false)
    expect(page.store.state.activation?.leaving).toEqual([])
  })

  it('should say what it switches from and to', async () => {
    const { page, chosen } = switchingPage()
    await page.activation.start(chosen, false)
    expect(activationHeading(page.store.state.activation!)).toBe('Switch from Sign up to Pet visits')
  })

  describe('that a person has confirmed with merge chosen', () => {
    async function confirmed() {
      const { page, server, chosen } = switchingPage()
      server.answer('POST /api/tickets/pet-visits/activate', ticketJson('pet-visits'))
      await page.activation.start(chosen, false)
      page.activation.toggleLeaving('merge')
      await page.activation.confirm()
      return { page, server }
    }

    it('should send what was chosen', async () => {
      const { server } = await confirmed()
      expect(server.posted('/api/tickets/pet-visits/activate')[0]?.body).toEqual({ leaving: ['commit', 'push', 'merge'], opening: ['branch'] })
    })

    it('should report it', async () => {
      const { page } = await confirmed()
      expect(page.store.state.toasts.at(-1)?.text).toBe('Sign up: committed, pushed, merged to main · Pet visits: branch created · Pet visits is now active')
    })
  })

  describe('that a person has cancelled', () => {
    async function cancelled() {
      const { page, server, chosen } = switchingPage()
      await page.activation.start(chosen, false)
      page.activation.cancel()
      return { page, server }
    }

    it('should close the dialog', async () => {
      const { page } = await cancelled()
      expect(page.store.state.activation).toBeNull()
    })

    it('should send nothing', async () => {
      const { server } = await cancelled()
      expect(server.posted('/api/tickets/pet-visits/activate')).toEqual([])
    })
  })
})

describe('Close Active Session', () => {
  async function closing() {
    const { page, server, active } = switchingPage()
    server.answer('POST /api/tickets/sign-up/close', ticketJson('sign-up', { title: 'Sign up', column: 'Complete' }))
    await page.activation.start(active, true)
    return { page, server }
  }

  it('should ask what to do with its work', async () => {
    const { page } = await closing()
    expect(activationHeading(page.store.state.activation!)).toBe('Close session Sign up')
  })

  it('should send what to do with its work', async () => {
    const { page, server } = await closing()
    await page.activation.confirm()
    expect(server.posted('/api/tickets/sign-up/close')[0]?.body).toEqual({ leaving: ['commit', 'push'] })
  })

  it('should select the ticket in Complete', async () => {
    const { page } = await closing()
    await page.activation.confirm()
    expect(page.store.state.selected).toBe('Complete/sign-up')
  })
})
