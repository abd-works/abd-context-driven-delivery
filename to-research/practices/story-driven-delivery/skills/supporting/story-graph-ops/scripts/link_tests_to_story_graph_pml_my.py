"""
link_tests_to_story_graph_pml_my.py

Scans pml-my test files and links them to stories in story-graph.json:
  - Reads *-scenarios.ts files to extract GWT scenario definitions
  - Reads *-e2e.spec.ts, *-presentation.spec.tsx, *-application.spec.ts for describe/it structure
  - Matches describe('Story Name', ...) to graph stories by name
  - Adds `scenarios`, `test_files` to each matched story

Usage:
  python link_tests_to_story_graph_pml_my.py <tests-dir> <story-graph.json>

Exit codes:
  0  success
  1  error
"""

import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Matches:  // STORY: Story Name  -or-  // =====\n// STORY: Story Name
STORY_COMMENT_RE = re.compile(r"//\s*(?:=+\s*\n//\s*)?STORY:\s*(.+)")

# Matches describe('Story Name', ...) or describe("Story Name", ...)
DESCRIBE_RE = re.compile(r"""describe\(\s*['"`]([^'"`]+)['"`]""")

# Matches export const FOO_SCENARIOS = {
SCENARIO_BLOCK_START_RE = re.compile(r"export\s+const\s+(\w+_SCENARIOS)\s*=\s*\{")

# Matches scenario property blocks:  scenarioN: { name: '...', given: '...', ... }
SCENARIO_ENTRY_RE = re.compile(
    r"""scenario\w+\s*:\s*\{[^}]*?name\s*:\s*['"`]([^'"`]+)['"`]""",
    re.DOTALL,
)


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_scenarios_from_ts(ts_path: Path) -> dict[str, list[dict]]:
    """
    Returns { story_name: [ {name, given, when, then}, ...], ... }
    by parsing // STORY: comments and SCENARIOS blocks.
    """
    text = ts_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # Build a map: export const NAME -> story_name (from preceding // STORY: comment)
    const_to_story: dict[str, str] = {}
    for i, line in enumerate(lines):
        m = STORY_COMMENT_RE.search(line)
        if m:
            story_name = m.group(1).strip()
            # Look ahead for the next export const *_SCENARIOS (up to 30 lines)
            for j in range(i + 1, min(i + 30, len(lines))):
                bm = SCENARIO_BLOCK_START_RE.search(lines[j])
                if bm:
                    const_to_story[bm.group(1)] = story_name
                    break

    # Extract scenario names from each SCENARIOS block
    result: dict[str, list[dict]] = {}
    for m in SCENARIO_BLOCK_START_RE.finditer(text):
        const_name = m.group(1)
        start = m.end()
        # Extract the object body by counting braces
        depth = 1
        pos = start
        while pos < len(text) and depth > 0:
            if text[pos] == "{":
                depth += 1
            elif text[pos] == "}":
                depth -= 1
            pos += 1
        block = text[start:pos]

        scenarios: list[dict] = []
        # Parse individual scenario entries within the block
        entry_re = re.compile(
            r"""(scenario(?:Outline)?\w*)\s*:\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}""",
            re.DOTALL,
        )
        for entry_m in entry_re.finditer(block):
            entry_body = entry_m.group(2)
            sc: dict = {}

            def extract_str(key: str) -> str:
                km = re.search(
                    rf"""{key}\s*:\s*['"`]([^'"`]+)['"`]""", entry_body
                )
                return km.group(1) if km else ""

            def extract_array(key: str) -> list[str]:
                km = re.search(
                    rf"""{key}\s*:\s*\[(.*?)\]""", entry_body, re.DOTALL
                )
                if not km:
                    return []
                arr_text = km.group(1)
                return re.findall(r"""['"`]([^'"`]+)['"`]""", arr_text)

            sc["name"] = extract_str("name")
            # Accept either `given` or `background` as the Given step
            sc["given"] = extract_str("given") or extract_str("background")
            sc["when"] = extract_str("when")
            sc["then"] = extract_array("then")
            if sc["name"]:
                scenarios.append(sc)

        story_name = const_to_story.get(const_name)
        if story_name and scenarios:
            result[story_name] = scenarios

    return result


def parse_describes_from_spec(spec_path: Path) -> list[str]:
    """Returns list of describe('...') names found in a spec file."""
    text = spec_path.read_text(encoding="utf-8", errors="replace")
    return [m.group(1) for m in DESCRIBE_RE.finditer(text)]


# ---------------------------------------------------------------------------
# Graph traversal
# ---------------------------------------------------------------------------

