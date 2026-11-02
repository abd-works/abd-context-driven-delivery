import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { boardJson, discovery, DISCOVERY_SLUGS, ticketJson } from 'test-utils/board-examples'
import { pageOn, stageOn, withChat } from 'test-utils/board-page-support'

import type { TicketFiles } from './ticket'
import { CARD_MENU } from './open-card-client'
import { cellPlace } from './tile-client'
import { chipsOf, chosenFormats, defaultPicks } from './tile-formats'

const STAGE = stageOn(discovery())
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

  it('should let a chip stand for a group', () => {
    expect(chipsOf(STAGE, DISCOVERY_SLUGS).map(chip => chip.label)).toEqual(['diagram', 'markdown'])
  })

  it('should give each fidelity its default format from a chip', () => {
    expect(chosenFormats(STAGE, DISCOVERY_SLUGS, ['markdown'])).toEqual(['markdown'])
  })

  describe('with a format generated on one fidelity of two', () => {
    async function markdownChip() {
      const { page, ticket } = activeTicketPage(MARKDOWN_MADE)
      await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: 'head-Discovery', slugs: DISCOVERY_SLUGS }, true)
      return page.tileActions.barOf(ticket, STAGE, page.store.state.tile!).chips.find(chip => chip.label === 'markdown')
    }

    it('should count how many fidelities it is generated on', async () => {
      expect((await markdownChip())?.count).toBe('1 of 2')
    })

    it('should say so in its hint', async () => {
      expect((await markdownChip())?.hint).toBe('markdown: 1 of 2 done')
    })
  })

  it('should keep Run off until a format is chosen', async () => {
    const { page, ticket } = activeTicketPage(MARKDOWN_MADE)
    await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] }, true)
    expect(page.tileActions.barOf(ticket, STAGE, page.store.state.tile!).runOff).toBe(true)
  })

  it('should keep Run off on a render with nothing to render', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] }, true)
    page.tileActions.chooseAction(page.store.state.tile!, 'render')
    expect(page.tileActions.barOf(ticket, STAGE, page.store.state.tile!).runOff).toBe(true)
  })

  it('should keep Run off on a locked ticket', async () => {
    const json = ticketJson('other')
    const { page, server } = pageOn(boardJson([discovery([json])], 'sign-up'))
    withChat(page, server)
    server.answer('POST /api/tickets/other/files', NOTHING_MADE)
    await page.tiles.open({ ticket: 'other', stage: STAGE, place: PLACE, slugs: [SLUG] }, true)
    expect(page.tileActions.barOf(page.ticket(json), STAGE, page.store.state.tile!).runOff).toBe(true)
  })

  it('should keep Run off with no chat connected', async () => {
    const { page, ticket } = activeTicketPage()
    page.store.change({ targetChat: null })
    await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] }, true)
    expect(page.tileActions.barOf(ticket, STAGE, page.store.state.tile!).runOff).toBe(true)
  })
})

describe('Generate Fidelity Output', () => {
  async function ran() {
    const { page, server } = activeTicketPage()
    server.answer('POST /api/tickets/sign-up/generate-commands', ['/actions-generate stories-story-map format=markdown'])
    await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] }, true)
    await page.tileActions.run(page.store.state.tile!, STAGE)
    return { page, server }
  }

  it('should send the commands the ticket names', async () => {
    const { server } = await ran()
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'command', text: '/actions-generate stories-story-map format=markdown' })
  })

  it('should clear the picks', async () => {
    const { page } = await ran()
    expect(page.store.state.tile?.picked).toEqual([])
  })
})

describe('Render Fidelity Format', () => {
  it('should turn existing output into the chosen format', async () => {
    const { page, server } = activeTicketPage(MARKDOWN_MADE)
    await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] }, true)
    page.tileActions.chooseAction(page.store.state.tile!, 'render')
    page.tileActions.toggleFormat(page.store.state.tile!, 'diagram')
    await page.tileActions.run(page.store.state.tile!, STAGE)
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'command', text: '/actions-render stories-story-map format=drawio' })
  })
})

describe('Send Sketch Iterate Or Document', () => {
  it.each(['sketch', 'iterate', 'document'])('should send %s as its own command', async action => {
    const { page, server } = activeTicketPage()
    await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] }, true)
    page.tileActions.chooseAction(page.store.state.tile!, action)
    await page.tileActions.run(page.store.state.tile!, STAGE)
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'command', text: `/actions-${action} stories-story-map` })
  })
})

