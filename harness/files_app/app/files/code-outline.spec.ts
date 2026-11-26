// A Code File Opens With Its Classes Open And Their Members Folded, as story_tests/review-generated-work-in-file-viewer/
// open-graph-nodes-in-files-app/open_graph_nodes_in_files_app_story.test.md writes it. Only the
// page folds: these are the lines whose folds close as a code file opens with no node selected.
import { describe, expect, it } from 'vitest'

import { memberLines } from './code-outline'

const TICKET_PY = [
  'from dataclasses import dataclass', // 1
  '', // 2
  '', // 3
  'class Ticket:', // 4
  '    """A card on the board."""', // 5
  '', // 6
  '    def activate(self) -> None:', // 7
  '        if self.closed:', // 8
  '            return', // 9
  '        self.active = True', // 10
  '', // 11
  '    @property', // 12
  '    async def close(self) -> None:', // 13
  '        def mark():', // 14
  '            pass', // 15
  '        mark()', // 16
  '', // 17
  '', // 18
  'def ticket_on_board(board):', // 19
  '    return board.tickets[0]', // 20
].join('\n')

const FILES_GRAPH_TS = [
  "import { FoldKeys } from './fold'", // 1
  '', // 2
  'export class FilesGraph {', // 3
  '  private readonly nodes: string[] = []', // 4
  '', // 5
  '  constructor(private readonly session: Session) {}', // 6
  '', // 7
  '  async filterTo(filter: string): Promise<void> {', // 8
  '    if (!filter) {', // 9
  '      return', // 10
  '    }', // 11
  '  }', // 12
  '', // 13
  '  private get shown(): string[] {', // 14
  "    return this.nodes.filter(node => node !== '{')", // 15
  '  }', // 16
  '', // 17
  '  readonly select = (node: string): void => {', // 18
  '    this.nodes.push(node)', // 19
  '  }', // 20
  '}', // 21
  '', // 22
  'export function graphOf(text: string): string {', // 23
  '  return text', // 24
  '}', // 25
].join('\n')

describe('A code file opened with no node selected', () => {
  describe('with a Python class', () => {
    it("should fold each of the class's operations at its first line, leaving the class and the module's functions open", () => {
      expect(memberLines(TICKET_PY, 'python')).toEqual([7, 13])
    })
  })

  describe('with a TypeScript class', () => {
    it("should fold each of the class's operations at its first line, leaving the class and the module's functions open", () => {
      expect(memberLines(FILES_GRAPH_TS, 'typescript')).toEqual([8, 14, 18])
    })
  })

  describe('with a markdown file', () => {
    it('should fold nothing', () => {
      expect(memberLines('# Checkout\n\n## Pay\n', 'markdown')).toEqual([])
    })
  })
})
