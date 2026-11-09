import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { BoardData } from '@cdd/space/kanban/board'

import { BoardPage } from './board-page'

// A cdd server that has not answered yet: every request the page sends stays pending, and each one is counted.
function slowServer() {
  const asked: string[] = []
  const send = (path: string) => {
    asked.push(path)
    return new Promise<Response>(() => undefined)
  }
  return { asked, send }
}

describe('Board Page', () => {
  beforeEach(() => vi.useFakeTimers())
  afterEach(() => vi.useRealTimers())

  // Each pending poll holds a connection on the cdd server, so a slow server must not collect one per tick.
  describe('that polls the chats while the cdd server answers slowly', () => {
    it('should ask for the build again only once the last answer came back', () => {
      const server = slowServer()
      const stop = new BoardPage(server.send).start()
      vi.advanceTimersByTime(20_000)
      stop()
      expect(server.asked.filter(path => path.endsWith('/build')).length).toBe(1)
    })
  })

  // The views read the board many times in one render, so one read of the board is one tree of clients, made once.
  describe('that has read one board', () => {
    function readPage(): BoardPage {
      const page = new BoardPage(slowServer().send)
      page.store.change({ board: boardRead() })
      return page
    }

    it('should answer the same board while the board read is unchanged', () => {
      const page = readPage()
      expect(page.board).toBe(page.board)
    })

    it('should answer a new board once the board is read again', () => {
      const page = readPage()
      const before = page.board
      page.store.change({ board: boardRead() })
      expect(page.board).not.toBe(before)
    })

    it('should answer the same practice each time it is named', () => {
      const page = readPage()
      expect(page.board.practiceNamed('stories')).toBe(page.board.practiceNamed('stories'))
    })

    it('should answer the same ticket each time it is listed', () => {
      const page = readPage()
      expect(page.board.tickets[0]).toBe(page.board.tickets[0])
    })

    it("should answer the same progress each time a ticket's fidelity is named", () => {
      const ticket = readPage().board.tickets[0]!
      expect(ticket.progressNamed('stories-story-map')).toBe(ticket.progressNamed('stories-story-map'))
    })
  })
})

// One board read as Python sends it, cut down to what the page's clients read: one stage holding one ticket with one
// fidelity's progress, and one practice.
function boardRead(): BoardData {
  const progress = { fidelity: { slug: 'stories-story-map' }, stage: { name: 'Discovery' }, state: 'not_started', is_enabled: true }
  const ticket = { name: 'sign-up', title: 'Sign up', column: { name: 'Discovery' }, progress: [progress], stage_work: [], next: null }
  const practice = { key: 'stories', slug: 'stories', short_name: 'Stories', colour: '#000' }
  return {
    project: 'shop',
    practices: [practice],
    fidelities: [{ fidelity: { slug: 'stories-story-map' }, practice: { key: 'stories' }, label: 'Story map', skill: '/x' }],
    open_tickets: [],
    active: null,
    columns: [{ name: 'Discovery', kind: 'stage', in_progress: [ticket], done: [] }],
  } as unknown as BoardData
}
