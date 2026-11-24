// Follow Story Steps To Code, as story_tests/review-generated-work-in-file-viewer/open-graph-nodes-in-files-app/
// open_graph_nodes_in_files_app_story.test.md writes it. The session answers each step of a story test with
// a callout for what it invokes and observes, on the line of the step that names it and under its title
// (space/session/files/file_steps.py, file_steps_spec.py); the page draws each where it is sent and opens no call of its own.
import { describe, expect, it } from 'vitest'

import type { NodeSourceData } from '@cdd/harness/graph/graph'
import type { SessionFileData } from '@cdd/space/session/session'

import { calloutsOf, isStoryTest } from './source-of-file'

const STEP_STORY = 'story_tests/manage-tickets/remove-tickets/delete-ticket.story.shared.py'
const node = (node_id: string, name: string, owner: string, file: string, start_line: number, text: string): NodeSourceData =>
  ({ node_id, name, type: 'Operation', owner, file, start_line, end_line: start_line + text.split(String.fromCharCode(10)).length - 1, text, members: [] }) as NodeSourceData
const DELETE = node('delete', 'delete', 'Ticket', 'space/kanban/ticket.py', 8, '    def delete(self, board: Board) -> None:' + String.fromCharCode(10) + '        board.reread()')
const TICKET_ON_BOARD = node('ticket_on_board', 'ticket_on_board', '', 'space/kanban/ticket_story_examples.py', 1, 'def ticket_on_board(world) -> str:' + String.fromCharCode(10) + '    return "checkout"')
const call = (line: number, title: string, target: NodeSourceData) => ({ kind: 'call', line, title, target })

// Its Given on line 9 calls ticket_on_board on line 11, and its When on line 13 calls Ticket.delete on line 15.
const storyTest = {
  path: STEP_STORY,
  callouts: [],
  steps: [
    { line: 9, callouts: [call(11, 'ticket_on_board', TICKET_ON_BOARD)] },
    { line: 13, callouts: [call(15, 'Ticket.delete', DELETE)] },
  ],
} as unknown as SessionFileData

describe('Story Test Callouts', () => {
  describe("with Delete Ticket's shared story test, its Given invoking ticket_on_board and its When Ticket.delete", () => {
    it('should put each callout on the line and under the title the session answered', () => {
      expect(calloutsOf(storyTest).map(callout => [callout.line, callout.title, callout.path, callout.startLine])).toEqual([
        [11, 'ticket_on_board', 'space/kanban/ticket_story_examples.py', 1],
        [15, 'Ticket.delete', 'space/kanban/ticket.py', 8],
      ])
    })

    it('should open no call or class its code or docstring names, its callouts being its steps own', () => {
      expect(isStoryTest(storyTest)).toBe(true)
    })
  })
})

describe('Connector Fold-outs Show Only Code', () => {
  describe("with a step invoking an operation whose text the graph marks with its calls", () => {
    it('should show the operation without the call markers', () => {
      const marked = { ...DELETE, text: `${DELETE.text} /* call:reread */` } as NodeSourceData
      const file = { ...storyTest, steps: [{ line: 13, callouts: [call(15, 'Ticket.delete', marked)] }] } as unknown as SessionFileData
      expect(calloutsOf(file)[0]!.text).toBe(DELETE.text)
    })
  })
})
