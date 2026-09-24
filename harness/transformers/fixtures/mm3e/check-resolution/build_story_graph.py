"""Build story-graph.json for check-resolution from specification-by-example artifacts."""
import json
import sys
from pathlib import Path

SCRIPTS = Path(r"C:\dev\agilebydesign-skills\skills\story-driven-delivery\story-graph-ops\scripts")
sys.path.insert(0, str(SCRIPTS))

OUTPUT = Path(__file__).parent / "story-graph.json"


def scenario(name: str, background: list, steps: list) -> dict:
    return {"name": name, "background": background, "steps": steps}


def scenario_outline(name: str, background: list, steps: list, examples: list) -> dict:
    return {"name": name, "background": background, "steps": steps, "examples": examples}


def example_table(columns: list, rows: list) -> dict:
    return {"columns": columns, "rows": rows}


def story(name: str, story_type: str, scenarios=None, scenario_outlines=None) -> dict:
    d = {"name": name, "story_type": story_type}
    if scenarios:
        d["scenarios"] = scenarios
    if scenario_outlines:
        d["scenario_outlines"] = scenario_outlines
    return d


# --- Plain Scenarios (from specification-by-example.md) ---

make_trait_check = story("Make Trait Check", "user", scenarios=[
    scenario(
        "Trait Check succeeds when Roll Total meets Difficulty Class",
        [],
        [
            'Given a **Character** *Kara* with a **Trait** *Athletics* at **purchasedRank** *6*',
            'And no **Circumstance Modifier** applies',
            'When *Kara* makes a **Check** with **Trait** *Athletics* against **DifficultyClass** *15*',
            'And the **d20** result is *12*',
            'Then the **CheckResult** has **rollTotal** *18*',
            'And the **CheckResult** has **isSuccess** *true*',
            'And the **margin** is *3*',
        ]
    ),
    scenario(
        "Trait Check fails when Roll Total is below Difficulty Class",
        [],
        [
            'Given a **Character** *Kara* with a **Trait** *Athletics* at **purchasedRank** *6*',
            'And no **Circumstance Modifier** applies',
            'When *Kara* makes a **Check** with **Trait** *Athletics* against **DifficultyClass** *15*',
            'And the **d20** result is *4*',
            'Then the **CheckResult** has **rollTotal** *10*',
            'And the **CheckResult** has **isSuccess** *false*',
            'And the **margin** is *-5*',
        ]
    ),
    scenario(
        "Circumstance Modifiers are added to Roll Total before comparison",
        [],
        [
            'Given a **Character** *Kara* with a **Trait** *Athletics* at **purchasedRank** *6*',
            'And a minor favorable **Circumstance Modifier** of *+2* applies',
            'When *Kara* makes a **Check** with **Trait** *Athletics* against **DifficultyClass** *15*',
            'And the **d20** result is *6*',
            'Then the **CheckResult** has **rollTotal** *14* (6 + 6 + 2)',
            'And the **CheckResult** has **isSuccess** *false*',
        ]
    ),
    scenario(
        "Major circumstance penalty from missing tools imposes minus five",
        [],
        [
            'Given a **Character** *Kara* with a **Trait** *Technology* at **purchasedRank** *8*',
            'And the required tools for the task are missing',
            'And a **Circumstance Modifier** of *-5* applies',
            'When *Kara* makes a **Check** with **Trait** *Technology* against **DifficultyClass** *15*',
            'And the **d20** result is *10*',
            'Then the **CheckResult** has **rollTotal** *13* (8 + 10 − 5)',
            'And the **CheckResult** has **isSuccess** *false*',
        ]
    ),
    scenario(
        "Makeshift tools reduce missing-tool penalty to minus two",
        [],
        [
            'Given a **Character** *Kara* with a **Trait** *Technology* at **purchasedRank** *8*',
            'And makeshift tools are available',
            'And a **Circumstance Modifier** of *-2* applies',
            'When *Kara* makes a **Check** with **Trait** *Technology* against **DifficultyClass** *15*',
            'And the **d20** result is *10*',
            'Then the **CheckResult** has **rollTotal** *16* (8 + 10 − 2)',
            'And the **CheckResult** has **isSuccess** *true*',
        ]
    ),
    scenario(
        "Natural 20 grants Critical Success increasing degree by one",
        [],
        [
            'Given a **Character** *Kara* with a **Trait** *Athletics* at **purchasedRank** *4*',
            'When *Kara* makes a **Check** with **Trait** *Athletics* against **DifficultyClass** *25*',
            'And the **d20** result is *20*',
            'Then the **CheckResult** has **rollTotal** *24*',
            'And the **CheckResult** has **isCritical** *true*',
            'And the degree of success is increased by one after normal calculation',
        ]
    ),
])

