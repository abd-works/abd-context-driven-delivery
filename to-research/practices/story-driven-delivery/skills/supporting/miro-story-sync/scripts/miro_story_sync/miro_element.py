"""Miro item element: parallel of ``DrawIOElement`` for the Miro REST API.

A ``MiroElement`` carries the same logical attributes as its DrawIO sibling
(``cell_id``, ``value``, ``position``, ``boundary``, fill / stroke / font
color / shape / aspect / align / font_style / font_size). Instead of
serialising to an XML ``mxCell`` it produces the JSON payload the Miro v2
items endpoints expect (``shape``, ``sticky_note``, ``text``).

Backends pick a Miro item kind per role (epic = shape rounded rectangle,
story = sticky_note, AC = text). The mapping lives in ``MIRO_SHAPE_BY_TYPE``
so it is easy to swap if a future Miro item type is preferred.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from . import _bootstrap  # noqa: F401

from diagram_story_sync.position import Position, Boundary
from diagram_story_sync.style_defaults import STYLE_DEFAULTS

__all__ = ['MiroElement', 'MIRO_SHAPE_BY_TYPE']


# Miro v2 supports several item types; we map each role onto a concrete one.
# All non-sticky_note items use ``shape`` with a ``shape`` style picker.
MIRO_SHAPE_BY_TYPE: Dict[str, Dict[str, str]] = {
    'epic':                 {'item_type': 'shape', 'shape': 'round_rectangle'},
    'sub_epic':             {'item_type': 'shape', 'shape': 'round_rectangle'},
    'story_user':           {'item_type': 'sticky_note'},
    'story_system':         {'item_type': 'sticky_note'},
    'story_technical':      {'item_type': 'sticky_note'},
    'actor':                {'item_type': 'sticky_note'},
    'acceptance_criteria':  {'item_type': 'shape', 'shape': 'rectangle'},
    'ac':                   {'item_type': 'shape', 'shape': 'rectangle'},
    'increment_lane':       {'item_type': 'shape', 'shape': 'rectangle'},
}


class MiroElement:
    """Backend-agnostic element record that knows how to become a Miro item dict.

    Held by ``MiroStoryNode`` instances exactly the way ``DrawIOElement`` is
    held by ``DrawIOStoryNode``. Geometry uses Miro's centre-anchored
    coordinate system on output (``position.x`` / ``position.y`` here are the
    top-left like everywhere else in this codebase, and we translate when
    serialising).
    """

    def __init__(self, cell_id: str, value: str = '', element_type: str = ''):
        self._cell_id = cell_id
        self._value = value
        self._element_type = element_type
        self._position = Position(0, 0)
        self._boundary = Boundary(0, 0, 0, 0)
        self._fill: Optional[str] = None
        self._stroke: Optional[str] = None
        self._font_color: Optional[str] = None
        self._font_size: Optional[int] = None
        self._shape: Optional[str] = None
        self._aspect: Optional[str] = None
        self._align: Optional[str] = None
        self._font_style: Optional[str] = None

    @property
    def cell_id(self) -> str:
        return self._cell_id

    @property
    def value(self) -> str:
        return self._value

    @property
    def element_type(self) -> str:
        return self._element_type

    @property
    def position(self) -> Position:
        return self._position

    @property
    def boundary(self) -> Boundary:
        return self._boundary

    @property
    def fill(self) -> Optional[str]:
        return self._fill

    @property
    def stroke(self) -> Optional[str]:
        return self._stroke

    @property
    def font_color(self) -> Optional[str]:
        return self._font_color

    @property
    def shape(self) -> Optional[str]:
        return self._shape

    def set_position(self, x: float, y: float) -> None:
        self._position = Position(x, y)
        self._boundary = Boundary(x, y, self._boundary.width, self._boundary.height)

    def set_size(self, width: float, height: float) -> None:
        self._boundary = Boundary(self._position.x, self._position.y, width, height)

    def set_style(self, fill: Optional[str] = None, stroke: Optional[str] = None,
                  font_color: Optional[str] = None, shape: Optional[str] = None,
                  font_size: Optional[int] = None, align: Optional[str] = None,
                  font_style: Optional[str] = None,
                  aspect: Optional[str] = None) -> None:
        if fill is not None:
            self._fill = fill
        if stroke is not None:
            self._stroke = stroke
        if font_color is not None:
            self._font_color = font_color
        if shape is not None:
            self._shape = shape
        if font_size is not None:
            self._font_size = font_size
        if align is not None:
            self._align = align
        if font_style is not None:
            self._font_style = font_style
        if aspect is not None:
            self._aspect = aspect

    def apply_style_for_type(self, element_type: str) -> None:
        """Pick fill / stroke / font from ``STYLE_DEFAULTS`` for the role."""
        self._element_type = element_type
        style = STYLE_DEFAULTS.get(element_type, {})
        self.set_style(**style)

    # ------------------------------------------------------------------
    # Miro REST API serialisation
    # ------------------------------------------------------------------

    def to_miro_payload(self) -> Dict[str, Any]:
        """JSON body the Miro v2 ``POST .../{board}/items`` endpoint accepts.

        Miro's coordinate system is centred (positive Y is *down*); the rest
        of this codebase uses top-left positions, so translate width/height to
        Miro's *centre* convention here.
        """
        kind = MIRO_SHAPE_BY_TYPE.get(self._element_type, {'item_type': 'shape',
                                                            'shape': 'rectangle'})
        item_type = kind['item_type']

        payload: Dict[str, Any] = {
            'data': {'content': self._value or ''},
            'position': self._miro_position(item_type),
            'geometry': self._miro_geometry(item_type),
        }
        if item_type == 'shape':
            payload['data']['shape'] = kind.get('shape', 'rectangle')
            payload['style'] = self._miro_style(item_type='shape')
        elif item_type == 'sticky_note':
            payload['style'] = self._miro_style(item_type='sticky_note')

        return {'item_type': item_type, 'payload': payload}

    def _miro_position(self, item_type: str = 'shape') -> Dict[str, Any]:
        # Miro positions an item at its centre.
        cx = self._position.x + self._boundary.width / 2.0
        cy = self._position.y + self._boundary.height / 2.0
        # sticky_notes use PositionChange (x, y only); shapes/frames/text use
        # Position (x, y, origin).
        if item_type == 'sticky_note':
            return {'x': cx, 'y': cy}
        return {'x': cx, 'y': cy, 'origin': 'center'}

    def _miro_geometry(self, item_type: str = 'shape') -> Dict[str, float]:
        # sticky_notes have a fixed aspect ratio — send width only.
        if item_type == 'sticky_note':
            return {'width': self._boundary.width}
        return {'width': self._boundary.width, 'height': self._boundary.height}

    def _miro_style(self, item_type: str) -> Dict[str, Any]:
        style: Dict[str, Any] = {}
        if item_type == 'sticky_note':
            # Sticky notes only accept fillColor, textAlign, textAlignVertical.
            if self._fill:
                style['fillColor'] = _approximate_sticky_color(self._fill)
            if self._align:
                style['textAlign'] = self._align
        else:
            # Shapes, frames, text items.
            if self._fill:
                style['fillColor'] = self._fill
            if self._stroke:
                style['borderColor'] = self._stroke
            if self._font_color:
                style['color'] = self._font_color
            if self._font_size:
                style['fontSize'] = self._font_size
            if self._align:
                style['textAlign'] = self._align
            if self._font_style == 'bold':
                style['fontFamily'] = 'open_sans'
                style['textAlign'] = style.get('textAlign', 'center')
        return style

    @classmethod
    def from_miro_item(cls, item: Dict[str, Any]) -> 'MiroElement':
        """Reverse of ``to_miro_payload`` for items returned by the API.

        Restores ``cell_id`` from a Miro tag / metadata key when present,
        otherwise falls back to the Miro item id. Position is converted from
        Miro's centre origin back to top-left.
        """
        item_id = str(item.get('id', ''))
        data = item.get('data') or {}
        content = data.get('content') or ''
        cell_id = (item.get('metadata') or {}).get('story_sync_cell_id', item_id)

        elem = cls(cell_id=cell_id, value=content,
                   element_type=item.get('metadata', {}).get('story_sync_role', ''))

        geom = item.get('geometry') or {}
        width = float(geom.get('width', 0.0))
        height = float(geom.get('height', 0.0))
        pos = item.get('position') or {}
        cx = float(pos.get('x', 0.0))
        cy = float(pos.get('y', 0.0))
        elem.set_position(cx - width / 2.0, cy - height / 2.0)
        elem.set_size(width, height)

        style = item.get('style') or {}
        if 'fillColor' in style:
            elem._fill = style['fillColor']
        if 'borderColor' in style:
            elem._stroke = style['borderColor']
        if 'textColor' in style:
            elem._font_color = style['textColor']
        if 'fontSize' in style:
            try:
                elem._font_size = int(style['fontSize'])
            except (TypeError, ValueError):
                pass
        return elem


def _approximate_sticky_color(hex_color: str) -> str:
    """Map a hex fill to one of Miro's sticky-note colour names.

    Miro sticky notes only accept a fixed palette (``yellow``, ``light_yellow``,
    ``dark_blue``, ``black``, ``light_blue``, ...). We pick the closest match
    for the colors in ``STYLE_DEFAULTS`` so the produced board matches the
    DrawIO outline at a glance.
    """
    palette = {
        '#fff2cc': 'yellow',
        '#1a237e': 'dark_blue',
        '#000000': 'black',
        '#dae8fc': 'light_blue',
        '#d5e8d4': 'light_green',
        '#e1d5e7': 'violet',
        '#f5f5f5': 'gray',
    }
    return palette.get(hex_color.lower(), 'yellow')
