import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardOnProject, ticketOn } from 'test-utils/board-page-support'

import { skillOf } from './ticket-client'

// checkout-flow is the active ticket, held by a violation on its story map; billing-report has nothing recorded yet.
const ACTIVE = 'checkout-flow'
const OTHER = 'billing-report'

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

describe('Restrict Actions To Active Session', () => {
  it('should lock a ticket that is not the active session', async () => {
    const { page } = await board.page()
    expect(ticketOn(page, OTHER).isLocked).toBe(true)
  })

  it('should leave the active ticket open', async () => {
    const { page } = await board.page()
    expect(ticketOn(page, ACTIVE).isLocked).toBe(false)
  })

  it('should unlock every ticket with Active session only off', async () => {
    const { page } = await board.page()
    page.layout.toggleOnlyActive()
    expect(ticketOn(page, OTHER).isLocked).toBe(false)
  })
})

describe('Display Ticket Details', () => {
  it('should say what runs next', async () => {
    const { page } = await board.page()
    expect(ticketOn(page, OTHER).nextNote).toBe('Next: stories-story_map, generate')
  })

  it('should say another session must be activated to run it', async () => {
    const { page } = await board.page()
    expect(ticketOn(page, OTHER).lockNote).toBe('Activate this session to run actions')
  })

  it('should name a split ticket by its parent', async () => {
    board.write('.sessions/child/session.json', JSON.stringify({ name: 'child', title: 'Child', scope: 'story', parent: 'epic', workpath: board.root, repo_path: board.root }))
    board.write('.sessions/child/session.log', '')
    const { page } = await board.page()
    expect(ticketOn(page, 'child').origin).toBe('story of epic')
  })

  it("should name the ticket's stage and how far it has got there", async () => {
    const { page } = await board.page()
    expect(ticketOn(page, OTHER).stagePlace).toBe('Discovery · in progress')
  })

  it('should keep a practice with two words in its skill', () => {
    expect(skillOf('clean_engineering-code')).toBe('/practices-clean-engineering-clean-engineering-code')
  })
})

describe('Review Fidelity', () => {
  describe('with a story map that has passed validate', () => {
    async function validated() {
      board.logOn(OTHER, 'generate /work stories story_map markdown stories', 'validate Stories story_map')
      const { page } = await board.page()
      page.layout.toggleOnlyActive()
      return page
    }

    it('should offer the review with no chat connected, since it is the person\'s own approval', async () => {
      expect(ticketOn(await validated(), OTHER).canRunNext).toBe(true)
    })

    it('should show the review done once Run next records it', async () => {
      const page = await validated()
      await ticketOn(page, OTHER).runNext()
      expect(ticketOn(page, OTHER).actionsOf('stories-story_map').review).toBe('done')
    })
  })
})

describe('Move Ticket', () => {
  it('should read the board again and select the ticket where it landed', async () => {
    const { page } = await board.page()
    await ticketOn(page, 'ready-to-move').moveNext()
    expect(page.store.state.selected).toBe('Specification/ready-to-move')
  })

  it('should select a dragged ticket in the stage it was dropped on', async () => {
    const { page } = await board.page()
    await ticketOn(page, 'move-me').moveTo('Implementation', true)
    expect(page.store.state.selected).toBe('Implementation/move-me')
  })

  describe('that a person has moved to the Backlog', () => {
    async function moved() {
      const { page } = await board.page()
      page.store.change({ openCard: 'back-to-backlog' })
      await ticketOn(page, 'back-to-backlog').movePrevious()
      return page
    }

    it('should let go of what was open on it', async () => {
      expect((await moved()).store.state.openCard).toBeNull()
    })

    it('should select its item', async () => {
      expect((await moved()).store.state.selected).toBe('Backlog/Back to backlog')
    })
  })

  it('should let a ticket in any column be dropped on the Backlog', async () => {
    const { page } = await board.page()
    await ticketOn(page, 'almost-shipped').dropOn('Backlog')
    expect(page.board.backlogItems.map(item => item.title)).toContain('Almost shipped')
  })

  it('should let only the active ticket, or one done in Implementation, be dropped on Complete', async () => {
    const { page } = await board.page()
    expect([ticketOn(page, ACTIVE).canDropOn('Complete'), ticketOn(page, 'almost-shipped').canDropOn('Complete'), ticketOn(page, OTHER).canDropOn('Complete')]).toEqual([true, true, false])
  })
})

