import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import type { ReportRuleData } from '@cdd/space/kanban/ticket'
import { folderGroupsOf, generatedPaths, offeredTabs } from '@src/kanban/ticket/files-panel-client'
import { BoardOnProject, ticketOn as shownTicket } from 'test-utils/board-page-support'
import type { FidelityProgressClient } from '@src/kanban/ticket/fidelity-progress-client'
import type { FilesByFidelity, TicketClient } from '@src/kanban/ticket/ticket-client'

import type { BoardPage } from './board-page'
import type { FilesPanel, ReportPanel } from './board-store'

// checkout-flow is the active ticket: its story map was validated with one rule broken on .context/story-map.md line 6.
const TICKET = 'checkout-flow'
const SESSION = 'session=.sessions/checkout-flow/session.json'
const SLUG = 'stories-story-map'
const REPORT_PATH = '.sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md'
const FAILING_LINE = 12
// A graph validate saved with no hits, in the shape harness/graph/saved_graph.py writes (version 2).
const CLEAN_GRAPH = { version: 2, overlays: [], practices: { stories: { source_root: '', root_facts: {}, nodes: [], edges: [], violations: [] } } }

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

describe('List Ticket Files', () => {
  it('should list the files that exist', async () => {
    const { page } = await board.page()
    await page.files.openFiles(ticketOn(page), [storyMapOn(page)], 'folder')
    expect(generatedPaths(filesPanel(page))).toEqual(['.context/story-map.md'])
  })

  describe('with a list that cannot be read', () => {
    async function refused() {
      const { page } = await board.page()
      const gone = goneTicket(page, 'no-such-ticket')
      await page.files.openFiles(gone, [gone.progressNamed(SLUG)!], 'folder')
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

describe('Browse Ticket Folder', () => {
  it('should group the files under their folders', () => {
    expect(folderGroupsOf(['tests/a.md', 'tests/deep/b.md', 'src/c.ts'])).toEqual([
      { root: 'tests/', entries: [{ path: 'tests/a.md', name: 'a.md' }, { path: 'tests/deep/b.md', name: 'deep/b.md' }] },
      { root: 'src/', entries: [{ path: 'src/c.ts', name: 'c.ts' }] },
    ])
  })
})

describe("Browse Ticket's Session Folder", () => {
  it('should list every file in the session folder', async () => {
    const { page } = await board.page()
    await page.files.openSessionFolder(ticketOn(page))
    expect(generatedPaths(filesPanel(page))).toContain(REPORT_PATH)
  })

  it('should show them as folders', async () => {
    const { page } = await board.page()
    await page.files.openSessionFolder(ticketOn(page))
    expect(filesPanel(page).mode).toBe('folder')
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
      expect(filesPanel(await opened()).texts[HANDOFF]).toBe('# Handoff\n')
    })
  })
})

describe('View Fidelity Files', () => {
  it('should open one tab per format, generated or not', async () => {
    const { page } = await board.page()
    await page.files.openFiles(ticketOn(page), [storyMapOn(page)], 'files')
    expect(filesPanel(page).tabs).toEqual(['.context/story-map.md', '.context/story-map.drawio'])
  })

  it('should open the tabs in the order Python sends the formats', () => {
    const files: FilesByFidelity = { [SLUG]: { markdown: [{ path: 'a.md', exists: true }], python: [{ path: 'c.py', exists: true }], drawio: [{ path: 'b.drawio', exists: true }] } }
    expect(offeredTabs(files, [SLUG])).toEqual(['a.md', 'c.py', 'b.drawio'])
  })

  it('should read the text of the file a tab shows', async () => {
    const { page } = await board.page()
    await page.files.openFiles(ticketOn(page), [storyMapOn(page)], 'files')
    expect(filesPanel(page).texts['.context/story-map.md']).toBe(['# Check Out Order', '', '## Payment', '', '- Enter Card Details', '- Handle Payment', '- Confirm Order', ''].join('\n'))
  })

  it('should go back to the folder when the last tab closes', async () => {
    const { page } = await board.page()
    await page.files.openFiles(ticketOn(page), [storyMapOn(page)], 'files')
    page.files.closeTab('.context/story-map.md')
    page.files.closeTab('.context/story-map.drawio')
    expect(filesPanel(page).mode).toBe('folder')
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

  // A report saved before the graph's shape 2 keeps its graph as it was; the board says so instead of failing to read.
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
      await ticketOn(page).fixViolation(rule, violation)
      return { rule, violation, commands: await chat.checkIn() }
    }

    it('should send one message to the chat', async () => {
      expect((await sent()).commands).toHaveLength(1)
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
      await ticketOn(page).fixRule(report, rule)
      const [command] = await chat.checkIn()
      expect(command!.text).toContain(`Fix all violations of ${rule.rule.slug} found in this report: ${report.path}`)
    })

    it('should ask for the fixes in every format of the fidelity', async () => {
      const { page } = await board.page()
      const chat = await board.connectChat(page)
      const rule = await brokenRule(page)
      await ticketOn(page).fixRule(reportPanel(page).report, rule)
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
      await ticketOn(page).fixReport(report)
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
      await page.files.openFiles(ticketOn(page), [storyMapOn(page)], 'folder')
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
      expect(generatedPaths(filesPanel(await changed()))).toEqual(['.context/story-map.md', '.context/story-map.drawio'])
    })
  })

  it('should keep a tab a person closed closed', async () => {
    const { page } = await board.page()
    await page.files.openFiles(ticketOn(page), [storyMapOn(page)], 'files')
    page.files.closeTab('.context/story-map.drawio')
    await page.files.reload()
    expect(filesPanel(page).tabs).toEqual(['.context/story-map.md'])
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
      await page.files.openFiles(ticketOn(page), [storyMapOn(page)], 'folder')
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
