import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import type { ReportRuleData } from '@cdd/harness/kanban/ticket'
import type { TicketFiles } from '@src/kanban/ticket/ticket'
import { folderGroupsOf, generatedPaths, offeredTabs } from '@src/kanban/ticket/files-panel-client'
import { BoardOnProject } from 'test-utils/board-page-support'

import type { BoardPage } from './board-page'
import type { FilesPanel, ReportPanel } from './board-store'

// checkout-flow is the active ticket: its story map was validated with one rule broken on tests/story-map.md line 6.
const TICKET = 'checkout-flow'
const SESSION = 'session=.sessions/checkout-flow/session.json'
const SLUG = 'stories-story_map'
const REPORT_PATH = '.sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md'
const FAILING_LINE = 12
const CLEAN_GRAPH = { practices: { stories: { nodes: [], rules: [] } } }

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

const filesPanel = (page: BoardPage) => page.store.state.panels.find(panel => panel.kind === 'files') as FilesPanel
const reportPanel = (page: BoardPage) => page.store.state.panels.find(panel => panel.kind === 'report') as ReportPanel

async function brokenRule(page: BoardPage): Promise<ReportRuleData> {
  await page.panels.openReport(TICKET, SLUG)
  return reportPanel(page).report.rules[0]!
}

describe('List Ticket Files', () => {
  it('should list the files that exist', async () => {
    const { page } = await board.page()
    await page.files.openFiles(TICKET, [SLUG], 'list')
    expect(generatedPaths(filesPanel(page))).toEqual(['tests/story-map.md'])
  })

  describe('with a list that cannot be read', () => {
    async function refused() {
      const { page } = await board.page()
      await page.files.openFiles('no-such-ticket', [SLUG], 'list')
      return page
    }

    it('should say so in a toast', async () => {
      expect((await refused()).store.state.toasts[0]?.text).toBe("cdd ticket.files failed: TicketNotFoundError: no ticket named 'no-such-ticket' on the board")
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
    await page.files.openSessionFolder(TICKET)
    expect(generatedPaths(filesPanel(page))).toContain(REPORT_PATH)
  })

  it('should show them as folders', async () => {
    const { page } = await board.page()
    await page.files.openSessionFolder(TICKET)
    expect(filesPanel(page).mode).toBe('folder')
  })

  describe('with its latest handoff opened', () => {
    const HANDOFF = `.sessions/${TICKET}/handoff-20261101T120000.md`

    async function opened() {
      board.write(HANDOFF, '# Handoff\n')
      const { page } = await board.page()
      await page.files.openSessionFile(TICKET, HANDOFF)
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

describe('View Files', () => {
  it('should open one tab per format, generated or not', async () => {
    const { page } = await board.page()
    await page.files.openFiles(TICKET, [SLUG], 'files')
    expect(filesPanel(page).tabs).toEqual(['tests/story-map.md', 'tests/story-map.drawio'])
  })

  it('should keep markdown before code before diagrams', () => {
    const files: TicketFiles = { [SLUG]: { drawio: [{ path: 'b.drawio', exists: true }], python: [{ path: 'c.py', exists: true }], markdown: [{ path: 'a.md', exists: true }] } }
    expect(offeredTabs(files, [SLUG])).toEqual(['a.md', 'c.py', 'b.drawio'])
  })

  it('should read the text of the file a tab shows', async () => {
    const { page } = await board.page()
    await page.files.openFiles(TICKET, [SLUG], 'files')
    expect(filesPanel(page).texts['tests/story-map.md']).toBe(['# Check Out Order', '', '## Payment', '', '- Enter Card Details', '- Handle Payment', '- Confirm Order', ''].join('\n'))
  })

  it('should go back to the list when the last tab closes', async () => {
    const { page } = await board.page()
    await page.files.openFiles(TICKET, [SLUG], 'files')
    page.files.closeTab('tests/story-map.md')
    page.files.closeTab('tests/story-map.drawio')
    expect(filesPanel(page).mode).toBe('list')
  })

  describe('with a violation in a file its fidelity does not declare', () => {
    async function opened() {
      board.write('src/other.py', 'x\n')
      const { page } = await board.page()
      await page.files.openFileAtLine(TICKET, SLUG, 'src/other.py', FAILING_LINE)
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
    await page.panels.openReport(TICKET, SLUG)
    expect(reportPanel(page).report.path).toBe(REPORT_PATH)
  })

  it("should show every fidelity's violations with no fidelity named", async () => {
    const { page } = await board.page()
    await page.panels.openReport(TICKET, '')
    expect(reportPanel(page).report.path).toBe('.sessions/checkout-flow/validation-reports')
  })
})

describe('Fix Report Violations', () => {
  it('should send Fix for one violation at its line', async () => {
    const { page } = await board.page()
    const chat = await board.connectChat(page)
    const rule = await brokenRule(page)
    await page.fixViolation(TICKET, rule, rule.violations[0]!)
    expect(await chat.checkIn()).toEqual([{ kind: 'command', text: `/actions-satisfy stories-story-map tests/story-map.md:6 rule verb-noun-format ${SESSION}` }])
  })

  it('should send Fix all for every violation of a rule', async () => {
    const { page } = await board.page()
    const chat = await board.connectChat(page)
    await page.fixRule(TICKET, await brokenRule(page))
    expect(await chat.checkIn()).toEqual([{ kind: 'command', text: `/actions-satisfy stories-story-map rule verb-noun-format ${SESSION}` }])
  })
})

describe('Refresh Board After Tool Calls', () => {
  describe('with a report and files open as the board changes', () => {
    // The story map validated again, clean, and its diagram generated, as the agent leaves them.
    async function changed() {
      const { page } = await board.page()
      await page.panels.openReport(TICKET, SLUG)
      await page.files.openFiles(TICKET, [SLUG], 'list')
      board.write('.sessions/checkout-flow/validation-reports/stories-story-map-20261102T100000.md', '# Graph rule validation\n')
      board.write('.sessions/checkout-flow/validation-reports/stories-story-map-20261102T100000.json', JSON.stringify(CLEAN_GRAPH))
      board.write('tests/story-map.drawio', '<mxfile/>\n')
      board.logOn(TICKET, 'validate Stories story_map')
      await page.reader.refresh()
      return page
    }

    it('should read the report again', async () => {
      expect(reportPanel(await changed()).report.rules).toEqual([])
    })

    it('should read the files again', async () => {
      expect(generatedPaths(filesPanel(await changed()))).toEqual(['tests/story-map.md', 'tests/story-map.drawio'])
    })
  })

  it('should keep a tab a person closed closed', async () => {
    const { page } = await board.page()
    await page.files.openFiles(TICKET, [SLUG], 'files')
    page.files.closeTab('tests/story-map.drawio')
    await page.files.reload()
    expect(filesPanel(page).tabs).toEqual(['tests/story-map.md'])
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
      await page.panels.openReport(TICKET, SLUG)
      await page.files.openFiles(TICKET, [SLUG], 'list')
      page.panels.toggleExpanded('report')
      page.panels.toggleExpanded('files')
      expect(page.store.state.panels.filter(panel => panel.isExpanded).map(panel => panel.kind)).toEqual(['files'])
    })
  })

  describe('Close Side Panel', () => {
    it('should close the panel', async () => {
      const { page } = await board.page()
      await page.panels.openReport(TICKET, SLUG)
      page.panels.close('report')
      expect(page.store.state.panels).toEqual([])
    })
  })
})
