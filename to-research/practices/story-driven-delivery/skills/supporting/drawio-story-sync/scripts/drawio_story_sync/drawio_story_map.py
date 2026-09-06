"""
DrawIOStoryMap - Domain model for rendering story maps to DrawIO.

Orchestrates rendering by delegating to domain nodes. Each node
(DrawIOEpic, DrawIOSubEpic, DrawIOStory, DrawIOIncrementLane) owns
its own rendering logic.  This class only coordinates creation order
and collects nodes for serialization.
"""
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple
from story_graph_ops.nodes import StoryMap, Epic, SubEpic, Story, StoryGroup
from .drawio_element import DrawIOElement, STYLE_DEFAULTS
from .drawio_story_node import (
    DrawIOStoryNode, DrawIOEpic, DrawIOSubEpic, DrawIOStory,
    DrawIOIncrementLane, SPACING, CONTAINER_PADDING, CELL_SIZE,
    _max_sub_epic_depth, _RowPositions, CELL_SPACING, ROW_GAP,
    _compare_node_lists, _collect_all_names,
)
from .drawio_story_node_serializer import DrawIOStoryNodeSerializer
from .layout_data import LayoutData
from .update_report import UpdateReport
from .render_summary import RenderSummary
from .ac_text_format import plain_ac_from_cell_value


_OUTLINE_PERSONA_FILL = STYLE_DEFAULTS['actor']['fill']


def _forward_fill_story_users(explicit: List[Optional[str]]) -> List[List[str]]:
    """Carry the last explicit persona left-to-right along a story row (outline).

    ``explicit[i]`` is the label on a chip centered above story *i*, or ``None``.
    Each story gets ``[]`` until the first explicit, then ``[last_label]`` until
    the next explicit replaces ``last_label``.
    """
    last: Optional[str] = None
    out: List[List[str]] = []
    for e in explicit:
        if e:
            last = e.strip()
        if last:
            out.append([last])
        else:
            out.append([])
    return out


def _outline_persona_nodes(nodes: List[Any]) -> List[Any]:
    """mxCells that use the same actor styling as ``DrawIOStoryNodeSerializer`` / renderer."""
    chips: List[Any] = []
    for n in nodes:
        if not isinstance(n, DrawIOElement):
            continue
        if getattr(n, 'fill', None) != _OUTLINE_PERSONA_FILL:
            continue
        cid = getattr(n, 'cell_id', '') or ''
        if '/ac-' in cid or cid.startswith('inc-lane'):
            continue
        label = (getattr(n, 'value', '') or '').strip()
        if not label:
            continue
        chips.append(n)
    return chips


def _apply_outline_row_personas(ordered_stories: List[Any], persona_nodes: List[Any]) -> None:
    """Set ``users`` and ``_had_actor_cells`` on each story in one leaf row."""
    explicit = [_explicit_persona_label_above_story(s, persona_nodes) for s in ordered_stories]
    filled = _forward_fill_story_users(explicit)
    row_has = any(e for e in explicit if e)
    for s, ulist in zip(ordered_stories, filled):
        s.users = ulist
        setattr(s, '_had_actor_cells', row_has)


def _explicit_persona_label_above_story(story: Any, persona_nodes: List[Any]) -> Optional[str]:
    """Persona chip whose center lies in this story's column and above the story."""
    sp = getattr(story, 'position', None)
    sb = getattr(story, 'boundary', None)
    if sp is None or sb is None:
        return None
    sx, sy = sp.x, sp.y
    sw, sh = sb.width, sb.height
    if sw <= 0 or sh <= 0:
        return None
    best_label: Optional[str] = None
    best_key: Optional[tuple] = None
    for n in persona_nodes:
        pos = getattr(n, 'position', None)
        b = getattr(n, 'boundary', None)
        if pos is None or b is None:
            continue
        ax = pos.x + b.width / 2.0
        ay = pos.y + b.height / 2.0
        if ax < sx or ax > sx + sw:
            continue
        if ay >= sy:
            continue
        lab = (getattr(n, 'value', '') or '').strip()
        if not lab:
            continue
        key = (sy - ay, abs(ax - (sx + sw / 2.0)))
        if best_key is None or key < best_key:
            best_key = key
            best_label = lab
    return best_label


_ACTOR_FILL = '#dae8fc'


def _outline_persona_mxcells(nodes: List[Any]) -> List[Any]:
    """mxCells that represent persona chips for outline ``users`` extraction.

    Includes path-based ids (``…/actor-…``) and **orphan** chips: DrawIO sometimes
    assigns numeric ids after duplicate/paste, but keeps the actor palette fill.
    """
    out: List[Any] = []
    for n in nodes:
        cid = getattr(n, 'cell_id', '') or ''
        label = (getattr(n, 'value', '') or '').strip()
        if not label:
            continue
        if '/actor-' in cid:
            out.append(n)
            continue
        if isinstance(n, DrawIOElement) and getattr(n, 'fill', None) == _ACTOR_FILL:
            if '/ac-' in cid or cid.startswith('inc-lane/'):
                continue
            out.append(n)
    return out


def _ordered_unique_labels(pairs: List[tuple]) -> List[str]:
    """Sort by x then drop duplicate labels (path + orphan duplicate same column)."""
    pairs = sorted(pairs, key=lambda t: t[0])
    seen: set = set()
    labels: List[str] = []
    for _x, lab in pairs:
        if lab in seen:
            continue
        seen.add(lab)
        labels.append(lab)
    return labels


