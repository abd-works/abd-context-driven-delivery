import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardOnProject, ticketOn } from 'test-utils/board-page-support'

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
    expect(ticketOn(page, OTHER).nextNote).toBe('Next: stories-story-map, generate')
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

  it('should keep a practice with two words in its skill', async () => {
    const { page } = await board.page()
    expect(page.board.fidelityShown('clean-engineering-code')?.skill).toBe('/practices-clean-engineering-clean-engineering-code')
  })

  it("should name a fidelity's tile as the catalog names it", async () => {
    const { page } = await board.page()
    expect(page.board.fidelityShown('ux-ia')?.label).toBe('information-architecture')
  })
})

describe('Display Child Tickets In Parent', () => {
  function writeChild(name: string, fields: Record<string, unknown> = {}): void {
    board.write(`.sessions/${name}/session.json`, JSON.stringify({ name, title: name, scope: 'story', parent: ACTIVE, workpath: board.root, repo_path: board.root, ...fields }))
    board.write(`.sessions/${name}/session.log`, '')
  }

  it("should give a parent its children as the page's tickets", async () => {
    writeChild('confirm-order')
    const { page } = await board.page()
    expect(ticketOn(page, ACTIVE).childTickets.map(child => [child.name, child.isStacked])).toEqual([['confirm-order', true]])
  })

  it('should find a child stacked in its parent by its address, though no column shows it', async () => {
    writeChild('confirm-order')
    const { page } = await board.page()
    expect(page.board.ticketAt('Discovery/confirm-order')?.name).toBe('confirm-order')
  })

  it('should fold a parent to its own card and show its children again', async () => {
    writeChild('confirm-order')
    const { page } = await board.page()
    const parent = ticketOn(page, ACTIVE)
    page.cards.toggleChildrenOf(parent)
    const folded = page.cards.showsChildrenOf(parent)
    page.cards.toggleChildrenOf(parent)
    expect([folded, page.cards.showsChildrenOf(parent)]).toEqual([false, true])
  })
})

