import { boardHolding, itemJson, placedTicket } from 'test-utils/board-examples'
import type { ExampleAnswers } from 'test-utils/behavior-test/example-api'

const searchItem = itemJson('Search the catalog', 'An idea.')
const giftCards = itemJson('Gift cards', 'Sell them at the till.')
const backToBacklog = placedTicket('back-to-backlog', 'Discovery', { progress: { 'stories-story_map': 'in_progress' } })
const heldItem = itemJson('Back to backlog')
const startedSearch = placedTicket('search-the-catalog', 'Discovery', { title: 'Search the catalog' })

export const BOARD_BEFORE_ITEMS = boardHolding([backToBacklog], [searchItem])

export const ITEM_ANSWERS: ExampleAnswers = {
  'POST /api/backlog': { body: giftCards, board: boardHolding([backToBacklog], [searchItem, giftCards]) },
  'POST /api/backlog/Search%20the%20catalog/start': { body: startedSearch, board: boardHolding([backToBacklog, startedSearch]) },
  'POST /api/tickets/back-to-backlog/move-previous': { body: heldItem, board: boardHolding([], [searchItem, heldItem]) },
  'POST /api/backlog/Back%20to%20backlog/start': { body: backToBacklog, board: boardHolding([backToBacklog], [searchItem]) },
}
