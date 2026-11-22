import { readFileSync } from 'node:fs'
import { join } from 'node:path'

import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import type { ReportRuleData } from '@cdd/space/kanban/ticket'
import { BoardOnProject, ticketOn as shownTicket } from 'test-utils/board-page-support'
import type { FidelityProgressClient } from '@src/kanban/ticket/fidelity-progress-client'
import type { TicketClient } from '@src/kanban/ticket/ticket-client'

import type { BoardPage } from './board-page'
import type { ReportPanel } from '../shared/board-store'

// checkout-flow is the active ticket: its story map was validated with one rule broken on .context/story-map.md line 6.
const TICKET = 'checkout-flow'
const SESSION = 'session=.sessions/checkout-flow/session.json'
const SLUG = 'stories-story-map'
const REPORT_PATH = '.sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md'
const FAILING_LINE = 12
// A graph validate saved with no hits, in the shape harness/graph/saved_graph.py writes (SAVED_SHAPE_VERSION 5).
const CLEAN_GRAPH = { version: 5, overlays: [], practices: { stories: { source_root: '', root_facts: {}, nodes: [], edges: [], violations: [] } } }

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

const reportPanel = (page: BoardPage) => page.store.state.panels.find(panel => panel.kind === 'report') as ReportPanel

// A panel holds the ticket it is about, as the board read shows it.
const ticketOn = (page: BoardPage): TicketClient => shownTicket(page, TICKET)

// The ticket's progress on its story map, whose report and help the panels show.
const storyMapOn = (page: BoardPage): FidelityProgressClient => ticketOn(page).work.progressNamed(SLUG)!

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
      await ticketOn(page).chatPrompts.validateAgain(storyMapOn(page))
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

  describe('with False pressed on one violation', () => {
    async function sent() {
      const { page } = await board.page()
      const chat = await board.connectChat(page)
      const rule = await brokenRule(page)
      const violation = rule.violations[0]!
      await reportPanel(page).report.reportFalseViolation(rule, violation)
      return { rule, violation, commands: await chat.checkIn() }
    }

    it('should say the violation is false and ask for the rule to be investigated for errors', async () => {
      const { rule, commands } = await sent()
      expect(commands[0]!.text).toContain(`This violation of the ${rule.fidelity.slug} rule is false. Investigate the rule for errors.`)
    })

    // The person edits the message in the chat's prompt before sending it, as with a fix.
    it("should fill the chat's prompt rather than send", async () => {
      expect((await sent()).commands[0]!.kind).toBe('fill')
    })

    it('should name the rule and what it requires', async () => {
      const { rule, commands } = await sent()
      expect(commands[0]!.text).toContain(`${rule.rule.slug}: ${rule.rule.body}`)
    })

    it('should give the finding at its file and line with the content it judged', async () => {
      const { violation, commands } = await sent()
      const failing = violation.source.find(entry => entry.number === violation.line)!
      const text = commands[0]!.text
      expect([text.includes(`.context/story-map.md:6: ${violation.message}`), text.includes(`> ${failing.number} | ${failing.text}`)]).toEqual([true, true])
    })

    // A false finding is a defect in the rule or its check, so the content it names stays as it is.
    it('should ask for the judged content to be left unchanged', async () => {
      expect((await sent()).commands[0]!.text).toContain('Change none of the content the finding names.')
    })

    it("should name the ticket's session", async () => {
      expect((await sent()).commands[0]!.text).toContain(SESSION)
    })
  })

  // Python keeps the acceptance and answers the report without the violation; the page draws that answer.
  describe('with Accept pressed on one violation', () => {
    async function accepted() {
      const { page } = await board.page()
      const rule = await brokenRule(page)
      await reportPanel(page).report.acceptViolation(rule, rule.violations[0]!)
      return { page, rule, report: reportPanel(page).report }
    }

    it('should list the violation no longer', async () => {
      expect((await accepted()).report.rules).toEqual([])
    })

    it('should count no open violation', async () => {
      expect((await accepted()).report.violationCount).toBe(0)
    })

    it('should say one accepted violation is left out', async () => {
      expect((await accepted()).report.acceptedCount).toBe(1)
    })

    it('should list the accepted violation under its rule, to take back', async () => {
      const { rule, report } = await accepted()
      expect(report.accepted.map(entry => [entry.rule.slug, entry.violations.map(violation => violation.message)])).toEqual([[rule.rule.slug, [rule.violations[0]!.message]]])
    })

    it("should keep it in the project's .context/violations-accepted.json by its rule and its node's id", async () => {
      const { rule } = await accepted()
      const kept = JSON.parse(readFileSync(join(board.root, '.context', 'violations-accepted.json'), 'utf8')).accepted
      expect(kept.map((entry: { rule: string; node_id: string }) => [entry.rule, entry.node_id])).toEqual([[rule.rule.slug, rule.violations[0]!.node_id]])
    })

    it("should leave the ticket's story map with no violations on the next board read", async () => {
      const { page } = await accepted()
      await page.reader.refresh()
      expect([storyMapOn(page).hasViolations, storyMapOn(page).violationCount]).toEqual([false, 0])
    })

    describe('that is then taken back', () => {
      async function takenBack() {
        const { page, report } = await accepted()
        const rule = report.accepted[0]!
        await report.reopenViolation(rule, rule.violations[0]!)
        return { page, report: reportPanel(page).report }
      }

      it('should list the violation again', async () => {
        expect((await takenBack()).report.rules.map(rule => [rule.rule.slug, rule.count])).toEqual([['verb-noun-format', 1]])
      })

      it('should say no accepted violation is left out', async () => {
        expect((await takenBack()).report.acceptedCount).toBe(0)
      })
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
  describe('with a report open as the board changes', () => {
    // The story map validated again, clean, and its diagram generated, as the agent leaves them.
    async function changed() {
      const { page } = await board.page()
      await page.panels.openReport(ticketOn(page), storyMapOn(page))
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
  })
})

describe('Arrange Side Panel', () => {
  describe('Resize Side Panel', () => {
    it('should set the width a drag asks for', () => {
      const { page } = board.unreadPage()
      page.panels.setWidth('help', 700)
      expect(page.panels.widthOf('help')).toBe(700)
    })

    it('should not go narrower than the smallest width', () => {
      const { page } = board.unreadPage()
      page.panels.setWidth('help', 10)
      expect(page.panels.widthOf('help')).toBe(360)
    })
  })

  describe('Expand Side Panel', () => {
    it('should expand one panel at a time', async () => {
      const { page } = await board.page()
      await page.panels.openReport(ticketOn(page), storyMapOn(page))
      await page.panels.openFidelityHelp(storyMapOn(page))
      page.panels.toggleExpanded('report')
      page.panels.toggleExpanded('help')
      expect(page.store.state.panels.filter(panel => panel.isExpanded).map(panel => panel.kind)).toEqual(['help'])
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
