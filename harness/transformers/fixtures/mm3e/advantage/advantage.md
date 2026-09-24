---
state: domain-sketch
---

# Module: [Advantage]

Scope: Advantage types: Combat, Fortune, General, and Skill advantages.

**Core terms**:
- advantage
- advantage rank
- combat advantage
- fortune advantage
- general advantage
- skill advantage
- Accurate Attack
- All-out Attack
- Defensive Attack
- Power Attack
- Improved Initiative
- Improved Critical
- Equipment
- Minion
- Sidekick
- Benefit
- Luck
- Inspire
- Leadership
- Beginner's Luck
- Skill Mastery
- Jack of all Trades
- Ranged Attack
- Close Attack
- Favored Environment
- Favored Foe

---


## Domain logic

- All advantages cost exactly 1 power point per rank; a non-ranked advantage is acquired once at effective rank 1.
- Each advantage belongs to exactly one of four categories (Combat, Fortune, General, Skill) and that membership is fixed at acquisition.
- Fortune advantages require a hero point to activate — the hero point is the activation cost, not a separate resource; hero point benefits ignore power level limits.
- Luck re-rolls consume one session use per rank from a separate per-session pool; the pool is limited to the character's current Luck rank uses and refreshes when hero points reset at adventure start.
- Luck's maximum rank is capped at half the series power level (rounded down); this is the only power-level-derived rank cap in this module.
- Attack trade-off advantages (Accurate Attack, All-out Attack, Defensive Attack, Power Attack) enforce a symmetric exchange: penalty taken must equal bonus gained, and neither the penalty nor the bonus may exceed 5.
- Total attack bonus from ranked attack advantages (Close Attack, Ranged Attack) is always subject to the series power level cap.
- The +2 circumstance bonus from Favored Environment and Favored Foe is never subject to the power level cap.
- Equipment grants 5 equipment points per rank to spend on physical gear; that gear is subject to loss, theft, and destruction and is never treated as a power effect.
- Minion point total is always exactly rank x 15; minions have no hero points and cannot have minions of their own; lost minions are replaced between adventures only.
- A Sidekick's power point total must always remain less than the owning character's total; sidekicks are full characters, not minions.
- Benefit value is bounded above by any other single advantage or a 1-point power effect; the GM has final approval authority.

# Core Domain

## Key Abstractions

### Advantage

An advantage is the named, purchasable capability unit of the Advantage module. It owns the identity of what an advantage is, how much it costs, how it scales through ranks, and what distinguishes ranked from non-ranked advantages. Every specific advantage is an instance of this concept. It collaborates with the Character Construction module (power points fund purchases) and interacts with all four category concepts, but does not own combat resolution, skill checks, or hero point mechanics. An advantage must always cost exactly 1 power point per rank; must always belong to exactly one of the four categories; and a non-ranked advantage must never appear with a rank number greater than 1.

#### Decisions made
- advantage rank is kept under Advantage rather than made its own KA: rank is a scalar property of an advantage, not an independent domain concept (independence test fails; rank has no meaning outside the advantage it belongs to).
- power point is a boundary term owned by Character Construction; it is not a Core term of this module.
- No terms moved out of this module from the Advantage KA.

#### advantage

- An advantage is a special ability or rule-breaking capability beyond the reach of ordinary characters, purchased with power points at character creation or advancement.
- Advantages allow heroes to do things most characters cannot, or to do ordinary things significantly better.
- Each advantage is categorized as Combat, Fortune, General, or Skill based on the domain of activity it affects.
- Advantages cost 1 power point per rank; those with no ranks are acquired once at effective rank 1.
- Each advantage's description states the benefit it provides and whether the advantage can be acquired in ranks.

**Ref — Ch5 Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_065.md
Locator: lines 4107-4148
Extract: whole

```source
## CHAPTER 5: ADVANTAGES
Heroes are more than just skilled, they often have amazing advantages, beyond the abilities of ordinary people. In MU-
TANTS & MASTERMINDS, advantages often allow heroes to break the rules, gaining access to and doing things most people
cannot, or simply doing them better.

### Acquiring Advantages
Advantages are rated in ranks and bought with power points, just like abilities and skills. Advantages cost 1 power point
per rank. Some advantages have no ranks and are acquired only once, effectively at rank 1.
Advantage Cost = 1 power point per advantage rank

### Advantage Descriptions
Each advantage's description explains the benefit it provides. It also says if the advantage can be acquired in ranks and
the effects of doing so. Such advantages are listed as "Ranked" alongside the advantage name. Ranks in a advantage are
noted with a number after the advantage's name, such as "Defensive Roll 2" (for a character who has taken two ranks
in the Defensive Roll advantage), just like skill and power ranks. If there is a maximum number of ranks a character can
take, it's listed in parentheses after the word "Ranked" in the advantage's heading.

### Types Of Advantages
Advantages are categorized as one of four types:
Combat Advantages are useful in combat and often modify how various combat maneuvers are performed.
Fortune Advantages require and enhance the use of hero points.
General Advantages provide special abilities or bonuses not covered by the other categories.
Skill Advantages offer bonuses or modifications to skill use.

### Advantage Descriptions
Each advantage is listed by name, type, and if the advantage is available in multiple ranks, followed by a description
of the advantage's benefits. The effects of additional ranks of the advantage (if any) are noted in the text of each
advantage. In some cases a advantage's description mentions the normal conditions for characters who do not have the
advantage for comparison.
```


#### Domain Sketch
Advantage is the foundational purchasable capability unit — the named ability a hero buys with power points to exceed ordinary character limits.

- accepts cost of exactly 1 power point per rank during character creation or advancement
- belongs to exactly one of the four categories (Combat, Fortune, General, Skill) fixed at definition time
- allows the holder to do something most characters cannot do, or to do something ordinary significantly better
- scales through rank when the advantage is Ranked; a non-ranked advantage is acquired once at effective rank 1
- publishes its benefit description and whether additional ranks are available

Invariant: cost is always exactly 1 power point per rank; a non-ranked advantage is always at effective rank 1; category membership is fixed and always exactly one of the four categories; the benefit must never grant an effect equivalent to a power costing more than 1 point.

#### Decisions made (term level)
- advantage and advantage rank are kept as two separate terms because rank governs a distinct set of rules (notation, caps, scaling) described independently from what an advantage is.
- Specific named advantages (Accurate Attack, Luck, etc.) are instances of advantage, not separate top-level concepts.
#### advantage rank

- Ranked advantages may be purchased multiple times, each purchase adding one rank that increases or extends the advantage's effect.
- Rank is noted by a number after the advantage name (e.g., "Defensive Roll 2" for two ranks).
- Non-ranked advantages are acquired only once; they do not scale with repeated purchase.
- If a maximum number of ranks exists, it is listed in parentheses in the advantage's heading (e.g., "Ranked (2)").
- Advantage cost equals 1 power point per rank, matching the cost formula for abilities and skills.

**Ref — Ch5 Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_065.md
Locator: lines 4107-4148
Extract: whole

```source
## CHAPTER 5: ADVANTAGES
Heroes are more than just skilled, they often have amazing advantages, beyond the abilities of ordinary people. In MU-
TANTS & MASTERMINDS, advantages often allow heroes to break the rules, gaining access to and doing things most people
cannot, or simply doing them better.

### Acquiring Advantages
Advantages are rated in ranks and bought with power points, just like abilities and skills. Advantages cost 1 power point
per rank. Some advantages have no ranks and are acquired only once, effectively at rank 1.
Advantage Cost = 1 power point per advantage rank

### Advantage Descriptions
Each advantage's description explains the benefit it provides. It also says if the advantage can be acquired in ranks and
the effects of doing so. Such advantages are listed as "Ranked" alongside the advantage name. Ranks in a advantage are
noted with a number after the advantage's name, such as "Defensive Roll 2" (for a character who has taken two ranks
in the Defensive Roll advantage), just like skill and power ranks. If there is a maximum number of ranks a character can
take, it's listed in parentheses after the word "Ranked" in the advantage's heading.

### Types Of Advantages
Advantages are categorized as one of four types:
Combat Advantages are useful in combat and often modify how various combat maneuvers are performed.
Fortune Advantages require and enhance the use of hero points.
General Advantages provide special abilities or bonuses not covered by the other categories.
Skill Advantages offer bonuses or modifications to skill use.

### Advantage Descriptions
Each advantage is listed by name, type, and if the advantage is available in multiple ranks, followed by a description
of the advantage's benefits. The effects of additional ranks of the advantage (if any) are noted in the text of each
advantage. In some cases a advantage's description mentions the normal conditions for characters who do not have the
advantage for comparison.
```


#### Domain Sketch
Advantage rank is the scalar multiplier that makes a Ranked advantage stronger with each additional purchase.

- records itself as a number after the advantage name (e.g., "Defensive Roll 2" for two ranks)
- scales the advantage's effect upward with each rank purchased
- enforces a published maximum rank when the advantage heading specifies one (e.g., "Ranked (2)")
- prevents purchase of additional ranks beyond the stated maximum
- for non-ranked advantages, holds fixed at effective rank 1 and cannot increase

Invariant: rank cannot exceed the maximum stated in the advantage's heading when a cap is listed; a non-ranked advantage is always rank 1.

#### Decisions made (term level)
- Kept as a property under the Advantage KA rather than a standalone concept: rank has no identity or behavior outside the advantage it belongs to.
---

### Advantage Category

An advantage category is the classification label that groups every advantage into one of four domain areas: Combat, Fortune, General, and Skill. The category owns the boundary of what kind of activity the advantage affects. The four category terms collectively define the taxonomy; each specific advantage belongs to exactly one category and that membership is fixed at definition time. Categories do not have ranks and are not purchased; they are structural tags. An advantage must always belong to exactly one category; no advantage may belong to two categories simultaneously.

#### Decisions made
- All four category terms are grouped under one KA because they collectively define the taxonomy; none is independent of the others or more structurally significant than the others.
- Category terms pass the module-fit test: advantage categorization is the core purpose of this module's classification system.
- No terms moved out of this module from the Advantage Category KA.

#### combat advantage

- Combat advantages modify how combat maneuvers are performed or provide bonuses during fighting.
- A combat advantage typically creates a trade-off (e.g., sacrificing attack bonus for effect bonus) or removes a penalty from a specific combat action.
- The full list includes: Accurate Attack, All-out Attack, Chokehold, Close Attack, Defensive Attack, Defensive Roll, Evasion, Fast Grab, Favored Environment, Grabbing Finesse, Improved Aim, Improved Critical, Improved Defense, Improved Disarm, Improved Grab, Improved Hold, Improved Initiative, Improved Smash, Improved Trip, Improvised Weapon, Move-by Action, Power Attack, Precise Attack, Prone Fighting, Quick Draw, Ranged Attack, Redirect, Set-up, Takedown, Throwing Mastery, Uncanny Dodge, Weapon Bind, Weapon Break.
- Combat advantages can be combined to represent fighting styles such as martial arts disciplines or superhero combat techniques.

**Ref — Ch5 Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_065.md
Locator: lines 4107-4148
Extract: whole

```source
## CHAPTER 5: ADVANTAGES
Heroes are more than just skilled, they often have amazing advantages, beyond the abilities of ordinary people. In MU-
TANTS & MASTERMINDS, advantages often allow heroes to break the rules, gaining access to and doing things most people
cannot, or simply doing them better.

### Acquiring Advantages
Advantages are rated in ranks and bought with power points, just like abilities and skills. Advantages cost 1 power point
per rank. Some advantages have no ranks and are acquired only once, effectively at rank 1.
Advantage Cost = 1 power point per advantage rank

### Advantage Descriptions
Each advantage's description explains the benefit it provides. It also says if the advantage can be acquired in ranks and
the effects of doing so. Such advantages are listed as "Ranked" alongside the advantage name. Ranks in a advantage are
noted with a number after the advantage's name, such as "Defensive Roll 2" (for a character who has taken two ranks
in the Defensive Roll advantage), just like skill and power ranks. If there is a maximum number of ranks a character can
take, it's listed in parentheses after the word "Ranked" in the advantage's heading.

### Types Of Advantages
Advantages are categorized as one of four types:
Combat Advantages are useful in combat and often modify how various combat maneuvers are performed.
Fortune Advantages require and enhance the use of hero points.
General Advantages provide special abilities or bonuses not covered by the other categories.
Skill Advantages offer bonuses or modifications to skill use.

### Advantage Descriptions
Each advantage is listed by name, type, and if the advantage is available in multiple ranks, followed by a description
of the advantage's benefits. The effects of additional ranks of the advantage (if any) are noted in the text of each
advantage. In some cases a advantage's description mentions the normal conditions for characters who do not have the
advantage for comparison.
```

**Ref — Combat Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_067.md
Locator: lines 4189-4286
Extract: whole

```source
### Combat Advantages
ADVANTAGE  EFFECT
Accurate Attack: Trade effect DC for attack bonus.
All-out Attack: Trade active defense for attack bonus.
Chokehold: Suffocate an opponent you have successfully grabbed.
Close Attack: +1 bonus to close attack checks per rank.
Defensive Attack: Trade attack bonus for active defense bonus.
Defensive Roll: +1 active defense bonus to Toughness per rank.
Evasion: Circumstance bonus to avoid area effects.
Fast Grab: Make a free grab check after an unarmed attack.
Favored Environment: Circumstance bonus to attack or defense in an environment.
Grabbing Finesse: Substitute Dex for Str when making grab attacks.
Improved Aim: Double circumstance bonuses for aiming.
Improved Critical: +1 to critical threat range with an attack per rank.
Improved Defense: +2 bonus to active defense when you take the defend action.
Improved Disarm: No penalty for the disarm action.
Improved Grab: Make grab attacks with one arm. Not vulnerable while grabbing.
Improved Hold: -5 circumstance penalty to escape from your holds.
Improved Initiative: +4 bonus to initiative checks per rank.
Improved Smash: No penalty for the smash action.
Improved Trip: No penalty for the trip action.
Improvised Weapon: Use Unarmed Combat skill with improvised weapons, +1 damage bonus.
Move-by Action: Move both before and after your standard action.
Power Attack: Trade attack bonus for effect bonus.
Precise Attack: Ignore attack check penalties for either cover or concealment.
Prone Fighting: No penalties for fighting while prone.
Quick Draw: Draw a weapon as a free action.
Ranged Attack: +1 bonus to ranged attack checks per rank.
Redirect: Use Deception to redirect a missed attack at another target.
Set-up: Transfer the benefit of an interaction skill to an ally.
Takedown: Free extra attack when you incapacitate a minion.
Throwing Mastery: +1 damage bonus with thrown weapons per rank.
Uncanny Dodge: Not vulnerable when surprised or caught off-guard.
Weapon Bind: Free disarm attempt when you actively defend.
Weapon Break: Free smash attack when you actively defend.
```


#### Domain Sketch
Combat advantage is the category label that groups advantages whose primary effect modifies combat maneuver terms, attack checks, defenses, or critical threat ranges.

- classifies each member advantage as affecting combat — establishing the domain boundary for this category
- modifies maneuver terms (attack bonus, active defenses, effect modifier, critical range) rather than skill use or hero point spending
- combines with other combat advantages at the character level to form coherent fighting styles (e.g., martial arts disciplines)

Invariant: a combat advantage always modifies a combat maneuver mechanic; it never requires a hero point to activate.

#### Decisions made (term level)
- Favored Environment is classified here (COMBAT), not under Skill Advantage, matching the source's explicit category label.
- Improved Initiative is classified here despite primarily affecting turn order — the source explicitly labels it COMBAT.
#### fortune advantage

- Fortune advantages require spending a hero point to activate; they enhance or modify the use of hero points.
- Fortune advantages include: Beginner's Luck, Inspire, Leadership, Luck, Seize Initiative, and Ultimate Effort.
- Each fortune advantage defines what the hero point purchase achieves (e.g., temporary skill ranks, an inspiration bonus, a removed condition, a die re-roll, initiative priority, or a guaranteed roll of 20).

**Ref — Ch5 Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_065.md
Locator: lines 4107-4148
Extract: whole

```source
## CHAPTER 5: ADVANTAGES
Heroes are more than just skilled, they often have amazing advantages, beyond the abilities of ordinary people. In MU-
TANTS & MASTERMINDS, advantages often allow heroes to break the rules, gaining access to and doing things most people
cannot, or simply doing them better.

### Acquiring Advantages
Advantages are rated in ranks and bought with power points, just like abilities and skills. Advantages cost 1 power point
per rank. Some advantages have no ranks and are acquired only once, effectively at rank 1.
Advantage Cost = 1 power point per advantage rank

### Advantage Descriptions
Each advantage's description explains the benefit it provides. It also says if the advantage can be acquired in ranks and
the effects of doing so. Such advantages are listed as "Ranked" alongside the advantage name. Ranks in a advantage are
noted with a number after the advantage's name, such as "Defensive Roll 2" (for a character who has taken two ranks
in the Defensive Roll advantage), just like skill and power ranks. If there is a maximum number of ranks a character can
take, it's listed in parentheses after the word "Ranked" in the advantage's heading.

### Types Of Advantages
Advantages are categorized as one of four types:
Combat Advantages are useful in combat and often modify how various combat maneuvers are performed.
Fortune Advantages require and enhance the use of hero points.
General Advantages provide special abilities or bonuses not covered by the other categories.
Skill Advantages offer bonuses or modifications to skill use.

### Advantage Descriptions
Each advantage is listed by name, type, and if the advantage is available in multiple ranks, followed by a description
of the advantage's benefits. The effects of additional ranks of the advantage (if any) are noted in the text of each
advantage. In some cases a advantage's description mentions the normal conditions for characters who do not have the
advantage for comparison.
```

**Ref — Fortune Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_068.md
Locator: lines 4287-4336
Extract: whole

```source
### Fortune Advantages
ADVANTAGE  EFFECT
Beginner's Luck: Spend a hero point to gain 5 temporary ranks in a skill.
Inspire: Spend a hero point to grant allies a +1 circumstance bonus per rank.
Leadership: Spend a hero point to remove a condition from an ally.
Luck: Re-roll a die roll once per rank.
Seize Initiative: Spend a hero point to go first in the initiative order.
Ultimate Effort: Spend a hero point to get an effective 20 on a specific check.

### General Advantages
ADVANTAGE  EFFECT
Assessment: Use Insight to learn an opponent's combat capabilities.
Benefit: Gain a significant perquisite or fringe benefit.
Diehard: Automatically stabilize when dying.
Eidetic Memory: Total recall, +5 circumstance bonus to remember things.
Equipment: 5 points of equipment per rank.
Extraordinary Effort: Gain two benefits when using extra effort.
Fearless: Immune to fear effects.
Great Endurance: +5 on checks involving endurance.
Instant Up: Stand from prone as a free action.
Interpose: Take an attack meant for an ally.
Minion: Gain a follower or minion with (15 x rank) power points.
Second Chance: Re-roll a failed check against a hazard once.
Sidekick: Gain a sidekick with (5 x rank) power points.
Teamwork: +5 bonus to support team checks.
Trance: Go into a deathlike trance that slows bodily functions.
```


