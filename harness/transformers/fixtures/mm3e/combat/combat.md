---
state: domain-sketch
---

# Module: [Combat]

Scope: Initiative and turn order, action types, the attack check sequence, resistance checks and degrees, combat maneuvers, concealment, cover, surprise, damage and resistance, recovery, hazards, minions, team attacks, and damaging objects.

**Core terms**:
- initiative
- action round
- turn
- standard action
- move action
- free action
- reaction
- attack check
- attack bonus
- defense class
- close attack
- ranged attack
- critical hit
- resistance check
- damage
- Toughness resistance
- concealment
- cover
- surprise
- aim
- charge
- defend
- delay
- disarm
- grab
- ready
- recover
- trip
- feint
- slam attack
- team attack
- combined attack
- minion
- hazard
- falling
- suffocation
- damaging objects
- Material Toughness
- dying
- incapacitated
- recovery check
- hero point
- extra effort
- power stunt

---

# Core Domain

## Turn Structure

Turn Structure is the time-and-sequence framework that governs who acts when and what they can do. The action round is the six-second unit of in-game time; initiative determines the order within each round; and a character's turn is the slot in that order where they act. Turn Structure owns the full action economy: the allotment of one standard and one move action per turn (or two move actions), the unlimited but GM-arbitrated free actions, and the reactive right to spend reactions whenever circumstances demand. Delay and Ready extend the framework temporally — Delay defers a turn to a later slot while Ready prepays a future reaction — enabling characters to coordinate and respond across the initiative sequence. Turn Structure interacts with all other KAs: Attack Resolution and Combat Maneuvers consume standard actions; tactical choices (Delay, Ready, Defend) consume actions to create positional or temporal advantages. The invariant is that no character may act outside their turn except via free actions and reactions, and no action can exceed its defined cost without an explicit extra effort or other modifier.

#### Decisions made

- initiative, action round, turn, standard action, move action, free action, reaction, delay, and ready all pass independence and module-fit tests — they define when and how any combat action occurs.
- defend is placed in Combat Maneuvers (not here) because it is a tactical action that uses the standard action to confer a specific defensive benefit, not a structural component of turn sequencing.
- recover is placed in Damage and Resistance (not here) because its function is to remove damage conditions, not to manage action economy.

### initiative

#### Domain Language

- Initiative determines the order in which characters take their turns during a conflict.
- Base initiative modifier equals the character's Agility rank; advantages (e.g., Improved Initiative) and powers can modify it further.
- At the start of a conflict each character rolls d20 + initiative modifier; the turn order counts down from highest result to lowest.
- Ties are broken first by highest Dodge bonus, then highest Agility, then highest Awareness; if still tied, tied players each roll a die with the highest going first.
- The GM may roll a single initiative check for an entire group of minions, giving them all the same result.
- Characters who enter a conflict after it begins roll initiative when they join and act when their turn comes up in the existing order.

#### Domain Sketch

- Computes the conflict's turn order as a descending list from highest result to lowest at the start of each conflict.
- Inserts newly-arriving characters into the existing order at the result they roll when they join.
- Invariant: Every character in a conflict has exactly one initiative position; that position persists across rounds unless modified by delay or ready.

#### References

**Ref — Ch8 Action & Adventure**
Source: context/rules/HeroesHandbook-rules__chunk_196.md
Locator: lines 14083-14127
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Ch8 Action & Adventure"
chunk_index: 196
line_range: "14083-14127"
---

### Initiative

The  order  in  which  characters  take  their  turns  is  determined  by  initiative.  Base  initiative  bonus  is  equal  to the  characterâ€™s  Agility  rank.  Many  characters  have  advantages or powers that modify their initiative, such as Improved Initiative. At the start of a conflict, roll an initiative check for each character:

d20 + initiative modifier

The  initiative  check  determines  what  order  characters act in, counting down from highest check result to lowest. If two characters have the same initiative result, they act in order of highest Dodge bonus first, then highest Agility and highest Awareness. If there is still a tie, each tied player should roll a die, with the highest roll going first. The GM may roll just once for an entire group of minions, giving them all the same initiative.

If characters enter a conflict after itâ€™s begun, they roll initiative when they join-in and act when their turn comes up in the existing order.
```

---

### action round

#### Domain Language

- An action round (round) is a six-second segment of in-game time used when turn order and action economy matter.
- During a round each character involved takes one turn — that character's opportunity to act.
- A round represents approximately one page of a comic book — just long enough for the group to each do one thing.
- Rounds structure conflicts, challenges, and any situation where sequence and action limits are important.

#### Domain Sketch

- Advances to the next round once every character in the initiative order has completed their turn.
- Serves as the atomic time unit against which effect durations ("until start of your next turn", "until end of your turn") are measured.
- Invariant: Every declared action occurs within a round — no action is resolved outside the round structure.

#### References

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195-1237
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch1 The Basics"
topic: "Attack Checks"
chunk_index: 16
line_range: "1195-1237"
---

### The Action Round

When things really start happening in a MUTANTS & MASTERMINDS game, time is broken down into six-second segments called rounds (sometimes â€œaction roundsâ€). A round isnâ€™t very much time. Think of it like a page in a comic book, just long enough to go around the table once, with each hero doing something. Each characterâ€™s portion of the round is called their turn.

The things you can do on your turn are broken up into actions. There are standard actions, move actions, free actions, and reactions. During a round you can take a standard and a move action (or substitute an additional move action for your standard action) along with as many free actions as you wish and as many reactions as are called for.
```

---

### turn

#### Domain Language

- A turn is a character's portion of an action round — the window in which that character declares and resolves their actions.
- When a character's turn begins, effects that last "until the start of your next turn" end.
- When a character's turn ends, effects that last "until the end of your turn" end and required resistance checks for ongoing effects are made.
- A character informs the GM when their turn is finished so the next character in initiative order may act.

#### Domain Sketch

- Opens by cleaning up "start of turn" expiring effects, then accepts action declarations.
- Closes by cleaning up "end of turn" expiring effects, then fires mandatory ongoing-effect resistance checks.
- Provides the temporal frame within which free actions are valid — free actions cannot occur outside a character's own turn.
- Invariant: A character has exactly one turn per round (extra effort can add one more action within the same turn, not a second turn).

#### References

**Ref — Standard Action**
Source: context/rules/HeroesHandbook-rules__chunk_197.md
Locator: lines 14128-14174
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Standard Action"
chunk_index: 197
line_range: "14128-14174"
---

### Taking Your Turn

When  it  is  your  turn  in  the  initiative  order,  you  declare what actions your character will perform, and they are resolved in order.

### Starting Your Turn

The Gamemaster informs you when it is your turn. When you start your turn, you should:

â€¢  End  effects that last â€œuntil the start of your next turnâ€.

### Ending Your Turn

At the end of your turn, you should:

â€¢  End any effects that last â€œuntil the end of your turnâ€.
â€¢  Make any necessary resistance checks to recover from ongoing effects.
â€¢  Inform the Gamemaster and other players that your turn is finished.
```

**Ref — Taking Actions**
Source: context/rules/HeroesHandbook-rules__chunk_198.md
Locator: lines 14175-14218
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Taking Actions"
chunk_index: 198
line_range: "14175-14218"
---

### Taking Actions

You get a standard and a move action each turn. You can exchange your standard action for an additional move action, allowing you to perform two move actions. You can also perform as many free actions on your turn as you wish.

### Order Of Actions

You perform your actions in any order that you wish, but you cannot normally â€œsplitâ€ your actions.

### Ending Your Turn

At the end of your turn, you should end effects, make resistance checks, and inform the GM.
```

---

### standard action

#### Domain Language

- A standard action allows a character to do something meaningful: attack, use a skill, activate a power or advantage, or perform a similar task.
- Each character is limited to one standard action per turn.
- A standard action may be exchanged for an additional move action (two move actions instead of one standard + one move).
- Special actions (aim, charge, defend, disarm, grab, feint, recover, ready, trip) are standard actions.

#### Domain Sketch

- Permits one of: attack check, skill check, power activation, or any named special action (the Combat Maneuvers KA lists these).
- Consumed at declaration; no refund for a failed action.
- Invariant: Only one standard action per turn; extra effort can grant one additional standard action.

#### References

*(Deduplicated — all refs cited by earlier terms in this KA block. See chunk_197 under turn, chunk_016 under action round.)*

---

### move action

#### Domain Language

- A move action allows a character to move up to their speed rank or perform an equivalent activity (draw/stow an item, stand up, pick up an object).
- In a normal turn a character gets one standard action and one move action; the move may come before or after the standard action.
- A standard action may be exchanged for an additional move action, enabling two move actions in one turn.
- Actions cannot normally be split — a character may not move part of their speed, take a standard action, then move the remainder.
- A DC 15 Athletics check as a free action can increase ground speed rank by +1 for one round on one or more degrees of success.

#### Domain Sketch

- Covers both physical displacement (moving up to speed rank) and equivalent physical tasks (drawing a weapon, standing from prone).
- May be taken before or after the standard action, but not split around it.
- Invariant: Only one move action per turn unless the standard action is exchanged for a second move action.

#### References

*(Deduplicated — all refs cited by earlier terms in this KA block. See chunk_197, chunk_198 under turn.)*

---

### free action

#### Domain Language

- A free action consumes so little time it is considered to take no real time over the span of a round.
- A character may perform as many free actions per turn as the GM considers reasonable.
- Examples: dropping an object, dropping prone, speaking a sentence or two, ceasing to concentrate on a power, maintaining a grab.
- Free actions are a conscious choice made on the character's own turn; they cannot occur when it is not the character's turn (reactions serve that role).

#### Domain Sketch

- Executes alongside any other action without consuming standard or move action budget.
- Invariant: Free actions only occur on the character's own turn; off-turn interventions use the reaction mechanism instead.

#### References

*(Deduplicated — all refs cited by earlier terms in this KA block. See chunk_197 under turn, chunk_016 under action round.)*

---

### reaction

#### Domain Language

- A reaction is a response to something else happening during the round; it can occur even when it is not the character's turn.
- Reactions take no significant time and do not count against the character's normal action allotment.
- A character can react as often as circumstances dictate, but only when circumstances dictate.
- Spending a hero point is a reaction.
- Examples: taking a readied action when triggered, counter-disarming after losing a melee disarm, firing a netline after declaring a ready.

#### Domain Sketch

- Fires outside the character's own turn in response to a triggering event.
- Does not consume or replace the character's standard, move, or free action budget.
- Invariant: Reactions fire only when circumstances trigger them; they cannot be voluntarily taken at any time like free actions.

#### References

**Ref — Reactions**
Source: context/rules/HeroesHandbook-rules__chunk_017.md
Locator: lines 1238-1344
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch1 The Basics"
topic: "Reactions"
chunk_index: 17
line_range: "1238-1344"
---

