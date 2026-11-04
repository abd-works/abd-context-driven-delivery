import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest'

import type { BoardPage } from '@src/kanban/board/board-page'
import type { ColumnClient } from '@src/kanban/board/column-client'
import { BoardOnProject, ticketOn } from 'test-utils/board-page-support'

import type { TicketFiles } from './ticket'
import { cellPlace, headPlace } from './tile-client'
import { chipsOf, chosenFormats, defaultPicks } from './tile-formats'

// billing-report is made the active ticket: nothing is recorded on it yet. The project's story map,
// tests/story-map.md, is its markdown; a spec removes it for a ticket with nothing generated.
const TICKET = 'billing-report'
const SLUG = 'stories-story_map'
const STORY_MAP = 'tests/story-map.md'
const TWO_SLUGS = [SLUG, 'ddd-bounded_context']
const PLACE = cellPlace('Discovery', SLUG)
const OTHER_SLUG = 'ddd-bounded_context'
const OTHER_PLACE = cellPlace('Discovery', OTHER_SLUG)
const THIRD_SLUG = 'ux-ia'
const THIRD_PLACE = cellPlace('Discovery', THIRD_SLUG)
const HEAD = headPlace('Discovery')
const HOVER_MILLISECONDS = 500
const LEAVE_MILLISECONDS = 250
const LATER_STAMP = '2026-11-02T10:00:00Z'

let board: BoardOnProject
let STAGE: ColumnClient
let NOTHING_MADE: TicketFiles
let MARKDOWN_MADE: TicketFiles

const filesOn = async (): Promise<TicketFiles> => (await board.board.api.post<TicketFiles>(`/ticket/${TICKET}/files`, { fidelities: [SLUG] }))!

beforeAll(async () => {
  board = await BoardOnProject.start()
  STAGE = (await board.page()).page.board.stageNamed('Discovery')!
  MARKDOWN_MADE = await filesOn()
  board.remove(STORY_MAP)
  NOTHING_MADE = await filesOn()
})

beforeEach(() => {
  board.reset()
  board.activate(TICKET)
})

afterAll(() => board.close())

async function activeTicketPage({ isMarkdownMade = false } = {}) {
  if (!isMarkdownMade) board.remove(STORY_MAP)
  const { page } = await board.page()
  await board.connectChat(page)
  return { page, ticket: ticketOn(page, TICKET), chat: board.chat('chat-1') }
}

const spot = (slugs = [SLUG], place = PLACE) => ({ ticket: TICKET, stage: STAGE, place, slugs })
const barAt = (page: BoardPage, place = PLACE) => page.tiles.openOn(TICKET, place)
const openPlaces = (page: BoardPage) => page.store.state.tiles.map(tile => tile.place)

describe('Choose Action And Formats', () => {
  it('should give each fidelity its default format', () => {
    expect(defaultPicks(STAGE, [SLUG], NOTHING_MADE)).toEqual(['markdown'])
  })

  it('should not pick a format already generated', () => {
    expect(defaultPicks(STAGE, [SLUG], MARKDOWN_MADE)).toEqual([])
  })

  it('should let a chip stand for a group', () => {
    expect(chipsOf(STAGE, TWO_SLUGS).map(chip => chip.label)).toEqual(['diagram', 'markdown'])
  })

  it('should give each fidelity its default format from a chip', () => {
    expect(chosenFormats(STAGE, TWO_SLUGS, ['markdown'])).toEqual(['markdown'])
  })

  describe('with a format generated on one fidelity of two', () => {
    async function markdownChip() {
      const { page, ticket } = await activeTicketPage({ isMarkdownMade: true })
      await page.tiles.open(spot(TWO_SLUGS, HEAD), true)
      return page.tileActions.barOf(ticket, STAGE, barAt(page, HEAD)!).chips.find(chip => chip.label === 'markdown')
    }

    it('should count how many fidelities it is generated on', async () => {
      expect((await markdownChip())?.count).toBe('1 of 2')
    })

    it('should say so in its hint', async () => {
      expect((await markdownChip())?.hint).toBe('markdown: 1 of 2 done')
    })
  })

  it('should keep Run off until a format is chosen', async () => {
    const { page, ticket } = await activeTicketPage({ isMarkdownMade: true })
    await page.tiles.open(spot(), true)
    expect(page.tileActions.barOf(ticket, STAGE, barAt(page)!).runOff).toBe(true)
  })

  it('should keep Run off on a render with nothing to render', async () => {
    const { page, ticket } = await activeTicketPage()
    await page.tiles.open(spot(), true)
    page.tileActions.chooseAction(barAt(page)!, 'render')
    expect(page.tileActions.barOf(ticket, STAGE, barAt(page)!).runOff).toBe(true)
  })

  it('should keep Run off on a locked ticket', async () => {
    const { page } = await activeTicketPage()
    await page.tiles.open({ ...spot(), ticket: 'move-me' }, true)
    expect(page.tileActions.barOf(ticketOn(page, 'move-me'), STAGE, page.tiles.openOn('move-me', PLACE)!).runOff).toBe(true)
  })

  it('should keep Run off with no chat connected', async () => {
    const { page, ticket } = await activeTicketPage()
    page.store.change({ targetChat: null })
    await page.tiles.open(spot(), true)
    expect(page.tileActions.barOf(ticket, STAGE, barAt(page)!).runOff).toBe(true)
  })
})

