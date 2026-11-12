"""The session board: the board and its columns (board.py), the tickets on it (ticket.py), and the ideas in its Backlog
(backlog_item.py). Tickets and backlog items build on the board, so the board is handed their classes here, when the
package is first imported, and board.py imports neither back."""

from space.kanban.board import Board
from space.kanban.backlog_item import BacklogItem
from space.kanban.ticket import Ticket

Board.places_cards(Ticket, BacklogItem)

# The apps the board's server serves register with App when this package is imported, so the server health report lists them.
import space.kanban.board_app  # noqa: E402,F401
