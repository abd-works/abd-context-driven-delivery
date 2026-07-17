# Grill Answers

### Module cut ? resolution and measurement

First module boundary from sandbox/mm3e - core mechanics.md is two peer modules: resolution (Check, modifiers, DC, degree of success/failure) and measurement (Rank, MeasurementsTable, rank?measure conversion and formulas). Character traits are out of scope for this slice; they appear only as external modifier sources at the resolution seam.

### resolve is an operation on Check

In the resolution sketch, resolve is a Check operation (verb), not a class. Modifier, DifficultyClass, and CheckResult are peer classes under the module seam ? not owned by resolve. Notation: trailing tokens after resolve are parameters; indented peers below ---- are associated/composed types.

### Modifier and DifficultyClass are interactions of resolve

resolve does not own Modifier or DifficultyClass. They are interactions shown as -> under the resolve operation: read modifier amounts, compare total to DifficultyClass. CheckResult remains the return type (peer class), not an interaction. Sketch updated in sandbox/.context/mm3e-core-mechanics-sketch.md.

### Pending ? Check vs Resolver name

User proposed resolver as the interaction host. Still open whether the public class is named Check (book term) or Resolver (role), and whether modifiers/DC are only resolve parameters or also held state on the class.

### One module per sketch file

Sketches split to one module per file under sandbox/.context/: mm3e-resolution-sketch.md and mm3e-measurement-sketch.md. Combined mm3e-core-mechanics-sketch.md removed. clean_engineering/sketch-template.md left unchanged.

### Modifier is amount only ? no trait/source noise

Modifier holds only amount. sourceLabel removed as noise. Resolution does not model traits or modifier provenance; callers supply numeric modifiers. One Modifier = one contribution; Check stacks many Modifiers.

### Single module core_mechanics ? measurement not standalone

Reversed the two-module cut. measurement is too small alone; Check/Modifier/DifficultyClass/CheckResult and Rank/MeasurementsTable/Measure live in one module core_mechanics. Sketch: sandbox/.context/mm3e-core-mechanics-sketch.md. Separate resolution/measurement sketch files removed. Q2 (cross-module dependency) is moot unless a later split returns.

### Modifier carries amount and trait

Restored trait on Modifier (replacing removed sourceLabel). One Modifier = amount + one trait reference. Still not modeling Ability/Skill/Advantage/Power as classes inside core_mechanics unless asked ? trait is the hook only.

### Check is against Trait; Modifier is amount + reason

