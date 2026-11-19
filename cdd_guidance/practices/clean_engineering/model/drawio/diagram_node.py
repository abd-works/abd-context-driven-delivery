"""Draw.io placed cells: mxCell write plus Draw.io styles."""
from __future__ import annotations

import html
import math
import re
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple

from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass
from cdd_guidance.practices.clean_engineering.model.drawio.page.drawio_page import style_value
from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import (
    DiagramClass,
    DiagramModule,
    ImportedClass,
)

CLASS_STYLE = (
    'verticalAlign=top;align=left;overflow=fill;fontSize=12;'
    'fontFamily=Helvetica;html=1;whiteSpace=wrap;'
)
IMPORTED_CLASS_STYLE = CLASS_STYLE + 'dashed=1;dashPattern=8 8;strokeColor=#666666;'
MODULE_STYLE = (
    'rounded=1;whiteSpace=wrap;html=1;fillColor=#1a3a6e;strokeColor=#0e2547;'
    'fontColor=#ffffff;fontSize=12;align=left;verticalAlign=top;'
    'spacingLeft=10;spacingTop=10;strokeWidth=3;'
)
MODULE_CHILD_STYLE = (
    'rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;'
    'fontColor=#000000;fontSize=12;align=left;verticalAlign=top;'
    'spacingLeft=10;spacingTop=10;strokeWidth=2;'
)


MEMBER_CHARACTER_WIDTH = 5.5
CARD_TEXT_PADDING = 18
CARD_MIN_WIDTH = 200
CARD_WIDTH_STEP = 20


class DrawioVertex:
    """A placed node written as one Draw.io vertex cell: its HTML label, its style, and its box."""

    def append_to(self, root_el: ET.Element) -> ET.Element:
        cell = ET.SubElement(root_el, 'mxCell')
        cell.set('id', self.cell_id)
        cell.set('value', self.html())
        cell.set('style', self.style())
        cell.set('vertex', '1')
        cell.set('parent', self.parent_id)
        geo = ET.SubElement(cell, 'mxGeometry')
        geo.set('x', str(int(self.geometry.x)))
        geo.set('y', str(int(self.geometry.y)))
        geo.set('width', str(int(self.geometry.width)))
        geo.set('height', str(int(self.geometry.height)))
        geo.set('as', 'geometry')
        return cell


class DrawIOClass(DiagramClass, DrawioVertex):
    """Draw.io UML class cell."""

    fill_color = ''
    owning_module = ''

    def width(self) -> int:
        """Wide enough that no line wraps, because the height counts one printed line per member."""
        longest = max((len(line) for line in self._member_lines()), default=0)
        wanted = longest * MEMBER_CHARACTER_WIDTH + CARD_TEXT_PADDING
        return max(CARD_MIN_WIDTH, math.ceil(wanted / CARD_WIDTH_STEP) * CARD_WIDTH_STEP)

    def html(self) -> str:
        name_html = html.escape(self.name)
        stereo = self._stereotype_html()
        return (
            f'<p style="margin:0px;margin-top:4px;text-align:center;">'
            f'{stereo}<b>{name_html}</b></p><hr size="1"/>'
            f'<p style="margin:0px;margin-left:4px;font-size:10px;">{self._properties_html()}</p>'
            f'<hr size="1"/>'
            f'<p style="margin:0px;margin-left:4px;font-size:10px;">{self._operations_html()}</p>'
            f'{"".join(item.folded_html() for item in self.folded)}'
        )

    def folded_html(self) -> str:
        """This class drawn inside another's card: a rule, its stereotypes and name as its own heading, then its
        properties and operations, each under a rule as on a card of its own."""
        return (
            f'<hr size="1"/>'
            f'<p style="margin:0px;margin-top:4px;text-align:center;">{self._stereotype_html()}<b>{html.escape(self.name)}</b></p>'
            f'<hr size="1"/>'
            f'<p style="margin:0px;margin-left:4px;font-size:10px;">{self._properties_html()}</p>'
            f'<hr size="1"/>'
            f'<p style="margin:0px;margin-left:4px;font-size:10px;">{self._operations_html()}</p>'
        )

    def style(self) -> str:
        """The class style, with the owning module recorded so parse puts the class back in it."""
        fill = f'fillColor={self.fill_color};strokeColor=#666666;' if self.fill_color else ''
        module = f'module={self.owning_module};' if self.owning_module else ''
        return f'{CLASS_STYLE}{fill}{module}'

    def _operation_lines(self) -> List[str]:
        return [
            f"{('- ' if op.name.startswith('_') else '+ ')}"
            f"{op.name}({', '.join(parameter.save() for parameter in op.parameters)})"
            f"{(': ' + op.return_type if op.return_type else '')}"
            for op in self.operations
        ]

    def _member_lines(self) -> List[str]:
        own = [self.name] + self.property_lines() + self._operation_lines()
        return own + [line for item in self.folded for line in item._member_lines()]

    def _properties_html(self) -> str:
        return ''.join(f'{html.escape(line)}<br/>' for line in self.property_lines()) or '<br/>'

    def _operations_html(self) -> str:
        return ''.join(f'{html.escape(line)}<br/>' for line in self._operation_lines()) or '<br/>'

    def _stereotype_html(self) -> str:
        """The class's stereotypes as `<<Mark>>`s in small italics above its name, where parse reads them back."""
        if not self.stereotypes:
            return ''
        label = ' '.join(f'<<{item}>>' for item in self.stereotypes)
        return f'<i style="font-size:9px;color:#888;">{html.escape(label)}</i><br/>'


