// Follow Story Steps To Code, as story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/
// switch_files_app_between_files_and_graph_story.test.md writes it. The session answers each step of a story test with
// what it invokes and observes (`.story.shared.py`); the page puts each on its step's line and opens no call of its own.
import { describe, expect, it } from 'vitest'

import type { NodeSourceData } from '@cdd/harness/graph/graph'
import type { SessionFileData } from '@cdd/space/session/session'

import { calloutsOf, isStoryTest } from './source-of-file'

const STEP_STORY = 'story_tests/manage-tickets/remove-tickets/delete-ticket.story.shared.py'
const node = (node_id: string, name: string, owner: string, file: string, start_line: number, text: string): NodeSourceData =>
  ({ node_id, name, type: 'Operation', owner, file, start_line, end_line: start_line + text.split('\n').length - 1, text, members: [] }) as NodeSourceData
const DELETE = node('delete', 'delete', 'Ticket', 'space/kanban/ticket.py', 8, '    def delete(self, board: Board) -> None:\n        board.reread()')
const TICKET_ON_BOARD = node('ticket_on_board', 'ticket_on_board', '', 'space/kanban/ticket_story_examples.py', 1, 'def ticket_on_board(world) -> str:\n    return "checkout"')

const storyTest = { path: STEP_STORY, callouts: [], steps: [{ line: 9, invokes: [TICKET_ON_BOARD], observes: [] }, { line: 13, invokes: [DELETE], observes: [] }] } as unknown as SessionFileData

describe('Story Test Callouts', () => {
  describe("with Delete Ticket's shared story test, its Given invoking ticket_on_board and its When Ticket.delete", () => {
    it("should put each step's callout on the step's own line", () => {
      expect(calloutsOf(storyTest).map(callout => [callout.line, callout.title, callout.path, callout.startLine])).toEqual([
        [9, 'ticket_on_board', 'space/kanban/ticket_story_examples.py', 1],
        [13, 'Ticket.delete', 'space/kanban/ticket.py', 8],
      ])
    })

    it('should open no call or class its code or docstring names, its callouts being its steps own', () => {
      expect(isStoryTest(storyTest)).toBe(true)
    })
  })
})
