import { describe, expect, it } from 'vitest'

import { activationHeading } from './activation-client'
import { boardJson, discovery, pageOn, ticketJson } from './spec-support'

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

  it('should send what was chosen and report it', async () => {
    const { page, server, chosen } = switchingPage()
    server.answer('POST /api/tickets/pet-visits/activate', ticketJson('pet-visits'))
    await page.activation.start(chosen, false)
    page.activation.toggleLeaving('merge')
    await page.activation.confirm()
    expect(server.posted('/api/tickets/pet-visits/activate')[0]?.body).toEqual({ leaving: ['commit', 'push', 'merge'], opening: ['branch'] })
    expect(page.store.state.toasts.at(-1)?.text).toBe('Sign up: committed, pushed, merged to main · Pet visits: branch created · Pet visits is now active')
  })

  it('should do nothing on Cancel', async () => {
    const { page, server, chosen } = switchingPage()
    await page.activation.start(chosen, false)
    page.activation.cancel()
    expect(page.store.state.activation).toBeNull()
    expect(server.posted('/api/tickets/pet-visits/activate')).toEqual([])
  })
})

describe('Close Active Session', () => {
  it('should ask what to do with its work, then close it', async () => {
    const { page, server, active } = switchingPage()
    server.answer('POST /api/tickets/sign-up/close', ticketJson('sign-up', { title: 'Sign up', column: 'Complete' }))
    await page.activation.start(active, true)
    expect(activationHeading(page.store.state.activation!)).toBe('Close session Sign up')
    await page.activation.confirm()
    expect(server.posted('/api/tickets/sign-up/close')[0]?.body).toEqual({ leaving: ['commit', 'push'] })
    expect(page.store.state.selected).toBe('Complete/sign-up')
  })
})
