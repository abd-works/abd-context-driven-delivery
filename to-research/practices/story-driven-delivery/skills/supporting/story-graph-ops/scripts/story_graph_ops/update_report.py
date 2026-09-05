import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class MatchEntry:
    extracted_name: str
    original_name: str
    confidence: float = 1.0
    parent: str = ''


@dataclass
class StoryEntry:
    name: str
    parent: str = ''


@dataclass
class LargeDeletions:
    missing_epics: List[str] = field(default_factory=list)
    missing_sub_epics: List[str] = field(default_factory=list)


@dataclass
class IncrementChange:
    """Delta for a single increment: stories added or removed."""
    name: str
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)


@dataclass
class IncrementMove:
    """A story that moved from one increment to another."""
    story: str
    from_increment: str   # '' means previously unassigned (orphan)
    to_increment: str     # '' means now unassigned (orphan)


@dataclass
class StoryMove:
    """A story that moved from one parent (sub-epic) to another in the hierarchy."""
    name: str
    from_parent: str
    to_parent: str


@dataclass
class SubEpicMove:
    """A sub-epic that moved from one parent (epic or sub-epic) to another."""
    name: str
    from_parent: str
    to_parent: str


@dataclass
class StoryGroupReorder:
    """Stories under a sub-epic reordered (e.g. left-to-right in outline DrawIO)."""
    parent_sub_epic: str
    story_names: List[str]


@dataclass
class SubEpicSiblingReorder:
    """Sub-epics under an epic (or nested under a sub-epic) reordered left-to-right."""
    parent: str
    sub_epic_names: List[str]


@dataclass
class ACChange:
    """Delta for acceptance criteria on a single story."""
    story_name: str
    parent: str = ''
    added: List[str] = field(default_factory=list)      # AC text added
    removed: List[str] = field(default_factory=list)     # AC text removed
    modified: List[Dict[str, str]] = field(default_factory=list)  # [{old, new}]
    reordered: List[str] = field(default_factory=list)   # new AC order (texts)


@dataclass
class ACMove:
    """An acceptance criterion that moved from one story to another."""
    ac_text: str
    from_story: str
    to_story: str


@dataclass
class StoryUsersChange:
    """Replace ``story.users`` (personas / actors) from outline DrawIO.

    ``parent_sub_epic`` disambiguates duplicate story names; may be empty
    to fall back to global story lookup.
    """
    story_name: str
    parent_sub_epic: str = ''
    users: List[str] = field(default_factory=list)


