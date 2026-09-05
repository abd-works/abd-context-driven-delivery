import json, re, sys
from pathlib import Path

_H = re.compile(r'^(#{1,6})\s+(.*)')


def _level(line):
    m = _H.match(line.strip())
    return len(m.group(1)) if m else 0


def _name(line):
    m = _H.match(line.strip())
    return m.group(2).strip() if m else ""


def collect_ac_text(body_lines):
    """Return one string per numbered AC item found in body_lines."""
    ac_items, current, in_item = [], [], False
    for raw in body_lines:
        s = raw.strip()
        if re.match(r"^\d+\.\s+\*\*WHEN\*\*", s):
            if current:
                ac_items.append("\n".join(current).strip())
            current = [s]
            in_item = True
        elif in_item:
            if _level(s) or s == "---":
                break
            current.append(s)
    if current:
        ac_items.append("\n".join(current).strip())
    return [a for a in ac_items if a]


def parse_stories_from_ac(md_path):
    """
    Walk every heading (H1-H6) and check its direct body for AC items.
    Returns {story_name: [ac_string, ...]} for every heading that
    has at least one WHEN/THEN AC item directly below it.
    Works regardless of epic hierarchy depth.
    """
    lines = md_path.read_text(encoding="utf-8").splitlines()
    stories, i = {}, 0
    while i < len(lines):
        lv = _level(lines[i])
        if lv:
            name = _name(lines[i])
            i += 1
            body = []
            while i < len(lines) and not _level(lines[i]):
                body.append(lines[i])
                i += 1
            acs = collect_ac_text(body)
            if acs and name:
                stories[name] = acs
        else:
            i += 1
    return stories


def iter_stories(node):
    """
    Recursively yield every story dict from a graph node at any depth.
    A node is a story when it carries the `story_type` key.
    """
    if isinstance(node, list):
        for item in node:
            yield from iter_stories(item)
    elif isinstance(node, dict):
        if "story_type" in node:
            yield node
        else:
            for val in node.values():
                if isinstance(val, (dict, list)):
                    yield from iter_stories(val)


def fuzzy_match(graph_name, ac_name):
    if graph_name == ac_name:
        return True
    if not graph_name.startswith(ac_name):
        return False
    return graph_name[len(ac_name):len(ac_name) + 1] in (" ", "(")


def main():
    if len(sys.argv) != 3:
        print("Usage: {} <ac.md> <story-graph.json>".format(sys.argv[0]), file=sys.stderr)
        return 1
    ac_path = Path(sys.argv[1])
    graph_path = Path(sys.argv[2])
    if not ac_path.exists():
        print("ERROR: {} not found".format(ac_path), file=sys.stderr)
        return 1
    if not graph_path.exists():
        print("EPRROR: {} not found".format(graph_path), file=sys.stderr)
        return 1
    ac_stories = parse_stories_from_ac(ac_path)
    if not ac_stories:
        print("[FORMAT] NOHEADINGS WITH WHEN/THEN", file=sys.stderr)
        return 2
    print("Parsed {} story/AC blocks from {}".format(len(ac_stories), ac_path.name))
    with graph_path.open(encoding="utf-8") as f:
        graph = json.load(f)
    matched = 0
    for story in iter_stories(graph):
        for ac_name, ac_list in ac_stories.items():
            if fuzzy_match(story["name"], ac_name):
                story["acceptance_criteria"] = ac_list
                matched += 1
                break
    all_graph_names = [s["name"] for s in iter_stories(graph)]
    unmatched = [n for n in ac_stories if not any(fuzzy_match(gn, n) for gn in all_graph_names)]
    if unmatched:
        print("WARNING: {} unmatched AC blocks:".format(len(unmatched)))
        for n in unmatched:
            print("  - {!r}".format(n))
    with graph_path.open("w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)
    print("Injected ACs for {}/{} stories -> {}".format(matched, len(ac_stories), graph_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
