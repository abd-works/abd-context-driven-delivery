"""A Claude Whiteboard board and its elements, which every practice's whiteboard format draws on:
``from harness.whiteboard import Whiteboard``. A practice builds its elements directly (*Shape*, *Section*, *Label*,
*Arrow*), each under an *ElementId*, and reads them back through the board (``sections``, ``shapes``, ``labels``,
``arrows``)."""
from .whiteboard import MAX_SIDE, Arrow, BoardElement, Box, ElementId, KeepsDocumentOnBoard, Label, Section, Shape, UnreadableBoard, Whiteboard, WhiteboardNode  # noqa: F401