### Reactions

A  reaction  is  something  you  do  in  response  to  something  else.  A  reaction  doesnâ€™t  take  any  significant  time, like a free action. The difference is you react in response to something else happening during the round, perhaps not even on your turn. Reactions donâ€™t count against your normal allotment of actions and you can react as often as the circumstances dictate, but only when they dictate.
```

---

### delay

#### Domain Language

- Delay is a no-action choice to defer one's entire turn to later in the initiative order.
- A character cannot delay after having already taken an action on their turn, or if unable to take actions.
- After any other character acts, the delayed character may choose to act; their initiative slot moves to where they acted.
- If the trigger never fires before the character's original initiative comes up next round, the delayed turn is lost and initiative stays put.
- Beneficial effects that last until end of turn expire when the character delays; harmful effects persist until after the character acts.

#### Domain Sketch

- Removes the character from the current initiative slot and holds them in reserve for later activation.
- Transfers the initiative position to the point of insertion when the character chooses to act.
- Invariant: Cannot delay after any action has been taken on the current turn, and cannot delay if unable to take actions.
- Invariant: The delayed turn is lost if not taken before the same initiative position arrives in the next round.

#### References

**Ref — Crawl**
Source: context/rules/HeroesHandbook-rules__chunk_211.md
Locator: lines 14871-14914
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Crawl"
chunk_index: 211
line_range: "14871-14914"
---

### Delay

### No Action

When you delay, you choose to take your turn later in the initiative order. You must delay your entire turn. You cannot delay if you have already taken an action on your turn, or if you are unable to take actions.

At any point after any other character in the conflict has acted, you can choose to take your turn. Your initiative moves into the new place in the order where you act, and you take your normal allocation of actions. If you do not act before your initiative comes up in the next round, your turn ends, you lose your delayed turn, and your initiative remains where it is.

Beneficial effects lasting until the end of your turn end when you choose to delay, but harmful effects that last until the end of your turn last until after you act. Likewise, you do not make resistance checks until after you have taken your turn, so delaying can draw out some effects.
```

---

### ready

#### Domain Language

- Ready is a standard action that prepares a single standard, move, or free action to trigger on a specified future condition.
- The character declares the action and triggering circumstances; the readied action fires as a reaction when conditions are met.
- When the readied action fires, the character's initiative slot moves to where they acted.
- If the trigger does not occur before the character's next initiative, the readied action is lost; the same action may be readied again.

#### Domain Sketch

- Packages an action with a trigger condition for deferred execution as a reaction.
- Shifts the character's initiative position to the point where the readied action fires.
- Invariant: Only one readied action at a time; the character may ready the same action again on a subsequent turn if the trigger never fired.
- Invariant: The readied action is automatically lost if the character's next initiative comes up without the trigger firing.

#### References

**Ref — Move**
Source: context/rules/HeroesHandbook-rules__chunk_213.md
Locator: lines 14959-14998
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Move"
chunk_index: 213
line_range: "14959-14998"
---

### Ready

### Standard Action

Readying lets you prepare to take an action later, after you would normally act on your initiative, but before your initiative on your next turn. Readying is a standard action, so you can move as well.

If you come to your next turn and have not yet performed your readied action, you donâ€™t get to take the readied action, you just lose your previous turn. You can ready the same action again on your next turn, if you wish, continuing to wait for the right circumstances.
```

**Ref — Standard Action**
Source: context/rules/HeroesHandbook-rules__chunk_214.md
Locator: lines 14999-15043
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Standard Action"
chunk_index: 214
line_range: "14999-15043"
---

### Maneuvers

You can ready a single standard, move, or free action. To do so, specify the action you will take and the circumstances under which you will take it. Then, any time before your next turn, you may take the readied action as a reaction to those circumstances. Your place in the initiative order then becomes the point where you took your readied action.
```

---

## Attack Resolution

Attack Resolution is the sequence that determines whether an attack lands and with what force. The attack check is the gatekeeper — rolling d20 + attack bonus against the target's defense class to produce a hit or miss; a natural 20 extends to a potential critical hit while a natural 1 always misses. Defense class is calculated from the applicable active defense (Parry for close, Dodge for ranged) plus 10, and is modified by conditions, concealment, and cover. The attack bonus aggregates Fighting or Dexterity, skill ranks, and circumstance modifiers (including maneuver trade-offs). Close and ranged attacks are the two fundamental attack types that differ by range and which defense they target. Critical hits extend the resolution: when a natural 20 produces a total that beats the defense class, the attacker chooses from three amplified outcomes. Aim and charge are action-phase modifiers that feed into the attack check. Attack Resolution owns the rules that determine whether an attack connects; it does not own damage outcomes (those belong to Damage and Resistance) or the conditions imposed by effects (owned by Check Resolution).

#### Decisions made

- attack check, attack bonus, defense class, close attack, ranged attack, and critical hit pass both tests — they are the core attack resolution mechanics.
- aim and charge are included here because they directly modify the attack check result or target selection; their outcome is a modifier to the attack roll, not a separate resolution system.
- slam attack is placed under Combat Maneuvers because it is a special maneuver used during charge, modifying the damage formula — its primary effect is on damage, not on the attack check itself.
- area and perception-range effects bypass attack checks entirely; they are flagged as a context gap for the AC phase.

### attack check

#### Domain Language

- An attack check determines whether an attack hits: d20 + attack bonus vs. target's defense class; equal or exceeding means a hit.
- A natural 20 on the d20 always hits regardless of defense and may be a critical hit.
- A natural 1 on the d20 always misses regardless of the total.
- Area and perception-range effects do not require attack checks; they automatically affect the target or area and cannot score critical hits or misses.

#### Domain Sketch

- Produces a binary hit/miss result that gates all further resolution (damage, conditions, effects).
- Extends to a critical hit determination when the d20 result is exactly 20.
- Invariant: d20 result of 1 always misses; d20 result of 20 always hits regardless of totals.
- Invariant: Area and perception-range attacks bypass this check entirely — no attack bonus, no defense class comparison.

#### References

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195-1237
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch1 The Basics"
topic: "Attack Checks"
chunk_index: 16
line_range: "1195-1237"
---

### Attack Checks

An  attack  check  determines  whether  or  not  you  hit  an opponent  in  combat  with  an  attack.  It  is  a  d20  roll  plus your bonus with that particular attack, usually based off of  Fighting  or  Dexterity  and  appropriate  modifiers,  like the Close and Ranged Combat skills. The difficulty is your targetâ€™s  defense  class:  Parry  for  close  attacks,  Dodge  for ranged attacks.

Attack Check = d20 + attack bonus + modifiers vs. defense class

A natural 20 on an attack check always hits and may be a critical hit. A natural 1 on an attack check always misses, regardless of the check total.
```

**Ref — Conflicts**
Source: context/rules/HeroesHandbook-rules__chunk_202.md
Locator: lines 14386-14434
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Vacuum"
chunk_index: 202
line_range: "14386-14434"
---

### Attacks

An attack check represents an attempt to hit a target with an attack. When you make an attack check, roll the die and add your bonus with that attack. If your result equals or exceeds the targetâ€™s defense, your attack hits and may have some effect.

Attack Check = d20 + attack bonus vs. defense class
```

---

### attack bonus

#### Domain Language

- The attack bonus is the modifier added to the d20 roll when making an attack check.
- For most characters it is based on Fighting (close attacks) or Dexterity (ranged attacks) plus applicable Close Combat or Ranged Combat skill ranks plus circumstance modifiers.
- Maneuvers (Accurate Attack, All-out Attack, Defensive Attack, Power Attack) can temporarily shift the attack bonus in exchange for other trade-offs.
- Conditions and tactical circumstances (aim bonus, charge penalty, concealment, cover) apply as circumstance modifiers.

#### Domain Sketch

- Aggregates all static and circumstance modifiers into a single value added to d20 for the attack check.
- Shifts temporarily when a maneuver trade-off is declared before the attack check.
- Invariant: Cannot be reduced below +0 by maneuver penalties (all maneuvers have this floor constraint).

#### References

**Ref — Standard Action**
Source: context/rules/HeroesHandbook-rules__chunk_214.md
Locator: lines 14999-15043
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Standard Action"
chunk_index: 214
line_range: "14999-15043"
---

### Accurate Attack

When you make an attack, you can take a penalty of up to â€"2 on the effect modifier of the attack and add the same number (up to +2) to your attack bonus. Your effect modifier cannot be reduced below +0 and your attack bonus cannot more than double.

### All-out Attack

When you make an attack you can take a penalty of up to â€"2 on your active defenses and add the same number (up to +2) to your attack bonus.

### Defensive Attack

When you make an attack you can take a penalty of up to â€"2 on your attack bonus and add the same number (up to +2) to your active defenses.
```

---

### defense class

#### Domain Language

- The defense class is the difficulty number an attack check must equal or exceed to hit: Defense Class = defense rank + 10.
- Close attacks target Parry; ranged attacks target Dodge; certain attacks may target other defenses.
- Vulnerable halves active defense ranks (round up); defenseless reduces active defense ranks to 0 making the base DC just 10.
- Attackers may make attack checks against defenseless targets as routine checks (auto-hit with bonus ≥ 0).

#### Domain Sketch

- Represents the minimum attack check result required to hit a specific character with a specific attack type.
- Recalculates dynamically when active defense ranks change (vulnerable, defenseless conditions).
- Invariant: Defense Class = active defense rank + 10; applies independently per attack type (close vs. ranged).

#### References

**Ref — No Cover**
Source: context/rules/HeroesHandbook-rules__chunk_208.md
Locator: lines 14738-14790
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "No Cover"
chunk_index: 208
line_range: "14738-14790"
---

### Defenses

Your defenses determine how difficult it is to hit you with various attacks. Most attacks target your active defenses, Dodge and Parry: close attacks target Parry while ranged attacks target Dodge.

You add your defense rank to a base value of 10 to determine your defense class against an attack:

Defense Class = defense + 10
```

**Ref — Vulnerable And Defenseless**
Source: context/rules/HeroesHandbook-rules__chunk_209.md
Locator: lines 14791-14830
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Vulnerable And Defenseless"
chunk_index: 209
line_range: "14791-14830"
---

### Vulnerable And Defenseless

When you are vulnerable, your active defense ranks are halved (round up fractions).

