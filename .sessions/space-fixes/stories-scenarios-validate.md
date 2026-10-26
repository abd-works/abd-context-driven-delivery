# Validate — stories / scenarios

**Artifacts:** `sandbox/space-battle/simulate-starfighter-dogfight/**/*_story.test.md` (13 walking-skeleton stories) and `examples/starfighters.examples.md`
**Date:** 2026-10-23 (second run, after fixes)
**Result:** 18 pass, 2 waived/n.a. All three failures from the first run are fixed (see "Fixed" below).

| Rule | Result | Evidence |
|---|---|---|
| `vocabulary-traces-to-domain-source` | pass | Every step uses the terms defined in `starfighters.examples.md` (Engagement, Arena, Heading, Speed, Activation, Range, Firing Arc, Hull). |
| `read-all-source-context-in-full` | pass | Each file's Evidence table points to the story-map decisions and the shared examples. |
| `do-not-invent-requirements` | waived | The user ruled on the story map that there are no given requirements; proposals stay. |
| `evidence-distinguishes-observed-inferred-and-intended` | pass | Every file labels its values intended and flags proposals (turn-order tiebreak, hit roll, edge stop, AI tactics, win condition). |
| `gwt-steps-trace-to-domain-operations` | pass | Each When maps to one operation: deploy, launch, order activations, commit orders, adjust throttle, maneuver, resolve movement, plan orders, fire, resolve shot, apply damage, destroy, determine victor. |
| `behavioral-and-system-observable-outcomes` | pass | Thens assert positions, headings, speeds, hull, activation order, rejection messages and engagement state. |
| `explore-full-interaction-surface` | pass | Each story covers its main flow plus rejection or edge cases: out of arena, occupied cell, missing side, out of turn, range, arc, speed cap, turn clip, heading wrap, arena edge, miss, last hull point, both outcomes. |
| `examples-trace-domain-model` | **fail** | `destroy_starfighter_story.test.md` asserts cell *(7,10)* is freed but never gives Black Two's position in Given. |
| `reconcile-live-immediately` | n.a. | Greenfield; no running product. |
| `flagged-writes-intended-gwt` | pass | The unconfirmed mechanics are written as intended GWT with **flagged** notes saying what is missing. |
| `scenario-names-continuation` | pass | Each main-flow Then names the next story in bold, ending at Determine Engagement Victor, which loops back to Order Starfighter Activations. |
| `given-only-what-the-system-checks` | pass | Givens hold only the speed, heading, position, hull or turn state the operation reads. |
| `given-names-complex-state-root-first` | **fail** | Adjust Throttle, Maneuver Starfighter, Resolve Starfighter Movement, Fire Laser Cannons, Resolve Shot Hit and Damage Hull start Given at the Starfighter. Starfighter is owned by the Engagement, so these should open with *Dogfight One* first, as Launch Engagement and Determine Engagement Victor do. |
| `but-marks-missing-state` | pass | But marks absent records: no starfighter deployed, no TIE fighter, no Pilot-flown starfighter, activation not finished, side destroyed. |
| `when-holds-the-operation` | **fail** | Fire Laser Cannons: the When is "**Red Five** fires", but the Pilot already chose the target in Commit Activation Orders and the Simulation Engine fires after movement. The actor in the When (and the map's "Pilot --> Fire Laser Cannons") should be the Simulation Engine, which makes it another system story. |
| `when-names-intent-not-interface-gesture` | pass | No buttons or gestures; every When names intent. |
| `expressive-system-interactions` | pass | System stories speak the engine's vocabulary (applies, resolves, rolls, orders). |
| `and-chaining` | pass | One Given/When/Then block each, continued with And; Backgrounds only where several scenarios share state. |
| `outline-requires-many-permutations` | pass | Outlines only where 4 data rows share one flow (activation order, throttle, maneuver, movement, shot hit); two-way cases are separate scenarios. |
| `plain-english-gwt-steps` | pass | Steps read as sentences with named actors and example names, not code identifiers. |
| `seed-prior-story-as-given` | pass | Later stories seed from earlier results (e.g. Damage Hull starts from hull values; Determine Victor starts from a destroyed starfighter) instead of replaying their Whens. |

## Fixed (second run passes)

1. `examples-trace-domain-model`: Destroy Starfighter's Given now places Black Two at *(7,10)*.
2. `given-names-complex-state-root-first`: Adjust Throttle, Maneuver Starfighter, Resolve Starfighter Movement, Fire Laser Cannons, Resolve Shot Hit and Damage Hull now open with *Dogfight One* in progress (Damage Hull through a Background shared by its two scenarios).
3. `when-holds-the-operation`: Fire Laser Cannons is a Simulation Engine system story in its scenarios and on the map, with the decision recorded in `story-map.md`.

The rows above that read **fail** are the first run's verdicts. All three now pass.

## Still open for the user (flagged in the files)

- What "fastest" means for activation order, and how ties break.
- Whether hits are random (proposed 1–100 roll vs range) or deterministic.
- Whether a starfighter stops at the arena edge and short of occupied cells.
