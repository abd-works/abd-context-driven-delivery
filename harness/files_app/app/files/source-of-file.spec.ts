// Follow Story Steps To Code, as story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/
// switch_files_app_between_files_and_graph_story.test.md writes it. The session answers each step of a story test with
// what it invokes and observes (`.story.shared.py`); the page puts each on its step's line and opens no call of its own.
import { describe, expect, it } from 'vitest'

import type { NodeSourceData } from '@cdd/harness/graph/graph'
import type { SessionFileData } from '@cdd/space/session/session'

import { calloutsOf, expandedLines, isStoryTest } from './source-of-file'

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

// The same story test with its text: its When on line 13 calls delete on line 15, its Then on line 17 observes the example
// CHECKOUT_TICKET on line 19 (space/kanban/graph_view_examples.py, STEP_STORY_TEXT).
const STEP_STORY_TEXT = [
  '"""Delete Ticket: a Ticket leaves the board."""',
  'from space.kanban.story_test import SharedStories',
  'from space.kanban.ticket_story_examples import CHECKOUT_TICKET, ticket_on_board',
  '',
  'shared_stories = SharedStories("Remove Tickets")',
  '',
  '@shared_stories.scenario("Delete Ticket", "a ticket on the board is deleted")',
  'def _(s):',
  '    @s.given("a ticket on the board")',
  '    def _(world):',
  '        world.ticket = ticket_on_board(world)',
  '',
  '    @s.when("the Person deletes it")',
  '    def _(world):',
  '        world.ticket.delete(world.board)',
  '',
  '    @s.then("the checkout ticket is gone")',
  '    def _(world):',
  '        assert ticket_left(world) == CHECKOUT_TICKET',
].join(String.fromCharCode(10))
const CHECKOUT_TICKET = { node_id: 'CHECKOUT_TICKET', name: 'CHECKOUT_TICKET', type: 'Example', owner: '', file: 'space/kanban/ticket_story_examples.py', start_line: 5, end_line: 5, text: 'CHECKOUT_TICKET = "checkout"', members: [] } as unknown as NodeSourceData
const storyTestWithText = {
  ...storyTest,
  text: STEP_STORY_TEXT,
  steps: [{ line: 9, invokes: [TICKET_ON_BOARD], observes: [] }, { line: 13, invokes: [DELETE], observes: [] }, { line: 17, invokes: [], observes: [CHECKOUT_TICKET] }],
} as unknown as SessionFileData

describe('Connectors Fold Out Where They Are Used', () => {
  describe("with Delete Ticket's story test and its text", () => {
    it('should put each connector on the line of its step that uses it, collapsed until opened', () => {
      expect(calloutsOf(storyTestWithText).map(callout => [callout.line, callout.title])).toEqual([
        [11, 'ticket_on_board'],
        [15, 'Ticket.delete'],
        [19, 'CHECKOUT_TICKET'],
      ])
    })
  })
})

describe('Connector Fold-outs Show Only Code', () => {
  describe("with a step invoking an operation whose text the graph marks with its calls", () => {
    it('should show the operation without the call markers', () => {
      const marked = { ...DELETE, text: `${DELETE.text} /* call:reread */` } as NodeSourceData
      const file = { ...storyTestWithText, steps: [{ line: 13, invokes: [marked], observes: [] }] } as unknown as SessionFileData
      expect(calloutsOf(file)[0]!.text).toBe(DELETE.text)
    })
  })
})

describe('Expand A Connector Inside Its Holder Only', () => {
  describe('with CHECKOUT_TICKET observed by the Then on line 17, and the Person selecting it under the scenario on lines 7 to 19', () => {
    const callouts = calloutsOf(storyTestWithText)
    const elsewhere = { ...callouts[2]!, line: 40 }

    it('should open it on line 19, where the scenario uses it, and nowhere else in the file', () => {
      expect(expandedLines([...callouts, elsewhere], ['CHECKOUT_TICKET'], [{ start: 7, end: 19 }])).toEqual([19])
    })
  })
})
