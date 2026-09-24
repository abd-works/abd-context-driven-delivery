---
state: key-abstractions
---

# Module: [Skill]

Scope: Skill basics (ranks, checks, DCs, modifiers, interaction skills, manipulation skills, skill mastery), and all individual skills.

**Core terms**:
- skill rank
- skill check
- skill modifier
- trained only
- interaction skill
- manipulation skill
- Skill Mastery
- circumstance modifier
- Acrobatics
- Athletics
- Close Combat
- Deception
- Expertise
- Insight
- Intimidation
- Investigation
- Perception
- Persuasion
- Ranged Combat
- Sleight of Hand
- Stealth
- Technology
- Treatment
- Vehicles

**Moved to other modules**:
- (none — all 24 Core terms belong to the Skill module)

---

# Core Domain

## Skill

The Skill abstraction is the core mechanical concept of the module — it defines what a skill is, how it is acquired, and how it is resolved. A skill is a learned ability combining training (ranks) and natural talent (ability modifier); its check is the single resolution path for all skill-based actions: roll d20, add the skill rank, add the ability modifier, add any circumstance modifiers, and compare to a DC. The Skill KA owns the rank economy (1 PP per 2 ranks, split freely across skills), the check formula, the Trained Only gate, and the circumstance modifier concept as it applies within skill use. Skill Mastery is included here because it is a direct enhancement to the skill check resolution — it removes the roll requirement for a nominated skill, granting the routine check result unconditionally. The Skill abstraction is the foundation upon which every named skill (Acrobatics, Deception, etc.) is built; no individual skill makes sense without this mechanical foundation.

The Skill abstraction collaborates with the Ability abstraction (which supplies the ability modifier), the Check Resolution module (which defines DC, degrees of success, and routine checks), and the Character Construction module (which owns power points). Invariants: every skill check must include the ability modifier even when the character is untrained; Trained Only skills must reject untrained attempts; circumstance modifiers are situational additive inputs to the check formula and do not change its structure.

#### Decisions made

- Skill Mastery kept in this KA rather than in an Advantage KA — it directly modifies skill check resolution (module-fit test passed); its definition is grounded in skill rank benchmarks and the routine check concept.
- circumstance modifier kept as a Core term here because Chapter 4 defines it in the context of skills; skill-specific circumstance modifiers are this module’s responsibility.
- Trained Only is a Core term, not a boundary term — it is a property of skills owned by this module.
- skill modifier limit (the PL cap) is owned by Character Construction; it is not a Core term here — it constrains what can be built, not how skills resolve.

### skill rank

#### Domain Language

- A skill rank is the number of points a character has invested in a skill; it serves as a numerical bonus added to the d20 roll on skill checks.
- Characters with at least one rank in a skill are considered trained in that skill.
- Skills cost 1 power point per 2 ranks; ranks may be split across multiple skills.
- A character with rank 0 in a skill is untrained; some skills may still be used untrained, others cannot.
- Skill rank benchmarks: +5 allows routine DC 15; +10 allows routine DC 20; +15 allows routine DC 25; +30 allows routine DC 40.

#### References

**Ref — Ch4 Skills**
Source: context/rules/HeroesHandbook-rules__chunk_041.md
Locator: lines 2689-2735
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Ch4 Skills"
chunk_index: 41
line_range: "2689-2735"
---

## CHAPTER 4: SKILLS

### Skill Rank
Your rank in a skill, based on the points you have invested
in that skill. If you have ranks in a skill youâ€™re considered
trained in that skill. You can use some skills even if you
donâ€™t have any ranks in them, known as using a skill un-
trained. Some skills may not be used untrained.

### Ability Modifier
Each skill has an ability modifier applied to the skillâ€™s
checks. Each skillâ€™s ability modifier is noted in its descrip-
tion and on the Skills table. If you use a skill untrained, the
ability modifier still applies to the skill check.

### Miscellaneous Modifiers
Miscellaneous modifiers to skill checks include modifiers
for circumstances, and bonuses from advantages or pow-
ers, among others.
The higher the total, the better the result. Youâ€™re usually look-
ing for a total that equals or exceeds a particular difficulty
class (DC), which may be based on another characterâ€™s traits.

### Critical Success
If you roll a 20 on the die when making a check youâ€™ve
scored a critical success. Determine the degree of suc-
cess normally and then increase it by one degree. This
can turn a low-level success into something more signifi-
cant, but more importantly, it can turn a failure into a full-
fledged success!

### Acquiring Skills
Give your hero skill ranks by spending power points: 2 skill
ranks per power point. Skill ranks do not all need to be as-
signed to the same skill. You can split them between differ-
ent skills. Characters can perform some tasks without any
training, using only raw talent (as defined by their ability
ranks), but skilled characters are better at such things. Those
with the right combinations of skills and advantages can
even hold their own against super-powered opponents.
Skill Cost = 1 power point per
2 skill ranks.
Heroes sneak into the closely guarded lairs of criminal masterminds, infiltrate alien computer systems, and build devices
beyond the understanding of modern science. They can piece together obscure clues to a villainâ€™s latest plot, run along
tightropes, and pilot vehicles through obstacle courses, all in a dayâ€™s work. In MUTANTS & MASTERMINDS, they do so through
the use of various skills, described in this chapter.
```

**Ref — Skill Basics**
Source: context/rules/HeroesHandbook-rules__chunk_042.md
Locator: lines 2736-2796
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Skill Basics"
chunk_index: 42
line_range: "2736-2796"
---

### Skill Basics
Skills are learned abilities, a combination of training (the skill) and natural talent (an ability rank). Each skill has a rank,
used as a bonus to the die roll when using the skill. To make a skill check, roll:
d20 + skill rank + ability modifier + miscellaneous modifiers

### How Skills Work
When you use a skill, make a skill check to see how you do. Based on the circumstances, your result must match or beat a
particular number to use the skill successfully. The harder the task, the higher the number you need to roll. (See Checks,
page 12, for more information.)

### Untrained Skill Checks
Generally, if you attempt a task requiring a skill you donâ€™t
have, you make a skill check as normal. Skill rank doesnâ€™t
apply because you donâ€™t have any ranks in the skill. You
do get other modifiers, however, such as the skillâ€™s ability
modifier.
Many skills can only be used if you are trained in them.
Skills that cannot be used untrained are marked with a
â€œNoâ€ in the â€œUntrainedâ€ column on the Skills table and
listed as â€œTrained Onlyâ€ in their descriptions. Attempts to
use these skills untrained automatically fail. In some cases,
a skill may have both trained and untrained aspects; if you
do not have any ranks in that skill, you can only use the
untrained ones.


### Interaction Skills
Certain skills, called interaction skills, are aimed at deal-
ing with others through social interaction. Interaction
skills allow you to influence the attitudes of others and get
them to cooperate with you in one way or another. Since
interaction skills are intended for dealing with others so-
cially, they have certain requirements.
First, you must be able to interact with the subject(s) of
the skill. They must be aware of you and able to under-
stand you. If they canâ€™t hear or understand you for some
reason, you have a â€“5 circumstance penalty to your skill
check (see Circumstance Modifiers in The Basics).
Interaction skills work best on intelligent subjects, ones
with an Intellect rank of â€“4 or better. You can use them
on creatures with Int â€“5, but again with a â€“5 circumstance
penalty; theyâ€™re just too dumb to get the subtleties of
your point. You canâ€™t use interaction skills at all on sub-
jects lacking one or more mental abilities. (Try convincing
a rock to be your friendâ€”or afraid of youâ€”sometime.)
The Immunity effect (see the Powers chapter) can also
render characters immune to interaction skills.
You can use interaction skills on groups of subjects at
once, but only to achieve the same result for everyone.
So you can attempt to use Deception or Persuasion to
convince a group of something, or Intimidation to cow
a crowd, for example, but you canâ€™t convince some indi-
viduals of one thing and the rest of another, or intimidate
some and not others. The GM decides if a particular use of
an interaction skill is effective against a group, and may
apply modifiers depending on the situation. The general
rules for interaction still apply: everyone in the group
must be able to hear and understand you, for example, or
you suffer a â€“5 on your skill check against them. Mindless
subjects are unaffected, as usual.
```

---

### skill check

#### Domain Language

- A skill check resolves skill use: roll d20 + skill rank + ability modifier + miscellaneous modifiers and compare to the Difficulty Class (DC).
- A result equal to or exceeding the DC is a success; higher totals produce better outcomes (degrees of success).
- Rolling a natural 20 scores a critical success: resolve degrees normally, then increase the result by one degree.
- When used untrained, skill rank is 0 but the ability modifier and other modifiers still apply.
- Attempts to use a Trained Only skill untrained automatically fail without a roll.

#### References

**Ref — Ch4 Skills**
Source: context/rules/HeroesHandbook-rules__chunk_041.md
Locator: lines 2689-2735
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Ch4 Skills"
chunk_index: 41
line_range: "2689-2735"
---

## CHAPTER 4: SKILLS

### Skill Rank
Your rank in a skill, based on the points you have invested
in that skill. If you have ranks in a skill youâ€™re considered
trained in that skill. You can use some skills even if you
donâ€™t have any ranks in them, known as using a skill un-
trained. Some skills may not be used untrained.

### Ability Modifier
Each skill has an ability modifier applied to the skillâ€™s
checks. Each skillâ€™s ability modifier is noted in its descrip-
tion and on the Skills table. If you use a skill untrained, the
ability modifier still applies to the skill check.

### Miscellaneous Modifiers
Miscellaneous modifiers to skill checks include modifiers
for circumstances, and bonuses from advantages or pow-
ers, among others.
The higher the total, the better the result. Youâ€™re usually look-
ing for a total that equals or exceeds a particular difficulty
class (DC), which may be based on another characterâ€™s traits.

### Critical Success
If you roll a 20 on the die when making a check youâ€™ve
scored a critical success. Determine the degree of suc-
cess normally and then increase it by one degree. This
can turn a low-level success into something more signifi-
cant, but more importantly, it can turn a failure into a full-
fledged success!

### Acquiring Skills
Give your hero skill ranks by spending power points: 2 skill
ranks per power point. Skill ranks do not all need to be as-
signed to the same skill. You can split them between differ-
ent skills. Characters can perform some tasks without any
training, using only raw talent (as defined by their ability
ranks), but skilled characters are better at such things. Those
with the right combinations of skills and advantages can
even hold their own against super-powered opponents.
Skill Cost = 1 power point per
2 skill ranks.
Heroes sneak into the closely guarded lairs of criminal masterminds, infiltrate alien computer systems, and build devices
beyond the understanding of modern science. They can piece together obscure clues to a villainâ€™s latest plot, run along
tightropes, and pilot vehicles through obstacle courses, all in a dayâ€™s work. In MUTANTS & MASTERMINDS, they do so through
the use of various skills, described in this chapter.
```

**Ref — Skill Basics**
Source: context/rules/HeroesHandbook-rules__chunk_042.md
Locator: lines 2736-2796
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Skill Basics"
chunk_index: 42
line_range: "2736-2796"
---

### Skill Basics
Skills are learned abilities, a combination of training (the skill) and natural talent (an ability rank). Each skill has a rank,
used as a bonus to the die roll when using the skill. To make a skill check, roll:
d20 + skill rank + ability modifier + miscellaneous modifiers

### How Skills Work
When you use a skill, make a skill check to see how you do. Based on the circumstances, your result must match or beat a
particular number to use the skill successfully. The harder the task, the higher the number you need to roll. (See Checks,
page 12, for more information.)

### Untrained Skill Checks
Generally, if you attempt a task requiring a skill you donâ€™t
have, you make a skill check as normal. Skill rank doesnâ€™t
apply because you donâ€™t have any ranks in the skill. You
do get other modifiers, however, such as the skillâ€™s ability
modifier.
Many skills can only be used if you are trained in them.
Skills that cannot be used untrained are marked with a
â€œNoâ€ in the â€œUntrainedâ€ column on the Skills table and
listed as â€œTrained Onlyâ€ in their descriptions. Attempts to
use these skills untrained automatically fail. In some cases,
a skill may have both trained and untrained aspects; if you
do not have any ranks in that skill, you can only use the
untrained ones.


### Interaction Skills
Certain skills, called interaction skills, are aimed at deal-
ing with others through social interaction. Interaction
skills allow you to influence the attitudes of others and get
them to cooperate with you in one way or another. Since
interaction skills are intended for dealing with others so-
cially, they have certain requirements.
First, you must be able to interact with the subject(s) of
the skill. They must be aware of you and able to under-
stand you. If they canâ€™t hear or understand you for some
reason, you have a â€“5 circumstance penalty to your skill
check (see Circumstance Modifiers in The Basics).
Interaction skills work best on intelligent subjects, ones
with an Intellect rank of â€“4 or better. You can use them
on creatures with Int â€“5, but again with a â€“5 circumstance
penalty; theyâ€™re just too dumb to get the subtleties of
your point. You canâ€™t use interaction skills at all on sub-
jects lacking one or more mental abilities. (Try convincing
a rock to be your friendâ€”or afraid of youâ€”sometime.)
The Immunity effect (see the Powers chapter) can also
render characters immune to interaction skills.
You can use interaction skills on groups of subjects at
once, but only to achieve the same result for everyone.
So you can attempt to use Deception or Persuasion to
convince a group of something, or Intimidation to cow
a crowd, for example, but you canâ€™t convince some indi-
viduals of one thing and the rest of another, or intimidate
some and not others. The GM decides if a particular use of
an interaction skill is effective against a group, and may
apply modifiers depending on the situation. The general
rules for interaction still apply: everyone in the group
must be able to hear and understand you, for example, or
you suffer a â€“5 on your skill check against them. Mindless
subjects are unaffected, as usual.
```

---

### skill modifier

#### Domain Language

- The skill modifier is the total bonus added to the d20 roll: skill rank + ability modifier + miscellaneous modifiers.
- Each skill has an associated ability whose rank adds as the ability modifier to all checks for that skill, even when used untrained.
- Miscellaneous modifiers include circumstance modifiers, bonuses from advantages, and bonuses from powers.
- The higher the total skill modifier, the more consistent and favorable the skill check outcomes.

#### References

**Ref — Ch4 Skills**
Source: context/rules/HeroesHandbook-rules__chunk_041.md
Locator: lines 2689-2735
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Ch4 Skills"
chunk_index: 41
line_range: "2689-2735"
---

## CHAPTER 4: SKILLS

### Skill Rank
Your rank in a skill, based on the points you have invested
in that skill. If you have ranks in a skill youâ€™re considered
trained in that skill. You can use some skills even if you
donâ€™t have any ranks in them, known as using a skill un-
trained. Some skills may not be used untrained.

### Ability Modifier
Each skill has an ability modifier applied to the skillâ€™s
checks. Each skillâ€™s ability modifier is noted in its descrip-
tion and on the Skills table. If you use a skill untrained, the
ability modifier still applies to the skill check.

### Miscellaneous Modifiers
Miscellaneous modifiers to skill checks include modifiers
for circumstances, and bonuses from advantages or pow-
ers, among others.
The higher the total, the better the result. Youâ€™re usually look-
ing for a total that equals or exceeds a particular difficulty
class (DC), which may be based on another characterâ€™s traits.

### Critical Success
If you roll a 20 on the die when making a check youâ€™ve
scored a critical success. Determine the degree of suc-
cess normally and then increase it by one degree. This
can turn a low-level success into something more signifi-
cant, but more importantly, it can turn a failure into a full-
fledged success!

### Acquiring Skills
Give your hero skill ranks by spending power points: 2 skill
ranks per power point. Skill ranks do not all need to be as-
signed to the same skill. You can split them between differ-
ent skills. Characters can perform some tasks without any
training, using only raw talent (as defined by their ability
ranks), but skilled characters are better at such things. Those
with the right combinations of skills and advantages can
even hold their own against super-powered opponents.
Skill Cost = 1 power point per
2 skill ranks.
Heroes sneak into the closely guarded lairs of criminal masterminds, infiltrate alien computer systems, and build devices
beyond the understanding of modern science. They can piece together obscure clues to a villainâ€™s latest plot, run along
tightropes, and pilot vehicles through obstacle courses, all in a dayâ€™s work. In MUTANTS & MASTERMINDS, they do so through
the use of various skills, described in this chapter.
```

**Ref — Skill Basics**
Source: context/rules/HeroesHandbook-rules__chunk_042.md
Locator: lines 2736-2796
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Skill Basics"
chunk_index: 42
line_range: "2736-2796"
---

### Skill Basics
Skills are learned abilities, a combination of training (the skill) and natural talent (an ability rank). Each skill has a rank,
used as a bonus to the die roll when using the skill. To make a skill check, roll:
d20 + skill rank + ability modifier + miscellaneous modifiers

### How Skills Work
When you use a skill, make a skill check to see how you do. Based on the circumstances, your result must match or beat a
particular number to use the skill successfully. The harder the task, the higher the number you need to roll. (See Checks,
page 12, for more information.)

### Untrained Skill Checks
Generally, if you attempt a task requiring a skill you donâ€™t
have, you make a skill check as normal. Skill rank doesnâ€™t
apply because you donâ€™t have any ranks in the skill. You
do get other modifiers, however, such as the skillâ€™s ability
modifier.
Many skills can only be used if you are trained in them.
Skills that cannot be used untrained are marked with a
â€œNoâ€ in the â€œUntrainedâ€ column on the Skills table and
listed as â€œTrained Onlyâ€ in their descriptions. Attempts to
use these skills untrained automatically fail. In some cases,
a skill may have both trained and untrained aspects; if you
do not have any ranks in that skill, you can only use the
untrained ones.


### Interaction Skills
Certain skills, called interaction skills, are aimed at deal-
ing with others through social interaction. Interaction
skills allow you to influence the attitudes of others and get
them to cooperate with you in one way or another. Since
interaction skills are intended for dealing with others so-
cially, they have certain requirements.
First, you must be able to interact with the subject(s) of
the skill. They must be aware of you and able to under-
stand you. If they canâ€™t hear or understand you for some
reason, you have a â€“5 circumstance penalty to your skill
check (see Circumstance Modifiers in The Basics).
Interaction skills work best on intelligent subjects, ones
with an Intellect rank of â€“4 or better. You can use them
on creatures with Int â€“5, but again with a â€“5 circumstance
penalty; theyâ€™re just too dumb to get the subtleties of
your point. You canâ€™t use interaction skills at all on sub-
jects lacking one or more mental abilities. (Try convincing
a rock to be your friendâ€”or afraid of youâ€”sometime.)
The Immunity effect (see the Powers chapter) can also
render characters immune to interaction skills.
You can use interaction skills on groups of subjects at
once, but only to achieve the same result for everyone.
So you can attempt to use Deception or Persuasion to
convince a group of something, or Intimidation to cow
a crowd, for example, but you canâ€™t convince some indi-
viduals of one thing and the rest of another, or intimidate
some and not others. The GM decides if a particular use of
an interaction skill is effective against a group, and may
apply modifiers depending on the situation. The general
rules for interaction still apply: everyone in the group
must be able to hear and understand you, for example, or
you suffer a â€“5 on your skill check against them. Mindless
subjects are unaffected, as usual.
```

---

### trained only

#### Domain Language

- Skills marked Trained Only require at least 1 rank to use; untrained attempts automatically fail.
- Some skills have both trained-only and untrained aspects; a character without ranks may use only the untrained aspects.
- Skills without the Trained Only marker may be attempted by any character using only the ability modifier.
- The Trained Only designation appears in the skill description and the Skills table Untrained column.

#### References

**Ref — Skill Basics**
Source: context/rules/HeroesHandbook-rules__chunk_042.md
Locator: lines 2736-2796
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Skill Basics"
chunk_index: 42
line_range: "2736-2796"
---

### Skill Basics
Skills are learned abilities, a combination of training (the skill) and natural talent (an ability rank). Each skill has a rank,
used as a bonus to the die roll when using the skill. To make a skill check, roll:
d20 + skill rank + ability modifier + miscellaneous modifiers

