import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { CddConnection } from '@cdd/cdd-connection'
import { BoardAdapter } from '@cdd/space/kanban/board'
import { TicketAdapter } from '@cdd/space/kanban/ticket'
import { BoardOnProject, RunningBoard, ticketOn } from 'test-utils/board-page-support'

import type { Send } from './board-api'
import { ageOf } from '../shared/board-brand'

const WAIT_MILLISECONDS = 10

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

const until = async (isReady: () => boolean): Promise<void> => {
  while (!isReady()) await new Promise(done => setTimeout(done, WAIT_MILLISECONDS))
}

const toastsOf = (page: { store: { state: { toasts: { text: string }[] } } }): string[] => page.store.state.toasts.map(toast => toast.text)

// A session closed under the name of one still open.
const closedTwinOf = (name: string, title: string) => board.writeSession({ name, title, folder: join('_complete', name) })

describe('Display Board', () => {
  describe('Display Connected Status', () => {
    it('should show a band when the board read answers that cdd is not connected', async () => {
      const lost = new CddConnection(join(tmpdir(), 'cdd-board-page-no-such-project'))
      const unreachable = await RunningBoard.on(lost)
      const { page } = unreachable.unreadPage()
      await page.reader.refresh()
      await unreachable.close()
      await lost.close()
      expect(page.store.state.serverFailure).toContain('The cdd server is not connected')
    })

    it('should drop the band when cdd answers again', async () => {
      const { page } = await board.page()
      page.store.change({ serverFailure: 'lost' })
      await page.reader.refresh()
      expect(page.store.state.serverFailure).toBeNull()
    })

    it('should read the board once to find that out', async () => {
      const { page, asked } = await board.page()
      page.store.change({ serverFailure: 'lost' })
      await page.reader.refresh()
      expect(asked).toHaveLength(1)
    })

    it('should drop the band when the chat list answers, because the chats are read through cdd', async () => {
      const { page } = await board.page()
      page.store.change({ serverFailure: 'lost' })
      await page.chat.refresh()
      expect(page.store.state.serverFailure).toBeNull()
    })

    describe('with a tool failing', () => {
      async function failed() {
        board.write('.sessions/broken/session.json', '{not json')
        const { page } = board.unreadPage()
        await page.reader.refresh()
        return page
      }

      it('should show no band', async () => {
        expect((await failed()).store.state.serverFailure).toBeNull()
      })

      it('should show a toast', async () => {
        // The session names its unreadable session.json, whose folder is the throwaway project's own.
        const [toast, ...others] = toastsOf(await failed())
        expect([toast, others]).toEqual([expect.stringMatching(/^cdd board\.show failed: JsonFileUnreadable: .*[\\/]\.sessions[\\/]broken[\\/]session\.json is not a readable JSON object \(Expecting property name/), []])
      })
    })

    describe('that a person has pressed Update', () => {
      const updated = async () => {
        const { page } = await board.page()
        page.pause = async () => undefined
        await page.update()
        return page
      }

      // The installer gets the latest code, pins cdd to it, and rebuilds the page, so an install outside the board
      // rebuilds it too.
      it('should have the installer get the latest code, pin cdd to it, and rebuild the page', async () => {
        await updated()
        expect(board.board.updates.steps).toEqual([expect.stringMatching(/scripts\/install\.py --ide Claude --update$/)])
      })

      it('should restart the board server once the update has answered', async () => {
        await updated()
        await until(() => board.board.updates.restarts === 1)
        expect(board.board.updates.restarts).toBe(1)
      })

      it('should load the page again from the restarted server', async () => {
        expect((await updated()).store.state.isNewBuild).toBe(true)
      })

      describe('with a step that fails', () => {
        beforeEach(() => {
          board.board.updates.failingStep = '--update'
        })

        it('should say in a toast which step failed', async () => {
          expect(toastsOf(await updated()).at(-1)).toBe('Update failed at get latest and re-pin: --update could not run')
        })

        it('should keep the page it has', async () => {
          expect((await updated()).store.state.isNewBuild).toBe(false)
        })

        it('should keep the board server running', async () => {
          await updated()
          expect(board.board.updates.restarts).toBe(0)
        })
      })
    })

    it('should show the band when the server itself does not answer', async () => {
      const stopped = await RunningBoard.on(board.project.cdd)
      await stopped.close()
      const { page } = stopped.unreadPage()
      await page.reader.refresh()
      expect(page.store.state.serverFailure).toContain('not answering')
    })
  })

  describe('Refresh Board After Tool Calls', () => {
    it('should keep the newer board when an older read answers late', async () => {
      const held: (() => void)[] = []
      const holding =
        (send: Send): Send =>
        async (path, init) => {
          const answer = await send(path, init)
          await new Promise<void>(release => held.push(release))
          return answer
        }
      const { page } = board.unreadPage(holding)
      const older = page.reader.refresh()
      await until(() => held.length === 1)
      await new TicketAdapter(board.project.cdd, 'move-me').moveTo('Discovery', true)
      const newer = page.reader.refresh()
      await until(() => held.length === 2)
      held[1]!()
      await newer
      held[0]!()
      await older
      expect(ticketOn(page, 'move-me').isDone).toBe(true)
    })
  })

  describe('Announce Ticket Changes', () => {
    it('should name the new column of a ticket that moves', async () => {
      const { page } = await board.page()
      await new TicketAdapter(board.project.cdd, 'move-me').moveTo('Discovery', true)
      await page.reader.refresh()
      expect(toastsOf(page)).toEqual(['Move me moved to Discovery · Done'])
    })

    it('should name a fidelity that is done', async () => {
      const { page } = await board.page()
      board.logOn('billing-report', 'generate /work stories story_map markdown stories', 'validate Stories story_map')
      await page.reader.refresh()
      expect(toastsOf(page)).toEqual(['stories-story-map done on billing-report'])
    })

    it('should say a ticket moved to the Backlog', async () => {
      const { page } = await board.page()
      await new TicketAdapter(board.project.cdd, 'back-to-backlog').movePrevious()
      await page.reader.refresh()
      expect(toastsOf(page)).toEqual(['Back to backlog moved to Backlog'])
    })

    it('should raise nothing on each read of a session open and closed under one name', async () => {
      closedTwinOf('billing-report', 'Billing report')
      const { page } = await board.page()
      await page.reader.refresh()
      expect(page.store.state.toasts).toEqual([])
    })

    it('should raise nothing on the first read', async () => {
      const { page } = board.unreadPage()
      await page.reader.refresh()
      expect(page.store.state.toasts).toEqual([])
    })
  })
})

describe('Arrange Board And Details', () => {
  describe('Resize Board And Details', () => {
    it('should give the board the height a drag asks for', () => {
      const { page } = board.unreadPage()
      page.layout.setBoardHeight(300, 900)
      expect(page.store.state.boardHeight).toBe(300)
    })

    it('should not let a drag close the board', () => {
      const { page } = board.unreadPage()
      page.layout.setBoardHeight(10, 900)
      expect(page.store.state.boardHeight).toBe(160)
    })

    it('should not let a drag close the details', () => {
      const { page } = board.unreadPage()
      page.layout.setBoardHeight(5000, 900)
      expect(page.store.state.boardHeight).toBe(650)
    })
  })

  describe('Expand Board Or Details', () => {
    it('should give one region the page', () => {
      const { page } = board.unreadPage()
      page.layout.toggleRegion('board')
      expect(page.store.state.expandedRegion).toBe('board')
    })

    it('should bring the other back on a second press', () => {
      const { page } = board.unreadPage()
      page.layout.toggleRegion('board')
      page.layout.toggleRegion('board')
      expect(page.store.state.expandedRegion).toBeNull()
    })
  })
})

describe('Set Stage WIP Limit', () => {
  it('should save a whole number', async () => {
    const { page } = await board.page()
    await page.board.stageNamed('Discovery')!.submitWipLimit('4')
    const saved = await new BoardAdapter(board.project.cdd).show()
    expect(saved.columns.find(column => column.name === 'Discovery')?.wip_limit).toBe(4)
  })

  it('should read the board again', async () => {
    const { page } = await board.page()
    await page.board.stageNamed('Discovery')!.submitWipLimit('4')
    expect(page.board.stageNamed('Discovery')?.wipLimit).toBe(4)
  })

  it('should change nothing for a limit that is not a number', async () => {
    const { page, asked } = await board.page()
    await page.board.stageNamed('Discovery')!.submitWipLimit('many')
    expect(asked).toEqual([])
  })

  it('should send the header the server asks of a page on this machine', async () => {
    const { page } = await board.page()
    await page.board.stageNamed('Discovery')!.submitWipLimit('4')
    expect(page.store.state.toasts).toEqual([])
  })
})

describe('Display Ticket Details', () => {
  it('should show the active ticket with no card pressed', async () => {
    const { page } = await board.page()
    expect(page.board.selectedTicket?.name).toBe('checkout-flow')
  })

  it('should show main, the default session, with no other ticket opened', async () => {
    await board.activate(null)
    const { page } = await board.page()
    expect(page.board.selectedTicket?.name).toBe('main')
  })

  it('should tell a closed session from an open one of the same name', async () => {
    closedTwinOf('billing-report', 'Billing report')
    const { page } = await board.page()
    page.board.select('Complete/billing-report')
    expect(page.board.selectedTicket?.column.name).toBe('Complete')
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
