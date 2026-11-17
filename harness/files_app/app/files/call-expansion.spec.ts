// Which calls and classes a line opens in place, as the story Open Calls Across Files In Files App asks
// (story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/).
import { describe, expect, it } from 'vitest'

import { CallCatalog, type FoldMember } from '@source-view/call-expansion'

// ticket.py: the class Ticket on lines 1 to 9, its close on lines 2 to 3 and its delete on lines 5 to 9, which calls
// self.close(), the module function reread_all, and names the class Board; reread_all on lines 12 to 13.
const TICKET_PY = [
  'class Ticket:',
  '    def close(self) -> None:',
  '        return None',
  '',
  '    def delete(self, board: Board) -> None:',
  '        self.close()',
  '        reread_all(board)',
  '        Board.reread(board)',
  '        return None',
  '',
  '',
  'def reread_all(board) -> None:',
  '    board.reread()',
].join('\n')

const lines = (from: number, to: number) => TICKET_PY.split('\n').slice(from - 1, to).join('\n')

const MEMBERS: FoldMember[] = [
  { node_id: 'Ticket', name: 'Ticket', type: 'OoadClass', owner: '', text: lines(1, 9), file: 'space/kanban/ticket.py', start_line: 1, end_line: 9 },
  { node_id: 'Ticket.close', name: 'close', type: 'Operation', owner: 'Ticket', text: lines(2, 3), file: 'space/kanban/ticket.py', start_line: 2, end_line: 3 },
  { node_id: 'Ticket.delete', name: 'delete', type: 'Operation', owner: 'Ticket', text: lines(5, 9), file: 'space/kanban/ticket.py', start_line: 5, end_line: 9 },
  // A module's function is owned by `_module`, as session.graph_members answers it (Clean Engineering's
  // MODULE_FUNCTION_HOLDER, cdd_guidance/practices/clean_engineering/model/base_class_model.py).
  { node_id: 'reread_all', name: 'reread_all', type: 'Operation', owner: '_module', text: lines(12, 13), file: 'space/kanban/ticket.py', start_line: 12, end_line: 13 },
  { node_id: 'Board', name: 'Board', type: 'OoadClass', owner: '', text: 'class Board:\n    def reread(self) -> None:\n        return None', file: 'space/kanban/board.py', start_line: 1, end_line: 3 },
  { node_id: 'Board.reread', name: 'reread', type: 'Operation', owner: 'Board', text: '    def reread(self) -> None:\n        return None', file: 'space/kanban/board.py', start_line: 2, end_line: 3 },
]

const calloutsOf = (catalog: CallCatalog) => catalog.calloutsIn(TICKET_PY, 1, 'python', ['ticket.py'], 'space/kanban/ticket.py')
const opened = (line: number) => calloutsOf(new CallCatalog(MEMBERS)).filter(callout => callout.line === line).map(callout => callout.id)

describe('Calls and classes a line opens in place', () => {
  describe('with a line inside the class it names', () => {
    it('should never open the class it sits in', () => {
      expect(calloutsOf(new CallCatalog(MEMBERS)).filter(callout => callout.id === 'Ticket')).toEqual([])
    })

    it('should still open another class it names', () => {
      expect(opened(5)).toContain('Board')
    })
  })

  describe('with the open file named from the project and its members named from their practice root', () => {
    it('should still never open the class it sits in', () => {
      const fromProject = new CallCatalog(MEMBERS).calloutsIn(TICKET_PY, 1, 'python', ['ticket.py'], 'repo/space/kanban/ticket.py')
      expect(fromProject.filter(callout => callout.id === 'Ticket')).toEqual([])
    })
  })

  describe('with another file defining a class of the same name, read first', () => {
    // Seen live 2026-11-16: `class AppServer:` in harness/diagnostics/app.py opened another file's AppServer.
    const OTHER_TICKET: FoldMember[] = [
      { node_id: 'old/Ticket', name: 'Ticket', type: 'OoadClass', owner: '', text: 'class Ticket:\n    def close(self):\n        pass', file: 'old/ticket.py', start_line: 1, end_line: 3 },
      { node_id: 'old/Ticket.close', name: 'close', type: 'Operation', owner: 'Ticket', text: '    def close(self):\n        pass', file: 'old/ticket.py', start_line: 2, end_line: 3 },
    ]
    const both = new CallCatalog([...OTHER_TICKET, ...MEMBERS])
    const at = (line: number) => calloutsOf(both).filter(callout => callout.line === line).map(callout => callout.id)

    it('should open neither Ticket on the lines of the open file\'s own Ticket', () => {
      expect(calloutsOf(both).filter(callout => callout.id === 'Ticket' || callout.id === 'old/Ticket')).toEqual([])
    })

    it("should open the open file's own Ticket.close for a call on self", () => {
      expect(at(6)).toEqual(['Ticket.close'])
    })
  })

  describe("with a method's call on self", () => {
    it('should open the method of the class around it', () => {
      expect(opened(6)).toEqual(['Ticket.close'])
    })
  })

  describe('with a call to a module function by its bare name', () => {
    it('should open that function', () => {
      expect(opened(7)).toEqual(['reread_all'])
    })
  })

  describe('with an operation its own call names', () => {
    it('should never open the operation it sits in', () => {
      expect(calloutsOf(new CallCatalog(MEMBERS)).filter(callout => callout.id === 'Ticket.delete')).toEqual([])
    })
  })
})
