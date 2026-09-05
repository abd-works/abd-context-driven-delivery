from abc import ABC, abstractmethod
from typing import List, Iterator, Optional, Dict, Any, Union, TYPE_CHECKING

_LEVEL_DOMAIN = frozenset(['domain_concepts', 'acceptance', 'scenarios', 'examples', 'tests', 'code'])
_LEVEL_ACCEPTANCE = frozenset(['acceptance', 'scenarios', 'examples', 'tests', 'code'])
_LEVEL_SCENARIOS = frozenset(['scenarios', 'examples', 'tests', 'code'])
_LEVEL_EXAMPLES = frozenset(['examples', 'tests', 'code'])
_LEVEL_TESTS = frozenset(['tests', 'code'])

# When story-graph.json is absent, shape/build still need a StoryMap (empty graph until first save).
EMPTY_STORY_GRAPH_DICT: Dict[str, Any] = {'epics': [], 'increments': []}


def _level_includes(level_set, include_level: Optional[str]) -> bool:
    return include_level is None or include_level in level_set


def _domain_concepts_to_dict_list(domain_concepts: Optional[List[Any]]) -> List[Dict[str, Any]]:
    """Safely serialize domain_concepts to list of dicts. Handles both DomainConcept objects and raw dicts."""
    if not domain_concepts:
        return []
    result = []
    for dc in domain_concepts:
        if hasattr(dc, 'to_dict') and callable(getattr(dc, 'to_dict')):
            result.append(dc.to_dict())
        elif isinstance(dc, dict):
            result.append(dc)
        # Skip non-serializable items to avoid losing other domain_concepts
    return result


from dataclasses import dataclass, field
from pathlib import Path
import json
import logging
from datetime import datetime
from story_graph_ops.domain import DomainConcept, StoryUser

def _log(message: str):
    """Write log message to file."""
    log_file = Path(__file__).parent.parent.parent / 'logs' / 'test_class_mover.log'
    log_file.parent.mkdir(exist_ok=True)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()} {message}\n")

@dataclass
class ActionResult:
    success: bool
    action_name: str
    data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

@dataclass
class Move:
    """Represents a node move between parents."""
    from_parent: str
    to_parent: str

@dataclass
class Rename:
    """Represents a node rename."""
    original_name: str
    new_name: str

