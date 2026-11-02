import { describe, expect, it } from 'vitest'

import { boardJson, discovery, ticketJson } from 'test-utils/board-examples'
import { pageOn, withChat } from 'test-utils/board-page-support'
import { skillOf } from './ticket-client'

describe('Restrict Actions To Active Session', () => {
  it('should lock a ticket that is not the active session', () => {
    const { page } = pageOn(boardJson([discovery([ticketJson('other')])], 'sign-up'))
    expect(page.ticket(ticketJson('other')).isLocked).toBe(true)
  })

  it('should leave the active ticket open', () => {
    const { page } = pageOn(boardJson([discovery([ticketJson('sign-up')])], 'sign-up'))
    expect(page.ticket(ticketJson('sign-up')).isLocked).toBe(false)
  })

  it('should unlock every ticket with Active session only off', () => {
    const { page } = pageOn(boardJson([discovery([ticketJson('other')])], 'sign-up'))
    page.layout.toggleOnlyActive()
    expect(page.ticket(ticketJson('other')).isLocked).toBe(false)
  })
})

describe('Display Ticket Details', () => {
  it('should say what next and that another session must be activated', () => {
    const { page } = pageOn(boardJson([discovery([ticketJson('other')])], 'sign-up'))
    expect(page.ticket(ticketJson('other')).footer).toBe('No handoff yet · Next: stories-story_map, generate · Activate this session to run actions')
  })

  it('should name a split ticket by its parent', () => {
    const { page } = pageOn(boardJson([discovery()]))
    expect(page.ticket(ticketJson('child', { scope: 'story', parent: 'epic' })).place).toBe('child · story of epic · Discovery · in progress')
  })

  it('should keep a practice with two words in its skill', () => {
    expect(skillOf('clean_engineering-code')).toBe('/practices-clean-engineering-clean-engineering-code')
  })
})

describe('Move Ticket', () => {
  it('should read the board again and select the ticket where it landed', async () => {
    const { page, server } = pageOn(boardJson([discovery([ticketJson('sign-up')])], 'sign-up'))
    server.answer('POST /api/tickets/sign-up/move-next', ticketJson('sign-up', { column: 'Specification' }))
    await page.ticket(ticketJson('sign-up')).moveNext()
    expect(page.store.state.selected).toBe('Specification/sign-up')
  })

  describe('that a person has moved to the Backlog', () => {
    async function moved() {
      const { page, server } = pageOn(boardJson([discovery([ticketJson('sign-up')])], 'sign-up'))
      page.store.change({ openCard: 'sign-up' })
      server.answer('POST /api/tickets/sign-up/move-previous', { title: 'sign-up', text: '', path: 'x.md', last_activity: '' })
      await page.ticket(ticketJson('sign-up')).movePrevious()
      return page
    }

    it('should let go of what was open on it', async () => {
      expect((await moved()).store.state.openCard).toBeNull()
    })

    it('should select its item', async () => {
      expect((await moved()).store.state.selected).toBe('Backlog/sign-up')
    })
  })

  it('should say the back arrow on Discovery goes to the Backlog', () => {
    const { page } = pageOn(boardJson([discovery()]))
    expect(page.ticket(ticketJson('sign-up')).backLabel).toBe('Move sign-up to the Backlog')
  })

  it('should say the back arrow from Discovery Done stays on the board', () => {
    const { page } = pageOn(boardJson([discovery()]))
    expect(page.ticket(ticketJson('sign-up', { is_done: true })).backLabel).toBe('Move sign-up to the previous column')
  })
})

