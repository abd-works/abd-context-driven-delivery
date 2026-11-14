import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import type { ReportRuleData } from '@cdd/space/kanban/ticket'
import { practicesOf, shownTabs } from '@src/kanban/ticket/files-panel-client'
import { BoardOnProject, ticketOn as shownTicket } from 'test-utils/board-page-support'
import type { FidelityProgressClient } from '@src/kanban/ticket/fidelity-progress-client'
import type { FilesByFidelity, TicketClient } from '@src/kanban/ticket/ticket-client'

import type { BoardPage } from './board-page'
import type { FilesPanel, ReportPanel } from '../shared/board-store'

// checkout-flow is the active ticket: its story map was validated with one rule broken on .context/story-map.md line 6.
const TICKET = 'checkout-flow'
const SESSION = 'session=.sessions/checkout-flow/session.json'
const SLUG = 'stories-story-map'
const REPORT_PATH = '.sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md'
const FAILING_LINE = 12
// A graph validate saved with no hits, in the shape harness/graph/saved_graph.py writes (SAVED_SHAPE_VERSION 3).
const CLEAN_GRAPH = { version: 3, overlays: [], practices: { stories: { source_root: '', root_facts: {}, nodes: [], edges: [], violations: [] } } }

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

const filesPanel = (page: BoardPage) => page.store.state.panels.find(panel => panel.kind === 'files') as FilesPanel
const reportPanel = (page: BoardPage) => page.store.state.panels.find(panel => panel.kind === 'report') as ReportPanel

// A panel holds the ticket it is about, as the board read shows it.
const ticketOn = (page: BoardPage): TicketClient => shownTicket(page, TICKET)

// The ticket's progress on its story map, whose report and files the panels show.
const storyMapOn = (page: BoardPage): FidelityProgressClient => ticketOn(page).progressNamed(SLUG)!

// A ticket the page still holds after the board stopped showing it: its tools name a ticket the board does not have.
const goneTicket = (page: BoardPage, name: string): TicketClient => {
  const shown = ticketOn(page).toJSON()
  const progress = shown.progress.map(entry => ({ ...entry, ticket: { name } }))
  return page.ticket({ ...shown, name, progress })
}

const EVERY_FORMAT = 'Fix every format of the fidelity: its documents, its diagrams, and its code.'

async function brokenRule(page: BoardPage): Promise<ReportRuleData> {
  await page.panels.openReport(ticketOn(page), storyMapOn(page))
  return reportPanel(page).report.rules[0]!
}

// A panel over two practices' fidelities, as the files panel holds it, for the filters' own specs.
const STORIES_FILES = { markdown: [{ path: 'stories/story-map.md', exists: true, is_changed: false }, { path: 'stories/checkout_story.test.md', exists: true, is_changed: true }] }
const BDD_FILES = { python: [{ path: 'src/order_spec.py', exists: true, is_changed: false }] }
const progressOf = (slug: string, practice: string) => ({ fidelity: { slug }, practice: { key: practice } }) as unknown as FidelityProgressClient
const twoPractices = (changes: Partial<FilesPanel> = {}): FilesPanel =>
  ({
    kind: 'files',
    source: 'fidelities',
    progress: [progressOf('stories-scenarios', 'stories'), progressOf('bdd-realization', 'bdd')],
    files: { 'stories-scenarios': STORIES_FILES, 'bdd-realization': BDD_FILES },
    practicesOn: ['stories'],
    changedOnly: false,
    activeTab: '',
    shown: null,
    lines: {},
    isExpanded: false,
    ...changes,
  }) as FilesPanel
const pathsOf = (panel: FilesPanel): string[] => shownTabs(panel).map(tab => tab.path)

