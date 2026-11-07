"""Draw.io placed cells: mxCell write plus Draw.io styles."""
from __future__ import annotations

import html
import math
import re
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple

from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass
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
        )

    def style(self) -> str:
        """The class style, with the owning module recorded so parse puts the class back in it."""
        fill = f'fillColor={self.fill_color};strokeColor=#666666;' if self.fill_color else ''
        module = f'module={self.owning_module};' if self.owning_module else ''
        return f'{CLASS_STYLE}{fill}{module}'

    def _property_lines(self) -> List[str]:
        return [f"+ {p.name}{(': ' + p.type_hint if p.type_hint else '')}" for p in self.properties]

    def _operation_lines(self) -> List[str]:
        return [
            f"{('- ' if op.name.startswith('_') else '+ ')}"
            f"{op.name}({', '.join(parameter.save() for parameter in op.parameters)})"
            f"{(': ' + op.return_type if op.return_type else '')}"
            for op in self.operations
        ]

    def _member_lines(self) -> List[str]:
        return [self.name] + self._property_lines() + self._operation_lines()

    def _properties_html(self) -> str:
        return ''.join(f'{html.escape(line)}<br/>' for line in self._property_lines()) or '<br/>'

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

    def load_class(self, source: OoadClass) -> DrawIOClass:
        loaded = DrawIOClass(name=source.name, sequential_order=source.sequential_order)
        loaded.translate_from(source)
        return loaded

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
        if self.nested:
            return MODULE_CHILD_STYLE
        return MODULE_STYLE

    def parse_html(self, value: str) -> Tuple[Optional[str], str, List[str]]:
        text = html.unescape(value)
        m = re.search('<b[^>]*>([^<]+)</b>', text, re.IGNORECASE)
        name = m.group(1).strip() if m else None
        if not name:
            return (None, '', [])
        purpose = self._purpose_from_html(text)
        return (name, purpose, self._terms_from_html(text))

    def _seam_bullets(self) -> str:
        shown = self.shown_seam_terms()
        return '<br>'.join((f'\u2022 {html.escape(t)}' for t in shown))

    def _purpose_from_html(self, text: str) -> str:
        im = re.search('<i[^>]*>([^<]*)</i>', text, re.IGNORECASE)
        if im:
            return im.group(1).strip()
        return ''

    def _terms_from_html(self, text: str) -> List[str]:
        terms: List[str] = []
        for bullet in re.findall('[\u2022\\-]\\s*([^<]+)', text):
            term = bullet.strip()
            if term and (not term.startswith('{')):
                terms.append(term)
            elif term.startswith('{') and term.endswith('}'):
                continue
            elif term:
                terms.append(term)
        if terms:
            return terms
        for li in re.findall('<li[^>]*>(?:<[^>]+>)*([^<]+)', text, re.IGNORECASE):
            term = li.strip()
            if term and 'stack' not in term.lower():
                terms.append(term)
        return terms