### How Skills Work
When you use a skill, make a skill check to see how you do. Based on the circumstances, your result must match or beat a
particular number to use the skill successfully. The harder the task, the higher the number you need to roll. (See Checks,
page 12, for more information.)

### Untrained Skill Checks
Generally, if you attempt a task requiring a skill you donâ€™t
have, you make a skill check as normal. Skill rank doesnâ€™t
apply because you donâ€™t have any ranks in the skill. You
do get other modifiers, however, such as the skillâ€™s ability
modifier.
Many skills can only be used if you are trained in them.
Skills that cannot be used untrained are marked with a
â€œNoâ€ in the â€œUntrainedâ€ column on the Skills table and
listed as â€œTrained Onlyâ€ in their descriptions. Attempts to
use these skills untrained automatically fail. In some cases,
a skill may have both trained and untrained aspects; if you
do not have any ranks in that skill, you can only use the
untrained ones.


### Interaction Skills
Certain skills, called interaction skills, are aimed at deal-
ing with others through social interaction. Interaction
skills allow you to influence the attitudes of others and get
them to cooperate with you in one way or another. Since
interaction skills are intended for dealing with others so-
cially, they have certain requirements.
First, you must be able to interact with the subject(s) of
the skill. They must be aware of you and able to under-
stand you. If they canâ€™t hear or understand you for some
reason, you have a â€“5 circumstance penalty to your skill
check (see Circumstance Modifiers in The Basics).
Interaction skills work best on intelligent subjects, ones
with an Intellect rank of â€“4 or better. You can use them
on creatures with Int â€“5, but again with a â€“5 circumstance
penalty; theyâ€™re just too dumb to get the subtleties of
your point. You canâ€™t use interaction skills at all on sub-
jects lacking one or more mental abilities. (Try convincing
a rock to be your friendâ€”or afraid of youâ€”sometime.)
The Immunity effect (see the Powers chapter) can also
render characters immune to interaction skills.
You can use interaction skills on groups of subjects at
once, but only to achieve the same result for everyone.
So you can attempt to use Deception or Persuasion to
convince a group of something, or Intimidation to cow
a crowd, for example, but you canâ€™t convince some indi-
viduals of one thing and the rest of another, or intimidate
some and not others. The GM decides if a particular use of
an interaction skill is effective against a group, and may
apply modifiers depending on the situation. The general
rules for interaction still apply: everyone in the group
must be able to hear and understand you, for example, or
you suffer a â€“5 on your skill check against them. Mindless
subjects are unaffected, as usual.
```

**Ref — Manipulation Skills**
Source: context/rules/HeroesHandbook-rules__chunk_043.md
Locator: lines 2797-2849
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Manipulation Skills"
chunk_index: 43
line_range: "2797-2849"
---

### Manipulation Skills
Some skills, called manipulation skills, require a degree
of fine physical manipulation. You need prehensile limbs
and a Strength rank or some suitable Precise power effect
to use manipulation skills effectively. If your physical ma-
nipulation capabilities are impaired in some fashion (such
as having your hands tied or full use of only one hand),
the GM may impose a circumstance modifier based on the
severity of the impairment. Characters lacking the ability
to use manipulation skills can still have ranks in them and
use them to oversee or assist the work of others (see Team
Checks, page 16).

### Skill Benchmarks
You can get a general idea of just how good a particu-
lar characterâ€™s skill bonus is using the general difficulty
class guidelines given in The Basics along with the
rules for routine checks (see Routine Checks in that
chapter).
For example, a +5 total skill modifier means the char-
acter can routinely achieve a result of 15 (a tough task).
Safe to say the character is a pro, able to routinely han-
dle tasks that would prove too much for someone less
skilled. A character with a +10 skill modifier achieve a
DC 20 (challenging task) on a routine basis, a real level of
expertise, while a +15 modifier can routinely complete
DC 25 (formidable) tasks. At the high end, a +30 skill
modifier can routinely accomplishing the nigh impos-
sible (DC 40 tasks)!

### Skill Descriptions
This section describes the skills available to MUTANTS & MASTERMINDS characters, including their common uses and modi-
fiers. Characters may be able to use skills for tasks other than those given here. The GM sets the DC and decides the
results in those cases. The format for skill descriptions is given here. Items that do not apply are omitted from the
skillâ€™s description.

### Skill Name
Ability â€¢ Trained Only â€¢ Interaction â€¢ Manipulation â€¢ Requires Tools
The skill name line and the line below it contain the fol-
lowing information:
Skill Name: What the skill is called. GMs may feel free to
change the names of some skills to better suit the style of
their game, if desired.
Ability: The ability that applies a modifier to the skill
check.
Trained Only: If â€œTrained Onlyâ€ is included on the line be-
low the skillâ€™s name, you must have at least 1 rank in the
skill in order to use it. If â€œTrained Onlyâ€ is absent, untrained
characters (those with 0 ranks in the skill) may use it.
Some skills may have trained only aspects, in which case
this notation is still listed, and the untrained aspects are
called out in the skill description.
```

---

## Interaction Skill

Interaction Skill is a named source category of skills whose purpose is social influence — changing the attitudes, beliefs, and actions of other characters through conversation, persuasion, trickery, or threat. The category owns its own requirements: subjects must be aware of and able to understand the user; unintelligent subjects impose a penalty; subjects lacking mental abilities cannot be targeted; the Immunity power effect can render a character wholly immune. These requirements belong to the category KA, not to individual skills. The four skills within this KA are Deception (lying, bluffing, disguise, feinting, innuendo, tricking), Intimidation (coercing, demoralizing, mass-intimidating minions), Persuasion (improving NPC attitudes step by step), and Insight (reading intentions, detecting illusions and influences, resisting social manipulation). Insight is the defensive counterpart to the three offensive interaction skills.

All four skills collaborate with each other: Deception creates situations that Insight detects; Intimidation and Deception can temporarily suppress Stealth checks; Persuasion negotiations compare check results. Group use is possible but applies the same result uniformly — differentiated targeting is not permitted. Invariant: interaction skills cannot produce different results for different members of a group in a single use; mindless subjects are always unaffected.

#### Decisions made

- Insight grouped with offensive interaction skills — its source description is framed entirely in terms of resisting and detecting social skills; it has no independent purpose outside that context.
- interaction skill (the category) kept as a named Core term to preserve the source’s own categorical vocabulary.
- Deception, Intimidation, Persuasion, and Insight all pass the independence test — each is a separately-named skill with its own DC table and use cases.

### interaction skill

#### Domain Language

- Interaction skills are a category used for social influence: changing others attitudes and gaining their cooperation.
- Require the subject to be aware of and able to understand the user; inability to hear or understand imposes a -5 circumstance penalty.
- Subjects with Intellect rank -5 impose a -5 circumstance penalty; subjects lacking any mental abilities cannot be targeted.
- The Immunity power effect can render a character completely immune to interaction skills.
- May be used on groups, but only to achieve the same result for every member; mindless subjects are unaffected.
- The interaction skills in this module are Deception, Intimidation, and Persuasion; Insight resists them.

#### References

**Ref — Skill Basics**
Source: context/rules/HeroesHandbook-rules__chunk_042.md
Locator: lines 2736-2796
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Skill Basics"
chunk_index: 42
line_range: "2736-2796"
---

### Skill Basics
Skills are learned abilities, a combination of training (the skill) and natural talent (an ability rank). Each skill has a rank,
used as a bonus to the die roll when using the skill. To make a skill check, roll:
d20 + skill rank + ability modifier + miscellaneous modifiers

### How Skills Work
When you use a skill, make a skill check to see how you do. Based on the circumstances, your result must match or beat a
particular number to use the skill successfully. The harder the task, the higher the number you need to roll. (See Checks,
page 12, for more information.)

### Untrained Skill Checks
Generally, if you attempt a task requiring a skill you donâ€™t
have, you make a skill check as normal. Skill rank doesnâ€™t
apply because you donâ€™t have any ranks in the skill. You
do get other modifiers, however, such as the skillâ€™s ability
modifier.
Many skills can only be used if you are trained in them.
Skills that cannot be used untrained are marked with a
â€œNoâ€ in the â€œUntrainedâ€ column on the Skills table and
listed as â€œTrained Onlyâ€ in their descriptions. Attempts to
use these skills untrained automatically fail. In some cases,
a skill may have both trained and untrained aspects; if you
do not have any ranks in that skill, you can only use the
untrained ones.


### Interaction Skills
Certain skills, called interaction skills, are aimed at deal-
ing with others through social interaction. Interaction
skills allow you to influence the attitudes of others and get
them to cooperate with you in one way or another. Since
interaction skills are intended for dealing with others so-
cially, they have certain requirements.
First, you must be able to interact with the subject(s) of
the skill. They must be aware of you and able to under-
stand you. If they canâ€™t hear or understand you for some
reason, you have a â€“5 circumstance penalty to your skill
check (see Circumstance Modifiers in The Basics).
Interaction skills work best on intelligent subjects, ones
with an Intellect rank of â€“4 or better. You can use them
on creatures with Int â€“5, but again with a â€“5 circumstance
penalty; theyâ€™re just too dumb to get the subtleties of
your point. You canâ€™t use interaction skills at all on sub-
jects lacking one or more mental abilities. (Try convincing
a rock to be your friendâ€”or afraid of youâ€”sometime.)
The Immunity effect (see the Powers chapter) can also
render characters immune to interaction skills.
You can use interaction skills on groups of subjects at
once, but only to achieve the same result for everyone.
So you can attempt to use Deception or Persuasion to
convince a group of something, or Intimidation to cow
a crowd, for example, but you canâ€™t convince some indi-
viduals of one thing and the rest of another, or intimidate
some and not others. The GM decides if a particular use of
an interaction skill is effective against a group, and may
apply modifiers depending on the situation. The general
rules for interaction still apply: everyone in the group
must be able to hear and understand you, for example, or
you suffer a â€“5 on your skill check against them. Mindless
subjects are unaffected, as usual.
```

---

## Manipulation Skill

Manipulation Skill is a named source category of skills requiring fine physical manipulation — the user must have prehensile limbs and a Strength rank, or a suitable Precise power effect. Physical impairment constrains use via circumstance penalties; characters without physical capability can still contribute via team check oversight. All four individual manipulation skills are Trained Only. Sleight of Hand (legerdemain, concealment, escape, theft) covers covert manual tasks. Technology (operating, building, repairing, sabotaging; requires tools) covers technical device work. Treatment (diagnosing, caring for, reviving, stabilizing, treating illness/poison; requires tools) covers medical work. Vehicles (operating any vehicle under stress) covers dramatic operation.

The Manipulation Skill KA collaborates with Check Resolution (team checks), the Power module (Precise power effect as physical substitute), and the Advantage module (Inventor advantage enabling Technology inventing). Invariant: all manipulation skills require prehensile limbs and Strength rank or Precise power effect; lacking tools for Requires Tools skills always imposes a −5 circumstance penalty.

#### Decisions made

- manipulation skill (the category) kept as a named Core term — the source defines its requirements separately from individual skills.
- Vehicles grouped here as a manipulation skill per source classification (Dexterity, Trained Only, Manipulation).
- Technology and Treatment both flag Requires Tools; the −5 penalty for lacking tools is a skill-level rule owned here.
- Open question: Inventor advantage wiring with Technology inventing — seam between Advantage module and this module not yet mapped.

### manipulation skill

#### Domain Language

- Manipulation skills require fine physical manipulation; the user must have prehensile limbs and a Strength rank, or a suitable Precise power effect.
- Physical impairment causes the GM to impose a circumstance penalty scaled to severity.
- A character lacking physical manipulation capability may still hold ranks and use them to oversee or assist others via team checks.
- The manipulation skills in this module are Sleight of Hand, Technology, Treatment, and Vehicles.

#### References

**Ref — Manipulation Skills**
Source: context/rules/HeroesHandbook-rules__chunk_043.md
Locator: lines 2797-2849
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Manipulation Skills"
chunk_index: 43
line_range: "2797-2849"
---

### Manipulation Skills
Some skills, called manipulation skills, require a degree
of fine physical manipulation. You need prehensile limbs
and a Strength rank or some suitable Precise power effect
to use manipulation skills effectively. If your physical ma-
nipulation capabilities are impaired in some fashion (such
as having your hands tied or full use of only one hand),
the GM may impose a circumstance modifier based on the
severity of the impairment. Characters lacking the ability
to use manipulation skills can still have ranks in them and
use them to oversee or assist the work of others (see Team
Checks, page 16).

### Skill Benchmarks
You can get a general idea of just how good a particu-
lar characterâ€™s skill bonus is using the general difficulty
class guidelines given in The Basics along with the
rules for routine checks (see Routine Checks in that
chapter).
For example, a +5 total skill modifier means the char-
acter can routinely achieve a result of 15 (a tough task).
Safe to say the character is a pro, able to routinely han-
dle tasks that would prove too much for someone less
skilled. A character with a +10 skill modifier achieve a
DC 20 (challenging task) on a routine basis, a real level of
expertise, while a +15 modifier can routinely complete
DC 25 (formidable) tasks. At the high end, a +30 skill
modifier can routinely accomplishing the nigh impos-
sible (DC 40 tasks)!

### Skill Descriptions
This section describes the skills available to MUTANTS & MASTERMINDS characters, including their common uses and modi-
fiers. Characters may be able to use skills for tasks other than those given here. The GM sets the DC and decides the
results in those cases. The format for skill descriptions is given here. Items that do not apply are omitted from the
skillâ€™s description.

### Skill Name
Ability â€¢ Trained Only â€¢ Interaction â€¢ Manipulation â€¢ Requires Tools
The skill name line and the line below it contain the fol-
lowing information:
Skill Name: What the skill is called. GMs may feel free to
change the names of some skills to better suit the style of
their game, if desired.
Ability: The ability that applies a modifier to the skill
check.
Trained Only: If â€œTrained Onlyâ€ is included on the line be-
low the skillâ€™s name, you must have at least 1 rank in the
skill in order to use it. If â€œTrained Onlyâ€ is absent, untrained
characters (those with 0 ranks in the skill) may use it.
Some skills may have trained only aspects, in which case
this notation is still listed, and the untrained aspects are
called out in the skill description.
```

---

### Skill Mastery

#### Domain Language

- Skill Mastery is an advantage that allows the character to use a routine check result (bonus + 10) on a nominated skill even under stress, without rolling.
- A character with Skill Mastery can always achieve their routine result for that skill regardless of pressure.
- Source example: character has Skill Mastery for Stealth and does not need to roll.

#### References

**Ref — Manipulation Skills**
Source: context/rules/HeroesHandbook-rules__chunk_043.md
Locator: lines 2797-2849
Extract: partial
Part: Skill Benchmarks section referencing routine check values.

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Manipulation Skills"
chunk_index: 43
line_range: "2797-2849"
---

### Manipulation Skills
Some skills, called manipulation skills, require a degree
of fine physical manipulation. You need prehensile limbs
and a Strength rank or some suitable Precise power effect
to use manipulation skills effectively. If your physical ma-
nipulation capabilities are impaired in some fashion (such
as having your hands tied or full use of only one hand),
the GM may impose a circumstance modifier based on the
severity of the impairment. Characters lacking the ability
to use manipulation skills can still have ranks in them and
use them to oversee or assist the work of others (see Team
Checks, page 16).

### Skill Benchmarks
You can get a general idea of just how good a particu-
lar characterâ€™s skill bonus is using the general difficulty
class guidelines given in The Basics along with the
rules for routine checks (see Routine Checks in that
chapter).
For example, a +5 total skill modifier means the char-
acter can routinely achieve a result of 15 (a tough task).
Safe to say the character is a pro, able to routinely han-
dle tasks that would prove too much for someone less
skilled. A character with a +10 skill modifier achieve a
DC 20 (challenging task) on a routine basis, a real level of
expertise, while a +15 modifier can routinely complete
DC 25 (formidable) tasks. At the high end, a +30 skill
modifier can routinely accomplishing the nigh impos-
sible (DC 40 tasks)!

### Skill Descriptions
This section describes the skills available to MUTANTS & MASTERMINDS characters, including their common uses and modi-
fiers. Characters may be able to use skills for tasks other than those given here. The GM sets the DC and decides the
results in those cases. The format for skill descriptions is given here. Items that do not apply are omitted from the
skillâ€™s description.

### Skill Name
Ability â€¢ Trained Only â€¢ Interaction â€¢ Manipulation â€¢ Requires Tools
The skill name line and the line below it contain the fol-
lowing information:
Skill Name: What the skill is called. GMs may feel free to
change the names of some skills to better suit the style of
their game, if desired.
Ability: The ability that applies a modifier to the skill
check.
Trained Only: If â€œTrained Onlyâ€ is included on the line be-
low the skillâ€™s name, you must have at least 1 rank in the
skill in order to use it. If â€œTrained Onlyâ€ is absent, untrained
characters (those with 0 ranks in the skill) may use it.
Some skills may have trained only aspects, in which case
this notation is still listed, and the untrained aspects are
called out in the skill description.
```

**Ref — Ranged Combat**
Source: context/rules/HeroesHandbook-rules__chunk_059.md
Locator: lines 3762-3826
Extract: partial
Part: Sleight of Hand example referencing Skill Mastery for Stealth.

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Ranged Combat"
chunk_index: 59
line_range: "3762-3826"
---

### Ranged Combat
Dexterity
Youâ€™re trained with a particular type of ranged attack,
giving you a bonus to your attack checks with it equal
to your skill rank (see Attack Check in The Basics and
in the Action & Adventure chapter). Each ranged attack
is a separate Ranged Combat skill with its own rank, and
encompasses a single weapon or power, although an ar-
ray may be considered one power, at the Gamemasterâ€™s
discretion (see Arrays in the Powers chapter for more
information).
So a hero might have Ranged Combat: Guns or Ranged
Combat: Fire Control, but Ranged Combat: Powers is too
broad. Ranged Combat: Throwing is an option and in-
cludes both thrown weapons and objects a character sim-
ply picks up and throws.
The bonus from a Ranged Combat skill applies only to at-
tack checks with the particular attack, not to defenses. For
a broader bonus to attack checks that is less than simply
raising Dexterity rank, see the Ranged Attack advantage
in the Advantages chapter.

### Sleight Of Hand
Dexterity â€¢ Manipulation â€¢ Trained Only
You can perform dexterous feats of legerdemain such as
palming small objects, picking pockets, slipping out of
restraints, and so forth. Stage magicians use Sleight of
Hand legitimately as a performance skill, but it is most
commonly known for its criminal applications.
CONCEALING
You can use Sleight of Hand to conceal a small item on
your person, making your check result the DC of an Inves-
tigation or Perception check to find it.
CONTORTING
You can use Slight  of Hand to contort your body. Make a
DC 30 Sleight of Hand check to fit through a tight space
wide enough for your head but too narrow for the width
of your shoulders, or to reach through an opening wide
enough for your hand, but too narrow for your arm.
ESCAPING
Make a Sleight of Hand check to slip out of various re-
straints. This takes at least a minute per check.

You can also make a Sleight of Hand check to plant a small
object on someone, slip something into their pocket, drop
something into their drink, place a tiny radio tracer on them,
and so forth. To plant the object, you must get a check result
of 20 or higher, regardless of the opponentâ€™s check result.
The opponent notices the attempt if his check result beats
yours, whether you succeed in planting the item or not.
Example: The Rubber-Bandit is robbing a muse-
um of some of its valuables when a security guard
passes by while making his rounds. The bouncing
Bandit has no fear of the rent-a-cop, so he decides
to have some fun. He has Skill Mastery for his Stealth
and, unsurprisingly, the guard doesnâ€™t notice him
slither closer, but then the Rubber-Bandit decides to
try and steal the guardâ€™s gun without being noticed.
Bandit has Sleight of Hand +12 and adds that to the
roll of a die. A whopping 19 plus 12 for a total of 31!
The guard, with a Perception skill of only +5, doesnâ€™t
have a prayer of noticing his gun being eased out of
its holster, but the GM rolls anyway and gets a total
of 20. A good roll, but no enough.
```