make_opposed_check = story("Make Opposed Check Against Opponent", "user", scenarios=[
    scenario(
        "Active Character wins when their Roll Total is higher",
        [],
        [
            'Given a **Character** *Vex* with a **Trait** *Deception* at **purchasedRank** *8*',
            'And an **Opposing Character** *Nyx* with a **Trait** *Insight* at **purchasedRank** *6*',
            'And an **OpposedCheck** is created with **isPassive** *false*',
            'When *Vex* and *Nyx* each resolve their **Check**',
            'And *Vex* rolls a **d20** result of *14* for **rollTotal** *22*',
            'And *Nyx* rolls a **d20** result of *11* for **rollTotal** *17*',
            'Then the **CheckResult** for the **Active Character** *Vex* has **isSuccess** *true*',
            'And the **margin** is *5*',
        ]
    ),
    scenario(
        "Tie resolved by higher Trait effectiveRank",
        [],
        [
            'Given a **Character** *Vex* with a **Trait** *Deception* at **purchasedRank** *8*',
            'And an **Opposing Character** *Nyx* with a **Trait** *Insight* at **purchasedRank** *6*',
            'And an **OpposedCheck** is created with **isPassive** *false*',
            'When both characters achieve the same **rollTotal** *18*',
            'Then the win is awarded to **Character** *Vex* who has the higher **effectiveRank** *8*',
        ]
    ),
    scenario(
        "Tie-Break Roll resolves equal Roll Totals and equal bonuses",
        [],
        [
            'Given a **Character** *Vex* with a **Trait** *Deception* at **purchasedRank** *7*',
            'And an **Opposing Character** *Nyx* with a **Trait** *Insight* at **purchasedRank** *7*',
            'And an **OpposedCheck** is created with **isPassive** *false*',
            'When both characters achieve the same **rollTotal** *19*',
            'And both have **effectiveRank** *7*',
            'Then a **Tie-Break Roll** is made on a **d20**',
            'And result *1–10* awards the win to the **Active Character** *Vex*',
            'And result *11–20* awards the win to the **Opposing Character** *Nyx*',
        ]
    ),
    scenario(
        "Passive Opposition sets DC to opponent modifier plus ten",
        [],
        [
            'Given a **Character** *Vex* with a **Trait** *Stealth* at **purchasedRank** *8*',
            'And an **Opposing Character** *Guard* with a **Trait** *Perception* at **purchasedRank** *5*',
            'And an **OpposedCheck** is created with **isPassive** *true*',
            'When *Vex* makes a **Check** against **DifficultyClass** *15* (opponent effectiveRank 5 + 10)',
            'And *Vex* rolls a **d20** result of *9* for **rollTotal** *17*',
            'Then the **CheckResult** has **isSuccess** *true*',
            'And the **Opposing Character** *Guard* does not roll',
        ]
    ),
])

resolve_comparison_check = story("Resolve Comparison Check Without Roll", "system", scenarios=[
    scenario(
        "Higher Rank wins deterministically without rolling",
        [],
        [
            'Given a **Character** *Atlas* with a **Trait** *Strength* at **purchasedRank** *10*',
            'And a **Character** *Piper* with a **Trait** *Strength* at **purchasedRank** *7*',
            'When a **Comparison Check** is made between *Atlas* and *Piper* on **Trait** *Strength*',
            'Then *Atlas* wins with the higher **effectiveRank** *10*',
            'And no **d20** is rolled',
            'And no **Circumstance Modifier** is involved',
        ]
    ),
    scenario(
        "Equal Ranks result in a tie with no winner",
        [],
        [
            'Given a **Character** *Atlas* with a **Trait** *Strength* at **purchasedRank** *8*',
            'And a **Character** *Piper* with a **Trait** *Strength* at **purchasedRank** *8*',
            'When a **Comparison Check** is made between *Atlas* and *Piper* on **Trait** *Strength*',
            'Then the system reports a tie with no winner determined',
        ]
    ),
    scenario(
        "Higher Rank gains priority advantage with no degree produced",
        [],
        [
            'Given a **Character** *Swift* with a **Trait** *Agility* at **purchasedRank** *9*',
            'And a **Character** *Brick* with a **Trait** *Agility* at **purchasedRank** *6*',
            'When a **Comparison Check** is used to determine priority between *Swift* and *Brick*',
            'Then *Swift* proceeds first with the higher **effectiveRank** *9*',
            'And no **degree** of success or failure is produced',
        ]
    ),
])

