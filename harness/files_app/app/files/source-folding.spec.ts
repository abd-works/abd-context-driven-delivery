// Which folds a selected node opens, as the story Fold Open Files To Selected Nodes asks
// (story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/).
import { describe, expect, it } from 'vitest'

import { linesToUnfold } from '@source-view/source-folding'

// Delete Ticket's Python shared story test: its Given's decorator on line 9 and its function on line 10, its When's
// decorator on line 13 and its function on line 14.
const STEP_STORY = [
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
].join('\n')

describe('Folds a selected node opens', () => {
  describe('with a step of a Python story test selected, its decorator first', () => {
    it("should unfold the step's function under its decorator, as well as the folds around it", () => {
      expect(linesToUnfold(STEP_STORY, [{ start: 9, end: 11 }])).toEqual([9, 10])
    })
  })

  describe('with an operation selected on its own first line', () => {
    it('should unfold the folds around that line alone', () => {
      expect(linesToUnfold(STEP_STORY, [{ start: 14, end: 15 }])).toEqual([14])
    })
  })

  describe('with two nodes selected', () => {
    it("should unfold each node's own lines", () => {
      expect(linesToUnfold(STEP_STORY, [{ start: 9, end: 11 }, { start: 13, end: 15 }])).toEqual([9, 10, 13, 14])
    })
  })
})