describe('List Ticket Files', () => {
  it("should show a tab for each of the fidelity's files, with whether each exists", async () => {
    const { page } = await board.page()
    await page.files.openFiles(ticketOn(page), [storyMapOn(page)])
    expect(shownTabs(filesPanel(page)).map(tab => [tab.path, tab.exists])).toEqual([
      ['.context/story-map.md', true],
      ['.context/story-map.drawio', false],
    ])
  })

  it('should show the files of no other practice', async () => {
    const { page } = await board.page()
    await page.files.openFiles(ticketOn(page), [storyMapOn(page)])
    expect(shownTabs(filesPanel(page)).map(tab => tab.practice)).toEqual(['stories', 'stories'])
  })

  it('should show only the changed files while the changed filter is on', () => {
    expect(pathsOf(twoPractices({ changedOnly: true }))).toEqual(['stories/checkout_story.test.md'])
  })

  it('should show every file again once the changed filter is cleared', () => {
    expect(pathsOf(twoPractices({ changedOnly: false }))).toEqual(['stories/story-map.md', 'stories/checkout_story.test.md'])
  })

  describe('with a list that cannot be read', () => {
    async function refused() {
      const { page } = await board.page()
      const gone = goneTicket(page, 'no-such-ticket')
      await page.files.openFiles(gone, [gone.progressNamed(SLUG)!])
      return page
    }

    it('should say so in a toast', async () => {
      expect((await refused()).store.state.toasts[0]?.text).toBe("cdd fidelity-progress.files failed: TicketNotFoundError: no ticket named 'no-such-ticket' on the board")
    })

    it('should open no panel', async () => {
      expect((await refused()).store.state.panels).toEqual([])
    })
  })
})

describe('Browse Ticket Files By Practice', () => {
  it("should offer a filter for each practice of the ticket's stage", async () => {
    const { page } = await board.page()
    await page.files.openFiles(ticketOn(page), [storyMapOn(page)])
    expect(practicesOf(filesPanel(page))).toContain('stories')
  })

  it('should turn on only the practice of the fidelity the files were opened from', async () => {
    const { page } = await board.page()
    await page.files.openFiles(ticketOn(page), [storyMapOn(page)])
    expect(filesPanel(page).practicesOn).toEqual(['stories'])
  })

  it("should show a practice's files after the others once its filter is on", () => {
    expect(pathsOf(twoPractices({ practicesOn: ['stories', 'bdd'] }))).toEqual(['stories/story-map.md', 'stories/checkout_story.test.md', 'src/order_spec.py'])
  })

  it('should name each tab with the practice whose color it takes', () => {
    expect(shownTabs(twoPractices({ practicesOn: ['stories', 'bdd'] })).map(tab => tab.practice)).toEqual(['stories', 'stories', 'bdd'])
  })
})

describe("Browse Ticket's Session Folder", () => {
  it('should show every file in the session folder as a tab', async () => {
    const { page } = await board.page()
    await page.files.openSessionFolder(ticketOn(page))
    expect(pathsOf(filesPanel(page))).toContain(REPORT_PATH)
  })

  describe('with its latest handoff opened', () => {
    const HANDOFF = `.sessions/${TICKET}/handoff-20261101T120000.md`

    async function opened() {
      board.write(HANDOFF, '# Handoff\n')
      const { page } = await board.page()
      await page.files.openSessionFile(ticketOn(page), HANDOFF)
      return page
    }

    it('should show the handoff in a tab', async () => {
      expect(filesPanel(await opened()).activeTab).toBe(HANDOFF)
    })

    it("should read the handoff's text", async () => {
      expect(filesPanel(await opened()).shown?.text).toBe('# Handoff\n')
    })
  })
})

describe('View Fidelity Files', () => {
  it('should open the tabs in the order Python sends the formats', () => {
    const files: FilesByFidelity = { [SLUG]: { markdown: [{ path: 'a.md', exists: true, is_changed: false }], python: [{ path: 'c.py', exists: true, is_changed: false }], drawio: [{ path: 'b.drawio', exists: true, is_changed: false }] } }
    expect(pathsOf(twoPractices({ progress: [progressOf(SLUG, 'stories')], files }))).toEqual(['a.md', 'c.py', 'b.drawio'])
  })

  it('should read the file the first tab shows', async () => {
    const { page } = await board.page()
    await page.files.openFiles(ticketOn(page), [storyMapOn(page)])
    expect(filesPanel(page).shown?.text).toBe(['# Check Out Order', '', '## Payment', '', '- Enter Card Details', '- Handle Payment', '- Confirm Order', ''].join('\n'))
  })

  it('should show a file not generated yet as nothing to read', async () => {
    const { page } = await board.page()
    await page.files.openFiles(ticketOn(page), [storyMapOn(page)])
    await page.files.openTab('.context/story-map.drawio')
    expect(filesPanel(page).shown).toBeNull()
  })

  describe('with a violation in a file its fidelity does not declare', () => {
    async function opened() {
      board.write('src/other.py', 'x\n')
      const { page } = await board.page()
      await page.files.openFileAtLine(ticketOn(page), storyMapOn(page), 'src/other.py', FAILING_LINE)
      return page
    }

    it('should open that file', async () => {
      expect(filesPanel(await opened()).activeTab).toBe('src/other.py')
    })

    it('should mark the line it failed on', async () => {
      expect(filesPanel(await opened()).lines['src/other.py']).toBe(FAILING_LINE)
    })
  })
})

