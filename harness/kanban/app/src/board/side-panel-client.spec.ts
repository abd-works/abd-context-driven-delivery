import { describe, expect, it } from 'vitest'

import type { Report, TicketFiles } from './board'
import type { FilesPanel, ReportPanel } from './board-store'
import { folderGroupsOf, generatedPaths, offeredTabs } from './side-panel-client'
import { boardJson, discovery, pageOn, ticketJson, withChat } from './spec-support'

const SLUG = 'stories-story_map'
const FILES: TicketFiles = { [SLUG]: { markdown: [{ path: 'tests/story-map.md', exists: true }], drawio: [{ path: 'tests/story-map.drawio', exists: false }] } }
const REPORT: Report = {
  path: '.sessions/sign-up/validation-reports/r.md',
  text: '',
  has_saved_graph: true,
  rules: [{ fidelity: SLUG, name: 'verb-noun-format', description: 'Name it.', count: 1, violations: [{ location: 'tests/story-map.md', line: 6, message: 'No verb', source: [] }] }],
}

function panelsPage() {
  const { page, server } = pageOn(boardJson([discovery([ticketJson('sign-up')])], 'sign-up'))
  server.answer('POST /api/tickets/sign-up/files', FILES)
  server.answer('GET /api/tickets/sign-up/file?path=tests%2Fstory-map.md', { path: 'tests/story-map.md', text: '# Map' })
  server.answer(`GET /api/tickets/sign-up/report?fidelity=${SLUG}`, REPORT)
  return { page, server }
}

const filesPanel = (page: ReturnType<typeof panelsPage>['page']) => page.store.state.panels.find(panel => panel.kind === 'files') as FilesPanel

describe('List Ticket Files', () => {
  it('should list the files that exist', async () => {
    const { page } = panelsPage()
    await page.panels.openFiles('sign-up', [SLUG], 'list')
    expect(generatedPaths(filesPanel(page))).toEqual(['tests/story-map.md'])
  })

  it('should say so in a toast when the list cannot be read', async () => {
    const { page, server } = panelsPage()
    server.answer('POST /api/tickets/sign-up/files', { error: 'cdd ticket.files failed: no' }, 502)
    await page.panels.openFiles('sign-up', [SLUG], 'list')
    expect(page.store.state.toasts[0]?.text).toBe('cdd ticket.files failed: no')
    expect(page.store.state.panels).toEqual([])
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

describe('View Files', () => {
  it('should open one tab per format, generated or not', async () => {
    const { page } = panelsPage()
    await page.panels.openFiles('sign-up', [SLUG], 'files')
    expect(filesPanel(page).tabs).toEqual(['tests/story-map.md', 'tests/story-map.drawio'])
  })

  it('should keep markdown before code before diagrams', () => {
    const files: TicketFiles = { [SLUG]: { drawio: [{ path: 'b.drawio', exists: true }], python: [{ path: 'c.py', exists: true }], markdown: [{ path: 'a.md', exists: true }] } }
    expect(offeredTabs(files, [SLUG])).toEqual(['a.md', 'c.py', 'b.drawio'])
  })

  it('should read the text of the file a tab shows', async () => {
    const { page } = panelsPage()
    await page.panels.openFiles('sign-up', [SLUG], 'files')
    expect(filesPanel(page).texts['tests/story-map.md']).toBe('# Map')
  })

  it('should go back to the list when the last tab closes', async () => {
    const { page } = panelsPage()
    await page.panels.openFiles('sign-up', [SLUG], 'files')
    page.panels.closeTab('tests/story-map.md')
    page.panels.closeTab('tests/story-map.drawio')
    expect(filesPanel(page).mode).toBe('list')
  })

  it('should open a violation\'s file at its line, even one its fidelity does not declare', async () => {
    const { page, server } = panelsPage()
    server.answer('GET /api/tickets/sign-up/file?path=src%2Fother.py', { path: 'src/other.py', text: 'x' })
    await page.panels.openFileAtLine('sign-up', SLUG, 'src/other.py', 12)
    expect(filesPanel(page).activeTab).toBe('src/other.py')
    expect(filesPanel(page).lines['src/other.py']).toBe(12)
  })
})

describe('Open Validation Report', () => {
  it('should show that fidelity\'s latest report', async () => {
    const { page } = panelsPage()
    await page.panels.openReport('sign-up', SLUG)
    expect((page.store.state.panels[0] as ReportPanel).report.path).toBe(REPORT.path)
  })

  it('should show every fidelity\'s violations with no fidelity named', async () => {
    const { page, server } = panelsPage()
    server.answer('GET /api/tickets/sign-up/violations', REPORT)
    await page.panels.openReport('sign-up', '')
    expect(server.requests.at(-1)?.path).toBe('/api/tickets/sign-up/violations')
  })
})

describe('Fix Report Violations', () => {
  it('should send Fix for one violation at its line', async () => {
    const { page, server } = panelsPage()
    withChat(page, server)
    await page.fixViolation(REPORT.rules[0]!, REPORT.rules[0]!.violations[0]!)
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'command', text: '/actions-satisfy stories-story-map tests/story-map.md:6 rule verb-noun-format' })
  })

  it('should send Fix all for every violation of a rule', async () => {
    const { page, server } = panelsPage()
    withChat(page, server)
    await page.fixRule(REPORT.rules[0]!)
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'command', text: '/actions-satisfy stories-story-map rule verb-noun-format' })
  })
})

