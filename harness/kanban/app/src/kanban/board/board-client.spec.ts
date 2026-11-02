import { describe, expect, it } from 'vitest'

import type { BoardData } from '@cdd/harness/kanban/board'
import { boardJson, discovery, ticketJson } from 'test-utils/board-examples'
import { FakeServer, pageOn } from 'test-utils/board-page-support'

import { ageOf } from './board-brand'
import { BoardPage } from './board-page'

const announcementsOf = (before: BoardData, after: BoardData): string[] => pageOn(after).page.board.announcementsSince(pageOn(before).page.board)

describe('Display Board', () => {
  describe('Display Connected Status', () => {
    it('should show a band when the board read answers that cdd is not connected', async () => {
      const server = new FakeServer().answer('GET /api/board', { error: 'The cdd server is not connected: spawn failed' }, 503)
      const page = new BoardPage(server.send)
      await page.reader.refresh()
      expect(page.store.state.serverFailure).toBe('The cdd server is not connected: spawn failed')
    })

    it('should drop the band when cdd answers again', async () => {
      const { page } = pageOn(boardJson([discovery()]))
      page.store.change({ serverFailure: 'lost' })
      await page.reader.refresh()
      expect(page.store.state.serverFailure).toBeNull()
    })

    it('should read the board once to find that out', async () => {
      const { page, server } = pageOn(boardJson([discovery()]))
      page.store.change({ serverFailure: 'lost' })
      await page.reader.refresh()
      expect(server.requests).toHaveLength(1)
    })

    it('should say a chat route answering proves nothing about cdd', async () => {
      const { page, server } = pageOn(boardJson([discovery()]))
      server.answer('GET /api/chats', [])
      page.store.change({ serverFailure: 'lost' })
      await page.chat.refresh()
      expect(page.store.state.serverFailure).toBe('lost')
    })

    describe('with a tool failing', () => {
      async function failed() {
        const server = new FakeServer().answer('GET /api/board', { error: 'cdd board.show failed: bad' }, 502)
        const page = new BoardPage(server.send)
        await page.reader.refresh()
        return page
      }

      it('should show no band', async () => {
        expect((await failed()).store.state.serverFailure).toBeNull()
      })

      it('should show a toast', async () => {
        expect((await failed()).store.state.toasts.map(toast => toast.text)).toEqual(['cdd board.show failed: bad'])
      })
    })

    it('should show the band when the server itself does not answer', async () => {
      const page = new BoardPage(() => Promise.reject(new TypeError('failed to fetch')))
      await page.reader.refresh()
      expect(page.store.state.serverFailure).toContain('not answering')
    })
  })

  describe('Refresh Board After Tool Calls', () => {
    it('should keep the newer board when an older read answers late', async () => {
      const older = boardJson([discovery([ticketJson('older')])])
      const newer = boardJson([discovery([ticketJson('newer')])])
      const answers: ((response: Response) => void)[] = []
      const page = new BoardPage(() => new Promise(resolve => answers.push(resolve)))
      const first = page.reader.refresh()
      const second = page.reader.refresh()
      answers[1]!(new Response(JSON.stringify(newer)))
      await second
      answers[0]!(new Response(JSON.stringify(older)))
      await first
      expect(page.board.tickets.map(ticket => ticket.name)).toEqual(['newer'])
    })
  })

  describe('Announce Ticket Changes', () => {
    it('should name the new column of a ticket that moves', () => {
      const before = boardJson([discovery([ticketJson('sign-up', { title: 'Sign up' })])])
      const after = boardJson([{ ...discovery(), name: 'Discovery', done: [ticketJson('sign-up', { title: 'Sign up', is_done: true })] }])
      expect(announcementsOf(before, after)).toEqual(['Sign up moved to Discovery · Done'])
    })

    it('should name a fidelity that was reviewed', () => {
      const before = boardJson([discovery([ticketJson('sign-up')])])
      const after = boardJson([discovery([ticketJson('sign-up', { progress: { 'stories-story_map': 'done' } })])])
      expect(announcementsOf(before, after)).toEqual(['stories-story_map reviewed on sign-up'])
    })

    it('should say a ticket moved to the Backlog', () => {
      const before = boardJson([discovery([ticketJson('sign-up', { title: 'Sign up' })])])
      const after = boardJson([discovery()], null, [{ title: 'Sign up', text: '', path: '.sessions/_backlog/sign-up.md', last_activity: '' }])
      expect(announcementsOf(before, after)).toEqual(['Sign up moved to Backlog'])
    })

    it('should raise nothing on each read of a session open and closed under one name', () => {
      const closed = { ...ticketJson('sign-up', { column: 'Complete' }) }
      const shown = { ...boardJson([discovery([ticketJson('sign-up')])]) }
      shown.columns.at(-1)!.tickets = [closed]
      expect(announcementsOf(shown, shown)).toEqual([])
    })

    it('should raise nothing on the first read', async () => {
      const { page, server } = pageOn(null)
      server.answer('GET /api/board', boardJson([discovery([ticketJson('sign-up')])]))
      await page.reader.refresh()
      expect(page.store.state.toasts).toEqual([])
    })
  })
})

