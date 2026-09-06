"""Factories and (de)serialization for Miro story nodes.

Mirrors ``DrawIOStoryNodeSerializer``: creators for Epic / SubEpic / Story
plus translation between ``MiroStoryNode`` and the Miro v2 items payload
returned by ``MiroElement.to_miro_payload``. The reverse path (reading a
board's items into ``MiroStoryNode`` instances) classifies items by the
``story_sync_role`` metadata key the renderer writes.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from . import _bootstrap  # noqa: F401

from .miro_element import MiroElement
from .miro_story_node import MiroEpic, MiroStory, MiroStoryNode, MiroSubEpic


__all__ = ['MiroStoryNodeSerializer']


class MiroStoryNodeSerializer:
    """Stateless helpers; mirrors ``DrawIOStoryNodeSerializer`` shape."""

    # ------------------------------------------------------------------
    # Factories
    # ------------------------------------------------------------------

    @staticmethod
    def create_epic(name: str, sequential_order: float = 0.0) -> MiroEpic:
        return MiroEpic(name=name, sequential_order=sequential_order, domain_concepts=[])

    @staticmethod
    def create_sub_epic(name: str, sequential_order: float = 0.0) -> MiroSubEpic:
        return MiroSubEpic(name=name, sequential_order=sequential_order, domain_concepts=[])

    @staticmethod
    def create_story(name: str, sequential_order: float = 0.0,
                     story_type: Optional[str] = None) -> MiroStory:
        return MiroStory(name=name, sequential_order=sequential_order,
                         story_type=story_type or 'user')

    @staticmethod
    def create_ac(text: str, sequential_order: float = 0.0) -> 'MiroAC':
        from .miro_story_node import MiroAC
        return MiroAC(name=text, sequential_order=sequential_order)

    # ------------------------------------------------------------------
    # Serialise
    # ------------------------------------------------------------------

    @staticmethod
    def to_item_spec(node: MiroStoryNode) -> Dict[str, Any]:
        """Convert a ``MiroStoryNode`` into a transport ``create_item`` spec.

        Output shape: ``{'item_type': 'shape'|'sticky_note', 'payload': {...},
        'cell_id': '...'}``. The transport persists ``cell_id`` in metadata so
        re-renders can match items back to nodes.
        """
        elem = node.element
        body = elem.to_miro_payload()
        item_type = body.pop('item_type')
        payload = body['payload']
        # Tag the role so ``from_miro_item`` can classify on read.
        meta = dict(payload.get('metadata') or {})
        meta['story_sync_role'] = elem.element_type
        meta['story_sync_cell_id'] = elem.cell_id
        payload['metadata'] = meta
        return {'item_type': item_type, 'payload': payload, 'cell_id': elem.cell_id}

    @staticmethod
    def to_item_specs(nodes: List[Any]) -> List[Dict[str, Any]]:
        """Serialise an ordered iterable of nodes/elements for the transport."""
        specs: List[Dict[str, Any]] = []
        for node in nodes:
            if isinstance(node, MiroStoryNode):
                specs.append(MiroStoryNodeSerializer.to_item_spec(node))
            elif isinstance(node, MiroElement):
                specs.append(_element_to_item_spec(node))
            else:
                continue
        return specs

    # ------------------------------------------------------------------
    # Deserialise (board read direction)
    # ------------------------------------------------------------------

    @staticmethod
    def from_miro_item(item: Dict[str, Any]) -> Tuple[Optional[MiroStoryNode], MiroElement]:
        """Classify a Miro item dict into ``(MiroStoryNode | None, MiroElement)``.

        ``None`` for the node when the item is not a story-map structural
        node (e.g. a free-floating sticky a user added). The ``MiroElement``
        is always returned so callers can keep a flat list of every item on
        the board.
        """
        elem = MiroElement.from_miro_item(item)
        role = (item.get('metadata') or {}).get('story_sync_role', '')
        node: Optional[MiroStoryNode] = None
        if role == 'epic':
            node = MiroStoryNodeSerializer.create_epic(elem.value)
            node._element = elem
        elif role == 'sub_epic':
            node = MiroStoryNodeSerializer.create_sub_epic(elem.value)
            node._element = elem
        elif role in {'story_user', 'story_system', 'story_technical'}:
            type_map = {
                'story_user': 'user',
                'story_system': 'system',
                'story_technical': 'technical',
            }
            node = MiroStoryNodeSerializer.create_story(
                elem.value, story_type=type_map[role])
            node._element = elem
        return node, elem


def _element_to_item_spec(elem: MiroElement) -> Dict[str, Any]:
    body = elem.to_miro_payload()
    item_type = body.pop('item_type')
    payload = body['payload']
    meta = dict(payload.get('metadata') or {})
    meta['story_sync_role'] = elem.element_type
    meta['story_sync_cell_id'] = elem.cell_id
    payload['metadata'] = meta
    return {'item_type': item_type, 'payload': payload, 'cell_id': elem.cell_id}
