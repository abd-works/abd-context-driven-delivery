---
fidelity: [discovery]
artifact: [story-map]
format: md
---

# Story Map — Online Simulator

**Sources / context:** sandbox/mm3e/yaml/HeroesHandbook.md (Chapter 1: The Basics, lines 202–1554; Chapter 2: Secret Origins, lines 1556–2293). Evidence: observed tabletop rules in those chapters. The Simulator actor is intended: the user asked for an online simulator of those rules.

---

(E) Resolve Action
    (E) Resolve Trait Check
        (S) Player --> Roll Trait Check
        (S) Gamemaster --> Set Difficulty Class
        (S) Player --> Take Routine Check
        (S) Player --> Roll Nonroutine Check
        (S) Gamemaster --> Waive Trait Check
        (S) Player --> Roll Percentage Chance
        (S) Player --> Roll Attack Check
        (S) Player --> Roll Resistance Check
    (E) Contest Character
        (S) Player --> Roll Opposed Check
        (S) Gamemaster --> Pick Opposing Trait
        (S) Simulator --> Apply Routine Opposition
        (S) Simulator --> Compare Trait Rank
    (E) Modify Check
        (S) Gamemaster --> Apply Circumstance Modifier
        (S) Gamemaster --> Apply Tool Penalty
        (S) Player --> Lead Team Check
        (S) Player --> Assist Team Check
    (E) Take Round Action
        (S) Simulator --> Open Action Round
        (S) Player --> Take Standard Action
        (S) Player --> Take Move Action
        (S) Player --> Take Free Action
        (S) Player --> Take Reaction
    (E) Impose Condition
        (S) Simulator --> Apply Basic Condition
        (S) Simulator --> Apply Combined Condition
        (S) Simulator --> Remove Condition Part
        (S) Player --> Wake Sleeping Character
        (S) Player --> Stabilize Dying Character
        (S) Player --> Shake Entranced Character
        (S) Player --> Stand Prone Character
    (E) Use Extra Effort
        (S) Player --> Gain Extra Action
        (S) Player --> Gain Effort Bonus
        (S) Player --> Increase Effort Rank
        (S) Player --> Perform Power Stunt
        (S) Player --> Gain Extra Resistance Check
        (S) Player --> Retry Failed Effect
        (S) Simulator --> Apply Effort Fatigue
    (E) Spend Hero Point
        (S) Simulator --> Grant Session Hero Point
        (S) Player --> Edit Scene
        (S) Player --> Perform Heroic Feat
        (S) Player --> Improve Roll
        (S) Player --> Request Inspiration
        (S) Player --> Counter Effect
        (S) Player --> Recover Condition
        (S) Gamemaster --> Award Hero Point
        (S) Simulator --> Reset Hero Point
    (E) Convert Rank Measure
        (S) Simulator --> Convert Rank To Measure
        (S) Simulator --> Choose Next Higher Rank
        (S) Simulator --> Halve Negative Rank
        (S) Simulator --> Add Measure Value
(E) Create Hero
    (E) Frame Hero
        (S) Player --> Note Hero Concept
        (S) Gamemaster --> Set Series Guideline
        (S) Gamemaster --> Set Series Power Level
        (S) Simulator --> Grant Starting Power Point
        (S) Player --> Customize Hero Archetype
    (E) Spend Power Point
        (S) Player --> Buy Ability Rank
        (S) Player --> Buy Defense Bonus
        (S) Player --> Buy Skill Rank
        (S) Player --> Buy Advantage
        (S) Player --> Buy Power Effect
    (E) Limit Power Level
        (S) Simulator --> Limit Skill Modifier
        (S) Simulator --> Limit Attack Effect
        (S) Simulator --> Limit Defense Pair
        (S) Gamemaster --> Review Trait Disparity
    (E) Define Complication
        (S) Player --> Choose Motivation
        (S) Player --> Choose Other Complication
        (S) Player --> Change Complication
        (S) Gamemaster --> Cap Complication Count
    (E) Record Hero Detail
        (S) Player --> Name Hero
        (S) Player --> Choose Origin
        (S) Player --> Record Hero Age
        (S) Player --> Describe Costume
        (S) Player --> Record Alternate Identity
        (S) Player --> Record Hero Persona
    (E) Close Hero Design
        (S) Player --> Total Power Point
        (S) Player --> Adjust Trait Total
        (S) Gamemaster --> Approve Hero
        (S) Gamemaster --> Reallocate Power Point
        (S) Gamemaster --> Assign Nonplayer Trait
    (E) Advance Hero
        (S) Gamemaster --> Award Adventure Power Point
        (S) Player --> Save Power Point
        (S) Player --> Improve Hero Trait
        (S) Gamemaster --> Raise Series Power Level
        (S) Gamemaster --> Improve Nonplayer Challenge

---

## Scope boundary

