/**
 * States each behavior of List Ticket Files, View Fidelity Files, and Open Validation Report once. Reaches the tier only through
 * its driver. The sentences match kanban_tools_spec.py.
 */
import { shareBehavior } from 'test-utils/behavior-test/behavior-test'

export type FilesAndReportsDriver = {
  generatedFilesOf: (ticket: string, fidelity: string) => Promise<string[]>
  textOfFile: (ticket: string, fidelity: string, path: string) => Promise<string>
  reportPathOf: (ticket: string, fidelity: string) => Promise<string>
  ruleNamesOf: (ticket: string, fidelity: string) => Promise<string[]>
  failingLineOf: (ticket: string, fidelity: string) => Promise<number>
}

const TICKET = 'checkout-flow'
const FIDELITY = 'stories-story_map'
const STORY_MAP = '.context/story-map.md'

export const filesAndReportsBehavior = shareBehavior<FilesAndReportsDriver>(({ describe, it, expect, driver }) => {
  describe('a ticket', () => {
    describe("with a fidelity's markdown generated", () => {
      it('should list the file with whether it exists', async () => {
        expect(await driver().generatedFilesOf(TICKET, FIDELITY)).toContain(STORY_MAP)
      })

      it("should return the file's text", async () => {
        expect(await driver().textOfFile(TICKET, FIDELITY, STORY_MAP)).toContain('Check Out Order')
      })
    })

    describe('with validation reports saved for a fidelity', () => {
      it("should show that fidelity's latest report", async () => {
        expect(await driver().reportPathOf(TICKET, FIDELITY)).toContain('stories-story-map-20261101T100000')
      })

      it('should list each rule the report names with its violations', async () => {
        expect(await driver().ruleNamesOf(TICKET, FIDELITY)).toEqual(['verb-noun-format'])
      })

      it('should give a violation the line it failed on', async () => {
        expect(await driver().failingLineOf(TICKET, FIDELITY)).toEqual(6)
      })
    })
  })
})
