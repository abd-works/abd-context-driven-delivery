"""Draw.io placed cells: mxCell write plus Draw.io styles."""
from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple

from practices.clean_engineering.model.base_class_model import OoadClass
from practices.clean_engineering.model.diagram.diagram_node import (
    DiagramClass,
    DiagramModule,
    DiagramNode,
    ImportedClass as SharedImportedClass,
)
from practices.clean_engineering.model.diagram.geometry import (
    CELL_MIN_HEIGHT,
    CELL_WIDTH,
    Geometry,
    MODULE_CELL_MIN_HEIGHT,
    MODULE_CELL_WIDTH,
    MODULE_HEADER_HEIGHT,
    MODULE_LINE_HEIGHT,
    MODULE_MAX_SEAM_BULLETS,
    MODULE_PURPOSE_MAX_CHARS,
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


class Page:
    """One mxGraphModel root that writes DiagramNode cells as mxCell."""

    def __init__(self, name: str, root_el: ET.Element) -> None:
        self.name = name
        self._root_el = root_el

    def place(self, node: DiagramNode) -> ET.Element:
        node.geometry = node.keep_or_place(node.geometry)
        cell = ET.SubElement(self._root_el, 'mxCell')
        cell.set('id', node.cell_id)
        cell.set('value', node.html())
        cell.set('style', node.style())
        cell.set('vertex', '1')
        cell.set('parent', node.parent_id)
        geo = ET.SubElement(cell, 'mxGeometry')
        geo.set('x', str(int(node.geometry.x)))
        geo.set('y', str(int(node.geometry.y)))
        geo.set('width', str(int(node.geometry.width)))
        geo.set('height', str(int(node.geometry.height)))
        geo.set('as', 'geometry')
        return cell


class DrawIOClass(DiagramClass):
    """Draw.io UML class cell."""

    def html(self) -> str:
        name_html = html.escape(self.display_name())
        stereo = self._stereotype_html()
        return (
            f'<p style="margin:0px;margin-top:4px;text-align:center;">'
            f'{stereo}<b>{name_html}</b></p><hr size="1"/>'
            f'<p style="margin:0px;margin-left:4px;font-size:10px;">{self._properties_html()}</p>'
            f'<hr size="1"/>'
            f'<p style="margin:0px;margin-left:4px;font-size:10px;">{self._operations_html()}</p>'
        )

    def style(self) -> str:
        return CLASS_STYLE

    def _properties_html(self) -> str:
        bits = ''.join(
            (
                f"+ {html.escape(p.name)}"
                f"{(': ' + html.escape(p.type_hint) if p.type_hint else '')}<br/>"
                for p in self.properties
            )
        )
        return bits or '<br/>'

    def _operations_html(self) -> str:
        bits = ''.join(
            (
                f"{('- ' if op.name.startswith('_') else '+ ')}"
                f"{html.escape(op.name)}({', '.join(op.parameters)})"
                f"{(': ' + html.escape(op.return_type) if op.return_type else '')}<br/>"
                for op in self.operations
            )
        )
        return bits or '<br/>'

    def _stereotype_html(self) -> str:
        stereotypes = self.tactical_stereotypes()
        if not stereotypes:
            return ''
        label = ' '.join(stereotypes)
        return f'<i style="font-size:9px;color:#888;">{html.escape(label)}</i><br/>'


class ImportedClass(SharedImportedClass, DrawIOClass):
    """Dashed Draw.io card for a class owned by another aggregate."""

    def html(self) -> str:
        name_html = html.escape(self.display_name())
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


class DrawIOModule(DiagramModule):
    """Draw.io rounded modules-view cell."""

    def load_class(self, source: OoadClass) -> DrawIOClass:
        loaded = DrawIOClass(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
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