---

### circumstance modifier

#### Domain Language

- A circumstance modifier is a bonus or penalty applied to a skill check that reflects the specific conditions under which it is made.
- Circumstance modifiers stack with the base skill modifier; favorable circumstances add bonuses, unfavorable circumstances impose penalties.
- Common penalties: lacking tools for a Requires Tools skill (-5); subject cannot hear/understand during interaction (-5); moving faster than speed rank minus 1 during Stealth (-5).
- Specific skill descriptions list the standard circumstance modifiers for each skill use.

#### References

**Ref — Ch4 Skills**
Source: context/rules/HeroesHandbook-rules__chunk_041.md
Locator: lines 2689-2735
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Ch4 Skills"
chunk_index: 41
line_range: "2689-2735"
---

## CHAPTER 4: SKILLS

### Skill Rank
Your rank in a skill, based on the points you have invested
in that skill. If you have ranks in a skill youâ€™re considered
trained in that skill. You can use some skills even if you
donâ€™t have any ranks in them, known as using a skill un-
trained. Some skills may not be used untrained.

### Ability Modifier
Each skill has an ability modifier applied to the skillâ€™s
checks. Each skillâ€™s ability modifier is noted in its descrip-
tion and on the Skills table. If you use a skill untrained, the
ability modifier still applies to the skill check.

### Miscellaneous Modifiers
Miscellaneous modifiers to skill checks include modifiers
for circumstances, and bonuses from advantages or pow-
ers, among others.
The higher the total, the better the result. Youâ€™re usually look-
ing for a total that equals or exceeds a particular difficulty
class (DC), which may be based on another characterâ€™s traits.

### Critical Success
If you roll a 20 on the die when making a check youâ€™ve
scored a critical success. Determine the degree of suc-
cess normally and then increase it by one degree. This
can turn a low-level success into something more signifi-
cant, but more importantly, it can turn a failure into a full-
fledged success!

### Acquiring Skills
Give your hero skill ranks by spending power points: 2 skill
ranks per power point. Skill ranks do not all need to be as-
signed to the same skill. You can split them between differ-
ent skills. Characters can perform some tasks without any
training, using only raw talent (as defined by their ability
ranks), but skilled characters are better at such things. Those
with the right combinations of skills and advantages can
even hold their own against super-powered opponents.
Skill Cost = 1 power point per
2 skill ranks.
Heroes sneak into the closely guarded lairs of criminal masterminds, infiltrate alien computer systems, and build devices
beyond the understanding of modern science. They can piece together obscure clues to a villainâ€™s latest plot, run along
tightropes, and pilot vehicles through obstacle courses, all in a dayâ€™s work. In MUTANTS & MASTERMINDS, they do so through
the use of various skills, described in this chapter.
```

**Ref — Finding The Skill You Want**
Source: context/rules/HeroesHandbook-rules__chunk_044.md
Locator: lines 2850-2893
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Finding The Skill You Want"
chunk_index: 44
line_range: "2850-2893"
---

### Finding The Skill You Want
If you donâ€™t find a particular skill on the list, like climbing,
bluffing, or search, remember that each skill in MUTANTS &
MASTERMINDS covers a lot of ground. So, youâ€™ll find climbing
isnâ€™t its own skill, but is listed as part of Athletics, while
bluffing and search are under Deception and Investiga-
tion, respectively. When in doubt, read through the skill
you think is most similar to what youâ€™re looking for.

Interaction: If â€œInteractionâ€ is included on the line below
the skillâ€™s name, it is an interaction skill.
Manipulation: If â€œManipulationâ€ is included on the line
below the skillâ€™s name, it is a manipulation skill.
Requires Tools: If â€œRequires Toolsâ€ is included on the line
below the skillâ€™s name, you need to have the proper tools
to use the skill. Not having the proper tools is a â€“5 circum-
stance penalty to the skill check (see Circumstance Modi-
fiers, page 15).
The skill name line is followed by a description of the skill
and how it is used.

### Acrobatics
Agility â€¢ Trained Only
Use Acrobatics to flip, dive, roll, tumble, and perform other
acrobatic maneuvers, as well as keeping your balance un-
der difficult circumstances.
BALANCING
You can keep your balance and move along a precari-
ous surface at your ground speed minus 1 rank with a
successful Acrobatics check against the surfaceâ€™s DC. A
degree of failure indicates you spend your move action
just maintaining your balance and do not actually move,
while two or more degrees of failure means you lose
your balance and fall.
You are vulnerable while balancing. If you accept a +5 in-
crease to the Acrobatics DC, you are not vulnerable.
If you fail a resistance check while balancing, make an-
other immediate Acrobatics check against the original DC
to avoid falling.
MANEUVERING
You can make Acrobatics checks for various acrobatic
stunts or maneuvers, from back flips to jumping over
an opponent (to get behind them), flipping up onto a
```

---

## Physical Skill

Physical Skill groups three skills grounded in bodily performance and environmental navigation: Acrobatics (balance, tumbling, falling, rising from prone — Agility, Trained Only), Athletics (climbing, jumping, running, swimming, falling — Strength, untrained allowed), and Stealth (hiding, tailing, moving without detection — Agility, untrained allowed). All three involve dynamic circumstance modifiers based on speed, surface conditions, and environmental factors, and all three have reactive interactions with other checks — Acrobatics reacts to failed resistance checks while balancing; Athletics reacts to failed resistance checks while climbing; Stealth reacts to Deception/Intimidation distraction checks.

Physical Skills collaborate with Check Resolution (immediate reaction check triggers), the Combat module (Stealth interacts with surprise and concealment), and the Power module (Wall-crawling for impossible climbs, Leaping for extreme jumps, movement effects that interact with Stealth). Invariant: Acrobatics is Trained Only; Athletics and Stealth are untrained-allowed. Fall damage resolution spans both Acrobatics (lessening) and Athletics (catching).

#### Decisions made

- Stealth grouped with physical skills rather than with Sleight of Hand in a Covert KA — Stealth is Agility-based and involves whole-body positioning relative to cover, not fine manual dexterity.
- Sleight of Hand placed in Manipulation Skill KA per source classification (Dexterity, Manipulation, Trained Only).
- Fall damage resolution spans Acrobatics and Athletics — the cross-skill interaction is documented in Domain Language bullets, not unified into a single term.

### Acrobatics

#### Domain Language

- Acrobatics is a Trained Only skill based on Agility covering balance, acrobatic maneuvers, rising from prone, and reducing fall damage.
- Balancing: a successful check allows movement at ground speed minus 1 rank; one degree of failure equals no movement; two or more degrees means falling; the character is vulnerable while balancing unless DC is increased by +5.
- Maneuvering: checks for acrobatic stunts (flips, vaults, tumbling); GM sets the DC; two or more degrees of failure typically leaves the character prone.
- Standing: DC 20 check as a free action to rise from prone instead of a move action; failure leaves the character prone.
- Tumbling: DC 5 check reduces fall damage by 1 per degree of success; fall reduced to rank 0 deals no damage and character rises as a free action.
- Failing a resistance check while balancing triggers an immediate Acrobatics check against the original DC to avoid falling.

#### References

**Ref — Finding The Skill You Want**
Source: context/rules/HeroesHandbook-rules__chunk_044.md
Locator: lines 2850-2893
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Finding The Skill You Want"
chunk_index: 44
line_range: "2850-2893"
---

### Finding The Skill You Want
If you donâ€™t find a particular skill on the list, like climbing,
bluffing, or search, remember that each skill in MUTANTS &
MASTERMINDS covers a lot of ground. So, youâ€™ll find climbing
isnâ€™t its own skill, but is listed as part of Athletics, while
bluffing and search are under Deception and Investiga-
tion, respectively. When in doubt, read through the skill
you think is most similar to what youâ€™re looking for.

Interaction: If â€œInteractionâ€ is included on the line below
the skillâ€™s name, it is an interaction skill.
Manipulation: If â€œManipulationâ€ is included on the line
below the skillâ€™s name, it is a manipulation skill.
Requires Tools: If â€œRequires Toolsâ€ is included on the line
below the skillâ€™s name, you need to have the proper tools
to use the skill. Not having the proper tools is a â€“5 circum-
stance penalty to the skill check (see Circumstance Modi-
fiers, page 15).
The skill name line is followed by a description of the skill
and how it is used.

### Acrobatics
Agility â€¢ Trained Only
Use Acrobatics to flip, dive, roll, tumble, and perform other
acrobatic maneuvers, as well as keeping your balance un-
der difficult circumstances.
BALANCING
You can keep your balance and move along a precari-
ous surface at your ground speed minus 1 rank with a
successful Acrobatics check against the surfaceâ€™s DC. A
degree of failure indicates you spend your move action
just maintaining your balance and do not actually move,
while two or more degrees of failure means you lose
your balance and fall.
You are vulnerable while balancing. If you accept a +5 in-
crease to the Acrobatics DC, you are not vulnerable.
If you fail a resistance check while balancing, make an-
other immediate Acrobatics check against the original DC
to avoid falling.
MANEUVERING
You can make Acrobatics checks for various acrobatic
stunts or maneuvers, from back flips to jumping over
an opponent (to get behind them), flipping up onto a
```

**Ref — Balancing Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_045.md
Locator: lines 2894-2994
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Balancing Difficulties"
chunk_index: 45
line_range: "2894-2994"
---

### Balancing Difficulties
DC

### Example Surface
A yard or more wide
Wide ledge (1-3 ft.)
Narrow ledge (less than 1 ft.)
Balance beam
Tightrope

### Circumstance Modifiers
+2
Surface slightly slippery
+5
Surface very slippery
+2
Surface slightly uneven
+5
Surface very uneven or angled
+5
Move at your normal speed rank
+5
Not vulnerable while balancing
SKILLS
SKILL
ABILITY
UNTRAINED?
ACTION
Acrobatics
Agl
No
move or free
Athletics
Str
Yes
move
Close Combat
Fgt
Yes
standard
Deception
Pre
Yes
standard
Expertise
Int
No*
â€”
Insight
Awe
Yes
free
Intimidation
Pre
Yes
standard
Investigation
Int
No
â€”
Perception
Awe
Yes
free
Persuasion
Pre
Yes
â€”
Ranged Combat
Dex
Yes
standard
Sleight of Hand
Dex
No
standard
Stealth
Agl
Yes
move
Technology
Int
No
standard
Treatment
Int
No
standard
Vehicles
Dex
No
move
A â€œâ€”â€ entry in the Action column means using the skill typically takes longer than a standard action. See the skill description for details.
* Some areas of Expertise can be used Untrained. See the entry on Expertise for more information.

letics check to catch yourself (DC equal to the initial check
+ 10). Someone else within armâ€™s reach can also make an
Athletics check to catch you with the same DC. If your at-
tempt to catch someone else gets more than one degree
of failure, you fall as well.
```

**Ref — Climbing Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_046.md
Locator: lines 2995-3065
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Climbing Difficulties"
chunk_index: 46
line_range: "2995-3065"
---

### Climbing Difficulties
DC

### Example Surface
A ladder
A knotted rope
A rope
An uneven surface, like a rock-face
A rough surface, like a brick wall

### Circumstance Modifiers
â€“10
An air duct, chimney, or other area
where you can brace against two
opposite walls
â€“5
A corner where you can brace
against perpendicular walls
â€“5
Climb of less than 10 feet total
+2
Surface slightly slippery
+5
Surface very slippery
+5
+1 speed rank (up to your full speed)
+5
Not vulnerable while climbing
Since you canâ€™t easily move to avoid attacks, you are vul-
nerable while climbing unless you accept a +5 increase in
the DC. Any time you fail a resistance check while climb-
ing, make an immediate Athletics check against the DC of
the climb. Failure means you fall.
At the GMâ€™s discretion, certain kinds of climbing attempts
might require tools like ropes, pitons, harness, and so
forth. Attempting such a climb without tools incurs a â€“5
circumstance penalty.
FALLING
A fall inflicts damage rank 4 plus twice the distance rank
fallen, to a maximum of rank 16 damage. A fall with a dam-
age rank of 0 or less, such as a fall of 6 feet or less, inflicts
no damage. You are prone at the end of a fall. You can use
Acrobatics to lessen the damage from a fall.
JUMPING
The result of an Athletics check is the distance (in feet)
you can clear in a running long-jump. If you make a stand-
ing jump, divide the distance in half. If you make a verti-
cal jump (straight up) divide the distance by 5, and if you
make a standing vertical jump, divide it by 10.
Your Athletics bonus + 10 is the base distance you can
jump under routine circumstances. So a hero with a +10
Athletics bonus can make a routine long-jump of 20 feet,
ledge, tumbling through obstacles, and so forth. The GM
sets the DC. Success means you accomplish the maneu-
ver, while failure means you do not, and two or more
degrees of failure usually means you slip and end up
prone (and may suffer additional effects, depending on
the stunt). A successful acrobatic maneuver may provide
you a circumstance bonus on certain follow-up actions,
if the GM sees fit.
STANDING
You can make a DC 20 Acrobatics check to go from prone
to standing as a free action rather than a move action. A
failed check means you remain prone.
TUMBLING
You can make an Acrobatics check (DC 5) to lessen dam-
age from a fall, reducing the damage by 1 per degree. A
fall reduced to rank 0 damage does no damage and you
quickly roll to your feet as a free action. Otherwise, you are
prone at the end of a fall.
```

**Ref — Acrobatics Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_047.md
Locator: lines 3066-3117
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Acrobatics Difficulties"
chunk_index: 47
line_range: "3066-3117"
---

### Acrobatics Difficulties
DC
TASK
Lessen damage from a fall (â€“1 per degree)
Acrobatic maneuver
Move from prone to
standing as a free action
Contort to fit through a tight space

### Athletics
Strength
Use Athletics for physical feats like climbing, jumping, rid-
ing animal mounts, and swimming.
CLIMBING
With a successful Athletics check, you can climb along a
slope, wall, or other steep incline at your ground speed
rank minus 2 as a move action. A perfectly smooth, flat,
vertical surface canâ€™t be climbed without the Wall-crawl-
ing effect of Movement (see the Powers chapter).
A failed Athletics check indicates you make no progress,
and two or more degrees of failure means you fall from
whatever height you attained (unless you are secured
with a safety harness or other equipment). Make an Ath-

### Super Jumping
If you want your hero to jump tens, hundreds, thou-
sands of feet, or even miles, look to the Leaping effect
in the Powers chapter.

a standing long-jump of 10 feet, a vertical jump of 4 feet,
and a standing vertical jump of 2 feet on a routine basis.

### Jumping Distance

### Type Of Jump
DISTANCE (IN FEET)
Running Long-Jump
Athletics check result
Standing Long-Jump
Athletics check result,
divided by 2
Running Vertical Jump
Athletics check result,
divided by 5
Standing Vertical Jump
Athletics check result,
divided by 10
RUNNING
You can make a DC 15 Athletics check as a free action to
run faster: one or more degree of success increases your
ground speed rank by +1 for one round.
```

---

### Athletics

#### Domain Language

- Athletics is a skill based on Strength; it may be used untrained; it covers climbing, falling, jumping, running, and swimming.
- Climbing: a successful check allows climbing at ground speed rank minus 2; failure equals no progress; two or more degrees means falling; the character is vulnerable while climbing unless DC is increased by +5.
- Falling: a fall inflicts damage rank 4 plus twice the distance rank fallen (maximum rank 16); falls of rank 0 or less deal no damage; the character is prone at end of fall; Acrobatics can lessen fall damage.
- Jumping: Athletics check result equals running long-jump distance in feet; standing long-jump divides by 2; running vertical jump divides by 5; standing vertical jump divides by 10.
- Running: DC 15 check as a free action increases ground speed rank by +1 for one round.
- Swimming: DC 10 check allows swimming at ground speed rank minus 2; failure equals no progress; two or more degrees means going under.

#### References

**Ref — Acrobatics Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_047.md
Locator: lines 3066-3117
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Acrobatics Difficulties"
chunk_index: 47
line_range: "3066-3117"
---

### Acrobatics Difficulties
DC
TASK
Lessen damage from a fall (â€“1 per degree)
Acrobatic maneuver
Move from prone to
standing as a free action
Contort to fit through a tight space

### Athletics
Strength
Use Athletics for physical feats like climbing, jumping, rid-
ing animal mounts, and swimming.
CLIMBING
With a successful Athletics check, you can climb along a
slope, wall, or other steep incline at your ground speed
rank minus 2 as a move action. A perfectly smooth, flat,
vertical surface canâ€™t be climbed without the Wall-crawl-
ing effect of Movement (see the Powers chapter).
A failed Athletics check indicates you make no progress,
and two or more degrees of failure means you fall from
whatever height you attained (unless you are secured
with a safety harness or other equipment). Make an Ath-

### Super Jumping
If you want your hero to jump tens, hundreds, thou-
sands of feet, or even miles, look to the Leaping effect
in the Powers chapter.

a standing long-jump of 10 feet, a vertical jump of 4 feet,
and a standing vertical jump of 2 feet on a routine basis.

### Jumping Distance

### Type Of Jump
DISTANCE (IN FEET)
Running Long-Jump
Athletics check result
Standing Long-Jump
Athletics check result,
divided by 2
Running Vertical Jump
Athletics check result,
divided by 5
Standing Vertical Jump
Athletics check result,
divided by 10
RUNNING
You can make a DC 15 Athletics check as a free action to
run faster: one or more degree of success increases your
ground speed rank by +1 for one round.
```

**Ref — Swimming**
Source: context/rules/HeroesHandbook-rules__chunk_048.md
Locator: lines 3118-3168
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Swimming"
chunk_index: 48
line_range: "3118-3168"
---

### Swimming
A successful DC 10 Athletics check allows you to swim
your ground speed rank minus 2 as a move action. If the
check fails, you make no progress through the water dur-
ing the action. With more than one degree of failure, you
go under. If underwater, you must hold your breath to
avoid drowning (see page 238).

### Swimming Difficulties
DC

### Modifiers
+5
Rescuing another character who cannot swim
+5
Rough or choppy water
+5
+1 speed rank (up to your full ground speed)
+10
Stormy or turbulent water

## Combat Skill

Combat Skill groups two skills that add directly to attack checks for specific weapons or powers: Close Combat (based on Fighting) and Ranged Combat (based on Dexterity). Both follow the same pattern: each is specific to a single named weapon or power, adds its rank to attack checks for that weapon/power only, and explicitly does not add to defense. Both can be used untrained. An array of powers may be treated as a single power at the GM’s discretion.

Combat Skills collaborate directly with the Combat module (attack checks) and the Character Construction module (trade-off economics). For broader bonuses across all close or ranged attacks, the Close Attack and Ranged Attack advantages are the alternative. Invariant: a Combat Skill bonus applies only to attack checks for the specific weapon or power it names — never to any other attack, and never to defense.

#### Decisions made

- Close Combat and Ranged Combat grouped as a single KA — they share the same pattern (ability base, specific weapon/power, attack-check-only bonus).
- Both pass the independence test — they are named skills with their own rank slots.
- Close Combat: Unarmed noted in Domain Language (excludes grab/trip); no separate Core term needed.

### Close Combat
Fighting
Youâ€™re trained with a particular type of close attack, giv-
ing you a bonus to your attack checks with it equal to
your skill rank (see Attack Check in The Basics and in
the Action & Adventure chapter). Each close attack is
a separate Close Combat skill with its own rank, and en-
compasses a single weapon or power, although an ar-
ray may be considered one power, at the Gamemasterâ€™s
discretion (see Arrays in the Powers chapter for more
information).
So a hero might have Close Combat: Swords, but Close
Combat: Melee Weapons is too broad. Close Combat: Un-
armed is an option, meaning skill with unarmed strikes
like punches and kicks. However, this bonus does not ap-
ply to other forms of unarmed combat maneuvers, includ-
ing, but not limited to, grabbing or tripping.

If itâ€™s important, you can distinguish between a deception
that fails because the target doesnâ€™t believe it and one
that fails because it asks too much. For instance, if the tar-
get gets a +10 bonus to resistance because the deception
demands serious risk, and the resistance check succeeds
by 10 or less, then the target doesnâ€™t so much see through
the deception as prove reluctant to go along with it. If the
targetâ€™s Insight check succeeds by 11 or more, he has seen
through the deception, and would have refused even if
it had not placed unusual demands on him (that is, even
without the +10 modifier).
```