When you are defenseless, your active defense ranks are reduced to zero, meaning the base difficulty class to hit you is just 10! Attackers can make attack checks against defenseless targets as routine checks, meaning a hit is guaranteed with an attack bonus of 0 or more.
```

---

### close attack

#### Domain Language

- A close attack targets a character within physical reach (by touch or melee weapon) and is checked against the target's Parry defense.
- Strength-based damage (unarmed, melee weapons) is close range by default.
- Close attacks can score critical hits; many maneuvers (charge, trip, disarm, grab) are close attacks.

#### Domain Sketch

- Selects Parry as the target defense, making Fighting rank the primary attack modifier.
- Enables all physical contact maneuvers (grab, trip, disarm, slam); ranged attacks cannot trigger these maneuvers.
- Invariant: Target must be within physical reach; attacks beyond reach require a ranged attack type.

#### References

**Ref — Damaging Objects**
Source: context/rules/HeroesHandbook-rules__chunk_206.md
Locator: lines 14631-14689
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Damaging Objects"
chunk_index: 206
line_range: "14631-14689"
---

### Range

An attack has one of three ranges: close, ranged, and perception. A close attack can only affect a target you can physically reach, by touch or wielding a melee weapon, for example. A ranged attack can affect a target at a distance.
```

---

### ranged attack

#### Domain Language

- A ranged attack targets a character at a distance and is checked against the target's Dodge defense.
- Short range (rank × 25 ft): no penalty; medium (rank × 50 ft): −2 circumstance; long (rank × 100 ft): −5 circumstance; beyond long range the target is out of range and cannot be attacked.
- Perception-range attacks automatically hit without an attack check and cannot score critical hits or misses.
- Modifiers affecting the attack check (including maneuvers) do not apply to area or perception effects.

#### Domain Sketch

- Selects Dodge as the target defense; applies distance modifiers based on range bands.
- Degrades accuracy at medium and long range through circumstance penalties to the attack check.
- Invariant: Cannot target beyond long range (rank × 100 ft); targets outside this range are simply out of range.
- Invariant: Perception-range attacks bypass this entire check — they automatically affect targets with no attack roll.

#### References

*(Deduplicated — chunk_206 cited by close attack; chunk_016 cited by attack check.)*

---

### critical hit

#### Domain Language

- A critical hit occurs when the attack check rolls a natural 20 and the total also equals or exceeds the target's defense class.
- A natural 20 that does not beat the defense class is still a hit but not a critical hit.
- On a critical hit the attacker chooses one of three effects: Increased Effect (+5 resistance DC), Added Effect (bonus rank-0 secondary effect), or Alternate Effect (temporary power stunt at no fatigue cost).
- Against a minion, Increased Effect bypasses the resistance check entirely — the minion automatically receives the worst degree.
- Improved Critical advantage extends the threat range below natural 20; auto-hit only occurs on a natural 20.
- Area and perception effects cannot score critical hits.

#### Domain Sketch

- Extends a natural-20 hit into one of three amplified outcome options chosen by the attacker.
- Applies the Increased Effect option against minions with an instant-defeat bypass rule.
- Invariant: Confirmation requires both natural 20 AND total ≥ defense class; missing the defense class on a natural 20 is a normal hit only.
- Invariant: Area and perception-range attacks can never produce critical hits.

#### References

**Ref — Critical Misses**
Source: context/rules/HeroesHandbook-rules__chunk_203.md
Locator: lines 14435-14489
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Critical Misses"
chunk_index: 203
line_range: "14435-14489"
---

### Critical Misses

Conversely, a natural 1 (the d20 comes up 1) on an attack check is always a miss, regardless of your total result.

### Critical Hits

When you make an attack check and get a natural 20, you automatically hit, regardless of your targetâ€™s defense, and you score a threat. To find out if itâ€™s a critical hit, determine if the attack check total is equal to or greater than the targetâ€™s defense. If so, it is a critical hit.

A critical hit can have one of the following three effects:

â€¢  Increased Effect: The critical hit increases the difficulty to resist the attackâ€™s effect by +5. Against a minion, this bypasses the resistance check entirely; the minion automatically receives the highest degree of the attackâ€™s effect.

â€¢  Added Effect: The critical hit adds another effect onto the attack, but its effective rank is 0.

â€¢  Alternate Effect: The critical hit results in an alternate effect for the attack, like a use of extra effort for a power stunt, except the character suffers no fatigue as a result.
```

---

### aim

#### Domain Language

- Aim is a standard action that lines up a subsequent attack, granting a circumstance bonus on the following attack check.
- Close attack or ranged attack at close range: +5 circumstance bonus; ranged attack at greater distance: +2 circumstance bonus.
- The attacker is vulnerable while aiming.
- A free action maintains aim before making the attack; losing the ability to maintain aim cancels the bonus.
- The very next action after aiming must be the attack; any other action cancels the aim bonus.

#### Domain Sketch

- Trades the current turn's standard action for a circumstance bonus to the immediately following attack check.
- Applies vulnerable condition to the aiming character from the moment aim is declared until the attack is made.
- Invariant: The aim bonus is lost if any action other than the declared attack occurs next.

#### References

**Ref — Standard Action**
Source: context/rules/HeroesHandbook-rules__chunk_210.md
Locator: lines 14831-14870
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Standard Action"
chunk_index: 210
line_range: "14831-14870"
---

AIM

### Standard Action

By taking a standard action to aim and line up an attack, you get a bonus to hit when you make the attack. If youâ€™re making a close attack, or a ranged attack at close range, you get a +5 circumstance bonus on your attack check. If youâ€™re making a ranged attack from a greater distance, you get a +2 circumstance bonus.

However, you are vulnerable while aiming and it requires a free action to maintain your aim before you make your attack. If you are unable to maintain it, you lose its benefit.

Once you aim, your next action must be to make the attack. Taking a different action spoils your aim and you lose the bonus.
```

---

### charge

#### Domain Language

- Charge is a standard action: the attacker moves their speed rank in a straight line toward a target, then makes a close attack at the end of movement with a −2 circumstance penalty.
- Combined with a move action, the attacker can move up to twice their speed rank before attacking.
- Charge enables the slam attack maneuver.

#### Domain Sketch

- Combines movement and a close attack into a single standard action at a −2 attack check penalty.
- Extends movement range when combined with a move action (up to 2× speed rank total).
- Enables the slam attack variant when the attacker chooses to use momentum as the damage source.
- Invariant: Movement must be in a relatively straight line toward the target; cannot charge a target not in line-of-movement.

#### References

*(Deduplicated — chunk_210 cited by aim.)*

---

## Damage and Resistance

Damage and Resistance is the system that determines the consequence of a landed attack and the pathway from unharmed through degradation to incapacitation, dying, and death. The Damage effect is the primary weapon of combat — when a hit is scored the target makes a Toughness resistance check against a DC of damage rank + 15. Degrees of failure accumulate penalties and impose conditions: a single miss begins a cumulative −1 Toughness penalty; two degrees add dazed; three degrees add staggered; four degrees incapacitate. The incapacitated state exposes the target to the dying sequence, and another failure while dying kills. Toughness resistance is the specific check that governs this, distinct from the generic resistance check used for other effects (Affliction, ongoing hazards). Recovery undoes this progression — living targets heal one damage condition per minute of rest, and the Recover action accelerates this in-conflict. The recovery check is the per-turn automatic roll that ends ongoing effects. This KA owns the damage progression from hit to death and the full recovery arc back to normal.

#### Decisions made

- resistance check is included here because combat's central use of resistance checks is for Toughness vs. Damage; the general resistance check mechanic is owned by Check Resolution, but Combat must define how it applies to ongoing combat effects.
- dying and incapacitated are placed here because they are the direct terminal outputs of the Toughness failure chain.
- recover (the action) is placed here rather than Turn Structure because its purpose is to remove damage conditions, not to manage action economy.
- recovery check is placed here because it is the primary mechanism by which ongoing conditions end in combat.

### resistance check

#### Domain Language

- A resistance check resists a power effect or hazard: d20 + defense bonus vs. resistance DC (typically effect rank + 10).
- Resistance checks are not actions — they represent involuntary responses and do not consume action allotment.
- Resistance checks may be graded: different degrees of failure impose progressively worse outcomes.
- Ongoing effects require a resistance check at the end of each of the target's turns; success ends the effect and removes conditions.
- The Recover action grants an additional resistance check against an ongoing effect beyond the normal end-of-turn check.

#### Domain Sketch

- Fires automatically at end of each turn for ongoing effects without requiring any action.
- Grades its result by degree of failure to determine which condition or penalty is imposed.
- Invariant: d20 + defense bonus vs. effect rank + 10 (Damage uses effect rank + 15).
- Invariant: Success on the resistance check against an ongoing effect ends that effect and removes all its conditions.

#### References

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195-1237
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch1 The Basics"
topic: "Attack Checks"
chunk_index: 16
line_range: "1195-1237"
---

### Resistance Checks

A  resistance  check  is  an  attempt  to  resist  different  effects, ranging from damage and injury to traps, poisons, and various power effects. A resistance check is a d20 roll + the appropriate defense.

Resistance Check = d20 + defense bonus + modifiers vs. hazardâ€™s DC (generally 10 + rank)

Resistance checks may be graded, with different results at different degrees.
```

**Ref — Vulnerable And Defenseless**
Source: context/rules/HeroesHandbook-rules__chunk_209.md
Locator: lines 14791-14830
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Vulnerable And Defenseless"
chunk_index: 209
line_range: "14791-14830"
---

### Ongoing Effects

Some effects are not resisted just once, but multiples times. Make a resistance check for the target of an ongoing effect at the end of each of the targetâ€™s turns. A successful check ends the effect and removes conditions imposed by it.
```

---

### damage

#### Domain Language

- Damage is a power effect applied by a successful attack; the target makes a Toughness resistance check against DC = damage rank + 15.
- Failure degrees: one degree → −1 cumulative Toughness penalty; two degrees → dazed + −1 penalty; three degrees → staggered + −1 penalty (if already staggered, apply fourth degree); four degrees → incapacitated.
- Toughness check penalties from repeated failures are cumulative across all hits.
- An incapacitated target that fails another Toughness check becomes dying; a dying target that fails becomes dead.
- Strength provides a built-in close-range Damage effect; Strength-based weapons add Strength rank + Damage rank together.

#### Domain Sketch

- Accumulates a −1 penalty on every Toughness resistance check, regardless of degree of failure.
- Escalates character state through a four-degree chain: penalty only → dazed → staggered → incapacitated.
- Chains further into dying and then dead when the incapacitated character continues to receive damage.
- Invariant: Damage resistance DC is always damage rank + 15.
- Invariant: Cumulative penalty persists until the character recovers; it stacks across all attackers.

#### References

**Ref — Critical Misses**
Source: context/rules/HeroesHandbook-rules__chunk_203.md
Locator: lines 14435-14489
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Critical Misses"
chunk_index: 203
line_range: "14435-14489"
---

### Damage

A successful attack with a Damage effect requires the target to make a Toughness resistance check.

### Damage Resistance Check