class DrawIOStoryMap(StoryMap):

    def __init__(self, diagram_type: str = 'outline', story_graph: Dict[str, Any] = None):
        super().__init__(story_graph or {'epics': []})
        self._diagram_type = diagram_type
        self._drawio_epics: List[DrawIOEpic] = []
        self._increment_lanes: List[DrawIOIncrementLane] = []
        self._loaded_nodes: List = []       # all parsed nodes from file (for extraction)
        self._all_stories: List[DrawIOStory] = []  # all parsed stories (including orphans from lanes)
        self._layout_data: Optional[LayoutData] = None
        self._has_rendered_ac = False       # track if AC was rendered
        self._has_rendered_increments = False  # track if increments were rendered

    @property
    def diagram_type(self) -> str:
        return self._diagram_type

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_epics(self) -> List[DrawIOEpic]:
        return list(self._drawio_epics)

    def get_sub_epics(self) -> List[DrawIOSubEpic]:
        result = []
        for epic in self._drawio_epics:
            result.extend(epic.get_sub_epics())
        return result

    def get_stories(self) -> List[DrawIOStory]:
        result = []
        for epic in self._drawio_epics:
            result.extend(epic.get_stories())
        return result

    def get_total_width(self) -> float:
        """Rightmost edge of the rendered outline content."""
        if not self._drawio_epics:
            return 0
        return max(e.boundary.right for e in self._drawio_epics)

    def get_bottom_y(self) -> float:
        """Lowest Y coordinate of any outline element (sub-epics or stories).

        Recursively checks nested sub-epics so that deeply nested elements
        (e.g. second-level sub-epics) are accounted for.
        """
        bottom = 0
        for story in self.get_stories():
            b = story.position.y + story.boundary.height
            if b > bottom:
                bottom = b
        for se in self._all_sub_epics_recursive():
            b = se.position.y + se.boundary.height
            if b > bottom:
                bottom = b
        return bottom

    def _all_sub_epics_recursive(self) -> List[DrawIOSubEpic]:
        """Return all sub-epics at every nesting level."""
        result = []
        stack = list(self.get_sub_epics())
        while stack:
            se = stack.pop()
            result.append(se)
            stack.extend(se.get_sub_epics())
        return result

    # ------------------------------------------------------------------
    # Render – Outline
    # ------------------------------------------------------------------

    def render_from_story_map(self, story_map: StoryMap,
                               layout_data: Optional[LayoutData] = None,
                               skip_stories: bool = False,
                               story_widths: Dict[str, float] = None) -> Union[Dict[str, Any], RenderSummary]:
        """Render outline diagram.  Each node renders itself.

        Computes global row positions first so all epics share the
        same Y levels, then lays out epics left-to-right.

        When *skip_stories* is True the outline renders epics and
        sub-epics but omits story cells (used by the increments view
        where stories appear only in increment lanes).
        
        Returns:
            RenderSummary with render statistics (also supports dict via to_dict())
        """
        self._layout_data = layout_data
        self._drawio_epics = []
        self._increment_lanes = []

        epics = list(story_map.epics)
        if not epics:
            return RenderSummary(epics=0, sub_epic_count=0, diagram_generated=True)

        # Global max depth → consistent rows across all epics
        max_depth = max(_max_sub_epic_depth(epic) for epic in epics)
        rows = _RowPositions(max_depth)

        # AC boxes are rendered only for acceptance_criteria diagram type
        render_ac = (self._diagram_type == 'acceptance_criteria')

        x_pos = DrawIOEpic.X_START
        for epic in epics:
            drawio_epic = DrawIOStoryNodeSerializer.create_epic(
                epic.name, getattr(epic, 'sequential_order', 0) or 0)
            drawio_epic.render_from_domain(epic, x_pos, rows, layout_data,
                                           skip_stories=skip_stories,
                                           story_widths=story_widths,
                                           render_ac=render_ac)
            self._drawio_epics.append(drawio_epic)
            x_pos = drawio_epic.boundary.right + CELL_SPACING

        return RenderSummary(
            epics=len(self._drawio_epics),
            sub_epic_count=len(self.get_sub_epics()),
            story_count=len(self.get_stories()),
            diagram_generated=True
        )

    # ------------------------------------------------------------------
    # Render – Increments  (outline + increment lanes below)
    # ------------------------------------------------------------------

    def render_increments_from_story_map(
            self, story_map: StoryMap,
            increments_data: list,
            layout_data: Optional[LayoutData] = None) -> Union[Dict[str, Any], RenderSummary]:
        """Render outline with orphaned stories, then increment lanes.
        
        Sets _has_rendered_increments flag for extraction logic.

        Stories assigned to an increment appear ONLY in their lane.
        Stories NOT assigned to any increment ("orphaned") appear
        under their sub-epic just like a normal outline, providing
        context for the column structure.

        Increment lanes are positioned below the orphaned story area
        so there is room for potentially multiple rows of unassigned
        stories.
        
        Returns:
            RenderSummary with render statistics including increment count
        """
        self._has_rendered_increments = True
        # Collect all story names that belong to at least one increment
        increment_story_names: set = set()
        for inc_data in increments_data:
            for s in inc_data.get('stories', []):
                increment_story_names.add(
                    s.get('name', '') if isinstance(s, dict) else str(s))

        # Phase 1: render full outline (epics, sub-epics, ALL stories)
        # so that orphaned stories appear under their sub-epics and we
        # get correct positions for every story.
        summary = self.render_from_story_map(story_map, layout_data,
                                             skip_stories=False)
        all_drawio_stories = self.get_stories()

        # Phase 2: remove increment-assigned stories from the outline
        # tree (they will live only in their lanes).  Orphaned stories
        # stay in the tree.
        for epic in self._drawio_epics:
            for se in epic.get_sub_epics():
                self._remove_increment_stories(se, increment_story_names)

        # Collect domain stories for user/actor info
        domain_stories = list(story_map.all_stories)

        # Phase 3: compute where increment lanes start.
        # Use the full story set's bottom (before removal) so column
        # widths are correct; then derive Y from the actual remaining
        # outline bottom which includes orphaned stories.
        outline_bottom = self.get_bottom_y()
        total_width = max(
            self.get_total_width(),
            max((s.position.x + CELL_SIZE for s in all_drawio_stories),
                default=0))

        # Reserve space below the outline for at least one row of orphan
        # stories (CELL_SIZE) plus padding.  This ensures lanes never overlap
        # with the deepest sub-epics or orphan story rows.
        y_start = outline_bottom + CELL_SIZE + ROW_GAP

        for idx, inc_data in enumerate(increments_data):
            story_names = []
            for s in inc_data.get('stories', []):
                story_names.append(s.get('name', '') if isinstance(s, dict) else str(s))

            lane = DrawIOIncrementLane(
                name=inc_data.get('name', f'Increment {idx + 1}'),
                priority=inc_data.get('priority', idx + 1),
                story_names=story_names)
            lane.render(idx, y_start, total_width, all_drawio_stories,
                        domain_stories=domain_stories)
            self._increment_lanes.append(lane)

        # Return RenderSummary with increment count
        if isinstance(summary, RenderSummary):
            summary.increments = len(increments_data)
            return summary
        else:
            # Backward compatibility: summary is a dict
            summary['increments'] = len(increments_data)
            return summary

    @staticmethod
    def _remove_increment_stories(sub_epic: DrawIOSubEpic,
                                   increment_names: set):
        """Remove stories that belong to increments from a sub-epic tree.

        Recurses into nested sub-epics.  Only leaf sub-epics have stories.
        """
        for nested in sub_epic.get_sub_epics():
            DrawIOStoryMap._remove_increment_stories(nested, increment_names)
        to_remove = [s for s in sub_epic.get_stories()
                     if s.name in increment_names]
        for s in to_remove:
            sub_epic._children.remove(s)

    # ------------------------------------------------------------------
    # Render – Exploration / Acceptance Criteria
    # ------------------------------------------------------------------

    def render_exploration_from_story_map(
            self, story_map: StoryMap,
            layout_data: Optional[LayoutData] = None) -> Union[Dict[str, Any], RenderSummary]:
        """Render outline with AC-aware spacing, then add AC boxes.

        Stories are spaced apart based on their widest acceptance
        criteria box so that AC text does not overlap between stories.
        
        Returns:
            RenderSummary with render statistics including AC count
        """
        self._has_rendered_ac = True
        domain_stories = self._collect_domain_stories(story_map)

        # Pre-compute the horizontal space each story needs (widest AC box)
        story_widths: Dict[str, float] = {}
        for name, ds in domain_stories.items():
            story_widths[name] = DrawIOStory.compute_ac_width(ds)

        summary = self.render_from_story_map(
            story_map, layout_data, story_widths=story_widths)

        ac_count = 0
        for drawio_story in self.get_stories():
            domain_story = domain_stories.get(drawio_story.name)
            if domain_story and domain_story.has_acceptance_criteria():
                drawio_story.render_ac_boxes(domain_story)
                ac_count += len(domain_story.acceptance_criteria)

        # Add AC count to summary
        if isinstance(summary, RenderSummary):
            summary.ac_count = ac_count
            summary.exploration = True
            return summary
        else:
            # Backward compatibility: summary is a dict
            summary['ac_count'] = ac_count
            summary['exploration'] = True
            return summary

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, file_path: Path):
        all_nodes = self._collect_all_nodes()
        xml_content = DrawIOStoryNodeSerializer.to_drawio_xml(all_nodes)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(xml_content, encoding='utf-8')

    def save_layout(self, layout_path: Path):
        layout = self.extract_layout()
        layout.save(layout_path)

    def save_as_json(self, file_path: Path):
        data = self._to_story_graph_dict()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def extract_layout(self) -> LayoutData:
        layout = LayoutData()
        for epic in self._drawio_epics:
            layout.set_entry(f'EPIC|{epic.name}',
                             epic.position.x, epic.position.y,
                             epic.boundary.width, epic.boundary.height)
            layout.set_entry(epic.cell_id,
                             epic.position.x, epic.position.y,
                             epic.boundary.width, epic.boundary.height)
            for se in epic.get_sub_epics():
                self._extract_layout_for_sub_epic(layout, epic.name, se)
        return layout

    def _extract_layout_for_sub_epic(self, layout: LayoutData, epic_name: str,
                                      se: DrawIOSubEpic):
        layout.set_entry(f'SUB_EPIC|{se.name}',
                         se.position.x, se.position.y,
                         se.boundary.width, se.boundary.height)
        layout.set_entry(se.cell_id,
                         se.position.x, se.position.y,
                         se.boundary.width, se.boundary.height)
        for nested_se in se.get_sub_epics():
            self._extract_layout_for_sub_epic(layout, epic_name, nested_se)
        for story in se.get_stories():
            layout.set_entry(
                f'STORY|{epic_name}|{se.name}|{story.name}',
                story.position.x, story.position.y,
                story.boundary.width, story.boundary.height)
            layout.set_entry(story.cell_id,
                             story.position.x, story.position.y,
                             story.boundary.width, story.boundary.height)

    # ------------------------------------------------------------------
    # Update report
    # ------------------------------------------------------------------

    def generate_update_report(self, original_story_map: StoryMap) -> UpdateReport:
        report = UpdateReport()

        # Extract increment assignments BEFORE Pass 1 so we can use them in rename detection.
        # This ensures stories in different increments aren't mistakenly treated as renames.
        extracted_increments = self.extract_increment_assignments() if self._has_rendered_increments or self._diagram_type == 'increments' else []
        original_increments = original_story_map.story_graph.get('increments', [])
        
        # Build story→increment mappings for both extracted and original
        extracted_story_to_inc = self._build_story_to_increment_map(extracted_increments)
        original_story_to_inc = self._build_story_to_increment_map(original_increments)

        # Pass 1: hierarchy comparison (horizontal position).
        extracted_epics = sorted(self._drawio_epics, key=lambda e: e.sequential_order or 0)
        original_epics = sorted(list(original_story_map.epics), key=lambda e: getattr(e, 'sequential_order', 0) or 0)

        # Collect all names from both trees so rename detection can
        # distinguish genuine renames from moves.
        all_extracted_names = _collect_all_names(extracted_epics)
        all_original_names = _collect_all_names(original_epics)

        _compare_node_lists(extracted_epics, original_epics, report,
                            parent_name='', recurse=True,
                            all_extracted_names=all_extracted_names,
                            all_original_names=all_original_names,
                            extracted_story_to_inc=extracted_story_to_inc,
                            original_story_to_inc=original_story_to_inc)

        # Flag large deletions: when entire epics or sub-epics are missing
        # from the diagram, flag them so the consumer can decide how to
        # handle bulk removals (e.g. confirmation prompt).
        for ep in report.removed_epics:
            report.add_missing_epic(ep.name)
        for se in report.removed_sub_epics:
            report.add_missing_sub_epic(se.name)

        # Reconcile moves: stories that appear in both new and removed
        # (or are descendants of removed sub-epics) are reclassified as
        # moved_stories so updateFromDiagram preserves their data.
        # Also pass extracted increment data so stories in lanes aren't reported as removed.
        # Reuse the extracted_increments we already computed above.
        report.reconcile_moves(original_story_map, extracted_increments=extracted_increments)

        # Pass 2: increment assignments (vertical position).
        # Only compute delta if we actually have increment data and either:
        # - This was rendered as increments, OR
        # - The extracted data has lanes (file was loaded with lanes)
        # Reuse the extracted_increments we already computed above.
        if extracted_increments and (self._has_rendered_increments or self._diagram_type == 'increments'):
            self._compute_increment_delta(report, extracted_increments, original_increments)

        # Exploration AC is applied per-story from the diagram after hierarchy
        # apply (see ``diagram_ac_sync.apply_per_story_diagram_ac``); no AC
        # patch list is written into the update report.

        # Pass 3: story users / personas (outline actor cells → graph ``users``).
        self._compute_users_delta(report, original_story_map)
        return report

    def _compute_users_delta(self, report: UpdateReport, original_story_map: StoryMap) -> None:
        """Diff actor-derived ``users`` on extracted stories vs canonical graph."""
        for e_ext in sorted(self._drawio_epics, key=lambda e: e.sequential_order or 0):
            e_orig = self._domain_epic_named(original_story_map, e_ext.name)
            if e_orig is None:
                continue
            self._compute_users_delta_under_parent(e_ext, e_orig, report)

    @staticmethod
    def _domain_epic_named(original_story_map: StoryMap, epic_name: str):
        for e in original_story_map.epics:
            if e.name == epic_name:
                return e
        return None

    def _compute_users_delta_under_parent(
        self, ext_parent, orig_parent, report: UpdateReport
    ) -> None:
        from story_graph_ops.nodes import Story as DomainStory

        for se_ext in sorted(ext_parent.get_sub_epics(), key=lambda s: s.sequential_order or 0):
            se_orig = None
            for cand in orig_parent.get_sub_epics():
                if cand.name == se_ext.name:
                    se_orig = cand
                    break
            if se_orig is None:
                continue
            nested = se_ext.get_sub_epics()
            if nested:
                self._compute_users_delta_under_parent(se_ext, se_orig, report)
            if not se_ext.get_stories():
                continue
            seen: set = set()
            unique_ext_stories = []
            for s in se_ext.get_stories():
                if s.name not in seen:
                    seen.add(s.name)
                    unique_ext_stories.append(s)
            orig_stories = [s for s in se_orig.stories if isinstance(s, DomainStory)]
            orig_by_name = {s.name: s for s in orig_stories}
            ext_ordered = sorted(
                unique_ext_stories,
                key=lambda s: float(s.position.x) if getattr(s, 'position', None) else 0.0,
            )
            orig_explicit: List[Optional[str]] = []
            for s_ext in ext_ordered:
                s_orig = orig_by_name.get(s_ext.name)
                if s_orig is None:
                    orig_explicit.append(None)
                    continue
                ou = [str(u) for u in (s_orig.users or [])]
                orig_explicit.append(ou[0].strip() if ou and ou[0].strip() else None)
            orig_effective = _forward_fill_story_users(orig_explicit)
            for i, s_ext in enumerate(ext_ordered):
                s_orig = orig_by_name.get(s_ext.name)
                if s_orig is None:
                    continue
                ext_u = list(getattr(s_ext, 'users', None) or [])
                orig_u_eff = orig_effective[i]
                had_cells = bool(getattr(s_ext, '_had_actor_cells', False))
                if not had_cells and not ext_u:
                    continue
                if ext_u != orig_u_eff:
                    report.add_story_users_change(
                        story_name=s_ext.name,
                        parent_sub_epic=se_ext.name,
                        users=ext_u,
                    )

    def _compute_increment_delta(self, report: UpdateReport,
                                  extracted: list,
                                  original_increments: list):
        """Compare extracted increment assignments against original and
        populate the report with changes, moves, removals, and new order.
        """
        from .update_report import IncrementChange, IncrementMove

        # Build original: story → set of increment names
        orig_by_story: dict = {}  # story_name → set of increment names
        orig_by_inc: dict = {}    # inc_name → set of story names
        for inc in original_increments:
            inc_name = inc.get('name', '')
            stories = set()
            for s in inc.get('stories', []):
                name = s.get('name', '') if isinstance(s, dict) else str(s)
                stories.add(name)
                orig_by_story.setdefault(name, set()).add(inc_name)
            orig_by_inc[inc_name] = stories

        # Build extracted: story → set of increment names
        ext_by_story: dict = {}
        ext_by_inc: dict = {}
        for inc in extracted:
            inc_name = inc['name']
            stories = set(inc['stories'])
            ext_by_inc[inc_name] = stories
            for s in stories:
                ext_by_story.setdefault(s, set()).add(inc_name)

        # Compute per-increment changes (only include increments that changed)
        all_inc_names = list(dict.fromkeys(
            [inc.get('name', '') for inc in original_increments] +
            [inc['name'] for inc in extracted]))

        changes = []
        for inc_name in all_inc_names:
            orig_stories = orig_by_inc.get(inc_name, set())
            ext_stories = ext_by_inc.get(inc_name, set())
            added = sorted(ext_stories - orig_stories)
            removed = sorted(orig_stories - ext_stories)
            if added or removed:
                changes.append(IncrementChange(
                    name=inc_name, added=added, removed=removed))

        # Compute moves (story was in increment A, now in increment B)
        moves = []
        all_stories = set(orig_by_story.keys()) | set(ext_by_story.keys())
        for story in sorted(all_stories):
            orig_incs = orig_by_story.get(story, set())
            ext_incs = ext_by_story.get(story, set())
            if orig_incs == ext_incs:
                continue
            # Story gained new increment(s)
            for inc in sorted(ext_incs - orig_incs):
                from_inc = ''
                # If it was in exactly one before and is now somewhere else,
                # that's a move from old → new
                if len(orig_incs) == 1 and len(ext_incs) == 1:
                    from_inc = next(iter(orig_incs))
                moves.append(IncrementMove(
                    story=story, from_increment=from_inc, to_increment=inc))

        # Compute removed increments: in original but not in extracted
        ext_inc_names = set(ext_by_inc.keys())
        removed_increments = [
            inc.get('name', '') for inc in original_increments
            if inc.get('name', '') not in ext_inc_names
        ]

        # Only include increment_order when the name sequence actually
        # changed.  Compare name order only -- not priority values --
        # because original priorities may not be sequential 1..N.
        new_name_seq = [inc['name'] for inc in extracted]
        orig_name_seq = [inc.get('name', '') for inc in original_increments]
        if new_name_seq != orig_name_seq:
            increment_order = [
                {'name': n, 'priority': i + 1}
                for i, n in enumerate(new_name_seq)
            ]
        else:
            increment_order = []

        report.set_increment_changes(changes, moves,
                                     removed_increments=removed_increments,
                                     increment_order=increment_order)

    # ------------------------------------------------------------------
    # Pass 2 – Increment extraction by vertical position
    # ------------------------------------------------------------------

    def _build_story_to_increment_map(self, increments: list) -> dict:
        """Build a mapping of story_name → increment_name.
        
        Args:
            increments: List of increment dicts with 'name' and 'stories' keys
            
        Returns:
            Dict mapping story names to their increment names
        """
        story_to_inc = {}
        for inc in increments:
            inc_name = inc.get('name', '')
            stories = inc.get('stories', [])
            for story_name in stories:
                # Handle both string story names and dict story objects
                if isinstance(story_name, dict):
                    story_name = story_name.get('name', '')
                if story_name:
                    story_to_inc[story_name] = inc_name
        return story_to_inc

    def extract_increment_assignments(self) -> list:
        """Determine which increment lane each story belongs to by Y position.

        Completely isolated from the hierarchy (pass 1).  Only looks at
        vertical boundaries of increment lanes vs story Y positions.

        Returns:
            List of dicts ``[{'name': 'CLI', 'stories': ['Story A', ...]}, ...]``
            ordered top-to-bottom by lane Y.
        """
        # If we have rendered lanes, use them directly.
        if self._increment_lanes:
            result = []
            for lane in sorted(self._increment_lanes,
                               key=lambda l: l._lane_element.position.y
                               if l._lane_element else 0):
                stories = [getattr(s, 'name', '') or getattr(s, 'value', '')
                           for s in lane._story_copies]
                result.append({'name': lane.name, 'stories': stories})
            return result

        # Loaded from file: scan all parsed nodes to discover lanes.
        all_nodes = self._loaded_nodes if self._loaded_nodes else self._collect_all_nodes()

        # 1. Find lane backgrounds: large rectangles with empty value.
        # _LANE_MIN_WIDTH uses 2×CELL_SIZE so it is safely larger than a single
        # story sticky note (CELL_SIZE) but small enough to match tool-generated
        # lane backgrounds even for maps with only one story column.
        lanes = []
        _LANE_MIN_WIDTH = CELL_SIZE * 2
        _LANE_MIN_HEIGHT = 50
        for n in all_nodes:
            cid = getattr(n, 'cell_id', '')
            val = getattr(n, 'value', '') or ''
            bnd = getattr(n, 'boundary', None)
            
            # Must be large rectangle (potential lane background)
            if bnd is None or bnd.height < _LANE_MIN_HEIGHT or bnd.width < _LANE_MIN_WIDTH:
                continue
            
            # Lane backgrounds are large rectangles with empty value
            # (both tool-generated and user-created backgrounds)
            if val == '':
                if cid.startswith('inc-lane/'):
                    slug = cid.replace('inc-lane/', '')
                else:
                    slug = cid
                lanes.append({
                    'slug': slug,
                    'y': n.position.y,
                    'height': bnd.height,
                    'name': '',
                    'cell_id': cid,
                })
            # User-created swimlane with name directly on it
            elif cid.startswith('inc-lane/') or '/' not in cid:
                shape = getattr(n, 'shape', '')
                if shape == 'swimlane' or (not cid.startswith('epic-') and not cid.startswith('sub-epic-')):
                    slug = cid.replace('inc-lane/', '') if cid.startswith('inc-lane/') else cid
                    lanes.append({
                        'slug': slug,
                        'y': n.position.y,
                        'height': bnd.height,
                        'name': val,
                        'cell_id': cid,
                    })

        # 2. Match lane labels to get human-readable names.
        for n in all_nodes:
            cid = getattr(n, 'cell_id', '')
            val = getattr(n, 'value', '') or ''
            if not val:
                continue
            if cid.startswith('inc-label/'):
                slug = cid.replace('inc-label/', '')
                for lane in lanes:
                    if lane['slug'] == slug:
                        lane['name'] = val
                        break
            elif '/' not in cid and val:
                ny = getattr(n, 'position', None)
                if ny is None:
                    continue
                for lane in lanes:
                    if (lane['name'] == ''
                            and lane['y'] <= ny.y <= lane['y'] + lane['height']):
                        lane['name'] = val
                        break

        if not lanes:
            return []

        lanes.sort(key=lambda l: l['y'])

        # 3. Gather story candidates by Y position.
        _skip_ids = {lane['cell_id'] for lane in lanes}
        candidates = []
        # Use _all_stories to include stories that were excluded from hierarchy
        # (those in increment lanes)
        stories_list = self._all_stories if hasattr(self, '_all_stories') and self._all_stories else self.get_stories()
        for story in stories_list:
            candidates.append((story.name, story.position.y))
        for n in all_nodes:
            name = getattr(n, 'name', None) or getattr(n, 'value', None) or ''
            if name and hasattr(n, 'position') and n.position.y > 0:
                cid = getattr(n, 'cell_id', '')
                if cid in _skip_ids:
                    continue
                if cid.startswith('inc-lane/') or cid.startswith('inc-label/'):
                    continue
                if '/actor-' in cid or '/ac-' in cid:
                    continue
                candidates.append((name, n.position.y))

        # 4. Assign stories to lanes by Y overlap.
        TOLERANCE = 20
        for lane in lanes:
            lane['stories'] = []
            lane['_seen'] = set()

        for name, y in candidates:
            for lane in lanes:
                top = lane['y'] - TOLERANCE
                bottom = lane['y'] + lane['height'] + TOLERANCE
                if top <= y <= bottom:
                    if name not in lane['_seen']:
                        lane['_seen'].add(name)
                        lane['stories'].append(name)
                    break

        return [{'name': l['name'], 'stories': l['stories']} for l in lanes]

    # ------------------------------------------------------------------
    # Pass 3 - Acceptance Criteria extraction
    # ------------------------------------------------------------------

    def extract_ac_assignments(self) -> Dict[str, List[str]]:
        """Extract acceptance criteria text per story from the diagram.

        Finds AC boxes (elements with cell_id containing '/ac-' or
        user-created boxes below stories with AC-like style) and maps each
        box to the **diagram story above it**: same column (closest center X),
        then smallest vertical gap under that story's bottom edge. Boxes with
        no story above them are skipped (not acceptance criteria for sync).

        Returns:
            Dict mapping each story's ``cell_id`` (full hierarchical path) to
            a list of AC text strings, ordered by Y position (top to bottom).
        """
        # Collect all stories and their positions
        stories = []
        for story in self.get_stories():
            stories.append({
                'name': story.name,
                'cell_id': story.cell_id,
                'x': story.position.x,
                'y': story.position.y,
                'width': getattr(story.boundary, 'width', CELL_SIZE),
                'height': getattr(story.boundary, 'height', CELL_SIZE),
            })

        if not stories:
            return {}

        # Collect AC boxes from story _ac_elements and unclassified nodes.
        # Tool-generated AC: cell_id contains '/ac-'
        # User-created AC: detected by style (yellow fill, wider than story,
        #                   positioned below a story)
        ac_candidates = []
        for story in self.get_stories():
            ac_candidates.extend(getattr(story, '_ac_elements', []))
        # Also include unclassified/loaded nodes so user-created AC boxes
        # (which lack '/ac-' in their cell_id) are considered.
        ac_candidates.extend(getattr(self, '_loaded_nodes', []))

        ac_boxes = []
        for n in ac_candidates:
            cid = getattr(n, 'cell_id', '')
            val = getattr(n, 'value', '') or getattr(n, 'name', '') or ''
            if not val:
                continue
            bnd = getattr(n, 'boundary', None)
            pos = getattr(n, 'position', None)
            if not bnd or not pos:
                continue

            is_tool_ac = '/ac-' in cid
            # User-created AC: wider than a story cell, below the story area
            is_user_ac = (not is_tool_ac
                          and '/' not in cid
                          and bnd.width > CELL_SIZE * 2
                          and bnd.height >= 30)

            if is_tool_ac or is_user_ac:
                ac_boxes.append({
                    'cell_id': cid,
                    'text': plain_ac_from_cell_value(val.strip()),
                    'x': pos.x,
                    'y': pos.y,
                    'width': bnd.width,
                    'height': bnd.height,
                })

        # Empty diagram AC layer must still produce per-story ``[]`` entries so
        # Pass 3 can diff "all AC removed" / "stories with no boxes" vs JSON.
        if not ac_boxes:
            return {s['cell_id']: [] for s in stories}

        # Sort AC boxes by Y position
        ac_boxes.sort(key=lambda b: b['y'])

        # Story on top of each AC (layout). Keys are story ``cell_id``.
        result: Dict[str, List[str]] = {}
        for ac in ac_boxes:
            ac_cx = ac['x'] + ac['width'] * 0.5
            candidates: List[Tuple[float, float, str]] = []
            for s in stories:
                story_bottom = s['y'] + s['height']
                if ac['y'] < story_bottom:
                    continue
                scx = s['x'] + s['width'] * 0.5
                x_dist = abs(ac_cx - scx)
                y_dist = ac['y'] - story_bottom
                candidates.append((x_dist, y_dist, s['cell_id']))
            if not candidates:
                continue
            candidates.sort()
            matched_cid = candidates[0][2]
            result.setdefault(matched_cid, []).append(ac['text'])

        for s in stories:
            result.setdefault(s['cell_id'], [])

        return result

    # ------------------------------------------------------------------
    # Dict conversion
    # ------------------------------------------------------------------

    def _to_story_graph_dict(self) -> Dict[str, Any]:
        epics = []
        for epic in self._drawio_epics:
            epic_dict = {
                'name': epic.name,
                'sequential_order': epic.sequential_order,
                'sub_epics': [self._sub_epic_to_dict(se) for se in epic.get_sub_epics()]
            }
            epics.append(epic_dict)
        return {'epics': epics}

    def _sub_epic_to_dict(self, se: DrawIOSubEpic) -> Dict[str, Any]:
        nested_sub_epics = se.get_sub_epics()
        if nested_sub_epics:
            return {
                'name': se.name,
                'sequential_order': se.sequential_order,
                'sub_epics': [self._sub_epic_to_dict(n) for n in nested_sub_epics],
                'story_groups': []
            }
        return {
            'name': se.name,
            'sequential_order': se.sequential_order,
            'sub_epics': [],
            'story_groups': [{
                'type': 'and', 'connector': None,
                'stories': [
                    {
                        'name': s.name,
                        'sequential_order': s.sequential_order,
                        'story_type': s.story_type or 'user',
                        'users': list(getattr(s, 'users', None) or []),
                    }
                    for s in se.get_stories()
                ]
            }]
        }

    # ------------------------------------------------------------------
    # Load from DrawIO file (reverse direction)
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, file_path: Path, diagram_type: str = 'outline') -> 'DrawIOStoryMap':
        """Load DrawIO diagram from file."""
        instance = cls(diagram_type=diagram_type)
        instance._load_from_file(file_path)
        return instance
    
    def _load_from_file(self, file_path: Path):
        """Internal method to load from file."""
        content = file_path.read_text(encoding='utf-8')
        nodes, parent_map = DrawIOStoryNodeSerializer.parse_nodes_from_xml(content)

        # Resolve group-relative positions: elements whose parent is a group
        # have x/y relative to the group.  Add the group's absolute position
        # so all nodes use absolute coordinates.
        self._resolve_group_positions(nodes, parent_map)

        nodes_by_id = {}
        for n in nodes:
            nodes_by_id[n.cell_id] = n

        epics = [n for n in nodes if isinstance(n, DrawIOEpic)]
        sub_epics = [n for n in nodes if isinstance(n, DrawIOSubEpic)]
        stories = [n for n in nodes if isinstance(n, DrawIOStory)]

        self._assign_by_parent_map(nodes_by_id, parent_map, epics, sub_epics, stories, all_nodes=nodes)
        self._assign_sequential_order_from_position(epics, sub_epics, stories)
        self._drawio_epics = epics
        self._all_stories = stories  # Keep all parsed stories for increment extraction

        # Classify remaining nodes: attach AC elements to their parent
        # stories, and reconstruct increment lanes.  Anything else is
        # discarded (lane backgrounds, labels; actor cells are consumed
        # into ``DrawIOStory.users`` above).
        classified = set()
        for e in epics:
            classified.add(id(e))
            self._classify_sub_epic_tree(e.get_sub_epics(), classified)
        
        # Mark all stories as classified (even those excluded from hierarchy)
        # so they don't end up in _loaded_nodes
        for s in stories:
            classified.add(id(s))

        # Build story lookup by cell_id for AC attachment
        story_by_cid = {}
        for s in stories:
            story_by_cid[s.cell_id] = s

        # Personas: actor-fill chips (same rule as serializer) above each story column,
        # then forward-fill along the row; ``_had_actor_cells`` is row-level when any
        # chip exists in that leaf sub-epic row.
        self._assign_outline_actor_cells_from_diagram(nodes)

        unclassified = []
        for n in nodes:
            if id(n) in classified:
                continue
            cid = getattr(n, 'cell_id', '')
            # Attach AC elements to parent story
            if '/ac-' in cid:
                story_cid = cid.rsplit('/ac-', 1)[0]
                parent_story = story_by_cid.get(story_cid)
                if parent_story:
                    if not hasattr(parent_story, '_ac_elements'):
                        parent_story._ac_elements = []
                    parent_story._ac_elements.append(n)
                else:
                    # Orphan tool AC (e.g. merged column: story header removed but
                    # ``/ac-*`` ids still reference the old story path). Keep the node
                    # so ``extract_ac_assignments`` can key by parent path + slug.
                    unclassified.append(n)
                continue
            unclassified.append(n)

        self._loaded_nodes = unclassified
        
        # Detect what type of content this diagram has based on loaded elements
        # Check for increment lanes
        for n in unclassified:
            cid = getattr(n, 'cell_id', '')
            shape = getattr(n, 'shape', '')
            if cid.startswith('inc-lane/') or cid.startswith('inc-label/') or shape == 'swimlane':
                self._has_rendered_increments = True
                break
        
        # Check for AC boxes (attached to stories)
        for s in stories:
            if hasattr(s, '_ac_elements') and s._ac_elements:
                self._has_rendered_ac = True
                break

    def _classify_sub_epic_tree(self, sub_epics, classified: set):
        """Recursively walk sub-epics and their children into the classified set."""
        for se in sub_epics:
            classified.add(id(se))
            for s in se.get_stories():
                classified.add(id(s))
            self._classify_sub_epic_tree(se.get_sub_epics(), classified)

    def _assign_outline_actor_cells_from_diagram(self, nodes: List[Any]) -> None:
        """Resolve ``DrawIOStory.users`` from outline persona chips (actor fill).

        Per leaf sub-epic row, stories are ordered left-to-right. A chip above a
        column sets an **explicit** persona; following stories inherit until the
        next explicit (forward-fill). Row has ``_had_actor_cells`` when any chip
        appears in that row (so clearing all chips can clear JSON on sync).
        """
        persona_nodes = _outline_persona_nodes(nodes)

        def assign_leaf_row(se: DrawIOSubEpic) -> None:
            nested = se.get_sub_epics()
            if nested:
                for ch in sorted(nested, key=lambda x: x.sequential_order or 0.0):
                    assign_leaf_row(ch)
                return
            st_list = se.get_stories()
            if not st_list:
                return
            ordered = sorted(
                st_list,
                key=lambda s: float(s.position.x) if getattr(s, 'position', None) else 0.0,
            )
            _apply_outline_row_personas(ordered, persona_nodes)

        for epic in sorted(self._drawio_epics, key=lambda e: e.sequential_order or 0.0):
            for se in sorted(epic.get_sub_epics(), key=lambda s: s.sequential_order or 0.0):
                assign_leaf_row(se)

    @staticmethod
    def _resolve_group_positions(nodes, parent_map):
        """Convert group-relative positions to absolute positions.

        DrawIO stores child positions relative to their parent group.
        This method adds the parent group's x/y offset so all nodes
        use absolute coordinates.
        """
        nodes_by_id = {n.cell_id: n for n in nodes}
        for node in nodes:
            pid = parent_map.get(node.cell_id, '')
            if pid in ('', '0', '1'):
                continue  # top-level element, position is already absolute
            parent_node = nodes_by_id.get(pid)
            if parent_node is None:
                continue
            if not hasattr(parent_node, 'position'):
                continue
            # Offset this node by its parent group's position
            abs_x = node.position.x + parent_node.position.x
            abs_y = node.position.y + parent_node.position.y
            node.set_position(abs_x, abs_y)

    # ------------------------------------------------------------------
    # Internal helpers (load direction)
    # ------------------------------------------------------------------

    def _assign_by_parent_map(self, nodes_by_id, parent_map, epics, sub_epics, stories, all_nodes=None):
        # ── Phase 1: ID-based assignment for epics and sub-epics only ──
        # Stories are intentionally excluded here because their cell IDs
        # become stale when users drag them to a new sub-epic in DrawIO
        # (DrawIO preserves the original ID, only the position changes).
        for node in list(epics) + list(sub_epics):
            cell_id = node.cell_id
            if '/' not in cell_id:
                continue
            found = False
            parts = cell_id.split('/')
            for cut in range(len(parts) - 1, 0, -1):
                candidate = '/'.join(parts[:cut])
                parent_node = nodes_by_id.get(candidate)
                if parent_node and parent_node is not node and hasattr(parent_node, 'add_child'):
                    parent_node.add_child(node)
                    found = True
                    break
            if found:
                continue
            pid = parent_map.get(cell_id, '')
            parent_from_attr = nodes_by_id.get(pid)
            if parent_from_attr and parent_from_attr is not node and hasattr(parent_from_attr, 'add_child'):
                parent_from_attr.add_child(node)
                continue

        # ── Phase 1b: Reparent sub-epics by vertical stacking (bar above = parent) ──
        # When cell_id assigns sub-epics to the epic in Phase 1, reparent so the bar directly
        # above (largest Y among bars above that contain this one) is the parent.
        for se in sub_epics:
            parent = getattr(se, '_parent', None)
            if not parent or not isinstance(parent, DrawIOEpic):
                continue
            se_cx = se.boundary.center.x
            se_y = se.boundary.y
            best_parent_se = None
            best_y = -1.0
            for candidate_se in parent.get_sub_epics():
                if candidate_se is se:
                    continue
                cand_y = candidate_se.boundary.y
                if cand_y >= se_y:
                    continue
                cl = candidate_se.boundary.x
                cr = candidate_se.boundary.x + candidate_se.boundary.width
                if cl <= se_cx <= cr and cand_y > best_y:
                    best_y = cand_y
                    best_parent_se = candidate_se
            if best_parent_se:
                parent._children.remove(se)
                se._parent = None
                best_parent_se.add_child(se)

        # ── Phase 2a: Orphan sub-epics → nest under the bar directly above ──
        # For orphan sub-epics (no hierarchical ID), find a sub-epic that already has a parent
        # and is directly above (largest Y among those above that contain this one).
        for se in sub_epics:
            if se._parent is not None:
                continue
            se_cx = se.boundary.center.x
            se_y = se.boundary.y
            best_parent_se = None
            best_y = -1.0
            for candidate_se in sub_epics:
                if candidate_se is se or candidate_se._parent is None:
                    continue
                cand_y = candidate_se.boundary.y
                if cand_y >= se_y:
                    continue
                cl = candidate_se.boundary.x
                cr = candidate_se.boundary.x + candidate_se.boundary.width
                if cl <= se_cx <= cr and cand_y > best_y:
                    best_y = cand_y
                    best_parent_se = candidate_se
            if best_parent_se:
                best_parent_se.add_child(se)

        # ── Phase 2b: Position-based sub-epic → epic fallback ──
        MARGIN = 200
        for se in sub_epics:
            if se._parent is not None:
                continue
            se_cx = se.boundary.center.x
            best_epic = None
            best_dist = float('inf')
            for epic in epics:
                left = epic.boundary.x - MARGIN
                right = epic.boundary.x + epic.boundary.width + MARGIN
                if left <= se_cx <= right:
                    dist = abs(se_cx - epic.boundary.center.x)
                    if dist < best_dist:
                        best_dist = dist
                        best_epic = epic
            if best_epic:
                best_epic.add_child(se)

        # ── Phase 2c: Reparent sub-epics by vertical stacking (higher bar = parent of lower bar) ──
        # Runs after Phase 2b so flat-ID sub-epics get nested. The bar directly above (smaller Y)
        # whose X span contains this bar is the parent. Among bars above that contain this one,
        # pick the one with largest Y = immediate parent in the stack. Repeat for multiple levels.
        def _reparent_sub_epics_under_containing_sibling():
            changed = False
            by_y = sorted(sub_epics, key=lambda n: (getattr(n.boundary, 'y', 0), getattr(n.boundary, 'x', 0)))
            for se in by_y:
                parent = getattr(se, '_parent', None)
                if not parent:
                    continue
                if isinstance(parent, DrawIOEpic):
                    siblings = parent.get_sub_epics()
                elif hasattr(parent, 'get_sub_epics'):
                    siblings = parent.get_sub_epics()
                else:
                    continue
                se_cx = se.boundary.center.x
                se_y = se.boundary.y
                best_parent_se = None
                best_y = -1.0
                for candidate_se in siblings:
                    if candidate_se is se:
                        continue
                    cand_y = candidate_se.boundary.y
                    if cand_y >= se_y:
                        continue
                    cl = candidate_se.boundary.x
                    cr = candidate_se.boundary.x + candidate_se.boundary.width
                    if cl <= se_cx <= cr and cand_y > best_y:
                        best_y = cand_y
                        best_parent_se = candidate_se
                if best_parent_se:
                    parent._children.remove(se)
                    se._parent = None
                    best_parent_se.add_child(se)
                    changed = True
            return changed

        while _reparent_sub_epics_under_containing_sibling():
            pass

        # ── Phase 3: Position-based story → sub-epic assignment ──
        # Always use position for stories (never IDs) because the visual
        # position in the diagram is the source of truth after user edits.
        # Skip stories that are inside increment lanes - those are handled by
        # increment extraction (Pass 2), not hierarchy assignment.
        
        # First, find increment lane Y ranges to exclude lane stories from hierarchy
        # Only check for lanes if we have clear lane indicators (swimlane shapes or inc-lane/ prefixes)
        lane_y_ranges = []
        has_explicit_lanes = False
        if all_nodes:
            for n in all_nodes:
                if isinstance(n, (DrawIOEpic, DrawIOSubEpic, DrawIOStory)):
                    continue
                cid = getattr(n, 'cell_id', '')
                shape = getattr(n, 'shape', '')
                # Only detect lanes if there are explicit indicators
                if cid.startswith('inc-lane/') or cid.startswith('inc-label/') or shape == 'swimlane':
                    has_explicit_lanes = True
                    break
        
        if has_explicit_lanes and all_nodes:
            for n in all_nodes:
                if isinstance(n, (DrawIOEpic, DrawIOSubEpic, DrawIOStory)):
                    continue
                if not hasattr(n, 'boundary') or not hasattr(n, 'position'):
                    continue
                cid = getattr(n, 'cell_id', '')
                val = getattr(n, 'value', '') or ''
                bnd = n.boundary
                shape = getattr(n, 'shape', '')
                # Detect lane backgrounds
                if (bnd and bnd.width >= 200 and bnd.height >= 50):
                    # Tool-generated: empty value with inc-lane/ or shape=swimlane
                    # User/test: large rectangle with lane-X id (but not lane-story-X-Y)
                    is_lane = (cid.startswith('inc-lane/') or 
                              shape == 'swimlane' or
                              (cid.startswith('lane-') and not cid.startswith('lane-story-')))
                    if is_lane:
                        lane_y_ranges.append((n.position.y, n.position.y + bnd.height))
        
        for story in stories:
            # Skip story copies in increment lanes (by cell ID or Y position)
            if story.cell_id.startswith('inc-lane/'):
                continue
            # Skip stories positioned within any increment lane Y range
            if lane_y_ranges:
                story_y = story.position.y
                in_lane = False
                for y_start, y_end in lane_y_ranges:
                    if y_start <= story_y <= y_end:
                        in_lane = True
                        break
                if in_lane:
                    continue
            
            story_cx = story.boundary.center.x
            best_se = None
            best_width = float('inf')
            for se in sub_epics:
                if se._parent is None:
                    continue
                se_left = se.boundary.x
                se_right = se.boundary.x + se.boundary.width
                if se_left <= story_cx <= se_right:
                    if not se.get_sub_epics() and se.boundary.width < best_width:
                        best_width = se.boundary.width
                        best_se = se
            if best_se:
                best_se.add_child(story)

    def _assign_sequential_order_from_position(self, epics, sub_epics, stories):
        Y_TOLERANCE = 30  # nodes within this many px of Y are on the same row

        # Epics: left-to-right by X only, ignore Y
        for idx, node in enumerate(sorted(epics, key=lambda n: n.position.x)):
            node.sequential_order = float(idx + 1)

        # Sub-epics and stories: order within parent, Y tolerance then X
        for group in [sub_epics, stories]:
            by_parent = {}
            for n in group:
                pid = id(n._parent) if n._parent else 0
                by_parent.setdefault(pid, []).append(n)
            for siblings in by_parent.values():
                sorted_nodes = sorted(siblings,
                    key=lambda n: (round(n.position.y / Y_TOLERANCE), n.position.x))
                for idx, node in enumerate(sorted_nodes):
                    node.sequential_order = float(idx + 1)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _collect_all_nodes(self) -> list:
        """Walk the tree and gather every renderable node.

        Serialization order determines visual stacking in DrawIO (later =
        on top).  For increments view we want:
          1. Lane backgrounds (large rectangles) – bottom layer
          2. Epics / sub-epics bars – structural outlines
             (includes stories with their actor and AC elements)
          3. Lane labels, actors, story copies inside lanes
        """
        nodes = []

        # 1. Lane backgrounds first (bottom layer)
        for lane in self._increment_lanes:
            if lane._lane_element:
                nodes.append(lane._lane_element)

        # 2. Epic tree (epics, sub-epics, stories, actors, AC)
        for epic in self._drawio_epics:
            nodes.extend(epic.collect_all_nodes())

        # 3. Lane labels, actors, story copies (top layer)
        for lane in self._increment_lanes:
            if lane._label_element:
                nodes.append(lane._label_element)
            nodes.extend(lane._actor_elements)
            nodes.extend(lane._story_copies)

        return nodes

    def _collect_domain_stories(self, story_map: StoryMap) -> dict:
        """Build name→Story lookup from all stories in the map."""
        result: Dict[str, Story] = {}
        for epic in story_map.epics:
            for sub_epic in epic.sub_epics:
                self._gather_stories(sub_epic, result)
        return result

    def _gather_stories(self, sub_epic, result: dict):
        for child in sub_epic.children:
            if isinstance(child, Story):
                result[child.name] = child
            elif isinstance(child, SubEpic):
                self._gather_stories(child, result)
            elif isinstance(child, StoryGroup):
                for story in child.children:
                    if isinstance(story, Story):
                        result[story.name] = story