describe('Refresh Board After Tool Calls', () => {
  it('should read an open report and files again when the board changes', async () => {
    const { page, server } = panelsPage()
    await page.panels.openReport('sign-up', SLUG)
    await page.panels.openFiles('sign-up', [SLUG], 'list')
    server.answer(`GET /api/tickets/sign-up/report?fidelity=${SLUG}`, { ...REPORT, rules: [] })
    server.answer('POST /api/tickets/sign-up/files', { [SLUG]: { markdown: [{ path: 'new.md', exists: true }] } })
    server.answer('GET /api/board', boardJson([discovery([ticketJson('sign-up', { last_activity: '2026-11-02T10:00:00Z' })])], 'sign-up'))
    await page.board.refresh()
    expect((page.store.state.panels.find(panel => panel.kind === 'report') as ReportPanel).report.rules).toEqual([])
    expect(generatedPaths(filesPanel(page))).toEqual(['new.md'])
  })

  it('should keep a tab a person closed closed', async () => {
    const { page } = panelsPage()
    await page.panels.openFiles('sign-up', [SLUG], 'files')
    page.panels.closeTab('tests/story-map.drawio')
    await page.panels.reload()
    expect(filesPanel(page).tabs).toEqual(['tests/story-map.md'])
  })
})

describe('Arrange Side Panel', () => {
  describe('Resize Side Panel', () => {
    it('should set the width a drag asks for', () => {
      const { page } = panelsPage()
      page.panels.setWidth('files', 700)
      expect(page.panels.widthOf('files')).toBe(700)
    })

    it('should not go narrower than the smallest width', () => {
      const { page } = panelsPage()
      page.panels.setWidth('files', 10)
      expect(page.panels.widthOf('files')).toBe(360)
    })
  })

  describe('Expand Side Panel', () => {
    it('should expand one panel at a time', async () => {
      const { page } = panelsPage()
      await page.panels.openReport('sign-up', SLUG)
      await page.panels.openFiles('sign-up', [SLUG], 'list')
      page.panels.toggleExpanded('report')
      page.panels.toggleExpanded('files')
      expect(page.store.state.panels.filter(panel => panel.isExpanded).map(panel => panel.kind)).toEqual(['files'])
    })
  })

  describe('Close Side Panel', () => {
    it('should close the panel', async () => {
      const { page } = panelsPage()
      await page.panels.openReport('sign-up', SLUG)
      page.panels.close('report')
      expect(page.store.state.panels).toEqual([])
    })
  })
})
