# Validate — stories / story_map

**Artifact:** `sandbox/space-battle/story-map.md`
**Date:** 2026-10-23 (second run, after fixes)
**Result:** 8 pass, 2 waived by user, 1 deferred

| Rule | Result | Evidence |
|---|---|---|
| `vocabulary-traces-to-domain-source` | pass (warn) | No domain model exists. Terms come from the Star Wars setting and stay consistent across nodes. |
| `read-all-source-context-in-full` | pass | The only source is the user request plus the recorded decisions; all are named under Sources and Decisions. |
| `do-not-invent-requirements` | waived | The user said they gave no requirements and the proposed stories stay. |
| `evidence-distinguishes-observed-inferred-and-intended` | waived | The user accepted the map-level evidence note. |
| `verb-noun-format` | pass | Fixed: "Take Damage" is now "Resolve Combat Damage" and "Fly AI Pilots" is now "Pilot AI Starfighters". Every other node was already verb–noun. |
| `story-name-captures-system-mechanic` | pass (warn) | "Maneuver Starfighter" is still broad for 2D; "Change Heading" would name the mechanic. |
| `four-to-nine-children` | pass | Root epic has 6 sub-epics. Sub-epics have 4, 6, 4, 4, 4 and 4 stories. |
| `story-scenarios-one-to-four` | deferred | No story has scenarios yet. The user agreed these come at the scenarios fidelity. |
| `branch-on-mechanical-uniqueness` | pass | Laser fire, torpedo launch and each damage step are separate mechanics. |
| `right-size-story-nodes` | pass | Ruling recorded in Decisions: Adjust Throttle, Maneuver Starfighter, Route Reactor Power and Lock Target are system stories. The Simulation Engine applies each with its own mechanics, separate from the Pilot's Commit Activation Orders. Warn: Resolve Shot Hit followed by the damage steps may still be one resolution with internal fan-out. |
| `behaviours-not-one-time-tasks` | pass | Every story is a repeatable interaction. |

## Remaining

- Add 1–4 scenarios per story at the scenarios fidelity.
