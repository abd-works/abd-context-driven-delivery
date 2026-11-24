// A Selected Node Is Marked By One Orange Line Beside Its Lines, as story_tests/review-generated-work-in-file-viewer/
// open-graph-nodes-in-files-app/open_graph_nodes_in_files_app_story.test.md writes it. Only the
// page marks lines, so the marks are read here as the decorations the source view is given.
import { describe, expect, it } from 'vitest'

import { SELECTED_RANGE, selectedMarks } from './file-marks'

const TICKET_LINES = 600

describe('Selected node marks', () => {
  describe('with Ticket.close selected, on lines 538 to 560', () => {
    const marks = selectedMarks([{ start: 538, end: 560 }], TICKET_LINES)

    it('should run one line beside lines 538 to 560, in the margin by the line numbers', () => {
      expect(marks.map(mark => [mark.range.startLineNumber, mark.range.endLineNumber, mark.options.linesDecorationsClassName])).toEqual([[538, 560, SELECTED_RANGE]])
    })

    it('should not shade the text of the lines', () => {
      expect(marks.map(mark => [mark.options.className, mark.options.inlineClassName])).toEqual([[undefined, undefined]])
    })
  })

  describe('with a node that covers the whole file selected', () => {
    it('should mark no lines', () => {
      expect(selectedMarks([{ start: 1, end: TICKET_LINES }], TICKET_LINES)).toEqual([])
    })
  })
})
