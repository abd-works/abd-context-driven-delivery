import { boardHolding, itemJson, placedTicket } from 'test-utils/board-examples'
import type { ExampleAnswers, PostedExample } from 'test-utils/behavior-test/example-api'

const readyToMove = placedTicket('ready-to-move', 'Discovery', { is_done: true })
const moveMe = placedTicket('move-me', 'Discovery')
const backToBacklog = placedTicket('back-to-backlog', 'Discovery')
const pricingRules = placedTicket('pricing-rules', 'Specification')
const almostShipped = placedTicket('almost-shipped', 'Implementation', { is_done: true })
const others = [readyToMove, moveMe, backToBacklog, pricingRules, almostShipped]

const replacing = (moved: ReturnType<typeof placedTicket>) => [...others.filter(ticket => ticket.name !== moved.name), moved]

const answering = (moved: ReturnType<typeof placedTicket>) => ({ body: moved, board: boardHolding(replacing(moved)) })

// A drop onto a stage's list moves the ticket to the stage and list it names, wherever it was.
const droppedOn =
  (ticket: ReturnType<typeof placedTicket>): PostedExample =>
  posted =>
    answering({ ...ticket, column: String(posted.stage), is_done: Boolean(posted.done) })

export const BOARD_BEFORE_MOVES = boardHolding(others)

export const MOVES: ExampleAnswers = {
  'POST /api/ticket/ready-to-move/move-to': droppedOn(readyToMove),
  'POST /api/ticket/move-me/move-to': droppedOn(moveMe),
  'POST /api/ticket/pricing-rules/move-to': droppedOn(pricingRules),
  'POST /api/ticket/almost-shipped/move-to': droppedOn(almostShipped),
  'POST /api/ticket/back-to-backlog/move-previous': {
    body: itemJson('Back to backlog'),
    board: boardHolding(others.filter(ticket => ticket !== backToBacklog), [itemJson('Back to backlog')]),
  },
  'POST /api/ticket/almost-shipped/move-next': answering({ ...almostShipped, column: 'Complete' }),
}
