# Manage Character Sheet

**Status:** specification

**Stories in scope:**
- *Create Character*
- *Update Ability Rank*

**Example factories (CE — via `manage-character-sheet-helper.js`):**
- `CharacterExampleFactory` — `loadHandbookSheetAtRankZero`
- `AbilityExampleFactory` — `loadStrengthAtRankZero`, `loadStrengthAtRankFive`, `loadStrengthAtRankNegOne`, `loadStrengthDebilitated`

**Scenarios (specification):**
- Create: handbook abilities at rank 0; all eight named abilities; initiative = Agility rank
- Update: rank 0→5; rank can drop below zero; debilitated when rank < -5

**Story vs tier (both stories):**
```bash
# Story (tier-neutral, fake)
node --test sandbox/play-core-mechanics/manage-character-sheet/create-character/create_character_story.js
node --test sandbox/play-core-mechanics/manage-character-sheet/update-ability-rank/update_ability_rank_story.js

# Isolated objects
node --test sandbox/play-core-mechanics/manage-character-sheet/create-character/create_character_spec.js
node --test sandbox/play-core-mechanics/manage-character-sheet/update-ability-rank/update_ability_rank_spec.js
```
- `*_story.js` — `story` / `scenario` / `given` / `when` / `then`, wired to **fake**
- `*_spec.js` — same scenarios, **isolated** objects
- `*_spec.{tier}.js` — other tiers (e.g. `production`)
- Shared GWT helper: `sandbox/play-core-mechanics/story-test.js`

**Context / notes:** Helper loads Character / Ability from factories. Character owns Abilities; mutate Ability.rank directly. PointTotals refresh deferred past Increment 1.
