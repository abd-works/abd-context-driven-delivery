"""
DrawIOStoryNodeSerializer - Creates, loads, and writes DrawIO story nodes to XML.
"""
import re
import xml.etree.ElementTree as ET
from typing import Optional, List
from .drawio_element import DrawIOElement
from .drawio_story_node import DrawIOStoryNode, DrawIOEpic, DrawIOSubEpic, DrawIOStory
from .story_io_position import Position, Boundary

_HTML_TAG_RE = re.compile(r'<[^>]+>')
_HTML_ENTITY_MAP = {'&amp;': '&', '&lt;': '<', '&gt;': '>',
                     '&quot;': '"', '&nbsp;': ' ', '&#39;': "'"}


def _strip_html(text: str) -> str:
    """Remove HTML tags and decode common entities from DrawIO cell values."""
    if '<' not in text:
        return text
    cleaned = _HTML_TAG_RE.sub('', text)
    for entity, char in _HTML_ENTITY_MAP.items():
        cleaned = cleaned.replace(entity, char)
    return cleaned.strip()


class DrawIOStoryNodeSerializer:

    @staticmethod
    def create_epic(name: str, sequential_order: float = 0.0) -> DrawIOEpic:
        return DrawIOEpic(name=name, sequential_order=sequential_order, domain_concepts=[])

    @staticmethod
    def create_sub_epic(name: str, sequential_order: float = 0.0) -> DrawIOSubEpic:
        return DrawIOSubEpic(name=name, sequential_order=sequential_order, domain_concepts=[])

    @staticmethod
    def create_story(name: str, sequential_order: float = 0.0,
                     story_type: str = None) -> DrawIOStory:
        return DrawIOStory(name=name, sequential_order=sequential_order,
                           story_type=story_type or 'user')

    @staticmethod
    def create_actor(name: str) -> DrawIOElement:
        element = DrawIOElement(cell_id=f'actor-{name.lower().replace(" ", "-")}', value=name)
        element.apply_style_for_type('actor')
        return element

    @staticmethod
    def to_mx_cell(node) -> ET.Element:
        cell = ET.Element('mxCell')
        if isinstance(node, DrawIOStoryNode):
            cell.set('id', node.cell_id)
            cell.set('value', node.name)
            cell.set('style', node.element.to_style_string())
            boundary = node.boundary
        else:
            cell.set('id', node.cell_id)
            cell.set('value', node.value)
            cell.set('style', node.to_style_string())
            boundary = node.boundary
        cell.set('vertex', '1')
        cell.set('parent', '1')
        geometry = ET.SubElement(cell, 'mxGeometry')
        geometry.set('x', str(node.position.x))
        geometry.set('y', str(node.position.y))
        geometry.set('width', str(boundary.width))
        geometry.set('height', str(boundary.height))
        geometry.set('as', 'geometry')
        return cell

    @staticmethod
    def from_mx_cell(cell: ET.Element):
        cell_id = cell.get('id', '')
        value = _strip_html(cell.get('value', ''))
        style = cell.get('style', '')
        parent_id = cell.get('parent', '')
        geometry = cell.find('mxGeometry')
        if geometry is None:
            return None, None
        x = float(geometry.get('x', '0'))
        y = float(geometry.get('y', '0'))
        width = float(geometry.get('width', '0'))
        height = float(geometry.get('height', '0'))
        style_dict = DrawIOElement.from_style_string(style)
        fill_color = style_dict.get('fillColor', '')
        node = DrawIOStoryNodeSerializer._classify_node(
            value, fill_color, cell_id=cell_id, style_dict=style_dict,
            width=width, height=height)
        if node:
            node._element._cell_id = cell_id
            node.set_position(x, y)
            node.set_size(width, height)
            return node, parent_id
        # Unrecognized fill → raw DrawIOElement (increment lanes, actors, AC boxes, etc.)
        raw = DrawIOElement(cell_id=cell_id, value=value)
        raw.set_style_from_string(style)
        raw.set_position(x, y)
        raw.set_size(width, height)
        return raw, parent_id

    @staticmethod
    def _classify_node(value: str, fill_color: str, *,
                        cell_id: str = '', style_dict: dict = None,
                        width: float = 0, height: float = 0) -> Optional[DrawIOStoryNode]:
        if fill_color == '#e1d5e7':
            return DrawIOStoryNodeSerializer.create_epic(value, 0)
        elif fill_color == '#d5e8d4':
            return DrawIOStoryNodeSerializer.create_sub_epic(value, 0)
        elif fill_color in ('#fff2cc', '#1a237e', '#000000'):
            # AC boxes share #fff2cc with stories but are distinguishable:
            # - cell_id contains '/ac-'  (tool-generated AC)
            # - align=left style without aspect=fixed  (wider text boxes)
            # - NOT square (width != height, typically 250x60)
            if fill_color == '#fff2cc':
                if '/ac-' in cell_id:
                    return None  # AC box, not a story
                sd = style_dict or {}
                if (sd.get('align') == 'left'
                        and 'aspect' not in sd
                        and width > 0 and height > 0
                        and abs(width - height) > 10):
                    return None  # User-created or loaded AC box
            story_type = 'user'
            if fill_color == '#1a237e':
                story_type = 'system'
            elif fill_color == '#000000':
                story_type = 'technical'
            return DrawIOStoryNodeSerializer.create_story(value, 0, story_type)
        return None

    @staticmethod
    def to_drawio_xml(nodes: list) -> str:
        mxfile = ET.Element('mxfile')
        mxfile.set('host', 'app.diagrams.net')
        diagram = ET.SubElement(mxfile, 'diagram')
        diagram.set('name', 'Story Map')
        diagram.set('id', 'story-map')
        model = ET.SubElement(diagram, 'mxGraphModel')
        root = ET.SubElement(model, 'root')
        ET.SubElement(root, 'mxCell').set('id', '0')
        parent_cell = ET.SubElement(root, 'mxCell')
        parent_cell.set('id', '1')
        parent_cell.set('parent', '0')
        for node in nodes:
            root.append(DrawIOStoryNodeSerializer.to_mx_cell(node))
        return ET.tostring(mxfile, encoding='unicode', xml_declaration=True)

    @staticmethod
    def parse_nodes_from_xml(xml_content: str):
        tree = ET.fromstring(xml_content)
        nodes = []
        parent_map = {}
        for cell in tree.iter('mxCell'):
            if cell.get('vertex') == '1':
                result = DrawIOStoryNodeSerializer.from_mx_cell(cell)
                if result is None:
                    continue
                node, parent_id = result
                if node:
                    nodes.append(node)
                    parent_map[node.cell_id] = parent_id
        return nodes, parent_map