class UpdateReport:

    def __init__(self):
        self._renames: List[MatchEntry] = []
        self._new_stories: List[StoryEntry] = []
        self._new_sub_epics: List[StoryEntry] = []
        self._new_epics: List[StoryEntry] = []
        self._removed_stories: List[StoryEntry] = []
        self._removed_sub_epics: List[StoryEntry] = []
        self._removed_epics: List[StoryEntry] = []
        self._large_deletions = LargeDeletions()
        self._matched_count = 0
        self._moved_stories: List[StoryMove] = []
        self._moved_sub_epics: List[SubEpicMove] = []
        self._increment_changes: List[IncrementChange] = []
        self._increment_moves: List[IncrementMove] = []
        self._removed_increments: List[str] = []
        self._increment_order: List[Dict[str, Any]] = []  # [{name, priority}, ...]
        self._ac_changes: List[ACChange] = []
        self._ac_moves: List[ACMove] = []
        self._story_group_reorders: List[StoryGroupReorder] = []
        self._sub_epic_sibling_reorders: List[SubEpicSiblingReorder] = []
        self._story_users_changes: List[StoryUsersChange] = []

    @property
    def story_users_changes(self) -> List[StoryUsersChange]:
        return list(self._story_users_changes)

    @property
    def story_group_reorders(self) -> List[StoryGroupReorder]:
        return list(self._story_group_reorders)

    @property
    def sub_epic_sibling_reorders(self) -> List[SubEpicSiblingReorder]:
        return list(self._sub_epic_sibling_reorders)

    @property
    def renames(self) -> List[MatchEntry]:
        return list(self._renames)

    @property
    def fuzzy_matches(self) -> List[MatchEntry]:
        return self.renames

    @property
    def new_stories(self) -> List[StoryEntry]:
        return list(self._new_stories)

    @property
    def new_sub_epics(self) -> List[StoryEntry]:
        return list(self._new_sub_epics)

    @property
    def new_epics(self) -> List[StoryEntry]:
        return list(self._new_epics)

    @property
    def removed_stories(self) -> List[StoryEntry]:
        return list(self._removed_stories)

    @property
    def removed_sub_epics(self) -> List[StoryEntry]:
        return list(self._removed_sub_epics)

    @property
    def removed_epics(self) -> List[StoryEntry]:
        return list(self._removed_epics)

    @property
    def large_deletions(self) -> LargeDeletions:
        return self._large_deletions

    @property
    def matched_count(self) -> int:
        return self._matched_count

    @property
    def moved_stories(self) -> List[StoryMove]:
        return list(self._moved_stories)

    @property
    def moved_sub_epics(self) -> List[SubEpicMove]:
        return list(self._moved_sub_epics)

    @property
    def increment_changes(self) -> List[IncrementChange]:
        return list(self._increment_changes)

    @property
    def increment_moves(self) -> List[IncrementMove]:
        return list(self._increment_moves)

    @property
    def removed_increments(self) -> List[str]:
        return list(self._removed_increments)

    @property
    def increment_order(self) -> List[Dict[str, Any]]:
        return list(self._increment_order)

    @property
    def ac_changes(self) -> List[ACChange]:
        return list(self._ac_changes)

    @property
    def ac_moves(self) -> List[ACMove]:
        return list(self._ac_moves)

    def set_ac_changes(self, changes: List[ACChange]):
        self._ac_changes = list(changes)

    def reconcile_ac_moves(self):
        """Post-process AC changes: detect AC text that moved between stories.

        If the same AC text appears in one story's 'removed' and another
        story's 'added', it's a move, not a delete+add.  Reconciled entries
        are moved from ac_changes into ac_moves.
        """
        # Build maps: ac_text -> story that removed it / added it
        removed_map: Dict[str, str] = {}  # ac_text -> story_name
        added_map: Dict[str, str] = {}

        for change in self._ac_changes:
            for text in change.removed:
                removed_map[text] = change.story_name
            for text in change.added:
                added_map[text] = change.story_name

        # Find overlap: same text removed from one story and added to another
        moved_texts: set = set()
        for text in list(removed_map.keys()):
            if text in added_map and removed_map[text] != added_map[text]:
                self._ac_moves.append(ACMove(
                    ac_text=text,
                    from_story=removed_map[text],
                    to_story=added_map[text]))
                moved_texts.add(text)

        # Remove reconciled entries from ac_changes
        if moved_texts:
            for change in self._ac_changes:
                change.added = [t for t in change.added if t not in moved_texts]
                change.removed = [t for t in change.removed if t not in moved_texts]
            # Remove empty changes (keep reorder-only entries)
            self._ac_changes = [c for c in self._ac_changes
                                if c.added or c.removed or c.modified
                                or c.reordered]

    def set_increment_changes(self, changes: List[IncrementChange],
                               moves: List[IncrementMove],
                               removed_increments: List[str] = None,
                               increment_order: List[Dict[str, Any]] = None):
        self._increment_changes = list(changes)
        self._increment_moves = list(moves)
        self._removed_increments = list(removed_increments or [])
        self._increment_order = list(increment_order or [])

    @property
    def has_changes(self) -> bool:
        ld = self._large_deletions
        return bool(
            self._renames
            or self._new_stories
            or self._new_sub_epics
            or self._new_epics
            or self._removed_stories
            or self._removed_sub_epics
            or self._removed_epics
            or self._moved_stories
            or self._moved_sub_epics
            or ld.missing_epics
            or ld.missing_sub_epics
            or self._increment_changes
            or self._increment_moves
            or self._removed_increments
            or self._increment_order
            or self._ac_changes
            or self._ac_moves
            or self._story_users_changes
            or self._story_group_reorders
            or self._sub_epic_sibling_reorders
        )

    def add_story_group_reorder(self, parent_sub_epic: str, story_names: List[str]) -> None:
        self._story_group_reorders.append(
            StoryGroupReorder(parent_sub_epic=parent_sub_epic, story_names=list(story_names)))

    def add_sub_epic_sibling_reorder(self, parent: str, sub_epic_names: List[str]) -> None:
        self._sub_epic_sibling_reorders.append(
            SubEpicSiblingReorder(parent=parent, sub_epic_names=list(sub_epic_names)))

    def add_story_users_change(
        self, story_name: str, parent_sub_epic: str, users: List[str]
    ) -> None:
        self._story_users_changes.append(
            StoryUsersChange(
                story_name=story_name,
                parent_sub_epic=parent_sub_epic or '',
                users=list(users),
            )
        )

    def add_exact_match(self, extracted_name: str, original_name: str, parent: str = ''):
        self._matched_count += 1

    def add_rename(self, extracted_name: str, original_name: str,
                   confidence: float, parent: str = ''):
        self._renames.append(
            MatchEntry(extracted_name=extracted_name, original_name=original_name,
                       confidence=confidence, parent=parent))

    def add_fuzzy_match(self, extracted_name: str, original_name: str,
                        confidence: float, parent: str = ''):
        self.add_rename(extracted_name, original_name, confidence, parent)

    def add_new_story(self, name: str, parent: str = ''):
        self._new_stories.append(StoryEntry(name=name, parent=parent))

    def add_new_sub_epic(self, name: str, parent: str = ''):
        self._new_sub_epics.append(StoryEntry(name=name, parent=parent))

    def add_new_epic(self, name: str, parent: str = ''):
        self._new_epics.append(StoryEntry(name=name, parent=parent))

    def add_removed_story(self, name: str, parent: str = ''):
        self._removed_stories.append(StoryEntry(name=name, parent=parent))

    def add_removed_sub_epic(self, name: str, parent: str = ''):
        self._removed_sub_epics.append(StoryEntry(name=name, parent=parent))

    def add_removed_epic(self, name: str, parent: str = ''):
        self._removed_epics.append(StoryEntry(name=name, parent=parent))

    def add_missing_epic(self, epic_name: str):
        self._large_deletions.missing_epics.append(epic_name)

    def add_missing_sub_epic(self, sub_epic_name: str):
        self._large_deletions.missing_sub_epics.append(sub_epic_name)

    def reconcile_moves(self, original_story_map=None, extracted_increments=None):
        """Post-process: detect stories and sub-epics that are actually moves, not new+removed.

        Sub-epics: if a sub-epic appears in both new_sub_epics and removed_sub_epics
        (same name), it was re-parented in the diagram (e.g. from epic to a sibling
        sub-epic). Remove from both so it is not treated as deleted.

        Stories (three cases):
        1. A story appears in both new_stories and removed_stories with
           different parents → it was moved between sub-epics.
        2. A story appears in new_stories and its name existed under a
           removed sub-epic in the original tree → it was promoted from
           the removed sub-epic to a new parent.
        3. A story is reported as removed from hierarchy but exists in
           increment lanes → it's intentionally not in hierarchy (increments view).

        Matched stories are moved from new/removed into moved_stories, or
        removed from removed_stories if they're in increment lanes.
        """
        moved_names: set = set()

        # --- Sub-epics: same name in both new and removed = move (re-parent) ---
        new_se_by_name: Dict[str, StoryEntry] = {s.name: s for s in self._new_sub_epics}
        removed_se_by_name: Dict[str, StoryEntry] = {s.name: s for s in self._removed_sub_epics}
        reconciled_se_names = set(new_se_by_name.keys()) & set(removed_se_by_name.keys())
        if reconciled_se_names:
            for name in reconciled_se_names:
                removed_entry = removed_se_by_name[name]
                new_entry = new_se_by_name[name]
                self._moved_sub_epics.append(SubEpicMove(
                    name=name,
                    from_parent=removed_entry.parent,
                    to_parent=new_entry.parent))
            self._new_sub_epics = [s for s in self._new_sub_epics
                                  if s.name not in reconciled_se_names]
            self._removed_sub_epics = [s for s in self._removed_sub_epics
                                      if s.name not in reconciled_se_names]
            for name in reconciled_se_names:
                self._large_deletions.missing_sub_epics = [
                    n for n in self._large_deletions.missing_sub_epics
                    if n != name]

        # --- Case 1: direct overlap between new and removed ---
        new_by_name: Dict[str, StoryEntry] = {}
        for s in self._new_stories:
            new_by_name.setdefault(s.name, s)

        removed_by_name: Dict[str, StoryEntry] = {}
        for s in self._removed_stories:
            removed_by_name.setdefault(s.name, s)

        for name in list(new_by_name.keys()):
            if name in removed_by_name:
                new_entry = new_by_name[name]
                removed_entry = removed_by_name[name]
                self._moved_stories.append(StoryMove(
                    name=name,
                    from_parent=removed_entry.parent,
                    to_parent=new_entry.parent))
                moved_names.add(name)

        # --- Case 2: stories from removed sub-epics ---
        if original_story_map:
            removed_se_names = {s.name for s in self._removed_sub_epics}
            if removed_se_names:
                # Collect all story names under removed sub-epics in the original
                orphaned_from_se: Dict[str, str] = {}  # story_name → sub_epic_name
                for epic in original_story_map.epics:
                    self._collect_stories_under_removed(
                        epic, removed_se_names, orphaned_from_se)

                for name, from_parent in orphaned_from_se.items():
                    if name in moved_names:
                        continue  # already handled by Case 1
                    if name in new_by_name:
                        # Story was under removed sub-epic but appears in new diagram
                        new_entry = new_by_name[name]
                        self._moved_stories.append(StoryMove(
                            name=name,
                            from_parent=from_parent,
                            to_parent=new_entry.parent))
                        moved_names.add(name)
                    elif name not in removed_by_name:
                        # Story was under removed sub-epic and is NOT in new diagram
                        # Add it to removed_stories if not already there
                        self._removed_stories.append(StoryEntry(name=name, parent=from_parent))

        # --- Case 3: stories in increment lanes (not removed from hierarchy) ---
        # If a story appears in increment assignments but is reported as removed
        # from hierarchy, it's not actually removed - it's just in a lane.
        if extracted_increments:
            # Collect all story names that appear in ANY increment lane
            stories_in_lanes: set = set()
            for inc in extracted_increments:
                stories_in_lanes.update(inc.get('stories', []))
            
            # Remove from removed_stories if they're in increments
            if stories_in_lanes:
                self._removed_stories = [s for s in self._removed_stories
                                        if s.name not in stories_in_lanes]
        
        # Remove reconciled entries from new_stories and removed_stories
        if moved_names:
            self._new_stories = [s for s in self._new_stories
                                 if s.name not in moved_names]
            self._removed_stories = [s for s in self._removed_stories
                                     if s.name not in moved_names]

    @staticmethod
    def _collect_stories_under_removed(node, removed_se_names: set,
                                        result: Dict[str, str]):
        """Walk the original tree and collect story names under removed sub-epics."""
        sub_epics = []
        if hasattr(node, 'sub_epics'):
            sub_epics = list(node.sub_epics)
        elif hasattr(node, 'children'):
            from story_graph_ops.nodes import SubEpic
            sub_epics = [c for c in node.children if isinstance(c, SubEpic)]

        for se in sub_epics:
            if se.name in removed_se_names:
                # All stories under this (now removed) sub-epic
                all_stories = []
                if hasattr(se, 'all_stories'):
                    all_stories = list(se.all_stories)
                elif hasattr(se, 'children'):
                    from story_graph_ops.nodes import Story
                    all_stories = [c for c in se.children if isinstance(c, Story)]
                
                # Also collect stories from story_groups
                if hasattr(se, 'story_groups') and se.story_groups:
                    for group in se.story_groups:
                        if hasattr(group, 'stories') and group.stories:
                            all_stories.extend(group.stories)
                
                for story in all_stories:
                    result[story.name] = se.name
            else:
                UpdateReport._collect_stories_under_removed(
                    se, removed_se_names, result)

    def to_dict(self) -> Dict[str, Any]:
        result = {'matched_count': self._matched_count}
        if self._renames:
            result['renames'] = [{'extracted': m.extracted_name, 'original': m.original_name,
                                  'confidence': m.confidence, 'parent': m.parent}
                                 for m in self._renames]
        if self._new_epics:
            result['new_epics'] = [{'name': s.name, 'parent': s.parent} for s in self._new_epics]
        if self._new_sub_epics:
            result['new_sub_epics'] = [{'name': s.name, 'parent': s.parent} for s in self._new_sub_epics]
        if self._new_stories:
            result['new_stories'] = [{'name': s.name, 'parent': s.parent} for s in self._new_stories]
        if self._removed_epics:
            result['removed_epics'] = [{'name': s.name, 'parent': s.parent} for s in self._removed_epics]
        if self._removed_sub_epics:
            result['removed_sub_epics'] = [{'name': s.name, 'parent': s.parent} for s in self._removed_sub_epics]
        if self._moved_stories:
            result['moved_stories'] = [
                {'name': m.name, 'from_parent': m.from_parent, 'to_parent': m.to_parent}
                for m in self._moved_stories]
        if self._moved_sub_epics:
            result['moved_sub_epics'] = [
                {'name': m.name, 'from_parent': m.from_parent, 'to_parent': m.to_parent}
                for m in self._moved_sub_epics]
        if self._removed_stories:
            result['removed_stories'] = [{'name': s.name, 'parent': s.parent} for s in self._removed_stories]
        if self._large_deletions.missing_epics or self._large_deletions.missing_sub_epics:
            result['large_deletions'] = {
                'missing_epics': self._large_deletions.missing_epics,
                'missing_sub_epics': self._large_deletions.missing_sub_epics
            }
        if self._increment_changes:
            result['increment_changes'] = [
                {k: v for k, v in
                 [('name', c.name),
                  ('added', c.added if c.added else None),
                  ('removed', c.removed if c.removed else None)]
                 if v is not None}
                for c in self._increment_changes
            ]
        if self._increment_moves:
            result['increment_moves'] = [
                {'story': m.story,
                 'from': m.from_increment or '(unassigned)',
                 'to': m.to_increment or '(unassigned)'}
                for m in self._increment_moves
            ]
        if self._removed_increments:
            result['removed_increments'] = self._removed_increments
        if self._increment_order:
            result['increment_order'] = self._increment_order
        if self._ac_changes:
            result['ac_changes'] = []
            for ac in self._ac_changes:
                entry = {'story': ac.story_name}
                if ac.parent:
                    entry['parent'] = ac.parent
                if ac.added:
                    entry['added'] = ac.added
                if ac.removed:
                    entry['removed'] = ac.removed
                if ac.modified:
                    entry['modified'] = ac.modified
                if ac.reordered:
                    entry['reordered'] = ac.reordered
                result['ac_changes'].append(entry)
        if self._ac_moves:
            result['ac_moves'] = [
                {'ac_text': m.ac_text, 'from_story': m.from_story,
                 'to_story': m.to_story}
                for m in self._ac_moves
            ]
        if self._story_group_reorders:
            result['story_group_reorders'] = [
                {'parent': r.parent_sub_epic, 'story_names': r.story_names}
                for r in self._story_group_reorders
            ]
        if self._sub_epic_sibling_reorders:
            result['sub_epic_sibling_reorders'] = [
                {'parent': r.parent, 'sub_epic_names': r.sub_epic_names}
                for r in self._sub_epic_sibling_reorders
            ]
        if self._story_users_changes:
            result['story_users_changes'] = [
                {
                    'story': c.story_name,
                    'parent_sub_epic': c.parent_sub_epic,
                    'users': list(c.users),
                }
                for c in self._story_users_changes
            ]
        if not self.has_changes:
            result['status'] = 'no_changes'
        return result

    def save(self, file_path: Path):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(self.to_dict(), indent=2), encoding='utf-8')

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UpdateReport':
        report = cls()
        report._matched_count = data.get('matched_count', 0)
        for m in data.get('renames', []):
            report.add_rename(m['extracted'], m['original'], m['confidence'], m.get('parent', ''))
        for s in data.get('new_epics', []):
            report.add_new_epic(s['name'], s.get('parent', ''))
        for s in data.get('new_sub_epics', []):
            report.add_new_sub_epic(s['name'], s.get('parent', ''))
        for s in data.get('new_stories', []):
            report.add_new_story(s['name'], s.get('parent', ''))
        for m in data.get('moved_stories', []):
            report._moved_stories.append(
                StoryMove(name=m['name'],
                          from_parent=m.get('from_parent', ''),
                          to_parent=m.get('to_parent', '')))
        for m in data.get('moved_sub_epics', []):
            report._moved_sub_epics.append(
                SubEpicMove(name=m['name'],
                            from_parent=m.get('from_parent', ''),
                            to_parent=m.get('to_parent', '')))
        for s in data.get('removed_epics', []):
            report.add_removed_epic(s['name'], s.get('parent', ''))
        for s in data.get('removed_sub_epics', []):
            report.add_removed_sub_epic(s['name'], s.get('parent', ''))
        for s in data.get('removed_stories', []):
            report.add_removed_story(s['name'], s.get('parent', ''))
        large = data.get('large_deletions', {})
        for e in large.get('missing_epics', []):
            report.add_missing_epic(e)
        for se in large.get('missing_sub_epics', []):
            report.add_missing_sub_epic(se)
        for c in data.get('increment_changes', []):
            report._increment_changes.append(
                IncrementChange(
                    name=c['name'],
                    added=c.get('added', []),
                    removed=c.get('removed', [])))
        for m in data.get('increment_moves', []):
            from_inc = m.get('from', '')
            if from_inc == '(unassigned)':
                from_inc = ''
            to_inc = m.get('to', '')
            if to_inc == '(unassigned)':
                to_inc = ''
            report._increment_moves.append(
                IncrementMove(
                    story=m['story'],
                    from_increment=from_inc,
                    to_increment=to_inc))
        report._removed_increments = list(data.get('removed_increments', []))
        report._increment_order = list(data.get('increment_order', []))
        for ac in data.get('ac_changes', []):
            report._ac_changes.append(ACChange(
                story_name=ac['story'],
                parent=ac.get('parent', ''),
                added=ac.get('added', []),
                removed=ac.get('removed', []),
                modified=ac.get('modified', []),
                reordered=ac.get('reordered', [])))
        for m in data.get('ac_moves', []):
            report._ac_moves.append(ACMove(
                ac_text=m['ac_text'],
                from_story=m['from_story'],
                to_story=m['to_story']))
        for r in data.get('story_group_reorders', []):
            report.add_story_group_reorder(
                r['parent'], list(r.get('story_names', [])))
        for r in data.get('sub_epic_sibling_reorders', []):
            report.add_sub_epic_sibling_reorder(
                r['parent'], list(r.get('sub_epic_names', [])))
        for c in data.get('story_users_changes', []):
            report.add_story_users_change(
                c.get('story', ''),
                c.get('parent_sub_epic', ''),
                list(c.get('users', [])),
            )
        return report
