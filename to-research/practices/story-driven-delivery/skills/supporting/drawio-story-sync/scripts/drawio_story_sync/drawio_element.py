from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from . import _bootstrap  # noqa: F401

from diagram_story_sync.style_defaults import STYLE_DEFAULTS  # noqa: F401

from .story_io_position import Position, Boundary


class DrawIOElement:

    def __init__(self, cell_id: str, value: str = ''):
        self._cell_id = cell_id
        self._value = value
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

    def set_position(self, x: float, y: float):
        self._position = Position(x, y)
        self._boundary = Boundary(x, y, self._boundary.width, self._boundary.height)

    def set_size(self, width: float, height: float):
        self._boundary = Boundary(self._position.x, self._position.y, width, height)

    def set_style(self, fill: str = None, stroke: str = None, font_color: str = None,
                  shape: str = None, font_size: int = None, align: str = None,
                  font_style: str = None, aspect: str = None):
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

    def apply_style_for_type(self, element_type: str):
        style = STYLE_DEFAULTS.get(element_type, {})
        self.set_style(**style)

    def set_style_from_string(self, style_string: str):
        """Parse a Draw.io style string and apply its values."""
        parsed = self.from_style_string(style_string)
        if 'shape' in parsed:
            self._shape = parsed['shape']
        elif 'rounded' in parsed and parsed['rounded'] == '1':
            self._shape = 'rounded'
        if 'fillColor' in parsed:
            self._fill = parsed['fillColor']
        if 'strokeColor' in parsed:
            self._stroke = parsed['strokeColor']
        if 'fontColor' in parsed:
            self._font_color = parsed['fontColor']
        if 'fontSize' in parsed:
            try:
                self._font_size = int(parsed['fontSize'])
            except ValueError:
                pass
        if 'align' in parsed:
            self._align = parsed['align']
        if 'fontStyle' in parsed and parsed['fontStyle'] == '1':
            self._font_style = 'bold'
        if 'aspect' in parsed and parsed['aspect'] == 'fixed':
            self._aspect = 'fixed'

    def to_style_string(self) -> str:
        """Generate Draw.io style string matching reference diagram format."""
        parts = []
        if self._shape == 'rounded':
            parts.append('rounded=1')
        parts.append('whiteSpace=wrap')
        parts.append('html=1')
        parts.append('overflow=hidden')
        if self._aspect == 'fixed':
            parts.append('aspect=fixed')
        if self._fill:
            parts.append(f'fillColor={self._fill}')
        if self._stroke:
            parts.append(f'strokeColor={self._stroke}')
        if self._font_color:
            parts.append(f'fontColor={self._font_color}')
        if self._font_size:
            parts.append(f'fontSize={self._font_size}')
        if self._align:
            parts.append(f'align={self._align}')
        if self._font_style == 'bold':
            parts.append('fontStyle=1')
        return ';'.join(parts) + ';'

    @classmethod
    def from_style_string(cls, style_string: str) -> Dict[str, str]:
        result = {}
        for part in style_string.split(';'):
            if '=' in part:
                key, val = part.split('=', 1)
                result[key] = val
        return result