class DrawIOImportedClass(ImportedClass, DrawIOClass):
    """Dashed Draw.io card for a class owned by another aggregate."""

    def html(self) -> str:
        name_html = html.escape(self.name)
        from_html = html.escape(f'«from: {self.from_module}»')
        props_html = ''.join(
            (
                f"+ {html.escape(p.name)}"
                f"{(': ' + html.escape(p.type_hint) if p.type_hint else '')}<br/>"
                for p in self.key_properties()
            )
        ) or '<br/>'
        stereo = self._stereotype_html()
        return (
            f'<p style="margin:0px;margin-top:2px;text-align:center;font-size:10px;">'
            f'<i>{from_html}</i></p>'
            f'<p style="margin:0px;text-align:center;">{stereo}<b>{name_html}</b></p>'
            f'<hr size="1"/>'
            f'<p style="margin:0px;margin-left:4px;font-size:10px;">{props_html}</p>'
            f'<hr size="1"/>'
            f'<p style="margin:0px;margin-left:4px;font-size:10px;"><br/></p>'
        )

    def style(self) -> str:
        return IMPORTED_CLASS_STYLE


class DrawIOModule(DiagramModule, DrawioVertex):
    """Draw.io rounded modules-view cell."""

    class_type = DrawIOClass

    KIND = ""
    """The kind of module a cell draws, written in its style as `kind=...;` so the drawing reads back as the cell type
    that drew it; a plain module names none."""

    def html(self) -> str:
        name_html = html.escape(self.name)
        purpose_html = html.escape(self.purpose_line())
        terms = self.public_terms()
        if not terms:
            return f'<b style="font-size: 14px;">{name_html}</b><br><i>{purpose_html}</i>'
        bullets = self._seam_bullets()
        return (
            f'<b style="font-size: 14px;">{name_html}</b><br><i>{purpose_html}</i>'
            f'<hr>{bullets}'
        )

    def style(self) -> str:
        kind = f'kind={self.KIND};' if self.KIND else ''
        return (MODULE_CHILD_STYLE if self.nested else MODULE_STYLE) + kind

    @classmethod
    def from_cell(cls, cell: ET.Element, sequential_order: int) -> Optional['DrawIOModule']:
        """The module a modules-view cell shows, read from the cell's HTML label; None when the cell's style names
        another kind than this type's, or the label names no module. A plain module reads a cell of any kind, so a
        reader that knows no kind of its own reads every cell as a plain module."""
        if cls.KIND and style_value(cell.get('style', ''), 'kind') != cls.KIND:
            return None
        label_html = html.unescape(cell.get('value', ''))
        bold = re.search('<b[^>]*>([^<]+)</b>', label_html, re.IGNORECASE)
        name = bold.group(1).strip() if bold else None
        if not name:
            return None
        return cls(name=name, sequential_order=sequential_order).take_label(label_html)

    def take_label(self, label_html: str) -> 'DrawIOModule':
        """Become the module a cell's label shows: its purpose and seam terms."""
        self.description = self._purpose_in(label_html)
        self.seam_terms = self._terms_in(label_html)
        return self

    def _seam_bullets(self) -> str:
        shown = self.shown_seam_terms()
        return '<br>'.join((f'• {html.escape(t)}' for t in shown))

    def _purpose_in(self, label_html: str) -> str:
        italic = re.search('<i[^>]*>([^<]*)</i>', label_html, re.IGNORECASE)
        return italic.group(1).strip() if italic else ''

    def _terms_in(self, label_html: str) -> List[str]:
        """The seam terms the label bullets, skipping a `{placeholder}`; else its list items that name no stack."""
        # A bullet starts the label or follows a tag, so the dash in a style such as `font-size` is not one.
        bullets = (bullet.strip() for bullet in re.findall(r'(?:^|>)\s*[•\-]\s*([^<]+)', label_html))
        terms = [term for term in bullets if term and not (term.startswith('{') and term.endswith('}'))]
        if terms:
            return terms
        items = (item.strip() for item in re.findall('<li[^>]*>(?:<[^>]+>)*([^<]+)', label_html, re.IGNORECASE))
        return [item for item in items if item and 'stack' not in item.lower()]