**In scope:** Chapter 1 play loop the Simulator resolves, and Chapter 2 hero creation through advancement. A check result includes its degree and, on a natural 20, one extra degree of success. An attack result includes a natural 20 hit and a natural 1 miss. An opposed or comparison tie breaks by higher bonus, then by a d20 split at 10. Helper degrees on a team check become the leader’s modifier, capped at +5 and –2. A hero is a power-point budget at a series power level: ability ranks cost 2 points, defense bonuses cost 1, skill ranks cost 1 per two ranks, advantages cost 1 per advantage or rank, and a power costs ((base effect + extras − flaws) × rank) + flat modifiers. Power level caps skill modifiers at power level +10, attack-plus-effect and each defense pair at twice the power level, and an effect that allows a resistance check but no attack check at the power level. A hero starts with at least a Motivation and one other complication. Spent points equal the starting total before the Gamemaster approves. Earned points after play spend the same way; the series power level rises by 1 after about 15 more points.

**Out of scope this turn:** The Abilities, Skills, Advantages, Powers, Gadgets & Gear, and Action & Adventure chapters (trait catalogs and effect construction beyond the cost formula). The archetype stat blocks from line 2295 onward. The Quickstart Character Generator is cited at line 1585, and its procedure is not in this extract. Motivation-as-descriptor, motivation-as-origin, and origin-as-descriptor wait for the Powers chapter.

**Evidence**

- observed — HeroesHandbook.md lines 257–281 and 816–877: check = d20 + modifiers vs difficulty class; the Gamemaster sets the DC or waives the check; a natural 20 increases the degree of success by one.
- observed — lines 881–979 and 1038–1154: a routine check uses 10; a shortfall can still be rolled; every five full points over or under the DC adds a degree.
- observed — lines 202–213: a percentage is the die times 5.
- observed — lines 1102–1126: opposed checks compare results; the higher bonus, then a d20 split at 10, breaks a tie; routine opposition is modifier + 10; when no rule names the contest, the Gamemaster picks the trait; a comparison check compares ranks with no die.
- observed — lines 1195–1218: an attack check uses defense class, a natural 20 always hits, and a natural 1 always misses; a resistance check is d20 + defense vs generally 10 + rank.
- observed — lines 1156–1194: circumstance modifiers are ±2 or ±5; missing tools are –5, makeshift tools are –2, and the Gamemaster may forbid the attempt; team-check helpers roll against DC 10.
- observed — lines 1220–1252: a round is six seconds; one standard and one move (or a second move in place of the standard), free actions the Gamemaster allows, and reactions when circumstances call for them.
- observed — lines 1254–1425: basic conditions supersede lesser ones; a combined condition can lose one part; waking, stabilizing, shaking an entranced character, and standing from prone are their own checks or actions.
- observed — lines 1426–1489: extra effort is a free action once per turn; the next turn applies fatigue unless a hero point removes it.
- observed — lines 1467–1541: one hero point at the start of a session; spends are edit scene, heroic feat, improve roll, inspiration, instant counter, and recover; the Gamemaster awards more; unspent points reset next adventure.
- observed — lines 336–389: ranks map to measures; use the next higher listed rank; negative ranks halve; add the measures, not the ranks.
- observed — lines 1565–1653: the Gamemaster sets series guidelines and power level (often 10, from 5 to 20 or more); the player notes a concept or customizes a power level 10 archetype inside power points, power level, and approval; design steps are abilities, defenses, skills, advantages, powers, at least two complications, a power-point total, details, then Gamemaster approval.
- observed — lines 1655–1792 and 1674–1766: starting power points follow the table (15 at power level 1, 150 at 10, 300 at 20); the Gamemaster may vary that total; ability rank costs 2, defense rank costs 1, skill ranks cost 1 per 2, an advantage costs 1 per advantage or rank, and a power costs ((base effect cost + extras − flaws) × rank) + flat modifiers. Spent points stay put.
- observed — lines 1835–1877: skill modifier ≤ power level +10; attack bonus + effect rank ≤ twice the power level; an effect with a resistance check and no attack check has effect rank ≤ the power level; Dodge and Toughness, Parry and Toughness, and Fortitude and Will each total ≤ twice the power level. Trade-offs may unbalance a pair. A disparity of more than 50% is reviewed before approval.
- observed — lines 1879–1894 and 1335–1336: a non-player character is not held to the series power level and is not costed; effective power level comes from the highest offensive and defensive traits. Reallocation stays inside the power level, is usually a transformed condition, and cannot raise the power point total.
- observed — lines 1903–2117: at least a Motivation and one other complication; the listed motivations and the other complication kinds share that rule. Complications change, and the Gamemaster may cap how many stay in play. An injury or similar trouble is a complication when it causes trouble.
- observed — lines 1958–1972: a shared motivation can grant a circumstance bonus on an interaction check, and a strongly differing motivation a circumstance penalty, with Gamemaster permission. This is the same mechanic as Apply Circumstance Modifier. This section does not state the modifier size.
- observed — lines 2123–2259: code name, origin (accident, alien, endowment, experiment, mutant, training, and the Gamemaster may limit origins), age, costume (immune to the hero’s own powers at no point cost), alternate or public identity, personality, and goals.
- observed — lines 2261–2283: 1 power point per session, 2 for a hard challenge, none after a poor adventure, and the Gamemaster may vary the rate; unspent points can wait for a higher power level; spent points use the same trait costs inside the current power level; raise power level by 1 after another 15 points, and improve some non-player challenges to match.
- intended — Simulator stores and checks these totals. The Quickstart Character Generator is named at line 1585, and its tables are not in this extract.