#### Domain Sketch
Fortune advantage is the category label for advantages whose activation consumes a hero point, translating luck, inspiration, and leadership into mechanical effects.

- classifies each member advantage as requiring a hero point spend to activate its effect
- defines the specific outcome that the hero point purchase achieves (re-roll, group bonus, condition removal, or temporary skill ranks)
- Luck is an exception: it functions like a hero point re-roll but draws from a separate per-session pool rather than consuming an actual hero point

Invariant: each fortune advantage defines a hero-point-activated effect; hero point benefits in this category ignore power level limits.

#### Decisions made (term level)
- Luck is classified here despite not spending a hero point at use time: the re-roll mechanic is identical to a hero point re-roll and the source labels it FORTUNE.
- Beginner's Luck is classified here (FORTUNE) per the source's explicit label, even though its effect grants temporary skill ranks.
#### general advantage

- General advantages provide special abilities or passive bonuses not covered by combat, fortune, or skill categories.
- General advantages include: Assessment, Benefit, Diehard, Eidetic Memory, Equipment, Extraordinary Effort, Fearless, Great Endurance, Instant Up, Interpose, Minion, Second Chance, Sidekick, Teamwork, and Trance.
- General advantages often grant immunity effects, passive bonuses to specific checks, or access to additional character resources (Equipment, Minion, Sidekick).

**Ref — Ch5 Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_065.md
Locator: lines 4107-4148
Extract: whole

```source
## CHAPTER 5: ADVANTAGES
Heroes are more than just skilled, they often have amazing advantages, beyond the abilities of ordinary people. In MU-
TANTS & MASTERMINDS, advantages often allow heroes to break the rules, gaining access to and doing things most people
cannot, or simply doing them better.

### Acquiring Advantages
Advantages are rated in ranks and bought with power points, just like abilities and skills. Advantages cost 1 power point
per rank. Some advantages have no ranks and are acquired only once, effectively at rank 1.
Advantage Cost = 1 power point per advantage rank

### Advantage Descriptions
Each advantage's description explains the benefit it provides. It also says if the advantage can be acquired in ranks and
the effects of doing so. Such advantages are listed as "Ranked" alongside the advantage name. Ranks in a advantage are
noted with a number after the advantage's name, such as "Defensive Roll 2" (for a character who has taken two ranks
in the Defensive Roll advantage), just like skill and power ranks. If there is a maximum number of ranks a character can
take, it's listed in parentheses after the word "Ranked" in the advantage's heading.

### Types Of Advantages
Advantages are categorized as one of four types:
Combat Advantages are useful in combat and often modify how various combat maneuvers are performed.
Fortune Advantages require and enhance the use of hero points.
General Advantages provide special abilities or bonuses not covered by the other categories.
Skill Advantages offer bonuses or modifications to skill use.

### Advantage Descriptions
Each advantage is listed by name, type, and if the advantage is available in multiple ranks, followed by a description
of the advantage's benefits. The effects of additional ranks of the advantage (if any) are noted in the text of each
advantage. In some cases a advantage's description mentions the normal conditions for characters who do not have the
advantage for comparison.
```

**Ref — Fortune Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_068.md
Locator: lines 4287-4336
Extract: whole

```source
### Fortune Advantages
ADVANTAGE  EFFECT
Beginner's Luck: Spend a hero point to gain 5 temporary ranks in a skill.
Inspire: Spend a hero point to grant allies a +1 circumstance bonus per rank.
Leadership: Spend a hero point to remove a condition from an ally.
Luck: Re-roll a die roll once per rank.
Seize Initiative: Spend a hero point to go first in the initiative order.
Ultimate Effort: Spend a hero point to get an effective 20 on a specific check.

### General Advantages
ADVANTAGE  EFFECT
Assessment: Use Insight to learn an opponent's combat capabilities.
Benefit: Gain a significant perquisite or fringe benefit.
Diehard: Automatically stabilize when dying.
Eidetic Memory: Total recall, +5 circumstance bonus to remember things.
Equipment: 5 points of equipment per rank.
Extraordinary Effort: Gain two benefits when using extra effort.
Fearless: Immune to fear effects.
Great Endurance: +5 on checks involving endurance.
Instant Up: Stand from prone as a free action.
Interpose: Take an attack meant for an ally.
Minion: Gain a follower or minion with (15 x rank) power points.
Second Chance: Re-roll a failed check against a hazard once.
Sidekick: Gain a sidekick with (5 x rank) power points.
Teamwork: +5 bonus to support team checks.
Trance: Go into a deathlike trance that slows bodily functions.
```


#### Domain Sketch
General advantage is the residual category for advantages that provide passive bonuses, immunity-like effects, or access to additional character resources — anything not covered by Combat, Fortune, or Skill.

- classifies each member advantage as falling outside the three more specific categories
- grants passive bonuses (e.g., Great Endurance), immunity effects (e.g., Fearless), resource access (Equipment, Minion, Sidekick), or narrative perquisites (Benefit)
- takes effect passively, at character creation, or through explicit character management — never through combat maneuver declaration or hero point spending

Invariant: a general advantage never requires a combat maneuver declaration or a hero point expenditure to take effect.

#### Decisions made (term level)
- Equipment, Minion, and Sidekick are modeled as distinct terms because each governs a distinct resource with its own point budget, scaling formula, and replacement or improvement rules.
#### skill advantage

- Skill advantages grant bonuses, modifications, or new capabilities tied to the use of skills.
- Skill advantages include: Agile Feint, Animal Empathy, Artificer, Attractive, Connected, Contacts, Daze, Fascinate, Favored Foe, Hide in Plain Sight, Improvised Tools, Inventor, Jack-of-all-trades, Languages, Ritualist, Skill Mastery, Startle, Taunt, Tracking, and Well-informed.
- Skill advantages often allow a skill to be used in unusual circumstances, substitute one skill for another, or remove penalties for using a skill without proper tools or training.

**Ref — Ch5 Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_065.md
Locator: lines 4107-4148
Extract: whole

```source
## CHAPTER 5: ADVANTAGES
Heroes are more than just skilled, they often have amazing advantages, beyond the abilities of ordinary people. In MU-
TANTS & MASTERMINDS, advantages often allow heroes to break the rules, gaining access to and doing things most people
cannot, or simply doing them better.

### Acquiring Advantages
Advantages are rated in ranks and bought with power points, just like abilities and skills. Advantages cost 1 power point
per rank. Some advantages have no ranks and are acquired only once, effectively at rank 1.
Advantage Cost = 1 power point per advantage rank

### Advantage Descriptions
Each advantage's description explains the benefit it provides. It also says if the advantage can be acquired in ranks and
the effects of doing so. Such advantages are listed as "Ranked" alongside the advantage name. Ranks in a advantage are
noted with a number after the advantage's name, such as "Defensive Roll 2" (for a character who has taken two ranks
in the Defensive Roll advantage), just like skill and power ranks. If there is a maximum number of ranks a character can
take, it's listed in parentheses after the word "Ranked" in the advantage's heading.

### Types Of Advantages
Advantages are categorized as one of four types:
Combat Advantages are useful in combat and often modify how various combat maneuvers are performed.
Fortune Advantages require and enhance the use of hero points.
General Advantages provide special abilities or bonuses not covered by the other categories.
Skill Advantages offer bonuses or modifications to skill use.

### Advantage Descriptions
Each advantage is listed by name, type, and if the advantage is available in multiple ranks, followed by a description
of the advantage's benefits. The effects of additional ranks of the advantage (if any) are noted in the text of each
advantage. In some cases a advantage's description mentions the normal conditions for characters who do not have the
advantage for comparison.
```

**Ref — Skill Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_069.md
Locator: lines 4337-4450
Extract: whole

```source
### Skill Advantages
ADVANTAGE  EFFECT
Agile Feint: Feint using Acrobatics skill or movement speed.
Animal Empathy: Use interaction skills normally with animals.
Artificer: Use Expertise: Magic to create temporary magical devices.
Attractive: Circumstance bonus to interaction based on your looks.
Connected: Call in assistance or favors with a Persuasion check.
Contacts: Make an initial Investigation check in one minute.
Daze: Use Deception or Intimidation to daze an opponent.
Fascinate: Use an interaction skill to entrance others.
Favored Foe: Circumstance bonus to checks against a type of opponent.
Hide in Plain Sight: Hide while observed without need for a diversion.
Improvised Tools: No penalty for using skills without tools.
Inventor: Use Technology to create temporary devices.
Jack-of-all-trades: Use any skill untrained.
Languages: Speak and understand additional languages.
Ritualist: Use Expertise: Magic to create and perform rituals.
Skill Mastery: Make routine checks with one skill under any conditions.
Startle: Use Intimidation to feint in combat.
Taunt: Use Deception to demoralize in combat.
Tracking: Use Perception to follow tracks.
Well-informed: Immediate Investigation or Persuasion check to know something.

BEGINNER'S LUCK
FORTUNE
By spending a hero point, you gain an effective 5 ranks in one skill of your choice you currently have at 4 or fewer
ranks, including skills you have no ranks in, even if they can't be used untrained. These temporary skill ranks last
for the duration of the scene and grant you their normal benefits.

BENEFIT
GENERAL, RANKED
You have some significant perquisite or fringe benefit. The exact nature of the benefit is for you and the Gamemaster
to determine. As a rule of thumb it should not exceed the benefits of any other advantage, or a power effect costing
1 point. It should also be significant enough to cost at least 1 power point. An example is Diplomatic Immunity.
A license to practice law or medicine should not be considered a Benefit; it's simply a part of having training in
the appropriate Expertise skill and has no significant game effect.
Benefits may come in ranks for improved levels of the same benefit. The GM is the final arbiter as to what does and
does not constitute a Benefit in the setting.

Sample Benefits:
- Alternate Identity: You have an alternate identity, complete with legal paperwork.
- Ambidexterity: You are equally adept using either hand, suffering no circumstance penalty for using your off-hand.
- Cipher: Your true history is well hidden. Investigation checks concerning you are made at a -5 circumstance penalty per rank.
- Diplomatic Immunity: By dint of your diplomatic status, you cannot be prosecuted for crimes in nations other than your own.
- Security Clearance: You have access to classified government information, installations, and possibly equipment and personnel.
- Status: By virtue of birth or achievement, you have special status (nobility, knighthood, aristocracy, etc.).
- Wealth: You have greater than average wealth (well-off rank 1 through billionaire rank 5).
```


#### Domain Sketch
Skill advantage is the category label for advantages that modify the conditions, scope, or quality of skill use — broadening what skills can do, removing restrictions, or granting situational circumstance bonuses.

- classifies each member advantage as affecting skill use rather than combat maneuvers, hero points, or general character resources
- removes training requirements (Jack-of-all-trades), enables pressure-free routine checks (Skill Mastery), or grants circumstance bonuses against specific targets (Favored Foe)
- applies its effect through the skill system — not by modifying attack checks directly or activating through hero point spending

Invariant: a skill advantage always affects the application of skill rules and does not directly modify attack check mechanics or activate through hero point spending.

#### Decisions made (term level)
- Favored Foe is placed here (Skill Advantage) rather than Combat Enhancement because its bonus applies to four social and perception skill checks; the source classifies it SKILL.
---

### Attack Trade-off

An Attack Trade-off is a combat advantage that implements the core maneuver trade-off mechanic: the character voluntarily reduces one combat stat by up to 5 to add the same number (up to 5) to another combat stat for that attack. The four Attack Trade-off advantages form a symmetric group covering all four trade-off directions: Accurate Attack trades effect for accuracy; All-out Attack trades defense for accuracy; Defensive Attack trades accuracy for defense; Power Attack trades accuracy for effect. This KA owns the mechanic of deliberately exchanging one combat value for another and enforces the rule that neither the penalty nor the bonus may exceed 5. It interacts with the attack check and active defense (both owned by Combat) but does not own their resolution. The trade-off must always be symmetric: the penalty applied must equal the bonus received, and neither may exceed 5.

#### Decisions made
- All four trade-off advantages are grouped together because they share the identical mechanic structure (-N to X, +N to Y, max 5); grouping reveals the pattern that distinct stat-pair combinations produce distinct advantages.
- Accurate Attack and Power Attack are distinct from each other (effect penalty vs. accuracy penalty) and from All-out Attack and Defensive Attack (which involve active defenses); none is redundant.
- No terms moved out of this module from the Attack Trade-off KA.
- Open question: whether the online tool should expose a combined trade-off UI (slider) or four separate toggles.

#### Accurate Attack

- Accurate Attack is a combat advantage that enables a trade-off between effect modifier and attack bonus during an accurate attack maneuver.
- The player may take a penalty of up to -5 on the attack's effect modifier and add that same number (up to +5) to the attack bonus.
- Accurate Attack is used when the character needs to ensure they hit at the cost of dealing less damage or a weaker effect.

**Ref — Accurate Attack**
Source: context/rules/HeroesHandbook-rules__chunk_066.md
Locator: lines 4149-4188
Extract: whole

```source
### Accurate Attack
COMBAT
When you make an accurate attack (see Maneuvers, page 249) you can take a penalty of up to -5 on the effect modifier
of the attack and add the same number (up to +5) to your attack bonus.

### Agile Feint
SKILL
You can use your Acrobatics bonus or movement speed rank in place of Deception to feint and trick in combat as if
your skill bonus or speed rank were your Deception bonus. Your opponent opposes the attempt with Acrobatics or Insight
(whichever is better).

### All-Out Attack
COMBAT
When you make an all-out attack (see Maneuvers, page 249) you can take a penalty of up to -5 on your active defenses
(Dodge and Parry) and add the same number (up to +5) to your attack bonus.

### Animal Empathy
SKILL
You have a special connection with animals. You can use interaction skills on animals normally, and do not have to
speak a language the animal understands; you communicate your intent through gestures and body language and learn
things by studying animal behavior. Characters normally have a -10 circumstance penalty to use interaction skills on
animals, due to their Intellect and lack of language.

ARTIFICER
SKILL
You can use the Expertise: Magic skill to create temporary magical devices. See Magical Inventions, page 212, for details.
```

**Ref — Combat Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_067.md
Locator: lines 4189-4286
Extract: whole

```source
### Combat Advantages
ADVANTAGE  EFFECT
Accurate Attack: Trade effect DC for attack bonus.
All-out Attack: Trade active defense for attack bonus.
Chokehold: Suffocate an opponent you have successfully grabbed.
Close Attack: +1 bonus to close attack checks per rank.
Defensive Attack: Trade attack bonus for active defense bonus.
Defensive Roll: +1 active defense bonus to Toughness per rank.
Evasion: Circumstance bonus to avoid area effects.
Fast Grab: Make a free grab check after an unarmed attack.
Favored Environment: Circumstance bonus to attack or defense in an environment.
Grabbing Finesse: Substitute Dex for Str when making grab attacks.
Improved Aim: Double circumstance bonuses for aiming.
Improved Critical: +1 to critical threat range with an attack per rank.
Improved Defense: +2 bonus to active defense when you take the defend action.
Improved Disarm: No penalty for the disarm action.
Improved Grab: Make grab attacks with one arm. Not vulnerable while grabbing.
Improved Hold: -5 circumstance penalty to escape from your holds.
Improved Initiative: +4 bonus to initiative checks per rank.
Improved Smash: No penalty for the smash action.
Improved Trip: No penalty for the trip action.
Improvised Weapon: Use Unarmed Combat skill with improvised weapons, +1 damage bonus.
Move-by Action: Move both before and after your standard action.
Power Attack: Trade attack bonus for effect bonus.
Precise Attack: Ignore attack check penalties for either cover or concealment.
Prone Fighting: No penalties for fighting while prone.
Quick Draw: Draw a weapon as a free action.
Ranged Attack: +1 bonus to ranged attack checks per rank.
Redirect: Use Deception to redirect a missed attack at another target.
Set-up: Transfer the benefit of an interaction skill to an ally.
Takedown: Free extra attack when you incapacitate a minion.
Throwing Mastery: +1 damage bonus with thrown weapons per rank.
Uncanny Dodge: Not vulnerable when surprised or caught off-guard.
Weapon Bind: Free disarm attempt when you actively defend.
Weapon Break: Free smash attack when you actively defend.
```


#### Domain Sketch
Accurate Attack enables a symmetric trade-off between effect potency and attack accuracy during an accurate attack maneuver.

- declares a penalty of up to −5 on the effect modifier before the attack roll is made
- applies the same value as a bonus to the attack check for that attack (up to +5)
- enforces that penalty and bonus are equal in magnitude and neither exceeds 5
- resolves only during an accurate attack maneuver — declaration must happen before the attack roll

Invariant: penalty taken must equal bonus gained; neither the penalty nor the bonus may exceed 5; declaration must precede the attack roll.

#### Decisions made (term level)
- Grouped with All-out Attack, Defensive Attack, and Power Attack under Attack Trade-off: all four implement the identical symmetric exchange pattern (−N to one stat, +N to another, max 5).
#### All-out Attack

- All-out Attack is a combat advantage that enables a trade-off between active defenses and attack bonus during an all-out attack maneuver.
- The player may take a penalty of up to -5 on active defenses (Dodge and Parry) and add that same number (up to +5) to the attack bonus.
- All-out Attack suits characters who prioritize landing hits over maintaining their own defenses.

**Ref — Accurate Attack**
Source: context/rules/HeroesHandbook-rules__chunk_066.md
Locator: lines 4149-4188
Extract: whole

```source
### Accurate Attack
COMBAT
When you make an accurate attack (see Maneuvers, page 249) you can take a penalty of up to -5 on the effect modifier
of the attack and add the same number (up to +5) to your attack bonus.

### Agile Feint
SKILL
You can use your Acrobatics bonus or movement speed rank in place of Deception to feint and trick in combat as if
your skill bonus or speed rank were your Deception bonus. Your opponent opposes the attempt with Acrobatics or Insight
(whichever is better).

### All-Out Attack
COMBAT
When you make an all-out attack (see Maneuvers, page 249) you can take a penalty of up to -5 on your active defenses
(Dodge and Parry) and add the same number (up to +5) to your attack bonus.

### Animal Empathy
SKILL
You have a special connection with animals. You can use interaction skills on animals normally, and do not have to
speak a language the animal understands; you communicate your intent through gestures and body language and learn
things by studying animal behavior. Characters normally have a -10 circumstance penalty to use interaction skills on
animals, due to their Intellect and lack of language.

ARTIFICER
SKILL
You can use the Expertise: Magic skill to create temporary magical devices. See Magical Inventions, page 212, for details.
```

