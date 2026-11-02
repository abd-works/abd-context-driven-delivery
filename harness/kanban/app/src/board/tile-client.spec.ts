import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { TicketFiles } from './board'
import { boardJson, discovery, DISCOVERY_SLUGS, pageOn, ticketJson, withChat } from './spec-support'
import { CARD_MENU, cellPlace } from './tile-client'
import { chipsOf, chosenFormats, defaultPicks } from './tile-formats'

const STAGE = discovery()
const SLUG = 'stories-story_map'
const PLACE = cellPlace('Discovery', SLUG)
const NOTHING_MADE: TicketFiles = { [SLUG]: { markdown: [{ path: 'tests/story-map.md', exists: false }], drawio: [{ path: 'tests/story-map.drawio', exists: false }] } }
const MARKDOWN_MADE: TicketFiles = { [SLUG]: { markdown: [{ path: 'tests/story-map.md', exists: true }], drawio: [{ path: 'tests/story-map.drawio', exists: false }] } }

function activeTicketPage(files: TicketFiles = NOTHING_MADE) {
  const json = ticketJson('sign-up')
  const { page, server } = pageOn(boardJson([discovery([json])], 'sign-up'))
  withChat(page, server)
  server.answer('POST /api/tickets/sign-up/files', files)
  return { page, server, ticket: page.ticket(json) }
}

describe('Choose Action And Formats', () => {
  it('should give each fidelity its default format', () => {
    expect(defaultPicks(STAGE, [SLUG], NOTHING_MADE)).toEqual(['markdown'])
  })

  it('should not pick a format already generated', () => {
    expect(defaultPicks(STAGE, [SLUG], MARKDOWN_MADE)).toEqual([])
  })

  it('should let a chip stand for a group, each fidelity using its default format from it', () => {
    expect(chipsOf(STAGE, DISCOVERY_SLUGS).map(chip => chip.label)).toEqual(['diagram', 'markdown'])
    expect(chosenFormats(STAGE, DISCOVERY_SLUGS, ['markdown'])).toEqual(['markdown'])
  })

  it('should say how many fidelities a format is generated on', async () => {
    const { page, ticket } = activeTicketPage(MARKDOWN_MADE)
    await page.tiles.open('sign-up', STAGE, 'head-Discovery', DISCOVERY_SLUGS, true)
    const markdown = page.tiles.barOf(ticket, STAGE, page.store.state.tile!).chips.find(chip => chip.label === 'markdown')
    expect(markdown?.count).toBe('1 of 2')
    expect(markdown?.hint).toBe('markdown: 1 of 2 done')
  })

  it('should keep Run off until a format is chosen', async () => {
    const { page, ticket } = activeTicketPage(MARKDOWN_MADE)
    await page.tiles.open('sign-up', STAGE, PLACE, [SLUG], true)
    expect(page.tiles.barOf(ticket, STAGE, page.store.state.tile!).runOff).toBe(true)
  })

  it('should keep Run off on a render with nothing to render', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.open('sign-up', STAGE, PLACE, [SLUG], true)
    page.tiles.chooseAction(page.store.state.tile!, 'render')
    expect(page.tiles.barOf(ticket, STAGE, page.store.state.tile!).runOff).toBe(true)
  })

  it('should keep Run off on a locked ticket', async () => {
    const json = ticketJson('other')
    const { page, server } = pageOn(boardJson([discovery([json])], 'sign-up'))
    withChat(page, server)
    server.answer('POST /api/tickets/other/files', NOTHING_MADE)
    await page.tiles.open('other', STAGE, PLACE, [SLUG], true)
    expect(page.tiles.barOf(page.ticket(json), STAGE, page.store.state.tile!).runOff).toBe(true)
  })

  it('should keep Run off with no chat connected', async () => {
    const { page, ticket } = activeTicketPage()
    page.store.change({ targetChat: null })
    await page.tiles.open('sign-up', STAGE, PLACE, [SLUG], true)
    expect(page.tiles.barOf(ticket, STAGE, page.store.state.tile!).runOff).toBe(true)
  })
})

describe('Generate Fidelity Output', () => {
  it('should send the commands the ticket names, and clear the picks', async () => {
    const { page, server } = activeTicketPage()
    server.answer('POST /api/tickets/sign-up/generate-commands', ['/actions-generate stories-story-map format=markdown'])
    await page.tiles.open('sign-up', STAGE, PLACE, [SLUG], true)
    await page.tiles.run(page.store.state.tile!, STAGE)
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'command', text: '/actions-generate stories-story-map format=markdown' })
    expect(page.store.state.tile?.picked).toEqual([])
  })
})

describe('Render Fidelity Format', () => {
  it('should turn existing output into the chosen format', async () => {
    const { page, server } = activeTicketPage(MARKDOWN_MADE)
    await page.tiles.open('sign-up', STAGE, PLACE, [SLUG], true)
    page.tiles.chooseAction(page.store.state.tile!, 'render')
    page.tiles.toggleFormat(page.store.state.tile!, 'diagram')
    await page.tiles.run(page.store.state.tile!, STAGE)
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'command', text: '/actions-render stories-story-map format=drawio' })
  })
})

