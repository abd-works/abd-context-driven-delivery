import type { BoardData } from '@cdd/harness/kanban/board'
import { boardHolding, placedTicket } from 'test-utils/board-examples'
import type { ExampleAnswers } from 'test-utils/behavior-test/example-api'

const tickets = [placedTicket('pricing-rules', 'Specification'), placedTicket('second-spec', 'Specification')]

export const BOARD_BEFORE_LIMITS = boardHolding(tickets)

const limited: BoardData = {
  ...BOARD_BEFORE_LIMITS,
  columns: BOARD_BEFORE_LIMITS.columns.map(column => (column.name === 'Specification' ? { ...column, wip_limit: 1, is_over_limit: true } : column)),
}

export const LIMIT_ANSWERS: ExampleAnswers = {
  'POST /api/board/wip-limit': { body: limited, board: limited },
}