**Ref — Combat Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_067.md
Locator: lines 4189-4286
Extract: whole

```source
### Combat Advantages
ADVANTAGE  EFFECT
Accurate Attack: Trade effect DC for attack bonus.
All-out Attack: Trade active defense for attack bonus.
Chokehold: Suffocate an opponent you have successfully grabbed.
Close Attack: +1 bonus to close attack checks per rank.
Defensive Attack: Trade attack bonus for active defense bonus.
Defensive Roll: +1 active defense bonus to Toughness per rank.
Evasion: Circumstance bonus to avoid area effects.
Fast Grab: Make a free grab check after an unarmed attack.
Favored Environment: Circumstance bonus to attack or defense in an environment.
Grabbing Finesse: Substitute Dex for Str when making grab attacks.
Improved Aim: Double circumstance bonuses for aiming.
Improved Critical: +1 to critical threat range with an attack per rank.
Improved Defense: +2 bonus to active defense when you take the defend action.
Improved Disarm: No penalty for the disarm action.
Improved Grab: Make grab attacks with one arm. Not vulnerable while grabbing.
Improved Hold: -5 circumstance penalty to escape from your holds.
Improved Initiative: +4 bonus to initiative checks per rank.
Improved Smash: No penalty for the smash action.
Improved Trip: No penalty for the trip action.
Improvised Weapon: Use Unarmed Combat skill with improvised weapons, +1 damage bonus.
Move-by Action: Move both before and after your standard action.
Power Attack: Trade attack bonus for effect bonus.
Precise Attack: Ignore attack check penalties for either cover or concealment.
Prone Fighting: No penalties for fighting while prone.
Quick Draw: Draw a weapon as a free action.
Ranged Attack: +1 bonus to ranged attack checks per rank.
Redirect: Use Deception to redirect a missed attack at another target.
Set-up: Transfer the benefit of an interaction skill to an ally.
Takedown: Free extra attack when you incapacitate a minion.
Throwing Mastery: +1 damage bonus with thrown weapons per rank.
Uncanny Dodge: Not vulnerable when surprised or caught off-guard.
Weapon Bind: Free disarm attempt when you actively defend.
Weapon Break: Free smash attack when you actively defend.
```


#### Domain Sketch
All-out Attack enables a symmetric trade-off between defensive capability and attack accuracy during an all-out attack maneuver.

- declares a penalty of up to −5 on both active defenses (Dodge and Parry) before the attack roll
- applies the same value as a bonus to the attack check for that attack (up to +5)
- enforces that penalty and bonus are equal in magnitude and neither exceeds 5
- resolves only during an all-out attack maneuver — declaration must happen before the attack roll

Invariant: penalty and bonus are equal; neither exceeds 5; both Dodge and Parry take the full penalty together; declaration precedes the attack roll.

#### Decisions made (term level)
- Distinct from Defensive Attack (inverse direction: defenses → accuracy) and from Power Attack (trades accuracy for effect, not defense for accuracy).
#### Defensive Attack

- Defensive Attack is a combat advantage that enables a trade-off between attack bonus and active defenses during a defensive attack maneuver.
- The player may take a penalty of up to -5 on the attack bonus and add that same number (up to +5) to both active defenses (Dodge and Parry).
- Defensive Attack is the inverse of All-out Attack: sacrificing offensive power for increased defensive capability.

**Ref — Defensive Attack**
Source: context/rules/HeroesHandbook-rules__chunk_071.md
Locator: lines 4495-4547
Extract: whole

```source
### Defensive Attack
COMBAT
When you make a defensive attack (see Maneuvers, page 249), you can take a penalty of up to -5 on your attack
bonus and add the same number (up to +5) to both your active defenses (Dodge and Parry).

### Defensive Roll
COMBAT, RANKED
You can avoid damage through agility and "rolling" with an attack. You receive a bonus to your Toughness equal
to your advantage rank, but it is considered an active defense similar to Dodge and Parry, so you lose this bonus
whenever you are vulnerable or defenseless. Your total Toughness, including this advantage, is still limited by power level.

DIEHARD
General
When your condition becomes dying you automatically stabilize on the following round without any need for a
Fortitude check, although further damage can still kill you.

EQUIPMENT
GENERAL, RANKED
You have 5 points per rank in this advantage to spend on equipment. This includes vehicles and headquarters. See
the Gadgets & Gear chapter for details on equipment and its costs. Many heroes rely almost solely on Equipment
in conjunction with their skills and other advantages.

EVASION
COMBAT, RANKED (2)
You have a +2 circumstance bonus to Dodge resistance checks to avoid area effects. If you have 2 ranks in this
advantage, your circumstance bonus increases to +5.
```

**Ref — Combat Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_067.md
Locator: lines 4189-4286
Extract: whole

```source
### Combat Advantages
ADVANTAGE  EFFECT
Accurate Attack: Trade effect DC for attack bonus.
All-out Attack: Trade active defense for attack bonus.
Chokehold: Suffocate an opponent you have successfully grabbed.
Close Attack: +1 bonus to close attack checks per rank.
Defensive Attack: Trade attack bonus for active defense bonus.
Defensive Roll: +1 active defense bonus to Toughness per rank.
Evasion: Circumstance bonus to avoid area effects.
Fast Grab: Make a free grab check after an unarmed attack.
Favored Environment: Circumstance bonus to attack or defense in an environment.
Grabbing Finesse: Substitute Dex for Str when making grab attacks.
Improved Aim: Double circumstance bonuses for aiming.
Improved Critical: +1 to critical threat range with an attack per rank.
Improved Defense: +2 bonus to active defense when you take the defend action.
Improved Disarm: No penalty for the disarm action.
Improved Grab: Make grab attacks with one arm. Not vulnerable while grabbing.
Improved Hold: -5 circumstance penalty to escape from your holds.
Improved Initiative: +4 bonus to initiative checks per rank.
Improved Smash: No penalty for the smash action.
Improved Trip: No penalty for the trip action.
Improvised Weapon: Use Unarmed Combat skill with improvised weapons, +1 damage bonus.
Move-by Action: Move both before and after your standard action.
Power Attack: Trade attack bonus for effect bonus.
Precise Attack: Ignore attack check penalties for either cover or concealment.
Prone Fighting: No penalties for fighting while prone.
Quick Draw: Draw a weapon as a free action.
Ranged Attack: +1 bonus to ranged attack checks per rank.
Redirect: Use Deception to redirect a missed attack at another target.
Set-up: Transfer the benefit of an interaction skill to an ally.
Takedown: Free extra attack when you incapacitate a minion.
Throwing Mastery: +1 damage bonus with thrown weapons per rank.
Uncanny Dodge: Not vulnerable when surprised or caught off-guard.
Weapon Bind: Free disarm attempt when you actively defend.
Weapon Break: Free smash attack when you actively defend.
```


#### Domain Sketch
Defensive Attack enables a symmetric trade-off between attack accuracy and defensive capability during a defensive attack maneuver.

- declares a penalty of up to −5 on the attack check before the roll
- applies the same value as a bonus to both active defenses (Dodge and Parry) for the round (up to +5)
- enforces that penalty and bonus are equal in magnitude and neither exceeds 5
- resolves only during a defensive attack maneuver — declaration must happen before the attack roll

Invariant: penalty must equal bonus; neither exceeds 5; both Dodge and Parry receive the full bonus as a pair; declaration precedes the attack roll.

#### Decisions made (term level)
- Defensive Attack is the inverse of All-out Attack: direction of trade reversed (accuracy → defenses vs. defenses → accuracy); mechanic otherwise structurally identical.
#### Power Attack

- Power Attack is a combat advantage that enables a trade-off between attack bonus and effect bonus during a power attack maneuver.
- The player may take a penalty of up to -5 on the attack bonus and add that same number (up to +5) to the attack's effect bonus.
- Power Attack is the inverse of Accurate Attack: sacrificing accuracy for increased damage or effect potency.

**Ref — Move-By Action**
Source: context/rules/HeroesHandbook-rules__chunk_078.md
Locator: lines 4852-4908
Extract: whole

```source
### Move-By Action
COMBAT
When taking a standard action and a move action you can move both before and after your standard action, provided
the total distance moved isn't greater than your normal movement speed.

### Power Attack
COMBAT
When you make a power attack (see Maneuvers, page 250) you can take a penalty of up to -5 on your attack bonus and
add the same number (up to +5) to the effect bonus of your attack.

### Precise Attack
COMBAT, RANKED (4)
When you make close or ranged attacks (choose one) you ignore attack check penalties for cover or concealment (choose
one), although total cover still prevents you from making attacks. Each additional rank in this advantage lets you choose
an additional option, so with Precise Attack 4, all your attacks ignore penalties for both cover and concealment.

### Prone Fighting
COMBAT
You suffer no circumstance penalty to attack checks for being prone, and adjacent opponents do not gain the usual
circumstance bonus for close attacks against you.

### Quick Draw
COMBAT
You can draw a weapon from a holster or sheath as a free action, rather than a move action.

### Ranged Attack
COMBAT, RANKED
You have a +1 bonus to ranged attacks checks per rank in this advantage. Your total attack bonus is still limited by
power level.
```

**Ref — Combat Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_067.md
Locator: lines 4189-4286
Extract: whole

```source
### Combat Advantages
ADVANTAGE  EFFECT
Accurate Attack: Trade effect DC for attack bonus.
All-out Attack: Trade active defense for attack bonus.
Chokehold: Suffocate an opponent you have successfully grabbed.
Close Attack: +1 bonus to close attack checks per rank.
Defensive Attack: Trade attack bonus for active defense bonus.
Defensive Roll: +1 active defense bonus to Toughness per rank.
Evasion: Circumstance bonus to avoid area effects.
Fast Grab: Make a free grab check after an unarmed attack.
Favored Environment: Circumstance bonus to attack or defense in an environment.
Grabbing Finesse: Substitute Dex for Str when making grab attacks.
Improved Aim: Double circumstance bonuses for aiming.
Improved Critical: +1 to critical threat range with an attack per rank.
Improved Defense: +2 bonus to active defense when you take the defend action.
Improved Disarm: No penalty for the disarm action.
Improved Grab: Make grab attacks with one arm. Not vulnerable while grabbing.
Improved Hold: -5 circumstance penalty to escape from your holds.
Improved Initiative: +4 bonus to initiative checks per rank.
Improved Smash: No penalty for the smash action.
Improved Trip: No penalty for the trip action.
Improvised Weapon: Use Unarmed Combat skill with improvised weapons, +1 damage bonus.
Move-by Action: Move both before and after your standard action.
Power Attack: Trade attack bonus for effect bonus.
Precise Attack: Ignore attack check penalties for either cover or concealment.
Prone Fighting: No penalties for fighting while prone.
Quick Draw: Draw a weapon as a free action.
Ranged Attack: +1 bonus to ranged attack checks per rank.
Redirect: Use Deception to redirect a missed attack at another target.
Set-up: Transfer the benefit of an interaction skill to an ally.
Takedown: Free extra attack when you incapacitate a minion.
Throwing Mastery: +1 damage bonus with thrown weapons per rank.
Uncanny Dodge: Not vulnerable when surprised or caught off-guard.
Weapon Bind: Free disarm attempt when you actively defend.
Weapon Break: Free smash attack when you actively defend.
```


#### Domain Sketch
Power Attack enables a symmetric trade-off between attack accuracy and effect potency during a power attack maneuver.

- declares a penalty of up to −5 on the attack check before the roll
- applies the same value as a bonus to the effect modifier of the attack (up to +5)
- enforces that penalty and bonus are equal in magnitude and neither exceeds 5
- resolves only during a power attack maneuver — declaration must happen before the attack roll

Invariant: penalty must equal bonus; neither exceeds 5; declaration precedes the attack roll.

#### Decisions made (term level)
- Power Attack is the inverse of Accurate Attack: Accurate Attack trades effect for accuracy; Power Attack trades accuracy for effect. Both operate on the same stat pair in opposite directions.
---

### Combat Enhancement

A Combat Enhancement is a combat advantage that provides a direct bonus to a specific combat parameter without requiring a trade-off against another stat. These advantages increase combat effectiveness unconditionally when their triggering condition is met. Improved Initiative grants +4 per rank to initiative checks; Improved Critical expands the critical threat range by 1 per rank; Ranged Attack and Close Attack each grant +1 per rank to their respective attack checks (both capped by power level); Favored Environment provides a per-round +2 circumstance bonus to attack or defense that is not power-level-capped. This KA interacts with the attack check and initiative systems owned by Combat, and with the power level cap owned by Character Construction.

#### Decisions made
- Improved Initiative, Improved Critical, Ranged Attack, Close Attack, and Favored Environment are grouped here rather than in Attack Trade-off because none requires a penalty: they are pure additions, not exchanges.
- Favored Environment is placed in Combat Enhancement (not Skill Enhancement) because its primary effect is a combat bonus applied at the start of each round.
- No terms moved out of this module from the Combat Enhancement KA.

#### Improved Initiative

- Improved Initiative is a ranked combat advantage that grants a +4 bonus to initiative checks per rank.
- Initiative determines the order of acting in combat; Improved Initiative allows the character to act earlier in the turn order.
- Each rank stacks for a cumulative +4 per rank (e.g., Improved Initiative 2 gives +8 to initiative checks).

**Ref — Improved Disarm**
Source: context/rules/HeroesHandbook-rules__chunk_075.md
Locator: lines 4705-4748
Extract: whole

```source
### Improved Disarm
COMBAT
You have no penalty to your attack check when attempting to disarm an opponent and they do not get the opportunity
to disarm you.

### Improved Grab
COMBAT
You can make grab attacks with only one arm, leaving the other free. You can also maintain the grab while using your
other hand to perform actions. You are not vulnerable while grabbing.

### Improved Hold
COMBAT
Your grab attacks are particularly difficult to escape. Opponents you grab suffer a -5 circumstance penalty on checks
to escape.

### Improved Initiative
COMBAT, RANKED
You have a +4 bonus to your initiative checks per rank in this advantage.

### Improved Smash
COMBAT
You have no penalty to attack checks to hit an object held by another character.

### Improved Trip
COMBAT
You have no penalty to your attack check to trip an opponent and they do not get the opportunity to trip you.
When making a trip attack, make an opposed check of your Acrobatics or Athletics against your opponent's Acrobatics
or Athletics, you choose which your opponent uses to defend, rather than the target choosing.
```

**Ref — Combat Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_067.md
Locator: lines 4189-4286
Extract: whole

```source
### Combat Advantages
ADVANTAGE  EFFECT
Accurate Attack: Trade effect DC for attack bonus.
All-out Attack: Trade active defense for attack bonus.
Chokehold: Suffocate an opponent you have successfully grabbed.
Close Attack: +1 bonus to close attack checks per rank.
Defensive Attack: Trade attack bonus for active defense bonus.
Defensive Roll: +1 active defense bonus to Toughness per rank.
Evasion: Circumstance bonus to avoid area effects.
Fast Grab: Make a free grab check after an unarmed attack.
Favored Environment: Circumstance bonus to attack or defense in an environment.
Grabbing Finesse: Substitute Dex for Str when making grab attacks.
Improved Aim: Double circumstance bonuses for aiming.
Improved Critical: +1 to critical threat range with an attack per rank.
Improved Defense: +2 bonus to active defense when you take the defend action.
Improved Disarm: No penalty for the disarm action.
Improved Grab: Make grab attacks with one arm. Not vulnerable while grabbing.
Improved Hold: -5 circumstance penalty to escape from your holds.
Improved Initiative: +4 bonus to initiative checks per rank.
Improved Smash: No penalty for the smash action.
Improved Trip: No penalty for the trip action.
Improvised Weapon: Use Unarmed Combat skill with improvised weapons, +1 damage bonus.
Move-by Action: Move both before and after your standard action.
Power Attack: Trade attack bonus for effect bonus.
Precise Attack: Ignore attack check penalties for either cover or concealment.
Prone Fighting: No penalties for fighting while prone.
Quick Draw: Draw a weapon as a free action.
Ranged Attack: +1 bonus to ranged attack checks per rank.
Redirect: Use Deception to redirect a missed attack at another target.
Set-up: Transfer the benefit of an interaction skill to an ally.
Takedown: Free extra attack when you incapacitate a minion.
Throwing Mastery: +1 damage bonus with thrown weapons per rank.
Uncanny Dodge: Not vulnerable when surprised or caught off-guard.
Weapon Bind: Free disarm attempt when you actively defend.
Weapon Break: Free smash attack when you actively defend.
```


#### Domain Sketch
Improved Initiative passively raises the character's position in the initiative order by boosting their initiative check result.

- adds +4 per rank to every initiative check without requiring any activation or declaration
- stacks cumulatively: Improved Initiative 2 grants +8, rank 3 grants +12, and so on
- applies automatically to every initiative check for as long as the advantage is held

Invariant: bonus is exactly +4 per rank and applies to all initiative checks without exception; no per-round declaration is needed.

#### Decisions made (term level)
- Modeled as a passive bonus (no player action required): the source describes it as a flat bonus, not a situational option.
#### Improved Critical

- Improved Critical is a ranked combat advantage that increases the critical threat range with a specific attack by 1 per rank.
- Base critical threat is natural 20; Improved Critical 1 extends this to natural 19-20; maximum threat range of 16-20 with 4 ranks.
- Only a natural 20 is an automatic hit; an attack that misses is not a critical hit even if the roll falls in the threat range.
- Each rank applies to a different attack or increases the threat range of an existing attack by one more.
- The chosen attack type is specified when the advantage is acquired.

**Ref — Great Endurance**
Source: context/rules/HeroesHandbook-rules__chunk_074.md
Locator: lines 4659-4704
Extract: whole

```source
### Great Endurance
General
You have a +5 bonus on checks to avoid becoming fatigued and checks to hold your breath, avoid damage from
starvation or thirst, avoid damage from hot or cold environments, and to resist suffocation and drowning.

### Hide In Plain Sight
SKILL
You can hide without any need for a Deception or Intimidation check or any sort of diversion, and without penalty
to your Stealth check. You're literally there one moment, and gone the next. You must still have some form of cover
or concealment within range of your normal movement speed in order to hide.

### Improved Aim
COMBAT
You have an even keener eye when it comes to ranged combat. When you take a standard action to aim, you gain double
the normal circumstance bonus: +10 for a close attack or ranged attack adjacent to the target, +5 for a ranged
attack at a greater distance.

### Improved Critical
COMBAT, RANKED
Increase your critical threat range with a particular attack (chosen when you acquire this advantage) by 1, allowing
you to score a critical hit on a natural 19 or 20. Only a natural 20 is an automatic hit, however, and an attack that
misses is not a critical. Each additional rank applies to a different attack or increases your threat range with an
existing attack by one more, to a maximum threat range of 16-20 with 4 ranks.

### Improved Defense
COMBAT
When you take the defend action in combat you gain a +2 circumstance bonus to your active defense checks for the round.
```