describe('Validate Fidelity', () => {
  it('should allow Validate on files already there, with nothing recorded yet', async () => {
    const { page, ticket } = await activeTicketPage({ isMarkdownMade: true })
    await page.tiles.open(spot(), true)
    expect(page.tileActions.barOf(ticket, STAGE, barAt(page)!).validateOff).toBe(false)
  })

  it('should keep Validate off with no files and nothing recorded', async () => {
    const { page, ticket } = await activeTicketPage()
    await page.tiles.open(spot(), true)
    expect(page.tileActions.barOf(ticket, STAGE, barAt(page)!).validateOff).toBe(true)
  })

  it('should link to the report of the fidelity left with violations', async () => {
    board.logOn(TICKET, 'validate Stories story_map', 'validate ddd bounded_context graph-rule domain-nouns-only tests/story-map.md:6')
    board.write(`.sessions/${TICKET}/validation-reports/stories-story-map-20261101T100000.md`, '# Graph rule validation\n')
    board.write(`.sessions/${TICKET}/validation-reports/ddd-bounded-context-20261101T100000.md`, '# Graph rule validation\n')
    const { page, ticket } = await activeTicketPage()
    await page.tiles.open(spot(TWO_SLUGS, HEAD), true)
    expect(page.tileActions.barOf(ticket, STAGE, barAt(page, HEAD)!).reportSlug).toBe(OTHER_SLUG)
  })
})

describe('Generate Fidelity Output', () => {
  async function ran() {
    const { page, chat } = await activeTicketPage()
    await page.tiles.open(spot(), true)
    await page.tileActions.run(barAt(page)!, STAGE)
    return { page, chat }
  }

  it('should send the commands the ticket names', async () => {
    const { chat } = await ran()
    expect(await chat.checkIn()).toEqual([{ kind: 'command', text: '/actions-generate stories-story-map format=markdown session=.sessions/billing-report/session.json' }])
  })

  it('should clear the picks', async () => {
    const { page } = await ran()
    expect(barAt(page)?.picked).toEqual([])
  })
})

describe('Render Fidelity Format', () => {
  it('should turn existing output into the chosen format', async () => {
    const { page, chat } = await activeTicketPage({ isMarkdownMade: true })
    await page.tiles.open(spot(), true)
    page.tileActions.chooseAction(barAt(page)!, 'render')
    page.tileActions.toggleFormat(barAt(page)!, 'diagram')
    await page.tileActions.run(barAt(page)!, STAGE)
    expect(await chat.checkIn()).toEqual([{ kind: 'command', text: '/actions-render stories-story-map format=drawio session=.sessions/billing-report/session.json' }])
  })
})

describe('Send Tile Action To Chat', () => {
  it.each(['sketch', 'iterate', 'document'])('should send %s as its own command', async action => {
    const { page, chat } = await activeTicketPage()
    await page.tiles.open(spot(), true)
    page.tileActions.chooseAction(barAt(page)!, action)
    await page.tileActions.run(barAt(page)!, STAGE)
    expect(await chat.checkIn()).toEqual([{ kind: 'command', text: `/actions-${action} stories-story-map session=.sessions/billing-report/session.json` }])
  })
})