describe('Arrange Board And Details', () => {
  describe('Resize Board And Details', () => {
    it('should give the board the height a drag asks for', () => {
      const { page } = pageOn(null)
      page.layout.setBoardHeight(300, 900)
      expect(page.store.state.boardHeight).toBe(300)
    })

    it('should not let a drag close the board', () => {
      const { page } = pageOn(null)
      page.layout.setBoardHeight(10, 900)
      expect(page.store.state.boardHeight).toBe(160)
    })

    it('should not let a drag close the details', () => {
      const { page } = pageOn(null)
      page.layout.setBoardHeight(5000, 900)
      expect(page.store.state.boardHeight).toBe(650)
    })
  })

  describe('Expand Board Or Details', () => {
    it('should give one region the page', () => {
      const { page } = pageOn(null)
      page.layout.toggleRegion('board')
      expect(page.store.state.expandedRegion).toBe('board')
    })

    it('should bring the other back on a second press', () => {
      const { page } = pageOn(null)
      page.layout.toggleRegion('board')
      page.layout.toggleRegion('board')
      expect(page.store.state.expandedRegion).toBeNull()
    })
  })
})

describe('Set Stage WIP Limit', () => {
  it('should save a whole number', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    server.answer('POST /api/board/wip-limit', {})
    await page.board.setWipLimit('Discovery', '4')
    expect(server.posted('/api/board/wip-limit')[0]?.body).toEqual({ stage: 'Discovery', limit: 4 })
  })

  it('should read the board again', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    server.answer('POST /api/board/wip-limit', {})
    await page.board.setWipLimit('Discovery', '4')
    expect(server.requests.at(-1)?.path).toBe('/api/board')
  })

  it('should change nothing for a limit that is not a number', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    await page.board.setWipLimit('Discovery', 'many')
    expect(server.requests).toEqual([])
  })

  it('should send the header the server asks of a page on this machine', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    server.answer('POST /api/board/wip-limit', {})
    await page.board.setWipLimit('Discovery', '4')
    expect(server.posted('/api/board/wip-limit')[0]?.headers['X-CDD-Board']).toBe('1')
  })
})

describe('Display Ticket Details', () => {
  it('should show the active ticket with no card pressed', () => {
    const { page } = pageOn(boardJson([discovery([ticketJson('older'), ticketJson('sign-up')])], 'sign-up'))
    expect(page.board.selectedTicket?.name).toBe('sign-up')
  })

  it('should show the ticket worked on last with none active', () => {
    const { page } = pageOn(boardJson([discovery([ticketJson('older'), ticketJson('sign-up', { last_activity: '2026-11-02T10:00:00Z' })])]))
    expect(page.board.selectedTicket?.name).toBe('sign-up')
  })

  it('should tell a closed session from an open one of the same name', () => {
    const shown = boardJson([discovery([ticketJson('sign-up')])], 'sign-up')
    shown.columns.at(-1)!.tickets = [ticketJson('sign-up', { column: 'Complete' })]
    const { page } = pageOn(shown)
    page.board.select('Complete/sign-up')
    expect(page.board.selectedTicket?.column).toBe('Complete')
  })
})

describe('Display Ticket Card', () => {
  const HOUR = 3_600_000
  const STAMP = '2026-11-01T10:00:00Z'

  it('should say one hour in the singular', () => {
    expect(ageOf(Date.parse(STAMP) + HOUR, STAMP)).toBe('1 hour ago')
  })

  it('should say how many hours ago its ticket was worked on', () => {
    expect(ageOf(Date.parse(STAMP) + 13 * HOUR, STAMP)).toBe('13 hours ago')
  })

  it('should say a ticket with no activity has none', () => {
    expect(ageOf(Date.parse(STAMP), '')).toBe('no activity yet')
  })
})