**Ref — Combat Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_067.md
Locator: lines 4189-4286
Extract: whole

```source
### Combat Advantages
ADVANTAGE  EFFECT
Accurate Attack: Trade effect DC for attack bonus.
All-out Attack: Trade active defense for attack bonus.
Chokehold: Suffocate an opponent you have successfully grabbed.
Close Attack: +1 bonus to close attack checks per rank.
Defensive Attack: Trade attack bonus for active defense bonus.
Defensive Roll: +1 active defense bonus to Toughness per rank.
Evasion: Circumstance bonus to avoid area effects.
Fast Grab: Make a free grab check after an unarmed attack.
Favored Environment: Circumstance bonus to attack or defense in an environment.
Grabbing Finesse: Substitute Dex for Str when making grab attacks.
Improved Aim: Double circumstance bonuses for aiming.
Improved Critical: +1 to critical threat range with an attack per rank.
Improved Defense: +2 bonus to active defense when you take the defend action.
Improved Disarm: No penalty for the disarm action.
Improved Grab: Make grab attacks with one arm. Not vulnerable while grabbing.
Improved Hold: -5 circumstance penalty to escape from your holds.
Improved Initiative: +4 bonus to initiative checks per rank.
Improved Smash: No penalty for the smash action.
Improved Trip: No penalty for the trip action.
Improvised Weapon: Use Unarmed Combat skill with improvised weapons, +1 damage bonus.
Move-by Action: Move both before and after your standard action.
Power Attack: Trade attack bonus for effect bonus.
Precise Attack: Ignore attack check penalties for either cover or concealment.
Prone Fighting: No penalties for fighting while prone.
Quick Draw: Draw a weapon as a free action.
Ranged Attack: +1 bonus to ranged attack checks per rank.
Redirect: Use Deception to redirect a missed attack at another target.
Set-up: Transfer the benefit of an interaction skill to an ally.
Takedown: Free extra attack when you incapacitate a minion.
Throwing Mastery: +1 damage bonus with thrown weapons per rank.
Uncanny Dodge: Not vulnerable when surprised or caught off-guard.
Weapon Bind: Free disarm attempt when you actively defend.
Weapon Break: Free smash attack when you actively defend.
```


#### Domain Sketch
Improved Critical passively extends the range of die rolls that qualify as critical threats for a specified attack type.

- records the specified attack type at acquisition time — the advantage is bound to that attack type
- extends the critical threat range by 1 per rank: base natural 20; rank 1 = 19–20; rank 4 = 16–20 (maximum)
- validates that a roll in the threat range that misses is not treated as a critical hit
- applies automatically to every attack of the specified type — no per-attack declaration required

Invariant: maximum threat range is 16–20 (4 ranks); only natural 20 is an automatic hit; an attack that misses is never a critical hit even within the threat range; advantage is bound to one specified attack type per rank.

#### Decisions made (term level)
- Each rank can expand the same attack's range or bind to a different attack type — the system must store which attacks have extended ranges and by how much.
#### Ranged Attack

- Ranged Attack is a ranked combat advantage that grants +1 to ranged attack checks per rank.
- The total attack bonus from Ranged Attack is still limited by the series power level.
- Ranged Attack suits characters with broad ranged combat skill across multiple attack types; for a specific ranged attack type, the Ranged Combat skill is preferred.

**Ref — Move-By Action**
Source: context/rules/HeroesHandbook-rules__chunk_078.md
Locator: lines 4852-4908
Extract: whole

```source
### Move-By Action
COMBAT
When taking a standard action and a move action you can move both before and after your standard action, provided
the total distance moved isn't greater than your normal movement speed.

### Power Attack
COMBAT
When you make a power attack (see Maneuvers, page 250) you can take a penalty of up to -5 on your attack bonus and
add the same number (up to +5) to the effect bonus of your attack.

### Precise Attack
COMBAT, RANKED (4)
When you make close or ranged attacks (choose one) you ignore attack check penalties for cover or concealment (choose
one), although total cover still prevents you from making attacks. Each additional rank in this advantage lets you choose
an additional option, so with Precise Attack 4, all your attacks ignore penalties for both cover and concealment.

### Prone Fighting
COMBAT
You suffer no circumstance penalty to attack checks for being prone, and adjacent opponents do not gain the usual
circumstance bonus for close attacks against you.

### Quick Draw
COMBAT
You can draw a weapon from a holster or sheath as a free action, rather than a move action.

### Ranged Attack
COMBAT, RANKED
You have a +1 bonus to ranged attacks checks per rank in this advantage. Your total attack bonus is still limited by
power level.
```

**Ref — Combat Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_067.md
Locator: lines 4189-4286
Extract: whole

```source
### Combat Advantages
ADVANTAGE  EFFECT
Accurate Attack: Trade effect DC for attack bonus.
All-out Attack: Trade active defense for attack bonus.
Chokehold: Suffocate an opponent you have successfully grabbed.
Close Attack: +1 bonus to close attack checks per rank.
Defensive Attack: Trade attack bonus for active defense bonus.
Defensive Roll: +1 active defense bonus to Toughness per rank.
Evasion: Circumstance bonus to avoid area effects.
Fast Grab: Make a free grab check after an unarmed attack.
Favored Environment: Circumstance bonus to attack or defense in an environment.
Grabbing Finesse: Substitute Dex for Str when making grab attacks.
Improved Aim: Double circumstance bonuses for aiming.
Improved Critical: +1 to critical threat range with an attack per rank.
Improved Defense: +2 bonus to active defense when you take the defend action.
Improved Disarm: No penalty for the disarm action.
Improved Grab: Make grab attacks with one arm. Not vulnerable while grabbing.
Improved Hold: -5 circumstance penalty to escape from your holds.
Improved Initiative: +4 bonus to initiative checks per rank.
Improved Smash: No penalty for the smash action.
Improved Trip: No penalty for the trip action.
Improvised Weapon: Use Unarmed Combat skill with improvised weapons, +1 damage bonus.
Move-by Action: Move both before and after your standard action.
Power Attack: Trade attack bonus for effect bonus.
Precise Attack: Ignore attack check penalties for either cover or concealment.
Prone Fighting: No penalties for fighting while prone.
Quick Draw: Draw a weapon as a free action.
Ranged Attack: +1 bonus to ranged attack checks per rank.
Redirect: Use Deception to redirect a missed attack at another target.
Set-up: Transfer the benefit of an interaction skill to an ally.
Takedown: Free extra attack when you incapacitate a minion.
Throwing Mastery: +1 damage bonus with thrown weapons per rank.
Uncanny Dodge: Not vulnerable when surprised or caught off-guard.
Weapon Bind: Free disarm attempt when you actively defend.
Weapon Break: Free smash attack when you actively defend.
```


#### Domain Sketch
Ranged Attack passively raises the character's bonus on all ranged attack checks, making them broadly effective across ranged attack types.

- adds +1 per rank to all ranged attack checks without targeting a specific attack type
- applies passively to every ranged attack — no declaration or activation required
- remains subject to the series power level cap on total attack bonus

Invariant: total attack bonus including Ranged Attack is always subject to power level cap; bonus applies to all ranged attacks without exception.

#### Decisions made (term level)
- Distinguished from the Ranged Combat skill: Ranged Attack is a broad bonus across all ranged attacks; Ranged Combat skill is for one specific attack type. Both can coexist.
#### Close Attack

- Close Attack is a ranked combat advantage that grants +1 to close attack checks per rank.
- The total attack bonus from Close Attack is still limited by the series power level.
- Close Attack suits characters with broad close combat skill (both armed and unarmed); for a specific close attack type, the Close Combat skill is preferred.

**Ref — Close Attack**
Source: context/rules/HeroesHandbook-rules__chunk_070.md
Locator: lines 4451-4494
Extract: whole

```source
### Close Attack
COMBAT, RANKED
You have a +1 bonus to close attacks checks per rank in this advantage. Your total attack bonus is still limited by
power level. This advantage best suits characters with a level of overall close combat skill (armed and unarmed).
For capability with a particular type of attack, use the Close Combat skill.

CONNECTED
SKILL
You know people who can help you out from time to time. It might be advice, information, help with a legal matter,
or access to resources. You can call in such favors by making a Persuasion check. The GM sets the DC of the check,
based on the aid required. A simple favor is DC 10, ranging up to DC 25 or higher for especially difficult, dangerous,
or expensive favors. You can spend a hero point to automatically secure the favor, if the GM allows it.

CONTACTS
SKILL
You have such extensive and well-informed contacts you can make an Investigation check to gather information in only
one minute, assuming you have some means of getting in touch with your contacts. Further Investigation checks to
gather information on the same subject require the normal length of time, since you must go beyond your immediate
network of contacts.

DAZE
SKILL, RANKED (2)
You can make a Deception or Intimidation check as a standard action to cause an opponent to hesitate in combat.
Make a skill check against your target's resistance check (the same skill, Insight, or Will defense, whichever has
the highest bonus). If you win, your target is dazed (able to take only a standard action) until the end of your
next round. The ability to Daze with Deception and with Intimidation are separate advantages.
```

**Ref — Combat Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_067.md
Locator: lines 4189-4286
Extract: whole

```source
### Combat Advantages
ADVANTAGE  EFFECT
Accurate Attack: Trade effect DC for attack bonus.
All-out Attack: Trade active defense for attack bonus.
Chokehold: Suffocate an opponent you have successfully grabbed.
Close Attack: +1 bonus to close attack checks per rank.
Defensive Attack: Trade attack bonus for active defense bonus.
Defensive Roll: +1 active defense bonus to Toughness per rank.
Evasion: Circumstance bonus to avoid area effects.
Fast Grab: Make a free grab check after an unarmed attack.
Favored Environment: Circumstance bonus to attack or defense in an environment.
Grabbing Finesse: Substitute Dex for Str when making grab attacks.
Improved Aim: Double circumstance bonuses for aiming.
Improved Critical: +1 to critical threat range with an attack per rank.
Improved Defense: +2 bonus to active defense when you take the defend action.
Improved Disarm: No penalty for the disarm action.
Improved Grab: Make grab attacks with one arm. Not vulnerable while grabbing.
Improved Hold: -5 circumstance penalty to escape from your holds.
Improved Initiative: +4 bonus to initiative checks per rank.
Improved Smash: No penalty for the smash action.
Improved Trip: No penalty for the trip action.
Improvised Weapon: Use Unarmed Combat skill with improvised weapons, +1 damage bonus.
Move-by Action: Move both before and after your standard action.
Power Attack: Trade attack bonus for effect bonus.
Precise Attack: Ignore attack check penalties for either cover or concealment.
Prone Fighting: No penalties for fighting while prone.
Quick Draw: Draw a weapon as a free action.
Ranged Attack: +1 bonus to ranged attack checks per rank.
Redirect: Use Deception to redirect a missed attack at another target.
Set-up: Transfer the benefit of an interaction skill to an ally.
Takedown: Free extra attack when you incapacitate a minion.
Throwing Mastery: +1 damage bonus with thrown weapons per rank.
Uncanny Dodge: Not vulnerable when surprised or caught off-guard.
Weapon Bind: Free disarm attempt when you actively defend.
Weapon Break: Free smash attack when you actively defend.
```


#### Domain Sketch
Close Attack passively raises the character's bonus on all close attack checks — armed and unarmed — making them broadly effective in melee.

- adds +1 per rank to all close attack checks (armed and unarmed) without targeting a specific attack type
- applies passively to every close attack — no declaration or activation required
- remains subject to the series power level cap on total attack bonus

Invariant: total attack bonus including Close Attack is always subject to power level cap; bonus applies to all close attacks without exception.

#### Decisions made (term level)
- Distinguished from the Close Combat skill: Close Attack is a broad bonus across all close attacks; Close Combat skill is for one specific attack type. Both can coexist.
#### Favored Environment

- Favored Environment is a combat advantage tied to a specific environment (e.g., air, underwater, space, extreme heat, jungles) where the character excels.
- While in the favored environment, the character gains a +2 circumstance bonus to either attack checks or active defenses; the choice is made at the start of each round.
- The +2 circumstance bonus from Favored Environment is not affected by power level limits.
- Examples of favored environments include in the air, underwater, in space, in extreme heat or cold, and in jungles or woodlands.

**Ref — Fast Grab**
Source: context/rules/HeroesHandbook-rules__chunk_073.md
Locator: lines 4614-4658
Extract: whole

```source
### Fast Grab
COMBAT
When you hit with an unarmed attack you can immediately make a grab check against that opponent as a free action.
Your unarmed attack inflicts its normal damage and counts as the initial attack check required to grab your opponent.

### Favored Environment
COMBAT
You have an environment you're especially suited for fighting in. Examples include in the air, underwater, in space,
in extreme heat or cold, in jungles or woodlands, and so forth. While you are in your favored environment, you gain a
+2 circumstance bonus to attack checks or your active defenses. Choose at the start of the round whether the bonus
applies to attack or defense. The choice remains until the start of your next round. This circumstance bonus is not
affected by power level.

### Favored Foe
SKILL
You have a particular type of opponent you've studied or are especially effective against. It may be a type of creature
(aliens, animals, constructs, mutants, undead, etc.), a profession (soldiers, police officers, Yakuza, etc.) or any
other category the GM approves. Especially broad categories like "humans" or "villains" are not permitted. You gain a
+2 circumstance bonus on Deception, Intimidation, Insight, and Perception checks dealing with your Favored Foe. This
circumstance bonus is not limited by power level.

FEARLESS
General
You are immune to fear effects of all sorts, essentially the same as an Immunity to Fear effect.
```

**Ref — Combat Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_067.md
Locator: lines 4189-4286
Extract: whole

```source
### Combat Advantages
ADVANTAGE  EFFECT
Accurate Attack: Trade effect DC for attack bonus.
All-out Attack: Trade active defense for attack bonus.
Chokehold: Suffocate an opponent you have successfully grabbed.
Close Attack: +1 bonus to close attack checks per rank.
Defensive Attack: Trade attack bonus for active defense bonus.
Defensive Roll: +1 active defense bonus to Toughness per rank.
Evasion: Circumstance bonus to avoid area effects.
Fast Grab: Make a free grab check after an unarmed attack.
Favored Environment: Circumstance bonus to attack or defense in an environment.
Grabbing Finesse: Substitute Dex for Str when making grab attacks.
Improved Aim: Double circumstance bonuses for aiming.
Improved Critical: +1 to critical threat range with an attack per rank.
Improved Defense: +2 bonus to active defense when you take the defend action.
Improved Disarm: No penalty for the disarm action.
Improved Grab: Make grab attacks with one arm. Not vulnerable while grabbing.
Improved Hold: -5 circumstance penalty to escape from your holds.
Improved Initiative: +4 bonus to initiative checks per rank.
Improved Smash: No penalty for the smash action.
Improved Trip: No penalty for the trip action.
Improvised Weapon: Use Unarmed Combat skill with improvised weapons, +1 damage bonus.
Move-by Action: Move both before and after your standard action.
Power Attack: Trade attack bonus for effect bonus.
Precise Attack: Ignore attack check penalties for either cover or concealment.
Prone Fighting: No penalties for fighting while prone.
Quick Draw: Draw a weapon as a free action.
Ranged Attack: +1 bonus to ranged attack checks per rank.
Redirect: Use Deception to redirect a missed attack at another target.
Set-up: Transfer the benefit of an interaction skill to an ally.
Takedown: Free extra attack when you incapacitate a minion.
Throwing Mastery: +1 damage bonus with thrown weapons per rank.
Uncanny Dodge: Not vulnerable when surprised or caught off-guard.
Weapon Bind: Free disarm attempt when you actively defend.
Weapon Break: Free smash attack when you actively defend.
```


#### Domain Sketch
Favored Environment grants a situational +2 circumstance bonus to attack or defense when the character is operating in their designated environment.

- recognizes when the character is in their favored environment (air, underwater, space, extreme heat, jungle, etc.)
- requires the character to choose at the start of each round whether the +2 applies to attack checks or to both active defenses
- holds the chosen allocation fixed until the start of the character's next round
- applies passively while in the environment — no action required beyond the round-start allocation choice

Invariant: the +2 bonus is not affected by power level limits; the allocation choice must be made at round start and applies for the full round; the advantage has no effect outside the designated environment.

#### Decisions made (term level)
- Whether the system auto-detects the environment or requires a player declaration is an open context gap noted in the story map.
- Classified under Combat Advantage (not Skill Advantage) per the source's explicit COMBAT category label.
---

### Fortune Activation

Fortune Activation groups the advantages that use the hero point as their primary activation resource. Each advantage in this KA requires spending a hero point (or operates in the same hero-point economy) to produce a benefit for the character or their allies. The KA owns the interaction between the hero point resource and advantage activation: it defines what happens when a hero point is spent, when the benefit expires, and what restrictions apply. Fortune Activation interacts with the hero point boundary term (owned by Character Construction) but does not define how hero points are earned or reset. All Fortune Activation advantages are categorized as Fortune type. Luck is included here despite not requiring an explicit hero point spend because it mirrors the hero-point re-roll mechanic at a rank-limited rate and belongs to the Fortune type.

#### Decisions made
- Luck is included here despite not requiring a hero point spend: it mirrors the hero-point re-roll mechanic and belongs to the Fortune type; its rank cap (half PL) connects it to the same economy.
- Beginner's Luck, Inspire, and Leadership are standard hero-point-spend Fortune advantages; grouping with Luck is cohesive.
- No terms moved out of this module from the Fortune Activation KA.

#### Luck

- Luck is a ranked fortune advantage (maximum rank = half series power level, rounded down) that allows the character to re-roll a die once per round, including adding 10 to re-rolls of 10 or less.
- The character can use Luck a number of times per game session equal to their Luck rank.
- Luck functions like spending a hero point for a re-roll but does not actually cost a hero point.
- Luck ranks refresh when hero points reset at the start of an adventure.
- The GM may adjust the maximum rank limit depending on the series.

**Ref — Instant Up**
Source: context/rules/HeroesHandbook-rules__chunk_077.md
Locator: lines 4799-4851
Extract: whole