make_resistance_check = story("Make Resistance Check Against Effect", "user", scenarios=[
    scenario("Resistance Check succeeds and no conditions are applied", [], [
        'Given a **Character** *Kara* with a **Trait** *Toughness* at **purchasedRank** *8*',
        'And an **Effect** *Fire Blast* with **rank** *6* producing **effectDc** *16*',
        'And an **AppliedEffect** links *Fire Blast* to *Kara*',
        'When *Kara* resolves a **Resistance Check** with **Trait** *Toughness* against **DifficultyClass** *16*',
        'And the **d20** result is *12* for **rollTotal** *20*',
        'Then the **GradedCheckResult** has **isSuccess** *true*',
        'And the **AppliedEffect** calls **end()**',
        'And no **Condition** is applied to *Kara*',
    ]),
    scenario("Resistance Check fails and condition imposed per degree of failure", [], [
        'Given a **Character** *Kara* with a **Trait** *Toughness* at **purchasedRank** *8*',
        'And an **Effect** *Fire Blast* with **rank** *6* producing **effectDc** *16*',
        'And the **Effect** maps *1 degree of failure* to **Condition** *Dazed*',
        'And an **AppliedEffect** links *Fire Blast* to *Kara*',
        'When *Kara* resolves a **Resistance Check** with **Trait** *Toughness* against **DifficultyClass** *16*',
        'And the **d20** result is *5* for **rollTotal** *13*',
        'Then the **GradedCheckResult** has **isSuccess** *false*',
        'And the **margin** is *-3* producing **degree** *1* of failure',
        'And **Condition** *Dazed* is applied to *Kara* via **ImposedConditions.applyCondition()**',
        'And the **ConditionSource** identity is *Fire Blast*',
    ]),
    scenario("Same-source more severe condition replaces less severe", [], [
        'Given a **Character** *Kara* with **ImposedConditions** containing active **Condition** *Dazed* from **ConditionSource** *Fire Blast*',
        'And an **Effect** *Fire Blast* with **rank** *6* producing **effectDc** *16*',
        'And the **Effect** maps *2 degrees of failure* to **Condition** *Stunned*',
        'And **Condition** *Stunned* has **supersedes** *Dazed*',
        'When *Kara* is hit again and resolves a **Resistance Check** with **rollTotal** *6* against **DifficultyClass** *16*',
        'Then the **GradedCheckResult** has **degree** *2* of failure',
        'And **Condition** *Stunned* becomes active on *Kara*',
        'And **Condition** *Dazed* from **ConditionSource** *Fire Blast* is removed',
        'And on recovery from *Stunned*, that source\'s conditions are cleared',
    ]),
    scenario("Same-source less severe condition does not change existing", [], [
        'Given a **Character** *Kara* with **ImposedConditions** containing active **Condition** *Stunned* from **ConditionSource** *Fire Blast*',
        'And an **Effect** *Fire Blast* with **rank** *6*',
        'And the **Effect** maps *1 degree of failure* to **Condition** *Dazed*',
        'And **Condition** *Dazed* has **supersededBy** *Stunned*',
        'When *Kara* is hit again and resolves a **Resistance Check** with *1 degree of failure*',
        'Then no change is made — **Condition** *Stunned* remains active',
        'And **Condition** *Dazed* is not added',
    ]),
    scenario("Different-source less severe condition is added as inactive", [], [
        'Given a **Character** *Kara* with **ImposedConditions** containing active **Condition** *Stunned* from **ConditionSource** *Fire Blast*',
        'And a different **Effect** *Ice Grip* with **rank** *4* producing **effectDc** *14*',
        'And the **Effect** maps *1 degree of failure* to **Condition** *Dazed*',
        'When *Kara* resolves a **Resistance Check** against **Effect** *Ice Grip* with *1 degree of failure*',
        'Then **Condition** *Dazed* is added to **ImposedConditions** with **ConditionSource** *Ice Grip*',
        'And the **ImposedCondition** has **isActive** *false*',
        'And the **ImposedCondition** has **blockingCondition** pointing to the *Stunned* imposed condition',
        'And if *Stunned* from *Fire Blast* is later removed, *Dazed* from *Ice Grip* becomes active',
    ]),
    scenario("Natural 20 on Resistance Check converts one degree of failure to success", [], [
        'Given a **Character** *Kara* with a **Trait** *Will* at **purchasedRank** *4*',
        'And an **Effect** *Mind Control* with **rank** *10* producing **effectDc** *20*',
        'And an **AppliedEffect** links *Mind Control* to *Kara*',
        'When *Kara* resolves a **Resistance Check** with **Trait** *Will* against **DifficultyClass** *20*',
        'And the **d20** result is *20* for **rollTotal** *24*',
        'Then the **GradedCheckResult** has **isCritical** *true*',
        'And **isSuccess** is *true* with **margin** *4*',
        'And the degree of success is increased by one after normal calculation',
        'And no **Condition** is applied',
    ]),
])

perform_routine_check = story("Perform Routine Check", "user", scenarios=[
    scenario("Routine Check succeeds when Routine Total meets DC", [], [
        'Given a **Character** *Sage* with a **Trait** *Technology* at **purchasedRank** *8*',
        'And no **Circumstance Modifier** applies',
        'And circumstances allow a **RoutineCheck**',
        'When the **RoutineCheck** is resolved with a fixed result of *10* substituted for the **d20**',
        'Then the **CheckResult** has **rollTotal** *18* (8 + 10)',
        'And **isSuccess** is *true* against **DifficultyClass** *15*',
        'And no **d20** is rolled',
    ]),
    scenario("Routine Total below DC allows player to choose a standard roll", [], [
        'Given a **Character** *Sage* with a **Trait** *Technology* at **purchasedRank** *4*',
        'And no **Circumstance Modifier** applies',
        'And circumstances allow a **RoutineCheck**',
        'When the **RoutineCheck** is resolved with a fixed result of *10*',
        'Then the **CheckResult** has **rollTotal** *14* (4 + 10)',
        'And **isSuccess** is *false* against **DifficultyClass** *20*',
        'And the player may choose to make a standard **Check** with **Trait** *Technology* rolling the **d20** instead',
    ]),
    scenario("Trait bonus plus ten or higher guarantees automatic success at DC twenty", [], [
        'Given a **Character** *Sage* with a **Trait** *Technology* at **purchasedRank** *10*',
        'And no **Circumstance Modifier** applies',
        'When the **RoutineCheck** is resolved with a fixed result of *10*',
        'Then the **CheckResult** has **rollTotal** *20* (10 + 10)',
        'And **isSuccess** is *true* against **DifficultyClass** *20*',
        'And no roll is required',
    ]),
    scenario("Extended Routine Eligibility allows routine resolution in non-standard situations", [], [
        'Given a **Character** *Sage* with a **Trait** *Acrobatics* at **purchasedRank** *12*',
        'And *Acrobatics* grants extended **Routine Eligibility** for balance-related tasks',
        'And the situation would not normally allow a routine check',
        'When a balance task at **DifficultyClass** *20* is attempted',
        'Then the **RoutineCheck** is applied because of the extended eligibility',
        'And the **CheckResult** has **rollTotal** *22* (12 + 10)',
        'And **isSuccess** is *true*',
    ]),
])