Corrected model: Check always targets/uses a Trait (ability, skill, etc.). Modifier is only amount + reason (e.g. circumstance) ? not a trait reference. Opposed checks (HeroesHandbook opposed checks: other character's check result as DC) and comparison checks (rank vs rank, no die) were not modeled yet; flagged as TODO on Check in mm3e-core-mechanics-sketch.md.

### OpposedCheck extends Check ? DC from opposing roll

OpposedCheck subtypes Check with trait + opposingTrait. resolve keeps the same shape as Check; DifficultyClass/target is supplied by the opposing roll result per HeroesHandbook opposed checks. Sketch updated in mm3e-core-mechanics-sketch.md.

### OpposedCheck records only opposingTrait delta

OpposedCheck : Check adds opposingTrait only (inherits trait). Two traits in play; resolve same shape; DC from opposing roll via _opposing_roll.

### Trait holds Rank only

Trait carries rank as a Rank (same module). No kind/identity on Trait at core_mechanics seam; Ability/Skill subtypes deferred. Check.resolve only needs the numeric rank.

### Pending ? comparison checks

Still open on Check: comparison checks (Rank vs Rank, no die) from HeroesHandbook. Next grill branch if continuing.

### Comparison is optional flag on OpposedCheck.resolve

Comparison checks live on OpposedCheck, not a separate class. resolve keeps modifiers and opposingTrait; optional comparison=true selects rank-vs-rank with no die; otherwise DC comes from the opposing roll. Sketch updated in mm3e-core-mechanics-sketch.md.

### difficultyClass and opposingTrait are construction properties

Check.difficultyClass is set at construction, not passed to resolve. OpposedCheck.opposingTrait is likewise a construction property. resolve takes modifiers only (OpposedCheck also optional comparison). Sketch updated in mm3e-core-mechanics-sketch.md.

### OpposedCheck.resolve rolls opposition then super.resolve

OpposedCheck.resolve rolls the opposing check first, overrides difficultyClass with that result, then calls Check.resolve (super) against the overridden DC. User chose option-3 style override at resolve time. Comparison path still noted as optional on resolve; sketch comments preserved user spelling optonal.

### Pending ? comparison path vs opposing-then-super

Opposed non-comparison path is settled (opposing roll ? override DC ? super.resolve). Still open how comparison=true interacts with that sequence.

### Interactions name real collaborator operations

OpposedCheck uses -> opposingTrait.resolve then super.resolve; no underscore placeholder rolls. clean_engineering/sketch-template.md updated ? prefer collaborator.operation / super.operation; underscore privates only when no real call exists; bare -> ClassName is not an interaction.

### comparison=true skips roll and super ? rank vs rank

When OpposedCheck.resolve is called with comparison true, skip opposingTrait.resolve and super.resolve; compare trait.rank vs opposingTrait.rank directly. Non-comparison path unchanged: opposingTrait.resolve ? override difficultyClass ? super.resolve.

### OpposedCheck holds opposingCheck not opposingTrait

OpposedCheck construction property is opposingCheck (a Check built from the opposing trait). Interactions: opposingCheck.resolve for opposed path; opposingCheck.trait.rank for comparison. Trait stays rank-only.

### opposingTrait at construction; opposing Check created at resolve

Reversed holding opposingCheck. OpposedCheck keeps opposingTrait (construction) so comparison can use opposingTrait.rank. For non-comparison resolve: create a Check from opposingTrait at runtime, call resolve on it, override difficultyClass, then super.resolve. Opposing Check is not a stored property.

### CheckResult carries degree from resolve

CheckResult has succeeded, total, and degree. resolve computes degree (handbook graded check). Callers do not recompute margin.

### dieRoll is a Check property set by resolve

dieRoll stays on Check and is written by resolve after the d20 is rolled. From the player/user view the roll is part of the check outcome surface, not an encapsulated internal ? hide-inner-details does not apply to dieRoll here.

### Rank formulas plus liftCapacity via MeasurementsTable

Rank owns distanceFrom, timeFrom, throwDistance (rank arithmetic). liftCapacity is separate ? Strength rank to mass Measure via MeasurementsTable.lookup, not a +/- formula. Matches handbook lift = mass column for Strength rank.

### Keep Check / OpposedCheck names

Public seam keeps Check and OpposedCheck ? handbook language. Resolver naming rejected.

### core_mechanics is chapter ? check and measurement are modules

Handbook Core Mechanics is an organisational chapter folder (sandbox/core_mechanics/), not a module. Modules underneath: check (Check/OpposedCheck seam) and measurement (Rank/MeasurementsTable seam). check depends on measurement for Rank.

### Restart clean-modules ? sketches per module under chapter

Re-read sandbox/mm3e - core mechanics.md. Sketches split to core_mechanics/check/.context/check-sketch.md and core_mechanics/measurement/.context/measurement-sketch.md. Combined sandbox/.context/mm3e-core-mechanics-sketch.md is prior working copy; chapter is organisational only.

### Attack check stays out of checks module

Attack checks (nat 20 always hit / nat 1 always miss, defense class) do not belong in the checks module. Completing Ch1 checks covers core resolve rules only; attack lives with combat / Action & Adventure later. No AttackCheck subtype on the check seam.

### TeamCheck.assist returns Modifier for leader

Team checks belong in the checks module as TeamCheck.assist ? Modifier (option A). Helpers resolve vs DC 10; degrees map to +2/+5/?2 circumstance for the leader?s resolve. Attack stays out.

### routine and routineOpposition are resolve flags

Option A: Check.resolve(modifiers, routine=False); OpposedCheck.resolve also routineOpposition=False (with comparison). Modes of this resolution, not construction properties or subtypes. Construction stays trait / difficultyClass / opposingTrait.

### TeamCheck addHelper ? helper owns trait

TeamCheck uses addHelper(helper); assist pulls trait from each helper (helper owns the trait). TeamCheck does not store bare Trait lists. Maps to assist ? Modifier for the leader after helper checks vs DC 10.

### TeamCheck helper is external (Character later)

TeamCheck.addHelper(helper) takes an external object that owns trait (in reality a Character). No Helper class defined in the checks module. assist pulls helper.trait to build ephemeral helper Checks vs DC 10 ? Modifier for the leader.

### Character before condition

Next module is character, not condition. Conditions affect a character and have no meaning without one ? condition depends on character as host. Aligns with TeamCheck helpers being external objects (Character) that own trait.

### Character + Abilities one module; Skills separate

Character and Abilities share one module (character). Skills is a peer module later ? Skills chapter is large enough for its own seam. Matches prior TeamCheck helper expectation (external Character owns trait) and keeps ability ranks inside the character boundary. Advantages/Powers remain out of this slice.

### Character + Abilities one module; Skills separate

Confirmed: Character and Abilities share one module (character). Skills is a separate peer module later ? Skills chapter is large enough for its own seam. Advantages/Powers out of this slice. Next open: Ability vs checks.Trait (Q2 unanswered).

### Character sketch saved under module folder

In-progress modules sketch saved at sandbox/character/.context/character-sketch.md (same convention as checks/.context/check-sketch.md). Locked so far: character+abilities one module; skills separate later. Q2 still open ? Ability vs checks.Trait. Resume grill from that question.

### Ability subtypes Trait

Ability is a subtype of checks.Trait. Ability adds ability-specific rules (absent, debilitated, buy/reduce ranks); Check still consumes Trait. Character exposes abilities (later skills) as traits for TeamCheck helpers and Check construction. Sketch: sandbox/character/.context/character-sketch.md.

### Defenses live in character module

Defenses (Dodge, Parry, Fortitude, Toughness, Will) and initiative belong in the character module now ? derived from abilities plus bought ranks. Combat later consumes defense ranks; it does not own them. Toughness buy rules (advantages/powers only) remain a TODO on the Defense seam. Sketch: sandbox/character/.context/character-sketch.md.

### Defense subtypes Trait

Defense is a subtype of checks.Trait, same as Ability. Resistance checks and defense-class targeting use Defense as Trait. Active-defense rules (vulnerable/defenseless on Dodge/Parry) and Toughness buy limits are Defense deltas, not Trait noise. Sketch: sandbox/character/.context/character-sketch.md.

### Character named accessors plus iterable collections

Character exposes named accessors (strength, dodge, ?) and iterable collections for all abilities / all defenses. Named path for call sites; collections for PP totals and power-level scans. Sketch: sandbox/character/.context/character-sketch.md.

### Abilities and defenses are named iterable collections

Revised Q5: Character does not expose strength/dodge as top-level properties. Callers use character.abilities.strength and character.defenses.dodge. Abilities and Defenses collections are both iterable and property-accessible by handbook name. Sketch: sandbox/character/.context/character-sketch.md.

### Sketch does not enumerate handbook ability names

Do not list strength/stamina/? as separate sketch properties under Abilities. Abilities/Defenses are named+iterable collections; handbook names are the property keys, not model elements to expand in the sketch. Sketch: sandbox/character/.context/character-sketch.md.

### Absent and debilitated on Ability; enhanced deferred

User proceeded with recommended Q6: Ability models absent and debilitated now. Enhanced ability ranks wait for the Powers module (nullify/stunts). Sketch: sandbox/character/.context/character-sketch.md.

### Defense rank computed from linkedAbility plus boughtRanks

Defense holds linkedAbility and boughtRanks; rank is computed (ability rank + bought). Toughness cannot take boughtRanks via power points ? advantages/powers only. Ability changes flow through the link; no sync step. Sketch: sandbox/character/.context/character-sketch.md.

### Point totals aggregate from trait containers

Power points / power level is not a heavy spend engine. A simple totals holder reads point totals by aggregating known containers (abilities, defenses, later skills, powers, etc.). Containers own their costs; totals just sum. Character exposes the containers; PointTotals (name TBD) reads them. Sketch: sandbox/character/.context/character-sketch.md.

### PointTotals is a sourced collection with total property

PointTotals is a collection of per-source point totals (abilities, defenses, skills, powers, ?). Exposes a total property with invariant total == sum of entries. Sketch: sandbox/character/.context/character-sketch.md.

### PointTotals aggregates Point entries

PointTotals is a collection of Point. Each Point has source and amount. PointTotals.total is a property with invariant equal to the sum of Point.amount. Sketch: sandbox/character/.context/character-sketch.md.

### Ability.debilitated is a property

debilitated is a property on Ability (like absent), not a comment. True when rank < -5; handbook collapse/dying effects hang off that. Sketch: sandbox/character/.context/character-sketch.md.

### Rank mutation plus PointTotals refresh

No buy/reduce ops on the seam. Mutate Ability.rank and Defense.boughtRanks; PointTotals refreshes from containers so total tracks costs. Sketch: sandbox/character/.context/character-sketch.md.

### PL and active defenses deferred; generate modules

On generate: skip PL checks this slice; active defenses (vulnerable/defenseless) deferred to conditions/combat. Proceed to modules-fidelity generate from sandbox/character/.context/character-sketch.md.

### Character modules fidelity generated

Generated sandbox/character/ from character-sketch.md: module-context.md plus stubs Character, Abilities, Defenses, Ability, Defense, PointTotals, Point. PL checks and active defenses deferred. Skills remains a later peer module.

### Character modules fidelity generated

Generated sandbox/character/ from character-sketch.md: module-context.md plus stubs Character, Abilities, Defenses, Ability, Defense, PointTotals, Point. PL checks and active defenses deferred. Skills remains a later peer module.

### cohesive-file standard ? class family in one file

Merged Ability+Abilities into abilities.py, Defense+Defenses into defenses.py, Point+PointTotals into point_totals.py. Clean Engineering now requires cohesive-file (class family per file, not one class per file) in clean_engineering.md, concepts.md, modules/code fidelities, Python template, and sketch-template.

### One stories map spanning checks and character

One StoryMap under sandbox with a single epic and two sub-epics (Resolve Checks + Manage Character Sheet). Vertical thin-slices may cut across both modules. Not separate maps per module folder.

### Increment 1 is hero resolves an ability check

First thin slice is vertical across both sub-epics - Manage Character Sheet exposes an Ability as Trait, Resolve Checks runs Check.resolve and surfaces die_roll / CheckResult (succeeded, total, degree). Object-level Check BDD in checks/check_spec.py stays; Stories acceptance sits above the Character-Trait seam.

### Increment 1 has four confirming stories

Spine is Create Character ? Display Abilities ? Update Ability Rank ? Resolve Ability Check. More than two stories; sheet lifecycle before the check. Names stay verb-noun; Player actor.

### Increment 1 Update Ability Rank is rank-only

Update Ability Rank asserts Ability.rank only. PointTotals refresh / spend visibility stays in approx for a later story. Increment 1 stays sheet lifecycle then Resolve Ability Check.

### No fidelity markers on sketch lines

Do not tag sketch lines with <-d / <-e / <-s. Fidelity is what is filled (structure vs main-flow vs variations), not per-line markers. Template and stories-sketch updated.

### Create Character starts all abilities at rank 0

Create Character establishes all eight handbook Abilities at rank 0. Update Ability Rank is what changes ranks before Resolve Ability Check. No initial rank map or PL array in Increment 1.

### Actor is Player not Hero

Increment 1 stories use Player as actor. Hero/Character is the domain object on the sheet, not the actor metadata. Story names stay verb-noun without the actor.

### Drop Display Abilities as a story

Display Abilities removed from Increment 1 ? no UI; listing ranks is not a separate story. Spine is Create Character ? Update Ability Rank ? Resolve Ability Check. Ability names/ranks appear as Given/Then on those stories when needed.

### Discovery map names four stories per sub-epic

Named Refresh Point Totals and Update Defense Ranks under Manage Character Sheet; Resolve Opposed Check, Resolve Routine Check, Assist Team Check under Resolve Checks. Increment 1 still only Create Character, Update Ability Rank, Resolve Ability Check. Exploration py generated for Increment 1 stories only. Epic still has two sub-epics (four-to-nine error until a later grill adds more activities).