---

### Close Combat

#### Domain Language

- Close Combat is a skill based on Fighting; it may be used untrained; each Close Combat skill is specific to a single weapon or power.
- The skill rank adds to attack checks for that specific weapon or power only; it does not apply to defense.
- Close Combat: Unarmed covers punches and kicks but not grabbing or tripping maneuvers.
- An array of powers may be treated as one power for Close Combat purposes at the GMs discretion.
- For a broader bonus across all close attacks, see the Close Attack advantage.

#### References

**Ref — Swimming**
Source: context/rules/HeroesHandbook-rules__chunk_048.md
Locator: lines 3118-3168
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Swimming"
chunk_index: 48
line_range: "3118-3168"
---

### Swimming
A successful DC 10 Athletics check allows you to swim
your ground speed rank minus 2 as a move action. If the
check fails, you make no progress through the water dur-
ing the action. With more than one degree of failure, you
go under. If underwater, you must hold your breath to
avoid drowning (see page 238).

### Swimming Difficulties
DC

### Modifiers
+5
Rescuing another character who cannot swim
+5
Rough or choppy water
+5
+1 speed rank (up to your full ground speed)
+10
Stormy or turbulent water

### Close Combat
Fighting
Youâ€™re trained with a particular type of close attack, giv-
ing you a bonus to your attack checks with it equal to
your skill rank (see Attack Check in The Basics and in
the Action & Adventure chapter). Each close attack is
a separate Close Combat skill with its own rank, and en-
compasses a single weapon or power, although an ar-
ray may be considered one power, at the Gamemasterâ€™s
discretion (see Arrays in the Powers chapter for more
information).
So a hero might have Close Combat: Swords, but Close
Combat: Melee Weapons is too broad. Close Combat: Un-
armed is an option, meaning skill with unarmed strikes
like punches and kicks. However, this bonus does not ap-
ply to other forms of unarmed combat maneuvers, includ-
ing, but not limited to, grabbing or tripping.

If itâ€™s important, you can distinguish between a deception
that fails because the target doesnâ€™t believe it and one
that fails because it asks too much. For instance, if the tar-
get gets a +10 bonus to resistance because the deception
demands serious risk, and the resistance check succeeds
by 10 or less, then the target doesnâ€™t so much see through
the deception as prove reluctant to go along with it. If the
targetâ€™s Insight check succeeds by 11 or more, he has seen
through the deception, and would have refused even if
it had not placed unusual demands on him (that is, even
without the +10 modifier).
```

**Ref — Deception Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_049.md
Locator: lines 3169-3225
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Deception Modifiers"
chunk_index: 49
line_range: "3169-3225"
---

### Deception Modifiers

### Resistance Circumstance
MODIFIER
The target wants
to believe you.
â€“5
The deception is believable
and doesnâ€™t affect the target
much either way.
+0
The deception is a little hard
to believe or puts the target at
some kind of risk.
+5
The deception is difficult
to believe or entails
a serious risk.
+10
The deception is way
out there, almost too
incredible to consider.
+20
The bonus from a Close Combat skill applies only to at-
tack checks with the particular attack, not to defenses. For
a broader bonus to attack checks that is less than simply
raising Fighting rank, see the Close Attack advantage in
the Advantages chapter.

### Deception
Presence â€¢ Interaction
Deception is the skill of getting others to believe what you
want them to believe. It covers things like acting, bluffing,
fast-talk, trickery, and subterfuge.
Deception takes as long as it takes to spin-out your story.
Uses of Deception in action rounds are generally standard
actions, although you can attempt to deceive as a move
action by taking a â€“5 penalty to your check.
BLUFFING
Make a Deception check to tell a believable lie or get
someone do go along with you.
A bluff is usually opposed by the targetâ€™s Deception or
Insight check. Favorable and unfavorable circumstances
weigh heavily on the outcome. Two circumstances can
work against you: the deception is hard to believe, or what
you ask goes against the targetâ€™s self-interest, nature, or
personality.
UNDER THE HOOD: CHOOSING SKILLS
There are a number of factors to consider when choosing skills for your MUTANTS & MASTERMINDS character.
TRAINING VS. TALENT
In game terms thereâ€™s no difference between a character who has ranks in a skill because of extensive training and an-
other whose skill ranks represent a natural talent or aptitude for the skill. Both are considered â€œtrainedâ€ in the skill in
game terms. For example, one character might have a high Persuasion skill based on the characterâ€™s extensive training in
negotiation, debate, and management. Another characterâ€™s Persuasion skill may stem more from personal attractiveness
or a knack for getting others to cooperate, while a third character may have a combination of the two. Feel free to decide
for yourself what mix of training and talent your characterâ€™s skill ranks represent.
```

---

### Deception

#### Domain Language

- Deception is an interaction skill based on Presence; it covers lying, bluffing, disguise, feinting, innuendo, and tricking.
- Bluffing: Deception check opposed by targets Deception or Insight; circumstance modifiers from -5 (target wants to believe) to +20 (outrageous claim); standard action, or move action at -5.
- Disguise: Deception check result becomes the DC of observers Perception checks; GM rolls secretly; associates of the impersonated person get Perception bonuses (+2 regular, +5 friend, +10 intimate).
- Feinting: standard action Deception check opposed by targets Deception or Insight; success makes target vulnerable against the users next attack until end of users next round.
- Innuendo: DC 10 basic / DC 15 complex / DC 20 new information; recipient uses Insight at the same DC to understand; more than one degree of failure on either side misinterprets the message.
- Tricking: Deception check opposed by Deception or Insight to mislead into a dangerous action; more than one degree of failure on the users check leaves the user vulnerable.

#### References

**Ref — Deception Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_049.md
Locator: lines 3169-3225
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Deception Modifiers"
chunk_index: 49
line_range: "3169-3225"
---

### Deception Modifiers

### Resistance Circumstance
MODIFIER
The target wants
to believe you.
â€“5
The deception is believable
and doesnâ€™t affect the target
much either way.
+0
The deception is a little hard
to believe or puts the target at
some kind of risk.
+5
The deception is difficult
to believe or entails
a serious risk.
+10
The deception is way
out there, almost too
incredible to consider.
+20
The bonus from a Close Combat skill applies only to at-
tack checks with the particular attack, not to defenses. For
a broader bonus to attack checks that is less than simply
raising Fighting rank, see the Close Attack advantage in
the Advantages chapter.

### Deception
Presence â€¢ Interaction
Deception is the skill of getting others to believe what you
want them to believe. It covers things like acting, bluffing,
fast-talk, trickery, and subterfuge.
Deception takes as long as it takes to spin-out your story.
Uses of Deception in action rounds are generally standard
actions, although you can attempt to deceive as a move
action by taking a â€“5 penalty to your check.
BLUFFING
Make a Deception check to tell a believable lie or get
someone do go along with you.
A bluff is usually opposed by the targetâ€™s Deception or
Insight check. Favorable and unfavorable circumstances
weigh heavily on the outcome. Two circumstances can
work against you: the deception is hard to believe, or what
you ask goes against the targetâ€™s self-interest, nature, or
personality.
UNDER THE HOOD: CHOOSING SKILLS
There are a number of factors to consider when choosing skills for your MUTANTS & MASTERMINDS character.
TRAINING VS. TALENT
In game terms thereâ€™s no difference between a character who has ranks in a skill because of extensive training and an-
other whose skill ranks represent a natural talent or aptitude for the skill. Both are considered â€œtrainedâ€ in the skill in
game terms. For example, one character might have a high Persuasion skill based on the characterâ€™s extensive training in
negotiation, debate, and management. Another characterâ€™s Persuasion skill may stem more from personal attractiveness
or a knack for getting others to cooperate, while a third character may have a combination of the two. Feel free to decide
for yourself what mix of training and talent your characterâ€™s skill ranks represent.
```

**Ref — Life Skills**
Source: context/rules/HeroesHandbook-rules__chunk_050.md
Locator: lines 3226-3283
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Life Skills"
chunk_index: 50
line_range: "3226-3283"
---

### Life Skills
When allocating skill ranks for your character consider not just the characterâ€™s role as a hero but also the various other
skills the character may have picked up in day-to-day life. For example, most adults have some sort of Expertise skill as
their occupation with at least 3 to 5 ranks (more if theyâ€™re especially good at their job). Some people pick up ranks in Per-
ception, although most get by using the skill untrained. Characters working with technology may have the Technology
skill even if it doesnâ€™t apply to their powers. A particularly well-educated person may have various Expertise skills for jobs
they donâ€™t even hold. These additional skills help round out a character and provide some background color andâ€”who
knows?â€”they may turn out to be useful in an adventure at some point!

### Adventuring Skills
Also give some thought to the skills your character needs to be effective in game play. Some are obvious, especially if
theyâ€™re part of your character concept. A scientist is likely to have ranks in Technology. A pilot should have Vehicles, while
a doctor should have Treatment in addition to Expertise: Physician. Beyond the obvious and life skills of your character
consider â€œutility skillsâ€ like Insight, Perception, and Stealth, which many characters find useful. A few ranks in such skills
may be a smart investment.

DISGUISE
You can use makeup, costumes, and other props to change
your appearance. Your Deception check result determines
the effectiveness of the disguise, opposed by othersâ€™ Per-
ception check results. The GM makes the Deception check
secretly so you are not sure exactly how well your disguise
holds up under scrutiny.
Disguise is heavily dependent on circumstances: favor-
able ones include appropriate costuming and a subject
resembling your normal appearance, while unfavorable
circumstances include disguising yourself as a member
of a different race or sex, or not having sufficient props
(which can be up to a â€“5 modifier). If you are imperson-
ating a particular individual, anyone who knows that
individual gets a circumstance bonus to the Perception
check: regular associates get a +2, while friends get a +5
and intimate loved ones a +10.
Successfully acting like who you appear to be may also
require a Deception check with a DC equal to the observ-
erâ€™s Insight check, modified by familiarity if the observer
knows the subject well, as mentioned previously.
A disguise normally requires at least 10 minutes of prepa-
ration. The GM makes Perception checks for those who
encounter you immediately upon meeting you and each
hour or day thereafter, depending on circumstances.
FEINTING
You can use Deception as a standard action to mislead an
opponent in combat. Make a Deception check as a stan-
dard action opposed by the better of your targetâ€™s Decep-
tion or Insight. If your Deception check succeeds, the tar-
get is vulnerable against your next attack, until the end of
your next round (see Vulnerable in the Conditions sec-
tion of The Basics chapter).
INNUENDO
You can use Deception to send covert messages using
word-play and double-meanings while apparently talking
about other things. The DC for a basic message is 10. Com-
plex messages or messages trying to communicate new
information have DCs of 15 or 20, respectively. The recipi-
ent of the message must make a Insight check against the
same DC to understand it.
```

**Ref — Innuendo Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_051.md
Locator: lines 3284-3373
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Innuendo Difficulties"
chunk_index: 51
line_range: "3284-3373"
---

### Innuendo Difficulties
DC
TASK
Basic message
Complex message
Message containing new or detailed information
Anyone listening in on your innuendo can attempt a In-
sight check against the message DC. If successful, the
eavesdropper notices a message hidden in your conversa-
tion. If the eavesdropper gets at least two degrees of suc-
cess, he also understands the message. Whether trying to
send or pick up on a message, more than one degree of
failure on the check means the receiver misinterprets the
message in some fashion.
TRICKING
You can use Deception to mislead an opponent into taking
a potentially unwise action, such as trying to hit you while
standing in front of an electrical junction box or at the edge
of a precipice. If your Deception check opposed by Decep-
tion or Insight succeeds, your opponent is heedless of the
potential danger and may hit the junction box or lose his
balance and fall, if his attack against you fails. (On the other
hand, if the attack succeeds, it might slam you into the junc-
tion box or send you flying off the edge. Youâ€™re taking a risk.)
More than one degree of failure on the Deception check
means you put yourself in a bad position; you are vulner-
able against the targetâ€™s attacks until the start of your next
round!

## Knowledge & Awareness Skill

Knowledge & Awareness Skill groups three skills that derive value from accumulated knowledge, active research, and attentiveness: Expertise (professional and scholarly knowledge in a named field — Intellect, Trained Only), Investigation (searching, evidence analysis, information gathering, surveillance — Intellect, Trained Only), and Perception (noticing things across all sense types, detecting disguises and concealed objects — Awareness, untrained allowed). All three are information-gathering mechanisms: Expertise retrieves stored knowledge, Investigation actively searches and analyzes, and Perception passively or reactively notices the environment.

This KA has deep connections to other skills: Deception creates disguises that Perception detects; Investigation searches for objects hidden by Sleight of Hand; Investigation surveillance sets the DC for Stealth evasion; Expertise can default to related areas with circumstance penalties. Insight is separated from this KA because its primary function is social resistance, not information gathering. Invariants: Expertise and Investigation are Trained Only; Perception is untrained-allowed; the GM routinely makes Perception and Investigation checks secretly.

#### Decisions made

- Insight placed in Interaction Skill KA — its description is dominated by social resistance functions; its information-gathering role (Detect Illusion, Evaluate) is secondary.
- Expertise, Investigation, and Perception all pass the independence test — each is a separately-named skill with its own DC tables and use cases.
- Open question: Expertise ability-modifier flexibility (GM may require Dexterity for technical tasks, Presence for performance) creates ambiguity in character construction — flagged for object-model phase.

### Expertise
Intellect â€¢ Trained Only
Expertise is a broad skill encompassing knowledge and
training in a variety of specialized fields, particularly pro-
fessional disciplines and scholarship. Each is considered a
separate skill and training in each is acquired separately,
so a former police officer turned district attorney might
have Expertise: Police Officer and Expertise: Law, each
with their own ranks, for example.
If you are trained in an Expertise, you can practice and
make a living at it. You know how to use the tools of that
trade, perform the professionâ€™s daily tasks, supervise un-
trained helpers, and handle common problems. For ex-
ample, someone trained in Expertise: Sailor knows how
to tie basic knots, tend and repair sails, and stand a deck
watch at sea. The GM sets DCs for specific tasks using the
guidelines provided in The Basics chapter under Checks,
keeping in mind that most job-related checks should be
considered routine (see Routine Checks in that section).
You can also make Expertise checks to see if your charac-
ter knows the answer to a particular question related to
the area of expertise, such as a scientist confronted with
a technical issue, or a lawyer considering a legal question.
The DC is 10 for easy questions, 15 for basic questions, and
20 or higher for difficult questions. You can usually answer
questions as a routine check, and the GM may make a
check for you in secret, so you wonâ€™t know whether or not
your characterâ€™s skill is entirely up to the task.
Expertise covers all areas except those tasks specifically
covered by other skills. So, for example, a police detec-
tive is going to be trained in Investigation (and probably
Insight and Perception) in addition to Expertise: Police
Officer, the same for an intrepid reporter with Expertise:
Journalism. A scientist might be trained in Technology

alongside Expertise: Science, a doctor needs training in
Treatment along with Expertise: Physician, and a trial law-
yer is going to want skill in Insight and Persuasion (and
possibly Deception) along with the training in the law that
comes with Expertise: Lawyer.
The ability modifier for Expertise is typically Intellect, but
some areas of expertise may call for different abilities, per-
haps depending on the task involved. For example, a tech-
nical expert might rely on Intellect to answer questions
and handle day-to-day procedures, but need Dexterity
to perform the actual functions of the job. Performance
skills, such as acting or music, may rely on Presence. The
GM sets the ability modifier as needed for the specific Ex-
pertise check.
Characters with expertise in a profession are also assumed
to be licensed or certified to practice it, if necessary. Prob-
lems like licensing issues, professional rivalries, and so
forth can be handled as complications (see Complica-
tions in the Characteristics chapter).
The GM may allow some Expertise checks to be made un-
trained, especially for â€œunskilledâ€ areas, measuring broad
general knowledge and life experience, but even then
an untrained Expertise check cannot be routine, and the
character can only handle easy or basic tasks or questions
(DC 10-15).
```

---

### Expertise

#### Domain Language

- Expertise is a Trained Only skill based on Intellect representing specialized professional or scholarly knowledge; each area is a separate skill.
- A trained character can practice and make a living at it: use tools of the trade, perform daily tasks, supervise helpers, handle common problems.
- Expertise checks answer knowledge questions: easy DC 10, basic DC 15, difficult DC 20+; most job-related checks are routine.
- The ability modifier is typically Intellect, but the GM may require a different ability based on the specific check.
- Some Expertise areas can be used untrained for general knowledge, but untrained checks cannot be routine (DC 10-15 only).
- Expertise covers professional knowledge not captured by other skills; professionals often need complementary skills (Investigation for detectives, Technology for scientists, Treatment for doctors).
- The GM may allow defaulting to a related Expertise at a circumstance penalty (-2 related, -5 loosely related).

#### References

**Ref — Innuendo Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_051.md
Locator: lines 3284-3373
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Innuendo Difficulties"
chunk_index: 51
line_range: "3284-3373"
---

### Innuendo Difficulties
DC
TASK
Basic message
Complex message
Message containing new or detailed information
Anyone listening in on your innuendo can attempt a In-
sight check against the message DC. If successful, the
eavesdropper notices a message hidden in your conversa-
tion. If the eavesdropper gets at least two degrees of suc-
cess, he also understands the message. Whether trying to
send or pick up on a message, more than one degree of
failure on the check means the receiver misinterprets the
message in some fashion.
TRICKING
You can use Deception to mislead an opponent into taking
a potentially unwise action, such as trying to hit you while
standing in front of an electrical junction box or at the edge
of a precipice. If your Deception check opposed by Decep-
tion or Insight succeeds, your opponent is heedless of the
potential danger and may hit the junction box or lose his
balance and fall, if his attack against you fails. (On the other
hand, if the attack succeeds, it might slam you into the junc-
tion box or send you flying off the edge. Youâ€™re taking a risk.)
More than one degree of failure on the Deception check
means you put yourself in a bad position; you are vulner-
able against the targetâ€™s attacks until the start of your next
round!

### Expertise
Intellect â€¢ Trained Only
Expertise is a broad skill encompassing knowledge and
training in a variety of specialized fields, particularly pro-
fessional disciplines and scholarship. Each is considered a
separate skill and training in each is acquired separately,
so a former police officer turned district attorney might
have Expertise: Police Officer and Expertise: Law, each
with their own ranks, for example.
If you are trained in an Expertise, you can practice and
make a living at it. You know how to use the tools of that
trade, perform the professionâ€™s daily tasks, supervise un-
trained helpers, and handle common problems. For ex-
ample, someone trained in Expertise: Sailor knows how
to tie basic knots, tend and repair sails, and stand a deck
watch at sea. The GM sets DCs for specific tasks using the
guidelines provided in The Basics chapter under Checks,
keeping in mind that most job-related checks should be
considered routine (see Routine Checks in that section).
You can also make Expertise checks to see if your charac-
ter knows the answer to a particular question related to
the area of expertise, such as a scientist confronted with
a technical issue, or a lawyer considering a legal question.
The DC is 10 for easy questions, 15 for basic questions, and
20 or higher for difficult questions. You can usually answer
questions as a routine check, and the GM may make a
check for you in secret, so you wonâ€™t know whether or not
your characterâ€™s skill is entirely up to the task.
Expertise covers all areas except those tasks specifically
covered by other skills. So, for example, a police detec-
tive is going to be trained in Investigation (and probably
Insight and Perception) in addition to Expertise: Police
Officer, the same for an intrepid reporter with Expertise:
Journalism. A scientist might be trained in Technology

alongside Expertise: Science, a doctor needs training in
Treatment along with Expertise: Physician, and a trial law-
yer is going to want skill in Insight and Persuasion (and
possibly Deception) along with the training in the law that
comes with Expertise: Lawyer.
The ability modifier for Expertise is typically Intellect, but
some areas of expertise may call for different abilities, per-
haps depending on the task involved. For example, a tech-
nical expert might rely on Intellect to answer questions
and handle day-to-day procedures, but need Dexterity
to perform the actual functions of the job. Performance
skills, such as acting or music, may rely on Presence. The
GM sets the ability modifier as needed for the specific Ex-
pertise check.
Characters with expertise in a profession are also assumed
to be licensed or certified to practice it, if necessary. Prob-
lems like licensing issues, professional rivalries, and so
forth can be handled as complications (see Complica-
tions in the Characteristics chapter).
The GM may allow some Expertise checks to be made un-
trained, especially for â€œunskilledâ€ areas, measuring broad
general knowledge and life experience, but even then
an untrained Expertise check cannot be routine, and the
character can only handle easy or basic tasks or questions
(DC 10-15).
```