apply_condition = story("Apply Condition to Character", "system", scenarios=[
    scenario("Basic Condition applied and its Game Modifier becomes active", [], [
        'Given a **Character** *Kara* with **ImposedConditions** containing no active conditions',
        'When **Condition** *Impaired* is applied to *Kara* from **ConditionSource** *Poison Gas*',
        'Then the **ImposedCondition** is recorded with **isActive** *true*',
        'And the **GameModifier** with **amount** *-2* and **appliesTo** *null* is enforced on all checks',
    ]),
    scenario("Multiple active conditions stack their effects", [], [
        'Given a **Character** *Kara* with **ImposedConditions** containing active **Condition** *Impaired* (−2 to all checks) from **ConditionSource** *Poison Gas*',
        'When **Condition** *Vulnerable* is applied from a different **ConditionSource** *Psychic Lance*',
        'Then both **ImposedConditions** are active simultaneously',
        'And **Condition** *Impaired* applies **GameModifier** **amount** *-2*',
        'And **Condition** *Vulnerable* halves active defense values',
        'And all effects stack',
    ]),
    scenario("Combined Condition applies all constituent Basic Conditions simultaneously", [], [
        'Given a **Character** *Kara* with **ImposedConditions** containing no active conditions',
        'When **CombinedCondition** *Staggered* is applied to *Kara*',
        'Then constituent **Condition** *Dazed* is applied (limits to free actions and one standard action)',
        'And constituent **Condition** *Hindered* is applied (speed is halved)',
        'And individual constituents can be independently superseded or resolved',
    ]),
    scenario("Dazed restricts character to free actions and one standard action", [], [
        'Given a **Character** *Kara* with **ImposedConditions** containing no active conditions',
        'When **Condition** *Dazed* is applied to *Kara*',
        'Then *Kara* is restricted to free actions and one standard action per turn',
    ]),
    scenario("Impaired applies minus two Circumstance Modifier scoped to a specific trait", [], [
        'Given a **Character** *Kara* with **ImposedConditions** containing no active conditions',
        'When **Condition** *Impaired* is applied to *Kara* with **GameModifier** **appliesTo** *Athletics* and **amount** *-2*',
        'Then only checks using **Trait** *Athletics* take the *-2* penalty',
        'And checks using other traits are unaffected',
    ]),
    scenario("Vulnerable halves active defense values", [], [
        'Given a **Character** *Kara* with a **Trait** *Dodge* at **purchasedRank** *10*',
        'And a **Trait** *Parry* at **purchasedRank** *7*',
        'When **Condition** *Vulnerable* is applied to *Kara*',
        'Then the **Trait** *Dodge* active defense is halved to *5*',
        'And the **Trait** *Parry* active defense is halved to *4* (rounded up)',
    ]),
])

supersede_condition = story("Supersede Condition in Chain", "system", scenarios=[
    scenario("More severe condition overrides lesser without destroying it", [], [
        'Given a **Character** *Kara* with **ImposedConditions** containing active **Condition** *Dazed* from **ConditionSource** *Effect Alpha*',
        'And **Condition** *Stunned* has **supersedes** *Dazed*',
        'When **Condition** *Stunned* is applied from the same **ConditionSource** *Effect Alpha*',
        'Then **Condition** *Stunned* becomes active',
        'And **Condition** *Dazed* from *Effect Alpha* is removed (same-source supersession)',
        'And the **ConditionSource** *Effect Alpha* continues to be tracked',
    ]),
    scenario("Dazed superseded by Stunned — no actions including free", [], [
        'Given a **Character** *Kara* with active **Condition** *Dazed* from **ConditionSource** *Sonic Burst*',
        'When **Condition** *Stunned* is applied from the same **ConditionSource** *Sonic Burst*',
        'Then *Kara* cannot take any actions including free actions (Stunned restriction)',
        'And the *Dazed* modifier (one standard action allowed) is no longer enforced',
    ]),
    scenario("Impaired superseded by Disabled — penalty increases to minus five", [], [
        'Given a **Character** *Kara* with active **Condition** *Impaired* (**GameModifier** **amount** *-2*) from **ConditionSource** *Venom*',
        'When **Condition** *Disabled* is applied from the same **ConditionSource** *Venom*',
        'Then **Condition** *Disabled* applies **GameModifier** **amount** *-5* instead of *Impaired\'s* *-2*',
        'And **Condition** *Impaired* from *Venom* is removed',
    ]),
    scenario("Vulnerable superseded by Defenseless — defenses become zero", [], [
        'Given a **Character** *Kara* with active **Condition** *Vulnerable* from **ConditionSource** *Force Field Collapse*',
        'When **Condition** *Defenseless* is applied from the same **ConditionSource** *Force Field Collapse*',
        'Then active defense bonuses are set to *0* (not merely halved)',
        'And attackers may use **RoutineCheck** resolution against *Kara*',
        'And forgoing routine makes any hit a critical hit',
    ]),
    scenario("Hindered superseded by Immobile — movement becomes zero", [], [
        'Given a **Character** *Kara* with active **Condition** *Hindered* from **ConditionSource** *Web Trap*',
        'When **Condition** *Immobile* is applied from the same **ConditionSource** *Web Trap*',
        'Then *Kara\'s* movement speed is overridden to *0*',
        'And **Condition** *Hindered* from *Web Trap* is removed',
    ]),
    scenario("Compelled superseded by Controlled — full action control transferred", [], [
        'Given a **Character** *Kara* with active **Condition** *Compelled* from **ConditionSource** *Domination*',
        'When **Condition** *Controlled* is applied from the same **ConditionSource** *Domination*',
        'Then full action control is transferred to the controlling character',
        'And all of *Kara\'s* actions are dictated by that character',
        'And **Condition** *Compelled* from *Domination* is removed',
    ]),
])