```source
### Instant Up
General
You can go from prone to standing as a free action without the need for an Acrobatics skill check.

INTERPOSE
General
Once per round, when an ally within range of your normal movement is hit by an attack, you can choose to place
yourself between the attacker and your ally as a reaction, making you the target of the attack instead. The attack
hits you rather than your ally, and you suffer the effects normally. You cannot use this advantage against area
effects or perception range attacks, only those requiring an attack check.

LUCK
FORTUNE, RANKED (1/2 PL)
Once per round, you can choose to re-roll a die roll, like spending a hero point, including adding 10 to re-rolls of
10 or less. You can do this a number of times per game session equal to your Luck rank, with a maximum rank of half
the series power level (rounded down). Your Luck ranks refresh when your hero points reset at the start of an adventure.
The GM may choose to set a different limit on ranks in this advantage, depending on the series.

MINION
GENERAL, RANKED
You have a follower or minion. This minion is an independent character with a power point total of (advantage rank x 15).
Minions are subject to the normal power level limits, and cannot have minions themselves. Your minions (if capable of
independent thought) automatically have a helpful attitude toward you. They are subject to the normal rules for minions.
Minions do not earn power points. Instead, you must spend earned power points to increase your rank in this advantage
to improve the minion's power point total and traits. Minions also do not have hero points. Any lost minions are replaced
in between adventures with other followers with similar abilities at the Gamemaster's discretion.
```

**Ref — Fortune Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_068.md
Locator: lines 4287-4336
Extract: whole

```source
### Fortune Advantages
ADVANTAGE  EFFECT
Beginner's Luck: Spend a hero point to gain 5 temporary ranks in a skill.
Inspire: Spend a hero point to grant allies a +1 circumstance bonus per rank.
Leadership: Spend a hero point to remove a condition from an ally.
Luck: Re-roll a die roll once per rank.
Seize Initiative: Spend a hero point to go first in the initiative order.
Ultimate Effort: Spend a hero point to get an effective 20 on a specific check.

### General Advantages
ADVANTAGE  EFFECT
Assessment: Use Insight to learn an opponent's combat capabilities.
Benefit: Gain a significant perquisite or fringe benefit.
Diehard: Automatically stabilize when dying.
Eidetic Memory: Total recall, +5 circumstance bonus to remember things.
Equipment: 5 points of equipment per rank.
Extraordinary Effort: Gain two benefits when using extra effort.
Fearless: Immune to fear effects.
Great Endurance: +5 on checks involving endurance.
Instant Up: Stand from prone as a free action.
Interpose: Take an attack meant for an ally.
Minion: Gain a follower or minion with (15 x rank) power points.
Second Chance: Re-roll a failed check against a hazard once.
Sidekick: Gain a sidekick with (5 x rank) power points.
Teamwork: +5 bonus to support team checks.
Trance: Go into a deathlike trance that slows bodily functions.
```


#### Domain Sketch
Luck provides a per-session pool of re-roll uses that function identically to hero point re-rolls but draw from a separate, rank-limited resource.

- tracks remaining uses for the session; each use consumes one rank from the pool (not a hero point)
- re-rolls one die roll once per round, adding 10 to any re-roll result of 10 or less — same mechanic as a hero point re-roll
- limits session uses to the character's current Luck rank — when the pool is empty, Luck cannot be used
- refreshes the full pool when hero points reset at the start of a new adventure

Invariant: maximum rank is half the series power level rounded down; cannot exceed once per round; pool is empty after rank uses that session; pool refreshes only at adventure start.

#### Decisions made (term level)
- Classified under Fortune Advantage despite not spending a hero point at use time: the re-roll mechanic is identical to a hero point re-roll and the source labels it FORTUNE.
- Luck's rank cap at half PL is the only power-level-derived rank cap in this module; character construction validation must enforce it.
#### Inspire

- Inspire is a ranked fortune advantage (maximum rank 5) that grants allies a circumstance bonus to all checks.
- Once per scene, the character spends a hero point and takes a standard action; allies who can interact with the character gain +1 per Inspire rank on all checks until the start of the character's next round.
- The maximum inspiration bonus is +5 (at rank 5); the character themselves does not receive the bonus.
- The inspiration bonus ignores power level limits, like other hero point uses.
- Multiple uses of Inspire do not stack; only the highest bonus applies.

**Ref — Improvised Tools**
Source: context/rules/HeroesHandbook-rules__chunk_076.md
Locator: lines 4749-4798
Extract: whole

```source
### Improvised Tools
SKILL
You ignore the circumstance penalty for using skills without proper tools, since you can improvise sufficient tools
with whatever is at hand. If you're forced to work without tools at all, you suffer only a -2 penalty.

### Improvised Weapon
COMBAT, RANKED
When wielding an improvised close combat weapon, you use your Close Combat: Unarmed skill bonus for attack checks
with the "weapon" rather than relying on your general Close Combat skill bonus. Additional ranks give you a +1 bonus
to Damage with improvised weapons per rank.

INSPIRE
FORTUNE, RANKED (5)
You can inspire your allies to greatness. Once per scene, by taking a standard action and spending a hero point,
allies able to interact with you gain a +1 circumstance bonus per Inspire rank on all checks until the start of your
next round, with a maximum bonus of +5. You do not gain the bonus, only your allies do. The inspiration bonus ignores
power level limits, like other uses of hero points. Multiple uses of Inspire do not stack, only the highest bonus applies.

JACK-OF-ALL-TRADES
SKILL
You can use any skill untrained, even skills or aspects of skills that normally cannot be used untrained, although you
must still have proper tools if the skill requires them.

LANGUAGES
SKILL, RANKED
You can speak and understand additional languages. With one rank in this advantage, you know an additional language.
For each additional rank, you double your additional known languages: two at rank 2, four at rank 3, eight at rank 4.

LEADERSHIP
FORTUNE
Your presence reassures and lends courage to your allies. As a standard action, you can spend a hero point to remove
one of the following conditions from an ally with whom you can interact: dazed, fatigued, or stunned.
```

**Ref — Fortune Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_068.md
Locator: lines 4287-4336
Extract: whole

```source
### Fortune Advantages
ADVANTAGE  EFFECT
Beginner's Luck: Spend a hero point to gain 5 temporary ranks in a skill.
Inspire: Spend a hero point to grant allies a +1 circumstance bonus per rank.
Leadership: Spend a hero point to remove a condition from an ally.
Luck: Re-roll a die roll once per rank.
Seize Initiative: Spend a hero point to go first in the initiative order.
Ultimate Effort: Spend a hero point to get an effective 20 on a specific check.

### General Advantages
ADVANTAGE  EFFECT
Assessment: Use Insight to learn an opponent's combat capabilities.
Benefit: Gain a significant perquisite or fringe benefit.
Diehard: Automatically stabilize when dying.
Eidetic Memory: Total recall, +5 circumstance bonus to remember things.
Equipment: 5 points of equipment per rank.
Extraordinary Effort: Gain two benefits when using extra effort.
Fearless: Immune to fear effects.
Great Endurance: +5 on checks involving endurance.
Instant Up: Stand from prone as a free action.
Interpose: Take an attack meant for an ally.
Minion: Gain a follower or minion with (15 x rank) power points.
Second Chance: Re-roll a failed check against a hazard once.
Sidekick: Gain a sidekick with (5 x rank) power points.
Teamwork: +5 bonus to support team checks.
Trance: Go into a deathlike trance that slows bodily functions.
```


#### Domain Sketch
Inspire translates a hero point and a moment of leadership into a temporary group-wide bonus that benefits all interacting allies.

- requires spending a hero point and taking a standard action to activate
- grants +1 per Inspire rank on all checks to all allies who can interact with the activating character, until start of that character's next round
- excludes the activating character — only allies receive the bonus
- enforces a maximum bonus of +5 (Inspire rank is capped at 5)

Invariant: bonus ignores power level limits; the activating character does not receive the bonus; multiple Inspire activations do not stack — only the highest applies; bonus expires at the start of the activating character's next round.

#### Decisions made (term level)
- "Allies who can interact" means within normal interaction range — the system determines who qualifies at activation time.
#### Leadership

- Leadership is a fortune advantage that allows the character to remove a condition from an ally.
- As a standard action, the character spends a hero point to remove one of the following conditions from an ally with whom they can interact: dazed, fatigued, or stunned.
- Leadership reflects the character's ability to reassure and lend courage, snapping allies out of debilitating conditions through presence and direction.

**Ref — Improvised Tools**
Source: context/rules/HeroesHandbook-rules__chunk_076.md
Locator: lines 4749-4798
Extract: whole

```source
### Improvised Tools
SKILL
You ignore the circumstance penalty for using skills without proper tools, since you can improvise sufficient tools
with whatever is at hand. If you're forced to work without tools at all, you suffer only a -2 penalty.

### Improvised Weapon
COMBAT, RANKED
When wielding an improvised close combat weapon, you use your Close Combat: Unarmed skill bonus for attack checks
with the "weapon" rather than relying on your general Close Combat skill bonus. Additional ranks give you a +1 bonus
to Damage with improvised weapons per rank.

INSPIRE
FORTUNE, RANKED (5)
You can inspire your allies to greatness. Once per scene, by taking a standard action and spending a hero point,
allies able to interact with you gain a +1 circumstance bonus per Inspire rank on all checks until the start of your
next round, with a maximum bonus of +5. You do not gain the bonus, only your allies do. The inspiration bonus ignores
power level limits, like other uses of hero points. Multiple uses of Inspire do not stack, only the highest bonus applies.

JACK-OF-ALL-TRADES
SKILL
You can use any skill untrained, even skills or aspects of skills that normally cannot be used untrained, although you
must still have proper tools if the skill requires them.

LANGUAGES
SKILL, RANKED
You can speak and understand additional languages. With one rank in this advantage, you know an additional language.
For each additional rank, you double your additional known languages: two at rank 2, four at rank 3, eight at rank 4.

LEADERSHIP
FORTUNE
Your presence reassures and lends courage to your allies. As a standard action, you can spend a hero point to remove
one of the following conditions from an ally with whom you can interact: dazed, fatigued, or stunned.
```

**Ref — Instant Up**
Source: context/rules/HeroesHandbook-rules__chunk_077.md
Locator: lines 4799-4851
Extract: whole

```source
### Instant Up
General
You can go from prone to standing as a free action without the need for an Acrobatics skill check.

INTERPOSE
General
Once per round, when an ally within range of your normal movement is hit by an attack, you can choose to place
yourself between the attacker and your ally as a reaction, making you the target of the attack instead. The attack
hits you rather than your ally, and you suffer the effects normally. You cannot use this advantage against area
effects or perception range attacks, only those requiring an attack check.

LUCK
FORTUNE, RANKED (1/2 PL)
Once per round, you can choose to re-roll a die roll, like spending a hero point, including adding 10 to re-rolls of
10 or less. You can do this a number of times per game session equal to your Luck rank, with a maximum rank of half
the series power level (rounded down). Your Luck ranks refresh when your hero points reset at the start of an adventure.
The GM may choose to set a different limit on ranks in this advantage, depending on the series.

MINION
GENERAL, RANKED
You have a follower or minion. This minion is an independent character with a power point total of (advantage rank x 15).
Minions are subject to the normal power level limits, and cannot have minions themselves. Your minions (if capable of
independent thought) automatically have a helpful attitude toward you. They are subject to the normal rules for minions.
Minions do not earn power points. Instead, you must spend earned power points to increase your rank in this advantage
to improve the minion's power point total and traits. Minions also do not have hero points. Any lost minions are replaced
in between adventures with other followers with similar abilities at the Gamemaster's discretion.
```

**Ref — Fortune Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_068.md
Locator: lines 4287-4336
Extract: whole

```source
### Fortune Advantages
ADVANTAGE  EFFECT
Beginner's Luck: Spend a hero point to gain 5 temporary ranks in a skill.
Inspire: Spend a hero point to grant allies a +1 circumstance bonus per rank.
Leadership: Spend a hero point to remove a condition from an ally.
Luck: Re-roll a die roll once per rank.
Seize Initiative: Spend a hero point to go first in the initiative order.
Ultimate Effort: Spend a hero point to get an effective 20 on a specific check.

### General Advantages
ADVANTAGE  EFFECT
Assessment: Use Insight to learn an opponent's combat capabilities.
Benefit: Gain a significant perquisite or fringe benefit.
Diehard: Automatically stabilize when dying.
Eidetic Memory: Total recall, +5 circumstance bonus to remember things.
Equipment: 5 points of equipment per rank.
Extraordinary Effort: Gain two benefits when using extra effort.
Fearless: Immune to fear effects.
Great Endurance: +5 on checks involving endurance.
Instant Up: Stand from prone as a free action.
Interpose: Take an attack meant for an ally.
Minion: Gain a follower or minion with (15 x rank) power points.
Second Chance: Re-roll a failed check against a hazard once.
Sidekick: Gain a sidekick with (5 x rank) power points.
Teamwork: +5 bonus to support team checks.
Trance: Go into a deathlike trance that slows bodily functions.
```


#### Domain Sketch
Leadership translates a hero point and a moment of commanding presence into removal of a debilitating condition from one ally.

- requires spending a hero point and taking a standard action to activate
- selects one ally within interaction range as the target
- removes exactly one of three eligible conditions from that ally: dazed, fatigued, or stunned

Invariant: only the three eligible conditions (dazed, fatigued, stunned) can be removed; the ally must be within interaction range; exactly one condition is removed per activation; no other conditions are eligible.

#### Decisions made (term level)
- Leadership requires no roll — spending the hero point and taking the standard action removes the condition immediately, per the source text.
#### Beginner's Luck

- Beginner's Luck is a fortune advantage that grants temporary skill ranks by spending a hero point.
- By spending a hero point, the character gains effective 5 ranks in one chosen skill they currently have at 4 or fewer ranks, including skills with no ranks or skills that normally cannot be used untrained.
- The temporary 5 ranks last for the duration of the scene and grant their normal benefits.
- The skill chosen can be any qualifying skill, giving unpracticed characters a brief surge of luck-based proficiency.

**Ref — Skill Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_069.md
Locator: lines 4337-4450
Extract: whole

```source
### Skill Advantages
ADVANTAGE  EFFECT
Agile Feint: Feint using Acrobatics skill or movement speed.
Animal Empathy: Use interaction skills normally with animals.
Artificer: Use Expertise: Magic to create temporary magical devices.
Attractive: Circumstance bonus to interaction based on your looks.
Connected: Call in assistance or favors with a Persuasion check.
Contacts: Make an initial Investigation check in one minute.
Daze: Use Deception or Intimidation to daze an opponent.
Fascinate: Use an interaction skill to entrance others.
Favored Foe: Circumstance bonus to checks against a type of opponent.
Hide in Plain Sight: Hide while observed without need for a diversion.
Improvised Tools: No penalty for using skills without tools.
Inventor: Use Technology to create temporary devices.
Jack-of-all-trades: Use any skill untrained.
Languages: Speak and understand additional languages.
Ritualist: Use Expertise: Magic to create and perform rituals.
Skill Mastery: Make routine checks with one skill under any conditions.
Startle: Use Intimidation to feint in combat.
Taunt: Use Deception to demoralize in combat.
Tracking: Use Perception to follow tracks.
Well-informed: Immediate Investigation or Persuasion check to know something.

BEGINNER'S LUCK
FORTUNE
By spending a hero point, you gain an effective 5 ranks in one skill of your choice you currently have at 4 or fewer
ranks, including skills you have no ranks in, even if they can't be used untrained. These temporary skill ranks last
for the duration of the scene and grant you their normal benefits.

BENEFIT
GENERAL, RANKED
You have some significant perquisite or fringe benefit. The exact nature of the benefit is for you and the Gamemaster
to determine. As a rule of thumb it should not exceed the benefits of any other advantage, or a power effect costing
1 point. It should also be significant enough to cost at least 1 power point. An example is Diplomatic Immunity.
A license to practice law or medicine should not be considered a Benefit; it's simply a part of having training in
the appropriate Expertise skill and has no significant game effect.
Benefits may come in ranks for improved levels of the same benefit. The GM is the final arbiter as to what does and
does not constitute a Benefit in the setting.

Sample Benefits:
- Alternate Identity: You have an alternate identity, complete with legal paperwork.
- Ambidexterity: You are equally adept using either hand, suffering no circumstance penalty for using your off-hand.
- Cipher: Your true history is well hidden. Investigation checks concerning you are made at a -5 circumstance penalty per rank.
- Diplomatic Immunity: By dint of your diplomatic status, you cannot be prosecuted for crimes in nations other than your own.
- Security Clearance: You have access to classified government information, installations, and possibly equipment and personnel.
- Status: By virtue of birth or achievement, you have special status (nobility, knighthood, aristocracy, etc.).
- Wealth: You have greater than average wealth (well-off rank 1 through billionaire rank 5).
```

**Ref — Fortune Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_068.md
Locator: lines 4287-4336
Extract: whole

```source
### Fortune Advantages
ADVANTAGE  EFFECT
Beginner's Luck: Spend a hero point to gain 5 temporary ranks in a skill.
Inspire: Spend a hero point to grant allies a +1 circumstance bonus per rank.
Leadership: Spend a hero point to remove a condition from an ally.
Luck: Re-roll a die roll once per rank.
Seize Initiative: Spend a hero point to go first in the initiative order.
Ultimate Effort: Spend a hero point to get an effective 20 on a specific check.

### General Advantages
ADVANTAGE  EFFECT
Assessment: Use Insight to learn an opponent's combat capabilities.
Benefit: Gain a significant perquisite or fringe benefit.
Diehard: Automatically stabilize when dying.
Eidetic Memory: Total recall, +5 circumstance bonus to remember things.
Equipment: 5 points of equipment per rank.
Extraordinary Effort: Gain two benefits when using extra effort.
Fearless: Immune to fear effects.
Great Endurance: +5 on checks involving endurance.
Instant Up: Stand from prone as a free action.
Interpose: Take an attack meant for an ally.
Minion: Gain a follower or minion with (15 x rank) power points.
Second Chance: Re-roll a failed check against a hazard once.
Sidekick: Gain a sidekick with (5 x rank) power points.
Teamwork: +5 bonus to support team checks.
Trance: Go into a deathlike trance that slows bodily functions.
```


#### Domain Sketch
Beginner's Luck converts a hero point into a burst of luck-based proficiency, granting effective skill ranks for one scene.

- requires spending a hero point to activate; no additional action cost beyond the hero point spend
- selects one skill the character currently has at 4 or fewer ranks (including skills with 0 ranks and normally untrained-restricted skills)
- grants effective rank 5 in that skill for the duration of the current scene
- expires at the end of the scene — temporary ranks do not carry over

Invariant: applies only to skills currently at 4 or fewer ranks; grants exactly effective rank 5 (not +5 to existing rank); lasts exactly for the scene; expires when the scene ends.

#### Decisions made (term level)
- Classified under Fortune Advantage (FORTUNE) per the source's explicit label, not Skill Advantage, despite the effect granting temporary skill ranks.
---

### Character Resource

