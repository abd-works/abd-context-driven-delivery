# Handoff ? Stories discovery iterate

## 1. Next session focus

Stories discovery iterate (markdown): continue grilling one slice at a time; next unlock still pending (skills vs thin-slice vs more character).

## 2. Resume in three lines

(a) Stage: **iterate** on Stories ? fidelity **discovery** ? format **markdown** ? session.path `sandbox` ? bout `discovery`.
(b) Last accepted: `story-map.md` has **Resolve Check** + **Build Character** only; overbuilt full-map dump was deleted; iterate tool hardened against whole-artifact ticks.
(c) Next: `/stories iterate` with `path=sandbox` `session=discovery` `fidelity=discovery` `format=markdown` ? ask **Question 9** (next unlock); do **not** generate until a concrete slice is unlocked.

## 3. Generator state

- Toolset: `context_tools.stories.stories:Stories`
- Fidelity / format: discovery / markdown
- Durable map: `sandbox/.context/story-map.md` (no thin-slice yet; no sketches in bout)
- Bout: `sandbox/.context/sessions/discovery/`
- Iterate contract (utilities/iterate): hard gate ? each tick writes ONLY the slice unlocked by last 2?3 answers; dumping a whole map/artifact is a DEFECT; stop and resume grilling after each tick

## 4. Grilling / skills state

- Grill answers: `sandbox/.context/sessions/discovery/grill-answers.md`
- Headings: Bout slug; Discovery map scope; Story naming authority; Overbuilt draft disposition; Restart; Keep prior decisions; First tick slice; Resolve Check activity shape; No sub-epic split; Next tick Create Character; Epic Build Character; Story source of truth; Build Character tick scope; Build Character stories this tick
- Suggested skills: `/stories` (iterate), `/grill-context` as needed, `/handoff` when pausing again

## 5. CDD progress

None (no cdd-sketch in this bout).

## 6. Artifacts to read

- `sandbox/.context/sessions/discovery/grill-answers.md`
- `sandbox/.context/sessions/discovery/session.md`
- `sandbox/.context/story-map.md`
- `sandbox/modules/checks/.context/module-context.md`
- `sandbox/modules/character/.context/module-context.md`
- `sandbox/modules/character/.context/character-segment.md` (large ? read in full before naming more character stories)
- `sandbox/modules/character/.context/abilities-segment.md` as needed
- `sandbox/stories/play-core-mechanics/story-context.md` (shipped names)
- `sandbox/.context/HeroesHandbook-index.md` ? **index mid-epic columns are stubs only**, not story inventory
- `utilities/iterate/iterate.py` ? iterate hard-gate instructions

## 7. Open questions / risks

- **Q9 unanswered:** next unlock ? (A) skills module, (B) thin-slice for stories on map, (C) more character-segment stories, (D) other
- Do not treat HeroesHandbook-index ?Suggested Mid-epic? lists as definitive stories
- Naming reconcile (play-core wins on overlap) still stands, but new stories must come from module segments/context
- Sub-epic structure / four-to-nine deferred (?revisit later?); single flat activity under each epic for now
- Scan of sandbox often merges unrelated workspace maps ? scope judgment to tick files