roll_resistance_ongoing = story("Roll Resistance Check Against Ongoing Effect to Remove Conditions", "user", scenarios=[
    scenario("Successful Resistance Check ends Ongoing Effect and removes all its conditions", [], [
        'Given a **Character** *Kara* with an **AppliedEffect** *Mind Fog* that has **isOngoing** *true*',
        'And the **AppliedEffect** has imposed **Condition** *Impaired* on *Kara* (active)',
        'And a **Trait** *Will* at **purchasedRank** *8* is used for resistance',
        'When *Kara* resolves a **Resistance Check** against **Effect** *Mind Fog* with **effectDc** *16*',
        'And the **GradedCheckResult** has **isSuccess** *true*',
        'Then **AppliedEffect.end()** is called',
        'And **Condition** *Impaired* from **ConditionSource** *Mind Fog* is removed from **ImposedConditions**',
        'And any **ImposedCondition** that was blocked by the removed condition becomes active',
    ]),
    scenario("Failed Resistance Check leaves Ongoing Effect and conditions in place", [], [
        'Given a **Character** *Kara* with an **AppliedEffect** *Mind Fog* that has **isOngoing** *true*',
        'And the **AppliedEffect** has imposed **Condition** *Impaired* on *Kara* (active)',
        'When *Kara* resolves a **Resistance Check** against **Effect** *Mind Fog* with **effectDc** *16*',
        'And the **GradedCheckResult** has **isSuccess** *false* with **degree** *1*',
        'Then the **AppliedEffect** remains with **isOngoing** *true*',
        'And **Condition** *Impaired* persists on *Kara*',
    ]),
    scenario("Failed Resistance Check with multiple degrees imposes additional conditions", [], [
        'Given a **Character** *Kara* with an **AppliedEffect** *Mind Fog* that has **isOngoing** *true*',
        'And the **AppliedEffect** has imposed **Condition** *Impaired* on *Kara* (active)',
        'And the **Effect** maps *2 degrees of failure* to **Condition** *Disabled*',
        'When *Kara* resolves a **Resistance Check** with **rollTotal** *6* against **effectDc** *16*',
        'And the **GradedCheckResult** has **isSuccess** *false* with **degree** *2*',
        'Then the **AppliedEffect** remains ongoing',
        'And **Condition** *Disabled* is applied via **ImposedConditions.applyCondition()**',
        'And **Condition** *Impaired* is superseded by *Disabled* (same source)',
    ]),
])

remove_condition_source_ends = story("Remove Condition When Source Effect Ends", "system", scenarios=[
    scenario("Source Effect ending removes all conditions it imposed", [], [
        'Given a **Character** *Kara* with **AppliedEffect** *Flame Aura* that imposed **Condition** *Impaired* and **Condition** *Vulnerable*',
        'And both conditions have **ConditionSource** *Flame Aura*',
        'When the **AppliedEffect** *Flame Aura* calls **end()**',
        'Then both **Condition** *Impaired* and **Condition** *Vulnerable* are removed from **ImposedConditions**',
        'And *Kara\'s* **ImposedConditions** no longer contains any conditions from *Flame Aura*',
    ]),
    scenario("Superseded Condition re-emerges when more severe ends and its source is still active", [], [
        'Given a **Character** *Kara* with active **Condition** *Stunned* from **ConditionSource** *Sonic Burst*',
        'And inactive **Condition** *Dazed* from **ConditionSource** *Mind Fog* with **blockingCondition** pointing to *Stunned*',
        'And **AppliedEffect** *Mind Fog* has **isOngoing** *true*',
        'When **AppliedEffect** *Sonic Burst* calls **end()** and **Condition** *Stunned* is removed',
        'Then **ImposedConditions.revealBlockedConditions()** activates **Condition** *Dazed*',
        'And the **ImposedCondition** for *Dazed* has **isActive** *true*',
        'And *Kara* is now limited by *Dazed* (one standard action per turn)',
    ]),
    scenario("Both conditions removed when more severe ends and lesser source also ended", [], [
        'Given a **Character** *Kara* with active **Condition** *Stunned* from **ConditionSource** *Sonic Burst*',
        'And inactive **Condition** *Dazed* from **ConditionSource** *Mind Fog* with **blockingCondition** pointing to *Stunned*',
        'And **AppliedEffect** *Mind Fog* has already called **end()** (isOngoing *false*)',
        'When **AppliedEffect** *Sonic Burst* calls **end()** and **Condition** *Stunned* is removed',
        'Then **Condition** *Dazed* from *Mind Fog* was already removed when *Mind Fog* ended',
        'And *Kara\'s* **ImposedConditions** is clear of both conditions',
    ]),
    scenario("Multiple source effects — only conditions from ended source are removed", [], [
        'Given a **Character** *Kara* with active **Condition** *Impaired* from **ConditionSource** *Poison Gas*',
        'And active **Condition** *Hindered* from **ConditionSource** *Web Trap*',
        'When **AppliedEffect** *Poison Gas* calls **end()**',
        'Then **Condition** *Impaired* from *Poison Gas* is removed',
        'And **Condition** *Hindered* from *Web Trap* remains active',
        'And **AppliedEffect** *Web Trap* still has **isOngoing** *true*',
    ]),
])