---

### Insight

#### Domain Language

- Insight is a skill based on Awareness; it may be used untrained; it covers reading intentions, detecting influence, evaluating trustworthiness, picking up innuendo, and resisting social manipulation.
- Detect Illusion: GM makes a secret Insight check (DC 10 + Illusion rank) to sense an illusions true nature.
- Detect Influence: Insight check (DC 10 + rank of the affecting effect or skill) to notice a subject acting under outside influence; three or more degrees give a general idea of the source.
- Evaluate: Insight check opposed by Deception to assess trustworthiness; DC 20 to evaluate a social situations mood; two or more degrees of failure causes misinterpretation.
- Innuendo: Insight is used to pick up on hidden Deception messages at the same DC as the sending check.
- Resist Influence: Insight check resists effects of interaction skills (Deception, Intimidation); if Insight result exceeds the opponents skill result, the character is unaffected.
- Insight checks are generally free actions; may be used as reactions against incoming interaction skill use.

#### References

**Ref — Insight**
Source: context/rules/HeroesHandbook-rules__chunk_052.md
Locator: lines 3374-3440
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Insight"
chunk_index: 52
line_range: "3374-3440"
---

### Insight
Awareness
You can tell someoneâ€™s true intentions and feelings by
paying attention to things like body language, inflection,
and your own intuition.
A successful Insight check allows you to resist the effects of
some interaction skills, becoming aware of the other personâ€™s
true intent. You can also use the skill to tell when someone is
behaving oddly or for assessing trustworthiness.

### Detect Illusion
The GM makes a secret Insight check to determine if your
hero senses the true nature of an illusion (DC 10 + Illusion
rank). Success means you pick up on a flaw in the illusion,
sensing it is not real. See the Illusion effect in the Powers
chapter for details.

### Detect Influence
You can make a Insight check to notice someone act-
ing under outside influence. The DC is 10 + the rank of
the effect or skill affecting the subject. If you succeed,
UNDER THE HOOD: CHARACTER EXPERTISE VS. PLAYER EXPERTISE
Expertise skills measure what your character knows about various things, whether you know anything about them or not.
Itâ€™s fairly easy to measure what a hero knows by making the appropriate skill check or looking at the routine check value
of (bonus +10).
However, players may know things their characters do not, either because of the playerâ€™s life experience or knowledge
of the game and its rules (and source material). In this case the Gamemaster may prefer players limit themselves to
only what Expertise skills their heroes have rather than what they may or may not know about a given situation. The
GM may bend this rule by allowing a player to spend a hero point to have a character act upon something he or she
would have no way of knowing, calling it a â€œhunchâ€ or a â€œlucky guessâ€ (a version of the inspiration rule). See the Hero
Points section for guidelines.
If thereâ€™s a question as to how to handle an issue of player versus character expertise in the game, consult your Gamemaster.

### Sample Areas Of Expertise
The following are examples of suitable areas of Expertise. This list is by no means exhaustive, the GM should feel free to
add to or modify this list as needed to suit the game and the characters in it.
Art, Business, Carpentry, Cooking, Criminal, Current Events, Dance, History, Journalism, Law, Law Enforcement, Medicine, Mili-
tary, Music, Magic, Philosophy, Politics, Popular Culture, Psychiatry, Science, Sociology, Streetwise, Theology

### Defaulting To Related Areas Of Expertise
On occasion, the GM may decide that training in an Expertise skill provides some ability to deal with tasks covered by
other, related, skills with a circumstance penalty to the skill check.
Example: Figuring out a particular clue involving a government conspiracy requires an Investigation or Expertise: Poli-
tics check. However, the GM allows a hero to substitute an Expertise: Law check with a â€“2 circumstance penalty, as the
knowledge is related, but outside the characterâ€™s specific field. Expertise: Journalism might suffer a â€“5 penalty, but could
still be useful (especially if the character works a legal or political beat as a reporter), while Expertise: Cooking is no help
at all, and cannot be used for the check (unless the player comes up with a very clever explanation!)

you notice the subject is not acting entirely of his or her
own will. Three or more degrees give you a general idea
of what is influencing them (and perhaps even whom,
depending on the situation and the Gamemasterâ€™s judg-
ment).
EVALUATE
With an Insight check, opposed by Deception, you can
tell if someone is trustworthy and honorable (or not)
upon meeting them. You can also make an Insight check
(DC 20) to evaluate a social situation, getting a feel for
the overall mood and prevailing attitudes. Two or more
degrees of failure on either check mean you misinterpret
the signs, so the GM may make these checks for you in
secret.
INNUENDO
You can use Insight to pick up on hidden messages sent
via the Deception skill (see the Deception skill descrip-
tion).
```

**Ref — Resist Influence**
Source: context/rules/HeroesHandbook-rules__chunk_053.md
Locator: lines 3441-3484
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Resist Influence"
chunk_index: 53
line_range: "3441-3484"
---

### Resist Influence
Make an Insight check when called to do so to resist or
overcome the effects of certain interaction skills, such
as Deception or Intimidation. If the result of your check
exceeds your opponentâ€™s, you are unaffected by their at-
tempt to influence you.

### Intimidation
Presence â€¢ Interaction
You know how to use threats (both real and implied) to
get others to do what you want.
COERCING
Make an Intimidation check, opposed by the targetâ€™s In-
sight or Will defense (whichever has the highest bonus). If
your check succeeds, you may treat the target as friendly,
but only for actions taken in your presence. That is, the tar-
get retains his normal attitude, but will talk, advise, offer
limited help, or advocate on your behalf while intimidated.
The target cooperates, but wonâ€™t necessarily obey your ev-
ery whim or do anything that would directly endanger him.
Properly intimidating someone takes time and an appro-
priately violent action or threat. Uses of Intimidation in ac-
tion rounds are generally standard actions, although you
can attempt to deceive as a move action by taking a â€“5
penalty to your check.
If you perform some action that makes you more impos-
ing, you gain a circumstance bonus on your Intimidation
check. If your target clearly has a superior position, you
suffer a circumstance penalty.
With more than one degree of failure on your check, the
target may actually do the opposite of what you want! Suc-

ceed or fail, a targetâ€™s true attitude towards you generally
becomes hostile after you attempt an Intimidation check,
even if they go along with you for the moment.
DEMORALIZING
You can use Intimidation in combat as a standard action
to undermine an opponentâ€™s confidence. Make an Intimi-
dation check as a standard action. If it succeeds, your tar-
get is impaired (a â€“2 circumstance penalty on checks) un-
til the end of your next round. With four or more degrees
of success, the target is disabled (a â€“5 penalty) until the
end of your next round.
```

---

### Intimidation

#### Domain Language

- Intimidation is an interaction skill based on Presence; it covers using threats to coerce compliance or demoralize opponents.
- Coercing: Intimidation check opposed by targets Insight or Will defense (whichever is higher); success treats target as friendly for actions in the users presence only; targets true attitude becomes hostile after the attempt; more than one degree of failure causes the opposite effect.
- Demoralizing: standard action check in combat; success imposes the impaired condition (-2 penalty on checks) until end of users next round; four or more degrees imposes disabled (-5 penalty) until end of users next round.
- Intimidating Minions: a single check against a whole group that can see and hear the user; compared to a single GM resistance check for the group; the effect must be the same for all members.
- An imposing action before the check grants a circumstance bonus; a clearly superior target position imposes a circumstance penalty.
- Uses in action rounds are standard actions; may be attempted as a move action at -5 penalty.

#### References

**Ref — Resist Influence**
Source: context/rules/HeroesHandbook-rules__chunk_053.md
Locator: lines 3441-3484
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Resist Influence"
chunk_index: 53
line_range: "3441-3484"
---

### Resist Influence
Make an Insight check when called to do so to resist or
overcome the effects of certain interaction skills, such
as Deception or Intimidation. If the result of your check
exceeds your opponentâ€™s, you are unaffected by their at-
tempt to influence you.

### Intimidation
Presence â€¢ Interaction
You know how to use threats (both real and implied) to
get others to do what you want.
COERCING
Make an Intimidation check, opposed by the targetâ€™s In-
sight or Will defense (whichever has the highest bonus). If
your check succeeds, you may treat the target as friendly,
but only for actions taken in your presence. That is, the tar-
get retains his normal attitude, but will talk, advise, offer
limited help, or advocate on your behalf while intimidated.
The target cooperates, but wonâ€™t necessarily obey your ev-
ery whim or do anything that would directly endanger him.
Properly intimidating someone takes time and an appro-
priately violent action or threat. Uses of Intimidation in ac-
tion rounds are generally standard actions, although you
can attempt to deceive as a move action by taking a â€“5
penalty to your check.
If you perform some action that makes you more impos-
ing, you gain a circumstance bonus on your Intimidation
check. If your target clearly has a superior position, you
suffer a circumstance penalty.
With more than one degree of failure on your check, the
target may actually do the opposite of what you want! Suc-

ceed or fail, a targetâ€™s true attitude towards you generally
becomes hostile after you attempt an Intimidation check,
even if they go along with you for the moment.
DEMORALIZING
You can use Intimidation in combat as a standard action
to undermine an opponentâ€™s confidence. Make an Intimi-
dation check as a standard action. If it succeeds, your tar-
get is impaired (a â€“2 circumstance penalty on checks) un-
til the end of your next round. With four or more degrees
of success, the target is disabled (a â€“5 penalty) until the
end of your next round.
```

**Ref — Intimidating Minions**
Source: context/rules/HeroesHandbook-rules__chunk_054.md
Locator: lines 3485-3527
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Intimidating Minions"
chunk_index: 54
line_range: "3485-3527"
---

### Intimidating Minions
You can intimidate a whole group of minionsâ€”who can
all see and hear youâ€”with a single check. If the group has
you at a disadvantage, you suffer the usual circumstance
penalty on your check. Compare your check result against
a single resistance check made by the GM for the entire
group. Your Intimidation check must have the same effect
on every member of the group (that is, you cannot demor-
alize some and coerce others, for example).
Example: Rocky is facing down Pack-Rat in one
of his many bolt holes around Emerald City when
the big rat commands a pack of his street thieves
to keep Rocky from following him. The gang of kids
steps forward to get in Rockyâ€™s way. Rocky has no
interest in hurting a bunch of kids, so he bellows,
â€œGet outta the way or Iâ€™ll knock your blocks off!â€
and his player decides to use Rockyâ€™s routine Intimi-
dation check of 18 to attempt to coerce the entire
group of minions into moving out of his way. The
street kids are all Thugs, so they have a resistance
rank of 0 (their Insight and Will ranks are tied).
Since Rocky is attempting the same effect on every
member of the group, he makes a single opposed
check. Unfortunately, the GM rolls a 13, which isnâ€™t
enough to beat Rockyâ€™s 18. The street kids know
Rocky wonâ€™t actually hurt them, but they dive out
of the way anyway as Rocky bulls past.â€

### Investigation
Intellect â€¢ Trained Only
You know how to search for and study clues, gather in-
formation through interviews and surveillance, and ana-
lyze evidence to help solve crimes. The GM may make In-
vestigation checks for you in secret, so you do not know
exactly what you have found, or if you may have missed
something.
SEARCH
You can search an area for clues, hidden items, traps, and
other details. Perception allows you to immediately notice
things, while an Investigation check allows you to pick up
on details with some effort.
```

---

### Investigation

#### Domain Language

- Investigation is a Trained Only skill based on Intellect covering searching for clues, gathering information, interviewing contacts, surveillance, and forensic analysis.
- Search: an Investigation check picks up on area details with effort; DC scales from low (ransacking a room) to 25+ (extremely obscure clues); concealed objects DC opposed by hiders Stealth or Sleight of Hand.
- Gather Evidence: DC 15 to collect evidence; failure allows analysis at -5; more than one degree of failure ruins evidence; two or more degrees of success grant +2 to later analysis.
- Analyze Evidence: DC 15 to extract useful information; DC modified by time elapsed and scene disturbance; does not create clues where none exist.
- Gather Information: DC 10+ taking at least one hour; degree of success determines information type (general / specific / restricted / protected); more than one degree of failure may alert those being investigated.
- Surveillance: a stationary Investigation check result becomes the DC of a subjects Stealth check to evade detection.
- The GM may make Investigation checks secretly.

#### References

**Ref — Intimidating Minions**
Source: context/rules/HeroesHandbook-rules__chunk_054.md
Locator: lines 3485-3527
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Intimidating Minions"
chunk_index: 54
line_range: "3485-3527"
---

### Intimidating Minions
You can intimidate a whole group of minionsâ€”who can
all see and hear youâ€”with a single check. If the group has
you at a disadvantage, you suffer the usual circumstance
penalty on your check. Compare your check result against
a single resistance check made by the GM for the entire
group. Your Intimidation check must have the same effect
on every member of the group (that is, you cannot demor-
alize some and coerce others, for example).
Example: Rocky is facing down Pack-Rat in one
of his many bolt holes around Emerald City when
the big rat commands a pack of his street thieves
to keep Rocky from following him. The gang of kids
steps forward to get in Rockyâ€™s way. Rocky has no
interest in hurting a bunch of kids, so he bellows,
â€œGet outta the way or Iâ€™ll knock your blocks off!â€
and his player decides to use Rockyâ€™s routine Intimi-
dation check of 18 to attempt to coerce the entire
group of minions into moving out of his way. The
street kids are all Thugs, so they have a resistance
rank of 0 (their Insight and Will ranks are tied).
Since Rocky is attempting the same effect on every
member of the group, he makes a single opposed
check. Unfortunately, the GM rolls a 13, which isnâ€™t
enough to beat Rockyâ€™s 18. The street kids know
Rocky wonâ€™t actually hurt them, but they dive out
of the way anyway as Rocky bulls past.â€

### Investigation
Intellect â€¢ Trained Only
You know how to search for and study clues, gather in-
formation through interviews and surveillance, and ana-
lyze evidence to help solve crimes. The GM may make In-
vestigation checks for you in secret, so you do not know
exactly what you have found, or if you may have missed
something.
SEARCH
You can search an area for clues, hidden items, traps, and
other details. Perception allows you to immediately notice
things, while an Investigation check allows you to pick up
on details with some effort.
```

**Ref — Search Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_055.md
Locator: lines 3528-3571
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Search Difficulties"
chunk_index: 55
line_range: "3528-3571"
---

### Search Difficulties
DC

### Sample Search
Ransack an area to find a certain object.
Notice a secret compartment, simple trap, or an
obscure clue.
25+
Find a well-hidden secret compartment or trap,
or an extremely obscure clue.
To determine how long it takes to search a given area, take
the total area measurement (in square feet, yards, or miles),
find the time measurement for that distance, and add 2.
So searching 60 square feet (roughly an 8 ft. by 8 ft. room)
takes the time rank of 60 feet (rank 1), plus 2, or 1 minute
(time rank 3). Searching a square mile takes the time rank of
1 mile (rank 8), plus 2, or two hours (time rank 10).
The DC for an Investigation check to find a concealed ob-
ject is usually opposed by the Stealth or Sleight of Hand
check of the character who hid it.

### Gather Evidence
To collect a piece of evidence for analysis, make an Investi-
gation check (DC 15). If the check succeeds, the evidence
can be analyzed (see the following). If the check fails, an
analysis can be done, but with a â€“5 penalty for highly
unfavorable circumstances. With more than one degree
of failure, the evidence is ruined and no analysis can be
done. On the other hand, two or more degrees of success
provide a +2 circumstance bonus to later analysis.

### Analyze Evidence
You can make an Investigation check to apply forensic
knowledge to evidence. This function of Investigation
does not give you clues where none exist. It simply allows
you to extract useful information from evidence and clues
you have found.
The base DC 15, modified by the time elapsed since the
evidence was left, and whether or not the scene was dis-
turbed. Success gives you information based on the clue
(and determined by the GM). Two or more degrees of fail-
ure may provide misleading or confusing evidence, also at
the GMâ€™s discretion.
```

**Ref — Evidence Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_056.md
Locator: lines 3572-3638
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Evidence Difficulties"
chunk_index: 56
line_range: "3572-3638"
---

### Evidence Difficulties
DC
TASK
Analyze Evidence
Gather Evidence

### Modifiers
+2
Every day since event (max modifier +10)
+5
Crime scene is outdoors
+2
Crime scene disturbed
+5
Crime scene highly disturbed

### Gather Information
You know how to make contacts, collect gossip and ru-
mors, question informants, and otherwise get information
from people.
By succeeding at a DC 10 Investigation check taking at
least an hour, you get a feel for the major news and ru-
mors in an area. This assumes no obvious reasons exist
why information would be withheld. The degree of the
check result determines the completeness and detail of
the information. Information ranges from general to pro-
tected, and the DC increases accordingly for the type of
information, as given on the table.

### Gather Information Results

### Degree Of Success

### Type Of Information
One
General
Two
Specific
Three
Restricted
Four
Protected
â€¢
General information concerns local happenings, ru-
mors, gossip, and the like.
â€¢
Specific information usually relates to a particular
question.
â€¢
Restricted information isnâ€™t generally known and re-
quires you to locate someone with access to the in-
formation.
â€¢
Protected information is even harder to come by and
might involve some danger, either for the one asking
the questions or the one providing the answers.
Failure on the Investigation check means you waste time
turning up nothing of value. An additional degree of failure
means you also alert someone who may be interested in
your inquiries, perhaps even someone you are investigating!
SURVEILLANCE
You can set up surveillance of a particular area, watching
from a stationary location. The DC of the subjectâ€™s Stealth
check to evade your notice is equal to the result of your
Investigation check. For actively following a subject, see
Tailing in the Stealth skill description.
```

---

### Perception

#### Domain Language

- Perception is a skill based on Awareness; it may be used untrained; it covers noticing and picking up on things in the environment across all sense types.
- Distance penalty: -1 circumstance penalty for every 10 feet between the character and what they try to perceive.
- Hearing: DC based on loudness (normal conversation DC 0, soft noise DC 10); through a door adds +5, through a solid wall +15; waking from sleep adds +10.
- Seeing: DC based on visibility (plain sight DC 0, subtle DC 5-10+); used to detect disguises (opposed by Deception) and concealed objects (opposed by Sleight of Hand).
- Discerning fine details requires at least three degrees of success.
- The GM usually makes Perception checks secretly.
- A character may retry a previously failed Perception check as a move action.
- Perception applies to all sense types defined in the Powers chapter.

#### References

**Ref — Perception**
Source: context/rules/HeroesHandbook-rules__chunk_057.md
Locator: lines 3639-3682
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Perception"
chunk_index: 57
line_range: "3639-3682"
---

### Perception
Awareness
Use this skill to notice and pick up on things. Discerning
detailsâ€”such as clearly hearing conversation or reading
fine textâ€”requires at least three degrees of success on
the Perception check.
In general, you have a â€“1 circumstance penalty to Percep-
tion checks for every 10 feet between you and what you are

trying to perceive. So hearing a noise from 50 feet away is a
â€“5 modifier to your Perception check, for example.
The GM usually makes Perception checks secretly so you
donâ€™t know whether there was nothing to notice or you
simply failed to notice it. The common sorts of Perception
checks are:
HEARING
Make a check against a DC based on how loud the noise
is or against an opposed Stealth check. Normal conversa-
tion is DC 0, a soft noise DC 10. Listening through a door
is +5 DC, +15 for a solid wall. While youâ€™re asleep, hearing
something well enough to wake up is +10 DC.
SEEING
Make a check against a DC based on how visible the ob-
ject is or against an opposed Stealth check. Something in
plain sight is DC 0, while something subtle or easily over-
looked may be DC 5, 10 or more. Visual perception is also
used to detect someone in disguise (see the Deception
skill) or to notice a concealed object (see the Sleight of
Hand skill).

### Other Senses
You can make Perception checks involving other sense
types as well (see the Powers chapter for more on sense
types). Noticing something obvious to a sense is DC 0.
Less obvious things are DC 10 or so, hidden things DC 20
or more, and discerning details requires at least three de-
grees of success, as usual.
You can make a Perception check every time you have the
opportunity to notice something new. As a move action,
you can attempt to notice something you failed (or be-
lieve you failed) to notice previously.
Various sensory effects provide modifiers on Perception
checks (see the Powers chapter for details).
```