Toughness vs. [Damage rank + 15]

Success: The damage has no effect.
Failure (one degree): The target has a â€"1 circumstance penalty to further resistance checks against damage.
Failure (two degrees): The target is dazed until the end of their next turn and has a â€"1 circumstance penalty.
Failure (three degrees): The target is staggered and has a -1 circumstance penalty.
Failure (four degrees): The target is incapacitated.

The circumstance penalties to Toughness checks are cumulative.

If an incapacitated target fails a resistance check against Damage, the targetâ€™s condition shifts to dying. A dying target who fails a resistance check against Damage is dead.
```

**Ref — Example Of Conflict**
Source: context/rules/HeroesHandbook-rules__chunk_204.md
Locator: lines 14490-14552
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Example Of Conflict"
chunk_index: 204
line_range: "14490-14552"
---

Trawler has Toughness 10 and the GM rolls a 9. Thatâ€™s a 19 total, two degrees of failure vs. DC 25. Trawler suffers both a â€"1 to Toughness checks and a dazed condition.
```

**Ref — Example Of Conflict**
Source: context/rules/HeroesHandbook-rules__chunk_205.md
Locator: lines 14553-14630
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Example Of Conflict"
chunk_index: 205
line_range: "14553-14630"
---

The laser is rank 10, for a Damage resistance DC of 25. Trawler has Toughness 10 and the GM rolls a 9. Thatâ€™s a 19 total, two degrees of failure vs. DC 25. Trawler suffers both a â€"1 to Toughness checks and a dazed condition.
```

---

### Toughness resistance

#### Domain Language

- Toughness resistance is the specific resistance check against a Damage effect: d20 + Toughness rank vs. damage rank + 15.
- Every failure imposes a −1 cumulative circumstance penalty to all future Toughness resistance checks for that character.
- The penalty stacks across multiple hits and across different attackers within a scene.
- Impervious Toughness ignores Damage effects below a threshold rank equal to half the Impervious rank.
- Living targets recover Toughness penalties by removing one damage condition per minute of rest.

#### Domain Sketch

- Specializes the resistance check for Damage effects with a higher DC formula (rank + 15 instead of rank + 10).
- Tracks a running cumulative penalty that degrades future Toughness checks until the character recovers.
- Invariant: Penalty is cumulative — each failure adds another −1 regardless of degree.

#### References

**Ref — Recovery**
Source: context/rules/HeroesHandbook-rules__chunk_216.md
Locator: lines 15092-15151
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Lasting Injuries"
chunk_index: 216
line_range: "15092-15151"
---

Living targets remove one damage condition per minute of rest, starting from their most severe condition and working back. So a damaged character recovers from being incapacitated, then staggered, dazed, and finally removes a â€"1 Toughness check penalty per minute until fully recovered.
```

---

### dying

#### Domain Language

- Dying is the near-death state entered when an incapacitated character suffers further Toughness failure, or when certain hazards reach their final stage.
- A dying character who fails another Toughness resistance check against damage dies.
- A dying character cannot stabilize from suffocation or vacuum until able to breathe/reach normal atmosphere.
- Death of major characters requires an active second effort; accidental single-roll death is near-impossible for main characters.
- Minions can be killed outright when a player declares intent to kill and the attack succeeds.
- Lasting injuries and death are handled as complications for narrative continuity.

#### Domain Sketch

- Sits at the terminal end of the damage escalation chain: incapacitated → dying → dead.
- Blocks self-stabilization when the cause (lack of air, vacuum) persists.
- Protects major characters from accidental death by requiring a second active harmful action after incapacitation.
- Invariant: Another Toughness resistance failure while dying results in death.

#### References

*(Deduplicated — chunk_203 cited by damage; chunk_216 cited by Toughness resistance.)*

---

### incapacitated

#### Domain Language

- Incapacitated is the condition imposed by four degrees of failure on a Toughness resistance check (defenseless + stunned + unaware; character typically falls prone).
- An incapacitated target that fails another Toughness resistance check transitions to dying.
- Incapacitation can also result from suffocation, vacuum exposure, or other hazard escalation.
- While incapacitated the character cannot act (stunned) and has no active defenses (defenseless).

#### Domain Sketch

- Combines three conditions simultaneously: defenseless (no active defense), stunned (no actions), and unaware.
- Serves as the gateway state that, on further damage, leads to dying.
- Can be reached by damage (4 degrees failure) or by hazards (suffocation, vacuum).
- Invariant: While incapacitated: cannot act, defense class = 10, attackers may use routine checks.

#### References

**Ref — Vacuum**
Source: context/rules/HeroesHandbook-rules__chunk_202.md
Locator: lines 14386-14434
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Vacuum"
chunk_index: 202
line_range: "14386-14434"
---

On the third round of exposure to vacuum, a character must succeed on a Fortitude check (DC 20) each round or suffer from aeroembolism. Two or more degrees of failure impose the incapacitated condition.

If the check fails, or when the character simply stops holding his breath, he begins to suffocate: the next round, he becomes incapacitated. The following round, heâ€™s dying.
```

---

### recovery check

#### Domain Language

- A recovery check is a resistance check made to end an ongoing condition or effect; it is not an action.
- At the end of each of the character's turns, a resistance check is automatically made against any ongoing effect.
- The Recover action (standard action, once per conflict) grants an additional resistance check beyond the normal end-of-turn check.
- Natural recovery: living targets remove one damage condition per minute of rest, working from the worst condition back toward normal.
- Healing and Regeneration effects can speed this process.

#### Domain Sketch

- Fires automatically at the end of each turn as part of the turn's closing sequence.
- Produces a binary result: success removes the ongoing effect and all its conditions; failure keeps them.
- Complements the once-per-conflict Recover action which grants one additional check on top of the automatic one.
- Invariant: Automatic recovery check costs no action; the Recover action grants an extra check at the cost of the full standard action for that turn.

#### References

**Ref — Recovery**
Source: context/rules/HeroesHandbook-rules__chunk_207.md
Locator: lines 14690-14737
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Recovery"
chunk_index: 207
line_range: "14690-14737"
---

Living targets remove one damage condition per minute of rest, starting from their worst condition and working back. So a damaged character recovers from being incapacitated, then staggered, dazed, and finally removes a â€"1 Toughness check penalty per minute until fully recovered.
```

---

### recover

#### Domain Language

- Recover is a standard action requiring the character's entire turn; usable only once per conflict.
- On recovery: remove the highest current level of damage or fatigue; alternatively make an additional resistance check against one ongoing effect (beyond the normal end-of-turn check).
- Recovery also grants +2 to active defenses until the start of the character's next turn.
- Remaining damage, fatigue, or effects after using recover must heal normally (rest or outside assistance).

#### Domain Sketch

- Removes the worst current damage condition or fatigue level in a single standard-action turn.
- Grants a defensive bonus (+2 active defenses) until start of next turn as a secondary benefit.
- Invariant: Once per conflict — the once-per-conflict limit cannot be reset during a scene.

#### References

*(Deduplicated — chunk_213 cited by recovery check.)*

---

## Combat Maneuvers

Combat Maneuvers are the specialized standard-action tactics that produce outcomes beyond a simple hit — disabling, restraining, toppling, misdirecting, or buffeting opponents. Each maneuver modifies the standard attack resolution sequence with a specific check chain: disarm and trip each use an attack check followed by an opposed secondary check; grab uses an attack check followed by a resistance check; feint replaces the attack check with a skill check to impose a condition; slam attack modifies the damage formula of a charge; and defend replaces an attack with a defensive opposed roll. Maneuvers are optional additions to declared actions; the GM decides if circumstances permit a given maneuver. None of the maneuvers directly deal Toughness damage by themselves (except slam attack, which adds a damage bonus); their primary purpose is to impose conditions (prone, restrained, bound, vulnerable) or change the tactical situation. Combat Maneuvers depend on Attack Resolution for the initial hit determination and on Damage and Resistance for damage outcomes when applicable.

#### Decisions made

- disarm, grab, trip, feint, slam attack, and defend pass both tests — each is a distinct tactical action with its own resolution chain.
- aim is placed under Attack Resolution (not here) because its sole effect is a circumstance bonus to the attack check.
- charge is placed under Attack Resolution (not here) because it is fundamentally an attack with movement; slam attack, the charge variant, is kept here because its primary mechanical contribution is to the damage formula.
- defend is included here rather than Turn Structure because it replaces the attack action with a defensive maneuver that produces a specific mechanical effect.
- No subtypes added: close attack and ranged attack already encode the subtype relationship to attack check as distinct terms; the existing term structure is sufficient.

### defend

#### Domain Language

- Defend is a standard action: the character focuses on avoiding attacks rather than attacking.
- The defender makes an opposed check of their active defense (Parry or Dodge) vs. each attack made on them until the start of their next turn.
- Any defend roll result of 10 or lower is treated as 10 (same as hero point re-roll floor), ensuring a minimum effective result of 11.
- An attacker must equal or exceed the defender's opposed check result — not merely the normal defense class.

#### Domain Sketch

- Replaces the standard attack with an active defense roll that supersedes the normal static defense class.
- Applies a floor of 10 to all defend rolls, guaranteeing the defender at least a result of 11 against every attack.
- Invariant: Attacker must match the defender's opposed result, not just the base Defense Class = defense + 10.

#### References

**Ref — Crawl**
Source: context/rules/HeroesHandbook-rules__chunk_211.md
Locator: lines 14871-14914
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Crawl"
chunk_index: 211
line_range: "14871-14914"
---

### Defend

### Standard Action