describe('Validate Fidelity', () => {
  it('should send the fidelity to validate', async () => {
    const { page, chat } = await activeTicketPage()
    await page.tiles.open(spot(), true)
    await page.tileActions.validate(barAt(page)!)
    expect(await chat.checkIn()).toEqual([{ kind: 'command', text: '/actions-validate stories-story-map session=.sessions/billing-report/session.json' }])
  })

  it('should stay off until the ticket allows it', async () => {
    const { page, ticket } = await activeTicketPage()
    await page.tiles.open(spot(), true)
    expect(page.tileActions.barOf(ticket, STAGE, barAt(page)!).validateOff).toBe(true)
  })
})

describe('Review Fidelity', () => {
  it('should not allow Review until Validate is clean', async () => {
    const { page, ticket } = await activeTicketPage()
    await page.tiles.open(spot(), true)
    expect(page.tileActions.barOf(ticket, STAGE, barAt(page)!).reviewOff).toBe(true)
  })
})

describe('Send Action To Stage Practices', () => {
  it('should name every fidelity of the stage in one command', async () => {
    const { page, chat } = await activeTicketPage()
    await page.tiles.open(spot(STAGE.workRequired, HEAD), true)
    page.tileActions.chooseAction(barAt(page, HEAD)!, 'sketch')
    await page.tileActions.run(barAt(page, HEAD)!, STAGE)
    expect(await chat.checkIn()).toEqual([{ kind: 'command', text: '/actions-sketch stories-story-map ddd-bounded-context ux-ia clean-engineering-modules bdd-behavior session=.sessions/billing-report/session.json' }])
  })
})

