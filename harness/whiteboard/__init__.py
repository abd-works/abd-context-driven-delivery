"""A Claude Whiteboard board and its elements, which every practice's whiteboard format draws on:
``from harness.whiteboard import Whiteboard``. A practice makes elements with *BoardElement*'s factories and reads them
back through the board (``sections``, ``shapes``, ``labels``, ``arrows``); the kinds behind them stay in the module."""
from .whiteboard import MAX_SIDE, BoardElement, BoardLinks, Box, UnreadableBoard, Whiteboard, WhiteboardNode  # noqa: F401