Rather than attacking, you focus on defense. Make an opposed check of your appropriate active defense versus any attack made on you until the start of your next turn. Add 10 to any roll of 10 or less that you make on these checks, just as if you spent a hero point (thus ensuring a minimum roll of 11). The attacker must equal or exceed your opposed check result in order to hit you.
```

---

### disarm

#### Domain Language

- Disarm is a standard action to knock an item out of an opponent's grasp.
- Attack check vs. the defender: −2 penalty for close disarm; −5 for ranged disarm.
- If the attack hits: opposed check of attack's damage rank vs. defender's Strength; win → defender drops the item.
- An unarmed disarm success allows grabbing the dropped item as a free action.
- If the attacker used a melee weapon and loses the opposed check, the defender may immediately counter-disarm as a reaction.

#### Domain Sketch

- Executes a two-check sequence: attack check (to hit) then opposed damage vs. Strength (to disarm).
- Differentiates between unarmed and weapon disarms in both penalties and counter-disarm exposure.
- Invariant: −2 close penalty, −5 ranged penalty applied before the attack check.

#### References

*(Deduplicated — chunk_211 cited by defend.)*

---

### grab

#### Domain Language

- Grab is a standard action to seize and restrain a target: attack check vs. target; on a hit the target resists with the better of Strength or Dodge vs. attacker's Strength or grab effect rank.
- One degree of success: target is restrained (immobile and vulnerable).
- Two or more degrees: target is bound (defenseless, immobile, and impaired).
- The attacker is hindered and vulnerable while maintaining the grab; maintaining is a free action each turn.
- After the grab is established, the attacker may take a standard action to inflict Strength damage on the grabbed target on subsequent turns.
- An existing hold can be improved with another grab action; cumulative degrees of success but losing frees the target.
- The attacker may drag a restrained or bound target: target resists with Strength vs. attacker's Strength; failure means target moves with attacker.
- A grabbed target may attempt to escape as a move action.

#### Domain Sketch

- Runs an attack check then a resistance check to determine hold degree: restrained (1 degree) or bound (2+ degrees).
- Imposes a reciprocal cost: the attacker is hindered and vulnerable while the hold is maintained.
- Enables follow-on damage and dragging as separate subsequent actions after the grab is established.
- Invariant: Maintaining the hold requires a free action each turn; missing the free action releases the target automatically.

#### References

**Ref — Drop An Item**
Source: context/rules/HeroesHandbook-rules__chunk_212.md
Locator: lines 14915-14958
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Drop An Item"
chunk_index: 212
line_range: "14915-14958"
---

### Grab

### Standard Action

You attempt to grab a target. Make an attack check against the target. If successful, the target makes a resistance check against your Strength (or the rank of a grabbing effect) using the better of Strength or Dodge. If you win with one degree of success, the target is restrained (immobile and vulnerable). Two or more degrees leave your opponent bound (defenseless, immobile, and impaired).

You are hindered and vulnerable while grabbing and holding an opponent. You can maintain a successful grab as a free action each turn. Since maintaining a grab is a free action, you can take a standard action to inflict your Strength damage to a grabbed target on subsequent turns.

You can drag a restrained or bound target along with you when you move. The target gets a Strength resistance check against your Strength.

A target can attempt to escape from a grab as a move action.
```

---

### trip

#### Domain Language

