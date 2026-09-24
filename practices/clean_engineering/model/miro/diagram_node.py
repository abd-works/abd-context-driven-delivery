"""Miro placed cells: Mermaid labels and canvas-composer SVG bounds."""
from __future__ import annotations

import re
from html import escape
from typing import List

from practices.clean_engineering.model.base_class_model import OoadClass
from practices.clean_engineering.model.diagram.diagram_node import (
    DiagramClass,
    DiagramModule,
    ImportedClass,
)
from practices.clean_engineering.model.diagram.geometry import Geometry


class MiroClass(DiagramClass):
    """OoadClass as a Mermaid classDiagram block."""

    def mermaid_id(self) -> str:
        identifier = re.sub(r'\W+', '_', self.display_name()).strip('_')
        if identifier and identifier[0].isdigit():
            identifier = f'class_{identifier}'
        return identifier or 'UnnamedClass'

    def mermaid_lines(self) -> List[str]:
        class_id = self.mermaid_id()
        lines = [f'    %% local: {class_id}', f'    class {class_id} {{']
        for stereotype in self.tactical_stereotypes():
            lines.append(f'        <<{stereotype}>>')
        for prop in self.properties:
            lines.append(f"        +{prop.type_hint or 'object'} {prop.name}")
        for operation in self.operations:
            parameters = ', '.join(operation.parameters)
            lines.append(
                f'        +{operation.name}({parameters}) {operation.return_type or "void"}'
            )
        lines.append('    }')
        return lines


class MiroImportedClass(ImportedClass):
    """Dashed-by-convention imported class in a Mermaid classDiagram."""

    def mermaid_id(self) -> str:
        identifier = re.sub(r'\W+', '_', self.display_name()).strip('_')
        if identifier and identifier[0].isdigit():
            identifier = f'class_{identifier}'
        return identifier or 'UnnamedClass'

    def mermaid_lines(self) -> List[str]:
        class_id = self.mermaid_id()
        lines = [f'    %% imported: {class_id}', f'    class {class_id} {{']
        lines.append(f'        <<from {self.from_module}>>')
        for stereotype in self.tactical_stereotypes():
            lines.append(f'        <<{stereotype}>>')
        for prop in self.key_properties():
            lines.append(f"        +{prop.type_hint or 'object'} {prop.name}")
        lines.append('    }')
        return lines


class MiroModule(DiagramModule):
    """Module as a Mermaid flowchart node or subgraph."""

    def load_class(self, source: OoadClass) -> MiroClass:
        loaded = MiroClass(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    def mermaid_id(self) -> str:
        return re.sub(r'[^a-zA-Z0-9]', '_', self.name)

    def mermaid_label(self) -> str:
        parts = [self.name]
        if self.description.strip():
            parts.append(self.purpose_line())
        terms = self.public_terms()
        if terms:
            parts.append('---')
            parts.extend(f'\u2022 {term}' for term in terms)
        return '\\n'.join(parts)


class Page:
    """One canvas-composer SVG that places modules as foreignObject widgets."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._elements: List[str] = []

    def place(self, node: DiagramModule, mermaid: str) -> None:
        node.geometry = node.keep_or_place(node.geometry)
        geo = node.geometry
        element_id = f'CleanEngineering-{node.mermaid_id()}'
        title = escape(f'{node.name} - Class Diagram', quote=True)
        escaped_mermaid = escape(mermaid, quote=False)
        escaped_module = escape(node.name, quote=True)
        escaped_system = escape(self.name, quote=True)
        self._elements.append(
            f'  <foreignObject id="{element_id}" x="{int(geo.x)}" y="{int(geo.y)}" '
            f'width="{int(geo.width)}" height="{int(geo.height)}" data-type="diagram" '
            f'data-title="{title}" data-module="{escaped_module}" '
            f'data-system="{escaped_system}">{escaped_mermaid}</foreignObject>'
        )

    def svg(self) -> str:
        return (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            '<svg xmlns="http://www.w3.org/2000/svg">\n'
            + '\n'.join(self._elements)
            + '\n</svg>'
        )