describe('Open Practice Tile', () => {
  // Only the page's own delays are timed by the spec; its calls to the server still take real time.
  const pointerTimers = () => vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should open a tile after a short hover', async () => {
    const { page } = await activeTicketPage()
    pointerTimers()
    page.tiles.hoverIn(spot())
    await vi.advanceTimersByTimeAsync(HOVER_MILLISECONDS)
    expect(openPlaces(page)).toEqual([PLACE])
  })

  it('should show the bar before its files are read', async () => {
    const { page } = await activeTicketPage()
    const opening = page.tiles.open(spot(), true)
    expect(openPlaces(page)).toEqual([PLACE])
    await opening
  })

  it('should pick formats from the files once they are read', async () => {
    const { page } = await activeTicketPage({ isMarkdownMade: true })
    await page.tiles.open(spot(), true)
    expect(barAt(page)?.picked).toEqual([])
  })

  it('should close it on leaving', async () => {
    const { page } = await activeTicketPage()
    await page.tiles.open(spot(), false)
    pointerTimers()
    page.tiles.hoverOut(TICKET, PLACE)
    await vi.advanceTimersByTimeAsync(LEAVE_MILLISECONDS)
    expect(page.store.state.tiles).toEqual([])
  })

  it('should keep a tile a person pressed open after the pointer leaves', async () => {
    const { page, ticket } = await activeTicketPage()
    await page.tiles.toggle(ticket, spot())
    pointerTimers()
    page.tiles.hoverOut(TICKET, PLACE)
    await vi.advanceTimersByTimeAsync(LEAVE_MILLISECONDS)
    expect(openPlaces(page)).toEqual([PLACE])
  })

  it('should close on a second press', async () => {
    const { page, ticket } = await activeTicketPage()
    await page.tiles.toggle(ticket, spot())
    await page.tiles.toggle(ticket, spot())
    expect(page.store.state.tiles).toEqual([])
  })

  describe('with two tiles pressed', () => {
    async function pressedTwo() {
      const { page, ticket } = await activeTicketPage()
      await page.tiles.toggle(ticket, spot())
      await page.tiles.toggle(ticket, spot([OTHER_SLUG], OTHER_PLACE))
      return { page, ticket }
    }

    it('should keep both bars open', async () => {
      const { page } = await pressedTwo()
      expect(openPlaces(page)).toEqual([PLACE, OTHER_PLACE])
    })

    it('should close only the bar pressed again', async () => {
      const { page, ticket } = await pressedTwo()
      await page.tiles.toggle(ticket, spot())
      expect(openPlaces(page)).toEqual([OTHER_PLACE])
    })

    it("should change only that bar's action", async () => {
      const { page } = await pressedTwo()
      page.tileActions.chooseAction(barAt(page)!, 'render')
      expect(page.store.state.tiles.map(tile => tile.action)).toEqual(['render', 'generate'])
    })
  })

  describe('with a pressed bar and a bar a hover opened', () => {
    async function pressedAndHovered() {
      const { page, ticket } = await activeTicketPage()
      await page.tiles.toggle(ticket, spot())
      pointerTimers()
      page.tiles.hoverIn(spot([OTHER_SLUG], OTHER_PLACE))
      await vi.advanceTimersByTimeAsync(HOVER_MILLISECONDS)
      return page
    }

    it('should open the hovered bar beside the pressed one', async () => {
      expect(openPlaces(await pressedAndHovered())).toEqual([PLACE, OTHER_PLACE])
    })

    it('should replace the hovered bar with the next one a hover opens, and keep the pressed one', async () => {
      const page = await pressedAndHovered()
      page.tiles.hoverIn(spot([THIRD_SLUG], THIRD_PLACE))
      await vi.advanceTimersByTimeAsync(HOVER_MILLISECONDS)
      expect(openPlaces(page)).toEqual([PLACE, THIRD_PLACE])
    })

    it('should close the hovered bar on leaving, and keep the pressed one', async () => {
      const page = await pressedAndHovered()
      page.tiles.hoverOut(TICKET, OTHER_PLACE)
      await vi.advanceTimersByTimeAsync(LEAVE_MILLISECONDS)
      expect(openPlaces(page)).toEqual([PLACE])
    })
  })

  describe('with two stage heads pressed', () => {
    it('should keep both stage bars open', async () => {
      const { page, ticket } = await activeTicketPage()
      const specification = page.board.stageNamed('Specification')!
      await page.tiles.toggle(ticket, spot(STAGE.workRequired, HEAD))
      await page.tiles.toggle(ticket, { ticket: TICKET, stage: specification, place: headPlace(specification.name), slugs: specification.workRequired })
      expect(openPlaces(page)).toEqual([HEAD, headPlace('Specification')])
    })
  })
})

describe('Expand Ticket', () => {
  it('should open with its tiles only, each opening its own action bar', async () => {
    const { page, ticket } = await activeTicketPage()
    page.cards.toggle(ticket)
    expect(page.store.state.tiles).toEqual([])
  })

  it('should expand only one card at a time', async () => {
    const { page, ticket } = await activeTicketPage()
    page.cards.toggle(ticket)
    page.cards.toggle(ticketOn(page, 'move-me'))
    expect(page.store.state.openCard).toBe('move-me')
  })

  describe('with a segment pressed', () => {
    async function pressed() {
      const { page, ticket } = await activeTicketPage()
      await page.cards.openSegment(ticket, STAGE, SLUG)
      return page
    }

    it('should open the card', async () => {
      expect((await pressed()).store.state.openCard).toBe(TICKET)
    })

    it('should open the tile of that fidelity', async () => {
      expect(openPlaces(await pressed())).toEqual([PLACE])
    })
  })

  it('should move an open bar to the tile the ticket works on next when it moves', async () => {
    const { page, ticket } = await activeTicketPage()
    await page.tiles.open(spot([OTHER_SLUG], OTHER_PLACE), true)
    await page.cards.follow(ticket)
    expect(openPlaces(page)).toEqual([PLACE])
  })
})

describe('Refresh Board After Tool Calls', () => {
  it("should read an open bar's files again when the board changes", async () => {
    const { page } = await activeTicketPage()
    await page.tiles.open(spot(), true)
    board.git('checkout', '--', STORY_MAP)
    board.write(`.sessions/${TICKET}/session.log`, `${LATER_STAMP} generate /work stories story_map markdown stories no-chat\n`)
    await page.reader.refresh()
    expect(barAt(page)?.files).toEqual(MARKDOWN_MADE)
  })
})