stabilize_dying_ally = story("Stabilize Dying Ally with Treatment Check", "user", scenarios=[
    scenario("Successful Treatment Check stabilizes the Dying Character", [], [
        'Given a **Character** *Sage* with a **Trait** *Treatment* at **purchasedRank** *10*',
        'And a **Character** *Kara* has the **CombinedCondition** *Dying*',
        'When *Sage* makes a **Treatment Check** on *Kara*',
        'And the **CheckResult** has **isSuccess** *true*',
        'Then *Kara* is marked as *Stabilized*',
        'And the **CombinedCondition** *Dying* ends',
        'But *Kara* remains *Incapacitated* until further treatment or rest',
    ]),
    scenario("Failed Treatment Check leaves Dying condition in place", [], [
        'Given a **Character** *Sage* with a **Trait** *Treatment* at **purchasedRank** *6*',
        'And a **Character** *Kara* has the **CombinedCondition** *Dying*',
        'When *Sage* makes a **Treatment Check** on *Kara*',
        'And the **CheckResult** has **isSuccess** *false*',
        'Then the **CombinedCondition** *Dying* persists on *Kara*',
        'And *Kara* must still attempt the **Fortitude Check** for that round',
    ]),
    scenario("Treatment Check consumes the Ally's action for the round", [], [
        'Given a **Character** *Sage* who is engaged in combat',
        'And a **Character** *Kara* has the **CombinedCondition** *Dying*',
        'When *Sage* makes a **Treatment Check** on *Kara*',
        'Then making the **Treatment Check** consumes *Sage\'s* standard action for that round',
    ]),
])


# --- Scenario Outlines (from specification-by-example-outline.md) ---

grade_check_result = story("Grade Check Result by Degree", "system", scenario_outlines=[
    scenario_outline(
        "Degree of success calculated from margin above DC",
        [
            'Given a **Character** *Kara* with a **Trait** *Athletics* at **purchasedRank** {purchased_rank}',
            'And a **Circumstance Modifier** of {circumstance_modifier}',
        ],
        [
            'Given a **DifficultyClass** with value {dc_value}',
            'When *Kara* resolves a graded **Check** with **Trait** *Athletics*',
            'And the **d20** result is {d20_roll} for **rollTotal** {roll_total}',
            'Then the **GradedCheckResult** has **margin** {margin}',
            'And **isSuccess** is {is_success}',
            'And **isCritical** is {is_critical}',
            'And **degree** is {degree}',
        ],
        [
            example_table(
                ["scenario", "purchased_rank", "circumstance_modifier", "dc_value", "d20_roll", "roll_total", "margin", "is_success", "is_critical", "degree"],
                [
                    ["Degree 1 — bare success", "6", "0", "15", "9", "15", "0", "true", "false", "1"],
                    ["Degree 2 — exceeds by 5", "6", "0", "15", "14", "20", "5", "true", "false", "2"],
                    ["Degree 3 — exceeds by 10", "6", "0", "15", "19", "25", "10", "true", "false", "3"],
                    ["Degree 4 — exceeds by 15 (maximum)", "6", "0", "5", "14", "20", "15", "true", "false", "4"],
                    ["Degree 4 — exceeds by 20 still capped", "6", "0", "5", "19", "25", "20", "true", "false", "4"],
                    ["Degree 1 — bare failure", "6", "0", "15", "5", "11", "-4", "false", "false", "1"],
                    ["Degree 2 — below by 5", "6", "0", "15", "4", "10", "-5", "false", "false", "2"],
                    ["Degree 3 — below by 10", "6", "0", "20", "4", "10", "-10", "false", "false", "3"],
                    ["Degree 4 — below by 15 (maximum)", "4", "0", "20", "1", "5", "-15", "false", "false", "4"],
                    ["Degree 4 — below by 20 still capped", "4", "0", "25", "1", "5", "-20", "false", "false", "4"],
                    ["Critical upgrades 1 failure to success", "4", "0", "25", "20", "24", "-1", "true", "true", "1"],
                ]
            )
        ]
    ),
])