---

### Persuasion

#### Domain Language

- Persuasion is an interaction skill based on Presence covering social graces, etiquette, negotiation, and winning others over.
- Improving attitudes: DC 15 check improves an NPCs attitude by one step; each two additional degrees improve by one more step; failure equals no change; more than one degree of failure worsens attitude by one step.
- NPC attitudes form a five-step scale: Hostile to Unfavorable to Indifferent to Favorable to Helpful.
- In negotiations, all participants roll Persuasion and compare results; opposed checks resolve competing advocacy before a third party.
- A successful Persuasion check takes at least a standard action and usually longer; the GM may forbid persuasion once combat begins.
- Each argument can only be attempted once per scene; retrying after failure requires a changed situation.

#### References

**Ref — Persuasion**
Source: context/rules/HeroesHandbook-rules__chunk_058.md
Locator: lines 3683-3761
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Persuasion"
chunk_index: 58
line_range: "3683-3761"
---

### Persuasion
Presence â€¢ Interaction
Youâ€™re skilled in dealing with people, from etiquette and
social graces to a way with words and public speaking,
all of which helps to get your point across, make a good
impression, negotiate, and generally win people over to
your way of seeing things.
In negotiations, all participants roll Persuasion checks to
see who gains the advantage. Opposed checks also re-
solve cases where two advocates plead opposing cases
before a third party.
Non-player characters each have an initial attitude to-
wards you or your cause. The GM chooses the characterâ€™s
initial attitude based on circumstances. Most of the time,

people are favorable or indifferent toward heroes, but a
specific circumstance or complication may call for a dif-
ferent attitude.
You can improve othersâ€™ attitudes with a DC 15 Persua-
sion check. Success improves the subjectâ€™s attitude by
one step, while every two additional degrees of success
improve it by another step (so two steps at three degrees,
three steps at five degrees, and so forth). Failure means
no change, and more than a degree of failure worsens the
subjectâ€™s attitude by one step! In the case of a hostile sub-
ject, they may outright attack or otherwise interfere with
you if their attitude worsens.
ATTITUDES
ATTITUDE
EFFECT
Hostile
Will take risks to attack
or interfere with you.
Unfavorable
Will insult, mislead,
or otherwise cause you trouble.
Indifferent
Acts as socially expected
towards you.
Favorable
Will chat, advise,
and offer limited help.
Helpful
Will take risks to
help or protect you.
Persuading someone is at least a standard action, usually
quite a bit longer. The GM decides if you can persuade at
all once a conflict has broken out! Even if the initial check
succeeds, the other character can only be persuaded so
far; you can try again in the same scene, but you check
against the subjectâ€™s initial attitude, and may end up wors-
ening it rather than improving it!
Example: The heroes must convince the imperi-
ous King of Atlantis that the surface world is not
responsible for recent attacks against his king-
dom in order to avert a war. The kingâ€™s attitude
is unfavorable towards these surface-world in-
terlopers  to begin with. The teamâ€™s spokesperson
makes a Persuasion attempt and gets a check
result of 22, a success with two degrees total.
That shifts the kingâ€™s attitude one step, to indif-
ferent. Heâ€™s inclined to continue negotiating with
the heroes and willing to place the assault on the
surface world on-hold for the time-being. The he-
roes try to convince the king further, but any ad-
ditional checks need at least the same degree of
success as the first to get his attitude to favorable,
where he is willing to call off the attack, and more
than one degree of failure on any check moves his
attitude to hostile, where he orders the intruders
arrested and the attack to begin at once!
If a Persuasion check fails, trying again is futile; the subject
is too set against your arguments. At the GMâ€™s discretion,
you can try again when the situation changes in some
way: you find a new approach to your argument, new
evidence appears, and so forth. The GM may consider you
at a disadvantage in further negotiations, imposing a cir-
cumstance penalty as well.
```

---

### Ranged Combat

#### Domain Language

- Ranged Combat is a skill based on Dexterity; it may be used untrained; each Ranged Combat skill is specific to a single weapon or power.
- The skill rank adds to attack checks for that specific weapon or power only; it does not apply to defense.
- Ranged Combat: Throwing covers thrown weapons and thrown objects.
- An array of powers may be treated as one power for Ranged Combat purposes at the GMs discretion.
- For a broader bonus across all ranged attacks, see the Ranged Attack advantage.

#### References

**Ref — Ranged Combat**
Source: context/rules/HeroesHandbook-rules__chunk_059.md
Locator: lines 3762-3826
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Ranged Combat"
chunk_index: 59
line_range: "3762-3826"
---

### Ranged Combat
Dexterity
Youâ€™re trained with a particular type of ranged attack,
giving you a bonus to your attack checks with it equal
to your skill rank (see Attack Check in The Basics and
in the Action & Adventure chapter). Each ranged attack
is a separate Ranged Combat skill with its own rank, and
encompasses a single weapon or power, although an ar-
ray may be considered one power, at the Gamemasterâ€™s
discretion (see Arrays in the Powers chapter for more
information).
So a hero might have Ranged Combat: Guns or Ranged
Combat: Fire Control, but Ranged Combat: Powers is too
broad. Ranged Combat: Throwing is an option and in-
cludes both thrown weapons and objects a character sim-
ply picks up and throws.
The bonus from a Ranged Combat skill applies only to at-
tack checks with the particular attack, not to defenses. For
a broader bonus to attack checks that is less than simply
raising Dexterity rank, see the Ranged Attack advantage
in the Advantages chapter.

### Sleight Of Hand
Dexterity â€¢ Manipulation â€¢ Trained Only
You can perform dexterous feats of legerdemain such as
palming small objects, picking pockets, slipping out of
restraints, and so forth. Stage magicians use Sleight of
Hand legitimately as a performance skill, but it is most
commonly known for its criminal applications.
CONCEALING
You can use Sleight of Hand to conceal a small item on
your person, making your check result the DC of an Inves-
tigation or Perception check to find it.
CONTORTING
You can use Slight  of Hand to contort your body. Make a
DC 30 Sleight of Hand check to fit through a tight space
wide enough for your head but too narrow for the width
of your shoulders, or to reach through an opening wide
enough for your hand, but too narrow for your arm.
ESCAPING
Make a Sleight of Hand check to slip out of various re-
straints. This takes at least a minute per check.

You can also make a Sleight of Hand check to plant a small
object on someone, slip something into their pocket, drop
something into their drink, place a tiny radio tracer on them,
and so forth. To plant the object, you must get a check result
of 20 or higher, regardless of the opponentâ€™s check result.
The opponent notices the attempt if his check result beats
yours, whether you succeed in planting the item or not.
Example: The Rubber-Bandit is robbing a muse-
um of some of its valuables when a security guard
passes by while making his rounds. The bouncing
Bandit has no fear of the rent-a-cop, so he decides
to have some fun. He has Skill Mastery for his Stealth
and, unsurprisingly, the guard doesnâ€™t notice him
slither closer, but then the Rubber-Bandit decides to
try and steal the guardâ€™s gun without being noticed.
Bandit has Sleight of Hand +12 and adds that to the
roll of a die. A whopping 19 plus 12 for a total of 31!
The guard, with a Perception skill of only +5, doesnâ€™t
have a prayer of noticing his gun being eased out of
its holster, but the GM rolls anyway and gets a total
of 20. A good roll, but no enough.
```

---

### Sleight of Hand

#### Domain Language

- Sleight of Hand is a Trained Only manipulation skill based on Dexterity covering legerdemain, pickpocketing, concealment, contortion, and escape.
- Concealing: Sleight of Hand check result becomes the DC for Investigation or Perception checks to find the concealed item.
- Contorting: DC 30 to fit through a tight space wide enough for the head but not shoulders.
- Escaping: check to slip out of restraints; takes at least one minute per check; DC varies by restraint type.
- Legerdemain: minor feats have DC 10 unless an observer is focused; under observation, opposed by the observers Perception.
- Planting objects: requires a check result of 20 or higher to successfully plant; target notices the attempt if their Perception beats the users check.
- Stealing: DC 20 to take something covertly from a person; opposed by targets Perception.

#### References

**Ref — Ranged Combat**
Source: context/rules/HeroesHandbook-rules__chunk_059.md
Locator: lines 3762-3826
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Ranged Combat"
chunk_index: 59
line_range: "3762-3826"
---

### Ranged Combat
Dexterity
Youâ€™re trained with a particular type of ranged attack,
giving you a bonus to your attack checks with it equal
to your skill rank (see Attack Check in The Basics and
in the Action & Adventure chapter). Each ranged attack
is a separate Ranged Combat skill with its own rank, and
encompasses a single weapon or power, although an ar-
ray may be considered one power, at the Gamemasterâ€™s
discretion (see Arrays in the Powers chapter for more
information).
So a hero might have Ranged Combat: Guns or Ranged
Combat: Fire Control, but Ranged Combat: Powers is too
broad. Ranged Combat: Throwing is an option and in-
cludes both thrown weapons and objects a character sim-
ply picks up and throws.
The bonus from a Ranged Combat skill applies only to at-
tack checks with the particular attack, not to defenses. For
a broader bonus to attack checks that is less than simply
raising Dexterity rank, see the Ranged Attack advantage
in the Advantages chapter.

### Sleight Of Hand
Dexterity â€¢ Manipulation â€¢ Trained Only
You can perform dexterous feats of legerdemain such as
palming small objects, picking pockets, slipping out of
restraints, and so forth. Stage magicians use Sleight of
Hand legitimately as a performance skill, but it is most
commonly known for its criminal applications.
CONCEALING
You can use Sleight of Hand to conceal a small item on
your person, making your check result the DC of an Inves-
tigation or Perception check to find it.
CONTORTING
You can use Slight  of Hand to contort your body. Make a
DC 30 Sleight of Hand check to fit through a tight space
wide enough for your head but too narrow for the width
of your shoulders, or to reach through an opening wide
enough for your hand, but too narrow for your arm.
ESCAPING
Make a Sleight of Hand check to slip out of various re-
straints. This takes at least a minute per check.

You can also make a Sleight of Hand check to plant a small
object on someone, slip something into their pocket, drop
something into their drink, place a tiny radio tracer on them,
and so forth. To plant the object, you must get a check result
of 20 or higher, regardless of the opponentâ€™s check result.
The opponent notices the attempt if his check result beats
yours, whether you succeed in planting the item or not.
Example: The Rubber-Bandit is robbing a muse-
um of some of its valuables when a security guard
passes by while making his rounds. The bouncing
Bandit has no fear of the rent-a-cop, so he decides
to have some fun. He has Skill Mastery for his Stealth
and, unsurprisingly, the guard doesnâ€™t notice him
slither closer, but then the Rubber-Bandit decides to
try and steal the guardâ€™s gun without being noticed.
Bandit has Sleight of Hand +12 and adds that to the
roll of a die. A whopping 19 plus 12 for a total of 31!
The guard, with a Perception skill of only +5, doesnâ€™t
have a prayer of noticing his gun being eased out of
its holster, but the GM rolls anyway and gets a total
of 20. A good roll, but no enough.
```

**Ref — Stealth**
Source: context/rules/HeroesHandbook-rules__chunk_060.md
Locator: lines 3827-3895
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Stealth"
chunk_index: 60
line_range: "3827-3895"
---

### Stealth
Agility
Youâ€™re skilled in going unnoticed. While using Stealth, you
can move at your speed rank minus 1 with no penalty.
Faster than that, up to your full speed, you take a â€“5 cir-
cumstance penalty to your Stealth checks.

### Escaping Difficulties
DC

### Sample Restraint
Ropes
Handcuffs
Straightjacket
15 + rank
Power Effect
Escaping from a grab is an Acrobatics or Athletics check.
See Grab in the Conflict section and Contorting, previ-
ously, for details.
LEGERDEMAIN
Minor feats of sleight of hand, such as making a coin or
playing card â€œvanish,â€ have a DC of 10 unless an observer
is focused on noticing what you are doing. When you per-
form this skill under observation, your check is opposed
by the observerâ€™s Perception check to see if they notice
the trick.
STEALING
To covertly take something from another person make a
Sleight of Hand check (DC 20). Your target makes a Per-
ception check and notices the attempt if his check result
beats yours, whether you succeed in taking the object
or not.

HIDING
If you have cover or concealment, make a Stealth check,
opposed by an observerâ€™s Perception check, to hide and
go unnoticed.
If others are aware of your presence, you canâ€™t use
Stealth to remain undetected. You can run around a
corner so you are out of sight and then use Stealth, but
others know which way you went. You canâ€™t hide at all if
you have absolutely no cover or concealment, since that
means you are standing out in plain sight. Of course, if
someone isnâ€™t looking directly at you (youâ€™re sneaking up
from behind, for example), then you have concealment
relative to that person.
A successful Deception or Intimidation check can give
you the momentary distraction needed to make a Stealth
check while people are aware of you. When others turn
their attention from you, make a Stealth check if you can
reach cover or concealment of some kind. (As a general
guideline, any such cover has to be within 1 foot for every
rank you have in Stealth.) This check, however, is at a â€“5
penalty because you have to move quickly.
TAILING
You can use Stealth to tail someone at your normal
speed. This assumes you have some cover or conceal-
ment (crowds of people, shadows, fog, etc.). If the subject
is worried about being followed, he can make a Percep-
tion check (opposed by your Stealth check) every time
he changes course (goes around a street corner, exits a
building, and so on). If he is unsuspecting, he only gets
one Perception check for the scene. If the subject notices
you, make a Deception check, opposed by Insight. If you
succeed, you manage to pass off your presence as coinci-
dence and can continue tailing. A failed Deception check,
or being noticed a second time, means the subject knows
something is up and reacts accordingly.
```

---

### Stealth

#### Domain Language

- Stealth is a skill based on Agility; it may be used untrained; it covers hiding from observers and tailing subjects without detection.
- Hiding: requires cover or concealment; Stealth check opposed by observers Perception; cannot hide when others are already aware unless a Deception or Intimidation check first creates a distraction (Stealth at -5); cannot hide in plain sight.
- Tailing: Stealth check to follow a subject at normal speed using available cover; a worried subject makes opposed Perception checks each time they change course; an unsuspecting subject gets only one check per scene.
- Speed: movement at speed rank minus 1 incurs no Stealth penalty; moving up to full speed imposes -5 circumstance penalty.
- When using Deception or Intimidation to create a distraction for hiding, cover must be within 1 foot per Stealth rank.

#### References

**Ref — Stealth**
Source: context/rules/HeroesHandbook-rules__chunk_060.md
Locator: lines 3827-3895
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Stealth"
chunk_index: 60
line_range: "3827-3895"
---

### Stealth
Agility
Youâ€™re skilled in going unnoticed. While using Stealth, you
can move at your speed rank minus 1 with no penalty.
Faster than that, up to your full speed, you take a â€“5 cir-
cumstance penalty to your Stealth checks.

### Escaping Difficulties
DC

### Sample Restraint
Ropes
Handcuffs
Straightjacket
15 + rank
Power Effect
Escaping from a grab is an Acrobatics or Athletics check.
See Grab in the Conflict section and Contorting, previ-
ously, for details.
LEGERDEMAIN
Minor feats of sleight of hand, such as making a coin or
playing card â€œvanish,â€ have a DC of 10 unless an observer
is focused on noticing what you are doing. When you per-
form this skill under observation, your check is opposed
by the observerâ€™s Perception check to see if they notice
the trick.
STEALING
To covertly take something from another person make a
Sleight of Hand check (DC 20). Your target makes a Per-
ception check and notices the attempt if his check result
beats yours, whether you succeed in taking the object
or not.

HIDING
If you have cover or concealment, make a Stealth check,
opposed by an observerâ€™s Perception check, to hide and
go unnoticed.
If others are aware of your presence, you canâ€™t use
Stealth to remain undetected. You can run around a
corner so you are out of sight and then use Stealth, but
others know which way you went. You canâ€™t hide at all if
you have absolutely no cover or concealment, since that
means you are standing out in plain sight. Of course, if
someone isnâ€™t looking directly at you (youâ€™re sneaking up
from behind, for example), then you have concealment
relative to that person.
A successful Deception or Intimidation check can give
you the momentary distraction needed to make a Stealth
check while people are aware of you. When others turn
their attention from you, make a Stealth check if you can
reach cover or concealment of some kind. (As a general
guideline, any such cover has to be within 1 foot for every
rank you have in Stealth.) This check, however, is at a â€“5
penalty because you have to move quickly.
TAILING
You can use Stealth to tail someone at your normal
speed. This assumes you have some cover or conceal-
ment (crowds of people, shadows, fog, etc.). If the subject
is worried about being followed, he can make a Percep-
tion check (opposed by your Stealth check) every time
he changes course (goes around a street corner, exits a
building, and so on). If he is unsuspecting, he only gets
one Perception check for the scene. If the subject notices
you, make a Deception check, opposed by Insight. If you
succeed, you manage to pass off your presence as coinci-
dence and can continue tailing. A failed Deception check,
or being noticed a second time, means the subject knows
something is up and reacts accordingly.
```

---

### Technology

#### Domain Language

- Technology is a Trained Only manipulation skill based on Intellect that requires tools; it covers operating, building, repairing, and sabotaging technological devices.
- Operating: routine operations do not require a check; unfamiliar devices require a check (DC 10 simple to DC 25+ highly advanced); lacking tools imposes -5.
- Building: DC and time based on complexity (Simple DC 15 / 2 hours through Advanced DC 25 / 4 days); failure wastes time and materials; time can be reduced 1 rank at -5 to the check.
- Repairing: DC is 5 lower and time rank 2 lower than building the same item.
- Jury-Rigging: DC is 10 lower than building, check is a standard action, but fixes only one problem and lasts until end of scene; must be fully repaired before it can be jury-rigged again.
- Demolitions: careful placement (at least one minute, DC 10) maximizes damage; two full degrees of success each add +5 damage to the structure.
- Security: disarms or sabotages locks, traps, and sensors; DC based on security level (simple DC 10 to super-max DC 40+); more than one degree of failure sets off the security device.
- Inventing: with the Inventor advantage, Technology can create temporary invention devices.

#### References

**Ref — Technology**
Source: context/rules/HeroesHandbook-rules__chunk_061.md
Locator: lines 3896-3943
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Technology"
chunk_index: 61
line_range: "3896-3943"
---

### Technology
Intellect â€¢ Trained Only â€¢ Manipulation â€¢ Requires Tools
Technology covers operating, building, repairing, and
generally working with technological devices and equip-
ment. Without the proper tools or equipment, you take a
â€“5 penalty to Technology checks for highly unfavorable
circumstances.
OPERATING
Most routine operations of technological equipment
donâ€™t require a skill check and can be done untrained. Us-
ing an unfamiliar device does require a check, with the DC
determined by how foreign or unusual the device is, from
simple (DC 10) to highly advanced (DC 25 or more).
BUILDING
The difficulty and time required to make an item depends
on its complexity, as shown on the Building Items table. If
your Technology check succeeds, you have made the item
after the necessary time. If the check fails, you did not pro-
duce a usable end result, and any time and materials are
wasted. More than one degree of failure on the check may
produce an accident or other unfortunate side-effect at
the GMâ€™s discretion.
REPAIRING
You can also use Technology to repair damaged items, with
a â€“5 to the DC to build the item and â€“2 to the time rank
required. So you can perform repairs on a complex item in
eight hours (time rank 12) with a DC of 20. Failure on the
check means you spend the time, but make no progress.
Two or more degrees of failure may indicate further dam-
age to the item or an accident similar to building it.
You can reduce the time rank to build or repair an item by
1 by taking a â€“5 penalty to your skill check.
JURY-RIGGING
You can also attempt jury-rigged, or temporary, repairs.
Doing this reduces the repair DC by an additional 5 (for a
total of â€“10 to the DC to build the item), and allows you to
make the Technology check as a standard action. Howev-
er, a jury-rigged repair can only fix a single problem, and
the repair only lasts until the end of the scene. The jury-
rigged item must be fully repaired thereafter, and cannot
be jury-rigged again until it is fully repaired.
DEMOLITIONS
Careful placement of an explosive against a fixed struc-
ture can maximize damage by exploiting vulnerabilities in
the structure. This requires at least a minute and a DC 10
Technology check. The GM makes the check, so you donâ€™t
know exactly how well you have done until the explosive
```