A Character Resource is a general advantage that grants the character access to an external asset that exists outside the character's own body but is owned and managed by them. Equipment grants 5 gear points per rank to spend on weapons, armor, vehicles, and headquarters. Minion grants an independent follower with (rank x 15) power points. Sidekick grants a full NPC partner with (rank x 5) power points. Benefit grants a contextual fringe benefit of agreed narrative and mechanical significance. This KA owns the rule that resources are funded by power points and ranks, that they do not earn points autonomously, and that they can be lost, destroyed, or superseded. Character Resources must never duplicate effects purchasable as individual powers at equivalent point cost; they represent access to things, not innate abilities.

#### Decisions made
- Equipment, Minion, Sidekick, and Benefit are grouped because all four grant access to an entity or resource external to the character's own traits, funded by power points.
- Benefit is placed here rather than standalone: it passes the independence test but is more a parameterized perquisite than a distinct domain concept; grouping with other resource advantages is correct.
- No terms moved out of this module from the Character Resource KA.
- Open question: whether the online tool tracks equipment point spending within the Equipment advantage or delegates to a separate gear management flow.

#### Equipment

- Equipment is a ranked general advantage that grants 5 equipment points per rank to spend on weapons, armor, vehicles, headquarters, and other gear.
- Equipment points purchase gear as defined in the Gadgets & Gear chapter.
- Many heroes rely on Equipment in combination with skills and other advantages as their primary source of power.
- Equipment is not a power; it is subject to the physical world (it can be lost, stolen, or destroyed).

**Ref — Defensive Attack**
Source: context/rules/HeroesHandbook-rules__chunk_071.md
Locator: lines 4495-4547
Extract: whole

```source
### Defensive Attack
COMBAT
When you make a defensive attack (see Maneuvers, page 249), you can take a penalty of up to -5 on your attack
bonus and add the same number (up to +5) to both your active defenses (Dodge and Parry).

### Defensive Roll
COMBAT, RANKED
You can avoid damage through agility and "rolling" with an attack. You receive a bonus to your Toughness equal
to your advantage rank, but it is considered an active defense similar to Dodge and Parry, so you lose this bonus
whenever you are vulnerable or defenseless. Your total Toughness, including this advantage, is still limited by power level.

DIEHARD
General
When your condition becomes dying you automatically stabilize on the following round without any need for a
Fortitude check, although further damage can still kill you.

EQUIPMENT
GENERAL, RANKED
You have 5 points per rank in this advantage to spend on equipment. This includes vehicles and headquarters. See
the Gadgets & Gear chapter for details on equipment and its costs. Many heroes rely almost solely on Equipment
in conjunction with their skills and other advantages.

EVASION
COMBAT, RANKED (2)
You have a +2 circumstance bonus to Dodge resistance checks to avoid area effects. If you have 2 ranks in this
advantage, your circumstance bonus increases to +5.
```

**Ref — Fortune Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_068.md
Locator: lines 4287-4336
Extract: whole

```source
### Fortune Advantages
ADVANTAGE  EFFECT
Beginner's Luck: Spend a hero point to gain 5 temporary ranks in a skill.
Inspire: Spend a hero point to grant allies a +1 circumstance bonus per rank.
Leadership: Spend a hero point to remove a condition from an ally.
Luck: Re-roll a die roll once per rank.
Seize Initiative: Spend a hero point to go first in the initiative order.
Ultimate Effort: Spend a hero point to get an effective 20 on a specific check.

### General Advantages
ADVANTAGE  EFFECT
Assessment: Use Insight to learn an opponent's combat capabilities.
Benefit: Gain a significant perquisite or fringe benefit.
Diehard: Automatically stabilize when dying.
Eidetic Memory: Total recall, +5 circumstance bonus to remember things.
Equipment: 5 points of equipment per rank.
Extraordinary Effort: Gain two benefits when using extra effort.
Fearless: Immune to fear effects.
Great Endurance: +5 on checks involving endurance.
Instant Up: Stand from prone as a free action.
Interpose: Take an attack meant for an ally.
Minion: Gain a follower or minion with (15 x rank) power points.
Second Chance: Re-roll a failed check against a hazard once.
Sidekick: Gain a sidekick with (5 x rank) power points.
Teamwork: +5 bonus to support team checks.
Trance: Go into a deathlike trance that slows bodily functions.
```


#### Domain Sketch
Equipment converts advantage rank into a budget of equipment points used to purchase physical gear from the Gadgets & Gear chapter.

- grants 5 equipment points per rank, accumulating linearly across ranks (rank 3 = 15 equipment points)
- allocates those points to weapons, armor, vehicles, headquarters, and other gear as defined by equipment rules
- treats all purchased gear as physical objects subject to the rules of the physical world — equipment can be lost, stolen, or destroyed
- does not interact with power level limits — equipment is not a power effect

Invariant: equipment points are always 5 per rank; equipment is always subject to loss/theft/destruction; Equipment is never treated as a power effect.

#### Decisions made (term level)
- Equipment is a resource-granting advantage: it converts rank to points that purchase gear through equipment chapter rules. The gear carries game-mechanical effect, not the advantage directly.
#### Minion

- Minion is a ranked general advantage that grants the character a follower with a power point total of (rank x 15).
- Minions are independent characters subject to normal power level limits; they cannot have minions of their own.
- Minions capable of independent thought are automatically helpful toward their owner; they follow normal minion rules (page 245).
- Minions do not earn power points independently; the character must spend earned power points to increase Minion rank and improve the minion's point total and traits.
- Lost minions are replaced between adventures at the Gamemaster's discretion.
- Minions do not have hero points.

**Ref — Instant Up**
Source: context/rules/HeroesHandbook-rules__chunk_077.md
Locator: lines 4799-4851
Extract: whole

```source
### Instant Up
General
You can go from prone to standing as a free action without the need for an Acrobatics skill check.

INTERPOSE
General
Once per round, when an ally within range of your normal movement is hit by an attack, you can choose to place
yourself between the attacker and your ally as a reaction, making you the target of the attack instead. The attack
hits you rather than your ally, and you suffer the effects normally. You cannot use this advantage against area
effects or perception range attacks, only those requiring an attack check.

LUCK
FORTUNE, RANKED (1/2 PL)
Once per round, you can choose to re-roll a die roll, like spending a hero point, including adding 10 to re-rolls of
10 or less. You can do this a number of times per game session equal to your Luck rank, with a maximum rank of half
the series power level (rounded down). Your Luck ranks refresh when your hero points reset at the start of an adventure.
The GM may choose to set a different limit on ranks in this advantage, depending on the series.

MINION
GENERAL, RANKED
You have a follower or minion. This minion is an independent character with a power point total of (advantage rank x 15).
Minions are subject to the normal power level limits, and cannot have minions themselves. Your minions (if capable of
independent thought) automatically have a helpful attitude toward you. They are subject to the normal rules for minions.
Minions do not earn power points. Instead, you must spend earned power points to increase your rank in this advantage
to improve the minion's power point total and traits. Minions also do not have hero points. Any lost minions are replaced
in between adventures with other followers with similar abilities at the Gamemaster's discretion.
```

**Ref — Fortune Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_068.md
Locator: lines 4287-4336
Extract: whole

```source
### Fortune Advantages
ADVANTAGE  EFFECT
Beginner's Luck: Spend a hero point to gain 5 temporary ranks in a skill.
Inspire: Spend a hero point to grant allies a +1 circumstance bonus per rank.
Leadership: Spend a hero point to remove a condition from an ally.
Luck: Re-roll a die roll once per rank.
Seize Initiative: Spend a hero point to go first in the initiative order.
Ultimate Effort: Spend a hero point to get an effective 20 on a specific check.

### General Advantages
ADVANTAGE  EFFECT
Assessment: Use Insight to learn an opponent's combat capabilities.
Benefit: Gain a significant perquisite or fringe benefit.
Diehard: Automatically stabilize when dying.
Eidetic Memory: Total recall, +5 circumstance bonus to remember things.
Equipment: 5 points of equipment per rank.
Extraordinary Effort: Gain two benefits when using extra effort.
Fearless: Immune to fear effects.
Great Endurance: +5 on checks involving endurance.
Instant Up: Stand from prone as a free action.
Interpose: Take an attack meant for an ally.
Minion: Gain a follower or minion with (15 x rank) power points.
Second Chance: Re-roll a failed check against a hazard once.
Sidekick: Gain a sidekick with (5 x rank) power points.
Teamwork: +5 bonus to support team checks.
Trance: Go into a deathlike trance that slows bodily functions.
```


#### Domain Sketch
Minion grants the character a follower — an independent character built on a power point budget derived from the advantage rank.

- builds the minion with a power point total of exactly (rank × 15) subject to normal series power level limits
- prevents the minion from having minions of its own
- grants the minion an automatically helpful attitude toward its owner when the minion is capable of independent thought
- requires the character to spend earned power points to increase Minion rank and improve the minion's point total and traits
- replaces a lost minion between adventures at the Gamemaster's discretion — not in-scene

Invariant: minion point total is always exactly rank × 15; minion never has hero points; minion cannot have its own minions; lost minions are replaced between adventures only.

#### Decisions made (term level)
- Kept distinct from Sidekick: Minion grants rank × 15 points, follows minion rules, has no hero points. Sidekick grants rank × 5 points, is a full character, can receive hero points from owner.
#### Sidekick

- Sidekick is a ranked general advantage that grants the character a partner/aide built with (rank x 5) power points, subject to series power level.
- A sidekick's power point total must be less than the character's own total.
- Sidekicks are NPCs but are automatically helpful and loyal; the GM normally allows the player to control their sidekick.
- Sidekicks are not minions: they are full-fledged characters not subject to minion rules.
- Sidekicks do not earn power points; the character spends earned points to increase Sidekick rank, granting 5 additional power points per rank increase.
- The character can spend hero points on the sidekick's behalf with the usual benefits; sidekicks themselves do not have hero points.

**Ref — Second Chance**
Source: context/rules/HeroesHandbook-rules__chunk_079.md
Locator: lines 4909-4972
Extract: whole

```source
### Second Chance
GENERAL, RANKED
Choose a particular hazard, such as falling, being tripped, triggering traps, mind control or a particular skill with
consequences for failure. If you fail a check against that hazard, you can make another immediately and use the better
of the two results. You only get one second chance for any given check, and the GM decides if a particular hazard or
skill is an appropriate focus for this advantage. You can take this advantage multiple times, each for a different hazard.

### Seize Initiative
FORTUNE
You can spend a hero point to automatically go first in the initiative order. You may only do so at the start of combat,
when you would normally make your initiative check. If more than one character uses this advantage, they all make
initiative checks normally and act in order of their initiative result, followed by all other characters.

SIDEKICK
GENERAL, RANKED
You have another character serving as your partner and aide. Create your sidekick as an independent character with
(advantage rank x 5) power points, and subject to the series power level. A sidekick's power point total must be less
than yours. Your sidekick is an NPC, but automatically helpful and loyal to you. Gamemasters should generally allow you
to control your sidekick, although sidekicks remain NPCs and the GM has final say in their actions.
Sidekicks do not earn power points. Instead, you must spend earned power points to increase your rank in Sidekick to
improve the sidekick's power point total and traits; each point you spend to increase your rank in Sidekick grants the
sidekick 5 additional power points. Sidekicks also do not have hero points, but you can spend your own hero points on
the sidekick's behalf with the usual benefits. Sidekicks are not minions, but full-fledged characters, so they are not
subject to the minion rules.
```

**Ref — Fortune Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_068.md
Locator: lines 4287-4336
Extract: whole

```source
### Fortune Advantages
ADVANTAGE  EFFECT
Beginner's Luck: Spend a hero point to gain 5 temporary ranks in a skill.
Inspire: Spend a hero point to grant allies a +1 circumstance bonus per rank.
Leadership: Spend a hero point to remove a condition from an ally.
Luck: Re-roll a die roll once per rank.
Seize Initiative: Spend a hero point to go first in the initiative order.
Ultimate Effort: Spend a hero point to get an effective 20 on a specific check.

### General Advantages
ADVANTAGE  EFFECT
Assessment: Use Insight to learn an opponent's combat capabilities.
Benefit: Gain a significant perquisite or fringe benefit.
Diehard: Automatically stabilize when dying.
Eidetic Memory: Total recall, +5 circumstance bonus to remember things.
Equipment: 5 points of equipment per rank.
Extraordinary Effort: Gain two benefits when using extra effort.
Fearless: Immune to fear effects.
Great Endurance: +5 on checks involving endurance.
Instant Up: Stand from prone as a free action.
Interpose: Take an attack meant for an ally.
Minion: Gain a follower or minion with (15 x rank) power points.
Second Chance: Re-roll a failed check against a hazard once.
Sidekick: Gain a sidekick with (5 x rank) power points.
Teamwork: +5 bonus to support team checks.
Trance: Go into a deathlike trance that slows bodily functions.
```


#### Domain Sketch
Sidekick grants the character a loyal partner built on a smaller power point budget, treated as a full-fledged character rather than a minion.

- builds the sidekick with a power point total of exactly (rank × 5), subject to series power level
- requires the sidekick's total power points to always remain less than the character's own total
- allows the character to spend hero points on the sidekick's behalf with normal hero point benefits
- requires the character to spend earned power points to increase Sidekick rank, adding 5 power points per rank increase
- does not apply minion rules to the sidekick — the sidekick is a full character under shared GM/player control

Invariant: sidekick total must always be less than owner's total; sidekick has no hero points of its own; sidekick is never subject to minion rules; hero points spent on the sidekick's behalf come from the owner's pool.

#### Decisions made (term level)
- Distinct from Minion: Sidekick costs fewer points per rank (5 vs. 15) but the sidekick is a full character, not a minion-rule follower. Owner can proxy hero points to the sidekick.
#### Benefit

- Benefit is a ranked general advantage representing a significant perquisite or fringe benefit agreed between the player and the GM.
- The benefit should not exceed the value of any other advantage or a power effect costing 1 point; it must be significant enough to justify at least 1 power point.
- Sample benefits include: Alternate Identity, Ambidexterity, Cipher, Diplomatic Immunity, Security Clearance, Status, and Wealth.
- Benefits can be taken in ranks for improved levels of the same benefit.
- Routine professional credentials (e.g., law or medicine licenses) do not qualify; they are considered training and have no significant game effect.
- The GM is the final arbiter of what constitutes a Benefit in the series.

**Ref — Skill Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_069.md
Locator: lines 4337-4450
Extract: whole

```source
### Skill Advantages
ADVANTAGE  EFFECT
Agile Feint: Feint using Acrobatics skill or movement speed.
Animal Empathy: Use interaction skills normally with animals.
Artificer: Use Expertise: Magic to create temporary magical devices.
Attractive: Circumstance bonus to interaction based on your looks.
Connected: Call in assistance or favors with a Persuasion check.
Contacts: Make an initial Investigation check in one minute.
Daze: Use Deception or Intimidation to daze an opponent.
Fascinate: Use an interaction skill to entrance others.
Favored Foe: Circumstance bonus to checks against a type of opponent.
Hide in Plain Sight: Hide while observed without need for a diversion.
Improvised Tools: No penalty for using skills without tools.
Inventor: Use Technology to create temporary devices.
Jack-of-all-trades: Use any skill untrained.
Languages: Speak and understand additional languages.
Ritualist: Use Expertise: Magic to create and perform rituals.
Skill Mastery: Make routine checks with one skill under any conditions.
Startle: Use Intimidation to feint in combat.
Taunt: Use Deception to demoralize in combat.
Tracking: Use Perception to follow tracks.
Well-informed: Immediate Investigation or Persuasion check to know something.

BEGINNER'S LUCK
FORTUNE
By spending a hero point, you gain an effective 5 ranks in one skill of your choice you currently have at 4 or fewer
ranks, including skills you have no ranks in, even if they can't be used untrained. These temporary skill ranks last
for the duration of the scene and grant you their normal benefits.

BENEFIT
GENERAL, RANKED
You have some significant perquisite or fringe benefit. The exact nature of the benefit is for you and the Gamemaster
to determine. As a rule of thumb it should not exceed the benefits of any other advantage, or a power effect costing
1 point. It should also be significant enough to cost at least 1 power point. An example is Diplomatic Immunity.
A license to practice law or medicine should not be considered a Benefit; it's simply a part of having training in
the appropriate Expertise skill and has no significant game effect.
Benefits may come in ranks for improved levels of the same benefit. The GM is the final arbiter as to what does and
does not constitute a Benefit in the setting.

Sample Benefits:
- Alternate Identity: You have an alternate identity, complete with legal paperwork.
- Ambidexterity: You are equally adept using either hand, suffering no circumstance penalty for using your off-hand.
- Cipher: Your true history is well hidden. Investigation checks concerning you are made at a -5 circumstance penalty per rank.
- Diplomatic Immunity: By dint of your diplomatic status, you cannot be prosecuted for crimes in nations other than your own.
- Security Clearance: You have access to classified government information, installations, and possibly equipment and personnel.
- Status: By virtue of birth or achievement, you have special status (nobility, knighthood, aristocracy, etc.).
- Wealth: You have greater than average wealth (well-off rank 1 through billionaire rank 5).
```

**Ref — Fortune Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_068.md
Locator: lines 4287-4336
Extract: whole

```source
### Fortune Advantages
ADVANTAGE  EFFECT
Beginner's Luck: Spend a hero point to gain 5 temporary ranks in a skill.
Inspire: Spend a hero point to grant allies a +1 circumstance bonus per rank.
Leadership: Spend a hero point to remove a condition from an ally.
Luck: Re-roll a die roll once per rank.
Seize Initiative: Spend a hero point to go first in the initiative order.
Ultimate Effort: Spend a hero point to get an effective 20 on a specific check.

### General Advantages
ADVANTAGE  EFFECT
Assessment: Use Insight to learn an opponent's combat capabilities.
Benefit: Gain a significant perquisite or fringe benefit.
Diehard: Automatically stabilize when dying.
Eidetic Memory: Total recall, +5 circumstance bonus to remember things.
Equipment: 5 points of equipment per rank.
Extraordinary Effort: Gain two benefits when using extra effort.
Fearless: Immune to fear effects.
Great Endurance: +5 on checks involving endurance.
Instant Up: Stand from prone as a free action.
Interpose: Take an attack meant for an ally.
Minion: Gain a follower or minion with (15 x rank) power points.
Second Chance: Re-roll a failed check against a hazard once.
Sidekick: Gain a sidekick with (5 x rank) power points.
Teamwork: +5 bonus to support team checks.
Trance: Go into a deathlike trance that slows bodily functions.
```


#### Domain Sketch
Benefit defines a narrative perquisite or fringe benefit cooperatively agreed between the player and GM, purchased with power points.