- Trip is a standard action (close attack vs. target's Parry at −2 circumstance penalty) to knock a target prone.
- If the attack hits: opposed check of Acrobatics or Athletics (better of each) between attacker and defender.
- Attacker wins → defender falls prone in an adjacent area of the attacker's choice.
- Attacker loses → defender may immediately attempt to counter-trip; if that fails, the attempt ends.

#### Domain Sketch

- Runs a two-check sequence: attack check (−2 vs. Parry) then opposed Acrobatics/Athletics.
- Produces the prone condition on the target, creating tactical disadvantage.
- Invariant: Counter-trip triggers only when the attacker LOSES the opposed check, not when they miss the initial attack.

#### References

**Ref — Standard Action**
Source: context/rules/HeroesHandbook-rules__chunk_214.md
Locator: lines 14999-15043
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Standard Action"
chunk_index: 214
line_range: "14999-15043"
---

### Standard Action (Trip)

You  try  to  trip  or  throw  your  opponent  to  the  ground. Make a close attack check against your opponentâ€™s Parry with a â€"2 circumstance penalty on the check. If the attack succeeds, make an opposed check of your Acrobatics or Athletics against your opponentâ€™s Acrobatics or Athletics.

If you win, the defender is prone in an area adjacent to you of your choice. If you lose, the defender immediately gets another opposed check to try and trip you. If it fails, the trip attempt ends.
```

---

### feint

#### Domain Language

- Feint is a standard action using Deception to mislead an opponent in combat.
- The feinting character makes a Deception check opposed by the better of the target's Deception or Insight.
- Success leaves the target vulnerable against the feinter's next attack until the end of the feinter's next round.

#### Domain Sketch

- Replaces the attack check with a skill check (Deception) to produce the vulnerable condition rather than damage.
- Imposes vulnerable for a limited duration (until end of feinter's next round), enabling a follow-up attack at increased effectiveness.
- Invariant: Feint produces vulnerable on the target, not damage; it is always used to set up a subsequent attack.

#### References

**Ref — Feint**
Source: context/rules/HeroesHandbook-rules__chunk_215.md
Locator: lines 15044-15091
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Feint"
chunk_index: 215
line_range: "15044-15091"
---

### Feint

You can use Deception as a standard action to mislead an opponent in combat. Make a Deception check as a standard action opposed by the better of your targetâ€™s Deception or Insight. If your Deception check succeeds, the target is vulnerable against your next attack, until the end of your next round.

### Slam Attack

When you charge, you can charge right into your target, using your momentum to strengthen your attack. The damage rank for your attack equals your movement speed rank, or your normal damage rank, with a +1 circumstance bonus, whichever is higher. If you move your full speed before you charge, increase your damage by either means by an additional +1 circumstance bonus. The Gamemaster may limit your base slam attack damage by the series power level.

You suffer some of the impact of slamming into a target; make a Toughness resistance check against half the damage rank of your attack (rounded down).
```

---

### slam attack

#### Domain Language

- Slam attack is a maneuver used during a charge, trading personal risk for greater damage.
- Damage rank = max(speed rank, normal damage rank + 1); add +1 more if the attacker moved their full speed before charging.
- The GM may cap base slam damage at the series power level before circumstance modifiers.
- The attacker must make a Toughness resistance check against half the slam attack's damage rank (rounded down).
- Appropriate Immunity effects protect the attacker from slam damage they inflict.

#### Domain Sketch

- Replaces the normal damage rank calculation with a speed-based or boosted formula during charge.
- Imposes a reciprocal Toughness check on the attacker at half the damage rank.
- Invariant: Attacker always risks half the slam damage to themselves; Immunity can negate this.

#### References

**Ref — Lasting Injuries**
Source: context/rules/HeroesHandbook-rules__chunk_216.md
Locator: lines 15092-15151
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Lasting Injuries"
chunk_index: 216
line_range: "15092-15151"
---

Bonuses to Toughness protect against slam attack damage normally. Immunity to slam damage you inflict is a rank 2 Immunity effect, while Immunity to all slam damage is rank 5.

### Surprise Attack

On occasions when your attack catches a target by surprise, the target is vulnerable to your attacks.

### Team Attack

Multiple attackers can attempt to combine their attacks in order to overwhelm an opponentâ€™s resistance. The attacks to be combined must have the same effect and resistance and be within 5 ranks of each other.
```

---

## Tactical Environment

Tactical Environment encompasses the contextual factors that modify combat outcomes without being actions themselves: concealment, cover, surprise, minion rules, and the mechanics for combining attackers (team attack, combined attack). Concealment and cover are passive modifiers applied by the GM based on the scene — both impose circumstance penalties to attack checks, with the important distinction that concealment impairs perception while cover impairs attack trajectory. Surprise reshapes the opening of a conflict, granting the non-surprised side an action window and making the surprised side vulnerable. Minions are a scaling device — the GM uses them to model hordes of weaker opposition with simplified rules that accelerate combat. Team attack and combined attack give multiple combatants a cooperative option to overcome targets whose individual resistance would be too high to crack. Tactical Environment interacts primarily with Attack Resolution (all modifiers flow into attack checks or defense class) and with Damage and Resistance (minion defeat, combined attack damage output).

#### Decisions made

- concealment, cover, surprise, minion, team attack, and combined attack all pass independence and module-fit tests.
- combined attack is kept as a distinct term from team attack because the partition lists it separately; however, decisions made notes that combined attack and team attack refer to the same mechanic; combined attack is the pattern-name while team attack is the rule-name.
- minion is kept here (not its own KA) because it is a rule modifier applied within combat, not an independent character type with lifecycle outside the combat domain.

### concealment

#### Domain Language

- Concealment applies when an attacker cannot clearly perceive their target with an accurate sense.
- Partial concealment (dim lighting, foliage, fog, smoke): −2 circumstance penalty to attack checks.
- Total concealment (complete darkness, heavy smoke): −5 circumstance penalty; attacker must know or guess the approximate area to target at all.
- Concealment is caused by conditions that obstruct perception — not physical obstructions that block attacks (those provide cover).
- Senses countering concealment (e.g., Counters Concealment: Darkness) remove the penalty for the corresponding condition.

#### Domain Sketch

- Applies a circumstance penalty to attack checks based on how well the attacker can perceive the target.
- Can be nullified by specific sense effects (Counters Concealment) that remove the perceptual obstruction.
- Invariant: Partial = −2, Total = −5; area and perception-range attacks bypass concealment penalties entirely.

#### References

**Ref — Recovery**
Source: context/rules/HeroesHandbook-rules__chunk_207.md
Locator: lines 14690-14737
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Recovery"
chunk_index: 207
line_range: "14690-14737"
---

### Concealment

To attack a target, you first have to have some idea of where to aim your attack. If you cannot clearly perceive the target, then it has concealment from you.

Partial Concealment applies a â€"2 circumstance penalty to your attack check.

Total Concealment applies a â€"5 circumstance penalty to your attack check.
```

**Ref — Light And Darkness**
Source: context/rules/HeroesHandbook-rules__chunk_200.md
Locator: lines 14260-14332
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Light And Darkness"
chunk_index: 200
line_range: "14260-14332"
---

### Light And Darkness

Poorly lit areas provide concealment. Characters with Counters Concealment (Darkness) Senses or other appropriate Senses effects can ignore concealment penalties for poor lighting.

### Suffocation

Characters can hold their breath for ten rounds (one minute) plus a number of rounds equal to twice their Stamina. After that time they must make a Fortitude check (DC 10) each round. Failure means the character becomes incapacitated. On the following round the character is dying.

A fall inflicts damage rank 4 plus twice the distance rank fallen, to a maximum of rank 16 damage.
```

---

### cover

#### Domain Language

- Cover applies when a target is behind a physical obstruction that could block or deflect an attack.
- Partial cover (roughly half the target behind obstruction): −2 circumstance penalty to attack checks.
- Total cover (three-quarters or more behind obstruction): −5 circumstance penalty to attack checks.
- Complete cover (target fully behind obstruction): cannot attack the target directly; may target the cover itself.
- Cover grants a circumstance bonus to Dodge resistance checks against area effects equal to its attack penalty, measured from the effect's origin.

#### Domain Sketch

- Applies a circumstance penalty to attack checks based on physical obstruction of the attack path.
- Grants a bonus to Dodge area-effect resistance checks equal to the cover penalty — the same obstruction that blocks attacks also deflects area effects.
- Invariant: Complete cover prevents targeting entirely; the attacker may instead target the obstruction.
- Invariant: Cover bonus to area-effect Dodge checks only applies when the cover is between the target and the effect's origin.

#### References

**Ref — No Cover**
Source: context/rules/HeroesHandbook-rules__chunk_208.md
Locator: lines 14738-14790
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "No Cover"
chunk_index: 208
line_range: "14738-14790"
---

### Cover

Partial Cover applies a â€"2 circumstance penalty to your attack check.

Total  Cover  applies  a  â€"5  circumstance  penalty  to  your  attack check.

If a target is completely behind cover, then you cannot attack that target (although you can attack the cover itself).

Cover also grants a circumstance bonus to Dodge resistance checks against area effects equal to its penalty to attack checks.
```

---

### surprise

#### Domain Language

- Surprise occurs when one or more characters begin a conflict unaware — typically from failing a Perception or similar check.
- If any characters are surprised, the conflict opens with a surprise round; all characters roll initiative normally.
- Surprised characters do not act during the surprise round; they are stunned and vulnerable until the end of the surprise round.
- Non-surprised characters during the surprise round are limited to a standard action and free actions (may exchange standard for a move action).
- Surprise attacks can occur mid-conflict via stealth, concealment, or unusual maneuvers; the target is vulnerable.

#### Domain Sketch

- Opens a special restricted round (surprise round) at the start of a conflict when any participants are surprised.
- Applies stunned + vulnerable to surprised characters for the duration of the surprise round.
- Limits non-surprised characters to standard + free actions in the surprise round (no full round).
- Invariant: Surprised characters cannot act during the surprise round; they recover to normal at the start of the first regular round.

#### References

**Ref — Ch8 Action & Adventure**
Source: context/rules/HeroesHandbook-rules__chunk_196.md
Locator: lines 14083-14127
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Ch8 Action & Adventure"
chunk_index: 196
line_range: "14083-14127"
---

### Surprise

Some conflicts begin with one or more characters caught unaware or surprised. If any characters in the conflict are surprised, then the action begins with a surprise round. Everyone involved in the conflict makes initiative checks as usual. Surprised characters do not act on the surprise round. They are stunned and vulnerable until the next round. Other characters may act, but are limited to a standard action and free actions.
```

**Ref — Lasting Injuries**
Source: context/rules/HeroesHandbook-rules__chunk_216.md
Locator: lines 15092-15151
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Lasting Injuries"
chunk_index: 216
line_range: "15092-15151"
---

### Surprise Attack

On occasions when your attack catches a target by surprise, the target is vulnerable to your attacks. Surprise attacks occur during the surprise round of a conflict and may also occur as a result of stealth or concealment, allowing you to sneak up on a target.

### Team Attack

Multiple attackers can attempt to combine their attacks in order to overwhelm an opponentâ€™s resistance. The attacks to be combined must have the same effect and resistance and be within 5 ranks of each other.

The attackers must all delay to the same point in the initiative order (that of the slowest attacker). Each attacker makes an attack check against the targetâ€™s defense.

Take the largest effect rank of the attacks that hit and count the combined degrees of success for the other attacks: one degree provides a +2 circumstance bonus to the rank of the main attack, three or more provides a +5 circumstance bonus. Unlike a normal team check, degrees of failure do not reduce success.
```

---

### team attack

#### Domain Language

- Team attack allows multiple attackers to combine their efforts to overwhelm a single target's resistance.
- All attacks must share the same effect type and resistance defense, and be within 5 ranks of each other.
- Participants must all delay to the same initiative slot (the slowest attacker's position).
- Each attacker makes their own attack check; effects not requiring attack checks automatically count as one degree of success.
- The main attack uses the largest effect rank; each additional attack that hits contributes: 1 degree → +2 circumstance bonus to main rank; 3+ degrees → +5 bonus.
- Misses in a team attack have no effect and impose no penalties.

#### Domain Sketch

- Coordinates multiple attackers at the same initiative point to combine compatible attack effects.
- Scales the combined effect rank upward based on how many contributing attacks land.
- Invariant: Contributing attacks must share the same effect type, resistance defense, and be within 5 ranks.
- Invariant: Misses contribute nothing; only hits add to the combined result.

#### References

*(Deduplicated — chunk_216 cited by surprise.)*

---

### combined attack

#### Domain Language

- Combined attack is the general pattern of multiple combatants coordinating compatible attacks against a single target (the team attack mechanic).
- Contributing attacks must share the same effect type and resistance defense and be within 5 ranks of each other before they can be combined.
- The result is a single composite effect rank boosted by the combined contributions of all participating hits.

#### Domain Sketch

- Describes the coordination pattern that produces a single composite effect rank from multiple compatible attacks.
- Enforces the compatibility constraint (same effect + resistance + within 5 ranks) before allowing combination.
- Invariant: The largest individual effect rank is the base; additional contributing hits add circumstance bonuses (not more base ranks).

#### References

*(Deduplicated — chunk_216 cited by surprise.)*

---

### minion

#### Domain Language

- A minion is a minor character subject to special rules making them easier to defeat than full characters.
- Minions cannot score critical hits against non-minions.
- Non-minions may make attack checks against minions as routine checks (guaranteed hit with attack bonus ≥ 0).
- If a minion fails any resistance check, they suffer the worst degree of the effect regardless of actual degree of failure.
- Certain advantages (e.g., Takedown) are specifically more effective against or designed for use against minions.
- The GM may roll a single initiative check for an entire minion group.

#### Domain Sketch

- Simplifies resolution by compressing all resistance failures to the worst possible outcome.
- Enables routine-check attacks against them, removing attack randomness when facing masses of minions.
- Invariant: Any resistance failure → worst degree (e.g., any Toughness failure → incapacitated).
- Invariant: Minions cannot produce critical hits against non-minions regardless of die result.

#### References

*(Deduplicated — chunk_208 cited by cover.)*

---

## Hazards and Objects

Hazards and Objects covers the non-combat-opponent sources of harm in the game world. Hazards are environmental dangers — falling, suffocation, heat, cold, vacuum, poison, disease, radiation — each governed by a Fortitude (or other) resistance check sequence that escalates conditions from fatigued through dying. Falling has its own damage formula (4 + 2× distance rank, capped at 16). Suffocation uses a breath-holding timer then a per-round Fortitude check. Damaging objects extends the combat system to inanimate targets: objects have Material Toughness values, cannot be dazed or staggered, and require either finishing attacks or repair. This KA interacts with Damage and Resistance (damage rank, Toughness check) and with Tactical Environment (hazards can affect the entire environment). The module owns the combat-facing rules for how hazards work in play.

#### Decisions made

- hazard, falling, suffocation, damaging objects, and Material Toughness pass both tests.
- heat, cold, starvation, thirst, poison, disease, and radiation are sub-types of hazard, covered by the hazard term; no separate core terms are needed.
- vacuum is similarly a hazard sub-type, not a standalone term.

### hazard

#### Domain Language

- Hazards are environmental dangers that harm characters independently of opponent attacks.
- Each hazard uses a resistance check (typically Fortitude) with DC = 10 + rank or a fixed DC; repeated failures escalate: fatigued → exhausted → incapacitated → dying.
- Hazard types include heat/cold, starvation/thirst, suffocation, vacuum, poison, disease, radiation, and falling.
- Immunity effects can negate specific hazard types entirely.
- Hazards may have their own initiative ranks in timed scenarios.

#### Domain Sketch

- Represents an environmental threat that fires resistance checks on a schedule independent of attacker turns.
- Escalates character conditions predictably from fatigued through dying on repeated failures.
- Can participate in initiative (with its own rank) in timed scenarios.
- Invariant: Immunity effect completely negates the corresponding hazard type.

#### References

**Ref — Challenges And Initiative**
Source: context/rules/HeroesHandbook-rules__chunk_199.md
Locator: lines 14219-14259
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Challenges And Initiative"
chunk_index: 199
line_range: "14219-14259"
---

### Environmental Hazards

Not all of the hazards heroes face come from supervillains. Sometimes the environment itself can be a danger. This section details some of the hazards heroes may face.

### Challenges And Initiative

With other challenges, it does matter who goes first, particularly when the challenge is timed in some fashion. The same may be true of other traps or hazards, which can have initiative ranks of their own.
```

**Ref — Light And Darkness**
Source: context/rules/HeroesHandbook-rules__chunk_200.md
Locator: lines 14260-14332
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Light And Darkness"
chunk_index: 200
line_range: "14260-14332"
---

### Heat And Cold

Characters in hot or cold conditions must make Fortitude checks (DC 10, +1 per previous check) to avoid becoming fatigued. Fatigued characters who fail a check become exhausted, then incapacitated, at which point the characterâ€™s condition becomes dying after another failed Fortitude check.

### Starvation And Thirst

Heroes can go without water for a day. After this, they need to make a Fortitude check (DC 10, +1 per previous check) each hour to avoid a level of fatigue.

### Suffocation

Characters can hold their breath for ten rounds plus a number of rounds equal to twice their Stamina. After that time they must make a Fortitude check (DC 10) each round. Failure means the character becomes incapacitated. On the following round the character is dying.

### Poison

Poisons generally have one of several effects: Affliction, Damage, or Weaken. Heroes generally resist poisons with Fortitude.

### Disease

When heroes come into contact with a disease they must make a Fortitude check (DC 10 + the diseaseâ€™s rank) to avoid becoming infected.

### Radiation

The Gamemaster can treat radiation exposure like a disease. The victim makes an initial Fortitude check and an additional check each day.
```

**Ref — Radiation Example**
Source: context/rules/HeroesHandbook-rules__chunk_201.md
Locator: lines 14333-14385
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Radiation Example"
chunk_index: 201
line_range: "14333-14385"
---

Radiation sickness is typically a Weaken Stamina effect. At the GMâ€™s discretion, radiation exposure can lead to other effects, such as damage to a heroâ€™s power ranks.

Fire Example: Torch (1), Campfire (2), Blowtorch (4), Flame thrower (6), Burning jet fuel/napalm (8), Chemical accelerants and fire powers (10+).
```

**Ref — Vacuum**
Source: context/rules/HeroesHandbook-rules__chunk_202.md
Locator: lines 14386-14434
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Vacuum"
chunk_index: 202
line_range: "14386-14434"
---

### Vacuum

The primary hazards of the vacuum of space are lack of air and exposure to unfiltered ionizing radiation.

On the third round of exposure to vacuum, a character must succeed on a Fortitude check (DC 20) each round or suffer from aeroembolism. A failed check means the creature is stunned.

Heroes able to ignore the effects of deep space must have Immunity to suffocation, vacuum, and radiation, at a minimum.
```

---

### falling

#### Domain Language

- Falling inflicts damage rank = 4 + (2 × distance rank fallen), capped at rank 16.
- Characters with Acrobatics can fall greater distances without injury.
- Falling onto a dangerous surface may inflict additional damage at the GM's discretion.
- Catching a falling character or object requires a Dexterity check (DC 5); the catcher subtracts their Strength rank from falling damage rank — both catcher and caught suffer any remaining damage.
- A power (Flight, Move Object) may substitute its rank for Strength when catching, at the GM's discretion.

#### Domain Sketch

- Translates fall distance into damage rank via a fixed formula and applies it as a Toughness check.
- Provides a catching intervention path (Dexterity DC 5) that partially absorbs damage for both the catcher and the falling target.
- Invariant: Maximum falling damage rank is 16 regardless of distance rank.

#### References

*(Deduplicated — chunk_200 cited by hazard.)*

---

### suffocation

#### Domain Language

- Characters may hold their breath for 10 rounds + (2 × Stamina rank) rounds before needing to check.
- After the limit, Fortitude check (DC 10, +1 per previous success) each round; failure → incapacitated.
- The following round after failure, the character becomes dying and cannot stabilize until able to breathe.
- Holding breath in vacuum additionally risks lung damage: Fortitude DC 15 (+1 per round); success causes loss of one Stamina rank; failure begins suffocation.
- Immunity to Suffocation removes this hazard entirely.

#### Domain Sketch

- Provides a grace period (breath-holding limit) before the Fortitude check sequence begins.
- Blocks stabilization from dying while the cause (no breathable atmosphere) persists.
- Invariant: Cannot stabilize while suffocating; removing the cause is the prerequisite for recovery.

#### References

*(Deduplicated — chunk_200, chunk_202 both cited by hazard.)*

---

### damaging objects

#### Domain Language

- Objects (targets lacking a Stamina rank) take damage similarly to characters but dazed and staggered results have no practical effect on inanimate targets.
- Inanimate objects are defenseless by definition and subject to finishing attacks: attacker may choose a routine check (auto-hit) or roll normally (auto-crit on any hit for +5 DC).
- Attacking an object held or worn by a character is a smash action (attack vs. character's defense at −5 if held; damage applied to the object).
- Two degrees of failure on the object's Toughness check causes a break; three or more degrees destroys the object.
- Objects cannot recover on their own — they must be repaired (Technology skill).

#### Domain Sketch

- Applies the damage system to inanimate targets with a defenseless-by-definition rule that simplifies resolution.
- Maps Toughness failure degrees to physical states: 2 degrees → break, 3+ degrees → destroyed.
- Invariant: Objects cannot self-recover; they require external repair via Technology skill.

#### References

**Ref — Damaging Objects**
Source: context/rules/HeroesHandbook-rules__chunk_206.md
Locator: lines 14631-14689
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Damaging Objects"
chunk_index: 206
line_range: "14631-14689"
---

### Damaging Objects

Objects (targets lacking a Stamina rank) take damage similar to other targets. Dazed and staggered results have no real effect on inanimate targets.

Inanimate objects are defenseless by definition and therefore subject to finishing attacks: you can choose between making your attack as a routine check or, if you make the attack check normally, gaining an automatic critical hit if your attack hits, for a +5 bonus to effect.

Attacking an object held or worn by another character is a smash action.

If an attackerâ€™s intention is to bend, break or destroy an object, then two degrees of failure on the Toughness check results in a break while three or more degrees of failure means the object is destroyed.

Objects, having no Stamina, do not recover from damage unless they have an effect like Regeneration. Instead, they must be repaired.
```

---

### Material Toughness

#### Domain Language

- Material Toughness is the Toughness rank of a common material at approximately one inch (distance rank −7) of thickness.
- Each doubling of thickness adds +1 Toughness; each halving subtracts −1.
- Example ranks: paper/soil 0, glass/ice/rope 1, wood 3, stone 5, iron 7, reinforced concrete 8, steel 9, titanium 15, super-alloys 20+.
- Equipment has Toughness based on its material; devices have base Toughness = total power points ÷ 5 (round down, minimum 1).

#### Domain Sketch

- Provides a reference table mapping material type and thickness to a Toughness rank for use in object damage calculations.
- Scales linearly with thickness (±1 per doubling/halving).
- Invariant: The listed ranks apply at approximately one inch; thickness scaling is applied before any circumstance modifier.

#### References

*(Deduplicated — chunk_206 cited by damaging objects.)*

---

## Hero Resources

Hero Resources are the meta-level economy that gives heroes the ability to transcend normal limits. Hero points are a narrative currency earned through complications and heroic play, spent as reactions to re-roll dice, edit scenes, gain temporary advantages, get inspiration, counter effects, or instantly recover conditions. Extra effort is a within-turn free action that sacrifices the next turn's condition to gain a power boost now — an additional action, a skill bonus, a temporary power rank increase, or a power stunt. Power stunt is the specific extra effort option that instantiates a temporary Alternate Effect of an existing power. All three work together: hero points are the safety net that removes extra effort's fatigue cost, and power stunt is extra effort's most tactically complex option. Hero Resources are not bounded by power level — their effects can exceed what normal powers allow — and they apply as a layer on top of all other combat mechanics, never replacing them.

#### Decisions made

- hero point, extra effort, and power stunt pass both tests — they are fully independent concepts fundamental to the combat loop.
- hero point's non-combat spend types (Edit Scene, Inspiration) are still part of hero point as defined here — the concept is defined whole.
- power stunt is kept as its own term because the partition lists it explicitly and it has its own rules (scene duration, permanent effects exclusion, critical hit free variant).

### hero point

#### Domain Language

- Players begin each game session with 1 hero point; unspent hero points do not carry over between sessions.
- Spending a hero point is a reaction (takes no time); a player may spend as many as they have in one turn.
- Improve Roll: re-roll any die roll before GM announces outcome; take the better; on a re-roll result of 1–10, add 10 (re-roll always yields 11–20).
- Edit Scene: add or change a scene detail with GM approval; cannot undo events that have already occurred.
- Heroic Feat: gain one rank of an advantage (except fortune advantages) until end of next turn; prerequisites must be met.
- Inspiration: receive a hint, clue, or direction from the GM.
- Instant Counter: attempt to counter an effect used against the hero as a reaction.
- Recover: immediately remove a dazed, fatigued, or stunned condition; or convert exhausted to fatigued.
- Heroes earn additional hero points from complications, acts of heroism, and roleplaying.

#### Domain Sketch

- Spends as a reaction (zero action cost) providing one of eight distinct rescue or amplification effects.
- Re-roll floor rule ensures no re-roll produces below 11, making hero point rolls statistically favorable.
- Invariant: Unspent hero points reset to 1 at the start of each new session — never carry over.
- Invariant: May be spent multiple times in one turn (limited only by number held).

#### References

**Ref — Extra Effort**
Source: context/rules/HeroesHandbook-rules__chunk_019.md
Locator: lines 1426-1475
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch1 The Basics"
topic: "Extra Effort"
chunk_index: 19
line_range: "1426-1475"
---

### Hero Points

Players start each game session with 1 hero point. Unspent hero points donâ€™t carry over to the next adventure.

### Cost Of Extra Effort

At the start of the turn immediately after using extra effort, the hero becomes fatigued. If you spend a hero point at the start of the turn following the extra effort to remove the fatigue, the hero suffers no adverse effects. In essence, spending a hero point lets you use extra effort without suffering fatigue.
```

**Ref — Using Hero Points**
Source: context/rules/HeroesHandbook-rules__chunk_020.md
Locator: lines 1476-1515
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch1 The Basics"
topic: "Using Hero Points"
chunk_index: 20
line_range: "1476-1515"
---

### Using Hero Points

Unless otherwise noted, spending a hero point is a reaction, taking no time, and you can spend as many hero points as you have.

### Edit Scene

You can â€œeditâ€ a scene to grant your hero an advantage.

### Heroic Feat

You can spend a hero point to gain the benefits of one rank of an advantage you donâ€™t already have until the end of your next turn.

### Hero Points

Players start each game session with 1 hero point. Unspent hero points donâ€™t carry over to the next adventure; the heroes start out with 1 point again.
```

**Ref — Improve Roll**
Source: context/rules/HeroesHandbook-rules__chunk_021.md
Locator: lines 1516-1555
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch1 The Basics"
topic: "Improve Roll"
chunk_index: 21
line_range: "1516-1555"
---

### Improve Roll

One hero point allows you to re-roll any die roll you make and take the better of the two rolls. On a result of 1 through 10 on the second roll, add 10 to the result (so the re-roll is always a result of 11-20). You must spend the hero point to improve a roll before the GM announces the outcome.

### Inspiration

You can spend a hero point to get sudden inspiration in the form of a hint, clue, or bit of help from the GM.

### Instant Counter

You can spend a hero point to attempt to counter an effect used against you as a reaction.

### Recover

You can spend a hero point to immediately remove a dazed, fatigued, or stunned condition, without taking an action. Spending a hero point to recover also lets you convert an exhausted condition into a fatigued condition.

### Earning Hero Points

Heroes get hero points from complications, acts of heroism, and roleplaying.
```

---

### extra effort

#### Domain Language

- Extra effort is a free action declared by the player, limited to once per turn.
- Choose one benefit: additional standard action; +2 circumstance bonus on one check (or upgrade existing +2 to +5); +1 rank to a power effect until start of next turn; power stunt (temporary Alternate Effect for the scene); additional resistance check against an ongoing effect; retry a failed effect; +1 speed rank until next turn; +1 Strength rank until next turn.
- Extra effort benefits are not limited by power level.
- Cost: at the start of the immediately following turn, the hero becomes fatigued; fatigued → exhausted on subsequent use; exhausted → incapacitated.
- Spending a hero point at the start of the following turn removes the fatigue cost entirely.

#### Domain Sketch

- Trades next-turn condition degradation for an immediate within-turn benefit chosen from eight options.
- Deferred cost fires at the start of the NEXT turn — not immediately — giving the hero a full benefit turn before the penalty.
- Invariant: Once per turn; fatigue escalates each time (normal → fatigued → exhausted → incapacitated).
- Invariant: Benefits are not limited by power level — extra effort can temporarily exceed PL caps.

#### References

*(Deduplicated — chunk_019, chunk_020 both cited by hero point.)*

---

### power stunt

#### Domain Language

- A power stunt uses extra effort to temporarily gain an Alternate Effect of one of the hero's existing powers.
- The stunt lasts until the end of the scene or until the effect's normal duration expires, whichever comes first.
- Permanent effects cannot be used as the basis for a power stunt.
- A power stunt gained via a critical hit's Alternate Effect option costs no fatigue.

#### Domain Sketch

- Instantiates a temporary Alternate Effect of an existing power for the duration of the scene.
- Costs extra effort's deferred fatigue unless obtained via critical hit's Alternate Effect option.
- Invariant: The base power must already exist on the character's sheet.
- Invariant: Permanent effects cannot be used as the basis; scene-duration cap applies.

#### References

*(Deduplicated — chunk_019 cited by hero point.)*

---

# Boundary Domain

## condition

Owned by: Check Resolution

#### Domain Language

- Conditions (dazed, staggered, stunned, vulnerable, defenseless, incapacitated, dying, prone, hindered, impaired, etc.) are game-state modifiers imposed by combat outcomes, power effects, and hazards.
- Combat causes, references, and escalates conditions; their authoritative definitions and supersession chains live in Check Resolution.
- The dying and incapacitated conditions are triggered by Toughness resistance check outcomes defined in Combat, but their modifier bundles are owned by Check Resolution.

#### Domain Sketch

- Combat defines WHEN conditions are imposed (on specific damage degrees, on grab success, on trip success) but does NOT define WHAT the conditions do.
- The condition's modifier bundle (action restrictions, defense reductions, speed changes) is enforced by the consuming system at the point of use — Combat enforces action limits mid-turn; Check Resolution enforces check penalties on each check.
- Invariant: A condition's definition and supersession chain is owned by Check Resolution; Combat's role is trigger-only.

#### References

**Ref — Reactions**
Source: context/rules/HeroesHandbook-rules__chunk_017.md
Locator: lines 1238-1344
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch1 The Basics"
topic: "Reactions"
chunk_index: 17
line_range: "1238-1344"
---

### Conditions

Heroes run into their share of difficulties in their work. One way MUTANTS & MASTERMINDS measures this is with different conditions. They are shorthand for the different game modifiers imposed by things from power effects to injuries or fatigue.

â€¢  Dazed: limited to free actions and a single standard action per turn. Stunned supersedes dazed.
â€¢  Stunned: cannot take any actions, including free actions.
â€¢  Vulnerable: halving their active defenses (round up the final value). Defenseless supersedes vulnerable.
â€¢  Defenseless: active defense bonuses of 0; attackers may use routine checks.
```

**Ref — Critical Misses**
Source: context/rules/HeroesHandbook-rules__chunk_203.md
Locator: lines 14435-14489
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Critical Misses"
chunk_index: 203
line_range: "14435-14489"
---

Failure (two degrees): The target is dazed until the end of their next turn.
Failure (three degrees): The target is staggered.
Failure (four degrees): The target is incapacitated.
```

---

## Toughness

Owned by: Character Construction

#### Domain Language

- Toughness is the physical resistance defense stat used as the basis for all Toughness resistance checks against Damage effects.
- Its rank is set during character construction; temporary −1 penalties from failed Toughness checks accumulate in combat and recover with rest.

#### Domain Sketch

- Character Construction defines the Toughness rank; Combat applies temporary penalties to that rank through the damage resistance check sequence.
- Invariant: Base Toughness rank is set at construction; combat only modifies via temporary cumulative penalties.

#### References

**Ref — Critical Misses**
Source: context/rules/HeroesHandbook-rules__chunk_203.md
Locator: lines 14435-14489
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Critical Misses"
chunk_index: 203
line_range: "14435-14489"
---

### Damage Resistance Check

Toughness vs. [Damage rank + 15]
```

---

## Dodge

Owned by: Character Construction

#### Domain Language

- Dodge is the active defense providing the defense class against ranged attacks (Dodge + 10).
- Combat halves Dodge rank (round up) when a character is vulnerable; reduces it to 0 when defenseless.

#### Domain Sketch

- Character Construction defines Dodge rank; Combat reads and temporarily modifies it when applying vulnerable or defenseless conditions.
- Invariant: Base Dodge is set at construction; Combat applies halving or zeroing only in response to specific conditions.

#### References

**Ref — No Cover**
Source: context/rules/HeroesHandbook-rules__chunk_208.md
Locator: lines 14738-14790
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "No Cover"
chunk_index: 208
line_range: "14738-14790"
---

Most attacks target your active defenses, Dodge and Parry: close attacks target Parry while ranged attacks target Dodge.

Defense Class = defense + 10
```

**Ref — Vulnerable And Defenseless**
Source: context/rules/HeroesHandbook-rules__chunk_209.md
Locator: lines 14791-14830
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Vulnerable And Defenseless"
chunk_index: 209
line_range: "14791-14830"
---

When you are vulnerable, your active defense ranks are halved (round up fractions).
When you are defenseless, your active defense ranks are reduced to zero.
```

---

## Parry

Owned by: Character Construction

#### Domain Language

- Parry is the active defense providing the defense class against close attacks (Parry + 10).
- Combat halves Parry rank (round up) when a character is vulnerable; reduces it to 0 when defenseless.

#### Domain Sketch

- Character Construction defines Parry rank; Combat reads and temporarily modifies it when applying vulnerable or defenseless conditions.
- Invariant: Base Parry is set at construction; Combat applies halving or zeroing only in response to specific conditions.

#### References

**Ref — No Cover**
Source: context/rules/HeroesHandbook-rules__chunk_208.md
Locator: lines 14738-14790
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "No Cover"
chunk_index: 208
line_range: "14738-14790"
---

Most attacks target your active defenses, Dodge and Parry: close attacks target Parry while ranged attacks target Dodge.
```

**Ref — Vulnerable And Defenseless**
Source: context/rules/HeroesHandbook-rules__chunk_209.md
Locator: lines 14791-14830
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Vulnerable And Defenseless"
chunk_index: 209
line_range: "14791-14830"
---

When you are vulnerable, your active defense ranks are halved. So the hero with Parry 11 and Dodge 9 would have ranks of Parry 6 and Dodge 5 while vulnerable.
```

---

## Fortitude

Owned by: Character Construction

#### Domain Language

- Fortitude is the physical resistance defense used for hazard checks (heat, cold, suffocation, disease, poison, vacuum, radiation) and ongoing physical effect resistance checks.

#### Domain Sketch

- Character Construction defines the Fortitude rank; Combat uses it as the resistance defense in all hazard check sequences and for physical ongoing effects.
- Invariant: Fortitude rank is set at construction; Combat does not modify the base rank.

#### References

**Ref — Light And Darkness**
Source: context/rules/HeroesHandbook-rules__chunk_200.md
Locator: lines 14260-14332
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Light And Darkness"
chunk_index: 200
line_range: "14260-14332"
---

Characters in hot or cold conditions must make Fortitude checks (DC 10, +1 per previous check) to avoid becoming fatigued.
```

**Ref — Vacuum**
Source: context/rules/HeroesHandbook-rules__chunk_202.md
Locator: lines 14386-14434
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Vacuum"
chunk_index: 202
line_range: "14386-14434"
---

On the third round of exposure to vacuum, a character must succeed on a Fortitude check (DC 20) each round.
```

---

## Strength

Owned by: Character Construction

#### Domain Language

- Strength provides a built-in close-range Damage effect; its rank adds to Damage rank for Strength-based weapons.
- Strength is used in grab checks (attacker vs. target Strength or Dodge), disarm opposed checks (damage vs. Strength), trip opposed checks (Acrobatics/Athletics vs. Acrobatics/Athletics), and dragging during grab.

#### Domain Sketch

- Character Construction defines Strength rank; Combat uses it as both a Damage source and a check modifier in grab, disarm, drag, and falling-catch interactions.
- Invariant: Strength rank is defined at construction; extra effort can temporarily increase it by +1 rank.

#### References

**Ref — Critical Misses**
Source: context/rules/HeroesHandbook-rules__chunk_203.md
Locator: lines 14435-14489
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Critical Misses"
chunk_index: 203
line_range: "14435-14489"
---

### Strength And Damage

Strength provides a â€œbuilt-inâ€ Damage effect. You add your Strength and Damage ranks together when determining the rank of the attack.
```

**Ref — Drop An Item**
Source: context/rules/HeroesHandbook-rules__chunk_212.md
Locator: lines 14915-14958
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Drop An Item"
chunk_index: 212
line_range: "14915-14958"
---

### Grab

The target makes a resistance check against your Strength (or the rank of a grabbing effect) using the better of Strength or Dodge.

You can drag a restrained or bound target. The target gets a Strength resistance check against your Strength.
```

---

## power effect

Owned by: Power

#### Domain Language

- A power effect's rank determines the resistance DC (effect rank + 10 for most; Damage uses effect rank + 15).
- Combat resolves power effects when activated as attacks; area and perception-range effects bypass attack checks and automatically affect targets.

#### Domain Sketch

- The Power module defines each effect's rank, action, range, duration, and resistance type; Combat reads these properties to resolve the attack check (if any) and resistance check.
- Invariant: Effect rank + 10 is the standard resistance DC; Damage effects use effect rank + 15.

#### References

**Ref — Conflicts**
Source: context/rules/HeroesHandbook-rules__chunk_202.md
Locator: lines 14386-14434
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Vacuum"
chunk_index: 202
line_range: "14386-14434"
---

### Attacks

An attack check represents an attempt to hit a target with an attack.

Attack Check = d20 + attack bonus vs. defense class
```

**Ref — Vulnerable And Defenseless**
Source: context/rules/HeroesHandbook-rules__chunk_209.md
Locator: lines 14791-14830
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Vulnerable And Defenseless"
chunk_index: 209
line_range: "14791-14830"
---

### Resistance

A successful attack has some effect on the target. Typically this is an effect from the Powers chapter. The effect has a rank, used to determine a difficulty class for the targetâ€™s resistance check.

Resistance Difficulty = effect rank + 10
```

---

## advantage

Owned by: Advantages

#### Domain Language

- Combat advantages (Improved Initiative, Improved Critical, Takedown, Move-by Action, etc.) modify combat mechanics; their definitions and prerequisites are owned by the Advantages module.
- Heroic Feat (a hero point spend) grants temporary access to one rank of an advantage for one turn.

#### Domain Sketch

- The Advantages module defines each advantage's prerequisites, rank costs, and behavioral descriptions; Combat applies the mechanical modifications those advantages specify (e.g., Improved Critical extends threat range, Takedown enables additional attacks on minion defeat).
- Invariant: Advantage definitions and prerequisites are read-only from Combat's perspective; only behavioral modifications are enforced here.

#### References

**Ref — Ch8 Action & Adventure**
Source: context/rules/HeroesHandbook-rules__chunk_196.md
Locator: lines 14083-14127
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Ch8 Action & Adventure"
chunk_index: 196
line_range: "14083-14127"
---

### Initiative

Many characters have advantages or powers that modify their initiative, such as Improved Initiative.
```

**Ref — Using Hero Points**
Source: context/rules/HeroesHandbook-rules__chunk_020.md
Locator: lines 1476-1515
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch8 Action & Adventure"
topic: "Using Hero Points"
chunk_index: 20
line_range: "1476-1515"
---

### Heroic Feat

You can spend a hero point to gain the benefits of one rank of an advantage you donâ€™t already have until the end of your next turn.
```