describe('Add Comment To File Selection', () => {
  async function commented() {
    const { page } = await board.page()
    await page.files.openFiles(ticketOn(page), [storyMapOn(page)])
    await page.files.addComment(3, 3, 'name the payment step after what the person does')
    return page
  }

  it('should show the comment on the open file, not sent', async () => {
    expect(filesPanel(await commented()).shown?.comments.map(comment => [comment.anchor, comment.state])).toEqual([['.context/story-map.md:L3-L3', 'not_sent']])
  })

  it('should take the comment away once deleted', async () => {
    const page = await commented()
    await page.files.removeComment('.context/story-map.md:L3-L3')
    expect(filesPanel(page).shown?.comments).toEqual([])
  })
})

describe('Save Edited File', () => {
  it('should show the file as saved', async () => {
    board.write('src/other.py', 'x\n')
    const { page } = await board.page()
    await page.files.openFileAtLine(ticketOn(page), storyMapOn(page), 'src/other.py', 1)
    await page.files.save('y\n')
    expect(filesPanel(page).shown?.text).toBe('y\n')
  })
})

describe('Open Validation Report', () => {
  it("should show that fidelity's latest report", async () => {
    const { page } = await board.page()
    await page.panels.openReport(ticketOn(page), storyMapOn(page))
    expect(reportPanel(page).report.path).toBe(REPORT_PATH)
  })

  it("should show every fidelity's violations with no fidelity named", async () => {
    const { page } = await board.page()
    await page.panels.openReport(ticketOn(page), null)
    expect(reportPanel(page).report.path).toBe('.sessions/checkout-flow/validation-reports')
  })

  // A report saved before the graph's current shape keeps its graph as it was; the board says so instead of failing to read.
  describe("with a report whose saved graph is out of date", () => {
    beforeEach(() => board.write(REPORT_PATH.replace(/\.md$/, '.json'), JSON.stringify({ overlays: [], practices: CLEAN_GRAPH.practices })))

    it('should say the report is out of date', async () => {
      const { page } = await board.page()
      await page.panels.openReport(ticketOn(page), storyMapOn(page))
      expect(reportPanel(page).report.isOutOfDate).toBe(true)
    })

    it('should send its fidelity to validate again', async () => {
      const { page } = await board.page()
      const chat = await board.connectChat(page)
      await ticketOn(page).validateAgain(storyMapOn(page))
      expect(await chat.checkIn()).toEqual([{ kind: 'command', text: `/actions-validate ${SLUG} ${SESSION}` }])
    })
  })
})

describe('Fix Report Violations', () => {
  describe('with Fix pressed on one violation', () => {
    async function sent() {
      const { page } = await board.page()
      const chat = await board.connectChat(page)
      const rule = await brokenRule(page)
      const violation = rule.violations[0]!
      await reportPanel(page).report.fixViolation(rule, violation)
      return { rule, violation, commands: await chat.checkIn() }
    }

    it('should send one message to the chat', async () => {
      expect((await sent()).commands).toHaveLength(1)
    })

    // The person edits the fix in the chat's prompt before sending it.
    it("should fill the chat's prompt rather than send", async () => {
      expect((await sent()).commands[0]!.kind).toBe('fill')
    })

    it('should name the rule and what it requires', async () => {
      const { rule, commands } = await sent()
      expect(commands[0]!.text).toContain(`${rule.rule.slug}: ${rule.rule.body}`)
    })

    it('should give the error at its file and line', async () => {
      const { violation, commands } = await sent()
      expect(commands[0]!.text).toContain(`.context/story-map.md:6: ${violation.message}`)
    })

    it('should quote the content that failed', async () => {
      const { violation, commands } = await sent()
      const failing = violation.source.find(entry => entry.number === violation.line)!
      expect(commands[0]!.text).toContain(`> ${failing.number} | ${failing.text}`)
    })

    it("should name the ticket's session", async () => {
      expect((await sent()).commands[0]!.text).toContain(SESSION)
    })

    // A fix in one format alone leaves the fidelity's other formats still breaking the rule.
    it('should ask for the fix in every format of the fidelity', async () => {
      expect((await sent()).commands[0]!.text).toContain(EVERY_FORMAT)
    })
  })

  describe('with Fix all pressed on a rule', () => {
    it('should ask the chat to fix all violations of that rule found in the report it names', async () => {
      const { page } = await board.page()
      const chat = await board.connectChat(page)
      const rule = await brokenRule(page)
      const { report } = reportPanel(page)
      await report.fixRule(rule)
      const [command] = await chat.checkIn()
      expect(command!.text).toContain(`Fix all violations of ${rule.rule.slug} found in this report: ${report.path}`)
    })

    it('should ask for the fixes in every format of the fidelity', async () => {
      const { page } = await board.page()
      const chat = await board.connectChat(page)
      const rule = await brokenRule(page)
      await reportPanel(page).report.fixRule(rule)
      const [command] = await chat.checkIn()
      expect(command!.text).toContain(EVERY_FORMAT)
    })
  })

  // The report already holds every violation, so the chat is pointed at it rather than sent a copy.
  describe('with Fix all pressed on the whole report', () => {
    async function sent() {
      const { page } = await board.page()
      const chat = await board.connectChat(page)
      await page.panels.openReport(ticketOn(page), storyMapOn(page))
      const { report } = reportPanel(page)
      await report.fixReport()
      return { report, commands: await chat.checkIn() }
    }

    it('should send one message to the chat', async () => {
      expect((await sent()).commands).toHaveLength(1)
    })

    it('should ask the chat to fix all violations found in the report it names', async () => {
      const { report, commands } = await sent()
      expect(commands[0]!.text).toContain(`Fix all violations found in this report: ${report.path}`)
    })

    it('should ask for the fixes in every format of the fidelity', async () => {
      expect((await sent()).commands[0]!.text).toContain(EVERY_FORMAT)
    })
  })
})