- negotiates the specific benefit with the GM before finalizing — both sides must agree on what the benefit represents
- validates that the benefit does not exceed the value of any other advantage or a 1-point power effect
- validates that the benefit is significant enough to justify at least 1 power point cost
- allows multiple ranks for escalating versions of the same benefit
- rejects routine professional credentials — a law or medicine license has no significant game effect and never qualifies

Invariant: GM has final approval authority; benefit value ceiling is any other advantage or a 1-point power effect; routine credentials never qualify.

#### Decisions made (term level)
- Benefit is intentionally open-ended: the source delegates definition to GM/player negotiation. The system must provide a free-text field for benefit description and track GM approval status.
---

### Skill Enhancement

A Skill Enhancement is a skill advantage that modifies the scope, reliability, or reach of a character's skill use without being tied to a specific single skill instance. Skill Mastery makes one chosen skill reliable under pressure. Jack-of-all-trades makes every skill accessible without training (while still requiring tools). Favored Foe applies a +2 circumstance bonus across four skill checks when facing a specific opponent type. All three are classified as Skill advantages and interact with the Skill module's check system, but they do not define the skills themselves. Skill Enhancement advantages are not power-level-capped. Each must operate on a defined scope: one chosen skill (Skill Mastery), all skills universally (Jack-of-all-trades), or all checks against a specific foe type (Favored Foe).

#### Decisions made
- Skill Mastery, Jack-of-all-trades, and Favored Foe are grouped because all three modify the scope or conditions of skill use rather than granting a combat bonus or fortune effect.
- Favored Foe is placed in Skill Enhancement rather than Combat Enhancement because its bonus applies across four skill checks and is classified as a SKILL advantage; its applicability in combat is incidental.
- No terms moved out of this module from the Skill Enhancement KA.

#### Skill Mastery

- Skill Mastery is a skill advantage that allows the character to make routine checks with one chosen skill even under pressure.
- Normally, routine checks cannot be made under pressure; Skill Mastery removes that restriction for the chosen skill.
- Skill Mastery does not allow routine checks with skills that categorically do not permit routine checks regardless of conditions.
- The advantage may be taken multiple times, each time applying to a different skill.

**Ref — Skill Mastery**
Source: context/rules/HeroesHandbook-rules__chunk_080.md
Locator: lines 4973-5016
Extract: whole

```source
### Skill Mastery
SKILL
Choose a skill. You can make routine checks with that skill even when under pressure (see Routine Checks in The Basics
chapter). This advantage does not allow you to make routine checks with skills that do not normally allow you to do so.
You can take this advantage multiple times for different skills.

STARTLE
SKILL
You can use Intimidation rather than Deception to feint in combat. Targets resist with Insight, Intimidation, or Will defense.

TAKEDOWN
COMBAT, RANKED (2)
If you render a minion incapacitated with an attack, you get an immediate extra attack as a free action against another
minion within range and adjacent to the previous target's location. The extra attack is with the same attack and bonus
as the first. You can continue using this advantage until you miss or there are no more minions within range.

TAUNT
SKILL
You can demoralize an opponent with Deception rather than Intimidation, disparaging and undermining confidence rather
than threatening. Targets resist using Deception, Insight, or Will defense.

TEAMWORK
General
You're effective at helping out your friends. When you support a team check you have a +5 circumstance bonus to your
check. This bonus also applies to the Aid action and Team Attacks.
```

**Ref — Skill Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_069.md
Locator: lines 4337-4450
Extract: whole

```source
### Skill Advantages
ADVANTAGE  EFFECT
Agile Feint: Feint using Acrobatics skill or movement speed.
Animal Empathy: Use interaction skills normally with animals.
Artificer: Use Expertise: Magic to create temporary magical devices.
Attractive: Circumstance bonus to interaction based on your looks.
Connected: Call in assistance or favors with a Persuasion check.
Contacts: Make an initial Investigation check in one minute.
Daze: Use Deception or Intimidation to daze an opponent.
Fascinate: Use an interaction skill to entrance others.
Favored Foe: Circumstance bonus to checks against a type of opponent.
Hide in Plain Sight: Hide while observed without need for a diversion.
Improvised Tools: No penalty for using skills without tools.
Inventor: Use Technology to create temporary devices.
Jack-of-all-trades: Use any skill untrained.
Languages: Speak and understand additional languages.
Ritualist: Use Expertise: Magic to create and perform rituals.
Skill Mastery: Make routine checks with one skill under any conditions.
Startle: Use Intimidation to feint in combat.
Taunt: Use Deception to demoralize in combat.
Tracking: Use Perception to follow tracks.
Well-informed: Immediate Investigation or Persuasion check to know something.

BEGINNER'S LUCK
FORTUNE
By spending a hero point, you gain an effective 5 ranks in one skill of your choice you currently have at 4 or fewer
ranks, including skills you have no ranks in, even if they can't be used untrained. These temporary skill ranks last
for the duration of the scene and grant you their normal benefits.

BENEFIT
GENERAL, RANKED
You have some significant perquisite or fringe benefit. The exact nature of the benefit is for you and the Gamemaster
to determine. As a rule of thumb it should not exceed the benefits of any other advantage, or a power effect costing
1 point. It should also be significant enough to cost at least 1 power point. An example is Diplomatic Immunity.
A license to practice law or medicine should not be considered a Benefit; it's simply a part of having training in
the appropriate Expertise skill and has no significant game effect.
Benefits may come in ranks for improved levels of the same benefit. The GM is the final arbiter as to what does and
does not constitute a Benefit in the setting.

Sample Benefits:
- Alternate Identity: You have an alternate identity, complete with legal paperwork.
- Ambidexterity: You are equally adept using either hand, suffering no circumstance penalty for using your off-hand.
- Cipher: Your true history is well hidden. Investigation checks concerning you are made at a -5 circumstance penalty per rank.
- Diplomatic Immunity: By dint of your diplomatic status, you cannot be prosecuted for crimes in nations other than your own.
- Security Clearance: You have access to classified government information, installations, and possibly equipment and personnel.
- Status: By virtue of birth or achievement, you have special status (nobility, knighthood, aristocracy, etc.).
- Wealth: You have greater than average wealth (well-off rank 1 through billionaire rank 5).
```


#### Domain Sketch
Skill Mastery removes the pressure restriction for one designated skill, allowing routine checks even under stressful conditions.

- removes the restriction that routine checks cannot be made under pressure, but only for the designated skill
- records the chosen skill at acquisition — each instance applies to a different skill
- does not enable routine checks for skills that categorically prohibit routine checks regardless of conditions
- can be acquired multiple times, each time selecting a different qualifying skill

Invariant: applies only to the specifically designated skill; does not override categorical prohibitions on routine checks; designated skill is fixed at acquisition.

#### Decisions made (term level)
- Skill Mastery is an advantage (not a skill upgrade) because it modifies the conditions under which a skill operates rather than increasing its rank.
#### Jack of all Trades

- Jack-of-all-trades is a skill advantage that allows the character to use any skill untrained, including skills and aspects of skills that normally cannot be used without training.
- The character must still have proper tools if a skill requires them; Jack-of-all-trades removes the training barrier only, not the tool requirement.
- This advantage is broadly applicable across all skill domains, making the character a versatile generalist.

**Ref — Improvised Tools**
Source: context/rules/HeroesHandbook-rules__chunk_076.md
Locator: lines 4749-4798
Extract: whole

```source
### Improvised Tools
SKILL
You ignore the circumstance penalty for using skills without proper tools, since you can improvise sufficient tools
with whatever is at hand. If you're forced to work without tools at all, you suffer only a -2 penalty.

### Improvised Weapon
COMBAT, RANKED
When wielding an improvised close combat weapon, you use your Close Combat: Unarmed skill bonus for attack checks
with the "weapon" rather than relying on your general Close Combat skill bonus. Additional ranks give you a +1 bonus
to Damage with improvised weapons per rank.

INSPIRE
FORTUNE, RANKED (5)
You can inspire your allies to greatness. Once per scene, by taking a standard action and spending a hero point,
allies able to interact with you gain a +1 circumstance bonus per Inspire rank on all checks until the start of your
next round, with a maximum bonus of +5. You do not gain the bonus, only your allies do. The inspiration bonus ignores
power level limits, like other uses of hero points. Multiple uses of Inspire do not stack, only the highest bonus applies.

JACK-OF-ALL-TRADES
SKILL
You can use any skill untrained, even skills or aspects of skills that normally cannot be used untrained, although you
must still have proper tools if the skill requires them.

LANGUAGES
SKILL, RANKED
You can speak and understand additional languages. With one rank in this advantage, you know an additional language.
For each additional rank, you double your additional known languages: two at rank 2, four at rank 3, eight at rank 4.

LEADERSHIP
FORTUNE
Your presence reassures and lends courage to your allies. As a standard action, you can spend a hero point to remove
one of the following conditions from an ally with whom you can interact: dazed, fatigued, or stunned.
```

**Ref — Skill Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_069.md
Locator: lines 4337-4450
Extract: whole

```source
### Skill Advantages
ADVANTAGE  EFFECT
Agile Feint: Feint using Acrobatics skill or movement speed.
Animal Empathy: Use interaction skills normally with animals.
Artificer: Use Expertise: Magic to create temporary magical devices.
Attractive: Circumstance bonus to interaction based on your looks.
Connected: Call in assistance or favors with a Persuasion check.
Contacts: Make an initial Investigation check in one minute.
Daze: Use Deception or Intimidation to daze an opponent.
Fascinate: Use an interaction skill to entrance others.
Favored Foe: Circumstance bonus to checks against a type of opponent.
Hide in Plain Sight: Hide while observed without need for a diversion.
Improvised Tools: No penalty for using skills without tools.
Inventor: Use Technology to create temporary devices.
Jack-of-all-trades: Use any skill untrained.
Languages: Speak and understand additional languages.
Ritualist: Use Expertise: Magic to create and perform rituals.
Skill Mastery: Make routine checks with one skill under any conditions.
Startle: Use Intimidation to feint in combat.
Taunt: Use Deception to demoralize in combat.
Tracking: Use Perception to follow tracks.
Well-informed: Immediate Investigation or Persuasion check to know something.

BEGINNER'S LUCK
FORTUNE
By spending a hero point, you gain an effective 5 ranks in one skill of your choice you currently have at 4 or fewer
ranks, including skills you have no ranks in, even if they can't be used untrained. These temporary skill ranks last
for the duration of the scene and grant you their normal benefits.

BENEFIT
GENERAL, RANKED
You have some significant perquisite or fringe benefit. The exact nature of the benefit is for you and the Gamemaster
to determine. As a rule of thumb it should not exceed the benefits of any other advantage, or a power effect costing
1 point. It should also be significant enough to cost at least 1 power point. An example is Diplomatic Immunity.
A license to practice law or medicine should not be considered a Benefit; it's simply a part of having training in
the appropriate Expertise skill and has no significant game effect.
Benefits may come in ranks for improved levels of the same benefit. The GM is the final arbiter as to what does and
does not constitute a Benefit in the setting.

Sample Benefits:
- Alternate Identity: You have an alternate identity, complete with legal paperwork.
- Ambidexterity: You are equally adept using either hand, suffering no circumstance penalty for using your off-hand.
- Cipher: Your true history is well hidden. Investigation checks concerning you are made at a -5 circumstance penalty per rank.
- Diplomatic Immunity: By dint of your diplomatic status, you cannot be prosecuted for crimes in nations other than your own.
- Security Clearance: You have access to classified government information, installations, and possibly equipment and personnel.
- Status: By virtue of birth or achievement, you have special status (nobility, knighthood, aristocracy, etc.).
- Wealth: You have greater than average wealth (well-off rank 1 through billionaire rank 5).
```


#### Domain Sketch
Jack-of-all-trades removes the trained restriction for all skills simultaneously, making the character a universal generalist without eliminating tool requirements.

- removes the restriction that certain skills or skill aspects require training before they can be used
- maintains tool requirements — if a skill requires tools, those tools are still needed even with this advantage
- applies passively and globally — no per-skill or per-check activation required

Invariant: tool requirements still apply and are never waived by this advantage; training restriction is fully removed for all skills; no activation is required.

#### Decisions made (term level)
- Distinct from Skill Mastery: Jack-of-all-trades removes training barriers globally; Skill Mastery removes pressure restrictions for one specific skill.
#### Favored Foe

- Favored Foe is a skill advantage granting +2 circumstance bonus to Deception, Intimidation, Insight, and Perception checks against a specific type of opponent.
- The opponent type is specified when the advantage is acquired and can be a creature type (aliens, animals, undead, etc.) or a profession (soldiers, Yakuza, etc.) approved by the GM.
- Broad categories such as "humans" or "villains" are not permitted as favored foes.
- The +2 circumstance bonus from Favored Foe is not limited by power level.

**Ref — Fast Grab**
Source: context/rules/HeroesHandbook-rules__chunk_073.md
Locator: lines 4614-4658
Extract: whole

```source
### Fast Grab
COMBAT
When you hit with an unarmed attack you can immediately make a grab check against that opponent as a free action.
Your unarmed attack inflicts its normal damage and counts as the initial attack check required to grab your opponent.

### Favored Environment
COMBAT
You have an environment you're especially suited for fighting in. Examples include in the air, underwater, in space,
in extreme heat or cold, in jungles or woodlands, and so forth. While you are in your favored environment, you gain a
+2 circumstance bonus to attack checks or your active defenses. Choose at the start of the round whether the bonus
applies to attack or defense. The choice remains until the start of your next round. This circumstance bonus is not
affected by power level.

### Favored Foe
SKILL
You have a particular type of opponent you've studied or are especially effective against. It may be a type of creature
(aliens, animals, constructs, mutants, undead, etc.), a profession (soldiers, police officers, Yakuza, etc.) or any
other category the GM approves. Especially broad categories like "humans" or "villains" are not permitted. You gain a
+2 circumstance bonus on Deception, Intimidation, Insight, and Perception checks dealing with your Favored Foe. This
circumstance bonus is not limited by power level.

FEARLESS
General
You are immune to fear effects of all sorts, essentially the same as an Immunity to Fear effect.
```

**Ref — Skill Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_069.md
Locator: lines 4337-4450
Extract: whole

```source
### Skill Advantages
ADVANTAGE  EFFECT
Agile Feint: Feint using Acrobatics skill or movement speed.
Animal Empathy: Use interaction skills normally with animals.
Artificer: Use Expertise: Magic to create temporary magical devices.
Attractive: Circumstance bonus to interaction based on your looks.
Connected: Call in assistance or favors with a Persuasion check.
Contacts: Make an initial Investigation check in one minute.
Daze: Use Deception or Intimidation to daze an opponent.
Fascinate: Use an interaction skill to entrance others.
Favored Foe: Circumstance bonus to checks against a type of opponent.
Hide in Plain Sight: Hide while observed without need for a diversion.
Improvised Tools: No penalty for using skills without tools.
Inventor: Use Technology to create temporary devices.
Jack-of-all-trades: Use any skill untrained.
Languages: Speak and understand additional languages.
Ritualist: Use Expertise: Magic to create and perform rituals.
Skill Mastery: Make routine checks with one skill under any conditions.
Startle: Use Intimidation to feint in combat.
Taunt: Use Deception to demoralize in combat.
Tracking: Use Perception to follow tracks.
Well-informed: Immediate Investigation or Persuasion check to know something.

BEGINNER'S LUCK
FORTUNE
By spending a hero point, you gain an effective 5 ranks in one skill of your choice you currently have at 4 or fewer
ranks, including skills you have no ranks in, even if they can't be used untrained. These temporary skill ranks last
for the duration of the scene and grant you their normal benefits.

BENEFIT
GENERAL, RANKED
You have some significant perquisite or fringe benefit. The exact nature of the benefit is for you and the Gamemaster
to determine. As a rule of thumb it should not exceed the benefits of any other advantage, or a power effect costing
1 point. It should also be significant enough to cost at least 1 power point. An example is Diplomatic Immunity.
A license to practice law or medicine should not be considered a Benefit; it's simply a part of having training in
the appropriate Expertise skill and has no significant game effect.
Benefits may come in ranks for improved levels of the same benefit. The GM is the final arbiter as to what does and
does not constitute a Benefit in the setting.

Sample Benefits:
- Alternate Identity: You have an alternate identity, complete with legal paperwork.
- Ambidexterity: You are equally adept using either hand, suffering no circumstance penalty for using your off-hand.
- Cipher: Your true history is well hidden. Investigation checks concerning you are made at a -5 circumstance penalty per rank.
- Diplomatic Immunity: By dint of your diplomatic status, you cannot be prosecuted for crimes in nations other than your own.
- Security Clearance: You have access to classified government information, installations, and possibly equipment and personnel.
- Status: By virtue of birth or achievement, you have special status (nobility, knighthood, aristocracy, etc.).
- Wealth: You have greater than average wealth (well-off rank 1 through billionaire rank 5).
```


#### Domain Sketch
Favored Foe grants a targeted circumstance bonus across four interaction and perception skills specifically when dealing with a designated opponent type.

- records the favored foe type at acquisition: a creature type (aliens, animals, constructs, mutants, undead) or a profession (soldiers, police, Yakuza) approved by the GM
- enforces that the type is not excessively broad — categories like "humans" or "villains" are not permitted
- grants +2 circumstance bonus to Deception, Intimidation, Insight, and Perception checks when those checks involve the favored foe
- does not apply to checks against targets that are not of the favored foe type

Invariant: +2 bonus is not subject to power level limits; foe type must be specific enough to receive GM approval; bonus applies to exactly the four listed skills; does not apply outside qualifying interactions with the favored foe.

#### Decisions made (term level)
- Classified under Skill Advantage (not Combat Enhancement) because its bonus applies across four social and perception skill checks; the source labels it SKILL.
---

# Boundary Domain

## hero point

Owned by: Character Construction

#### Domain Language

