#!/usr/bin/env python3
"""Convert story-map.md tree syntax to story-graph.json format.

Usage:
    python md_story_map_to_story_graph.py <input-story-map.md> <output-story-graph.json>

Format expected:
    (E) Epic Name
        (E) Sub-Epic Name
            (S) actor --> Story Name
            opt (S) actor --> Optional Story Name
"""
import re
import json
import sys
from pathlib import Path


def clean_empty(node):
    """Recursively remove empty sub_epics/story_groups to keep JSON clean."""
    if isinstance(node, dict):
        for key in ('sub_epics', 'story_groups'):
            if key in node and not node[key]:
                del node[key]
        for v in list(node.values()):
            if isinstance(v, (dict, list)):
                clean_empty(v)
    elif isinstance(node, list):
        for item in node:
            clean_empty(item)


def parse(md_path: Path) -> dict:
    lines = md_path.read_text(encoding='utf-8').splitlines()

    epics = []
    # Stack holds (depth: int, node: dict) for E nodes only (never stories)
    stack: list[tuple[int, dict]] = []
    in_tree = False  # flip to True once we see the first (E) line

    for line in lines:
        stripped = line.lstrip()

        # Skip preamble (title, subtitle, ---) until we've entered the tree
        if not in_tree:
            if re.match(r'\(E\)', stripped):
                in_tree = True
            else:
                continue

        # Stop at the notes / gaps sections that follow the tree
        if stripped.startswith('## ') or stripped.startswith('# '):
            break

        if not stripped:
            continue

        # Strip inline comments before matching
        stripped = re.sub(r'\s*//.*$', '', stripped).strip()
        if not stripped:
            continue

        depth = (len(line) - len(line.lstrip())) // 4

        m_epic = re.match(r'\(E\)\s+(.+)', stripped)
        m_opt = re.match(r'opt\s+\(S\)\s+(.+?)\s+-->\s+(.+)', stripped)
        m_story = re.match(r'\(S\)\s+(.+?)\s+-->\s+(.+)', stripped)

        if m_epic:
            name = m_epic.group(1).strip()
            node: dict = {'name': name, 'sub_epics': [], 'story_groups': []}

            # Pop items at same or deeper depth to find the parent
            while stack and stack[-1][0] >= depth:
                stack.pop()

            if depth == 0:
                epics.append(node)
            elif stack:
                stack[-1][1].setdefault('sub_epics', []).append(node)

            stack.append((depth, node))

        elif m_story or m_opt:
            if m_opt:
                actor, name = m_opt.group(1), m_opt.group(2).strip()
            else:
                actor, name = m_story.group(1), m_story.group(2).strip()  # type: ignore[union-attr]

            story = {
                'name': name,
                'story_type': 'user',
                'users': [actor],
                'acceptance_criteria': [],
                'scenarios': [],
            }

            # Find parent (don't push stories onto the stack — they are leaves)
            while stack and stack[-1][0] >= depth:
                stack.pop()

            if stack:
                parent = stack[-1][1]
                sg_list = parent.setdefault('story_groups', [])
                if not sg_list:
                    sg_list.append({'stories': []})
                sg_list[0]['stories'].append(story)

    graph = {'epics': epics}
    clean_empty(graph)
    return graph


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: md_story_map_to_story_graph.py <input.md> <output.json>", file=sys.stderr)
        sys.exit(1)

    md_file = Path(sys.argv[1])
    out_file = Path(sys.argv[2])
    out_file.parent.mkdir(parents=True, exist_ok=True)

    graph = parse(md_file)
    out_file.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"Written {len(graph['epics'])} epics to {out_file}")