describe('Send Next Fidelity Action', () => {
  it('should name the step that runs next', async () => {
    const { page } = await board.page()
    expect(ticketOn(page, OTHER).runNextLabel).toBe('Run next: generate')
  })

  it('should say fix violations on held violations', async () => {
    const { page } = await board.page()
    expect(ticketOn(page, ACTIVE).runNextLabel).toBe('Run next: fix violations')
  })

  describe('with generate next', () => {
    async function ran() {
      board.activate(OTHER)
      const { page, asked } = await board.page()
      const chat = await board.connectChat(page)
      await ticketOn(page, OTHER).runNext()
      return { asked, chat }
    }

    it('should ask for the commands of the default format', async () => {
      const { asked } = await ran()
      expect(asked.find(request => request.path === `/api/ticket/${OTHER}/generate-commands`)?.body).toEqual({ fidelities: ['stories-story_map'], formats: ['markdown'] })
    })

    it('should send those commands in order', async () => {
      const { chat } = await ran()
      expect(await chat.checkIn()).toEqual([{ kind: 'command', text: '/actions-generate stories-story-map format=markdown session=.sessions/billing-report/session.json' }])
    })
  })

  // Run next reaches back to an earlier stage's unfinished fidelity, whose default format is that stage's, not the
  // ticket's own.
  describe('with generate next on a fidelity of a stage the ticket has moved past', () => {
    async function ran() {
      board.logOn(OTHER, 'move Specification')
      board.activate(OTHER)
      const { page } = await board.page()
      const chat = await board.connectChat(page)
      await ticketOn(page, OTHER).runNext()
      return { page, chat }
    }

    it("should generate it in its own stage's default format", async () => {
      const { chat } = await ran()
      expect(await chat.checkIn()).toEqual([{ kind: 'command', text: '/actions-generate stories-story-map format=markdown session=.sessions/billing-report/session.json' }])
    })

    it('should mark its tile as the next one', async () => {
      const { page } = await ran()
      const discovery = page.board.stageNamed('Discovery')!
      expect(ticketOn(page, OTHER).isNext(discovery, 'stories-story_map')).toBe(true)
    })
  })

  it('should fill the prompt on validate', async () => {
    board.activate('back-to-backlog')
    const { page } = await board.page()
    const chat = await board.connectChat(page)
    await ticketOn(page, 'back-to-backlog').runNext()
    expect(await chat.checkIn()).toEqual([{ kind: 'fill', text: '/actions-validate stories-story-map session=.sessions/back-to-backlog/session.json' }])
  })

  describe('with violations held and no chat connected', () => {
    it('should still offer Run next', async () => {
      const { page } = await board.page()
      expect(ticketOn(page, ACTIVE).canRunNext).toBe(true)
    })

    it('should open the report', async () => {
      const { page } = await board.page()
      await ticketOn(page, ACTIVE).runNext()
      expect(page.store.state.panels.map(panel => panel.kind)).toEqual(['report'])
    })
  })

  it('should stay off with no chat to send to', async () => {
    board.activate(OTHER)
    const { page } = await board.page()
    expect(ticketOn(page, OTHER).canRunNext).toBe(false)
  })
})

describe('Choose Ticket Practices', () => {
  async function turnedOff() {
    const { page } = await board.page()
    page.store.change({ tiles: [{ ticket: ACTIVE, place: 'cell-Discovery-ddd-bounded_context', stage: 'Discovery', slugs: ['ddd-bounded_context'], action: 'generate', picked: [], isPinned: true, files: {} }] })
    await ticketOn(page, ACTIVE).enablePractice('ddd', false)
    return page
  }

  it('should let go of the tile of a practice turned off', async () => {
    expect((await turnedOff()).store.state.tiles).toEqual([])
  })

  it('should say so and where it was saved', async () => {
    expect((await turnedOff()).store.state.toasts[0]?.text).toBe('DDD off for Checkout flow · saved to .sessions/checkout-flow/session.json')
  })
})

describe('Write Ticket Handoff', () => {
  it('should fill the prompt with the handoff command', async () => {
    const { page } = await board.page()
    const chat = await board.connectChat(page)
    await ticketOn(page, ACTIVE).fillHandoff()
    expect(await chat.checkIn()).toEqual([{ kind: 'fill', text: 'Write a handoff for ticket checkout-flow with /space-handoff-handoff-session.' }])
  })
})

describe('Close Active Session', () => {
  async function closed() {
    const { page } = await board.page()
    const chat = await board.connectChat(page)
    await ticketOn(page, ACTIVE).closeSession()
    return { page, chat }
  }

  it('should send the close session command to the chat', async () => {
    const { chat } = await closed()
    expect(await chat.checkIn()).toEqual([{ kind: 'command', text: '/space:session:close-session' }])
  })

  it('should leave the ticket in its column', async () => {
    const { page } = await closed()
    expect(ticketOn(page, ACTIVE).column).toBe('Discovery')
  })
})