describe('Refresh Board After Tool Calls', () => {
  describe('with a report and files open as the board changes', () => {
    // The story map validated again, clean, and its diagram generated, as the agent leaves them.
    async function changed() {
      const { page } = await board.page()
      await page.panels.openReport(ticketOn(page), storyMapOn(page))
      await page.files.openFiles(ticketOn(page), [storyMapOn(page)])
      board.write('.sessions/checkout-flow/validation-reports/stories-story-map-20261102T100000.md', '# Graph rule validation\n')
      board.write('.sessions/checkout-flow/validation-reports/stories-story-map-20261102T100000.json', JSON.stringify(CLEAN_GRAPH))
      board.write('.context/story-map.drawio', '<mxfile/>\n')
      board.logOn(TICKET, 'validate Stories story_map')
      await page.reader.refresh()
      return page
    }

    it('should read the report again', async () => {
      expect(reportPanel(await changed()).report.rules).toEqual([])
    })

    it('should read the files again', async () => {
      expect(shownTabs(filesPanel(await changed())).filter(tab => tab.exists).map(tab => tab.path)).toEqual(['.context/story-map.md', '.context/story-map.drawio'])
    })
  })

  it('should read the open file again', async () => {
    const { page } = await board.page()
    await page.files.openFiles(ticketOn(page), [storyMapOn(page)])
    board.write('.context/story-map.md', '# Check Out Order Again\n')
    await page.files.reload()
    expect(filesPanel(page).shown?.text).toBe('# Check Out Order Again\n')
  })
})

describe('Arrange Side Panel', () => {
  describe('Resize Side Panel', () => {
    it('should set the width a drag asks for', () => {
      const { page } = board.unreadPage()
      page.panels.setWidth('files', 700)
      expect(page.panels.widthOf('files')).toBe(700)
    })

    it('should not go narrower than the smallest width', () => {
      const { page } = board.unreadPage()
      page.panels.setWidth('files', 10)
      expect(page.panels.widthOf('files')).toBe(360)
    })
  })

  describe('Expand Side Panel', () => {
    it('should expand one panel at a time', async () => {
      const { page } = await board.page()
      await page.panels.openReport(ticketOn(page), storyMapOn(page))
      await page.files.openFiles(ticketOn(page), [storyMapOn(page)])
      page.panels.toggleExpanded('report')
      page.panels.toggleExpanded('files')
      expect(page.store.state.panels.filter(panel => panel.isExpanded).map(panel => panel.kind)).toEqual(['files'])
    })
  })

  describe('Close Side Panel', () => {
    it('should close the panel', async () => {
      const { page } = await board.page()
      await page.panels.openReport(ticketOn(page), storyMapOn(page))
      page.panels.close('report')
      expect(page.store.state.panels).toEqual([])
    })
  })
})