describe('Validate Fidelity', () => {
  it('should send the fidelity to validate', async () => {
    const { page, server } = activeTicketPage()
    await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] }, true)
    await page.tileActions.validate(page.store.state.tile!)
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'command', text: '/actions-validate stories-story-map' })
  })

  it('should stay off until the ticket allows it', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] }, true)
    expect(page.tileActions.barOf(ticket, STAGE, page.store.state.tile!).validateOff).toBe(true)
  })
})

describe('Review Fidelity', () => {
  it('should not allow Review until Validate is clean', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] }, true)
    expect(page.tileActions.barOf(ticket, STAGE, page.store.state.tile!).reviewOff).toBe(true)
  })
})

describe('Run Action Across Practices', () => {
  it('should name every fidelity of the stage in one command', async () => {
    const { page, server } = activeTicketPage()
    await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: 'head-Discovery', slugs: DISCOVERY_SLUGS }, true)
    page.tileActions.chooseAction(page.store.state.tile!, 'sketch')
    await page.tileActions.run(page.store.state.tile!, STAGE)
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
    page.tiles.hoverIn({ ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] })
    await vi.advanceTimersByTimeAsync(500)
    expect(page.store.state.tile?.place).toBe(PLACE)
  })

  it('should close it on leaving', async () => {
    const { page } = activeTicketPage()
    await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] }, false)
    page.tiles.hoverOut(PLACE)
    await vi.advanceTimersByTimeAsync(250)
    expect(page.store.state.tile).toBeNull()
  })

  it('should keep a tile a person pressed open after the pointer leaves', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.toggle(ticket, { ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] })
    page.tiles.hoverOut(PLACE)
    await vi.advanceTimersByTimeAsync(250)
    expect(page.store.state.tile?.place).toBe(PLACE)
  })

  it('should leave a pressed bar alone when the pointer crosses another tile', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.toggle(ticket, { ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] })
    page.tiles.hoverIn({ ticket: 'sign-up', stage: STAGE, place: cellPlace('Discovery', 'ddd-bounded_context'), slugs: ['ddd-bounded_context'] })
    await vi.advanceTimersByTimeAsync(500)
    expect(page.store.state.tile?.place).toBe(PLACE)
  })

  it('should close on a second press', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.toggle(ticket, { ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] })
    await page.tiles.toggle(ticket, { ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] })
    expect(page.store.state.tile).toBeNull()
  })
})

describe('Expand Ticket', () => {
  it('should open with its action bar over all its fidelities', async () => {
    const { page, ticket } = activeTicketPage()
    await page.cards.toggle(ticket, STAGE)
    expect(page.store.state.cardMenu).toMatchObject({ place: CARD_MENU, slugs: DISCOVERY_SLUGS })
  })

  it('should expand only one card at a time', async () => {
    const other = ticketJson('other')
    const { page, server, ticket } = activeTicketPage()
    server.answer('POST /api/tickets/other/files', NOTHING_MADE)
    await page.cards.toggle(ticket, STAGE)
    await page.cards.toggle(page.ticket(other), STAGE)
    expect(page.store.state.openCard).toBe('other')
  })

  describe('with a segment pressed', () => {
    async function pressed() {
      const { page, ticket } = activeTicketPage()
      await page.cards.openSegment(ticket, STAGE, SLUG)
      return page
    }

    it('should open the card', async () => {
      expect((await pressed()).store.state.openCard).toBe('sign-up')
    })

    it('should open the tile of that fidelity', async () => {
      expect((await pressed()).store.state.tile?.place).toBe(PLACE)
    })
  })

  it('should move an open bar to the tile the ticket works on next when it moves', async () => {
    const { page, ticket } = activeTicketPage()
    await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: cellPlace('Discovery', 'ddd-bounded_context'), slugs: ['ddd-bounded_context'] }, true)
    await page.cards.follow(ticket)
    expect(page.store.state.tile?.place).toBe(PLACE)
  })
})

describe('Refresh Board After Tool Calls', () => {
  it('should read an open bar\'s files again when the board changes', async () => {
    const { page, server } = activeTicketPage()
    await page.tiles.open({ ticket: 'sign-up', stage: STAGE, place: PLACE, slugs: [SLUG] }, true)
    server.answer('POST /api/tickets/sign-up/files', MARKDOWN_MADE)
    server.answer('GET /api/board', boardJson([discovery([ticketJson('sign-up', { last_activity: '2026-11-02T10:00:00Z' })])], 'sign-up'))
    await page.reader.refresh()
    expect(page.store.state.tile?.files).toEqual(MARKDOWN_MADE)
  })
})
