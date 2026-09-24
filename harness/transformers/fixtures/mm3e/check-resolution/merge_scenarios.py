"""Merge specification-by-example scenarios into existing story-graph.json stories."""
import json
import sys
from pathlib import Path

SCRIPTS = Path(r"C:\dev\agilebydesign-skills\skills\story-driven-delivery\story-graph-ops\scripts")
sys.path.insert(0, str(SCRIPTS))

GRAPH_PATH = Path(__file__).parent / "story-graph.json"

# Import scenarios from the build script
from build_story_graph import (
    make_trait_check, grade_check_result, make_opposed_check,
    resolve_comparison_check, make_resistance_check, perform_routine_check,
    lead_team_check, apply_condition, supersede_condition,
    roll_resistance_ongoing, remove_condition_source_ends,
    roll_fortitude_dying, stabilize_dying_ally,
    translate_rank, derive_measurement,
)

SCENARIO_DATA = {
    "Make Trait Check": make_trait_check,
    "Grade Check Result by Degree": grade_check_result,
    "Make Opposed Check Against Opponent": make_opposed_check,
    "Resolve Comparison Check Without Roll": resolve_comparison_check,
    "Make Resistance Check Against Effect": make_resistance_check,
    "Perform Routine Check": perform_routine_check,
    "Lead Team Check with Helpers": lead_team_check,
    "Apply Condition to Character": apply_condition,
    "Supersede Condition in Chain": supersede_condition,
    "Roll Resistance Check Against Ongoing Effect to Remove Conditions": roll_resistance_ongoing,
    "Remove Condition When Source Effect Ends": remove_condition_source_ends,
    "Roll Fortitude Check to Stabilize While Dying": roll_fortitude_dying,
    "Stabilize Dying Ally with Treatment Check": stabilize_dying_ally,
    "Translate Trait Rank to Real-World Value": translate_rank,
    "Derive Measurement from Rank Formula": derive_measurement,
}


def find_and_merge(node, matched):
    """Recursively walk graph structure and merge scenarios into matching stories."""
    if isinstance(node, dict):
        if "stories" in node:
            for story in node["stories"]:
                name = story.get("name", "")
                if name in SCENARIO_DATA:
                    src = SCENARIO_DATA[name]
                    if "scenarios" in src:
                        story["scenarios"] = src["scenarios"]
                    if "scenario_outlines" in src:
                        story["scenario_outlines"] = src["scenario_outlines"]
                    matched.append(name)
        for key in ("epics", "sub_epics", "story_groups"):
            if key in node:
                for child in node[key]:
                    find_and_merge(child, matched)


with open(GRAPH_PATH, "r", encoding="utf-8") as f:
    graph = json.load(f)

matched = []
find_and_merge(graph, matched)

with open(GRAPH_PATH, "w", encoding="utf-8") as f:
    json.dump(graph, f, indent=2, ensure_ascii=False)

print(f"Merged scenarios into {len(matched)} stories:")
for name in matched:
    sc = len(SCENARIO_DATA[name].get("scenarios", []))
    so = len(SCENARIO_DATA[name].get("scenario_outlines", []))
    print(f"  {name} — {sc} scenarios, {so} outlines")

unmatched = set(SCENARIO_DATA.keys()) - set(matched)
if unmatched:
    print(f"\nWARNING: {len(unmatched)} stories not found in graph:")
    for name in unmatched:
        print(f"  {name}")