- Hero points are a game resource spent to activate fortune advantages (Inspire, Leadership, Beginner's Luck, Seize Initiative, Ultimate Effort), enhance Luck re-rolls, and fund Sidekick actions.
- Fortune advantages define their effects in terms of spending a hero point as the activation cost.
- Hero points reset at the start of each adventure, which also refreshes Luck ranks.

**Ref — Instant Up**
Source: context/rules/HeroesHandbook-rules__chunk_077.md
Locator: lines 4799-4851
Extract: whole

```source
### Instant Up
General
You can go from prone to standing as a free action without the need for an Acrobatics skill check.

INTERPOSE
General
Once per round, when an ally within range of your normal movement is hit by an attack, you can choose to place
yourself between the attacker and your ally as a reaction, making you the target of the attack instead. The attack
hits you rather than your ally, and you suffer the effects normally. You cannot use this advantage against area
effects or perception range attacks, only those requiring an attack check.

LUCK
FORTUNE, RANKED (1/2 PL)
Once per round, you can choose to re-roll a die roll, like spending a hero point, including adding 10 to re-rolls of
10 or less. You can do this a number of times per game session equal to your Luck rank, with a maximum rank of half
the series power level (rounded down). Your Luck ranks refresh when your hero points reset at the start of an adventure.
The GM may choose to set a different limit on ranks in this advantage, depending on the series.

MINION
GENERAL, RANKED
You have a follower or minion. This minion is an independent character with a power point total of (advantage rank x 15).
Minions are subject to the normal power level limits, and cannot have minions themselves. Your minions (if capable of
independent thought) automatically have a helpful attitude toward you. They are subject to the normal rules for minions.
Minions do not earn power points. Instead, you must spend earned power points to increase your rank in this advantage
to improve the minion's power point total and traits. Minions also do not have hero points. Any lost minions are replaced
in between adventures with other followers with similar abilities at the Gamemaster's discretion.
```

**Ref — Fortune Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_068.md
Locator: lines 4287-4336
Extract: whole

```source
### Fortune Advantages
ADVANTAGE  EFFECT
Beginner's Luck: Spend a hero point to gain 5 temporary ranks in a skill.
Inspire: Spend a hero point to grant allies a +1 circumstance bonus per rank.
Leadership: Spend a hero point to remove a condition from an ally.
Luck: Re-roll a die roll once per rank.
Seize Initiative: Spend a hero point to go first in the initiative order.
Ultimate Effort: Spend a hero point to get an effective 20 on a specific check.

### General Advantages
ADVANTAGE  EFFECT
Assessment: Use Insight to learn an opponent's combat capabilities.
Benefit: Gain a significant perquisite or fringe benefit.
Diehard: Automatically stabilize when dying.
Eidetic Memory: Total recall, +5 circumstance bonus to remember things.
Equipment: 5 points of equipment per rank.
Extraordinary Effort: Gain two benefits when using extra effort.
Fearless: Immune to fear effects.
Great Endurance: +5 on checks involving endurance.
Instant Up: Stand from prone as a free action.
Interpose: Take an attack meant for an ally.
Minion: Gain a follower or minion with (15 x rank) power points.
Second Chance: Re-roll a failed check against a hazard once.
Sidekick: Gain a sidekick with (5 x rank) power points.
Teamwork: +5 bonus to support team checks.
Trance: Go into a deathlike trance that slows bodily functions.
```


#### Domain Sketch
Hero point is the meta-currency owned by Character Construction that fortune advantages consume to activate their effects. This module defines only the spend effects — it does not own hero point generation, refresh, or storage.

- consumed by fortune advantages (Inspire, Leadership, Beginner's Luck) as the activation cost for their effects
- proxied by Luck for re-roll effects — Luck draws from its own per-session pool rather than consuming an actual hero point
- bypasses power level limits when funding Inspire's bonus — a property of hero point benefits generally

Invariant: hero points are owned by Character Construction; this module consumes them but never generates or refreshes them.
---

## power point

Owned by: Character Construction

#### Domain Language

- Power points are the resource spent to purchase advantage ranks at character creation and advancement; the cost is 1 power point per rank.
- Power points also fund Minion and Sidekick improvements: the character spends earned power points to increase their rank in these advantages.

**Ref — Ch5 Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_065.md
Locator: lines 4107-4148
Extract: whole

```source
## CHAPTER 5: ADVANTAGES
Heroes are more than just skilled, they often have amazing advantages, beyond the abilities of ordinary people. In MU-
TANTS & MASTERMINDS, advantages often allow heroes to break the rules, gaining access to and doing things most people
cannot, or simply doing them better.

### Acquiring Advantages
Advantages are rated in ranks and bought with power points, just like abilities and skills. Advantages cost 1 power point
per rank. Some advantages have no ranks and are acquired only once, effectively at rank 1.
Advantage Cost = 1 power point per advantage rank

### Advantage Descriptions
Each advantage's description explains the benefit it provides. It also says if the advantage can be acquired in ranks and
the effects of doing so. Such advantages are listed as "Ranked" alongside the advantage name. Ranks in a advantage are
noted with a number after the advantage's name, such as "Defensive Roll 2" (for a character who has taken two ranks
in the Defensive Roll advantage), just like skill and power ranks. If there is a maximum number of ranks a character can
take, it's listed in parentheses after the word "Ranked" in the advantage's heading.

### Types Of Advantages
Advantages are categorized as one of four types:
Combat Advantages are useful in combat and often modify how various combat maneuvers are performed.
Fortune Advantages require and enhance the use of hero points.
General Advantages provide special abilities or bonuses not covered by the other categories.
Skill Advantages offer bonuses or modifications to skill use.

### Advantage Descriptions
Each advantage is listed by name, type, and if the advantage is available in multiple ranks, followed by a description
of the advantage's benefits. The effects of additional ranks of the advantage (if any) are noted in the text of each
advantage. In some cases a advantage's description mentions the normal conditions for characters who do not have the
advantage for comparison.
```


#### Domain Sketch
Power point is the acquisition currency owned by Character Construction that funds advantage purchases. This module consumes power points at 1 per advantage rank — it does not own their generation or budget.

- funds advantage acquisition at 1 power point per rank for all advantages in this module
- funds rank increases for Minion and Sidekick out of the character's earned power points pool

Invariant: power points are owned by Character Construction; this module spends them but never generates them.
---

## power level

Owned by: Character Construction

#### Domain Language

- Power level is the series cap that limits total attack bonus and active defense values, including those gained from ranked combat advantages such as Close Attack and Ranged Attack.
- Luck's maximum rank is capped at half the series power level (rounded down).
- Power level limits do not apply to circumstance bonuses from Favored Environment or Favored Foe.

**Ref — Close Attack**
Source: context/rules/HeroesHandbook-rules__chunk_070.md
Locator: lines 4451-4494
Extract: whole

```source
### Close Attack
COMBAT, RANKED
You have a +1 bonus to close attacks checks per rank in this advantage. Your total attack bonus is still limited by
power level. This advantage best suits characters with a level of overall close combat skill (armed and unarmed).
For capability with a particular type of attack, use the Close Combat skill.

CONNECTED
SKILL
You know people who can help you out from time to time. It might be advice, information, help with a legal matter,
or access to resources. You can call in such favors by making a Persuasion check. The GM sets the DC of the check,
based on the aid required. A simple favor is DC 10, ranging up to DC 25 or higher for especially difficult, dangerous,
or expensive favors. You can spend a hero point to automatically secure the favor, if the GM allows it.

CONTACTS
SKILL
You have such extensive and well-informed contacts you can make an Investigation check to gather information in only
one minute, assuming you have some means of getting in touch with your contacts. Further Investigation checks to
gather information on the same subject require the normal length of time, since you must go beyond your immediate
network of contacts.

DAZE
SKILL, RANKED (2)
You can make a Deception or Intimidation check as a standard action to cause an opponent to hesitate in combat.
Make a skill check against your target's resistance check (the same skill, Insight, or Will defense, whichever has
the highest bonus). If you win, your target is dazed (able to take only a standard action) until the end of your
next round. The ability to Daze with Deception and with Intimidation are separate advantages.
```

**Ref — Instant Up**
Source: context/rules/HeroesHandbook-rules__chunk_077.md
Locator: lines 4799-4851
Extract: whole

```source
### Instant Up
General
You can go from prone to standing as a free action without the need for an Acrobatics skill check.

INTERPOSE
General
Once per round, when an ally within range of your normal movement is hit by an attack, you can choose to place
yourself between the attacker and your ally as a reaction, making you the target of the attack instead. The attack
hits you rather than your ally, and you suffer the effects normally. You cannot use this advantage against area
effects or perception range attacks, only those requiring an attack check.

LUCK
FORTUNE, RANKED (1/2 PL)
Once per round, you can choose to re-roll a die roll, like spending a hero point, including adding 10 to re-rolls of
10 or less. You can do this a number of times per game session equal to your Luck rank, with a maximum rank of half
the series power level (rounded down). Your Luck ranks refresh when your hero points reset at the start of an adventure.
The GM may choose to set a different limit on ranks in this advantage, depending on the series.

MINION
GENERAL, RANKED
You have a follower or minion. This minion is an independent character with a power point total of (advantage rank x 15).
Minions are subject to the normal power level limits, and cannot have minions themselves. Your minions (if capable of
independent thought) automatically have a helpful attitude toward you. They are subject to the normal rules for minions.
Minions do not earn power points. Instead, you must spend earned power points to increase your rank in this advantage
to improve the minion's power point total and traits. Minions also do not have hero points. Any lost minions are replaced
in between adventures with other followers with similar abilities at the Gamemaster's discretion.
```


#### Domain Sketch
Power level is the series cap owned by Character Construction that enforces upper bounds on attack bonuses and Luck's maximum rank. This module depends on it for cap enforcement but does not own it.

- caps total attack bonus (including bonuses from Ranged Attack and Close Attack advantages) at the series power level
- limits Luck's maximum rank to half the series power level (rounded down)
- does not cap circumstance bonuses from Favored Environment or Favored Foe — those explicitly ignore power level limits

Invariant: power level cap applies to attack bonuses from ranked attack advantages; Luck rank cap is always half PL rounded down; circumstance bonuses from Favored Environment and Favored Foe are always exempt from the cap.
---

## attack check

Owned by: Combat

#### Domain Language

- Attack checks are the rolls used during combat maneuvers; combat advantages modify their bonuses or penalties.
- Accurate Attack, All-out Attack, Power Attack, and Defensive Attack all apply adjustments directly to the attack check modifier.
- Close Attack and Ranged Attack each add a flat bonus to the relevant type of attack check.

**Ref — Combat Advantages**
Source: context/rules/HeroesHandbook-rules__chunk_067.md
Locator: lines 4189-4286
Extract: whole

```source
### Combat Advantages
ADVANTAGE  EFFECT
Accurate Attack: Trade effect DC for attack bonus.
All-out Attack: Trade active defense for attack bonus.
Chokehold: Suffocate an opponent you have successfully grabbed.
Close Attack: +1 bonus to close attack checks per rank.
Defensive Attack: Trade attack bonus for active defense bonus.
Defensive Roll: +1 active defense bonus to Toughness per rank.
Evasion: Circumstance bonus to avoid area effects.
Fast Grab: Make a free grab check after an unarmed attack.
Favored Environment: Circumstance bonus to attack or defense in an environment.
Grabbing Finesse: Substitute Dex for Str when making grab attacks.
Improved Aim: Double circumstance bonuses for aiming.
Improved Critical: +1 to critical threat range with an attack per rank.
Improved Defense: +2 bonus to active defense when you take the defend action.
Improved Disarm: No penalty for the disarm action.
Improved Grab: Make grab attacks with one arm. Not vulnerable while grabbing.
Improved Hold: -5 circumstance penalty to escape from your holds.
Improved Initiative: +4 bonus to initiative checks per rank.
Improved Smash: No penalty for the smash action.
Improved Trip: No penalty for the trip action.
Improvised Weapon: Use Unarmed Combat skill with improvised weapons, +1 damage bonus.
Move-by Action: Move both before and after your standard action.
Power Attack: Trade attack bonus for effect bonus.
Precise Attack: Ignore attack check penalties for either cover or concealment.
Prone Fighting: No penalties for fighting while prone.
Quick Draw: Draw a weapon as a free action.
Ranged Attack: +1 bonus to ranged attack checks per rank.
Redirect: Use Deception to redirect a missed attack at another target.
Set-up: Transfer the benefit of an interaction skill to an ally.
Takedown: Free extra attack when you incapacitate a minion.
Throwing Mastery: +1 damage bonus with thrown weapons per rank.
Uncanny Dodge: Not vulnerable when surprised or caught off-guard.
Weapon Bind: Free disarm attempt when you actively defend.
Weapon Break: Free smash attack when you actively defend.
```


#### Domain Sketch
Attack check is the combat roll owned by the Combat module that combat advantages modify. This module adjusts attack check bonuses and penalties but does not own attack resolution.

- receives bonus adjustments from Ranged Attack (+1/rank) and Close Attack (+1/rank), both subject to power level cap
- receives penalty or bonus adjustments during trade-off maneuvers: Accurate Attack, All-out Attack, Defensive Attack, Power Attack each apply −N or +N to the attack check
- receives optional +2 circumstance bonus from Favored Environment when the player chooses attack allocation at round start

Invariant: attack checks are owned by Combat; this module modifies their bonus values through advantage rules but does not resolve the check.
---

## active defense

Owned by: Combat

#### Domain Language

- Active defenses (Dodge and Parry) are the defenses adjusted by combat advantage trade-offs: All-out Attack reduces them, Defensive Attack raises them.
- Defensive Roll adds bonus Toughness as an active defense that is lost when the character is vulnerable or defenseless.
- Favored Environment's +2 bonus can optionally apply to active defenses rather than attack.

**Ref — Defensive Attack**
Source: context/rules/HeroesHandbook-rules__chunk_071.md
Locator: lines 4495-4547
Extract: whole

```source
### Defensive Attack
COMBAT
When you make a defensive attack (see Maneuvers, page 249), you can take a penalty of up to -5 on your attack
bonus and add the same number (up to +5) to both your active defenses (Dodge and Parry).

### Defensive Roll
COMBAT, RANKED
You can avoid damage through agility and "rolling" with an attack. You receive a bonus to your Toughness equal
to your advantage rank, but it is considered an active defense similar to Dodge and Parry, so you lose this bonus
whenever you are vulnerable or defenseless. Your total Toughness, including this advantage, is still limited by power level.

DIEHARD
General
When your condition becomes dying you automatically stabilize on the following round without any need for a
Fortitude check, although further damage can still kill you.

EQUIPMENT
GENERAL, RANKED
You have 5 points per rank in this advantage to spend on equipment. This includes vehicles and headquarters. See
the Gadgets & Gear chapter for details on equipment and its costs. Many heroes rely almost solely on Equipment
in conjunction with their skills and other advantages.

EVASION
COMBAT, RANKED (2)
You have a +2 circumstance bonus to Dodge resistance checks to avoid area effects. If you have 2 ranks in this
advantage, your circumstance bonus increases to +5.
```

**Ref — Fast Grab**
Source: context/rules/HeroesHandbook-rules__chunk_073.md
Locator: lines 4614-4658
Extract: whole

```source
### Fast Grab
COMBAT
When you hit with an unarmed attack you can immediately make a grab check against that opponent as a free action.
Your unarmed attack inflicts its normal damage and counts as the initial attack check required to grab your opponent.

### Favored Environment
COMBAT
You have an environment you're especially suited for fighting in. Examples include in the air, underwater, in space,
in extreme heat or cold, in jungles or woodlands, and so forth. While you are in your favored environment, you gain a
+2 circumstance bonus to attack checks or your active defenses. Choose at the start of the round whether the bonus
applies to attack or defense. The choice remains until the start of your next round. This circumstance bonus is not
affected by power level.

### Favored Foe
SKILL
You have a particular type of opponent you've studied or are especially effective against. It may be a type of creature
(aliens, animals, constructs, mutants, undead, etc.), a profession (soldiers, police officers, Yakuza, etc.) or any
other category the GM approves. Especially broad categories like "humans" or "villains" are not permitted. You gain a
+2 circumstance bonus on Deception, Intimidation, Insight, and Perception checks dealing with your Favored Foe. This
circumstance bonus is not limited by power level.

FEARLESS
General
You are immune to fear effects of all sorts, essentially the same as an Immunity to Fear effect.
```


#### Domain Sketch
Active defense is the combat defense value (Dodge and Parry) owned by the Combat module that combat advantages modify. This module adjusts active defense values through trade-off maneuvers and circumstance bonuses.

- receives penalty adjustments from All-out Attack (−N to both Dodge and Parry, symmetric with attack bonus)
- receives bonus adjustments from Defensive Attack (+N to both Dodge and Parry, symmetric with attack penalty)
- receives optional +2 circumstance bonus from Favored Environment when the player chooses defense allocation at round start

Invariant: active defenses are owned by Combat; this module modifies them through advantage rules but does not resolve defense checks.
---

## extra effort

Owned by: Combat

#### Domain Language

- Extra effort is a general mechanic allowing characters to push beyond their normal limits; Extraordinary Effort modifies how extra effort works, granting two benefits instead of one at the cost of doubled fatigue.
- Spending a hero point at the start of the following turn reduces the cost of extraordinary effort from exhausted to merely fatigued.

**Ref — Extraordinary Effort**
Source: context/rules/HeroesHandbook-rules__chunk_072.md
Locator: lines 4548-4613
Extract: whole

```source
### Extraordinary Effort
General
When using extra effort, you can gain two of the listed benefits, even stacking two of the same type of benefit.
However, you also double the cost of the effort; you're exhausted starting the turn after your extraordinary effort.
If you are already fatigued, you are incapacitated. If you are already exhausted, you cannot use extraordinary effort.
Spending a hero point at the start of your next turn reduces the cost of your extraordinary effort to merely fatigued,
the same as a regular extra effort.

### Martial Arts And Fighting Styles
You can use combinations of advantages to create different "fighting styles" ranging from martial arts to superhero
combat techniques. For example, a "soft" fighting style focusing primarily on defense might include the advantages
Defensive Attack, Improved Defense, Improved Trip, and Instant Up. A "hard" fighting style focused on offense might
include All-out Attack, Improved Critical, Improved Smash, Power Attack, and Startle.

Sample Fighting Styles:
- Boxing: All-out Attack, Defensive Attack, Improved Critical (Unarmed), Power Attack, Takedown.
- Judo: Accurate Attack, Defensive Attack, Improved Disarm, Improved Grab, Improved Hold, Improved Trip.
- Kung Fu: Defensive Attack, Improved Critical (Unarmed), Improved Smash, Improved Trip, Instant Up, Power Attack, Startle.
- Sword-fighting: Accurate Attack, Defensive Attack, Improved Disarm, Improved Initiative, Power Attack, Taunt.
- Wrestling: Chokehold, Fast Grab, Improved Grab, Improved Hold, Power Attack.
```


#### Domain Sketch
Extra effort is the general mechanic owned by the Combat module. Extraordinary Effort modifies it: granting two benefits instead of one at doubled fatigue cost.

- doubles the normal benefits of extra effort (two benefits instead of one, including stacking the same type twice)
- doubles the fatigue cost (character becomes exhausted instead of fatigued, starting the turn after)
- prevents use when already exhausted
- allows reduction of the doubled fatigue cost back to normal (fatigued) by spending a hero point at the start of the following turn

Invariant: extra effort mechanics are owned by Combat; Extraordinary Effort modifies benefit count and fatigue cost but not what benefits are available.