**Ref — Building Items**
Source: context/rules/HeroesHandbook-rules__chunk_062.md
Locator: lines 3944-3994
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Building Items"
chunk_index: 62
line_range: "3944-3994"
---

### Building Items
DC
COMPLEXITY

### Time Rank
EXAMPLES
Simple
10 (2 hours)
electronic timer or detonator, tripwire trap
Moderate
12 (8 hours)
radio direction finder, lock, engine component
Complex
14 (24 hours)
cell phone, combustion engine
Advanced
16 (4 days)
computer, vehicle

goes off. For every two full degrees of success, the explo-
sive deals +5 damage to the structure. Failure means the
explosive does not go off as planned, while more than one
degree of failure means the charge goes off while you are
setting it! In all cases, the explosive deals normal damage
to all other targets.
You can make an explosive device more difficult to dis-
arm. To do so, choose a disarm difficulty class before mak-
ing your check to set the detonator. Your DC to set the
detonator is the desired disarm DC. Failure means the
explosive fails to go off as planned. Two or more degrees
of failure mean the explosive goes off as the detonator is
being installed!
Disarming an explosive also requires a Technology check.
The DC is usually 10, unless the person who set the deto-
nator chose a higher disarm DC (previously). If you fail the
check, you do not disarm the explosive. With more than a
degree of failure, the explosive goes off. Setting or disarm-
ing a detonator is a standard action.
INVENTING
If you have the Inventor advantage (see the Advantages
chapter), you can use Technology to create inventions,
temporary devices. See Inventing, page 211, for details.
SECURITY
You can use Technology to disarm or sabotage various
security devices, including locks, traps, and sensors. This
takes at least a minute, possibly longer, at the GMâ€™s dis-
cretion. The GM makes your Technology check secretly
so you donâ€™t necessarily know right away if you have suc-
ceeded. The Gamemaster sets the DC of the check based
on the level of security:
```

**Ref — Security Levels**
Source: context/rules/HeroesHandbook-rules__chunk_063.md
Locator: lines 3995-4045
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Security Levels"
chunk_index: 63
line_range: "3995-4045"
---

### Security Levels
DC

### Security Example
Simple lock or home alarm system
Quality lock or home alarm system
Business and corporate security
High security: branch bank vault, museum
Very high security: bank headquarters
vault, medium prison
Maximum security: highly secure prison
Super-max security: super-prison

### Modifiers
+5
Preventing your tampering
 from being noticed.
Failure on your skill check means nothing happens, but
you can keep trying. More than one degree of failure sets
off the security or trap, if it is possible to do so.


### Treatment
Intellect â€¢ Trained Only â€¢ Manipulation â€¢ Requires Tools
Youâ€™re trained in treating injuries and ailments. The check
DC and effect of Treatment depend on the task:

### Treatment Difficulties
DC
TASK
Diagnose injuries and ailments.
Provide long-term care.
Revive dazed or stunned characters.
Stabilize dying character.
Treat diseases or poisons.
If you do not have the appropriate medical equipment
and supplies, you take a â€“5 circumstance penalty on your
check. If your subject has a particularly unusual biology
(an alien, for example) you may also suffer a circumstance
penalty.
You can use the Treatment skill on yourself, but only to
diagnose, provide care, or treat disease or poison. You
take a â€“5 circumstance penalty on checks when treating
yourself.
DIAGNOSIS
You can diagnose injuries and ailments with an eye to-
ward further treatment. This takes at least a minute. At
the GMâ€™s discretion, a successful diagnosis provides a +2
bonus for favorable circumstances on further Treatment
checks.
```

---

### Treatment

#### Domain Language

- Treatment is a Trained Only manipulation skill based on Intellect that requires tools; it covers diagnosing, caring for, reviving, stabilizing, and treating injured or ill characters.
- Diagnosis: takes at least one minute; at GMs discretion, success grants +2 to subsequent Treatment checks.
- Provide Care: treating a patient for a day or more reduces recovery time rank by 1; a character can treat up to their Treatment rank in patients at once.
- Revive: standard action to remove the dazed or stunned condition; cannot revive a dying character without first stabilizing.
- Stabilize: standard action Treatment check stabilizes a dying character.
- Treat Disease or Poison: each time the patient makes a resistance check against an ailment, the treating character also makes a Treatment check; one degree of success grants +2 to the patients resistance check; three or more degrees grants +5.
- Lacking appropriate medical equipment imposes -5; treating a subject with unusual biology may impose an additional penalty; treating oneself imposes -5 and is limited to diagnosis, care, or treating disease/poison.

#### References

**Ref — Security Levels**
Source: context/rules/HeroesHandbook-rules__chunk_063.md
Locator: lines 3995-4045
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Security Levels"
chunk_index: 63
line_range: "3995-4045"
---

### Security Levels
DC

### Security Example
Simple lock or home alarm system
Quality lock or home alarm system
Business and corporate security
High security: branch bank vault, museum
Very high security: bank headquarters
vault, medium prison
Maximum security: highly secure prison
Super-max security: super-prison

### Modifiers
+5
Preventing your tampering
 from being noticed.
Failure on your skill check means nothing happens, but
you can keep trying. More than one degree of failure sets
off the security or trap, if it is possible to do so.


### Treatment
Intellect â€¢ Trained Only â€¢ Manipulation â€¢ Requires Tools
Youâ€™re trained in treating injuries and ailments. The check
DC and effect of Treatment depend on the task:

### Treatment Difficulties
DC
TASK
Diagnose injuries and ailments.
Provide long-term care.
Revive dazed or stunned characters.
Stabilize dying character.
Treat diseases or poisons.
If you do not have the appropriate medical equipment
and supplies, you take a â€“5 circumstance penalty on your
check. If your subject has a particularly unusual biology
(an alien, for example) you may also suffer a circumstance
penalty.
You can use the Treatment skill on yourself, but only to
diagnose, provide care, or treat disease or poison. You
take a â€“5 circumstance penalty on checks when treating
yourself.
DIAGNOSIS
You can diagnose injuries and ailments with an eye to-
ward further treatment. This takes at least a minute. At
the GMâ€™s discretion, a successful diagnosis provides a +2
bonus for favorable circumstances on further Treatment
checks.
```

**Ref — Provide Care**
Source: context/rules/HeroesHandbook-rules__chunk_064.md
Locator: lines 4046-4106
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Provide Care"
chunk_index: 64
line_range: "4046-4106"
---

### Provide Care
Providing care means treating an injured patient for a
day or more. If successful, the patient further reduces the
recovery time by 1 rank (see Recovery in the Action &
Adventure chapter). You can provide care for up to your
Treatment rank in patients at one time.
REVIVE
You can remove the dazed or stunned conditions from
a subject (see Conditions in the Action & Adventure
chapter). The check to revive is a standard action. A suc-
cessful check removes the condition. Other conditions
the patient may have remain, so reviving someone inca-
pacitated due to fatigue still leaves the patient exhaust-
ed, for example, while awakening someone incapacitat-
ed due to damage still leaves the patient staggered. You
canâ€™t awaken a dying character without stabilizing him
first (see the following).
STABILIZE
As a standard action, a successful Treatment check stabi-
lizes a dying character.

### Treat Disease And Poison
You can treat a character afflicted with a disease or poison.
Each time the character makes a resistance check against
the ailment, you make a Treatment check. One degree of
success provides the patient with a +2 circumstance bo-
nus to the resistance check, three or more degrees of suc-
cess provides a +5 circumstance bonus.

### Vehicles
Dexterity â€¢ Trained Only â€¢ Manipulation
Use this skill to operate vehicles, from ground vehicles like
cars to boats, planes, or even spaceships! See Vehicles in
the Gadgets & Gear chapter for details.
Routine tasks, such as ordinary operation of known vehi-
cles, donâ€™t require a check and may even be done untrained
for some vehicles, particularly common ones like cars. Make
a check only when operating the vehicle in a stressful or
dramatic situation like being chased or attacked, or trying
to reach a destination in a limited amount of time.
You can also make Vehicle checks to perform various ma-
neuvers with a vehicle:

### Vehicles Difficulties
DC
MANEUVER
Easy (low-speed turn)
Average (sudden reverse, dodging obstacles)
Difficult (tight turns)
Challenging (bootlegger reverse,
loop, barrel roll)
Formidable (high-speed maneuvers,
jumping or flying around obstacles)
Note that the Vehicles skill does not cover riding animal
mounts. For that, use the Expertise: Riding skill, based on
Agility, with the same guidelines as given for Vehicles skill
checks. At the Gamemasterâ€™s discretion, skills like Athletics
can serve for riding mounts (perhaps with a circumstance
penalty), especially if riding is a fairly uncommon skill, as it
is in the modern world.
```

---

### Vehicles

#### Domain Language

- Vehicles is a Trained Only manipulation skill based on Dexterity covering operation of ground vehicles, boats, aircraft, and spacecraft in dramatic or stressful situations.
- Routine vehicle operations do not require a check and may be done untrained for common vehicles.
- Vehicle maneuver DCs range from Easy DC 10 (low-speed turn) to Formidable DC 25 (high-speed maneuvers around obstacles).
- Vehicles does not cover riding animal mounts; for animal mounts, use Expertise: Riding (based on Agility).

#### References

**Ref — Provide Care**
Source: context/rules/HeroesHandbook-rules__chunk_064.md
Locator: lines 4046-4106
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Provide Care"
chunk_index: 64
line_range: "4046-4106"
---

### Provide Care
Providing care means treating an injured patient for a
day or more. If successful, the patient further reduces the
recovery time by 1 rank (see Recovery in the Action &
Adventure chapter). You can provide care for up to your
Treatment rank in patients at one time.
REVIVE
You can remove the dazed or stunned conditions from
a subject (see Conditions in the Action & Adventure
chapter). The check to revive is a standard action. A suc-
cessful check removes the condition. Other conditions
the patient may have remain, so reviving someone inca-
pacitated due to fatigue still leaves the patient exhaust-
ed, for example, while awakening someone incapacitat-
ed due to damage still leaves the patient staggered. You
canâ€™t awaken a dying character without stabilizing him
first (see the following).
STABILIZE
As a standard action, a successful Treatment check stabi-
lizes a dying character.

### Treat Disease And Poison
You can treat a character afflicted with a disease or poison.
Each time the character makes a resistance check against
the ailment, you make a Treatment check. One degree of
success provides the patient with a +2 circumstance bo-
nus to the resistance check, three or more degrees of suc-
cess provides a +5 circumstance bonus.

### Vehicles
Dexterity â€¢ Trained Only â€¢ Manipulation
Use this skill to operate vehicles, from ground vehicles like
cars to boats, planes, or even spaceships! See Vehicles in
the Gadgets & Gear chapter for details.
Routine tasks, such as ordinary operation of known vehi-
cles, donâ€™t require a check and may even be done untrained
for some vehicles, particularly common ones like cars. Make
a check only when operating the vehicle in a stressful or
dramatic situation like being chased or attacked, or trying
to reach a destination in a limited amount of time.
You can also make Vehicle checks to perform various ma-
neuvers with a vehicle:

### Vehicles Difficulties
DC
MANEUVER
Easy (low-speed turn)
Average (sudden reverse, dodging obstacles)
Difficult (tight turns)
Challenging (bootlegger reverse,
loop, barrel roll)
Formidable (high-speed maneuvers,
jumping or flying around obstacles)
Note that the Vehicles skill does not cover riding animal
mounts. For that, use the Expertise: Riding skill, based on
Agility, with the same guidelines as given for Vehicles skill
checks. At the Gamemasterâ€™s discretion, skills like Athletics
can serve for riding mounts (perhaps with a circumstance
penalty), especially if riding is a fairly uncommon skill, as it
is in the modern world.
```

---

# Boundary Domain

## ability modifier

Owned by: Ability

#### Domain Language

- Each skill has an associated ability whose rank is applied as a modifier to all skill checks for that skill, even when used untrained.
- The ability modifier is one component of the total skill modifier (skill rank + ability modifier + miscellaneous modifiers).

#### References

**Ref — Ch4 Skills**
Source: context/rules/HeroesHandbook-rules__chunk_041.md
Locator: lines 2689-2735
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Ch4 Skills"
chunk_index: 41
line_range: "2689-2735"
---

## CHAPTER 4: SKILLS

### Skill Rank
Your rank in a skill, based on the points you have invested
in that skill. If you have ranks in a skill youâ€™re considered
trained in that skill. You can use some skills even if you
donâ€™t have any ranks in them, known as using a skill un-
trained. Some skills may not be used untrained.

### Ability Modifier
Each skill has an ability modifier applied to the skillâ€™s
checks. Each skillâ€™s ability modifier is noted in its descrip-
tion and on the Skills table. If you use a skill untrained, the
ability modifier still applies to the skill check.

### Miscellaneous Modifiers
Miscellaneous modifiers to skill checks include modifiers
for circumstances, and bonuses from advantages or pow-
ers, among others.
The higher the total, the better the result. Youâ€™re usually look-
ing for a total that equals or exceeds a particular difficulty
class (DC), which may be based on another characterâ€™s traits.

### Critical Success
If you roll a 20 on the die when making a check youâ€™ve
scored a critical success. Determine the degree of suc-
cess normally and then increase it by one degree. This
can turn a low-level success into something more signifi-
cant, but more importantly, it can turn a failure into a full-
fledged success!

### Acquiring Skills
Give your hero skill ranks by spending power points: 2 skill
ranks per power point. Skill ranks do not all need to be as-
signed to the same skill. You can split them between differ-
ent skills. Characters can perform some tasks without any
training, using only raw talent (as defined by their ability
ranks), but skilled characters are better at such things. Those
with the right combinations of skills and advantages can
even hold their own against super-powered opponents.
Skill Cost = 1 power point per
2 skill ranks.
Heroes sneak into the closely guarded lairs of criminal masterminds, infiltrate alien computer systems, and build devices
beyond the understanding of modern science. They can piece together obscure clues to a villainâ€™s latest plot, run along
tightropes, and pilot vehicles through obstacle courses, all in a dayâ€™s work. In MUTANTS & MASTERMINDS, they do so through
the use of various skills, described in this chapter.
```

---

## power point

Owned by: Character Construction

#### Domain Language

- Skills are purchased with power points at 1 power point per 2 ranks.
- Skill ranks may be split across multiple skills from a single power point expenditure.

#### References

**Ref — Ch4 Skills**
Source: context/rules/HeroesHandbook-rules__chunk_041.md
Locator: lines 2689-2735
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Ch4 Skills"
chunk_index: 41
line_range: "2689-2735"
---

## CHAPTER 4: SKILLS

### Skill Rank
Your rank in a skill, based on the points you have invested
in that skill. If you have ranks in a skill youâ€™re considered
trained in that skill. You can use some skills even if you
donâ€™t have any ranks in them, known as using a skill un-
trained. Some skills may not be used untrained.

### Ability Modifier
Each skill has an ability modifier applied to the skillâ€™s
checks. Each skillâ€™s ability modifier is noted in its descrip-
tion and on the Skills table. If you use a skill untrained, the
ability modifier still applies to the skill check.

### Miscellaneous Modifiers
Miscellaneous modifiers to skill checks include modifiers
for circumstances, and bonuses from advantages or pow-
ers, among others.
The higher the total, the better the result. Youâ€™re usually look-
ing for a total that equals or exceeds a particular difficulty
class (DC), which may be based on another characterâ€™s traits.

### Critical Success
If you roll a 20 on the die when making a check youâ€™ve
scored a critical success. Determine the degree of suc-
cess normally and then increase it by one degree. This
can turn a low-level success into something more signifi-
cant, but more importantly, it can turn a failure into a full-
fledged success!

### Acquiring Skills
Give your hero skill ranks by spending power points: 2 skill
ranks per power point. Skill ranks do not all need to be as-
signed to the same skill. You can split them between differ-
ent skills. Characters can perform some tasks without any
training, using only raw talent (as defined by their ability
ranks), but skilled characters are better at such things. Those
with the right combinations of skills and advantages can
even hold their own against super-powered opponents.
Skill Cost = 1 power point per
2 skill ranks.
Heroes sneak into the closely guarded lairs of criminal masterminds, infiltrate alien computer systems, and build devices
beyond the understanding of modern science. They can piece together obscure clues to a villainâ€™s latest plot, run along
tightropes, and pilot vehicles through obstacle courses, all in a dayâ€™s work. In MUTANTS & MASTERMINDS, they do so through
the use of various skills, described in this chapter.
```

---

## degree of success / degree of failure

Owned by: Check Resolution

#### Domain Language

- Skill check outcomes are measured in degrees; typically each 5 points above or below the DC constitutes one degree.
- Skill descriptions specify outcomes per degree (e.g., Persuasion attitude improvement per extra two degrees; Intimidation demoralizing improves at four degrees).

#### References

**Ref — Skill Basics**
Source: context/rules/HeroesHandbook-rules__chunk_042.md
Locator: lines 2736-2796
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Skill Basics"
chunk_index: 42
line_range: "2736-2796"
---

### Skill Basics
Skills are learned abilities, a combination of training (the skill) and natural talent (an ability rank). Each skill has a rank,
used as a bonus to the die roll when using the skill. To make a skill check, roll:
d20 + skill rank + ability modifier + miscellaneous modifiers

### How Skills Work
When you use a skill, make a skill check to see how you do. Based on the circumstances, your result must match or beat a
particular number to use the skill successfully. The harder the task, the higher the number you need to roll. (See Checks,
page 12, for more information.)

### Untrained Skill Checks
Generally, if you attempt a task requiring a skill you donâ€™t
have, you make a skill check as normal. Skill rank doesnâ€™t
apply because you donâ€™t have any ranks in the skill. You
do get other modifiers, however, such as the skillâ€™s ability
modifier.
Many skills can only be used if you are trained in them.
Skills that cannot be used untrained are marked with a
â€œNoâ€ in the â€œUntrainedâ€ column on the Skills table and
listed as â€œTrained Onlyâ€ in their descriptions. Attempts to
use these skills untrained automatically fail. In some cases,
a skill may have both trained and untrained aspects; if you
do not have any ranks in that skill, you can only use the
untrained ones.


### Interaction Skills
Certain skills, called interaction skills, are aimed at deal-
ing with others through social interaction. Interaction
skills allow you to influence the attitudes of others and get
them to cooperate with you in one way or another. Since
interaction skills are intended for dealing with others so-
cially, they have certain requirements.
First, you must be able to interact with the subject(s) of
the skill. They must be aware of you and able to under-
stand you. If they canâ€™t hear or understand you for some
reason, you have a â€“5 circumstance penalty to your skill
check (see Circumstance Modifiers in The Basics).
Interaction skills work best on intelligent subjects, ones
with an Intellect rank of â€“4 or better. You can use them
on creatures with Int â€“5, but again with a â€“5 circumstance
penalty; theyâ€™re just too dumb to get the subtleties of
your point. You canâ€™t use interaction skills at all on sub-
jects lacking one or more mental abilities. (Try convincing
a rock to be your friendâ€”or afraid of youâ€”sometime.)
The Immunity effect (see the Powers chapter) can also
render characters immune to interaction skills.
You can use interaction skills on groups of subjects at
once, but only to achieve the same result for everyone.
So you can attempt to use Deception or Persuasion to
convince a group of something, or Intimidation to cow
a crowd, for example, but you canâ€™t convince some indi-
viduals of one thing and the rest of another, or intimidate
some and not others. The GM decides if a particular use of
an interaction skill is effective against a group, and may
apply modifiers depending on the situation. The general
rules for interaction still apply: everyone in the group
must be able to hear and understand you, for example, or
you suffer a â€“5 on your skill check against them. Mindless
subjects are unaffected, as usual.
```

