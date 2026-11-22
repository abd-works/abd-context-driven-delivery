---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Produce Formal Artifacts

Story map: [Produce Formal Artifacts](../../../.context/story-map.md#e-produce-formal-artifacts). Session release-1-2-fixes.

**Evidence modes.** Every scenario below is *Observed*: it runs in `record-test-tiers-of-module/record_test_tiers_of_module_story.test.py`, and each names the spec that also runs it. The story was decided by the person on 2026-11-22, as change 6 of the defect analysis (`.sessions/release-1-2-fixes/exploratory-testing/defect-causes.md`, shortcoming 6: nothing says which tier a story needs).

### Domain terms

- ++module++ — a folder that holds a module card, `.context/module-context.md`, named by its path from the project.
- ++test tier++ — one of unit, server and web: every module's tests use unit, a module that publishes operations through a server also uses server, and a module that shows a page also uses web.
- ++record++ — `test_tiers` in the session's `session.json`: for each module, the test tool of each tier it uses.

> In steps: the bookshop's files are the examples below.

## Examples

### files of the bookshop project

| file | holds |
| --- | --- |
| ++shop/orders/.context/module-context.md++ | the module card of shop/orders, which makes the folder a module |
| ++shop/orders/orders_spec.py++ | a unit spec of shop/orders |
| ++shop/orders/orders.story.server.spec.py++ | the server tier of a story test of shop/orders |
| ++shop/orders/orders.story.ui.spec.ts++ | the browser tier of a story test of shop/orders |
| ++shop/orders/orders.spec.ts++ | a unit spec of shop/orders in TypeScript |
| ++story_tests/buy/pay.story.server.spec.py++ | the server tier of a story test, under no module's folder |

### test tools

| tier | language | test tool |
| --- | --- | --- |
| unit, server | Python | mamba |
| web | any | playwright |
| unit, server | TypeScript | not told by the file's name |

## Story: Record Test Tiers Of Module

### Evidence

| Source | Note |
|--------|------|
| The person, 2026-11-22 | "The tiers in use are tracked in session.json, for each module"; "the appropriate generate or render command fills it"; the server and web tiers are recorded only for modules that are apps |
| `cdd_guidance/practices/tdd/tdd.md`, Set up the tiers of a module | the setup advice, and the rules `module-tiers-recorded` and `story-tested-at-each-recorded-tier` |
| `analysis/guidance-gaps.md`, shortcoming 7 | story tests at the server tier: 13 defects, none caught; browser story tests: 13 |

#### Scenario: Record the unit tier as a module's specs are generated

Observed (`cdd_guidance/actions/generate/generate_spec.py`, `cdd_guidance/practices/tdd/module_tiers_spec.py`).

*Given* the bookshop session writes its BDD development specs under ++shop/orders++, a ++module++, with no ++test tier++ recorded
*When* the agent generates bdd-development
*Then* `session.json` records the unit tier of ++shop/orders++ with mamba
  *And* the reply says what the ++record++ holds

#### Scenario: Ask the agent to decide the tiers no test file shows

Observed (`generate_spec.py`, `module_tiers_spec.py`).

*Given* the bookshop session writes its BDD development specs under ++shop/orders++, which has no server or browser test
*When* the agent generates bdd-development
*Then* the reply says it cannot tell whether ++shop/orders++ publishes operations through a server or shows a page
  *And* the reply asks the agent to record each tier the module needs with `session.record_test_tier`

#### Scenario: Record the server and web tiers a module's story tests show

Observed (`module_tiers_spec.py`; `cdd_guidance/actions/render/render_spec.py` for a render's answer).

*Given* ++shop/orders++ holds ++shop/orders/orders.story.server.spec.py++ and ++shop/orders/orders.story.ui.spec.ts++, just rendered
*When* the render records what the saved files show
*Then* `session.json` records unit and server with mamba and web with playwright for ++shop/orders++
  *And* the render asks nothing more about the tiers of ++shop/orders++

#### Scenario: Record a tier the agent decided

Observed (`space/session/test_tiers_spec.py`).

*Given* `session.json` records the unit tier of ++shop/orders++ with mamba
*When* the agent records the web tier of ++shop/orders++ with playwright
*Then* the session answers ++shop/orders++ with unit mamba and web playwright
  *And* another reader of `session.json` reads the same tiers

### Edge conditions

Walked for `edge-conditions-walked`.

#### Scenario: Ask the agent for the module of a story test under no module's folder

Missing input: the module. Observed (`module_tiers_spec.py`).

*Given* ++story_tests/buy/pay.story.server.spec.py++, just rendered under `story_tests`, where no folder holds a module card
*When* the render records what the saved file shows
*Then* `session.json` records no ++module++
  *And* the render names ++story_tests/buy/pay.story.server.spec.py++ as a server tier test and asks the agent to record it for the module it tests

#### Scenario: Ask the agent for the test tool a file's name does not say

Missing input: the test tool. Observed (`module_tiers_spec.py`).

*Given* ++shop/orders/orders.spec.ts++, just rendered, a unit test in TypeScript
*When* the render records what the saved file shows
*Then* `session.json` records no tier for ++shop/orders++
  *And* the render asks the agent to record the unit tier with the test tool the module's tests run with

#### Scenario: Refuse a tier that is none of unit, server and web

Malformed input. Observed (`test_tiers_spec.py`).

*Given* the bookshop session with no ++test tier++ recorded
*When* the agent records the heavy tier of ++shop/orders++ with mamba
*Then* the agent is told heavy is no tier, and that the tiers are unit, server, web
  *And* `session.json` records no tier

#### Scenario: Refuse a tier recorded with no test tool

Empty input. Observed (the story test).

*Given* the bookshop session with no ++test tier++ recorded
*When* the agent records the server tier of ++shop/orders++ with an empty test tool
*Then* the agent is told to name the test tool of the server tier
  *And* `session.json` records no tier

#### Scenario: Keep the test tool an agent recorded

The same action repeated, and a duplicate of something that exists. Observed (`module_tiers_spec.py`, `test_tiers_spec.py`).

*Given* the agent recorded the unit tier of ++shop/orders++ with pytest
*When* a render saves ++shop/orders/orders_spec.py++ and records what it shows
*Then* the unit tier of ++shop/orders++ is still recorded with pytest

#### Scenario: Refuse a record that is wrongly shaped

The thing acted on changed since it was last seen: a person or another program edited `session.json`. Observed (`test_tiers_spec.py`, `module_tiers_spec.py`).

*Given* the bookshop's `session.json` holds its test tiers as a list of tiers
*When* the agent generates bdd-development
*Then* the generate is refused, naming `test_tiers` and what it holds, and is not read as no tiers chosen

#### Scenario: Report a recorded module whose folder is no longer there

The thing acted on gone since it was last seen. Observed (`module_tiers_spec.py`). The person's answer, 2026-11-22: generate reports it and leaves the removal to the person.

*Given* `session.json` records unit and server with mamba for shop/returns, whose folder was deleted
*When* the agent generates bdd-development
*Then* the reply names shop/returns as a module whose folder is no longer there, with the tiers recorded for it
  *And* the ++record++ of shop/returns is left as it is, for the person to remove or record again under the module's new folder

- **Two actors at once:** two chats recording a tier of one session at the same moment each keep their tier, because every change to `session.json` holds the file from its read to its write (Keep Every Change To Session Record, `space/session/session_record_processes_heavy_spec.py`).
- **An action interrupted partway:** does not apply, because a record is one write of `session.json`, and a generate stopped after it leaves a record that is true.
- **A dependency absent or wrong:** a fidelity working in no session records nothing and says nothing (`generate_spec.py`, "with no named session on the project").
- **An actor not allowed to act:** does not apply, because any chat working in a session may change its `session.json`.