lead_team_check = story("Lead Team Check with Helpers", "user", scenario_outlines=[
    scenario_outline(
        "Helper results produce Circumstance Modifier for Leader's Check",
        [
            'Given each **Character** {character_name} with **role** {role}',
            'And each **Character** {character_name} has a **Trait** {trait_name} at **purchasedRank** {purchased_rank}',
        ],
        [
            'When the **TeamCheck** is initiated with the *leader* **Character** resolving against **DifficultyClass** {helper_dc}',
            'And each *helper* **Character** resolves a **Check** against **DifficultyClass** {helper_dc}',
            'Then {successes} helpers achieve **Helper Success**',
            'And **has_failure** is {has_failure}',
            'And **computeHelperModifier()** returns {helper_modifier}',
            'And the *leader* **Character** receives a **circumstanceModifier** of {circumstance_modifier} on their **Check**',
            'And only the *leader* **Character\'s** final **rollTotal** determines the outcome',
        ],
        [
            example_table(
                ["scenario", "character_name", "role"],
                [
                    ["One helper succeeds", "Atlas", "leader"],
                    ["One helper succeeds", "Bolt", "helper"],
                    ["Two helpers succeed", "Atlas", "leader"],
                    ["Two helpers succeed", "Bolt", "helper"],
                    ["Two helpers succeed", "Sage", "helper"],
                    ["Three helpers succeed", "Atlas", "leader"],
                    ["Three helpers succeed", "Bolt", "helper"],
                    ["Three helpers succeed", "Sage", "helper"],
                    ["Three helpers succeed", "Piper", "helper"],
                    ["One helper fails", "Atlas", "leader"],
                    ["One helper fails", "Bolt", "helper"],
                    ["Mixed \u2014 two succeed one fails", "Atlas", "leader"],
                    ["Mixed \u2014 two succeed one fails", "Bolt", "helper"],
                    ["Mixed \u2014 two succeed one fails", "Sage", "helper"],
                    ["Mixed \u2014 two succeed one fails", "Piper", "helper"],
                ]
            ),
            example_table(
                ["scenario", "character_name", "trait_name", "purchased_rank"],
                [
                    ["One helper succeeds", "Atlas", "Athletics", "8"],
                    ["One helper succeeds", "Bolt", "Athletics", "6"],
                    ["Two helpers succeed", "Atlas", "Athletics", "8"],
                    ["Two helpers succeed", "Bolt", "Athletics", "6"],
                    ["Two helpers succeed", "Sage", "Athletics", "7"],
                    ["Three helpers succeed", "Atlas", "Athletics", "8"],
                    ["Three helpers succeed", "Bolt", "Athletics", "6"],
                    ["Three helpers succeed", "Sage", "Athletics", "7"],
                    ["Three helpers succeed", "Piper", "Athletics", "5"],
                    ["One helper fails", "Atlas", "Athletics", "8"],
                    ["One helper fails", "Bolt", "Athletics", "2"],
                    ["Mixed \u2014 two succeed one fails", "Atlas", "Athletics", "8"],
                    ["Mixed \u2014 two succeed one fails", "Bolt", "Athletics", "6"],
                    ["Mixed \u2014 two succeed one fails", "Sage", "Athletics", "7"],
                    ["Mixed \u2014 two succeed one fails", "Piper", "Athletics", "2"],
                ]
            ),
            example_table(
                ["scenario", "helper_dc", "successes", "has_failure", "helper_modifier", "circumstance_modifier"],
                [
                    ["One helper succeeds", "10", "1", "false", "+2", "+2"],
                    ["Two helpers succeed", "10", "2", "false", "+2", "+2"],
                    ["Three helpers succeed", "10", "3", "false", "+5", "+5"],
                    ["One helper fails", "10", "0", "true", "-2", "-2"],
                    ["Mixed \u2014 two succeed one fails", "10", "2", "true", "+2", "+2"],
                ]
            ),
        ]
    ),
])

roll_fortitude_dying = story("Roll Fortitude Check to Stabilize While Dying", "user", scenario_outlines=[
    scenario_outline(
        "Fortitude Check accumulates degrees toward stabilization or death",
        [
            'Given a **Character** *Kara* has the **CombinedCondition** *Dying*',
            'And a **Fortitude Check** is required at **DifficultyClass** *15* each round',
        ],
        [
            'Given *Kara\'s* **ImposedConditions** has **dyingSuccessCount** {dying_success_count} and **dyingFailureCount** {dying_failure_count}',
            'When *Kara* resolves a **Fortitude Check** at **DifficultyClass** *15*',
            'And the **d20** result is {d20_roll}',
            'And the **GradedCheckResult** has **isSuccess** {is_success} with **isCritical** {is_critical} and **degree** {degree}',
            'Then **ImposedConditions.recordDyingFortitudeResult()** returns {outcome}',
        ],
        [
            example_table(
                ["scenario", "dying_success_count", "dying_failure_count", "d20_roll", "is_success", "is_critical", "degree", "outcome"],
                [
                    ["First success — still alive", "0", "0", "12", "true", "false", "1", "ALIVE"],
                    ["Second success — stabilized", "1", "0", "14", "true", "false", "1", "STABILIZED"],
                    ["Critical on first round — stabilized", "0", "1", "20", "true", "true", "2", "STABILIZED"],
                    ["First failure — still alive", "0", "0", "3", "false", "false", "1", "ALIVE"],
                    ["Second failure — still alive", "1", "1", "4", "false", "false", "1", "ALIVE"],
                    ["Third failure — dead", "0", "2", "2", "false", "false", "1", "DEAD"],
                ]
            )
        ]
    ),
])