describe('Expand Ticket From Empty Area', () => {
  it('should open the card and leave it open when pressed again', async () => {
    const { page } = await board.page()
    page.cards.open(ticketOn(page, OTHER))
    page.cards.open(ticketOn(page, OTHER))
    expect([page.store.state.openCard, page.store.state.selected]).toEqual([OTHER, 'Discovery/billing-report'])
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

  it('should name validate on held violations', async () => {
    const { page } = await board.page()
    expect(ticketOn(page, ACTIVE).runNextLabel).toBe('Run next: validate')
  })

  describe('with generate next', () => {
    async function ran() {
      await board.activate(OTHER)
      const { page, asked } = await board.page()
      const chat = await board.connectChat(page)
      await ticketOn(page, OTHER).runNext()
      return { asked, chat }
    }

    it('should send the generate command in the default format', async () => {
      const { chat } = await ran()
      expect(await chat.checkIn()).toEqual([{ kind: 'command', text: '/actions-generate stories-story-map session=.sessions/billing-report/session.json' }])
    })
  })

  // Run next reaches back to an earlier stage's unfinished fidelity, whose default format is that stage's, not the
  // ticket's own.
  describe('with generate next on a fidelity of a stage the ticket has moved past', () => {
    async function ran() {
      board.logOn(OTHER, 'move Specification')
      await board.activate(OTHER)
      const { page } = await board.page()
      const chat = await board.connectChat(page)
      await ticketOn(page, OTHER).runNext()
      return { page, chat }
    }

    it("should generate it in its own stage's default format", async () => {
      const { chat } = await ran()
      expect(await chat.checkIn()).toEqual([{ kind: 'command', text: '/actions-generate stories-story-map session=.sessions/billing-report/session.json' }])
    })

    it('should mark its tile as the next one', async () => {
      const { page } = await ran()
      expect(ticketOn(page, OTHER).progressNamed('stories-story-map')!.isNext).toBe(true)
    })
  })

  it('should fill the prompt on validate', async () => {
    await board.activate('back-to-backlog')
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
    await board.activate(OTHER)
    const { page } = await board.page()
    expect(ticketOn(page, OTHER).canRunNext).toBe(false)
  })
})

describe('Choose Ticket Practices', () => {
  async function turnedOff() {
    const { page } = await board.page()
    const discovery = page.board.stageNamed('Discovery')!
    const boundedContext = discovery.workRequired.find(fidelity => fidelity.slug === 'ddd-bounded-context')!
    page.store.change({ tiles: [{ ticket: ticketOn(page, ACTIVE), place: 'cell-Discovery-ddd-bounded-context', stage: discovery, fidelities: [boundedContext], action: 'generate', isPinned: true, choices: [] }] })
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
    expect(await chat.checkIn()).toEqual([{ kind: 'fill', text: 'Write a handoff for ticket checkout-flow with /space-session-handoff-session session=.sessions/checkout-flow/session.json' }])
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
    expect(await chat.checkIn()).toEqual([{ kind: 'command', text: '/space:session:close-session session=.sessions/checkout-flow/session.json' }])
  })

  it('should leave the ticket in its column', async () => {
    const { page } = await closed()
    expect(ticketOn(page, ACTIVE).column.name).toBe('Discovery')
  })
})

// A ticket's chat is the chat working in the ticket's worktree, so a person clicking the ticket sends to it.
describe('Open Ticket Chat', () => {
  describe("with a chat working in the ticket's worktree", () => {
    async function clicked() {
      const { page } = await board.page()
      await board.connectChat(page, 'other-chat')
      const worktree = board.openWorktree(ACTIVE)
      await board.chat('ticket-chat', 'abd · first words', worktree).checkIn()
      await page.chat.refresh()
      await page.reader.refresh()
      await ticketOn(page, ACTIVE).choose()
      return page
    }

    it("should send the board's commands to that chat", async () => {
      expect((await clicked()).store.state.targetChat).toBe('ticket-chat')
    })

    it('should list that chat by its own name', async () => {
      const page = await clicked()
      const chat = page.store.state.chats.find(entry => entry.id === 'ticket-chat')!
      expect(page.chatName(chat)).toBe('abd · first words')
    })
  })

  // A chat a person picks while the ticket is selected is assigned to it, in place of the one in its worktree.
  describe('with another chat picked while the ticket is selected', () => {
    async function pickedThenClicked() {
      const { page } = await board.page()
      await board.connectChat(page, 'other-chat')
      const worktree = board.openWorktree(ACTIVE)
      await board.chat('ticket-chat', 'abd · first words', worktree).checkIn()
      await page.chat.refresh()
      await page.reader.refresh()
      await ticketOn(page, ACTIVE).choose()
      await page.pickChat('other-chat')
      await ticketOn(page, ACTIVE).choose()
      return page
    }

    it('should choose the picked chat again when the ticket is clicked', async () => {
      expect((await pickedThenClicked()).store.state.targetChat).toBe('other-chat')
    })

    it("should send the ticket's commands to the picked chat", async () => {
      const page = await pickedThenClicked()
      const other = board.chat('other-chat', '', '')
      await ticketOn(page, ACTIVE).closeSession()
      expect(await other.checkIn()).toEqual([{ kind: 'command', text: '/space:session:close-session session=.sessions/checkout-flow/session.json' }])
    })
  })

  // A person can act on a ticket from its card or its report without clicking the ticket first.
  describe('with another chat picked last', () => {
    async function closedWithoutClicking() {
      const { page } = await board.page()
      await board.connectChat(page, 'other-chat')
      const worktree = board.openWorktree(ACTIVE)
      const ticketChat = board.chat('ticket-chat', 'abd · first words', worktree)
      await ticketChat.checkIn()
      await page.chat.refresh()
      await page.reader.refresh()
      page.chat.choose('other-chat')
      await ticketOn(page, ACTIVE).closeSession()
      return ticketChat
    }

    it("should send the ticket's command to the ticket's chat", async () => {
      expect(await (await closedWithoutClicking()).checkIn()).toEqual([{ kind: 'command', text: '/space:session:close-session session=.sessions/checkout-flow/session.json' }])
    })
  })

  // A chat's working folder can move into a folder of its checkout, and it still works on that checkout's ticket.
  describe("with a chat working in a folder inside the ticket's worktree", () => {
    it("should send the board's commands to that chat", async () => {
      const { page } = await board.page()
      await board.connectChat(page, 'other-chat')
      const worktree = board.openWorktree(ACTIVE)
      await board.chat('ticket-chat', 'abd · first words', `${worktree}\\harness\\kanban`).checkIn()
      await page.chat.refresh()
      await page.reader.refresh()
      await ticketOn(page, ACTIVE).choose()
      expect(page.store.state.targetChat).toBe('ticket-chat')
    })
  })

  // A chat whose mod is older than the folder it works in sends none; the board titled it by its ticket when it opened it.
  describe("with a chat titled by the ticket that names no folder", () => {
    async function clicked() {
      const { page } = await board.page()
      await board.connectChat(page, 'other-chat')
      board.openWorktree(ACTIVE)
      await board.chat('ticket-chat', ACTIVE, '').checkIn()
      await page.chat.refresh()
      await page.reader.refresh()
      await ticketOn(page, ACTIVE).choose()
      return { page, opened: board.openedChats() }
    }

    it("should send the board's commands to that chat", async () => {
      expect((await clicked()).page.store.state.targetChat).toBe('ticket-chat')
    })

    it('should open no new chat', async () => {
      expect((await clicked()).opened).toHaveLength(0)
    })
  })

  // A press only selects: it opens no worktree and no chat, and with no chat on the ticket nothing is sent until one is.
  describe("with no chat working on the ticket and none picked", () => {
    it('should open no worktree and no chat on a press', async () => {
      const { page } = await board.page()
      await ticketOn(page, ACTIVE).choose()
      expect([ticketOn(page, ACTIVE).worktree, board.openedChats()]).toEqual(['', []])
    })

    it("should send none of the ticket's commands and ask for its chat", async () => {
      const { page, asked } = await board.page()
      await board.chat('chat-1').checkIn()
      await page.chat.refresh()
      await ticketOn(page, ACTIVE).fillHandoff()
      expect([asked.filter(request => request.path.endsWith('/send')), page.store.state.toasts.at(-1)?.text]).toEqual([[], 'No chat works on checkout-flow yet: open its chat from its card, or pick one in the chat list.'])
    })
  })

  // Python's chat.open hands the Claude app a claude://code/new link on a folder; the person confirms the folder and sends.
  describe("with no chat working in the ticket's worktree, and its chat opened", () => {
    async function clicked(times = 1) {
      const { page } = await board.page()
      const worktree = board.openWorktree(ACTIVE)
      await page.reader.refresh()
      for (let click = 0; click < times; click++) await ticketOn(page, ACTIVE).openChat()
      return { worktree, opened: board.openedChats() }
    }

    it("should open a new chat on the ticket's worktree", async () => {
      const { worktree, opened } = await clicked()
      expect(new URL(opened[0]!).searchParams.get('folder')).toBe(worktree)
    })

    it("should ask the new chat to take the ticket's name as its title", async () => {
      const { opened } = await clicked()
      expect(new URL(opened[0]!).searchParams.get('q')).toContain(`Title this session "${ACTIVE}"`)
    })

    // Its chat bar, its log and every tool it calls work on the ticket from its first turn, not on main.
    it("should ask the new chat to open the ticket's session first", async () => {
      const { opened } = await clicked()
      expect(new URL(opened[0]!).searchParams.get('q')).toContain(`First call sessions.switch with name ${ACTIVE}`)
    })

    // Opening the worktree and the Claude app takes a while, so the click shows at once that the chat is on its way.
    it("should show the ticket's chat as opening", async () => {
      const { page } = await board.page()
      board.openWorktree(ACTIVE)
      await page.reader.refresh()
      await ticketOn(page, ACTIVE).openChat()
      expect(page.chat.isOpeningFor(ACTIVE)).toBe(true)
    })

    it('should open it only once while that chat starts', async () => {
      expect((await clicked(2)).opened).toHaveLength(1)
    })
  })

  describe('with a ticket that has no worktree yet', () => {
    async function clicked() {
      const { page } = await board.page()
      await ticketOn(page, ACTIVE).openChat()
      return { page, opened: board.openedChats() }
    }

    it('should open its worktree', async () => {
      const { page } = await clicked()
      expect(ticketOn(page, ACTIVE).worktree).not.toBe('')
    })

    it('should open the new chat on that worktree', async () => {
      const { page, opened } = await clicked()
      expect(new URL(opened[0]!).searchParams.get('folder')).toBe(ticketOn(page, ACTIVE).worktree)
    })
  })

  // A ticket in Complete has closed its work, so clicking it opens no branch, worktree, or chat for it.
  describe('with a ticket in Complete', () => {
    it('should open no new chat', async () => {
      const { page } = await board.page()
      await page.board.tickets.find(ticket => ticket.name === 'shipped-work')!.openChat()
      expect(board.openedChats()).toEqual([])
    })
  })
})