describe('Run Next Step', () => {
  it('should name the step that runs next', () => {
    const { page } = pageOn(boardJson([discovery()]))
    expect(page.ticket(ticketJson('sign-up')).runNextLabel).toBe('Run next: generate')
  })

  it('should say fix violations on held violations', () => {
    const { page } = pageOn(boardJson([discovery()]))
    expect(page.ticket(ticketJson('sign-up', { next_action: 'satisfy' })).runNextLabel).toBe('Run next: fix violations')
  })

  describe('with generate next', () => {
    async function ran() {
      const { page, server } = pageOn(boardJson([discovery([ticketJson('sign-up')])], 'sign-up'))
      withChat(page, server)
      server.answer('POST /api/tickets/sign-up/generate-commands', ['/actions-render a', '/actions-generate b'])
      await page.ticket(ticketJson('sign-up')).runNext()
      return server
    }

    it('should ask for the commands of the default format', async () => {
      expect((await ran()).posted('/api/tickets/sign-up/generate-commands')[0]?.body).toEqual({ fidelities: ['stories-story_map'], formats: ['markdown'] })
    })

    it('should send those commands in order', async () => {
      expect((await ran()).posted('/api/chats/chat-1/commands').map(request => request.body)).toEqual([
        { kind: 'command', text: '/actions-render a' },
        { kind: 'command', text: '/actions-generate b' },
      ])
    })
  })

  it('should fill the prompt on validate', async () => {
    const { page, server } = pageOn(boardJson([discovery()], 'sign-up'))
    withChat(page, server)
    await page.ticket(ticketJson('sign-up', { next_action: 'validate' })).runNext()
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'fill', text: '/actions-validate stories-story-map' })
  })

  describe('with violations held and no chat connected', () => {
    function heldPage() {
      const { page, server } = pageOn(boardJson([discovery()], 'sign-up'))
      server.answer('GET /api/tickets/sign-up/report?fidelity=stories-story_map', { path: 'r.md', text: '', rules: [], has_saved_graph: true })
      return { page, ticket: page.ticket(ticketJson('sign-up', { next_action: 'satisfy' })) }
    }

    it('should still offer Run next', () => {
      expect(heldPage().ticket.canRunNext).toBe(true)
    })

    it('should open the report', async () => {
      const { page, ticket } = heldPage()
      await ticket.runNext()
      expect(page.store.state.panels.map(panel => panel.kind)).toEqual(['report'])
    })
  })

  it('should stay off with no chat to send to', () => {
    const { page } = pageOn(boardJson([discovery()], 'sign-up'))
    expect(page.ticket(ticketJson('sign-up')).canRunNext).toBe(false)
  })
})

describe('Choose Ticket Practices', () => {
  async function turnedOff() {
    const { page, server } = pageOn(boardJson([discovery([ticketJson('sign-up', { title: 'Sign up' })])], 'sign-up'))
    server.answer('POST /api/tickets/sign-up/practice', ticketJson('sign-up'))
    page.store.change({ tile: { ticket: 'sign-up', place: 'cell-Discovery-ddd-bounded_context', stage: 'Discovery', slugs: ['ddd-bounded_context'], action: 'generate', picked: [], isPinned: true, files: {} } })
    await page.ticket(ticketJson('sign-up', { title: 'Sign up' })).enablePractice('ddd', false)
    return page
  }

  it('should let go of the tile of a practice turned off', async () => {
    expect((await turnedOff()).store.state.tile).toBeNull()
  })

  it('should say so and where it was saved', async () => {
    expect((await turnedOff()).store.state.toasts[0]?.text).toBe('DDD off for Sign up · saved to .sessions/sign-up/session.json')
  })
})

describe('Write Ticket Handoff', () => {
  it('should fill the prompt with the handoff command', async () => {
    const { page, server } = pageOn(boardJson([discovery()], 'sign-up'))
    withChat(page, server)
    await page.ticket(ticketJson('sign-up')).fillHandoff()
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'fill', text: 'Write a handoff for ticket sign-up with /space-handoff-handoff-session.' })
  })
})

describe('Satisfy Violations From Band', () => {
  it('should fill the prompt with the fidelities that have violations', async () => {
    const { page, server } = pageOn(boardJson([discovery()], 'sign-up'))
    withChat(page, server)
    await page.ticket(ticketJson('sign-up', { progress: { 'stories-story_map': 'violations' } })).fillSatisfy()
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'fill', text: '/actions-satisfy stories-story-map' })
  })
})
