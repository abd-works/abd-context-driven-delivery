---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Deliver Work With Overlays

Story map: [Deliver Work With Overlays](../../../.context/story-map.md#e-deliver-work-with-overlays). Session tdd-practice.

**Evidence modes.** *Observed* scenarios hold for stack patterns today (`cdd_guidance/patterns/`, `harness/graph/pattern_overlays.py`, `harness/guidance_actions/guidance_actions.py`). *Intended* scenarios come from the person's request of 2026-11-14 and need an overlay that decorates chosen fidelities, such as ++tdd++, which does not exist yet. Each Intended scenario names the evidence still missing (`flagged-writes-intended-gwt`).

### Domain terms

- ++overlay++ — guidance laid on top of the practices, chosen for a session; today every overlay is a stack pattern registered with `PatternOverlays`.
- ++overlays word++ — the `overlays=` word a command names the overlays in, comma separated (`guidance_actions.py` `overlays_named`).
- ++decorated fidelity++ — a practice fidelity an overlay adds its guidance and rules to (Intended).
- ++overlay shared rules++ — the `## Shared rules` section of an overlay's markdown, such as `lern_domain_driven.md`.

> In steps: ++example++ names a row of a table below.

## Examples

### sessions

| session | overlays at start | kept in |
| --- | --- | --- |
| ++checkout-flow++ | set by each scenario's Given | `.sessions/checkout-flow/session.json` |

### overlays

| overlay | kind | evidence |
| --- | --- | --- |
| ++lern_domain_driven++ | stack pattern | Observed: `cdd_guidance/patterns/lern_domain_driven/` |
| ++mern_domain_driven++ | stack pattern | Observed: `cdd_guidance/patterns/mern_domain_driven/` |
| ++tdd++ | guidance overlay | Intended: requested 2026-11-14, not built |

### decorated fidelities of tdd

| practice | fidelity | instructions slug |
| --- | --- | --- |
| Clean Engineering | code | ++clean-engineering-code++ |
| Stories | acceptance_tests | ++stories-acceptance-tests++ |
| BDD | development | ++bdd-development++ |

### undecorated fidelity

| practice | fidelity | instructions slug |
| --- | --- | --- |
| Stories | story_map | ++stories-story-map++ |

## Story: Select Pattern Overlays For Session

### Evidence

| Source | Note |
|--------|------|
| User, 2026-11-14 | "select pattern overlay(s) for session" |
| `harness/guidance_actions/guidance_actions.py:66` | `overlays_named`: no word keeps the session's overlays; an empty word clears them |
| `harness/guidance_actions/guidance_actions.py:238` | an action run with the word chooses those overlays on the session first |

#### Scenario: Choose the overlays a command names

Observed.

*Given* checkout-flow's session overlays none
*When* Claude Code generates stories-acceptance-tests with overlays=lern_domain_driven,mern_domain_driven
*Then* checkout-flow's session overlays ++lern_domain_driven++ and ++mern_domain_driven++
  *And* checkout-flow's session.json keeps both among its overlays

#### Scenario: Keep the session's overlays when a command names none

Observed.

*Given* checkout-flow's session overlays ++lern_domain_driven++
*When* Claude Code generates stories-acceptance-tests with no overlays word
*Then* checkout-flow's session still overlays lern_domain_driven

#### Scenario: Clear the overlays with an empty overlays word

Observed.

*Given* checkout-flow's session overlays ++lern_domain_driven++
*When* Claude Code generates stories-acceptance-tests with overlays=
*Then* checkout-flow's session overlays none

#### Scenario: Choose a guidance overlay beside a stack pattern

Intended. Evidence still missing: no ++tdd++ overlay exists, and `PatternOverlays` registers only folders holding `practices/`.

*Given* checkout-flow's session overlays none
*When* Claude Code generates bdd-development with overlays=lern_domain_driven,tdd
*Then* checkout-flow's session overlays ++lern_domain_driven++ and ++tdd++

## Story: Decorate Practice Fidelity With Overlay Guidance

### Evidence

| Source | Note |
|--------|------|
| User, 2026-11-14 | "decorate guidelines with overlay guideline (eg TDD is added to CE, Stories, BDD at right fidelities)" |
| `harness/graph/pattern_overlays.py:26` | today a pattern decorates a practice only through `practices/<practice>/model` and `rules`, read by the graph |
| `cdd_guidance/practices/clean_engineering/rules/testing-approach.md` | the test shape ladder, which says `@bdd` and `@stories` refer to it |

#### Scenario: Decorate each fidelity the overlay names

Intended. Evidence still missing: an overlay has no way to name the fidelities it decorates.

*Given* the ++tdd++ overlay names ++clean-engineering-code++, ++stories-acceptance-tests++ and ++bdd-development++ as its decorated fidelities
*When* the cdd server registers the tdd overlay
*Then* clean-engineering-code, stories-acceptance-tests and bdd-development each list tdd among their overlays
  *And* the Agent goes on to Inject Overlay Guidance Into Fidelity Instructions

#### Scenario: Leave a fidelity the overlay does not name undecorated

Intended. Evidence still missing: as above.

*Given* the ++tdd++ overlay names ++clean-engineering-code++, ++stories-acceptance-tests++ and ++bdd-development++ as its decorated fidelities
*When* the cdd server registers the tdd overlay
*Then* ++stories-story-map++ lists no overlay

## Story: Inject Overlay Guidance Into Fidelity Instructions

### Evidence

| Source | Note |
|--------|------|
| User, 2026-11-14 | "inject overlay guidance" |
| `harness/guidance_actions/guidance_actions.py:667` | `inject_rules` injects the listed guidance's rules after an action, not an overlay's |

#### Scenario: Add a decorating overlay's guidance to the fidelity instructions

Intended. Evidence still missing: fidelity instructions hold the practice's words only.

*Given* checkout-flow's session overlays ++tdd++
*When* the Agent loads the ++stories-acceptance-tests++ instructions
*Then* the instructions hold the tdd overlay's guidance after the practice's rules
  *And* they name tdd as the overlay it comes from

#### Scenario: Leave out an overlay that does not decorate the fidelity

Intended. Evidence still missing: as above.

*Given* checkout-flow's session overlays ++tdd++
*When* the Agent loads the ++stories-story-map++ instructions
*Then* the instructions hold no tdd guidance

#### Scenario: Load the practice's words alone with no overlay chosen

Observed for every fidelity today.

*Given* checkout-flow's session overlays none
*When* the Agent loads the ++bdd-development++ instructions
*Then* the instructions hold BDD's guidance and rules and name no overlay

## Story: Generate With Overlay Rules

### Evidence

| Source | Note |
|--------|------|
| User, 2026-11-14 | "generate with overlay rules" |
| `cdd_guidance/actions/generate/generate.py:28` | Generate adds `_overlay_rules()` to its instructions |
| `harness/guidance_actions/guidance_actions.py:465` | each overlay's rules open with `## Pattern overlay: {name}` and hold its shared rules |

#### Scenario: Add each chosen overlay's shared rules when generating

Observed.

*Given* checkout-flow's session overlays ++lern_domain_driven++ and ++mern_domain_driven++
*When* the Agent generates stories-acceptance-tests
*Then* the instructions hold a Pattern overlay: lern_domain_driven section with its ++overlay shared rules++
  *And* they hold a Pattern overlay: mern_domain_driven section with its shared rules

#### Scenario: Generate with no overlay chosen

Observed.

*Given* checkout-flow's session overlays none
*When* the Agent generates stories-acceptance-tests
*Then* the instructions name no pattern overlay

#### Scenario: Add an overlay's rules only to a fidelity it decorates

Intended. Evidence still missing: `_overlay_rules` adds every chosen overlay to every fidelity.

*Given* checkout-flow's session overlays ++tdd++
*When* the Agent generates ++stories-story-map++
*Then* the instructions hold no tdd rules
*When* the Agent generates ++bdd-development++
*Then* the instructions hold the tdd overlay's rules

## Story: Validate With Overlay Rules

### Evidence

| Source | Note |
|--------|------|
| User, 2026-11-14 | "validate with overlay rules" |
| `cdd_guidance/actions/validate/validate.py:107` | Validate asks to judge the work against the overlaid patterns' rules too |
| `harness/guidance_actions/guidance_actions.py:445` | for paths it is given, the overlays the work was generated with; otherwise the session's |

#### Scenario: Judge the work against the overlays it was generated with

Observed.

*Given* checkout-flow's acceptance tests were generated with ++lern_domain_driven++
*When* the Agent validates stories-acceptance-tests on those tests
*Then* the report asks to judge the work against the lern_domain_driven shared rules too

#### Scenario: Validate with no overlay chosen

Observed.

*Given* checkout-flow's session overlays none
*When* the Agent validates stories-acceptance-tests
*Then* the report names no pattern overlay

#### Scenario: Judge an overlay's rules only on a fidelity it decorates

Intended. Evidence still missing: as for Generate With Overlay Rules.

*Given* checkout-flow's session overlays ++tdd++
*When* the Agent validates ++stories-story-map++
*Then* the report judges no tdd rules
*When* the Agent validates ++bdd-development++
*Then* the report judges the work against the tdd overlay's rules too