---

## routine check

Owned by: Check Resolution

#### Domain Language

- A routine check result is bonus + 10, used when no pressure exists and rolling is unnecessary.
- Skill Mastery allows a character to use the routine check result for a specific skill even under stress.

#### References

**Ref — Manipulation Skills**
Source: context/rules/HeroesHandbook-rules__chunk_043.md
Locator: lines 2797-2849
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Manipulation Skills"
chunk_index: 43
line_range: "2797-2849"
---

### Manipulation Skills
Some skills, called manipulation skills, require a degree
of fine physical manipulation. You need prehensile limbs
and a Strength rank or some suitable Precise power effect
to use manipulation skills effectively. If your physical ma-
nipulation capabilities are impaired in some fashion (such
as having your hands tied or full use of only one hand),
the GM may impose a circumstance modifier based on the
severity of the impairment. Characters lacking the ability
to use manipulation skills can still have ranks in them and
use them to oversee or assist the work of others (see Team
Checks, page 16).

### Skill Benchmarks
You can get a general idea of just how good a particu-
lar characterâ€™s skill bonus is using the general difficulty
class guidelines given in The Basics along with the
rules for routine checks (see Routine Checks in that
chapter).
For example, a +5 total skill modifier means the char-
acter can routinely achieve a result of 15 (a tough task).
Safe to say the character is a pro, able to routinely han-
dle tasks that would prove too much for someone less
skilled. A character with a +10 skill modifier achieve a
DC 20 (challenging task) on a routine basis, a real level of
expertise, while a +15 modifier can routinely complete
DC 25 (formidable) tasks. At the high end, a +30 skill
modifier can routinely accomplishing the nigh impos-
sible (DC 40 tasks)!

### Skill Descriptions
This section describes the skills available to MUTANTS & MASTERMINDS characters, including their common uses and modi-
fiers. Characters may be able to use skills for tasks other than those given here. The GM sets the DC and decides the
results in those cases. The format for skill descriptions is given here. Items that do not apply are omitted from the
skillâ€™s description.

### Skill Name
Ability â€¢ Trained Only â€¢ Interaction â€¢ Manipulation â€¢ Requires Tools
The skill name line and the line below it contain the fol-
lowing information:
Skill Name: What the skill is called. GMs may feel free to
change the names of some skills to better suit the style of
their game, if desired.
Ability: The ability that applies a modifier to the skill
check.
Trained Only: If â€œTrained Onlyâ€ is included on the line be-
low the skillâ€™s name, you must have at least 1 rank in the
skill in order to use it. If â€œTrained Onlyâ€ is absent, untrained
characters (those with 0 ranks in the skill) may use it.
Some skills may have trained only aspects, in which case
this notation is still listed, and the untrained aspects are
called out in the skill description.
```

---

## attack check

Owned by: Combat

#### Domain Language

- Close Combat and Ranged Combat skill ranks add to attack checks for the specific weapon or power the skill covers.
- Attack checks are resolved in the Combat module; the Skill module provides the bonus source.

#### References

**Ref — Swimming**
Source: context/rules/HeroesHandbook-rules__chunk_048.md
Locator: lines 3118-3168
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Swimming"
chunk_index: 48
line_range: "3118-3168"
---

### Swimming
A successful DC 10 Athletics check allows you to swim
your ground speed rank minus 2 as a move action. If the
check fails, you make no progress through the water dur-
ing the action. With more than one degree of failure, you
go under. If underwater, you must hold your breath to
avoid drowning (see page 238).

### Swimming Difficulties
DC

### Modifiers
+5
Rescuing another character who cannot swim
+5
Rough or choppy water
+5
+1 speed rank (up to your full ground speed)
+10
Stormy or turbulent water

### Close Combat
Fighting
Youâ€™re trained with a particular type of close attack, giv-
ing you a bonus to your attack checks with it equal to
your skill rank (see Attack Check in The Basics and in
the Action & Adventure chapter). Each close attack is
a separate Close Combat skill with its own rank, and en-
compasses a single weapon or power, although an ar-
ray may be considered one power, at the Gamemasterâ€™s
discretion (see Arrays in the Powers chapter for more
information).
So a hero might have Close Combat: Swords, but Close
Combat: Melee Weapons is too broad. Close Combat: Un-
armed is an option, meaning skill with unarmed strikes
like punches and kicks. However, this bonus does not ap-
ply to other forms of unarmed combat maneuvers, includ-
ing, but not limited to, grabbing or tripping.

If itâ€™s important, you can distinguish between a deception
that fails because the target doesnâ€™t believe it and one
that fails because it asks too much. For instance, if the tar-
get gets a +10 bonus to resistance because the deception
demands serious risk, and the resistance check succeeds
by 10 or less, then the target doesnâ€™t so much see through
the deception as prove reluctant to go along with it. If the
targetâ€™s Insight check succeeds by 11 or more, he has seen
through the deception, and would have refused even if
it had not placed unusual demands on him (that is, even
without the +10 modifier).
```

---

## condition

Owned by: Check Resolution

#### Domain Language

- Some skill outcomes impose conditions on targets (e.g., Intimidation demoralizing imposes impaired or disabled; Deception feinting imposes vulnerable).
- Treatment skill removes conditions (dazed, stunned) and stabilizes the dying condition.

#### References

**Ref — Resist Influence**
Source: context/rules/HeroesHandbook-rules__chunk_053.md
Locator: lines 3441-3484
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Resist Influence"
chunk_index: 53
line_range: "3441-3484"
---

### Resist Influence
Make an Insight check when called to do so to resist or
overcome the effects of certain interaction skills, such
as Deception or Intimidation. If the result of your check
exceeds your opponentâ€™s, you are unaffected by their at-
tempt to influence you.

### Intimidation
Presence â€¢ Interaction
You know how to use threats (both real and implied) to
get others to do what you want.
COERCING
Make an Intimidation check, opposed by the targetâ€™s In-
sight or Will defense (whichever has the highest bonus). If
your check succeeds, you may treat the target as friendly,
but only for actions taken in your presence. That is, the tar-
get retains his normal attitude, but will talk, advise, offer
limited help, or advocate on your behalf while intimidated.
The target cooperates, but wonâ€™t necessarily obey your ev-
ery whim or do anything that would directly endanger him.
Properly intimidating someone takes time and an appro-
priately violent action or threat. Uses of Intimidation in ac-
tion rounds are generally standard actions, although you
can attempt to deceive as a move action by taking a â€“5
penalty to your check.
If you perform some action that makes you more impos-
ing, you gain a circumstance bonus on your Intimidation
check. If your target clearly has a superior position, you
suffer a circumstance penalty.
With more than one degree of failure on your check, the
target may actually do the opposite of what you want! Suc-

ceed or fail, a targetâ€™s true attitude towards you generally
becomes hostile after you attempt an Intimidation check,
even if they go along with you for the moment.
DEMORALIZING
You can use Intimidation in combat as a standard action
to undermine an opponentâ€™s confidence. Make an Intimi-
dation check as a standard action. If it succeeds, your tar-
get is impaired (a â€“2 circumstance penalty on checks) un-
til the end of your next round. With four or more degrees
of success, the target is disabled (a â€“5 penalty) until the
end of your next round.
```

**Ref — Provide Care**
Source: context/rules/HeroesHandbook-rules__chunk_064.md
Locator: lines 4046-4106
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Provide Care"
chunk_index: 64
line_range: "4046-4106"
---

### Provide Care
Providing care means treating an injured patient for a
day or more. If successful, the patient further reduces the
recovery time by 1 rank (see Recovery in the Action &
Adventure chapter). You can provide care for up to your
Treatment rank in patients at one time.
REVIVE
You can remove the dazed or stunned conditions from
a subject (see Conditions in the Action & Adventure
chapter). The check to revive is a standard action. A suc-
cessful check removes the condition. Other conditions
the patient may have remain, so reviving someone inca-
pacitated due to fatigue still leaves the patient exhaust-
ed, for example, while awakening someone incapacitat-
ed due to damage still leaves the patient staggered. You
canâ€™t awaken a dying character without stabilizing him
first (see the following).
STABILIZE
As a standard action, a successful Treatment check stabi-
lizes a dying character.

### Treat Disease And Poison
You can treat a character afflicted with a disease or poison.
Each time the character makes a resistance check against
the ailment, you make a Treatment check. One degree of
success provides the patient with a +2 circumstance bo-
nus to the resistance check, three or more degrees of suc-
cess provides a +5 circumstance bonus.

### Vehicles
Dexterity â€¢ Trained Only â€¢ Manipulation
Use this skill to operate vehicles, from ground vehicles like
cars to boats, planes, or even spaceships! See Vehicles in
the Gadgets & Gear chapter for details.
Routine tasks, such as ordinary operation of known vehi-
cles, donâ€™t require a check and may even be done untrained
for some vehicles, particularly common ones like cars. Make
a check only when operating the vehicle in a stressful or
dramatic situation like being chased or attacked, or trying
to reach a destination in a limited amount of time.
You can also make Vehicle checks to perform various ma-
neuvers with a vehicle:

### Vehicles Difficulties
DC
MANEUVER
Easy (low-speed turn)
Average (sudden reverse, dodging obstacles)
Difficult (tight turns)
Challenging (bootlegger reverse,
loop, barrel roll)
Formidable (high-speed maneuvers,
jumping or flying around obstacles)
Note that the Vehicles skill does not cover riding animal
mounts. For that, use the Expertise: Riding skill, based on
Agility, with the same guidelines as given for Vehicles skill
checks. At the Gamemasterâ€™s discretion, skills like Athletics
can serve for riding mounts (perhaps with a circumstance
penalty), especially if riding is a fairly uncommon skill, as it
is in the modern world.
```

---

## power effect

Owned by: Power

#### Domain Language

- The Immunity power effect can render a character completely immune to interaction skills.
- The Illusion power effect is the target of Insights Detect Illusion use.
- The Precise power effect can substitute for prehensile limbs and Strength rank when using manipulation skills.

#### References

**Ref — Skill Basics**
Source: context/rules/HeroesHandbook-rules__chunk_042.md
Locator: lines 2736-2796
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Skill Basics"
chunk_index: 42
line_range: "2736-2796"
---

### Skill Basics
Skills are learned abilities, a combination of training (the skill) and natural talent (an ability rank). Each skill has a rank,
used as a bonus to the die roll when using the skill. To make a skill check, roll:
d20 + skill rank + ability modifier + miscellaneous modifiers

### How Skills Work
When you use a skill, make a skill check to see how you do. Based on the circumstances, your result must match or beat a
particular number to use the skill successfully. The harder the task, the higher the number you need to roll. (See Checks,
page 12, for more information.)

### Untrained Skill Checks
Generally, if you attempt a task requiring a skill you donâ€™t
have, you make a skill check as normal. Skill rank doesnâ€™t
apply because you donâ€™t have any ranks in the skill. You
do get other modifiers, however, such as the skillâ€™s ability
modifier.
Many skills can only be used if you are trained in them.
Skills that cannot be used untrained are marked with a
â€œNoâ€ in the â€œUntrainedâ€ column on the Skills table and
listed as â€œTrained Onlyâ€ in their descriptions. Attempts to
use these skills untrained automatically fail. In some cases,
a skill may have both trained and untrained aspects; if you
do not have any ranks in that skill, you can only use the
untrained ones.


### Interaction Skills
Certain skills, called interaction skills, are aimed at deal-
ing with others through social interaction. Interaction
skills allow you to influence the attitudes of others and get
them to cooperate with you in one way or another. Since
interaction skills are intended for dealing with others so-
cially, they have certain requirements.
First, you must be able to interact with the subject(s) of
the skill. They must be aware of you and able to under-
stand you. If they canâ€™t hear or understand you for some
reason, you have a â€“5 circumstance penalty to your skill
check (see Circumstance Modifiers in The Basics).
Interaction skills work best on intelligent subjects, ones
with an Intellect rank of â€“4 or better. You can use them
on creatures with Int â€“5, but again with a â€“5 circumstance
penalty; theyâ€™re just too dumb to get the subtleties of
your point. You canâ€™t use interaction skills at all on sub-
jects lacking one or more mental abilities. (Try convincing
a rock to be your friendâ€”or afraid of youâ€”sometime.)
The Immunity effect (see the Powers chapter) can also
render characters immune to interaction skills.
You can use interaction skills on groups of subjects at
once, but only to achieve the same result for everyone.
So you can attempt to use Deception or Persuasion to
convince a group of something, or Intimidation to cow
a crowd, for example, but you canâ€™t convince some indi-
viduals of one thing and the rest of another, or intimidate
some and not others. The GM decides if a particular use of
an interaction skill is effective against a group, and may
apply modifiers depending on the situation. The general
rules for interaction still apply: everyone in the group
must be able to hear and understand you, for example, or
you suffer a â€“5 on your skill check against them. Mindless
subjects are unaffected, as usual.
```

**Ref — Manipulation Skills**
Source: context/rules/HeroesHandbook-rules__chunk_043.md
Locator: lines 2797-2849
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Manipulation Skills"
chunk_index: 43
line_range: "2797-2849"
---

### Manipulation Skills
Some skills, called manipulation skills, require a degree
of fine physical manipulation. You need prehensile limbs
and a Strength rank or some suitable Precise power effect
to use manipulation skills effectively. If your physical ma-
nipulation capabilities are impaired in some fashion (such
as having your hands tied or full use of only one hand),
the GM may impose a circumstance modifier based on the
severity of the impairment. Characters lacking the ability
to use manipulation skills can still have ranks in them and
use them to oversee or assist the work of others (see Team
Checks, page 16).

### Skill Benchmarks
You can get a general idea of just how good a particu-
lar characterâ€™s skill bonus is using the general difficulty
class guidelines given in The Basics along with the
rules for routine checks (see Routine Checks in that
chapter).
For example, a +5 total skill modifier means the char-
acter can routinely achieve a result of 15 (a tough task).
Safe to say the character is a pro, able to routinely han-
dle tasks that would prove too much for someone less
skilled. A character with a +10 skill modifier achieve a
DC 20 (challenging task) on a routine basis, a real level of
expertise, while a +15 modifier can routinely complete
DC 25 (formidable) tasks. At the high end, a +30 skill
modifier can routinely accomplishing the nigh impos-
sible (DC 40 tasks)!

### Skill Descriptions
This section describes the skills available to MUTANTS & MASTERMINDS characters, including their common uses and modi-
fiers. Characters may be able to use skills for tasks other than those given here. The GM sets the DC and decides the
results in those cases. The format for skill descriptions is given here. Items that do not apply are omitted from the
skillâ€™s description.

### Skill Name
Ability â€¢ Trained Only â€¢ Interaction â€¢ Manipulation â€¢ Requires Tools
The skill name line and the line below it contain the fol-
lowing information:
Skill Name: What the skill is called. GMs may feel free to
change the names of some skills to better suit the style of
their game, if desired.
Ability: The ability that applies a modifier to the skill
check.
Trained Only: If â€œTrained Onlyâ€ is included on the line be-
low the skillâ€™s name, you must have at least 1 rank in the
skill in order to use it. If â€œTrained Onlyâ€ is absent, untrained
characters (those with 0 ranks in the skill) may use it.
Some skills may have trained only aspects, in which case
this notation is still listed, and the untrained aspects are
called out in the skill description.
```

---

## team check

Owned by: Check Resolution

#### Domain Language

- Characters lacking physical manipulation capability can still use manipulation skill ranks to oversee or assist others via team checks.
- Team checks are owned by Check Resolution; manipulation skills reference them as an alternative application mode.

#### References

**Ref — Manipulation Skills**
Source: context/rules/HeroesHandbook-rules__chunk_043.md
Locator: lines 2797-2849
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch4 Skills"
topic: "Manipulation Skills"
chunk_index: 43
line_range: "2797-2849"
---

### Manipulation Skills
Some skills, called manipulation skills, require a degree
of fine physical manipulation. You need prehensile limbs
and a Strength rank or some suitable Precise power effect
to use manipulation skills effectively. If your physical ma-
nipulation capabilities are impaired in some fashion (such
as having your hands tied or full use of only one hand),
the GM may impose a circumstance modifier based on the
severity of the impairment. Characters lacking the ability
to use manipulation skills can still have ranks in them and
use them to oversee or assist the work of others (see Team
Checks, page 16).

### Skill Benchmarks
You can get a general idea of just how good a particu-
lar characterâ€™s skill bonus is using the general difficulty
class guidelines given in The Basics along with the
rules for routine checks (see Routine Checks in that
chapter).
For example, a +5 total skill modifier means the char-
acter can routinely achieve a result of 15 (a tough task).
Safe to say the character is a pro, able to routinely han-
dle tasks that would prove too much for someone less
skilled. A character with a +10 skill modifier achieve a
DC 20 (challenging task) on a routine basis, a real level of
expertise, while a +15 modifier can routinely complete
DC 25 (formidable) tasks. At the high end, a +30 skill
modifier can routinely accomplishing the nigh impos-
sible (DC 40 tasks)!

### Skill Descriptions
This section describes the skills available to MUTANTS & MASTERMINDS characters, including their common uses and modi-
fiers. Characters may be able to use skills for tasks other than those given here. The GM sets the DC and decides the
results in those cases. The format for skill descriptions is given here. Items that do not apply are omitted from the
skillâ€™s description.

### Skill Name
Ability â€¢ Trained Only â€¢ Interaction â€¢ Manipulation â€¢ Requires Tools
The skill name line and the line below it contain the fol-
lowing information:
Skill Name: What the skill is called. GMs may feel free to
change the names of some skills to better suit the style of
their game, if desired.
Ability: The ability that applies a modifier to the skill
check.
Trained Only: If â€œTrained Onlyâ€ is included on the line be-
low the skillâ€™s name, you must have at least 1 rank in the
skill in order to use it. If â€œTrained Onlyâ€ is absent, untrained
characters (those with 0 ranks in the skill) may use it.
Some skills may have trained only aspects, in which case
this notation is still listed, and the untrained aspects are
called out in the skill description.
```