describe('Send Sketch Iterate Or Document', () => {
  it.each(['sketch', 'iterate', 'document'])('should send %s as its own command', async action => {
    const { page, server } = activeTicketPage()
    await page.tiles.open('sign-up', STAGE, PLACE, [SLUG], true)
    page.tiles.chooseAction(page.store.state.tile!, action)
    await page.tiles.run(page.store.state.tile!, STAGE)
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'command', text: `/actions-${action} stories-story-map` })
  })
})

describe('Validate Fidelity', () => {
  it('should send the fidelity to validate', async () => {
    const { page, server } = activeTicketPage()
    await page.tiles.open('sign-up', STAGE, PLACE, [SLUG], true)
    await page.tiles.validate(page.store.state.tile!)
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'command', text: '/actions-validate stories-story-map' })
  })

  it('should stay off until the ticket allows it', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.open('sign-up', STAGE, PLACE, [SLUG], true)
    expect(page.tiles.barOf(ticket, STAGE, page.store.state.tile!).validateOff).toBe(true)
  })
})

describe('Review Fidelity', () => {
  it('should not allow Review until Validate is clean', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.open('sign-up', STAGE, PLACE, [SLUG], true)
    expect(page.tiles.barOf(ticket, STAGE, page.store.state.tile!).reviewOff).toBe(true)
  })
})

describe('Run Action Across Practices', () => {
  it('should name every fidelity of the stage in one command', async () => {
    const { page, server } = activeTicketPage()
    await page.tiles.open('sign-up', STAGE, 'head-Discovery', DISCOVERY_SLUGS, true)
    page.tiles.chooseAction(page.store.state.tile!, 'sketch')
    await page.tiles.run(page.store.state.tile!, STAGE)
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'command', text: '/actions-sketch stories-story-map ddd-bounded-context' })
  })
})

describe('Open Practice Tile', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should open a tile after a short hover', async () => {
    const { page } = activeTicketPage()
    page.tiles.hoverIn('sign-up', STAGE, PLACE, [SLUG])
    await vi.advanceTimersByTimeAsync(500)
    expect(page.store.state.tile?.place).toBe(PLACE)
  })

  it('should close it on leaving', async () => {
    const { page } = activeTicketPage()
    await page.tiles.open('sign-up', STAGE, PLACE, [SLUG], false)
    page.tiles.hoverOut(PLACE)
    await vi.advanceTimersByTimeAsync(250)
    expect(page.store.state.tile).toBeNull()
  })

  it('should keep a tile a person pressed open after the pointer leaves', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.toggle(ticket, STAGE, PLACE, [SLUG])
    page.tiles.hoverOut(PLACE)
    await vi.advanceTimersByTimeAsync(250)
    expect(page.store.state.tile?.place).toBe(PLACE)
  })

  it('should leave a pressed bar alone when the pointer crosses another tile', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.toggle(ticket, STAGE, PLACE, [SLUG])
    page.tiles.hoverIn('sign-up', STAGE, cellPlace('Discovery', 'ddd-bounded_context'), ['ddd-bounded_context'])
    await vi.advanceTimersByTimeAsync(500)
    expect(page.store.state.tile?.place).toBe(PLACE)
  })

  it('should close on a second press', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.toggle(ticket, STAGE, PLACE, [SLUG])
    await page.tiles.toggle(ticket, STAGE, PLACE, [SLUG])
    expect(page.store.state.tile).toBeNull()
  })
})

describe('Expand Ticket', () => {
  it('should open with its action bar over all its fidelities', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.toggleCard(ticket, STAGE)
    expect(page.store.state.cardMenu?.place).toBe(CARD_MENU)
    expect(page.store.state.cardMenu?.slugs).toEqual(DISCOVERY_SLUGS)
  })

  it('should expand only one card at a time', async () => {
    const other = ticketJson('other')
    const { page, server, ticket } = activeTicketPage()
    server.answer('POST /api/tickets/other/files', NOTHING_MADE)
    await page.tiles.toggleCard(ticket, STAGE)
    await page.tiles.toggleCard(page.ticket(other), STAGE)
    expect(page.store.state.openCard).toBe('other')
  })

  it('should open the card on the fidelity of a pressed segment', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.openSegment(ticket, STAGE, SLUG)
    expect(page.store.state.openCard).toBe('sign-up')
    expect(page.store.state.tile?.place).toBe(PLACE)
  })

  it('should move an open bar to the tile the ticket works on next when it moves', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.open('sign-up', STAGE, cellPlace('Discovery', 'ddd-bounded_context'), ['ddd-bounded_context'], true)
    await page.tiles.follow(ticket)
    expect(page.store.state.tile?.place).toBe(PLACE)
  })
})

describe('Refresh Board After Tool Calls', () => {
  it('should read an open bar\'s files again when the board changes', async () => {
    const { page, server } = activeTicketPage()
    await page.tiles.open('sign-up', STAGE, PLACE, [SLUG], true)
    server.answer('POST /api/tickets/sign-up/files', MARKDOWN_MADE)
    server.answer('GET /api/board', boardJson([discovery([ticketJson('sign-up', { last_activity: '2026-11-02T10:00:00Z' })])], 'sign-up'))
    await page.board.refresh()
    expect(page.store.state.tile?.files).toEqual(MARKDOWN_MADE)
  })
})