translate_rank = story("Translate Trait Rank to Real-World Value", "system", scenario_outlines=[
    scenario_outline(
        "Rank looked up in Measurements Table returns real-world value",
        [
            'Given the **Measurement** service is available with the standard **Measurements Table**',
        ],
        [
            'Given a **Trait** with **effectiveRank** {rank}',
            'When the system calls **Measurement.lookup()** with rank {rank} and type {measurement_type}',
            'Then the returned **Real-World Value** is {real_world_value} {unit}',
        ],
        [
            example_table(
                ["scenario", "rank", "measurement_type", "real_world_value", "unit"],
                [
                    ["Rank 0 mass", "0", "MASS", "6", "lbs"],
                    ["Rank 1 mass", "1", "MASS", "12", "lbs"],
                    ["Rank 5 mass", "5", "MASS", "200", "lbs"],
                    ["Rank 0 distance", "0", "DISTANCE", "6", "feet"],
                    ["Rank 5 distance", "5", "DISTANCE", "200", "feet"],
                    ["Rank -1 mass — halved", "-1", "MASS", "3", "lbs"],
                    ["Rank -2 mass — halved again", "-2", "MASS", "1.5", "lbs"],
                    ["Rank 10 distance — approximate", "10", "DISTANCE", "6000", "feet"],
                    ["Rank 3 time", "3", "TIME", "50", "seconds"],
                ]
            )
        ]
    ),
])

derive_measurement = story("Derive Measurement from Rank Formula", "system", scenario_outlines=[
    scenario_outline(
        "Travel distance derived from Time Rank plus Speed Rank",
        [
            'Given the **Measurement** service is available with the standard **Measurements Table**',
        ],
        [
            'Given a **Time Rank** of {time_rank}',
            'And a **Speed Rank** of {speed_rank}',
            'When the system calls **Measurement.travelDistanceRank()** with timeRank {time_rank} and speedRank {speed_rank}',
            'Then the result rank is {result_rank}',
            'And the **Measurements Table** lookup for that rank as DISTANCE returns {result_value} {unit}',
        ],
        [
            example_table(
                ["scenario", "time_rank", "speed_rank", "result_rank", "result_value", "unit"],
                [
                    ["Walking one round", "0", "0", "0", "6", "feet"],
                    ["Running one round", "0", "2", "2", "30", "feet"],
                    ["Flying one minute", "3", "5", "8", "1500", "feet"],
                    ["Long march one hour", "9", "2", "11", "12000", "feet"],
                ]
            )
        ]
    ),
    scenario_outline(
        "Travel time derived from Distance Rank minus Speed Rank",
        [
            'Given the **Measurement** service is available with the standard **Measurements Table**',
        ],
        [
            'Given a **Distance Rank** of {distance_rank}',
            'And a **Speed Rank** of {speed_rank}',
            'When the system calls **Measurement.travelTimeRank()** with distanceRank {distance_rank} and speedRank {speed_rank}',
            'Then the result rank is {result_rank}',
            'And the **Measurements Table** lookup for that rank as TIME returns {result_value} {unit}',
        ],
        [
            example_table(
                ["scenario", "distance_rank", "speed_rank", "result_rank", "result_value", "unit"],
                [
                    ["Walk 200 feet at speed rank 0", "5", "0", "5", "3", "minutes"],
                    ["Fly 6000 feet at speed rank 5", "10", "5", "5", "3", "minutes"],
                ]
            )
        ]
    ),
    scenario_outline(
        "Throwing distance derived from Strength Rank minus Mass Rank",
        [
            'Given the **Measurement** service is available with the standard **Measurements Table**',
        ],
        [
            'Given a **Strength Rank** of {strength_rank}',
            'And a **Mass Rank** of {mass_rank}',
            'When the system calls **Measurement.throwingDistanceRank()** with strengthRank {strength_rank} and massRank {mass_rank}',
            'Then the result rank is {result_rank}',
            'And the **Measurements Table** lookup for that rank as DISTANCE returns {result_value} {unit}',
        ],
        [
            example_table(
                ["scenario", "strength_rank", "mass_rank", "result_rank", "result_value", "unit"],
                [
                    ["Strong hero throws light object", "10", "2", "8", "1500", "feet"],
                    ["Average hero throws medium object", "5", "5", "0", "6", "feet"],
                    ["Weak throw — negative result", "3", "6", "-3", "0.75", "feet"],
                ]
            )
        ]
    ),
])


if __name__ == "__main__":
    graph = {
        "epics": [
            {
                "name": "Resolve Checks — Make Check",
                "sub_epics": [],
                "story_groups": [{"stories": [
                    make_trait_check, grade_check_result, make_opposed_check,
                    resolve_comparison_check, make_resistance_check,
                    perform_routine_check, lead_team_check,
                ]}]
            },
            {
                "name": "Resolve Checks — Apply Conditions",
                "sub_epics": [],
                "story_groups": [{"stories": [apply_condition, supersede_condition]}]
            },
            {
                "name": "Resolve Checks — Recover from Conditions",
                "sub_epics": [],
                "story_groups": [{"stories": [
                    roll_resistance_ongoing, remove_condition_source_ends,
                    roll_fortitude_dying, stabilize_dying_ally,
                ]}]
            },
            {
                "name": "Translate Rank to Measure",
                "sub_epics": [],
                "story_groups": [{"stories": [translate_rank, derive_measurement]}]
            },
        ],
        "increments": []
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)

    print(f"Wrote story-graph.json to {OUTPUT}")
    print(f"  Epics: {len(graph['epics'])}")
    total_stories = sum(
        len(sg['stories'])
        for epic in graph['epics']
        for sg in epic.get('story_groups', [])
    )
    print(f"  Stories: {total_stories}")