# =============================================================================
# Diagram Type Subclasses
# =============================================================================

class DrawIOOutlineMap(DrawIOStoryMap):
    """DrawIO story map specialized for outline diagrams.
    
    Renders story map hierarchy as epics, sub-epics, and stories without
    acceptance criteria or increment lanes.
    """
    
    def __init__(self, story_graph: Dict[str, Any] = None):
        super().__init__(diagram_type='outline', story_graph=story_graph)
    
    def render(self, story_map: StoryMap,
               layout_data: Optional[LayoutData] = None,
               skip_stories: bool = False,
               story_widths: Dict[str, float] = None) -> Union[Dict[str, Any], RenderSummary]:
        """Render outline diagram showing story map hierarchy.
        
        Args:
            story_map: The story map to render
            layout_data: Optional saved positions for nodes
            skip_stories: If True, only render epics and sub-epics (for increment base)
            story_widths: Optional custom widths for stories
            
        Returns:
            RenderSummary with render statistics
        """
        return self.render_from_story_map(
            story_map, layout_data, skip_stories, story_widths)


class DrawIOExplorationMap(DrawIOStoryMap):
    """DrawIO story map specialized for exploration/acceptance criteria diagrams.
    
    Renders story map with acceptance criteria boxes positioned below stories,
    with AC-aware spacing to prevent overlap.
    """
    
    def __init__(self, story_graph: Dict[str, Any] = None):
        super().__init__(diagram_type='acceptance_criteria', story_graph=story_graph)
    
    def render(self, story_map: StoryMap,
               layout_data: Optional[LayoutData] = None) -> Union[Dict[str, Any], RenderSummary]:
        """Render exploration diagram with acceptance criteria.
        
        Args:
            story_map: The story map to render
            layout_data: Optional saved positions for nodes
            
        Returns:
            RenderSummary with render statistics including AC count
        """
        return self.render_exploration_from_story_map(story_map, layout_data)


class DrawIOIncrementsMap(DrawIOStoryMap):
    """DrawIO story map specialized for increment diagrams.
    
    Renders story map with increment lanes below the outline, showing story
    assignments to delivery increments. Stories assigned to increments appear
    only in their lanes; unassigned stories appear in the outline above.
    """
    
    def __init__(self, story_graph: Dict[str, Any] = None):
        super().__init__(diagram_type='increments', story_graph=story_graph)
    
    def render(self, story_map: StoryMap,
               increments_data: list,
               layout_data: Optional[LayoutData] = None) -> Union[Dict[str, Any], RenderSummary]:
        """Render increments diagram with story assignments.
        
        Args:
            story_map: The story map to render
            increments_data: List of increment dictionaries with story assignments
            layout_data: Optional saved positions for nodes
            
        Returns:
            RenderSummary with render statistics including increment count
        """
        return self.render_increments_from_story_map(
            story_map, increments_data, layout_data)