@dataclass
class StoryNode(ABC):
    name: str
    sequential_order: Optional[float] = None
    behavior: Optional[str] = None
    _bot: Optional[Any] = field(default=None, repr=False)
    
    # State properties set during comparison
    is_new: bool = field(default=False, repr=False)
    is_removed: bool = field(default=False, repr=False)
    has_moved: Optional[Move] = field(default=None, repr=False)
    is_renamed: Optional[Rename] = field(default=None, repr=False)

    def __post_init__(self):
        self._children: List['StoryNode'] = []

    @property
    @abstractmethod
    def children(self) -> List['StoryNode']:
        pass

    def __iter__(self) -> Iterator['StoryNode']:
        return iter(self.children)
    
    def __getitem__(self, child_name: str) -> 'StoryNode':
        """Access child by name"""
        for child in self.children:
            if child.name == child_name:
                return child
        raise KeyError(f"Child '{child_name}' not found in {type(self).__name__} '{self.name}'")

    def __repr__(self) -> str:
        order = f', order={self.sequential_order}' if self.sequential_order is not None else ''
        return f"{self.__class__.__name__}(name='{self.name}'{order})"
    
    @property
    def node_type(self) -> str:
        return self.__class__.__name__.lower()

    def save(self) -> None:
        """Save this node's changes to the story graph and persist to disk."""
        if not self._bot:
            return
        
        story_map = self._bot.story_map
        
        if isinstance(self, Story):
            self.file_link = story_map._calculate_story_file_link(self)
        
        story_map.save()
    
    def save_all(self) -> None:
        """Save this node and all children's changes to the story graph and persist to disk."""
        # Same as save() since updating the parent updates all children
        self.save()

    def _scope_command_for_node(self) -> str:
        """Get scope command string for this node type."""
        if isinstance(self, Scenario):
            return f"story {self.name}"
        elif isinstance(self, Story):
            return f"story {self.name}"
        elif isinstance(self, StoryGroup):
            return f"story {self.name}"
        elif isinstance(self, SubEpic):
            return f"subepic {self.name}"
        elif isinstance(self, Epic):
            return f"epic {self.name}"
        return f"story {self.name}"

    def submit_instructions(self, behavior: str, action: str):
        """Submit instructions with scope set to this node, then restore original scope.
        Uses same combine_next/combine_with_next logic as CLI behavior.action path.
        
        Args:
            behavior: The behavior name to execute
            action: The action name to execute
        
        Returns:
            Instructions object in test mode; result dict otherwise
        """
        scope_file = self._bot.workspace_directory / 'scope.json'
        with open(scope_file, 'r') as f:
            scope_before = json.load(f)
        self._bot.scope(self._scope_command_for_node())
        try:
            in_test = bool('pytest' in __import__('sys').modules or __import__('os').environ.get('PYTEST_CURRENT_TEST'))
            result = self._bot.submit_action(behavior, action, return_instructions=in_test)
            if in_test and isinstance(result, dict) and 'instructions' in result:
                instructions = result['instructions']
                if instructions and hasattr(instructions, '_scope') and instructions._scope:
                    instructions._scope = instructions._scope.copy()
                return instructions
            return result
        finally:
            # Always restore scope to original state
            with open(scope_file, 'w') as f:
                json.dump(scope_before, f)
            # Reload in-memory scope from file to match
            self._bot._scope.load()

    def get_required_behavior_instructions(self, action: str = 'build'):
        behavior_needed = self.behavior_needed
        return self.submit_instructions(behavior=behavior_needed, action=action)
    
    def submit_required_behavior_instructions(self, action: str):
        """Submit the required behavior instructions. Behavior from node; action passed in (e.g. build)."""
        behavior_needed = self.behavior_needed
        return self.submit_instructions(behavior=behavior_needed, action=action)

    def submit_current_instructions(self):
        """Submit instructions using bot's current behavior and action with scope set to this node."""
        current_behavior = self._bot.behaviors.current.name
        current_action = self._bot.behaviors.current.actions.current.action_name
        
        return self.submit_instructions(behavior=current_behavior, action=current_action)

    @staticmethod
    def _parse_steps_from_data(steps_value: Any) -> List[str]:
        if isinstance(steps_value, str):
            return [s.strip() for s in steps_value.split('\n') if s.strip()]
        elif isinstance(steps_value, list):
            result = []
            for item in steps_value:
                if isinstance(item, str):
                    result.append(item.strip() if item.strip() else item)
                elif isinstance(item, dict) and 'text' in item:
                    result.append(str(item['text']).strip())
                else:
                    result.append(str(item))
            return result
        else:
            return []

    @staticmethod
    def _add_steps_to_node(node: 'StoryNode', step_strings: List[str]) -> None:
        for step_idx, step_text in enumerate(step_strings):
            step = Step(name=step_text, text=step_text, sequential_order=float(step_idx + 1), _parent=node)
            node._children.append(step)

    @staticmethod
    def _generate_default_test_method_name(name: str) -> str:
        if not name:
            return ''
        words = name.split()
        method_name = '_'.join((word.lower() for word in words))
        return f'test_{method_name}'

    def _filter_children_by_type(self, target_type: type) -> List['StoryNode']:
        return [child for child in self._children if isinstance(child, target_type)]

    def rename(self, name: str = None) -> dict:
        """Rename the node. Parameter 'name' for CLI compatibility."""
        if name is None or not name:
            raise ValueError('Node name cannot be empty')
        if name != name.strip():
            raise ValueError('Node name cannot be whitespace-only')
        
        invalid_chars = ['<', '>', '\\', '|', '*', '?', '"']
        found_invalid = [ch for ch in invalid_chars if ch in name]
        if found_invalid:
            chars_str = ', '.join(found_invalid)
            raise ValueError(f'Name contains invalid characters: {chars_str}')
        
        if hasattr(self, '_parent') and self._parent:
            for sibling in self._parent.children:
                if sibling is not self and sibling.name == name:
                    raise ValueError(f"Name '{name}' already exists among siblings")
        
        node_type = type(self).__name__
        old_name = self.name
        self.name = name
        
        # Save changes to disk
        self.save()
        
        return {'node_type': node_type, 'old_name': old_name, 'new_name': name, 'operation': 'rename'}

    def copy_name(self) -> dict:
        """Return node name for clipboard. Used by panel context menu (event -> CLI -> bot)."""
        return {'status': 'success', 'result': self.name}

    def render_diagram(self) -> dict:
        """Render diagram for this node's scope. CLI: story_graph.<path>.render_diagram
        Delegates to shape.render.renderDiagram(scope=self.name) when bot has shape behavior."""
        if self._bot:
            shape = self._bot.behaviors.find_by_name('shape')
            if shape:
                render = shape.actions.find_by_name('render')
                if render and hasattr(render, 'renderDiagram'):
                    return render.renderDiagram(scope=self.name)
        return {'status': 'success', 'message': 'Diagram rendered for scope'}

    def copy_json(self, include_level: Optional[str] = None) -> dict:
        """Return this node as story-graph JSON for clipboard. Uses scope.include_level when available (same as submit)."""
        if not self._bot or not hasattr(self._bot, 'story_map'):
            raise ValueError('Cannot serialize node without bot context')
        if include_level is None and hasattr(self._bot, '_scope') and self._bot._scope:
            include_level = getattr(self._bot._scope, 'include_level', 'examples') or 'examples'
        if include_level is None:
            include_level = 'examples'
        story_map = self._bot.story_map
        generate_trace = include_level in ('tests', 'code')
        node_dict = story_map.node_to_dict(self, include_level=include_level, generate_trace=generate_trace)
        return {'status': 'success', 'result': node_dict}

    def delete(self, cascade: bool = True) -> dict:
        """Delete this node. Always cascades to delete all children."""
        import time
        start_time = time.time()
        
        if not hasattr(self, '_parent') or not self._parent:
            raise ValueError('Cannot delete node without parent')
        
        node_type = type(self).__name__
        node_name = self.name
        parent = self._parent
        children_count = len(self._children)
        
        # Handle Story deletion from StoryGroup
        if isinstance(parent, StoryGroup):
            if isinstance(self, Story) and self._bot:
                self._bot.story_map.remove_story_from_all_increments(node_name)
            parent._children.remove(self)
            parent._resequence_children()
            # If the story group is now empty, remove it from the sub-epic
            if len(parent._children) == 0:
                sub_epic = parent._parent
                if sub_epic is not None and hasattr(sub_epic, '_children'):
                    sub_epic._children.remove(parent)
                    sub_epic.save()
            else:
                parent.save()
            elapsed = time.time() - start_time
            print(f"[DELETE TIMING] Deleted {node_type} '{node_name}' in {elapsed:.3f}s")
            return {'node_type': node_type, 'node_name': node_name, 'operation': 'delete', 'children_deleted': children_count}
        
        # Always cascade delete
        if isinstance(self, Story) and self._bot:
            self._bot.story_map.remove_story_from_all_increments(node_name)
        self._children.clear()
        
        parent._children.remove(self)
        self._resequence_siblings()
        
        # Save changes from PARENT
        parent.save()
        
        elapsed = time.time() - start_time
        print(f"[DELETE TIMING] Deleted {node_type} '{node_name}' in {elapsed:.3f}s")
        
        return {'node_type': node_type, 'node_name': node_name, 'operation': 'delete', 'children_deleted': children_count}

    def move_to(self, target: Union[str, 'StoryNode'] = None, position: Optional[int] = None, at_position: Optional[int] = None) -> dict:
        """Move node to a different parent or reorder within same parent. Parameters 'target' and 'at_position' for CLI compatibility."""
        # Handle CLI parameter alias
        if at_position is not None and position is None:
            position = at_position
        
        # If no target specified, move within same parent (just reorder)
        if target is None:
            if not hasattr(self, '_parent') or not self._parent:
                raise ValueError('Cannot move node without parent')
            target = self._parent
        elif isinstance(target, str):
            # Resolve string target to actual node
            target = self._resolve_target_from_string(target)
        
        node_type = type(self).__name__
        node_name = self.name
        source_parent_name = self._parent.name if hasattr(self, '_parent') and self._parent else None
        target_parent_name = target.name
        
        # Check for circular reference first (before checking parent)
        if self._is_circular_reference(target):
            raise ValueError('Cannot move node to its own descendant - circular reference')
        
        if not hasattr(self, '_parent') or not self._parent:
            raise ValueError('Cannot move node without parent')
        
        # Check if moving Story within same SubEpic (Story._parent is StoryGroup, need to check grandparent)
        actual_parent = self._parent
        if isinstance(actual_parent, StoryGroup) and hasattr(actual_parent, '_parent'):
            actual_grandparent = actual_parent._parent
            if actual_grandparent == target:
                # Moving within same SubEpic
                if position is not None:
                    current_position = actual_parent._children.index(self)
                    if current_position != position:
                        actual_parent._children.remove(self)
                        adjusted_position = min(position, len(actual_parent._children))
                        actual_parent._children.insert(adjusted_position, self)
                        actual_parent._resequence_children()
                        
                        # Save changes to disk
                        self.save()
                else:
                    raise ValueError(f"Node '{self.name}' already exists under parent '{target.name}'")
                return {'node_type': node_type, 'node_name': node_name, 'source_parent': source_parent_name, 'target_parent': target_parent_name, 'position': position, 'operation': 'move'}
        
        if self._parent == target:
            if position is not None:
                current_position = self._parent.children.index(self)
                if current_position != position:
                    self._parent._children.remove(self)
                    adjusted_position = min(position, len(self._parent.children))
                    self._parent._children.insert(adjusted_position, self)
                    self._resequence_siblings()
                    
                    # Save changes to disk
                    self.save()
            else:
                raise ValueError(f"Node '{self.name}' already exists under parent '{target.name}'")
            return {'node_type': node_type, 'node_name': node_name, 'source_parent': source_parent_name, 'target_parent': target_parent_name, 'position': position, 'operation': 'move'}
        
        for existing_child in target.children:
            if existing_child.name == self.name:
                raise ValueError(f"Node '{self.name}' already exists under parent '{target.name}'")
        
        self._validate_hierarchy_rules(target)
        
        # CRITICAL: Stories MUST be inside StoryGroups, not directly in SubEpic/Epic
        actual_target = target
        if isinstance(self, Story) and isinstance(target, (SubEpic, Epic)):
            # Find or create a StoryGroup in the target
            story_groups = [child for child in target._children if isinstance(child, StoryGroup)]
            if story_groups:
                # Use the first StoryGroup
                actual_target = story_groups[0]
            else:
                # Create a new StoryGroup
                story_group = StoryGroup(
                    name='',
                    sequential_order=0.0,
                    group_type='and',
                    connector=None,
                    _parent=target,
                    _bot=self._bot
                )
                target._children.append(story_group)
                actual_target = story_group
        
        # Check if we need to move test class (Story moving between SubEpics)
        source_subepic = None
        target_subepic = None
        if isinstance(self, Story):
            _log(f"[move_to] Story '{self.name}' is being moved")
            
            # Find source SubEpic
            current = self._parent
            while current and not isinstance(current, SubEpic):
                if hasattr(current, '_parent'):
                    current = current._parent
                else:
                    break
            source_subepic = current if isinstance(current, SubEpic) else None
            
            if source_subepic:
                _log(f"[move_to] Source SubEpic: '{source_subepic.name}'")
            else:
                _log(f"[move_to] Source SubEpic: None")
            
            # Find target SubEpic
            current = actual_target
            while current and not isinstance(current, SubEpic):
                if hasattr(current, '_parent'):
                    current = current._parent
                else:
                    break
            target_subepic = current if isinstance(current, SubEpic) else None
            
            if target_subepic:
                _log(f"[move_to] Target SubEpic: '{target_subepic.name}'")
            else:
                _log(f"[move_to] Target SubEpic: None")
        
        # Perform the move
        _log(f"[move_to] BEFORE MOVE - actual_target type: {type(actual_target).__name__}, name: {actual_target.name}, children count: {len(actual_target._children)}")
        old_parent = self._parent
        self._parent._children.remove(self)
        self._parent._resequence_siblings()
        # If we moved the last story out of a StoryGroup, remove the empty group from the sub-epic
        if isinstance(old_parent, StoryGroup) and len(old_parent._children) == 0:
            sub_epic = old_parent._parent
            if sub_epic is not None and hasattr(sub_epic, '_children'):
                sub_epic._children.remove(old_parent)
        self._parent = actual_target
        if position is not None:
            adjusted_position = min(position, len(actual_target.children))
            _log(f"[move_to] INSERTING at position {adjusted_position}")
            actual_target._children.insert(adjusted_position, self)
        else:
            _log(f"[move_to] APPENDING to children (no position specified)")
            actual_target._children.append(self)
        _log(f"[move_to] AFTER MOVE - actual_target children count: {len(actual_target._children)}")
        actual_target._resequence_children()
        
        # Move test class if needed
        if isinstance(self, Story) and source_subepic and target_subepic and source_subepic != target_subepic:
            _log(f"[move_to] Story moving between different SubEpics")
            _log(f"[move_to] Story test_class: {self.test_class}")
            
            if self.test_class and hasattr(source_subepic, 'test_file') and hasattr(target_subepic, 'test_file'):
                _log(f"[move_to] Source test_file: {source_subepic.test_file}")
                _log(f"[move_to] Target test_file: {target_subepic.test_file}")
                
                if source_subepic.test_file and target_subepic.test_file:
                    from story_graph_ops.test_class_mover import TestClassMover
                    
                    # Get absolute paths
                    if self._bot and hasattr(self._bot, 'bot_paths'):
                        workspace_dir = Path(self._bot.bot_paths.workspace_directory)
                        source_file = workspace_dir / 'test' / source_subepic.test_file
                        target_file = workspace_dir / 'test' / target_subepic.test_file
                        
                        _log(f"[move_to] Workspace dir: {workspace_dir}")
                        _log(f"[move_to] Source file: {source_file}")
                        _log(f"[move_to] Target file: {target_file}")
                        _log(f"[move_to] Source exists: {source_file.exists()}")
                        _log(f"[move_to] Target exists: {target_file.exists()}")
                        
                        # Move the test class
                        if source_file.exists() and target_file.exists():
                            _log(f"[move_to] Initiating test class move")
                            result = TestClassMover.move_class(source_file, target_file, self.test_class)
                            _log(f"[move_to] Test class move result: {result}")
                        else:
                            _log(f"[move_to] Skipping test class move - file(s) do not exist")
                    else:
                        _log(f"[move_to] Skipping test class move - bot or bot_paths not available")
                else:
                    _log(f"[move_to] Skipping test class move - test_file not set on source or target")
            else:
                _log(f"[move_to] No test class to move")
        else:
            if isinstance(self, Story):
                if not source_subepic or not target_subepic:
                    _log(f"[move_to] Not a SubEpic-to-SubEpic move")
                elif source_subepic == target_subepic:
                    _log(f"[move_to] Moving within same SubEpic")
        
        # Save changes to disk
        self.save()
        
        return {'node_type': node_type, 'node_name': node_name, 'source_parent': source_parent_name, 'target_parent': target_parent_name, 'position': position, 'operation': 'move'}

    def _is_circular_reference(self, potential_parent: 'StoryNode') -> bool:
        current = potential_parent
        while hasattr(current, '_parent') and current._parent:
            if current._parent == self:
                return True
            current = current._parent
        return False
    
    def _resolve_target_from_string(self, target_name: str) -> 'StoryNode':
        """Resolve a target node name to an actual node by searching from root.
        Supports both simple names and dotted paths like \"Epic1\".\"Child1\"
        """
        import re
        
        _log(f"[_resolve_target_from_string] RECEIVED target_name: '{target_name}' (type: {type(target_name)})")
        
        # Handle already-quoted paths from parameter parsing (e.g., "Epic1"."Child1")
        path_str = target_name
        if path_str.startswith('"') and '"."' in path_str:
            # Already in quoted format, use as-is
            _log(f"[_resolve_target_from_string] Detected quoted path format: '{path_str}'")
        # Check if this is a dotted path (e.g., Epic1.Child1 or story_graph."Epic1"."Child1")
        elif path_str.startswith('story_graph.'):
            path_str = path_str[len('story_graph.'):]
            _log(f"[_resolve_target_from_string] After stripping story_graph: '{path_str}'")
        
        # Parse quoted path segments (e.g., "Epic1"."Child1" -> ["Epic1", "Child1"])
        path_segments = re.findall(r'"([^"]+)"', path_str)
        _log(f"[_resolve_target_from_string] Extracted path_segments: {path_segments}")
        
        # Navigate to root (story_map)
        current = self
        while hasattr(current, '_parent') and current._parent:
            current = current._parent
            if not hasattr(current, '_parent'):  # Reached Epic level
                # Go one more level up to StoryMap if Epic has _bot
                if hasattr(current, '_bot') and current._bot and hasattr(current._bot, 'story_graph'):
                    story_map = current._bot.story_map
                    
                    # If we have path segments, navigate the path
                    if path_segments:
                        node = None
                        # Start from the first epic that matches
                        for epic in story_map.epics:
                            if epic.name == path_segments[0]:
                                node = epic
                                break
                        
                        if not node:
                            raise ValueError(f"Epic '{path_segments[0]}' not found in path: {target_name}")
                        
                        # Navigate through remaining segments
                        for segment in path_segments[1:]:
                            found = False
                            for child in node.children:
                                if child.name == segment:
                                    node = child
                                    found = True
                                    break
                            if not found:
                                raise ValueError(f"Node '{segment}' not found in path: {target_name}")
                        
                        return node
                    else:
                        # Simple name search (legacy behavior)
                        for epic in story_map.epics:
                            if epic.name == target_name:
                                return epic
                            # Search in epic's children recursively
                            found = self._search_node_recursive(epic, target_name)
                            if found:
                                return found
                break
        
        raise ValueError(f"Target '{target_name}' not found")
    
    def _search_node_recursive(self, node: 'StoryNode', name: str) -> Optional['StoryNode']:
        """Recursively search for a node by name"""
        for child in node.children:
            if child.name == name:
                return child
            found = self._search_node_recursive(child, name)
            if found:
                return found
        return None
    
    def move_to_position(self, position: int) -> dict:
        """Alias for move_to with only position (moves within same parent)"""
        return self.move_to(position=position)
    
    def move_after(self, sibling: Union[str, 'StoryNode']) -> dict:
        """Move this node to be positioned after the specified sibling.
        
        Args:
            sibling: Either the name of a sibling node or a StoryNode instance
            
        Returns:
            Dict with operation details including new position
        """
        # Handle Epic nodes (no _parent, managed by StoryMap)
        if isinstance(self, Epic):
            if not self._bot or not hasattr(self._bot, 'story_map'):
                raise ValueError('Cannot move epic without bot context')
            
            story_map = self._bot.story_map
            
            # Resolve sibling if it's a string
            if isinstance(sibling, str):
                target_sibling = None
                for epic in story_map._epics_list:
                    if epic.name == sibling:
                        target_sibling = epic
                        break
                if not target_sibling:
                    raise ValueError(f"Epic '{sibling}' not found in story map")
                sibling = target_sibling
            
            # Find current and target positions
            current_position = story_map._epics_list.index(self)
            sibling_position = story_map._epics_list.index(sibling)
            
            # Remove from current position
            story_map._epics_list.remove(self)
            
            # Insert after sibling (adjust position if we removed before the sibling)
            new_position = sibling_position if current_position > sibling_position else sibling_position
            story_map._epics_list.insert(new_position, self)
            
            # Update sequential order
            for idx, e in enumerate(story_map._epics_list):
                e.sequential_order = idx
            
            # Rebuild epics collection and save
            story_map._epics = EpicsCollection(story_map._epics_list)
            story_map.save()
            
            return {
                'node_type': 'Epic',
                'node_name': self.name,
                'operation': 'move_after',
                'sibling': sibling.name,
                'new_position': new_position
            }
        
        # Handle other node types (SubEpic, Story, etc.)
        if not hasattr(self, '_parent') or not self._parent:
            raise ValueError('Cannot move node without parent')
        
        # Resolve sibling if it's a string
        if isinstance(sibling, str):
            target_sibling = None
            for child in self._parent.children:
                if child.name == sibling:
                    target_sibling = child
                    break
            if not target_sibling:
                raise ValueError(f"Sibling '{sibling}' not found under parent '{self._parent.name}'")
            sibling = target_sibling
        
        # Verify sibling has same parent
        if not hasattr(sibling, '_parent') or sibling._parent != self._parent:
            raise ValueError(f"Node '{sibling.name}' is not a sibling of '{self.name}'")
        
        # Find position after the sibling
        sibling_position = self._parent.children.index(sibling)
        new_position = sibling_position + 1
        
        # Use move_to with the calculated position
        return self.move_to(position=new_position)

    def _validate_hierarchy_rules(self, target_parent: 'StoryNode') -> None:
        if isinstance(self, SubEpic) and isinstance(target_parent, SubEpic):
            for child in target_parent.children:
                if isinstance(child, (Story, StoryGroup)):
                    raise ValueError('Cannot move SubEpic to SubEpic with Stories')
        if isinstance(self, Story) and isinstance(target_parent, SubEpic):
            for child in target_parent.children:
                if isinstance(child, SubEpic):
                    raise ValueError('Cannot move Story to SubEpic with SubEpics')

    def _resequence_siblings(self) -> None:
        if hasattr(self, '_parent') and self._parent:
            self._parent._resequence_children()

    def _resequence_children(self) -> None:
        for idx, child in enumerate(self._children):
            if hasattr(child, 'sequential_order'):
                child.sequential_order = float(idx)

    def execute_action(self, action_name: str, parameters: Optional[Dict[str, Any]] = None) -> ActionResult:
        if self._bot is None:
            raise ValueError('Cannot execute action: node has no bot reference')
        available_actions = self._get_available_actions()
        if action_name not in available_actions:
            available_actions_list = ', '.join(available_actions)
            raise ValueError(f"Action '{action_name}' not found. Available actions: {available_actions_list}")
        self._validate_action_parameters(action_name, parameters)
        return ActionResult(success=True, action_name=action_name, data={'node': self.name, 'action': action_name})

    def _get_available_actions(self) -> List[str]:
        if hasattr(self, '_registered_actions'):
            return self._registered_actions
        if self._bot and hasattr(self._bot, 'behaviors'):
            return [behavior.name for behavior in self._bot.behaviors]
        return ['clarify', 'strategy', 'build', 'validate', 'render']

    def _validate_action_parameters(self, action_name: str, parameters: Optional[Dict[str, Any]]) -> None:
        if parameters is None:
            parameters = {}
        if isinstance(parameters, str):
            import json
            try:
                parameters = json.loads(parameters)
            except (json.JSONDecodeError, ValueError) as e:
                # Try sanitizing if it's a control character error
                if 'control character' in str(e).lower() or 'Invalid' in str(e):
                    from story_graph_ops._utils_min import sanitize_json_string
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"[StoryNode] JSON parse error in parameters, sanitizing: {str(e)}")
                    try:
                        parameters = json.loads(sanitize_json_string(parameters))
                    except (json.JSONDecodeError, ValueError):
                        raise ValueError(f'Invalid JSON parameters: {parameters}')
                else:
                    raise ValueError(f'Invalid JSON parameters: {parameters}')
        required_params = {
            'build': ['output'],
            'validate': ['rules'],
            'render': ['format']
        }
        valid_values = {
            'render': {
                'format': ['markdown', 'json', 'html']
            }
        }
        # Check for invalid parameters first
        expected_params = required_params.get(action_name, [])
        for param in parameters:
            if param not in expected_params and action_name in required_params:
                expected_str = ', '.join(expected_params) if expected_params else 'none'
                raise ValueError(f'Invalid parameter: {param}. Expected: {expected_str}')
        # Then check for missing required parameters
        if action_name in required_params:
            for param in required_params[action_name]:
                if param not in parameters:
                    raise ValueError(f'Missing required parameter: {param}')
        # Finally check for invalid values
        if action_name in valid_values:
            for param, valid_list in valid_values[action_name].items():
                if param in parameters and parameters[param] not in valid_list:
                    valid_str = ', '.join(valid_list)
                    raise ValueError(f'Invalid {param} value: {parameters[param]}. Expected: {valid_str}')

    def openStoryFile(self) -> dict:
        """Open story markdown files for this node and all children recursively.
        
        Returns:
            dict with status and list of opened files
        """
        opened_files = []
        
        if isinstance(self, Story):
            # Single story - open its file
            if self.file_link:
                opened_files.append(self.file_link)
        elif isinstance(self, (Epic, SubEpic)):
            # Epic or SubEpic - recursively open all story files
            for child in self.children:
                if isinstance(child, Story):
                    if child.file_link:
                        opened_files.append(child.file_link)
                elif isinstance(child, (Epic, SubEpic)):
                    # Recursively get files from nested epics/sub-epics
                    result = child.openStoryFile()
                    if result.get('files'):
                        opened_files.extend(result['files'])
        
        return {
            'status': 'success',
            'node': self.name,
            'node_type': self.node_type,
            'files': opened_files,
            'count': len(opened_files)
        }
    
    def _get_matching_test_files_for_story(self, sub_epic: 'SubEpic', workspace_dir: Path, test_dir: Path) -> List[str]:
        """Return workspace-relative paths for all test files matching this sub-epic (multi-language, multi-file)."""
        from story_graph_ops._utils_min import find_matching_test_files, name_to_test_stem
        import re
        primary = getattr(sub_epic, 'test_file', None) or ''
        if primary:
            p = Path(primary)
            stem = p.stem
            # Strip tier suffix (_server, _client, _e2e) and test suffix (.test, .spec) for pattern matching
            # e.g. "select-recipient_e2e.spec" -> "select-recipient"
            pattern = re.sub(r'(_server|_client|_e2e)?(\.test|\.spec)?$', '', stem)
            parent_str = str(p.parent)
            # Strip leading 'test/' or 'test\\' from parent path since we search relative to test_dir
            if parent_str.startswith('test/') or parent_str.startswith('test\\'):
                parent_str = parent_str[5:]
            under_path = parent_str if parent_str and parent_str != '.' else None
        else:
            pattern = name_to_test_stem(sub_epic.name or '')
            under_path = None
        matching_rel = find_matching_test_files(test_dir, pattern, under_path)
        # Paths relative to workspace for panel (test/...)
        return [f"test/{r}".replace('\\', '/') for r in matching_rel]

    def openTest(self) -> dict:
        """Open test files for this node and all children recursively.
        Supports multiple languages and multiple test files per scenario (e.g. test_foo.py, test_foo_e2e.js).
        Returns dict with status and list of opened test files (workspace-relative paths).
        """
        opened_files = []
        workspace_dir = Path(self._bot.bot_paths.workspace_directory) if self._bot and hasattr(self._bot, 'bot_paths') else Path('.')
        test_dir = workspace_dir / getattr(self._bot.bot_paths, 'test_path', Path('test')) if self._bot and hasattr(self._bot, 'bot_paths') else workspace_dir / 'test'

        if isinstance(self, Story):
            parent = self._parent
            sub_epic = None
            while parent:
                if isinstance(parent, SubEpic):
                    sub_epic = parent
                    break
                parent = parent._parent if hasattr(parent, '_parent') else None
            if sub_epic:
                all_paths = self._get_matching_test_files_for_story(sub_epic, workspace_dir, test_dir)
                for i, file_rel in enumerate(all_paths):
                    info = {'file': file_rel}
                    if i == 0:
                        info['test_class'] = self.test_class
                        info['scenarios'] = [
                            {'name': s.name, 'test_method': s.test_method}
                            for s in self.scenarios if s.test_method
                        ]
                    opened_files.append(info)
        elif isinstance(self, (Epic, SubEpic)):
            for child in self.children:
                if isinstance(child, Story):
                    parent = child._parent
                    sub_epic = None
                    while parent:
                        if isinstance(parent, SubEpic):
                            sub_epic = parent
                            break
                        parent = parent._parent if hasattr(parent, '_parent') else None
                    if sub_epic:
                        all_paths = self._get_matching_test_files_for_story(sub_epic, workspace_dir, test_dir)
                        for i, file_rel in enumerate(all_paths):
                            info = {'file': file_rel}
                            if i == 0:
                                info['test_class'] = child.test_class
                                info['scenarios'] = [
                                    {'name': s.name, 'test_method': s.test_method}
                                    for s in child.scenarios if s.test_method
                                ]
                            opened_files.append(info)
                elif isinstance(child, (Epic, SubEpic)):
                    result = child.openTest()
                    if result.get('files'):
                        opened_files.extend(result['files'])

        return {
            'status': 'success',
            'node': self.name,
            'node_type': self.node_type,
            'files': opened_files,
            'count': len(opened_files)
        }
    
    def openCode(self) -> dict:
        """Open source code files referenced by the test file for this node.
        
        Traces imports in the test file and resolves them to actual source files 
        under src/ in the workspace. Filters out stdlib, third-party libs, 
        and test helpers.
        
        Scope varies by node type:
        - Scenario: top-level imports + imports within the specific test_method only
        - Story: top-level imports + all imports within the test_class
        - SubEpic: all imports in the entire test_file
        - Epic: all imports from all test_files recursively
        
        Returns:
            dict with status and list of resolved source file paths (workspace-relative)
        """
        import ast
        from pathlib import Path
        
        if not self._bot or not hasattr(self._bot, 'bot_paths'):
            return {
                'status': 'success',
                'node': self.name,
                'node_type': self.node_type,
                'files': [],
                'count': 0
            }
        
        workspace_dir = Path(self._bot.bot_paths.workspace_directory)
        src_dir = workspace_dir / 'src'
        
        if not src_dir.exists():
            return {
                'status': 'success',
                'node': self.name,
                'node_type': self.node_type,
                'files': [],
                'count': 0
            }
        
        # Collect top-level package names that exist under src/
        src_packages = set()
        for item in src_dir.iterdir():
            if item.is_dir() and not item.name.startswith(('__', '.')):
                src_packages.add(item.name)
            elif item.is_file() and item.suffix == '.py' and item.name != '__init__.py':
                src_packages.add(item.stem)
        
        # Determine scope(s) based on node type
        scopes = self._get_code_scopes()
        
        code_files = []
        seen_code_files = set()
        
        for scope in scopes:
            test_file_rel = scope['test_file']
            test_file_path = workspace_dir / test_file_rel
            if not test_file_path.exists():
                continue
            
            try:
                source_code = test_file_path.read_text(encoding='utf-8')
                tree = ast.parse(source_code)
            except (SyntaxError, UnicodeDecodeError):
                continue
            
            # Collect imports scoped to the appropriate level
            imports = self._collect_scoped_imports(
                tree,
                test_class=scope.get('test_class'),
                test_methods=scope.get('test_methods')
            )
            
            # Filter imports to only workspace src/ modules and resolve to files
            for module_name in imports:
                top_package = module_name.split('.')[0]
                if top_package not in src_packages:
                    continue
                
                resolved = self._resolve_module_to_file(src_dir, module_name)
                if resolved:
                    rel_path = str(resolved.relative_to(workspace_dir)).replace('\\', '/')
                    if rel_path not in seen_code_files:
                        seen_code_files.add(rel_path)
                        code_files.append(rel_path)
        
        return {
            'status': 'success',
            'node': self.name,
            'node_type': self.node_type,
            'files': code_files,
            'count': len(code_files)
        }
    
    def _get_code_scopes(self) -> list:
        """Return list of scope dicts for import tracing, based on node type.
        
        Each scope has:
            test_file: workspace-relative path to test file (e.g. 'test/invoke_bot/...')
            test_class: class name to scope to (None = entire file)
            test_methods: list of method names to scope to (None = entire class)
        """
        if isinstance(self, Scenario):
            # Scenario: scope to specific test_method within test_class
            story = self._parent
            while story and not isinstance(story, Story):
                story = story._parent if hasattr(story, '_parent') else None
            
            sub_epic = (story._parent if story else self._parent)
            while sub_epic and not isinstance(sub_epic, SubEpic):
                sub_epic = sub_epic._parent if hasattr(sub_epic, '_parent') else None
            
            if sub_epic and hasattr(sub_epic, 'test_file') and sub_epic.test_file:
                test_file = sub_epic.test_file
                if not test_file.startswith('test/') and not test_file.startswith('test\\'):
                    test_file = f'test/{test_file}'
                return [{
                    'test_file': test_file,
                    'test_class': story.test_class if story else None,
                    'test_methods': [self.test_method] if self.test_method else None
                }]
            return []
        
        elif isinstance(self, Story):
            # Story: scope to entire test_class (all methods)
            sub_epic = self._parent
            while sub_epic and not isinstance(sub_epic, SubEpic):
                sub_epic = sub_epic._parent if hasattr(sub_epic, '_parent') else None
            
            if sub_epic and hasattr(sub_epic, 'test_file') and sub_epic.test_file:
                test_file = sub_epic.test_file
                if not test_file.startswith('test/') and not test_file.startswith('test\\'):
                    test_file = f'test/{test_file}'
                return [{
                    'test_file': test_file,
                    'test_class': self.test_class,
                    'test_methods': None
                }]
            return []
        
        elif isinstance(self, SubEpic):
            # SubEpic: scope to entire test_file, plus recurse into child sub-epics
            scopes = []
            if hasattr(self, 'test_file') and self.test_file:
                test_file = self.test_file
                if not test_file.startswith('test/') and not test_file.startswith('test\\'):
                    test_file = f'test/{test_file}'
                scopes.append({
                    'test_file': test_file,
                    'test_class': None,
                    'test_methods': None
                })
            for child in self._children:
                if isinstance(child, SubEpic):
                    scopes.extend(child._get_code_scopes())
            return scopes
        
        elif isinstance(self, Epic):
            # Epic: recurse into all children
            scopes = []
            for child in self._children:
                if isinstance(child, (SubEpic, Epic)):
                    scopes.extend(child._get_code_scopes())
            return scopes
        
        return []
    
    @staticmethod
    def _collect_scoped_imports(tree, test_class=None, test_methods=None) -> set:
        """Collect imports from AST tree, scoped to the appropriate level.
        
        - No test_class: ALL imports in the entire file
        - test_class, no test_methods: top-level imports + all imports within test_class
        - test_class AND test_methods: top-level imports + imports only within those methods
        """
        import ast
        imports = set()
        
        # Always collect top-level (module-level) imports
        for node in ast.iter_child_nodes(tree):
            StoryNode._collect_imports_from_node(node, imports)
        
        if test_class:
            # Find the test class
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == test_class:
                    if test_methods:
                        # Scenario scope: only imports from specific methods 
                        # (plus any class-body-level imports)
                        for item in ast.iter_child_nodes(node):
                            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                if item.name in test_methods:
                                    for sub in ast.walk(item):
                                        StoryNode._collect_imports_from_node(sub, imports)
                            else:
                                # Class-body-level imports (not inside a method)
                                StoryNode._collect_imports_from_node(item, imports)
                    else:
                        # Story scope: all imports from the entire class
                        for item in ast.walk(node):
                            StoryNode._collect_imports_from_node(item, imports)
                    break
        else:
            # SubEpic/Epic scope: ALL imports in the file
            for node in ast.walk(tree):
                StoryNode._collect_imports_from_node(node, imports)
        
        return imports
    
    @staticmethod
    def _collect_imports_from_node(node, imports: set):
        """Extract module names from import/from-import AST nodes."""
        import ast
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    
    @staticmethod
    def _resolve_module_to_file(src_dir, module_name: str):
        """Resolve a dotted module name to an actual file under src_dir.
        
        Tries: src/a/b/c.py, then src/a/b/c/__init__.py, then parent module.
        """
        from pathlib import Path
        parts = module_name.split('.')
        
        # Try as a .py file: src/actions/action_context.py
        candidate = src_dir / Path(*parts)
        py_file = candidate.with_suffix('.py')
        if py_file.exists():
            return py_file
        
        # Try as a package: src/scope/__init__.py
        init_file = candidate / '__init__.py'
        if init_file.exists():
            return init_file
        
        # Try parent module if the last part might be a class/function name
        if len(parts) > 1:
            parent_candidate = src_dir / Path(*parts[:-1])
            parent_py = parent_candidate.with_suffix('.py')
            if parent_py.exists():
                return parent_py
            parent_init = parent_candidate / '__init__.py'
            if parent_init.exists():
                return parent_init
        
        return None

    def openAll(self) -> dict:
        """Open all related files for this node: story files, test files, exploration docs, and inferred code files.
        
        Returns:
            dict with story_files, test_files, exploration_docs, and code_files lists
        """
        import re
        from pathlib import Path
        
        # Get story files
        story_result = self.openStoryFile()
        story_files = story_result.get('files', [])
        
        # Get test files
        test_result = self.openTest()
        test_files = test_result.get('files', [])
        
        # Get exploration docs (for sub-epics)
        exploration_docs = []
        if self._bot and hasattr(self._bot, 'bot_paths'):
            exploration_path = self._bot.bot_paths.story_graph_paths.behavior_path('exploration')
            if exploration_path and exploration_path.exists():
                # Collect exploration docs for this node and ancestors
                node_names = [self.name]
                # Walk up the parent chain to collect names
                parent = getattr(self, '_parent', None)
                while parent:
                    if hasattr(parent, 'name'):
                        node_names.append(parent.name)
                    parent = getattr(parent, '_parent', None)
                
                # Check each node name for an exploration doc
                for name in node_names:
                    if name:
                        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
                        if slug:
                            candidate = exploration_path / f"{slug}-exploration.md"
                            if candidate.exists() and str(candidate) not in exploration_docs:
                                exploration_docs.append(str(candidate))
        
        # Get inferred code files
        code_result = self.openCode()
        code_files = code_result.get('files', [])
        
        return {
            'status': 'success',
            'node': self.name,
            'node_type': self.node_type,
            'story_files': story_files,
            'test_files': test_files,
            'exploration_docs': exploration_docs,
            'code_files': code_files,
            'total_count': len(story_files) + len(test_files) + len(exploration_docs) + len(code_files)
        }
    
    def openStoryGraph(self) -> dict:
        """Open story-graph.json with this node's path expanded and cursor positioned.
        
        Returns:
            dict with status and story graph path, node path, and line number info
        """
        from pathlib import Path
        import json
        if not self._bot or not hasattr(self._bot, 'bot_paths'):
            raise ValueError('Bot context required to open story graph')
        
        story_graph_path = self._bot.bot_paths.story_graph_paths.story_graph_path
        node_path = self._scope_command_for_node()
        
        # Try to find line number for this node in the JSON file
        line_number = None
        if story_graph_path.exists():
            try:
                with open(story_graph_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    text = ''.join(lines)
                    
                # Search for the node by name in the JSON
                # Look for "name": "NodeName" pattern
                for i, line in enumerate(lines):
                    # Match node name in JSON (accounting for escaped quotes)
                    import re
                    name_pattern = re.compile(r'"name"\s*:\s*"' + re.escape(self.name) + r'"')
                    if name_pattern.search(line):
                        # Verify this is the right node by checking context
                        # For epics: should be within "epics": [ ... ]
                        # For sub-epics: should be within parent epic's "sub_epics": [ ... ]
                        # For stories: should be within "stories": [ ... ]
                        line_number = i + 1  # VS Code uses 1-based line numbers
                        break
            except Exception as e:
                # If we can't find the line number, that's okay - cursor positioning is optional
                pass
        
        return {
            'status': 'success',
            'node': self.name,
            'node_type': self.node_type,
            'story_graph_path': str(story_graph_path),
            'node_path': node_path,
            'expand_path': node_path,
            'line_number': line_number
        }

@dataclass
class Epic(StoryNode):
    domain_concepts: Optional[List[DomainConcept]] = None

    def __post_init__(self):
        super().__post_init__()
        if self.domain_concepts is None:
            self.domain_concepts = []
        self._children: List['StoryNode'] = []

    @property
    def children(self) -> List['StoryNode']:
        return self._children

    @property
    def all_stories(self) -> List['Story']:
        stories = []
        for child in self.children:
            if isinstance(child, Story):
                stories.append(child)
            elif isinstance(child, (SubEpic, StoryGroup)):
                stories.extend(self._get_stories_from_node(child))
        return stories

    def _get_stories_from_node(self, node: StoryNode) -> List['Story']:
        stories = []
        for child in node.children:
            if isinstance(child, Story):
                stories.append(child)
            elif hasattr(child, 'children'):
                stories.extend(self._get_stories_from_node(child))
        return stories

    def find_sub_epic_by_name(self, sub_epic_name: str) -> Optional['SubEpic']:
        for child in self.children:
            if isinstance(child, SubEpic) and child.name == sub_epic_name:
                return child
        return None

    @property
    def sub_epics(self) -> List['SubEpic']:
        return [child for child in self.children if isinstance(child, SubEpic)]

    def comparison_role(self) -> str:
        return "epic"

    def get_sub_epics(self) -> List["SubEpic"]:
        return list(self.sub_epics)

    def get_stories(self) -> List["Story"]:
        return []

    @property
    def behavior_needed(self) -> str:
        hierarchy = ['shape', 'exploration', 'scenarios', 'tests', 'code']
        
        sub_epics = self.sub_epics
        if not sub_epics:
            return 'shape'
        
        highest_behavior = 'code'
        
        for sub_epic in sub_epics:
            sub_epic_behavior = sub_epic.behavior_needed
            if hierarchy.index(sub_epic_behavior) < hierarchy.index(highest_behavior):
                highest_behavior = sub_epic_behavior
        
        return highest_behavior

    def create(self, name: Optional[str] = None, child_type: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Alias for create_child"""
        return self.create_child(name, child_type, position)
    
    def create_sub_epic(self, name: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Create SubEpic child"""
        return self.create_child(name, 'SubEpic', position)
    
    def create_child(self, name: Optional[str] = None, child_type: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        # Validate name is not empty
        if name is not None and not name.strip():
            raise ValueError("Child name cannot be empty")
            
        for child in self.children:
            if child.name == name:
                raise ValueError(f"Child with name '{name}' already exists")
        if child_type == 'SubEpic' or child_type is None:
            sequential_order = float(len(self._children)) if position is None else float(position)
            child = SubEpic(name=name or self._generate_unique_child_name(), sequential_order=sequential_order, _parent=self, _bot=self._bot)
        else:
            raise ValueError(f'Epic can only create SubEpic children, not {child_type}')
            
        if position is not None:
            adjusted_position = min(position, len(self._children))
            self._children.insert(adjusted_position, child)
            self._resequence_children()
        else:
            child.sequential_order = float(len(self._children))
            self._children.append(child)
        
        # Save changes to disk
        child.save()
        
        return child

    def _generate_unique_child_name(self, child_type: str = 'Child') -> str:
        counter = 1
        while True:
            name = f'{child_type}{counter}'
            if not any(child.name == name for child in self.children):
                return name
            counter += 1

    def delete(self, cascade: bool = True) -> dict:
        """Delete this epic from the story map. Always cascades to delete all children."""
        if not self._bot:
            raise ValueError('Cannot delete epic without bot context')
        
        story_map = self._bot.story_map
        return story_map.delete_epic(self.name)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], bot: Optional[Any]=None) -> 'Epic':
        domain_concepts = [DomainConcept.from_dict(dc) for dc in data.get('domain_concepts', [])]
        epic = cls(
            name=data.get('name', ''),
            domain_concepts=domain_concepts,
            behavior=data.get('behavior'),
            _bot=bot
        )
        for i, sub_epic_data in enumerate(data.get('sub_epics', [])):
            if sub_epic_data.get('sequential_order') is None:
                sub_epic_data = {**sub_epic_data, 'sequential_order': float(i)}
            sub_epic = SubEpic.from_dict(sub_epic_data, parent=epic, bot=bot)
            epic._children.append(sub_epic)
        for story_group_data in data.get('story_groups', []):
            story_group = StoryGroup.from_dict(story_group_data, parent=epic, bot=bot)
            epic._children.append(story_group)
        return epic

@dataclass
class SubEpic(StoryNode):
    sequential_order: float
    domain_concepts: Optional[List[DomainConcept]] = None
    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is None:
            raise ValueError('SubEpic requires sequential_order')
        if self.domain_concepts is None:
            self.domain_concepts = []
        self._children: List['StoryNode'] = []
        # Initialize test_file attribute (not a dataclass field to avoid signature issues)
        if not hasattr(self, 'test_file'):
            self.test_file = None

    @property
    def children(self) -> List['StoryNode']:
        """Return children, transparently exposing Stories from StoryGroups."""
        if self.has_stories and not self.has_subepics:
            # Pure stories case: aggregate all stories from all story groups
            stories = []
            for child in self._children:
                if isinstance(child, StoryGroup):
                    stories.extend(child.children)
            return stories
        elif self.has_stories and self.has_subepics:
            # Mixed case (violation state): return SubEpics + Stories from StoryGroups
            result = []
            for child in self._children:
                if isinstance(child, SubEpic):
                    result.append(child)
                elif isinstance(child, StoryGroup):
                    result.extend(child.children)
            return result
        return self._children
    
    def __getitem__(self, child_name: str) -> 'StoryNode':
        """Access child by name"""
        for child in self.children:
            if child.name == child_name:
                return child
        raise KeyError(f"Child '{child_name}' not found in SubEpic '{self.name}'")
    
    def __getitem__(self, child_name: str) -> 'StoryNode':
        """Access child by name"""
        for child in self.children:
            if child.name == child_name:
                return child
        raise KeyError(f"Child '{child_name}' not found in SubEpic '{self.name}'")

    @classmethod
    def from_dict(cls, data: Dict[str, Any], parent: Optional[StoryNode]=None, bot: Optional[Any]=None) -> 'SubEpic':
        sequential_order = data.get('sequential_order')
        if sequential_order is None:
            sequential_order = 0.0
        domain_concepts = [DomainConcept.from_dict(dc) for dc in data.get('domain_concepts', [])]
        sub_epic = cls(
            name=data.get('name', ''),
            sequential_order=float(sequential_order),
            domain_concepts=domain_concepts,
            behavior=data.get('behavior'),
            _parent=parent,
            _bot=bot
        )
        sub_epic.test_file = data.get('test_file')
        for nested_sub_epic_data in data.get('sub_epics', []):
            nested_sub_epic = SubEpic.from_dict(nested_sub_epic_data, parent=sub_epic, bot=bot)
            sub_epic._children.append(nested_sub_epic)
        for story_group_data in data.get('story_groups', []):
            story_group = StoryGroup.from_dict(story_group_data, parent=sub_epic, bot=bot)
            sub_epic._children.append(story_group)
        return sub_epic

    @property
    def sub_epics(self) -> List['SubEpic']:
        return [child for child in self._children if isinstance(child, SubEpic)]

    @property
    def stories(self) -> List['Story']:
        """Direct story children (extracted from StoryGroups)."""
        result = []
        for child in self._children:
            if isinstance(child, Story):
                result.append(child)
            elif isinstance(child, StoryGroup):
                result.extend(child.children)
        return result

    def comparison_role(self) -> str:
        return "sub_epic"

    def get_sub_epics(self) -> List["SubEpic"]:
        return list(self.sub_epics)

    def get_stories(self) -> List["Story"]:
        return list(self.stories)

    @property
    def all_stories(self) -> List['Story']:
        """All stories recursively through nested sub-epics."""
        if self.has_subepics:
            stories = []
            for nested_se in self.sub_epics:
                stories.extend(nested_se.all_stories)
            return stories
        return self.stories

    @property
    def has_subepics(self) -> bool:
        return any(isinstance(child, SubEpic) for child in self._children)

    @property
    def has_stories(self) -> bool:
        # Check for actual Story objects, not just StoryGroups
        # An empty StoryGroup doesn't count as having stories
        for child in self._children:
            if isinstance(child, Story):
                return True
            elif isinstance(child, StoryGroup):
                # Check if the StoryGroup actually contains Stories
                if child._children and any(isinstance(story, Story) for story in child._children):
                    return True
        return False

    @property
    def behavior_needed(self) -> str:
        hierarchy = ['shape', 'exploration', 'scenarios', 'tests', 'code']
        
        if self.has_subepics:
            sub_epics = [child for child in self._children if isinstance(child, SubEpic)]
            if not sub_epics:
                return 'shape'
            
            highest_behavior = 'code'
            for sub_epic in sub_epics:
                sub_epic_behavior = sub_epic.behavior_needed
                if hierarchy.index(sub_epic_behavior) < hierarchy.index(highest_behavior):
                    highest_behavior = sub_epic_behavior
            
            return highest_behavior
        else:
            stories = [child for child in self.children if isinstance(child, Story)]
            
            if not stories:
                return 'shape'
            
            current_behavior = stories[0].behavior_needed
            
            for story in stories[1:]:
                current_behavior = story.get_behavior_needed(current_behavior)
            
            return current_behavior

    @property
    def behaviors_needed(self) -> List[str]:
        """Return list of applicable behaviors for this sub-epic.
        
        Empty sub-epics (no sub-epics, no stories) return both 'shape' and 'exploration'.
        Sub-epics with content return single behavior in a list.
        """
        if self.has_subepics:
            sub_epics = [child for child in self._children if isinstance(child, SubEpic)]
            if not sub_epics:
                return ['shape', 'exploration']
            return [self.behavior_needed]
        else:
            stories = [child for child in self.children if isinstance(child, Story)]
            if not stories:
                return ['shape', 'exploration']
            return [self.behavior_needed]

    def create(self, name: Optional[str] = None, child_type: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Alias for create_child"""
        return self.create_child(name, child_type, position)
    
    def create_story(self, name: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Create Story child"""
        return self.create_child(name, 'Story', position)
    
    def create_sub_epic(self, name: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Create SubEpic child"""
        return self.create_child(name, 'SubEpic', position)
    
    def create_child(self, name: Optional[str] = None, child_type: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        # Validate name is not empty
        if name is not None and not name.strip():
            raise ValueError("Child name cannot be empty")
            
        if child_type is None:
            child_type = 'Story' if self.has_stories else 'SubEpic'
        
        if child_type == 'SubEpic':
            for child in self.children:
                if child.name == name:
                    raise ValueError(f"Child with name '{name}' already exists")
            if self.has_stories:
                raise ValueError('Cannot create SubEpic under SubEpic with Stories')
            sequential_order = float(len(self._children)) if position is None else float(position)
            child = SubEpic(name=name or self._generate_unique_child_name(), sequential_order=sequential_order, _parent=self, _bot=self._bot)
                
        elif child_type == 'Story':
            # Only prevent creating Stories if there are SubEpics AND no Stories exist yet
            # If Stories already exist, we're in a mixed state which is handled
            if self.has_subepics and not self.has_stories:
                raise ValueError('Cannot create Story under SubEpic with SubEpics')
            story_group = self._get_or_create_story_group()
                
            for existing_story in story_group.children:
                if existing_story.name == name:
                    raise ValueError(f"Child with name '{name}' already exists")
            sequential_order = float(len(story_group._children)) if position is None else float(position)
            child = Story(name=name or self._generate_unique_child_name('Story'), sequential_order=sequential_order, _parent=story_group, _bot=self._bot)
                
            if position is not None:
                adjusted_position = min(position, len(story_group._children))
                story_group._children.insert(adjusted_position, child)
                story_group._resequence_children()
            else:
                child.sequential_order = float(len(story_group._children))
                story_group._children.append(child)
            
            # Save changes to disk
            child.save()
            
            return child
        else:
            raise ValueError(f'SubEpic can only create SubEpic or Story children, not {child_type}')
        if position is not None:
            adjusted_position = min(position, len(self._children))
            self._children.insert(adjusted_position, child)
            self._resequence_children()
        else:
            child.sequential_order = float(len(self._children))
            self._children.append(child)
        
        # Save changes to disk
        child.save()
        
        return child

    def _get_or_create_story_group(self) -> 'StoryGroup':
        for child in self._children:
            if isinstance(child, StoryGroup):
                return child
        story_group = StoryGroup(name=f'{self.name} Stories', sequential_order=float(len(self._children)), _parent=self, _bot=self._bot)
        self._children.append(story_group)
        return story_group

    def _generate_unique_child_name(self, child_type: str = 'Child') -> str:
        if child_type == 'Story' or (hasattr(self, 'has_stories') and self.has_stories):
            story_group = self._get_or_create_story_group()
            counter = 1
            while True:
                name = f'{child_type}{counter}'
                if not any(child.name == name for child in story_group.children):
                    return name
                counter += 1
        else:
            counter = 1
            while True:
                name = f'{child_type}{counter}'
                if not any(child.name == name for child in self.children):
                    return name
                counter += 1

@dataclass
class StoryGroup(StoryNode):
    sequential_order: float
    group_type: str = 'and'
    connector: Optional[str] = None
    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is None:
            raise ValueError('StoryGroup requires sequential_order')
        self._children: List['StoryNode'] = []

    @property
    def children(self) -> List['StoryNode']:
        return self._children

    @property
    def behavior_needed(self) -> str:
        """Determine the highest-priority behavior needed for this story group.

        Priority order: code > tests > scenarios > exploration
        If any child requires a higher-priority behavior, return that.
        """
        hierarchy = ['code', 'tests', 'scenarios', 'exploration']
        # collect child behaviors; if child lacks attribute, skip
        priorities = []
        for child in self._children:
            try:
                b = child.behavior_needed
            except Exception:
                # skip children that don't expose behavior_needed
                continue
            if b in hierarchy:
                priorities.append(hierarchy.index(b))
        if not priorities:
            return 'exploration'
        # return the most advanced (lowest index) behavior
        min_idx = min(priorities)
        return hierarchy[min_idx]

    @property
    def behaviors_needed(self) -> List[str]:
        """Return a deduplicated list of behaviors needed by children, ordered by priority."""
        hierarchy = ['code', 'tests', 'scenarios', 'exploration']
        seen = []
        for child in self._children:
            try:
                child_beh = getattr(child, 'behaviors_needed', None)
            except Exception:
                child_beh = None
            if child_beh is None:
                # try single behavior
                try:
                    cb = child.behavior_needed
                    child_beh = [cb]
                except Exception:
                    child_beh = []
            for b in child_beh:
                if b not in seen:
                    seen.append(b)
        # sort seen by hierarchy
        seen.sort(key=lambda x: hierarchy.index(x) if x in hierarchy else len(hierarchy))
        return seen
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], parent: Optional[StoryNode]=None, bot: Optional[Any]=None) -> 'StoryGroup':
        """Create StoryGroup from dictionary data."""
        sequential_order = data.get('sequential_order')
        if sequential_order is None:
            sequential_order = 0.0
        group_type = data.get('type', 'and')
        connector = data.get('connector')
        story_group = cls(
            name='',  # StoryGroup doesn't have a name in the typical sense
            sequential_order=float(sequential_order),
            group_type=group_type,
            connector=connector,
            behavior=data.get('behavior'),
            _parent=parent,
            _bot=bot
        )
        for story_data in data.get('stories', []):
            story = Story.from_dict(story_data, parent=story_group, bot=bot)
            story_group._children.append(story)
        return story_group

@dataclass
class Story(StoryNode):
    sequential_order: float
    connector: Optional[str] = None
    story_type: str = 'user'
    users: Optional[List[StoryUser]] = None
    test_file: Optional[str] = None
    test_class: Optional[str] = None
    file_link: Optional[str] = None  # Link to story markdown file
    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is None:
            raise ValueError('Story requires sequential_order')
        if self.users is None:
            self.users = []
        self._children: List['StoryNode'] = []

    @property
    def children(self) -> List['StoryNode']:
        return self._children

    def comparison_role(self) -> str:
        return "story"

    def get_sub_epics(self) -> List["SubEpic"]:
        return []

    def get_stories(self) -> List["Story"]:
        return []
    
    def __getitem__(self, child_name: str) -> 'StoryNode':
        """Access child by name"""
        for child in self.children:
            if child.name == child_name:
                return child
        raise KeyError(f"Child '{child_name}' not found in Story '{self.name}'")

    @property
    def scenarios(self) -> List['Scenario']:
        return [child for child in self._children if isinstance(child, Scenario)]

    @property
    def acceptance_criteria(self) -> List['AcceptanceCriteria']:
        return [child for child in self._children if isinstance(child, AcceptanceCriteria)]

    @property
    def default_test_class(self) -> str:
        if not self.name:
            return ''
        words = self.name.split()
        class_name = ''.join((word.capitalize() for word in words))
        return f'Test{class_name}'
    
    def has_acceptance_criteria(self) -> bool:
        return len(self.acceptance_criteria) > 0
    
    def has_scenarios(self) -> bool:
        return len(self.scenarios) > 0
    
    def has_tests(self) -> bool:
        if self.test_class:
            return True
        
        for scenario in self.scenarios:
            if scenario.test_method:
                return True
        
        return False

    @property
    def all_scenarios_have_tests(self) -> bool:
        if not self.scenarios:
            return False
        
        # Check if all scenarios have test_method fields populated
        if not all(scenario.test_method for scenario in self.scenarios):
            return False
        
        # If no bot context, fall back to simple check
        if not self._bot or not hasattr(self._bot, 'bot_paths'):
            return True
        
        # Check if the test file actually exists
        # test_file ALWAYS comes from parent sub-epic, never from the story itself
        test_file = None
        test_class = self.test_class
        
        # Get test_file from parent sub-epic
        parent = self._parent
        while parent:
            if isinstance(parent, SubEpic):
                test_file = parent.test_file if hasattr(parent, 'test_file') else None
                break
            parent = parent._parent if hasattr(parent, '_parent') else None
        
        # If no test_file, tests don't exist
        if not test_file:
            return False
        
        # Check if test file exists on disk
        from pathlib import Path
        workspace_dir = Path(self._bot.bot_paths.workspace_directory if hasattr(self._bot.bot_paths, 'workspace_directory') else '.')
        test_dir = workspace_dir / self._bot.bot_paths.test_path
        test_file_path = test_dir / test_file
        
        if not test_file_path.exists():
            return False
        
        # Check if test class exists in file
        if test_class:
            from story_graph_ops._utils_min import find_test_class_line
            if not find_test_class_line(test_file_path, test_class):
                return False
        
        return True
    
    @property
    def many_scenarios(self) -> int:
        return len(self.scenarios)
    
    @property
    def many_acceptance_criteria(self) -> int:
        return len(self.acceptance_criteria)
    
    @property
    def behavior_needed(self) -> str:
        return self.get_behavior_needed()
    
    @property
    def behaviors_needed(self) -> List[str]:
        """Return list of applicable behaviors for this story.
        
        Empty stories (no AC, no scenarios) return both 'exploration' and 'scenarios'.
        Stories with content return single behavior in a list.
        """
        if self.all_scenarios_have_tests:
            return ['code']
        if self.many_scenarios > 0:
            return ['tests']
        if self.many_acceptance_criteria > 0:
            return ['scenarios']
        # Empty story - return both options
        return ['exploration', 'scenarios']
    
    def get_behavior_needed(self, behavior_already_needed: str = None) -> str:
        hierarchy = ['code', 'tests', 'scenarios', 'exploration']
        start_idx = 0 if behavior_already_needed is None else hierarchy.index(behavior_already_needed)
        
        if start_idx <= hierarchy.index('code'):
            if self.all_scenarios_have_tests:
                return 'code'
        
        if start_idx <= hierarchy.index('tests'):
            if self.many_scenarios > 0:
                return 'tests'
        
        if start_idx <= hierarchy.index('scenarios'):
            if self.many_acceptance_criteria > 0:
                return 'scenarios'
        
        return 'exploration'

    def create(self, name: Optional[str] = None, child_type: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Alias for create_child"""
        return self.create_child(name, child_type, position)
    
    def create_scenario(self, name: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Create Scenario child"""
        return self.create_child(name, 'Scenario', position)
    
    def create_acceptance_criteria(self, name: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Create AcceptanceCriteria child"""
        return self.create_child(name, 'AcceptanceCriteria', position)
    
    def create_child(self, name: Optional[str] = None, child_type: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        # Validate name is not empty
        if name is not None and not name.strip():
            raise ValueError("Child name cannot be empty")
            
        for child in self.children:
            if child.name == name:
                raise ValueError(f"Child with name '{name}' already exists")
        if child_type == 'Scenario' or child_type is None:
            sequential_order = float(len(self._filter_children_by_type(Scenario))) if position is None else float(position)
            child = Scenario(name=name or self._generate_unique_child_name(), sequential_order=sequential_order, _parent=self, _bot=self._bot)
        elif child_type == 'AcceptanceCriteria':
            sequential_order = float(len(self._filter_children_by_type(AcceptanceCriteria))) if position is None else float(position)
            child = AcceptanceCriteria(name=name or self._generate_unique_child_name(), text=name or self._generate_unique_child_name(), sequential_order=sequential_order, _parent=self, _bot=self._bot)
        else:
            raise ValueError(f'Story can only create Scenario or AcceptanceCriteria children, not {child_type}')
        if position is not None:
            adjusted_position = min(position, len(self._children))
            self._children.insert(adjusted_position, child)
            self._resequence_children()
        else:
            self._children.append(child)
        
        # Save changes to disk
        child.save()
        
        return child

    def _generate_unique_child_name(self, child_type: str = 'Child') -> str:
        counter = 1
        while True:
            name = f'{child_type}{counter}'
            if not any(child.name == name for child in self.children):
                return name
            counter += 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any], parent: Optional[StoryNode]=None, bot: Optional[Any]=None) -> 'Story':
        sequential_order = data.get('sequential_order')
        if sequential_order is None:
            sequential_order = 0.0
        users = [StoryUser.from_str(u) for u in data.get('users', [])]
        story = cls(
            name=data.get('name', ''),
            sequential_order=float(sequential_order),
            connector=data.get('connector'),
            story_type=data.get('story_type', 'user'),
            users=users,
            test_file=data.get('test_file'),
            test_class=data.get('test_class'),
            file_link=data.get('file_link'),
            behavior=data.get('behavior'),
            _parent=parent,
            _bot=bot
        )
        acceptance_criteria_data = data.get('acceptance_criteria', [])
        for idx, ac_data in enumerate(acceptance_criteria_data):
            ac = AcceptanceCriteria.from_dict(ac_data, index=idx, parent=story, bot=bot)
            story._children.append(ac)
        scenarios_data = data.get('scenarios', [])
        for idx, scenario_data in enumerate(scenarios_data):
            scenario = Scenario.from_dict(scenario_data, index=idx, parent=story, bot=bot)
            story._children.append(scenario)
        # Legacy support: merge scenario_outlines into scenarios
        scenario_outlines_data = data.get('scenario_outlines', [])
        for idx, scenario_outline_data in enumerate(scenario_outlines_data):
            scenario = Scenario.from_dict(scenario_outline_data, index=len(scenarios_data) + idx, parent=story, bot=bot)
            story._children.append(scenario)
        return story

@dataclass
class Scenario(StoryNode):
    sequential_order: float
    type: str = ''
    background: List[str] = field(default_factory=list)
    examples: Optional[List[Dict[str, Any]]] = None
    test_method: Optional[str] = None
    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is None:
            raise ValueError('Scenario requires sequential_order')
        # Normalize examples to a list of table dicts for consistency
        self.examples = self._normalize_examples_data(self.examples)
        self._children: List['StoryNode'] = []

    @staticmethod
    def _normalize_examples_data(examples: Any) -> Optional[List[Dict[str, Any]]]:
        """Normalize examples into a list of table dicts (columns/rows)."""
        if not examples:
            return None
        if isinstance(examples, dict):
            return [examples]
        if isinstance(examples, list):
            tables = [tbl for tbl in examples if isinstance(tbl, dict)]
            return tables or None
        return None

    @property
    def children(self) -> List['StoryNode']:
        return self._children

    @property
    def steps(self) -> List['Step']:
        return self._filter_children_by_type(Step)

    @property
    def examples_columns(self) -> List[str]:
        """Return columns from examples table, or empty list if no examples."""
        for table in self.examples or []:
            columns = table.get('columns') or table.get('headers')
            if columns:
                return columns
        return []

    @property
    def examples_rows(self) -> List[List[str]]:
        """Return rows from examples table, or empty list if no examples."""
        for table in self.examples or []:
            columns = table.get('columns') or table.get('headers')
            rows = table.get('rows', [])
            if columns and rows:
                return rows
        return []

    @property
    def has_examples(self) -> bool:
        """Check if this scenario has examples (data-driven testing)."""
        if not self.examples:
            return False
        for table in self.examples:
            columns = table.get('columns') or table.get('headers')
            if columns:
                return True
        return False

    @property
    def default_test_method(self) -> str:
        return StoryNode._generate_default_test_method_name(self.name)

    @property
    def behavior_needed(self) -> str:
        if not self.test_method:
            return 'tests'
        
        if not self._bot or not hasattr(self._bot, 'bot_paths'):
            return 'code' if self.test_method else 'tests'
        
        parent = self._parent
        while parent and not isinstance(parent, Story):
            parent = parent._parent if hasattr(parent, '_parent') else None
        
        if not parent:
            return 'code' if self.test_method else 'tests'
        
        # test_file ALWAYS comes from parent sub-epic, never from the story itself
        test_file = None
        test_class = parent.test_class
        
        # Get test_file from parent sub-epic (Story's parent is StoryGroup, StoryGroup's parent is SubEpic)
        sub_epic_parent = parent._parent
        while sub_epic_parent:
            if isinstance(sub_epic_parent, SubEpic):
                test_file = sub_epic_parent.test_file if hasattr(sub_epic_parent, 'test_file') else None
                break
            sub_epic_parent = sub_epic_parent._parent if hasattr(sub_epic_parent, '_parent') else None
        
        if not test_file or not test_class:
            return 'tests'
        
        from pathlib import Path
        workspace_dir = Path(self._bot.bot_paths.workspace_directory if hasattr(self._bot.bot_paths, 'workspace_directory') else '.')
        test_dir = workspace_dir / self._bot.bot_paths.test_path
        test_file_path = test_dir / test_file
        
        if not test_file_path.exists():
            return 'tests'
        
        from story_graph_ops._utils_min import find_test_method_line
        if not find_test_method_line(test_file_path, self.test_method):
            return 'tests'
        
        return 'code'

    @classmethod
    def from_dict(cls, data: Dict[str, Any], index: int=0, parent: Optional[StoryNode]=None, bot: Optional[Any]=None) -> 'Scenario':
        sequential_order = float(data.get('sequential_order', index + 1))
        scenario = cls(name=data.get('name', ''), sequential_order=sequential_order, type=data.get('type', ''), background=data.get('background', []), examples=data.get('examples'), test_method=data.get('test_method'), _parent=parent, _bot=bot)
        cls._add_steps_to_node(scenario, cls._parse_steps_from_data(data.get('steps', '')))
        return scenario

# ScenarioOutline class has been removed - use Scenario with optional examples field instead

@dataclass
class AcceptanceCriteria(StoryNode):
    text: str = ''
    sequential_order: float = 0.0
    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is None:
            raise ValueError('AcceptanceCriteria requires sequential_order')

    @property
    def children(self) -> List['StoryNode']:
        return []

    @classmethod
    def from_dict(cls, data: Union[str, Dict[str, Any]], index: int=0, parent: Optional[StoryNode]=None, bot: Optional[Any]=None) -> 'AcceptanceCriteria':
        if isinstance(data, str):
            text = data
            sequential_order = float(index + 1)
        else:
            text = data.get('description', data.get('text', ''))
            sequential_order = float(data.get('sequential_order', index + 1))
        return cls(name=text, text=text, sequential_order=sequential_order, _parent=parent, _bot=bot)

@dataclass
class Step(StoryNode):
    text: str = ''
    sequential_order: float = 0.0
    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is None:
            raise ValueError('Step requires sequential_order')

    @property
    def children(self) -> List['StoryNode']:
        return []

class EpicsCollection:
    
    def __init__(self, epics: List[Epic]):
        self._epics = epics
        self._epics_by_name = {epic.name: epic for epic in epics}
    
    def __getitem__(self, name: str) -> Epic:
        if name not in self._epics_by_name:
            raise KeyError(f'Epic "{name}" not found')
        return self._epics_by_name[name]
    
    def __iter__(self) -> Iterator[Epic]:
        return iter(self._epics)
    
    def __len__(self) -> int:
        return len(self._epics)

@dataclass
class Increment:
    name: str
    priority: int
    stories: List[Union[str, Dict[str, Any]]] = field(default_factory=list)
    description: Optional[str] = None
    goal: Optional[str] = None
    estimated_stories: Optional[int] = None
    relative_size: Optional[str] = None
    approach: Optional[str] = None
    focus: Optional[str] = None
    _story_map: Optional['StoryMap'] = field(default=None, repr=False)

    def __getitem__(self, story_name: str) -> 'Story':
        """Allow story access by name for path resolution: increment['Story Name'] -> Story node."""
        story_names = [self._story_name(s) for s in self.stories]
        if story_name not in story_names:
            raise KeyError(f'Story "{story_name}" not found in increment "{self.name}"')
        if not self._story_map:
            raise ValueError('Increment has no story_map reference for story lookup')
        story = self._story_map.find_story_by_name(story_name)
        if not story:
            raise KeyError(f'Story "{story_name}" not found in story graph')
        return story

    def _story_name(self, story) -> str:
        return story['name'] if isinstance(story, dict) else str(story)

    @property
    def stories_in_order(self) -> List[Dict[str, Any]]:
        story_dicts = [
            s if isinstance(s, dict) else {'name': s, 'sequential_order': 0}
            for s in self.stories
        ]
        return sorted(story_dicts, key=lambda s: s.get('sequential_order', 0))

    def format_for_cli(self) -> str:
        output_lines = [f"{self.name}:"]
        if self.stories:
            for story in self.stories_in_order:
                output_lines.append(f"  - {story['name']}")
        else:
            output_lines.append("  (no stories)")
        return "\n".join(output_lines)

    def add_story(self, story_name: str, position: Optional[int] = None) -> None:
        if any(self._story_name(s) == story_name for s in self.stories):
            raise ValueError(f'Story "{story_name}" already in increment "{self.name}"')
        if position is not None:
            idx = max(0, min(int(position), len(self.stories)))
            self.stories.insert(idx, story_name)
        else:
            self.stories.append(story_name)

    def remove_story(self, story_name: str) -> None:
        updated = [s for s in self.stories if self._story_name(s) != story_name]
        if len(updated) == len(self.stories):
            raise ValueError(f'Story "{story_name}" not in increment "{self.name}"')
        self.stories = updated

    def reorder_story(self, story_name: str, position: int) -> None:
        story = next((s for s in self.stories if self._story_name(s) == story_name), None)
        if story is None:
            raise ValueError(f'Story "{story_name}" not in increment "{self.name}"')
        self.stories.remove(story)
        position = max(0, min(position, len(self.stories)))
        self.stories.insert(position, story)

    def rename_story_reference(self, old_name: str, new_name: str) -> None:
        self.stories = [
            {'name': new_name, 'sequential_order': s.get('sequential_order', 1.0) if isinstance(s, dict) else 1.0}
            if self._story_name(s) == old_name else s
            for s in self.stories
        ]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Increment':
        return cls(
            name=data.get('name', ''),
            priority=data.get('priority', 0),
            stories=data.get('stories', []),
            description=data.get('description'),
            goal=data.get('goal'),
            estimated_stories=data.get('estimated_stories'),
            relative_size=data.get('relative_size'),
            approach=data.get('approach'),
            focus=data.get('focus')
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'name': self.name,
            'priority': self.priority,
            'stories': self.stories,
        }
        optional_fields = ('description', 'goal', 'estimated_stories', 'relative_size', 'approach', 'focus')
        result.update({k: getattr(self, k) for k in optional_fields if getattr(self, k) is not None})
        return result

class IncrementCollection:

    def __init__(self, increments: List[Increment], story_map: Optional['StoryMap'] = None):
        self._increments = increments
        self._story_map = story_map
        if story_map:
            for inc in self._increments:
                inc._story_map = story_map
        self._rebuild_indexes()

    def _rebuild_indexes(self) -> None:
        self._by_name = {inc.name: inc for inc in self._increments}
        self._by_priority = {inc.priority: inc for inc in self._increments}

    def __iter__(self) -> Iterator[Increment]:
        return iter(self._increments)

    def __len__(self) -> int:
        return len(self._increments)

    def __getitem__(self, name: str) -> Increment:
        if name not in self._by_name:
            raise KeyError(f'Increment "{name}" not found')
        return self._by_name[name]

    def find_by_name(self, name: str) -> Optional[Increment]:
        return self._by_name.get(name)

    def find_by_priority(self, priority: int) -> Optional[Increment]:
        return self._by_priority.get(priority)

    @property
    def sorted_by_priority(self) -> List[Increment]:
        return sorted(self._increments, key=lambda inc: inc.priority)

    def format_for_cli(self) -> str:
        if not self._increments:
            return "No increments defined in story graph"
        return "\n".join(inc.format_for_cli() for inc in self._increments)

    def add(self, name: str, after: Optional[str] = None) -> None:
        if name in self._by_name:
            raise ValueError(f'Increment "{name}" already exists')
        if after is not None:
            after_inc = self._by_name.get(after)
            if after_inc is None:
                raise ValueError(f'Increment "{after}" not found')
            new_priority = after_inc.priority + 1
            for inc in self._increments:
                if inc.priority >= new_priority:
                    inc.priority += 1
            insert_idx = next(i for i, inc in enumerate(self._increments) if inc.name == after) + 1
            new_inc = Increment(name=name, priority=new_priority, stories=[], _story_map=self._story_map)
            self._increments.insert(insert_idx, new_inc)
        else:
            max_priority = max((inc.priority for inc in self._increments), default=0)
            new_inc = Increment(name=name, priority=max_priority + 1, stories=[], _story_map=self._story_map)
            self._increments.append(new_inc)
        self._rebuild_indexes()

    def reorder(self, name: str, before: Optional[str] = None, after: Optional[str] = None) -> None:
        """Move increment before or after another increment, updating all priorities."""
        if name not in self._by_name:
            raise ValueError(f'Increment "{name}" not found')
        anchor_name = before or after
        if anchor_name and anchor_name not in self._by_name:
            raise ValueError(f'Increment "{anchor_name}" not found')
        # Remove from current position
        inc = self._by_name[name]
        self._increments.remove(inc)
        # Find insertion index
        if anchor_name:
            anchor_idx = next(i for i, x in enumerate(self._increments) if x.name == anchor_name)
            insert_idx = anchor_idx if before else anchor_idx + 1
        else:
            insert_idx = len(self._increments)
        self._increments.insert(insert_idx, inc)
        # Reassign priorities to match list order
        for i, x in enumerate(self._increments):
            x.priority = i + 1
        self._rebuild_indexes()

    def remove(self, name: str) -> bool:
        for i, inc in enumerate(self._increments):
            if inc.name == name:
                self._increments.pop(i)
                self._rebuild_indexes()
                return True
        return False

    def rename(self, from_name: str, to_name: str) -> None:
        if to_name in self._by_name and to_name != from_name:
            raise ValueError(f'Increment "{to_name}" already exists')
        inc = self._by_name.get(from_name)
        if inc is None:
            raise ValueError(f'Increment "{from_name}" not found')
        inc.name = to_name
        self._rebuild_indexes()

    def add_story_to(self, increment_name: str, story_name: str, position: Optional[int] = None) -> None:
        inc = self._by_name.get(increment_name)
        if inc is None:
            raise ValueError(f'Increment "{increment_name}" not found')
        inc.add_story(story_name, position=position)

    def remove_story_from(self, increment_name: str, story_name: str) -> None:
        inc = self._by_name.get(increment_name)
        if inc is None:
            raise ValueError(f'Increment "{increment_name}" not found')
        inc.remove_story(story_name)

    def reorder_story_in(self, increment_name: str, story_name: str, position: int) -> None:
        inc = self._by_name.get(increment_name)
        if inc is None:
            raise ValueError(f'Increment "{increment_name}" not found')
        inc.reorder_story(story_name, position)

    def remove_story_from_all(self, story_name: str) -> None:
        for inc in self._increments:
            inc.stories = [s for s in inc.stories if inc._story_name(s) != story_name]

    def rename_story_references(self, old_name: str, new_name: str) -> None:
        for inc in self._increments:
            inc.rename_story_reference(old_name, new_name)

    @classmethod
    def from_list(cls, increments_data: List[Dict[str, Any]], story_map: Optional['StoryMap'] = None) -> 'IncrementCollection':
        return cls([Increment.from_dict(data) for data in increments_data], story_map=story_map)

    def to_list(self) -> List[Dict[str, Any]]:
        return [inc.to_dict() for inc in self._increments]

class StoryMap:

    def __init__(self, story_graph: Dict[str, Any], bot=None, story_graph_path: Optional[Path] = None):
        self.story_graph = story_graph
        self._bot = bot
        self._story_graph_path: Optional[Path] = Path(story_graph_path) if story_graph_path else None
        self._epics_list: List[Epic] = []
        for epic_data in story_graph.get('epics', []):
            self._epics_list.append(Epic.from_dict(epic_data, bot=bot))
        self._epics = EpicsCollection(self._epics_list)
        self._increments = IncrementCollection.from_list(story_graph.get('increments', []), story_map=self)

    @classmethod
    def from_bot(cls, bot: Any) -> 'StoryMap':
        # Use centralized path resolution when bot_paths is available
        if hasattr(bot, 'bot_paths') and hasattr(bot.bot_paths, 'story_graph_paths'):
            story_graph_path = bot.bot_paths.story_graph_paths.story_graph_path
        elif hasattr(bot, 'bot_paths') and hasattr(bot.bot_paths, 'workspace_directory'):
            # Fallback for bots without story_graph_paths
            from story_graph_ops.story_graph_paths import StoryGraphPaths
            bot_name = bot.bot_paths.bot_directory.name if hasattr(bot.bot_paths, 'bot_directory') else 'story'
            paths = StoryGraphPaths(bot.bot_paths.workspace_directory, bot_name)
            story_graph_path = paths.story_graph_path
        elif isinstance(bot, (str, Path)):
            # Legacy path for when bot is just a directory path
            bot_directory = Path(bot)
            story_graph_path = bot_directory / 'docs' / 'story' / 'story-graph.json'
        else:
            raise TypeError(f'Expected bot with bot_paths.story_graph_paths, bot_paths.workspace_directory, or Path/str, got {type(bot)}')
        
        if not story_graph_path.exists():
            logger = logging.getLogger(__name__)
            logger.debug(
                'Story graph not found at %s; using empty graph (create or build will persist story-graph.json)',
                story_graph_path,
            )
            return cls(EMPTY_STORY_GRAPH_DICT.copy(), bot=bot, story_graph_path=story_graph_path)

        # Load story graph with error handling for control characters
        try:
            with open(story_graph_path, 'r', encoding='utf-8') as f:
                story_graph = json.load(f)
        except ValueError as e:
            if 'control character' in str(e).lower() or 'Invalid' in str(e):
                logger = logging.getLogger(__name__)
                logger.warning(f"[StoryMap] JSON parse error in story graph file, sanitizing: {str(e)}")
                from story_graph_ops._utils_min import sanitize_json_string
                content = story_graph_path.read_text(encoding='utf-8')
                sanitized_content = sanitize_json_string(content)
                story_graph = json.loads(sanitized_content)
            else:
                raise

        return cls(story_graph, bot=bot, story_graph_path=story_graph_path)

    @classmethod
    def from_json_file(cls, path: Union[str, Path], bot=None) -> 'StoryMap':
        """Load from ``story-graph.json`` on disk (standalone; no bot required)."""
        story_graph_path = Path(path)
        if not story_graph_path.is_file():
            return cls(EMPTY_STORY_GRAPH_DICT.copy(), bot=bot, story_graph_path=story_graph_path)
        try:
            with open(story_graph_path, 'r', encoding='utf-8') as f:
                story_graph = json.load(f)
        except ValueError as e:
            if 'control character' in str(e).lower() or 'Invalid' in str(e):
                logger = logging.getLogger(__name__)
                logger.warning(f"[StoryMap] JSON parse error in story graph file, sanitizing: {str(e)}")
                from story_graph_ops._utils_min import sanitize_json_string
                content = story_graph_path.read_text(encoding='utf-8')
                sanitized_content = sanitize_json_string(content)
                story_graph = json.loads(sanitized_content)
            else:
                raise
        return cls(story_graph, bot=bot, story_graph_path=story_graph_path)

    def save(self) -> None:
        """Save the story graph to disk using bot paths or ``story_graph_path`` from ``from_json_file``."""
        self.story_graph['epics'] = [self._epic_to_dict(e) for e in self._epics_list]
        self.story_graph['increments'] = self._increments.to_list()
        story_graph_path: Optional[Path] = None
        if self._story_graph_path is not None:
            story_graph_path = self._story_graph_path
        elif self._bot and hasattr(self._bot, 'bot_paths'):
            story_graph_path = self._bot.bot_paths.story_graph_paths.story_graph_path
        if story_graph_path is None:
            return
        story_graph_path.parent.mkdir(parents=True, exist_ok=True)
        with open(story_graph_path, 'w', encoding='utf-8') as f:
            json.dump(self.story_graph, f, indent=2, ensure_ascii=False)
        if self._bot and hasattr(self._bot, '_story_graph'):
            self._bot._story_graph = None

    @property
    def epics(self) -> EpicsCollection:
        return self._epics

    def comparison_epics(self) -> List["Epic"]:
        """Epic roots used for diagram-vs-json diff (override in diagram-backed maps)."""
        return list(self._epics_list)
    
    def __getitem__(self, epic_name: str) -> Epic:
        """Allow epic access by name: story_map['Epic Name']"""
        return self._epics[epic_name]

    def walk(self, node: StoryNode) -> Iterator[StoryNode]:
        yield node
        for child in node.children:
            yield from self.walk(child)

    @property
    def all_stories(self) -> List['Story']:
        stories = []
        for epic in self._epics_list:
            for node in self.walk(epic):
                if isinstance(node, Story):
                    stories.append(node)
        return stories

    @property
    def all_scenarios(self) -> List['Scenario']:
        scenarios = []
        for epic in self._epics_list:
            for node in self.walk(epic):
                if isinstance(node, Story):
                    scenarios.extend(node.scenarios)
        return scenarios

    @property
    def all_domain_concepts(self) -> List[DomainConcept]:
        concepts = []
        for epic in self._epics_list:
            if epic.domain_concepts:
                concepts.extend(epic.domain_concepts)
        return concepts

    def get_all_nodes(self) -> List[StoryNode]:
        nodes = []
        for epic in self._epics_list:
            for node in self.walk(epic):
                nodes.append(node)
        return nodes

    def get_all_acceptance_criteria(self) -> List[Dict[str, Any]]:
        ac_list = []
        for story in self.all_stories:
            for ac in story.acceptance_criteria:
                ac_entry = ac if isinstance(ac, dict) else {'text': str(ac)}
                ac_list.append(ac_entry)
        return ac_list

    @property
    def increments(self) -> IncrementCollection:
        return self._increments

    def get_increments(self) -> List[Dict[str, Any]]:
        """Return increments as list of dictionaries (legacy compatibility)."""
        return self._increments.to_list()

    def remove_increment(self, increment_name: str) -> bool:
        removed = self._increments.remove(increment_name)
        if removed:
            self.save()
        return removed

    def add_increment(self, name: str, after: Optional[str] = None) -> None:
        self._increments.add(name, after)
        self.save()

    def rename_increment(self, from_name: str, to_name: str) -> None:
        self._increments.rename(from_name, to_name)
        self.save()

    def reorder_increment(self, increment_name: str, before: Optional[str] = None, after: Optional[str] = None) -> None:
        self._increments.reorder(increment_name, before=before, after=after)
        self.save()

    def add_story_to_increment(self, increment_name: str, story_name: str, position: Optional[int] = None) -> None:
        if story_name not in {s.name for s in self.all_stories}:
            raise ValueError(f'Story "{story_name}" not found in graph')
        self._increments.add_story_to(increment_name, story_name, position=position)
        self.save()

    def remove_story_from_increment(self, increment_name: str, story_name: str) -> None:
        self._increments.remove_story_from(increment_name, story_name)
        self.save()

    def reorder_story_in_increment(self, increment_name: str, story_name: str, position: int) -> None:
        self._increments.reorder_story_in(increment_name, story_name, int(position))
        self.save()

    def rename_story_in_hierarchy(self, old_name: str, new_name: str) -> None:
        story = self.find_story_by_name(old_name)
        if not story:
            raise ValueError(f'Story "{old_name}" not found')
        if story._parent:
            for sibling in story._parent.children:
                if sibling is not story and sibling.name == new_name:
                    raise ValueError(f'Story "{new_name}" already exists among siblings')
        story.name = new_name
        self._increments.rename_story_references(old_name, new_name)
        self.story_graph['epics'] = [self._epic_to_dict(e) for e in self._epics_list]
        self.save()

    def remove_story_from_all_increments(self, story_name: str) -> None:
        self._increments.remove_story_from_all(story_name)

    def submit_increment_instructions(self, name: str, behavior: str = None, action: str = None):
        """Submit instructions for each story in the increment. Same flow as hierarchy view per story."""
        if not self._bot:
            raise ValueError('StoryMap has no bot reference')
        inc = self._increments.find_by_name(name)
        if not inc:
            raise ValueError(f'Increment "{name}" not found')
        story_names = [inc._story_name(s) for s in inc.stories]
        if not story_names:
            return {'status': 'skipped', 'message': f'Increment "{name}" has no stories'}
        scope_file = self._bot.workspace_directory / 'scope.json'
        with open(scope_file, 'r') as f:
            scope_before = json.load(f)
        results = []
        try:
            for story_name in story_names:
                self._bot.scope(f'story "{story_name}"')
                try:
                    if behavior and action:
                        result = self._bot.submit_action(behavior, action)
                    else:
                        result = self._bot.submit_current()
                    results.append({'story': story_name, 'result': result})
                except Exception as e:
                    results.append({'story': story_name, 'error': str(e)})
        finally:
            with open(scope_file, 'w') as f:
                json.dump(scope_before, f)
            self._bot._scope.load()
        last = results[-1] if results else None
        return last.get('result', last) if last and 'result' in last else {'status': 'ok', 'submitted': len(results), 'results': results}

    def copy_increment_stories_json(self, name: str, include_level: Optional[str] = None) -> dict:
        """Return each story in the increment as story-graph JSON (same as copy_json per story). Respects scope.include_level."""
        if not self._bot:
            raise ValueError('StoryMap has no bot reference')
        inc = self._increments.find_by_name(name)
        if not inc:
            raise ValueError(f'Increment "{name}" not found')
        story_names = [inc._story_name(s) for s in inc.stories]
        if not story_names:
            return {'status': 'success', 'result': []}
        if include_level is None and hasattr(self._bot, '_scope') and self._bot._scope:
            include_level = getattr(self._bot._scope, 'include_level', 'examples') or 'examples'
        if include_level is None:
            include_level = 'examples'
        generate_trace = include_level in ('tests', 'code')
        result = []
        for story_name in story_names:
            story = self.find_story_by_name(story_name)
            if story:
                node_dict = self.node_to_dict(story, include_level=include_level, generate_trace=generate_trace)
                result.append(node_dict)
        return {'status': 'success', 'result': result}

    def apply_update_report(
        self, report: 'UpdateReport', *, apply_ac_patches: bool = False
    ) -> None:
        """Apply an update report to this story map.
        
        This is a thin wrapper around StoryMapUpdater for backward compatibility.
        New code should use generate_update_report() or merge() instead.
        
        Args:
            report: The UpdateReport to apply
            apply_ac_patches: If True, apply ``ac_moves`` / ``ac_changes`` from the
                report (legacy). Exploration sync leaves this False and applies
                AC from the diagram elsewhere.
        """
        from story_graph_ops.story_map_updater import StoryMapUpdater
        updater = StoryMapUpdater(target_map=self)
        updater.update_from_report(report=report, apply_ac_patches=apply_ac_patches)
    
    def generate_update_report(self, other_map: 'StoryMap') -> 'UpdateReport':
        """Generate an update report by comparing this map against another.
        
        Convenience wrapper that creates StoryMapUpdater internally.
        
        Args:
            other_map: The source map to compare against this (target) map
            
        Returns:
            UpdateReport containing the differences
        """
        from story_graph_ops.story_map_updater import StoryMapUpdater
        updater = StoryMapUpdater(target_map=self)
        return updater.generate_report_from(source_map=other_map)
    
    def merge(self, other_map: 'StoryMap', report: Optional['UpdateReport'] = None) -> None:
        """Merge changes from another map into this map.
        
        Convenience wrapper. If no report provided, generates one first.
        
        Args:
            other_map: The source map to merge from
            report: Optional pre-generated UpdateReport. If None, generates one.
        """
        from story_graph_ops.story_map_updater import StoryMapUpdater
        updater = StoryMapUpdater(target_map=self)
        
        if report is None:
            report = updater.generate_report_from(source_map=other_map)
        
        updater.update_from_report(report=report, apply_ac_patches=False)

    def filter_by_name(self, name: str) -> Optional['StoryMap']:
        """Return a new StoryMap containing only the subtree rooted at
        the node with the given name.  The returned StoryMap preserves
        the epic/sub-epic hierarchy leading to the matched node.

        Returns None if no node with that name is found.
        """
        node = self.find_node(name)
        if not node:
            return None

        if isinstance(node, Epic):
            return StoryMap({'epics': [self._epic_to_dict(node)]})

        # Walk up to find the containing epic and build a filtered graph
        # that includes only the path to this node.
        for epic in self._epics_list:
            for child in self.walk(epic):
                if child.name == name:
                    # Found it -- rebuild the epic with only this subtree
                    if isinstance(node, SubEpic):
                        filtered_epic = dict(self._epic_to_dict(epic))
                        filtered_epic['sub_epics'] = [
                            self._sub_epic_to_dict(node)]
                        filtered_epic['story_groups'] = []
                        return StoryMap({'epics': [filtered_epic]})
                    elif isinstance(node, Story):
                        # Find the parent sub-epic
                        for se_child in epic.children:
                            if isinstance(se_child, SubEpic):
                                for s in se_child.all_stories:
                                    if s.name == name:
                                        filtered_se = dict(
                                            self._sub_epic_to_dict(se_child))
                                        filtered_epic = dict(
                                            self._epic_to_dict(epic))
                                        filtered_epic['sub_epics'] = [
                                            filtered_se]
                                        filtered_epic['story_groups'] = []
                                        return StoryMap(
                                            {'epics': [filtered_epic]})
        return None

    def filter_by_epic_names(self, epic_names: set) -> 'StoryMap':
        filtered_epics = [e for e in self._epics_list if e.name in epic_names]
        filtered_graph = {'epics': [self._epic_to_dict(e) for e in filtered_epics]}
        return StoryMap(filtered_graph)

    def filter_by_story_names(self, story_names: set) -> List['Story']:
        stories = []
        for epic in self._epics_list:
            for node in self.walk(epic):
                if isinstance(node, Story) and node.name in story_names:
                    stories.append(node)
        return stories

    def find_node(self, node_name: str) -> Optional[StoryNode]:
        for epic in self._epics_list:
            if epic.name == node_name:
                return epic
            for child in epic.children:
                if child.name == node_name:
                    return child
                if hasattr(child, 'children'):
                    result = self._find_in_children(child, node_name)
                    if result:
                        return result
        return None
    
    def _find_in_children(self, node: StoryNode, name: str) -> Optional[StoryNode]:
        for child in node.children:
            if child.name == name:
                return child
            if hasattr(child, 'children'):
                result = self._find_in_children(child, name)
                if result:
                    return result
        return None
    
    def find_epic_by_name(self, epic_name: str) -> Optional[Epic]:
        for epic in self._epics_list:
            if epic.name == epic_name:
                return epic
        return None

    def find_story_by_name(self, story_name: str) -> Optional['Story']:
        for epic in self._epics_list:
            for node in self.walk(epic):
                if isinstance(node, Story) and node.name == story_name:
                    return node
        return None
    
    def create_epic(self, name: Optional[str] = None, position: Optional[int] = None) -> Epic:
        """Create a new Epic at the root level of the story map.
        
        Args:
            name: Name for the new Epic. If None, generates unique name (Epic1, Epic2, etc.)
            position: Position to insert the Epic. If None, adds to end. If exceeds count, adjusts to last position.
            
        Returns:
            The newly created Epic instance
            
        Raises:
            ValueError: If an Epic with the same name already exists or name is empty
        """
        # Validate name is not empty
        if name is not None and not name.strip():
            raise ValueError("Epic name cannot be empty")
        
        # Validate name uniqueness
        if name:
            for epic in self._epics_list:
                if epic.name == name:
                    raise ValueError(f"Epic with name '{name}' already exists")
        
        # Generate unique name if not provided
        if not name:
            name = self._generate_unique_epic_name()
        
        # Create Epic instance
        epic = Epic(name=name, domain_concepts=[], _bot=self._bot)
        
        # Add to epics list at specified position
        if position is not None:
            adjusted_position = min(position, len(self._epics_list))
            self._epics_list.insert(adjusted_position, epic)
        else:
            self._epics_list.append(epic)
        
        # Set sequential_order based on position in list
        for idx, e in enumerate(self._epics_list):
            e.sequential_order = idx
        
        # Rebuild epics collection with new epic
        self._epics = EpicsCollection(self._epics_list)
        
        # Save to disk (save() will regenerate dict)
        self.save()
        
        return epic
    
    def delete_epic(self, name: str) -> Dict[str, Any]:
        """Delete an epic from the story map. Always cascades to delete all children.
        
        Args:
            name: Name of the epic to delete
            
        Returns:
            Dict with operation details
            
        Raises:
            ValueError: If epic not found
        """
        # Find the epic
        epic_to_delete = None
        for epic in self._epics_list:
            if epic.name == name:
                epic_to_delete = epic
                break
        
        if not epic_to_delete:
            raise ValueError(f"Epic '{name}' not found")
        
        children_count = len(epic_to_delete._children)
        
        # Remove from list (cascade delete of all children)
        self._epics_list.remove(epic_to_delete)
        
        # Update sequential order
        for idx, e in enumerate(self._epics_list):
            e.sequential_order = idx
        
        # Rebuild epics collection
        self._epics = EpicsCollection(self._epics_list)
        
        # Save to disk (save() will regenerate dict)
        self.save()
        
        return {
            'node_type': 'Epic',
            'node_name': name,
            'operation': 'delete',
            'children_deleted': children_count
        }
    
    def _generate_unique_epic_name(self) -> str:
        """Generate a unique Epic name (Epic1, Epic2, etc.)"""
        counter = 1
        while True:
            name = f'Epic{counter}'
            if not any(epic.name == name for epic in self._epics_list):
                return name
            counter += 1

    def _epic_to_dict(self, epic: Epic, include_level: Optional[str] = None, generate_trace: bool = False) -> Dict[str, Any]:
        result = {
            'name': epic.name,
            'sequential_order': epic.sequential_order,
            'behavior': epic.behavior,
            'domain_concepts': _domain_concepts_to_dict_list(epic.domain_concepts) if _level_includes(_LEVEL_DOMAIN, include_level) else [],
            'sub_epics': [self._sub_epic_to_dict(child, include_level, generate_trace) for child in epic._children if isinstance(child, SubEpic)],
            'story_groups': [self._story_group_to_dict(child, include_level, generate_trace) for child in epic._children if isinstance(child, StoryGroup)]
        }
        return result

    def _sub_epic_to_dict(self, sub_epic: SubEpic, include_level: Optional[str] = None, generate_trace: bool = False) -> Dict[str, Any]:
        result = {
            'name': sub_epic.name,
            'sequential_order': sub_epic.sequential_order,
            'behavior': sub_epic.behavior,
            'domain_concepts': _domain_concepts_to_dict_list(sub_epic.domain_concepts) if _level_includes(_LEVEL_DOMAIN, include_level) else [],
        }
        if sub_epic.test_file is not None:
            result['test_file'] = sub_epic.test_file
        nested_subepics = [child for child in sub_epic._children if isinstance(child, SubEpic)]
        result.update({
            'sub_epics': [self._sub_epic_to_dict(child, include_level, generate_trace) for child in nested_subepics],
            'story_groups': [self._story_group_to_dict(child, include_level, generate_trace) for child in sub_epic._children if isinstance(child, StoryGroup)]
        })
        return result

    def _story_group_to_dict(self, story_group: StoryGroup, include_level: Optional[str] = None, generate_trace: bool = False) -> Dict[str, Any]:
        result = {
            'name': story_group.name,
            'sequential_order': story_group.sequential_order,
            'type': story_group.group_type,
            'connector': story_group.connector,
            'behavior': story_group.behavior,
            'stories': [self._story_to_dict(child, include_level, generate_trace) for child in story_group.children if isinstance(child, Story)]
        }
        return result

    def _story_to_dict(self, story: Story, include_level: Optional[str] = None, generate_trace: bool = False) -> Dict[str, Any]:
        scenarios = []
        acceptance_criteria = []
        for child in story._children:
            if isinstance(child, Scenario):
                scenarios.append(self._scenario_to_dict(child, story, include_level, generate_trace))
            elif isinstance(child, AcceptanceCriteria):
                acceptance_criteria.append(self._acceptance_criteria_to_dict(child))
        result = {
            'name': story.name,
            'sequential_order': story.sequential_order,
            'connector': story.connector,
            'story_type': story.story_type,
            'users': [str(u) for u in story.users] if story.users else [],
            'test_class': story.test_class,
            'scenarios': scenarios if _level_includes(_LEVEL_SCENARIOS, include_level) else [],
            'acceptance_criteria': acceptance_criteria if _level_includes(_LEVEL_ACCEPTANCE, include_level) else [],
            'behavior': story.behavior
        }
        if story.file_link is not None:
            result['file_link'] = story.file_link
        return result
    
    def _scenario_to_dict(self, scenario: Scenario, story: Optional['Story'] = None, include_level: Optional[str] = None, generate_trace: bool = False) -> Dict[str, Any]:
        def _step_text(step) -> str:
            t = getattr(step, 'text', '')
            if isinstance(t, str):
                return t
            if isinstance(t, dict):
                return str(t.get('text', ''))
            return str(t) if t is not None else ''

        steps_text = '\n'.join(_step_text(step) for step in scenario.steps) if scenario.steps else ''
        result = {
            'name': scenario.name,
            'sequential_order': scenario.sequential_order,
            'type': scenario.type,
            'background': scenario.background if _level_includes(_LEVEL_SCENARIOS, include_level) else [],
            'test_method': scenario.test_method,
            'steps': steps_text if _level_includes(_LEVEL_SCENARIOS, include_level) else ''
        }
        if _level_includes(_LEVEL_EXAMPLES, include_level) and scenario.examples:
            result['examples'] = scenario.examples
        if _level_includes(_LEVEL_TESTS, include_level) and story:
            test_code_data = self._generate_test_code_for_scenario(scenario, story)
            if test_code_data:
                result['test'] = test_code_data
        if _level_includes(_LEVEL_TESTS, include_level) and story and generate_trace and scenario.test_method and story.test_class:
            trace_data = self._generate_trace_for_scenario(scenario, story)
            if trace_data:
                result['trace'] = trace_data
        return result

    def _generate_test_code_for_scenario(self, scenario: 'Scenario', story: 'Story') -> Optional[Dict[str, Any]]:
        """Extract test method info for scenario (method, file, line)."""
        if not hasattr(scenario, 'test_method') or not scenario.test_method:
            return None
        test_file = self._get_story_test_file(story)
        if not test_file or not hasattr(story, 'test_class') or not story.test_class:
            return None
        try:
            workspace = getattr(self._bot, 'bot_paths', None) and getattr(self._bot.bot_paths, 'workspace_directory', None)
            if not workspace:
                workspace = Path.cwd()
            test_dir = workspace / getattr(getattr(self._bot, 'bot_paths', None), 'test_path', Path('test'))
            test_file_path = test_dir / test_file
            if not test_file_path.exists():
                return None
            from traceability.trace_generator import TraceGenerator
            source = test_file_path.read_text(encoding='utf-8')
            lines = source.split('\n')
            generator = TraceGenerator(workspace, max_depth=3)
            code, start, _ = generator._extract_method_from_class(source, lines, story.test_class, scenario.test_method)
            if code:
                return {'method': scenario.test_method, 'file': str(test_file), 'line': start}
        except Exception:
            pass
        return None

    def _generate_trace_for_scenario(self, scenario: 'Scenario', story: 'Story') -> List[Dict[str, Any]]:
        """Generate trace for scenario (symbol, file, line, children through code)."""
        test_file = self._get_story_test_file(story)
        if not test_file:
            return []
        try:
            from traceability.trace_generator import TraceGenerator
            workspace = getattr(self._bot, 'bot_paths', None) and getattr(self._bot.bot_paths, 'workspace_directory', None)
            if not workspace:
                workspace = Path.cwd()
            test_dir = workspace / getattr(getattr(self._bot, 'bot_paths', None), 'test_path', Path('test'))
            test_file_path = test_dir / test_file
            if not test_file_path.exists():
                return []
            source = test_file_path.read_text(encoding='utf-8')
            lines = source.split('\n')
            generator = TraceGenerator(workspace, max_depth=3)
            generator._build_method_index()
            test_code, _, _ = generator._extract_method_from_class(source, lines, story.test_class, scenario.test_method)
            source_file = str(test_file_path.relative_to(workspace)).replace("\\", "/") if test_code else None
            if not test_code and test_file_path.suffix == '.py':
                js_path = test_file_path.with_suffix('.js')
                if js_path.exists():
                    js_source = js_path.read_text(encoding='utf-8')
                    js_lines = js_source.split('\n')
                    test_code, _, _ = generator._extract_method_from_js(
                        js_source, js_lines, story.test_class, scenario.test_method
                    )
                    if test_code:
                        source_file = str(js_path.relative_to(workspace)).replace("\\", "/")
            if not test_code:
                return []
            calls = generator._find_calls_in_code(test_code, source_file)
            trace_sections = []
            for call in calls:
                sections = generator._resolve_call(call, depth=1, shallow=False)
                if sections:
                    trace_sections.extend(sections)
            # Also trace from JS test file when it exists (adds panel/JS impl)
            if test_file_path.suffix == '.py':
                js_path = test_file_path.with_suffix('.js')
                if js_path.exists() and story.test_class:
                    js_traces = generator._trace_from_js_test_file(js_path, story.test_class, workspace)
                    if js_traces:
                        trace_sections.extend(js_traces)
            return trace_sections
        except Exception:
            return []

    def _get_story_test_file(self, story: 'Story') -> Optional[str]:
        """Get test_file from parent SubEpic."""
        parent = getattr(story, '_parent', None)
        while parent:
            if hasattr(parent, 'test_file') and parent.test_file:
                return parent.test_file
            parent = getattr(parent, '_parent', None)
        return None

    def _acceptance_criteria_to_dict(self, ac: AcceptanceCriteria) -> Dict[str, Any]:
        return {
            'name': ac.name,
            'text': ac.text,
            'sequential_order': ac.sequential_order
        }

    def node_to_dict(self, node: StoryNode, include_level: Optional[str] = None, generate_trace: bool = False) -> Dict[str, Any]:
        """Serialize any story node to its story-graph JSON shape (for copy_json). Uses include_level like submit."""
        if isinstance(node, Epic):
            return self._epic_to_dict(node, include_level, generate_trace)
        if isinstance(node, SubEpic):
            return self._sub_epic_to_dict(node, include_level, generate_trace)
        if isinstance(node, StoryGroup):
            return self._story_group_to_dict(node, include_level, generate_trace)
        if isinstance(node, Story):
            return self._story_to_dict(node, include_level, generate_trace)
        if isinstance(node, Scenario):
            story = getattr(node, '_parent', None) if isinstance(node, Scenario) else None
            return self._scenario_to_dict(node, story, include_level, generate_trace)
        if isinstance(node, AcceptanceCriteria):
            return self._acceptance_criteria_to_dict(node)
        raise ValueError(f'Unknown node type: {type(node).__name__}')
    
    
    def _calculate_story_file_link(self, story: Story) -> str:
        """Calculate the file path for a story's markdown file."""
        if not self._bot or not hasattr(self._bot, 'bot_paths'):
            return ''
        
        # Build path: docs/story/scenarios/Epic/SubEpic/.../Story.md
        path_parts = []
        current = story
        
        # Walk up to collect all parent names
        while hasattr(current, '_parent') and current._parent:
            current = current._parent
            if isinstance(current, (Epic, SubEpic)):
                path_parts.insert(0, current.name)
        
        # Add story name
        path_parts.append(f"📄 {story.name}.md")
        
        # Build full path using centralized path resolution
        docs_path = self._bot.bot_paths.story_graph_paths.scenarios_path
        story_path = docs_path
        for part in path_parts:
            story_path = story_path / part
        
        return str(story_path)