import { boardHolding, itemJson, placedTicket } from 'test-utils/board-examples'
import type { ExampleAnswers } from 'test-utils/behavior-test/example-api'

const readyToMove = placedTicket('ready-to-move', 'Discovery', { is_done: true })
const moveMe = placedTicket('move-me', 'Discovery')
const backToBacklog = placedTicket('back-to-backlog', 'Discovery')
const pricingRules = placedTicket('pricing-rules', 'Specification')
const almostShipped = placedTicket('almost-shipped', 'Implementation', { is_done: true })
const others = [readyToMove, moveMe, backToBacklog, pricingRules, almostShipped]

const replacing = (moved: ReturnType<typeof placedTicket>) => [...others.filter(ticket => ticket.name !== moved.name), moved]

const answering = (moved: ReturnType<typeof placedTicket>) => ({ body: moved, board: boardHolding(replacing(moved)) })

export const BOARD_BEFORE_MOVES = boardHolding(others)

export const MOVES: ExampleAnswers = {
  'POST /api/tickets/ready-to-move/move-next': answering({ ...readyToMove, column: 'Specification', is_done: false }),
  'POST /api/tickets/move-me/move-next': answering({ ...moveMe, is_done: true }),
  'POST /api/tickets/move-me/move-previous': answering(moveMe),
  'POST /api/tickets/pricing-rules/move-previous': answering({ ...pricingRules, column: 'Discovery', is_done: true }),
  'POST /api/tickets/back-to-backlog/move-previous': {
    body: itemJson('Back to backlog'),
    board: boardHolding(others.filter(ticket => ticket !== backToBacklog), [itemJson('Back to backlog')]),
  },
  'POST /api/tickets/almost-shipped/move-next': answering({ ...almostShipped, column: 'Complete' }),
  'POST /api/tickets/almost-shipped/move-previous': answering({ ...almostShipped, is_done: false }),
}