def all_stories(epics: list) -> list[dict]:
    stories = []
    for epic in epics:
        for sub in epic.get("sub_epics", []):
            for sg in sub.get("story_groups", []):
                stories.extend(sg.get("stories", []))
            stories.extend(sub.get("stories", []))
        for sg in epic.get("story_groups", []):
            stories.extend(sg.get("stories", []))
        stories.extend(epic.get("stories", []))
    return stories


def fuzzy_match(graph_name: str, ac_name: str) -> bool:
    if graph_name == ac_name:
        return True
    rest = graph_name[len(ac_name):]
    return graph_name.startswith(ac_name) and (rest.startswith(" ") or rest.startswith("("))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <tests-dir> <story-graph.json>", file=sys.stderr)
        return 1

    tests_dir = Path(sys.argv[1])
    graph_path = Path(sys.argv[2])

    if not tests_dir.is_dir():
        print(f"ERROR: {tests_dir} is not a directory", file=sys.stderr)
        return 1
    if not graph_path.exists():
        print(f"ERROR: {graph_path} not found", file=sys.stderr)
        return 1

    # --- Load graph --------------------------------------------------------- #
    with graph_path.open(encoding="utf-8") as f:
        graph = json.load(f)

    stories = all_stories(graph.get("epics", []))
    story_by_name: dict[str, dict] = {s["name"]: s for s in stories}

    # --- Scan scenarios files ----------------------------------------------- #
    # story_name -> list of {name, given, when, then}
    story_scenarios: dict[str, list[dict]] = {}
    for sc_file in sorted(tests_dir.rglob("*-scenarios.ts")):
        parsed = parse_scenarios_from_ts(sc_file)
        story_scenarios.update(parsed)

    print(f"Parsed scenarios for {len(story_scenarios)} stories from scenarios.ts files")

    # --- Manual overrides for stories with no dedicated scenarios file ------- #
    # "Activate Customer" is covered implicitly by the Checkout and Pay step;
    # the confirmation of billing creation IS the Submit Payment success path.
    if "Activate Customer" not in story_scenarios:
        story_scenarios["Activate Customer"] = [
            {
                "name": "Successful payment activates the customer account",
                "given": "an Onboarding Customer who has completed the FAC payment iframe",
                "when": "POST /billing creates the billing account and POST /order places the order",
                "then": [
                    "metadata.verified is set to true",
                    "billing.id is present on the customer record",
                    "the route gate resolves to true and the customer can access /my routes",
                ],
            },
            {
                "name": "Failed payment leaves customer in Onboarding state",
                "given": "an Onboarding Customer attempting payment",
                "when": "the Midtier payment status is 'failed'",
                "then": [
                    "no billing account is created",
                    "metadata.verified remains false",
                    "the route gate resolves to false",
                ],
            },
        ]
        print("  Added manual scenarios for 'Activate Customer'")

    # --- Scan spec files and build per-story file list ---------------------- #
    # story_name -> list of relative paths
    story_test_files: dict[str, list[str]] = {}
    spec_extensions = ("*-e2e.spec.ts", "*-presentation.spec.tsx", "*-application.spec.ts")
    for pattern in spec_extensions:
        for spec_file in sorted(tests_dir.rglob(pattern)):
            rel = spec_file.relative_to(tests_dir.parent).as_posix()
            describes = parse_describes_from_spec(spec_file)
            for story_name in describes:
                # Try exact match first, then fuzzy
                matched_name = None
                if story_name in story_by_name:
                    matched_name = story_name
                else:
                    for gn in story_by_name:
                        if fuzzy_match(gn, story_name):
                            matched_name = gn
                            break
                if matched_name:
                    story_test_files.setdefault(matched_name, [])
                    if rel not in story_test_files[matched_name]:
                        story_test_files[matched_name].append(rel)

    print(f"Linked test files for {len(story_test_files)} stories from spec files")

    # --- Inject into graph -------------------------------------------------- #
    linked = 0
    for story in stories:
        name = story["name"]
        # Find scenario match (exact or fuzzy)
        sc_key = None
        if name in story_scenarios:
            sc_key = name
        else:
            for k in story_scenarios:
                if fuzzy_match(name, k):
                    sc_key = k
                    break

        tf_key = name if name in story_test_files else None
        if not tf_key:
            for k in story_test_files:
                if fuzzy_match(name, k):
                    tf_key = k
                    break

        if sc_key:
            story["scenarios"] = story_scenarios[sc_key]
            linked += 1
        if tf_key:
            story["test_files"] = story_test_files[tf_key]

    print(f"Injected scenarios for {linked}/{len(stories)} stories")

    # --- Write back --------------------------------------------------------- #
    with graph_path.open("w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)

    print(f"Updated {graph_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
