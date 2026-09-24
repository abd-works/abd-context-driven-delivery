---
state: key-abstractions
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

## CHAPTER 8: ACTION & ADVENTURE



MUTANTS & MASTERMINDS

DELUXE HEROâ€™S HANDBOOK


BAM! POW! Like the comics, MUTANTS & MASTERMINDS is about action, so this chapter looks at the flow of the game and how heroes accomplish their amazing feats, ranging from last-minute rescues and brilliant investigations to thrilling battles against the forces of evil.

The chapter starts out with a look at action rounds, used to measure time when seconds count, then moves on to the different challenges heroes face, followed by handling conflicts like super-powered battles. The chapter concludes with information on the potential consequences, including various conditions imposed on heroes and the hazards of the environment around them. This is followed by handling conflicts like super-powered battles, including special actions, consequences of damage, and recovery from it.

### Action Rounds

The action round (or simply round) is how MUTANTS & MASTERMINDS breaks down time when things like who goes first and how much each character can accomplish are important. A round represents about six seconds of time in the game world.

During a round, each character involved takes a turn, which is that characterâ€™s opportunity to do something. A character has an allotment of actions, used during that characterâ€™s turn. Players decide what their characters do on their turns, while the GM handles everyone elseâ€™s turn.

### Initiative

The  order  in  which  characters  take  their  turns  is  determined  by  initiative.  Base  initiative  bonus  is  equal  to the  characterâ€™s  Agility  rank.  Many  characters  have  advantages or powers that modify their initiative, such as
Improved Initiative. At the start of a conflict, roll an initiative check for each character:

d20 + initiative modifier

The  initiative  check  determines  what  order  characters act in, counting down from highest check result to lowest. Usually, the GM writes the names of the characters down in initiative order to move quickly from one character to the next each round. You can also have all of the charactersâ€™ names listed on index cards you can reshuffle to fit the initiative order. If two characters have the same initiative result, they act in order of highest Dodge bonus first, then highest Agility and highest Awareness. If there is still a tie, each tied player should roll a die, with the highest roll going first. The GM may roll just once for an entire group of minions, giving them all the same initiative.

If characters enter a conflict after itâ€™s begun, they roll initiative when they join-in and act when their turn comes up in the existing order.

### Surprise

Some conflicts begin with one or more characters caught unaware or surprised. This is typically because the character did not succeed on a Perception or other check and

was therefore caught off-guard. Some characters on a side can be surprised while others are not.

If any characters in the conflict are surprised, then the action  begins  with  a  surprise  round.  Everyone  involved  in the conflict makes initiative checks as usual. Surprised characters do not act on the surprise round. They are stunned and vulnerable until the next round (see Conditions in The
Basics chapter). Other characters may act, but are limited to a standard action and free actions, although they may exchange their standard action for a move action, as usual.

### Action Types

The four types of actions characters can take are standard, move, free, and reaction. In a normal round, you can perform a standard action and a move action, or two move actions. You can also perform as many free and reactions actions as your GM allows.

Some situations (like the surprise round) and conditions (like  being  dazed)  limit  the  actions  you  can  take  during your turn.
```

---

### action round

#### Domain Language

- An action round (round) is a six-second segment of in-game time used when turn order and action economy matter.
- During a round each character involved takes one turn — that character's opportunity to act.
- A round represents approximately one page of a comic book — just long enough for the group to each do one thing.
- Rounds structure conflicts, challenges, and any situation where sequence and action limits are important.

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

## CHAPTER 8: ACTION & ADVENTURE

MUTANTS & MASTERMINDS

DELUXE HEROâ€™S HANDBOOK

BAM! POW! Like the comics, MUTANTS & MASTERMINDS is about action, so this chapter looks at the flow of the game and how heroes accomplish their amazing feats, ranging from last-minute rescues and brilliant investigations to thrilling battles against the forces of evil.

The chapter starts out with a look at action rounds, used to measure time when seconds count, then moves on to the different challenges heroes face, followed by handling conflicts like super-powered battles. The chapter concludes with information on the potential consequences, including various conditions imposed on heroes and the hazards of the environment around them.

### Action Rounds

The action round (or simply round) is how MUTANTS & MASTERMINDS breaks down time when things like who goes first and how much each character can accomplish are important. A round represents about six seconds of time in the game world.

During a round, each character involved takes a turn, which is that characterâ€™s opportunity to do something. A character has an allotment of actions, used during that characterâ€™s turn. Players decide what their characters do on their turns, while the GM handles everyone elseâ€™s turn.
```

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

An  attack  check  determines  whether  or  not  you  hit  an opponent  in  combat  with  an  attack.  It  is  a  d20  roll  plus your bonus with that particular attack, usually based off of  Fighting  or  Dexterity  and  appropriate  modifiers,  like the Close and Ranged Combat skills. The difficulty is your targetâ€™s  defense  class:  Parry  for  close  attacks,  Dodge  for ranged attacks. Certain attacks may target other defenses.
If  you  equal  or  exceed  your  targetâ€™s  defense  class  result, your attack hits. Otherwise, you miss.

Attack Check = d20 + attack bonus + modifiers vs. defense class

A natural 20 on an attack check (where the die comes up 20) always hits and may be a critical hit (see Critical Hits in the Action & Adventure chapter). A natural 1 on an attack check (where the die comes up 1) always misses, regardless of the check total.

### Resistance Checks

A  resistance  check  is  an  attempt  to  resist  different  effects, ranging from damage and injury to traps, poisons, and various power effects. A resistance check is a d20 roll + the appropriate defense (typically Dodge, Fortitude, Toughness, or Will).

Resistance Check = d20 + defense bonus + modifiers vs. hazardâ€™s DC (generally 10 + rank)

The difficulty class is based on the strength of the hazard, such as the rank of an effect or the strength of a disease or poison, typically that value plus 10 (like a routine check). Resistance checks may be graded, with different results at different degrees.

### The Action Round

When things really start happening in a MUTANTS & MASTERMINDS game, time is broken down into six-second segments called rounds (sometimes â€œaction roundsâ€). A round isnâ€™t very much time. Think of it like a page in a comic book, just long enough to go around the table once, with each hero  doing  something.  Each  characterâ€™s  portion  of  the round is called their turn.

The things you can do on your turn are broken up into actions. There are standard actions, move actions, free actions, and reactions. During a round you can take a standard and a move action (or substitute an additional move action for your standard action) along with as many free actions as you wish and as many reactions as are called for.
```

---

### turn

#### Domain Language

- A turn is a character's portion of an action round — the window in which that character declares and resolves their actions.
- When a character's turn begins, effects that last "until the start of your next turn" end.
- When a character's turn ends, effects that last "until the end of your turn" end and required resistance checks for ongoing effects are made.
- A character informs the GM when their turn is finished so the next character in initiative order may act.

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

### Standard Action

A  standard  action  allows  you  to  do  something. You  can make  an  attack,  use  a  skill,  advantage,  or  power,  or  perform  other  similar  actions.  During  a  combat  round,  you can take a standard action and a move action.

### Move Action

A move action allows you to move your speed or perform an action taking a similar amount of time, such as draw or stow a weapon or other object, stand up, pick up an object, or perform some equivalent action (see the Actions in Combat Table).

You can take a move action in place of a standard action. For example, rather than moving your speed and attacking you can stand up and move your speed (two move actions), draw a weapon and climb (two move actions), or pick up an object and stow it (two move actions). You can also make a DC 15 Athletics check as a free action to run faster: one or more degree of success increases your ground speed rank by +1 for one round.

### Free Action

Free actions consume very little time and, over the span of the round, their impact is so minor they are considered to take no real time at all. You can perform one or more free actions  while  taking  another  action.  For  instance,  dropping an object, dropping to a prone position, speaking a sentence or two, and ceasing to concentrate on maintaining a power are all free actions.

### Reaction

A  reaction  is  something  that  happens  in  response  to something  else,  like  a  reflex.  Like  free  actions,  reactions take so little time theyâ€™re considered free. The difference between  the  two  is  a  free  action  is  a  conscious  choice made  on  the  characterâ€™s  turn  to  act.  A  reaction  can  occur even when itâ€™s not your turn to act. Some powers and other traits are usable as reactions.

### No Action

Finally,  some  things  players  are  called  upon  to  doâ€"certain die rolls like resistance checks, for exampleâ€"are not considered actions at all, as they involve no action on the part of the characters.

### Taking Your Turn

When  it  is  your  turn  in  the  initiative  order,  you  declare what actions your character will perform, and they are resolved in order.

### Starting Your Turn

The Gamemaster informs you when it is your turn. When you start your turn, you should:

â€¢

End  effects that last â€œuntil the start of your next turnâ€.
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

You perform your actions in any order that you wish, but you cannot normally â€œsplitâ€ your actions. So, for example, although you can move (move action) and then attack (standard  action)  or  attack  and  then  move,  you  cannot  move half  your  distance,  attack,  and  then  move  the  other  half unless you have some special trait that allows you to do so.

### Extra Action

### Ending Your Turn

At the end of your turn, you should:

â€¢

End any effects that last â€œuntil the end of your turnâ€.

â€¢  Make  any  necessary  resistance  checks  to  recover

You  can  use  extra  effort  in  order  to  take  an  additional standard or move action on your turn (see Extra Effort on page 19).

â€¢

from ongoing effects.

Inform the Gamemaster and other players that your turn is finished, allowing the next character in the initiative order to go.
```

---

### standard action

#### Domain Language

- A standard action allows a character to do something meaningful: attack, use a skill, activate a power or advantage, or perform a similar task.
- Each character is limited to one standard action per turn.
- A standard action may be exchanged for an additional move action (two move actions instead of one standard + one move).
- Special actions (aim, charge, defend, disarm, grab, feint, recover, ready, trip) are standard actions.

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

### Standard Action

A  standard  action  allows  you  to  do  something. You  can make  an  attack,  use  a  skill,  advantage,  or  power,  or  perform  other  similar  actions.  During  a  combat  round,  you can take a standard action and a move action.

### Move Action

A move action allows you to move your speed or perform an action taking a similar amount of time, such as draw or stow a weapon or other object, stand up, pick up an object, or perform some equivalent action.

You can take a move action in place of a standard action.

### Free Action

Free actions consume very little time and, over the span of the round, their impact is so minor they are considered to take no real time at all.

### Reaction

A  reaction  is  something  that  happens  in  response  to something  else,  like  a  reflex.  Like  free  actions,  reactions take so little time theyâ€™re considered free. The difference between the two is a free action is a conscious choice made on the characterâ€™s turn to act. A reaction can occur even when itâ€™s not your turn to act.
```

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

### Standard Actions

A  standard  action  generally  involves  acting  upon  something, whether itâ€™s an attack or using a power to affect something. Youâ€™re limited to one standard action each round.

### Move Actions

A  move  action,  like  the  name  implies,  usually  involves moving. You can take your move action before or after your standard action, so you can attack then move, or move then attack. You cannot, however, normally split-up your move action before and after your standard action. Move actions also include things like drawing weapons, standing up, and picking up or manipulating objects.

### Free Actions

A  free  action  is  something  so  comparatively  minor  it doesnâ€™t take significant time, so you can perform as many free actions in a round as the GM considers reasonable. Free actions include things like talking, dropping something, ending the use of a power, activating or maintaining some other powers, and so forth.
```

---

### move action

#### Domain Language

- A move action allows a character to move up to their speed rank or perform an equivalent activity (draw/stow an item, stand up, pick up an object).
- In a normal turn a character gets one standard action and one move action; the move may come before or after the standard action.
- A standard action may be exchanged for an additional move action, enabling two move actions in one turn.
- Actions cannot normally be split — a character may not move part of their speed, take a standard action, then move the remainder.
- A DC 15 Athletics check as a free action can increase ground speed rank by +1 for one round on one or more degrees of success.

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

### Move Action

A move action allows you to move your speed or perform an action taking a similar amount of time, such as draw or stow a weapon or other object, stand up, pick up an object, or perform some equivalent action (see the Actions in Combat Table).

You can take a move action in place of a standard action. For example, rather than moving your speed and attacking you can stand up and move your speed (two move actions), draw a weapon and climb (two move actions), or pick up an object and stow it (two move actions). You can also make a DC 15 Athletics check as a free action to run faster: one or more degree of success increases your ground speed rank by +1 for one round.
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

You perform your actions in any order that you wish, but you cannot normally â€œsplitâ€ your actions. So, for example, although you can move (move action) and then attack (standard action) or attack and then move, you cannot move half your distance, attack, and then move the other half unless you have some special trait that allows you to do so.
```

---

### free action

#### Domain Language

- A free action consumes so little time it is considered to take no real time over the span of a round.
- A character may perform as many free actions per turn as the GM considers reasonable.
- Examples: dropping an object, dropping prone, speaking a sentence or two, ceasing to concentrate on a power, maintaining a grab.
- Free actions are a conscious choice made on the character's own turn; they cannot occur when it is not the character's turn (reactions serve that role).

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

### Free Action

Free actions consume very little time and, over the span of the round, their impact is so minor they are considered to take no real time at all. You can perform one or more free actions while taking another action. For instance, dropping an object, dropping to a prone position, speaking a sentence or two, and ceasing to concentrate on maintaining a power are all free actions.
```

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

### Free Actions

A  free  action  is  something  so  comparatively  minor  it doesnâ€™t take significant time, so you can perform as many free actions in a round as the GM considers reasonable. Free actions include things like talking (heroes and villains always find time to say a lot in the middle of a fight), dropping something, ending the use of a power, activating or maintaining some other powers, and so forth.
```

---

### reaction

#### Domain Language

- A reaction is a response to something else happening during the round; it can occur even when it is not the character's turn.
- Reactions take no significant time and do not count against the character's normal action allotment.
- A character can react as often as circumstances dictate, but only when circumstances dictate.
- Spending a hero point is a reaction.
- Examples: taking a readied action when triggered, counter-disarming after losing a melee disarm, firing a netline after declaring a ready.

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

During a round you can take a standard and a move action (or substitute an additional move action for your standard action) along with as many free actions as you wish and as many reactions as are called for.
```

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

A  reaction  is  something  you  do  in  response  to  something  else.  A  reaction  doesnâ€™t  take  any  significant  time, like a free action. The difference is you react in response to something else happening during the round, perhaps not even on your turn. Reactions donâ€™t count against your normal  allotment  of  actions  and  you  can  react  as  often as the circumstances dictate, but only when they dictate.

### Conditions

Heroes  run  into  their  share  of  difficulties  in  their  work. One way MUTANTS & MASTERMINDS measures this is with different  conditions.  They  are  shorthand  for  the  different game modifiers imposed by things from power effects to injuries or fatigue. So, for example, â€œvulnerableâ€ is a condition where a heroâ€™s active defenses are reduced.

### Basic Conditions

Each  basic  condition  describes  a  single  game  modifier.

â€¢  Dazed:  A  dazed  character  is  limited  to  free  actions and a single standard action per turn, although the character may use that action to perform a move, as usual. Stunned supersedes dazed.

â€¢  Stunned: Stunned characters cannot take any actions, including free actions

â€¢  Vulnerable:  Vulnerable  characters  are  limited  in their  ability  to  defend  themselves,  halving  their  active defenses (round up the final value). Defenseless supersedes vulnerable.

â€¢  Defenseless: A defenseless character has active defense  bonuses  of  0.  Attackers  can  make  attacks  on defenseless  opponents  as  routine  checks.  If  the  attacker chooses to forgo the routine check and make a normal attack check, any hit is treated as a critical hit.
```

---

### delay

#### Domain Language

- Delay is a no-action choice to defer one's entire turn to later in the initiative order.
- A character cannot delay after having already taken an action on their turn, or if unable to take actions.
- After any other character acts, the delayed character may choose to act; their initiative slot moves to where they acted.
- If the trigger never fires before the character's original initiative comes up next round, the delayed turn is lost and initiative stays put.
- Beneficial effects that last until end of turn expire when the character delays; harmful effects persist until after the character acts.

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

### Crawl

### Move Action

While prone, you can only move by crawling. You crawl at your  normal  ground  speed  â€"1  rank  (or  half  your  normal speed).

Characters  with  the  Slither  effect  of  Movement  crawl  at their normal ground speed.

### Defend

### Standard Action

Rather than attacking, you focus on defense. Make an opposed  check  of  your  appropriate  active  defense  versus any attack made on you until the start of your next turn. Add  10  to  any  roll  of  10  or  less  that  you  make  on  these checks, just as if you spent a hero point (thus ensuring a minimum  roll  of  11). The  attacker  must  equal  or  exceed your opposed check result in order to hit you.

### Delay

### No Action

When you delay, you choose to take your turn later in the initiative order. You must delay your entire turn. You cannot delay if you have already taken an action on your turn, or if you are unable to take actions.

At any point after any other character in the conflict has acted,  you  can  choose  to  take  your  turn.  Your  initiative moves into the new place in the order where you act, and you take your normal allocation of actions. If you do not act before your initiative comes up in the next round, your turn ends, you lose your delayed turn, and your initiative remains where it is.

Beneficial effects lasting until the end of your turn end when you choose to delay, but harmful effects that last until the end of your turn last until after you act. Likewise, you do not make resistance checks until after you have taken your turn, so delaying can draw out some effects.

### Disarm

### Standard Action

You attempt to knock an itemâ€"such as a weapon or deviceâ€"out of an opponentâ€™s grasp. Make an attack check against the defender with a â€"2 penalty. If you attempt to disarm with a ranged attack, you are at â€"5 penalty. If your attack succeeds, make an opposed check of your attackâ€™s damage  against  the  defenderâ€™s  Strength.  If  you  win,  the defender dropped the held object. If you made the disarm unarmed, you can grab the dropped object as a free action. If you make a disarm attempt with a melee weapon and lose the opposed check, the defender may immediately make an attempt to disarm you as a reaction; make another opposed damage vs. Strength check.
```

---

### ready

#### Domain Language

- Ready is a standard action that prepares a single standard, move, or free action to trigger on a specified future condition.
- The character declares the action and triggering circumstances; the readied action fires as a reaction when conditions are met.
- When the readied action fires, the character's initiative slot moves to where they acted.
- If the trigger does not occur before the character's next initiative, the readied action is lost; the same action may be readied again.

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

### Move

### Move Action

You can move up to your normal speed rank in any movement mode available to you as a move action.

### Ready

### Standard Action

Readying lets you prepare to take an action later, after you would normally act on your initiative, but before your initiative on your next turn. Readying is a standard action, so you can move as well.

If you come to your next turn and have not yet performed your readied action, you donâ€™t get to take the readied action, you just lose your previous turn. You can ready the same action again on your next turn, if you wish, continuing to wait for the right circumstances.

### Recover

### Standard Action

You take your entire turn to try and catch your breath and bounce back a bit. When you recover, you can remove your highest level of damage or fatigue. Alternately, rather than removing a level of damage or fatigue, you can choose to make a resistance check against an ongoing effect, in addition to the normal resistance check at the end of your turn.

You  can  only  recover  once  per  conflict.
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

### Standard Action

You  try  to  trip  or  throw  your  opponent  to  the  ground. Make a close attack check against your opponentâ€™s Parry with a â€"2 circumstance penalty on the check.

### Maneuvers

You can ready a single standard, move, or free action. To do  so,  specify  the  action  you  will  take  and  the  circumstances under which you will take it. Then, any time before your next turn, you may take the readied action as a reaction to those circumstances. Your place in the initiative order then becomes the point where you took your readied action.

A maneuver is a different way of performing a particular action. For example, a defensive attack is an attack action that improves your defenses at the cost of accuracy.

### Accurate Attack

When you make an attack, you can take a penalty of up to â€"2 on the effect modifier of the attack and add the same number (up to +2) to your attack bonus.

### All-out Attack

When  you  make  an  attack  you  can  take  a  penalty  of  up to â€"2 on your active defenses (Dodge and Parry) and add the  same  number  (up  to  +2)  to  your  attack  bonus.

### Defensive Attack

When you make an attack you can take a penalty of up to â€"2 on your attack bonus and add the same number (up to +2) to your active defenses (Dodge and Parry).

### Demoralize

You can use Intimidation in combat as a standard action to undermine an opponentâ€™s confidence.
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

An  attack  check  determines  whether  or  not  you  hit  an opponent  in  combat  with  an  attack.  It  is  a  d20  roll  plus your bonus with that particular attack, usually based off of  Fighting  or  Dexterity  and  appropriate  modifiers,  like the Close and Ranged Combat skills. The difficulty is your targetâ€™s  defense  class:  Parry  for  close  attacks,  Dodge  for ranged attacks. Certain attacks may target other defenses. If  you  equal  or  exceed  your  targetâ€™s  defense  class  result, your attack hits. Otherwise, you miss.

Attack Check = d20 + attack bonus + modifiers vs. defense class

A natural 20 on an attack check (where the die comes up 20) always hits and may be a critical hit. A natural 1 on an attack check (where the die comes up 1) always misses, regardless of the check total. This differs from normal checks and reflects the variable and unpredictable nature of combat.
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

### Conflicts

A conflict is when two or more characters go up against each other, typically in a fight of some sort.

### Attacks

An attack check represents an attempt to hit a target with an attack. When you make an attack check, roll the die and add your bonus with that attack. If your result equals or exceeds  the  targetâ€™s  defense,  your  attack  hits  and  may have some effect.

Attack Check = d20 + attack bonus vs. defense class

### Critical Hits

When you make an attack check and get a natural 20 (the d20 actually shows 20), you automatically hit, regardless of  your  targetâ€™s  defense,  and  you  score  a  threat. The  hit might also be a critical hit (sometimes called a â€œcritâ€). To find out if itâ€™s a critical hit, determine if the attack check total is equal to or greater than the targetâ€™s defense. If so, it is a critical hit. If not, the attack still hits, but as a normal attack, not a critical.

A critical hit can have one of the following three effects, chosen by the player when the critical hit is determined:

â€¢  Increased Effect: The critical hit increases the difficulty to resist the attackâ€™s effect by +5.

â€¢  Added  Effect:  The  critical  hit  adds  another  effect onto the attack, but its effective rank is 0.

â€¢  Alternate  Effect: The  critical  hit  results  in  an  alternate effect for the attack, like a use of extra effort for a power stunt, except the character suffers no fatigue as a result.
```

---

### attack bonus

#### Domain Language

- The attack bonus is the modifier added to the d20 roll when making an attack check.
- For most characters it is based on Fighting (close attacks) or Dexterity (ranged attacks) plus applicable Close Combat or Ranged Combat skill ranks plus circumstance modifiers.
- Maneuvers (Accurate Attack, All-out Attack, Defensive Attack, Power Attack) can temporarily shift the attack bonus in exchange for other trade-offs.
- Conditions and tactical circumstances (aim bonus, charge penalty, concealment, cover) apply as circumstance modifiers.

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

An  attack  check  determines  whether  or  not  you  hit  an opponent  in  combat  with  an  attack.  It  is  a  d20  roll  plus your bonus with that particular attack, usually based off of  Fighting  or  Dexterity  and  appropriate  modifiers,  like the Close and Ranged Combat skills.

Attack Check = d20 + attack bonus + modifiers vs. defense class
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

### Accurate Attack

When you make an attack, you can take a penalty of up to â€"2 on the effect modifier of the attack and add the same number (up to +2) to your attack bonus. Your effect modifier cannot be reduced below +0 and your attack bonus cannot more than double in this way.

### All-out Attack

When  you  make  an  attack  you  can  take  a  penalty  of  up to â€"2 on your active defenses (Dodge and Parry) and add the  same  number  (up  to  +2)  to  your  attack  bonus.

### Defensive Attack

When you make an attack you can take a penalty of up to â€"2 on your attack bonus and add the same number (up to +2) to your active defenses (Dodge and Parry).
```

---

### defense class

#### Domain Language

- The defense class is the difficulty number an attack check must equal or exceed to hit: Defense Class = defense rank + 10.
- Close attacks target Parry; ranged attacks target Dodge; certain attacks may target other defenses.
- Vulnerable halves active defense ranks (round up); defenseless reduces active defense ranks to 0 making the base DC just 10.
- Attackers may make attack checks against defenseless targets as routine checks (auto-hit with bonus ≥ 0).

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

### No Cover

### Partial Cover

### Total Cover

### Cover

Targets may also hide behind obstructions to gain cover against your attacks.

Partial Cover applies a â€"2 circumstance penalty to your attack check.

Total  Cover  applies  a  â€"5  circumstance  penalty  to  your  attack check.

### Defenses

Your defenses determine how difficult it is to hit you with various attacks. Most attacks target your active defenses, Dodge and Parry: close attacks target Parry while ranged attacks target Dodge.

You  add  your  defense  rank  to  a  base  value  of  10  (like  a routine  check)  to  determine  your  defense  class  against an attack, which is the DC of the attack check:

Defense Class = defense + 10

Cover  also  grants  a  circumstance  bonus  to  Dodge  resistance  checks  against  area  effects  equal  to  its  penalty  to attack checks.

### Minions

Minions  are  minor  characters  subject  to  special  rules  in combat, and generally easier to defeat than normal characters.

â€¢  Minions  cannot  score  critical  hits  against  non-minions.

â€¢  Non-minions  can  make  attack  checks  against  minions as routine checks.

â€¢  If a minion fails a resistance check, the minion suffers the worst degree of the effect.
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

Two conditions strongly affect your defenses. When you are  vulnerable,  your  active  defense  ranks  are  halved (round  up  fractions).

When  you  are  defenseless,  your  active  defense  ranks are  reduced  to  zero, meaning  the  base  difficulty  class  to hit you is just 10! Whatâ€™s more, attackers can make attack checks against defenseless targets as routine checks, meaning a hit is guaranteed with an attack bonus of 0 or more, unless there are other modifiers affecting the check.

### Resistance

A successful attack has some effect on the target. Typically this is an effect from the Powers chapter, such as Damage or Affliction. The effect has a rank, used to determine a difficulty class for the targetâ€™s resistance check.

Resistance Difficulty = effect rank + 10

The target of the attack makes a resistance check against the effect to determine what, if anything, happens.

### Ongoing Effects

Some effects are not resisted just once, but multiple times. Make a resistance check for the target of an ongoing effect at the end of each of the targetâ€™s turns. A successful check ends the effect and removes conditions imposed by it.
```

---

### close attack

#### Domain Language

- A close attack targets a character within physical reach (by touch or melee weapon) and is checked against the target's Parry defense.
- Strength-based damage (unarmed, melee weapons) is close range by default.
- Close attacks can score critical hits; many maneuvers (charge, trip, disarm, grab) are close attacks.

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

An attack has one of three ranges: close, ranged, and perception. A close attack can only affect a target you can physically reach, by touch or wielding a melee weapon, for example. A ranged attack can affect a target at a distance, while a perception attack can hit a target you are able to accurately perceive automatically without need for an attack check.

A ranged attack has a short range up to its rank x 25 feet, at which it has no penalties. At medium range (up to rank x 50 feet), the attack check has a â€"2 circumstance modifier. At long range (up to rank x 100 feet), the attack check has a â€"5 circumstance modifier. Ranged attacks cannot go beyond long range.
```

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

The difficulty is your targetâ€™s  defense  class:  Parry  for  close  attacks,  Dodge  for ranged attacks. Certain attacks may target other defenses.
```

---

### ranged attack

#### Domain Language

- A ranged attack targets a character at a distance and is checked against the target's Dodge defense.
- Short range (rank × 25 ft): no penalty; medium (rank × 50 ft): −2 circumstance; long (rank × 100 ft): −5 circumstance; beyond long range the target is out of range and cannot be attacked.
- Perception-range attacks automatically hit without an attack check and cannot score critical hits or misses.
- Modifiers affecting the attack check (including maneuvers) do not apply to area or perception effects.

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

An attack has one of three ranges: close, ranged, and perception. A close attack can only affect a target you can physically reach. A ranged attack can affect a target at a distance, while a perception attack can hit a target you are able to accurately perceive automatically without need for an attack check.

A ranged attack has a short range up to its rank x 25 feet, at which it has no penalties. At medium range (up to rank x 50 feet), the attack check has a â€"2 circumstance modifier. At long range (up to rank x 100 feet), the attack check has a â€"5 circumstance modifier. Ranged attacks cannot go beyond long range; a target further away is out of range and cannot be attacked.

### Perception And Area Effects

Perception and Area effects do not require attack checks, they  automatically  affect  a  given  target  or  area. Because of this, these attacks cannot score critical hits or misses, nor do modifiers affecting the attack checkâ€"including various maneuversâ€"affect them.
```

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

Attack Check = d20 + attack bonus + modifiers vs. defense class

The difficulty is your targetâ€™s defense class: Parry for close attacks, Dodge for ranged attacks.
```

---

### critical hit

#### Domain Language

- A critical hit occurs when the attack check rolls a natural 20 and the total also equals or exceeds the target's defense class.
- A natural 20 that does not beat the defense class is still a hit but not a critical hit.
- On a critical hit the attacker chooses one of three effects: Increased Effect (+5 resistance DC), Added Effect (bonus rank-0 secondary effect), or Alternate Effect (temporary power stunt at no fatigue cost).
- Against a minion, Increased Effect bypasses the resistance check entirely — the minion automatically receives the worst degree.
- Improved Critical advantage extends the threat range below natural 20; auto-hit only occurs on a natural 20.
- Area and perception effects cannot score critical hits.

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

### Critical Hits

When you make an attack check and get a natural 20 (the d20 actually shows 20), you automatically hit, regardless of  your  targetâ€™s  defense,  and  you  score  a  threat. The  hit might also be a critical hit. To find out if itâ€™s a critical hit, determine if the attack check total is equal to or greater than the targetâ€™s defense. If so, it is a critical hit. If not, the attack still hits, but as a normal attack, not a critical.

### Increased Threat Range

Characters  with  the  Improved  Critical  advantage can score a threat on a natural result less than 20, although they still automatically hit only on a natural 20. Any attack check that doesnâ€™t result in a hit is not a threat.

A critical hit can have one of the following three effects, chosen by the player when the critical hit is determined:

â€¢  Increased Effect: The critical hit increases the difficulty to resist the attackâ€™s effect by +5. Against a minion, this bypasses the resistance check entirely; the minion automatically receives the highest degree of the attackâ€™s effect.

â€¢  Added  Effect:  The  critical  hit  adds  another  effect onto the attack, but its effective rank is 0, so the resistance DC is just the base value (10, or 15 for Damage).

â€¢  Alternate  Effect: The  critical  hit  results  in  an  alternate effect for the attack, like a use of extra effort for a power stunt, except the character suffers no fatigue as a result.
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

### Critical Misses

Conversely, a natural 1 (the d20 comes up 1) on an attack check is always a miss, regardless of your total result.

### Damage

A successful attack with a Damage effect requires the target to make a Toughness resistance check.

### Damage Resistance Check

Toughness vs. [Damage rank + 15]

Success : The damage has no effect.

Failure (one degree): The target has a â€"1 circumstance penalty to further resistance checks against damage.

Failure (two degrees): The target is dazed until the end of their next turn and has a â€"1 circumstance penalty to further checks against damage.

Failure  (three  degrees):  The  target  is  staggered and  has  a  -1  circumstance  penalty  to  further  checks against damage. If the target is staggered again, apply the fourth degree of effect.

Failure (four degrees): The target is incapacitated.

The  circumstance  penalties  to Toughness  checks  are  cumulative.

If an incapacitated target fails a resistance check against Damage, the targetâ€™s condition shifts to dying. A dying target who fails a resistance check against Damage is dead.
```

---

### aim

#### Domain Language

- Aim is a standard action that lines up a subsequent attack, granting a circumstance bonus on the following attack check.
- Close attack or ranged attack at close range: +5 circumstance bonus; ranged attack at greater distance: +2 circumstance bonus.
- The attacker is vulnerable while aiming.
- A free action maintains aim before making the attack; losing the ability to maintain aim cancels the bonus.
- The very next action after aiming must be the attack; any other action cancels the aim bonus.

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

### Standard Action

If you are in position to attack an opponent, you can attempt to aid an ally engaged in melee with that opponent as a standard action.

AIM

### Standard Action

By taking a standard action to aim and line up an attack, you get a bonus to hit when you make the attack. If youâ€™re making a close attack, or a ranged attack at close range, you  get  a  +5  circumstance  bonus  on  your  attack  check. If youâ€™re making a ranged attack from a greater distance, you get a +2 circumstance bonus.

However, you are vulnerable while aiming and it requires a free action to maintain your aim before you make your attack. If you are unable to maintain it, you lose its benefit.

Once you aim, your next action must be to make the attack. Taking a different action spoils your aim and you lose the bonus.

### Attack

### Standard Action

With  a  standard  action,  you  can  make  an  attack  check against any opponent within the attackâ€™s range.

### Charge

### Standard Action

You rush forward to attack. You move your speed rank in a mode of movement available to you in a relatively straight line  towards  your  target.  At  the  end  of  your  movement, you perform a close attack against your opponent with a â€"2 circumstance penalty to the attack check.

You can combine a charge action with a move action, allowing you to move up to twice your speed.
```

---

### charge

#### Domain Language

- Charge is a standard action: the attacker moves their speed rank in a straight line toward a target, then makes a close attack at the end of movement with a −2 circumstance penalty.
- Combined with a move action, the attacker can move up to twice their speed rank before attacking.
- Charge enables the slam attack maneuver.

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

### Charge

### Standard Action

You rush forward to attack. You move your speed rank in a mode of movement available to you in a relatively straight line  towards  your  target.  At  the  end  of  your  movement, you perform a close attack against your opponent with a â€"2 circumstance penalty to the attack check.

You can combine a charge action with a move action, allowing you to move up to twice your speed (your speed rank as a move action, then your speed rank again when you charge).
```

---

## Damage and Resistance

Damage and Resistance is the system that determines the consequence of a landed attack and the pathway from unharmed through degradation to incapacitation, dying, and death. The Damage effect is the primary weapon of combat — when a hit is scored the target makes a Toughness resistance check against a DC of damage rank + 15. Degrees of failure accumulate penalties and impose conditions: a single miss begins a cumulative −1 Toughness penalty; two degrees add dazed; three degrees add staggered; four degrees incapacitate. The incapacitated state exposes the target to the dying sequence, and another failure while dying kills. Toughness resistance is the specific check that governs this, distinct from the generic resistance check used for other effects (Affliction, ongoing hazards). Recovery undoes this progression — living targets heal one damage condition per minute of rest, and the Recover action accelerates this in-conflict. The recovery check is the per-turn automatic roll that ends ongoing effects. This KA owns the damage progression from hit to death and the full recovery arc back to normal.

#### Decisions made

- resistance check is included here because combat's central use of resistance checks is for Toughness vs. Damage; the general resistance check mechanic is owned by Check Resolution, but Combat must define how it applies to ongoing combat effects.
- dying and incapacitated are placed here because they are the direct terminal outputs of the Toughness failure chain — they are not general conditions the system imposes arbitrarily but specific outcomes of damage resolution.
- recover (the action) is placed here rather than Turn Structure because its purpose is to remove damage conditions, not to manage action economy.
- recovery check is placed here because it is the primary mechanism by which ongoing conditions end in combat.

### resistance check

#### Domain Language

- A resistance check resists a power effect or hazard: d20 + defense bonus vs. resistance DC (typically effect rank + 10).
- Resistance checks are not actions — they represent involuntary responses and do not consume action allotment.
- Resistance checks may be graded: different degrees of failure impose progressively worse outcomes.
- Ongoing effects require a resistance check at the end of each of the target's turns; success ends the effect and removes conditions.
- The Recover action grants an additional resistance check against an ongoing effect beyond the normal end-of-turn check.

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

A  resistance  check  is  an  attempt  to  resist  different  effects, ranging from damage and injury to traps, poisons, and various power effects. A resistance check is a d20 roll + the appropriate defense (typically Dodge, Fortitude, Toughness, or Will).

Resistance Check = d20 + defense bonus + modifiers vs. hazardâ€™s DC (generally 10 + rank)

The difficulty class is based on the strength of the hazard, such as the rank of an effect or the strength of a disease or poison, typically that value plus 10 (like a routine check). Resistance checks may be graded, with different results at different degrees.
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

A successful attack has some effect on the target. Typically this is an effect from the Powers chapter, such as Damage or Affliction. The effect has a rank, used to determine a difficulty class for the targetâ€™s resistance check.

Resistance Difficulty = effect rank + 10

The target of the attack makes a resistance check against the effect to determine what, if anything, happens.

### Ongoing Effects

Some  effects  are  not  resisted  just  once,  but  multiples times. The later resistance checks represent how fast the target is able to â€œshake offâ€ the effect. Make a resistance check for the target of an ongoing effect at the end of each of the targetâ€™s turns. A successful check ends the effect and removes conditions imposed by it.
```

---

### damage

#### Domain Language

- Damage is a power effect applied by a successful attack; the target makes a Toughness resistance check against DC = damage rank + 15.
- Failure degrees: one degree → −1 cumulative Toughness penalty; two degrees → dazed + −1 penalty; three degrees → staggered + −1 penalty (if already staggered, apply fourth degree); four degrees → incapacitated.
- Toughness check penalties from repeated failures are cumulative across all hits.
- An incapacitated target that fails another Toughness check becomes dying; a dying target that fails becomes dead.
- Strength provides a built-in close-range Damage effect; Strength-based weapons add Strength rank + Damage rank together.

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

Success : The damage has no effect.

Failure (one degree): The target has a â€"1 circumstance penalty to further resistance checks against damage.

Failure (two degrees): The target is dazed until the end of their next turn and has a â€"1 circumstance penalty to further checks against damage.

Failure  (three  degrees):  The  target  is  staggered and  has  a  -1  circumstance  penalty  to  further  checks against damage. If the target is staggered again (three degrees of failure on a Damage resistance check), apply  the  fourth  degree  of  effect.

Failure (four degrees): The target is incapacitated.

The  circumstance  penalties  to Toughness  checks  are  cumulative, so a target who fails three resistance checks against Damage, each with one degree of failure, has a total â€"3 penalty.

If an incapacitated target fails a resistance check against Damage, the targetâ€™s condition shifts to dying. A dying target who fails a resistance check against Damage is dead.

### Strength And Damage

Strength provides a â€œbuilt-inâ€ Damage effect: the ability to hit things! You can apply effect modifiers to the Damage your Strength inflicts, making it Penetrating or even an Area effect!

If you choose, a Damage effect can be Strength-basedâ€" something like a melee weaponâ€"allowing your Strength Damage to add to it. You add your Strength and Damage ranks together when determining the rank of the attack.
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

### Example Of Conflict

The GM compares Princessâ€™ result to the smugglersâ€™ Will defense, which is 12. Her check succeeded with one degree. The smugglers are impaired (â€"2 on their checks) until the end of Princessâ€™ next turn.

Ultramarine: Rolls a 9, with a +10 attack bonus. I got a 19.

GM: Knowing that well exceeds the smugglerâ€™s Dodge defense of 12, rolls a Dodge resistance check, getting a 16, minus the impaired penalty from Princessâ€™ Intimidation for a 14 vs. DC 20. Two degrees of failure. The smuggler is defenseless and immobilized.
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

### Example Of Conflict

Ultramarineâ€™s player rolls an attack check with her laser, getting an 11 with a +10 bonus for a 21 result. That beats Trawlerâ€™s Dodge DC of 16, so the GM rolls a Toughness resistance check. The laser is rank 10, for a Damage resistance DC of 25. Trawler has Toughness 10 and the GM rolls a 9. Thatâ€™s a 19 total, two degrees of failure vs. DC 25. Trawler suffers both a â€"1 to Toughness checks and a dazed condition.
```

---

### Toughness resistance

#### Domain Language

- Toughness resistance is the specific resistance check against a Damage effect: d20 + Toughness rank vs. damage rank + 15.
- Every failure imposes a −1 cumulative circumstance penalty to all future Toughness resistance checks for that character.
- The penalty stacks across multiple hits and across different attackers within a scene.
- Impervious Toughness ignores Damage effects below a threshold rank equal to half the Impervious rank.
- Living targets recover Toughness penalties by removing one damage condition per minute of rest.

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

Success : The damage has no effect.

Failure (one degree): The target has a â€"1 circumstance penalty to further resistance checks against damage.

Failure (two degrees): The target is dazed until the end of their next turn and has a â€"1 circumstance penalty to further checks against damage.

Failure (four degrees): The target is incapacitated.

The  circumstance  penalties  to Toughness  checks  are  cumulative.
```

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

### Recovery

As a result of conflict, characters often suffer adverse conditions from being knocked  around  and  hit  with  different  powers. The specific conditions are discussed in the effects defined in the Powers chapter, particularly Affliction and Damage, the most common effects of conflicts.

Living targets remove one damage condition per minute of rest, starting from their most severe condition and working back. So a damaged character recovers from being incapacitated, then staggered, dazed, and finally removes a â€"1 Toughness check penalty per minute until fully recovered. The Healing and Regeneration effects can speed this process.

Objects, having no Stamina, do not recover from damage unless they have an effect like Regeneration. Instead, they must be repaired.
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

If an incapacitated target fails a resistance check against Damage, the targetâ€™s condition shifts to dying. A dying target who fails a resistance check against Damage is dead.
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

### Death

Character death is a relatively rare happenstance in the comic books. The MUTANTS & MASTERMINDS rules make character death a similarly rare occurrence. Characters generally only acquire the dying condition after being incapacitated and suffering further harm, which usually means someone is actively trying to kill them. Even then, dying characters have opportunities to stabilize and stave off death. It takes a second active effort to kill a dying character outright, so accidental death due to a single bad die roll is all but impossible for the major characters in a series.

Note that none of this applies to minions, who can be killed simply with a successful attack and a declaration of intent to do so.

### Surprise Attack

On  occasions  when  your  attack  catches  a  target  by  surprise, the target is vulnerable to your attacks.

### Team Attack

Multiple attackers can attempt to combine their attacks in order to overwhelm an opponentâ€™s resistance. The attacks to be combined must have the same effect and resistance and be within 5 ranks of each other.
```

---

### incapacitated

#### Domain Language

- Incapacitated is the condition imposed by four degrees of failure on a Toughness resistance check (defenseless + stunned + unaware; character typically falls prone).
- An incapacitated target that fails another Toughness resistance check transitions to dying.
- Incapacitation can also result from suffocation, vacuum exposure, or other hazard escalation.
- While incapacitated the character cannot act (stunned) and has no active defenses (defenseless).

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

Failure (four degrees): The target is incapacitated.

If an incapacitated target fails a resistance check against Damage, the targetâ€™s condition shifts to dying.
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

On the third round of exposure to vacuum, a character must succeed on a Fortitude check (DC 20) each round or suffer from aeroembolism. A failed check means the creature is stunned and remains so until returned to normal atmospheric pressure. Two or more degrees of failure impose the incapacitated condition.

The real danger of vacuum comes from suffocation. If the check fails, or when the character simply stops holding his breath, he begins to suffocate: the next round, he becomes incapacitated. The following round, heâ€™s dying and cannot stabilize until returned to a normal atmosphere.
```

---

### recovery check

#### Domain Language

- A recovery check is a resistance check made to end an ongoing condition or effect; it is not an action.
- At the end of each of the character's turns, a resistance check is automatically made against any ongoing effect.
- The Recover action (standard action, once per conflict) grants an additional resistance check beyond the normal end-of-turn check.
- Natural recovery: living targets remove one damage condition per minute of rest, working from the worst condition back toward normal.
- Healing and Regeneration effects can speed this process.

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

### Recover

### Standard Action

You take your entire turn to try and catch your breath and bounce back a bit. When you recover, you can remove your highest level of damage or fatigue. Alternately, rather than removing a level of damage or fatigue, you can choose to make a resistance check against an ongoing effect, in addition to the normal resistance check at the end of your turn.

You  can  only  recover  once  per  conflict.  Once  you  have done so, you must recover from any remaining damage, fatigue, or effects normally (or with outside assistance).

When you recover, you gain +2 to your active defenses until the start of your next turn.
```

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

To  attack  a  target,  you  first  have  to  have  some  idea  of where to aim your attack. If you can perceive something with an accurate sense (such as sight) then you can target it with an attack. If you cannot clearly perceive the target, then it has concealment from you.

Partial Concealment  applies  a  â€"2  circumstance  penalty to your attack check for not being able to clearly perceive your target.

Total Concealment applies a â€"5 circumstance penalty to your attack check for not being able to perceive the target at all.

Living targets remove one damage condition per minute of rest, starting from their worst condition and working back. So a damaged character recovers from being incapacitated, then staggered, dazed, and finally removes a â€"1 Toughness check penalty per minute until fully recovered.
```

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

Living targets remove one damage condition per minute of rest, starting from their most severe condition and working back. So a damaged character recovers from being incapacitated, then staggered, dazed, and finally removes a â€"1 Toughness check penalty per minute until fully recovered. The Healing and Regeneration effects can speed this process.
```

---

### recover

#### Domain Language

- Recover is a standard action requiring the character's entire turn; usable only once per conflict.
- On recovery: remove the highest current level of damage or fatigue; alternatively make an additional resistance check against one ongoing effect (beyond the normal end-of-turn check).
- Recovery also grants +2 to active defenses until the start of the character's next turn.
- Remaining damage, fatigue, or effects after using recover must heal normally (rest or outside assistance).

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

### Recover

### Standard Action

You take your entire turn to try and catch your breath and bounce back a bit. When you recover, you can remove your highest level of damage or fatigue. Alternately, rather than removing a level of damage or fatigue, you can choose to make a resistance check against an ongoing effect, in addition to the normal resistance check at the end of your turn.

You can only recover once per conflict. Once you have done so, you must recover from any remaining damage, fatigue, or effects normally (or with outside assistance).

When you recover, you gain +2 to your active defenses until the start of your next turn.
```

---

## Combat Maneuvers

Combat Maneuvers are the specialized standard-action tactics that produce outcomes beyond a simple hit — disabling, restraining, toppling, misdirecting, or buffeting opponents. Each maneuver modifies the standard attack resolution sequence with a specific check chain: disarm and trip each use an attack check followed by an opposed secondary check; grab uses an attack check followed by a resistance check; feint replaces the attack check with a skill check to impose a condition; slam attack modifies the damage formula of a charge; and defend replaces an attack with a defensive opposed roll. Maneuvers are optional additions to declared actions; the GM decides if circumstances permit a given maneuver. None of the maneuvers directly deal Toughness damage by themselves (except slam attack, which adds a damage bonus); their primary purpose is to impose conditions (prone, restrained, bound, vulnerable) or change the tactical situation. Combat Maneuvers depend on Attack Resolution for the initial hit determination and on Damage and Resistance for damage outcomes when applicable.

#### Decisions made

- disarm, grab, trip, feint, slam attack, and defend pass both tests — each is a distinct tactical action with its own resolution chain.
- aim is placed under Attack Resolution (not here) because its sole effect is a circumstance bonus to the attack check, not a separate tactical outcome.
- charge is placed under Attack Resolution (not here) because it is fundamentally an attack with movement; slam attack, the charge variant, is kept here because its primary mechanical contribution is to the damage formula.
- defend is included here rather than Turn Structure because it replaces the attack action with a defensive maneuver that produces a specific mechanical effect on opponent attacks.

### defend

#### Domain Language

- Defend is a standard action: the character focuses on avoiding attacks rather than attacking.
- The defender makes an opposed check of their active defense (Parry or Dodge) vs. each attack made on them until the start of their next turn.
- Any defend roll result of 10 or lower is treated as 10 (same as hero point re-roll floor), ensuring a minimum effective result of 11.
- An attacker must equal or exceed the defender's opposed check result — not merely the normal defense class.

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

Rather than attacking, you focus on defense. Make an opposed  check  of  your  appropriate  active  defense  versus any attack made on you until the start of your next turn. Add  10  to  any  roll  of  10  or  less  that  you  make  on  these checks, just as if you spent a hero point (thus ensuring a minimum  roll  of  11). The  attacker  must  equal  or  exceed your opposed check result in order to hit you.
```

---

### disarm

#### Domain Language

- Disarm is a standard action to knock an item out of an opponent's grasp.
- Attack check vs. the defender: −2 penalty for close disarm; −5 for ranged disarm.
- If the attack hits: opposed check of attack's damage rank vs. defender's Strength; win → defender drops the item.
- An unarmed disarm success allows grabbing the dropped item as a free action.
- If the attacker used a melee weapon and loses the opposed check, the defender may immediately counter-disarm as a reaction.

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

### Disarm

### Standard Action

You attempt to knock an itemâ€"such as a weapon or deviceâ€"out of an opponentâ€™s grasp. Make an attack check against the defender with a â€"2 penalty. If you attempt to disarm with a ranged attack, you are at â€"5 penalty. If your attack succeeds, make an opposed check of your attackâ€™s damage  against  the  defenderâ€™s  Strength.  If  you  win,  the defender dropped the held object. If you made the disarm unarmed, you can grab the dropped object as a free action. If you make a disarm attempt with a melee weapon and lose the opposed check, the defender may immediately make an attempt to disarm you as a reaction; make another opposed damage vs. Strength check. If this disarm attempt fails, you do not, however, get an additional attempt to disarm the defender.
```

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

### Drop An Item

### Free Action

Dropping a held item is a free action.

### Drop Prone

### Free Action

Dropping  to  a  prone  position  is  a  free  action,  although getting up requires a move action (see Stand).

### Escape

### Move Action

You attempt to escape from a successful grab (see Grab). Make  a  check  of  your  Athletics  or  Acrobatics  against the  routine  check  result  of  your  opponentâ€™s  Strength  or grab  effect  rank.  If  you  succeed,  you  end  the  grab  and can move away from your opponent.

### Grab

### Standard Action

You  attempt  to  grab  a  target.  Make  an  attack  check against the target. If successful, the target makes a resistance check against your Strength (or the rank of a grabbing effect) using the better of Strength or Dodge. If you win with one degree of success, the target is restrained (immobile  and  vulnerable). Two  or  more  degrees  leave your  opponent  bound  (defenseless,  immobile,  and  impaired).  You  can  attempt  to  improve  an  existing  hold with another grab action on a following turn.

You  are  hindered  and  vulnerable  while  grabbing  and holding an opponent. You can maintain a successful grab as a free action each turn, but cannot perform other actions requiring the use of your grabbing limb(s) while doing so. Since maintaining a grab is a free action, you can take a standard action to inflict your Strength damage to a grabbed target on subsequent turns after the grab is established.

You can drag a restrained or bound target along with you when  you  move.  The  target  gets  a  Strength  resistance check  against  your  Strength.

You can end a grab (releasing your target) as a free action. A target can attempt to escape from a grab as a move action (see Escape).
```

---

### trip

#### Domain Language

- Trip is a standard action (close attack vs. target's Parry at −2 circumstance penalty) to knock a target prone.
- If the attack hits: opposed check of Acrobatics or Athletics (better of each) between attacker and defender.
- Attacker wins → defender falls prone in an adjacent area of the attacker's choice.
- Attacker loses → defender may immediately attempt to counter-trip; if that fails, the attempt ends.

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

### Standard Action

You  try  to  trip  or  throw  your  opponent  to  the  ground. Make a close attack check against your opponentâ€™s Parry with a â€"2 circumstance penalty on the check. If the attack succeeds, make an opposed check of your Acrobatics or Athletics against your opponentâ€™s Acrobatics or Athletics. Use whichever has the better bonus in each case.

If you win, the defender is prone in an area adjacent to you of your choice. If you lose, the defender immediately gets another opposed check to try and trip you. If it fails, the trip attempt ends.
```

---

### feint

#### Domain Language

- Feint is a standard action using Deception to mislead an opponent in combat.
- The feinting character makes a Deception check opposed by the better of the target's Deception or Insight.
- Success leaves the target vulnerable against the feinter's next attack until the end of the feinter's next round.

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

### Finishing Attack

When you attack a defenseless target at close range, you can  choose  to  make  the  attack  as  a  routine  check. This generally means your attack hits automatically, since the target has no defense bonus, and the routine check overcomes the normal difficulty.

If  you  choose  to  make  your  attack  check  normally (against DC 10), then a successful hit is treated as a critical hit, with a +5 circumstance bonus to the attackâ€™s resistance DC. Additionally, if you hit with a damaging attack with intent to kill, and the targetâ€™s resistance check has three or more degrees of failure, the target dies immediately.

### Power Attack

When you make an attack you can take a penalty of up to â€"2 on your attack bonus and add the same number (up to +2) to the effect bonus of your attack.

### Slam Attack

When you charge, you can charge right into your target, using  your  momentum  to  strengthen  your  attack.  The damage rank for your attack equals your movement speed rank, or your normal damage rank, with a +1 circumstance bonus, whichever is higher. If you move your full speed before you charge, increase your damage by either means by an additional +1 circumstance bonus. The Gamemaster may limit your base slam attack damage by the series power level.

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

### Slam Attack

When you charge, you can charge right into your target, using  your  momentum  to  strengthen  your  attack,  but potentially receiving some damage from the impact yourself. The damage rank for your attack equals your movement speed rank, or your normal damage rank, with a +1 circumstance bonus, whichever is higher. If you move your full speed before you charge, increase your damage by either means by an additional +1 circumstance bonus.

You suffer some of the impact of slamming into a target; make a Toughness resistance check against half the damage rank of your attack (rounded down).

Example:  Slingshot  flies  into  a  foe,  moving  at speed  rank  10.  His  unarmed  damage  (Strength) rank is only 2, so he uses his speed rank of 10 for the damage. Since he also moved his full speed to build up momentum, he increases his damage by +1 for a total damage rank of 11.
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

Bonuses  to Toughness  protect  against  slam  attack  damage  normally.  Immunity  to  slam  damage  you  inflict  is  a rank 2 Immunity effect, while Immunity to all slam damage is rank 5.

### Surprise Attack

On  occasions  when  your  attack  catches  a  target  by  surprise,  the  target  is  vulnerable  to  your  attacks.  Surprise attacks occur during the surprise round of a conflict and may also occur as a result of stealth or concealment, allowing you to sneak up on a target.
```

---

## Tactical Environment

Tactical Environment encompasses the contextual factors that modify combat outcomes without being actions themselves: concealment, cover, surprise, minion rules, and the mechanics for combining attackers (team attack, combined attack). Concealment and cover are passive modifiers applied by the GM based on the scene — both impose circumstance penalties to attack checks, with the important distinction that concealment impairs perception while cover impairs attack trajectory. Surprise reshapes the opening of a conflict, granting the non-surprised side an action window and making the surprised side vulnerable. Minions are a scaling device — the GM uses them to model hordes of weaker opposition with simplified rules that accelerate combat. Team attack and combined attack give multiple combatants a cooperative option to overcome targets whose individual resistance would be too high to crack. Tactical Environment interacts primarily with Attack Resolution (all modifiers flow into attack checks or defense class) and with Damage and Resistance (minion defeat, combined attack damage output).

#### Decisions made

- concealment, cover, surprise, minion, team attack, and combined attack all pass independence and module-fit tests.
- combined attack is kept as a distinct term from team attack because the partition lists it separately; however, decisions made notes that combined attack and team attack refer to the same mechanic; combined attack is the pattern-name while team attack is the rule-name.
- minion is kept here (not its own KA) because it is a rule modifier applied within combat, not an independent character type with lifecycle outside the combat domain; minion stats and hiring are owned by Character Construction.

### concealment

#### Domain Language

- Concealment applies when an attacker cannot clearly perceive their target with an accurate sense.
- Partial concealment (dim lighting, foliage, fog, smoke): −2 circumstance penalty to attack checks.
- Total concealment (complete darkness, heavy smoke): −5 circumstance penalty; attacker must know or guess the approximate area to target at all.
- Concealment is caused by conditions that obstruct perception — not physical obstructions that block attacks (those provide cover).
- Senses countering concealment (e.g., Counters Concealment: Darkness) remove the penalty for the corresponding condition.

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

To  attack  a  target,  you  first  have  to  have  some  idea  of where to aim your attack. If you can perceive something with an accurate sense (such as sight) then you can target it with an attack. If you cannot clearly perceive the target, then it has concealment from you.

Partial Concealment  applies  a  â€"2  circumstance  penalty to your attack check for not being able to clearly perceive your  target.  It  includes  conditions  like  dim  lighting,  foliage, heavy precipitation, fog, smoke, and the like.

Total Concealment applies a â€"5 circumstance penalty to your attack check for not being able to perceive the target at all, presuming the attacker even knows (or guesses) the right area to target.
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

Criminals  often  lurk  in  the  darkness,  and  many  crimes take  place  at  night.  Most  cities  are  lit  well  enough,  but sometimes  heroes  run  into  areas  where  itâ€™s  difficult  to see. Poorly lit areas provide concealment. Characters with Counters Concealment (Darkness) Senses or other appropriate Senses effects can ignore concealment penalties for poor lighting.
```

---

### cover

#### Domain Language

- Cover applies when a target is behind a physical obstruction that could block or deflect an attack.
- Partial cover (roughly half the target behind obstruction): −2 circumstance penalty to attack checks.
- Total cover (three-quarters or more behind obstruction): −5 circumstance penalty to attack checks.
- Complete cover (target fully behind obstruction): cannot attack the target directly; may target the cover itself.
- Cover grants a circumstance bonus to Dodge resistance checks against area effects equal to its attack penalty, measured from the effect's origin.

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

### No Cover

### Partial Cover

### Total Cover

### Cover

Targets may also hide behind obstructions to gain cover against your attacks. Obstructions that do not physically block  attacks  but  simply  make  the  target  harder  to  perceiveâ€"such as lighting, fog, or foliageâ€"provide concealment rather than cover.

Partial Cover applies a â€"2 circumstance penalty to your attack check. It generally means about half of the target is behind cover, such as around a corner, behind a tree or pillar, or a low wall.

Total  Cover  applies  a  â€"5  circumstance  penalty  to  your  attack check, with three-quarters or more of the target behind cover.

If a target is completely behind cover, then you cannot attack that target (although you can attack the cover itself).

Cover  also  grants  a  circumstance  bonus  to  Dodge  resistance  checks  against  area  effects  equal  to  its  penalty  to attack checks, so long as the target has cover with respect to the origin point of the effect.
```

---

### surprise

#### Domain Language

- Surprise occurs when one or more characters begin a conflict unaware — typically from failing a Perception or similar check.
- If any characters are surprised, the conflict opens with a surprise round; all characters roll initiative normally.
- Surprised characters do not act during the surprise round; they are stunned and vulnerable until the end of the surprise round.
- Non-surprised characters during the surprise round are limited to a standard action and free actions (may exchange standard for a move action).
- Surprise attacks can occur mid-conflict via stealth, concealment, or unusual maneuvers; the target is vulnerable.

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

Some conflicts begin with one or more characters caught unaware or surprised. This is typically because the character did not succeed on a Perception or other check and was therefore caught off-guard.

If any characters in the conflict are surprised, then the action  begins  with  a  surprise  round.  Everyone  involved  in the conflict makes initiative checks as usual. Surprised characters do not act on the surprise round. They are stunned and vulnerable until the next round. Other characters may act, but are limited to a standard action and free actions, although they may exchange their standard action for a move action, as usual.
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

On  occasions  when  your  attack  catches  a  target  by  surprise,  the  target  is  vulnerable  to  your  attacks.  Surprise attacks occur during the surprise round of a conflict (see Surprise earlier in this chapter) and may also occur as a result of stealth or concealment, allowing you to sneak up on a target. The GM can also grant you a surprise attack for an unusual maneuver that catches the target off-guard.
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

### Team Attack

Multiple attackers can attempt to combine their attacks in order to overwhelm an opponentâ€™s resistance. The attacks to be combined must have the same effect and resistance and be within 5 ranks of each other. So attacks all doing Damage against Toughness can combine, but not with a Mental Blast, for example, which is a Damage effect, but resisted by Will rather than Toughness.

The attackers must all delay to the same point in the initiative order (that of the slowest attacker). Each attacker makes an attack check against the targetâ€™s defense. Effects not requiring an attack check may be used in a team attack; count the effect as having one degree of success, if it is not the main attack.

Take the largest effect rank of the attacks that hit and count the combined degrees of success for the other attacks: one degree  provides  a  +2  circumstance  bonus  to  the  rank  of the main attack, three or more provides a +5 circumstance bonus. Unlike a normal team check, degrees of failure do not reduce success; those attacks simply miss and have no effect.
```

---

### combined attack

#### Domain Language

- Combined attack is the general pattern of multiple combatants coordinating compatible attacks against a single target (the team attack mechanic).
- Contributing attacks must share the same effect type and resistance defense and be within 5 ranks of each other before they can be combined.
- The result is a single composite effect rank boosted by the combined contributions of all participating hits.

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

### Team Attack

Multiple attackers can attempt to combine their attacks in order to overwhelm an opponentâ€™s resistance. The attacks to be combined must have the same effect and resistance and be within 5 ranks of each other.

Take the largest effect rank of the attacks that hit and count the combined degrees of success for the other attacks: one degree  provides  a  +2  circumstance  bonus  to  the  rank  of the main attack, three or more provides a +5 circumstance bonus.
```

---

### minion

#### Domain Language

- A minion is a minor character subject to special rules making them easier to defeat than full characters.
- Minions cannot score critical hits against non-minions.
- Non-minions may make attack checks against minions as routine checks (guaranteed hit with attack bonus ≥ 0).
- If a minion fails any resistance check, they suffer the worst degree of the effect regardless of actual degree of failure.
- Certain advantages (e.g., Takedown) are specifically more effective against or designed for use against minions.
- The GM may roll a single initiative check for an entire minion group.

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

### Minions

Minions  are  minor  characters  subject  to  special  rules  in combat, and generally easier to defeat than normal characters.  Villains  often  employ  hordes  of  minions  against heroes. The following rules apply to minions:

â€¢  Minions  cannot  score  critical  hits  against  non-minions.

â€¢  Non-minions  can  make  attack  checks  against  minions as routine checks.

â€¢  If a minion fails a resistance check, the minion suffers the worst degree of the effect. So a minion failing a Damage  resistance  check,  for  example,  is  incapacitated, regardless of the degree of failure.

â€¢  Certain  traits  (like  the  Takedown  advantage)  are more effective against or specifically target minions.
```

---

## Hazards and Objects

Hazards and Objects covers the non-combat-opponent sources of harm in the game world. Hazards are environmental dangers — falling, suffocation, heat, cold, vacuum, poison, disease, radiation — each governed by a Fortitude (or other) resistance check sequence that escalates conditions from fatigued through dying. Falling has its own damage formula (4 + 2× distance rank, capped at 16). Suffocation uses a breath-holding timer then a per-round Fortitude check. Damaging objects extends the combat system to inanimate targets: objects have Material Toughness values, cannot be dazed or staggered, and require either finishing attacks or repair. This KA interacts with Damage and Resistance (damage rank, Toughness check) and with Tactical Environment (hazards can affect the entire environment). The module owns the combat-facing rules for how hazards work in play; the GM is the authority for what hazards exist in a scene.

#### Decisions made

- hazard, falling, suffocation, damaging objects, and Material Toughness pass both tests — they are all about the non-opponent sources of harm in combat, owned entirely by this module.
- heat, cold, starvation, thirst, poison, disease, and radiation are not listed as separate core terms; they are sub-types of hazard, covered by the hazard term.
- vacuum is treated similarly — it is a hazard sub-type, not a standalone term.

### hazard

#### Domain Language

- Hazards are environmental dangers that harm characters independently of opponent attacks.
- Each hazard uses a resistance check (typically Fortitude) with DC = 10 + rank or a fixed DC; repeated failures escalate: fatigued → exhausted → incapacitated → dying.
- Hazard types include heat/cold, starvation/thirst, suffocation, vacuum, poison, disease, radiation, and falling.
- Immunity effects can negate specific hazard types entirely.
- Hazards may have their own initiative ranks in timed scenarios.

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

Not  all  of  the  hazards  heroes  face  come  from  supervillains. Sometimes the environment itself can be a danger, particularly when villains try to use it to their advantage. Heroes end up in a lot of dangerous places and deal with less than ideal conditions. This section details some of the hazards heroes may face.

### Falling

### Challenges And Initiative

Challenges may or may not involve initiative checks, depending on the nature of the challenge. With other challenges, it does matter who goes first, particularly when the challenge is timed in some fashion. The same may be true of other traps or hazards, which can have initiative ranks of their own.
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

Intense  heat  and  cold  wear  down  characters,  while  prolonged exposure to the elements can be extremely dangerous. Characters in hot or cold conditions must make Fortitude checks (DC 10, +1 per previous check) to avoid becoming fatigued.  Fatigued  characters  who  fail  a  check  become exhausted, then incapacitated, at which point the characterâ€™s condition becomes dying after another failed Fortitude check.

### Starvation And Thirst

Heroes  can  go  without  water  for  a  day.  After  this,  they need to make a Fortitude check (DC 10, +1 per previous check) each hour to avoid a level of fatigue.

### Suffocation

Characters can hold their breath for ten rounds (one minute) plus a number of rounds equal to twice their Stamina. After that time they must make a Fortitude check (DC 10) each round to continue holding their breath. Failure means the character becomes incapacitated. On the following round the character is dying.

### Poison

A deadly toxin may be able to fell the strongest hero. Poisons generally have one of several effects particularly Affliction, Damage, or Weaken. Heroes generally resist poisons with Fortitude.

### Disease

When heroes come into contact with a disease they must make  a  Fortitude  check  (DC  10  +  the  diseaseâ€™s  rank)  to avoid  becoming  infected.

### Radiation

Otherwise the Gamemaster can treat radiation exposure like a disease: The victim makes an initial Fortitude check and an additional check each day.
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

### Radiation Example

Lingering irradiation, Nuclear fallout, Exposure to radioactive materials, Stellar radiation (deep space), Nuclear reactor, Nuclear blast

### Fire Example

Torch, Campfire, Blowtorch, Flame thrower, Burning jet fuel/napalm, Chemical accelerants and fire powers

Radiation sickness is typically a Weaken Stamina effect. At the GMâ€™s discretion, radiation exposure can lead to other effects, such as damage to a heroâ€™s power ranks.
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

On the third round of exposure to vacuum, a character must succeed on a Fortitude check (DC 20) each round or suffer from aeroembolism. A failed check means excruciating pain; the creature is stunned.

The real danger of vacuum comes from suffocation, though holding oneâ€™s breath in vacuum damages the lungs. A character who attempts to hold his breath must make a Fortitude check (DC 15) every round; on a successful check the character loses a rank of Stamina. If the check fails, he begins to suffocate: the next round, he becomes incapacitated. The following round, heâ€™s dying and cannot stabilize until returned to a normal atmosphere.
```

---

### falling

#### Domain Language

- Falling inflicts damage rank = 4 + (2 × distance rank fallen), capped at rank 16.
- Characters with Acrobatics can fall greater distances without injury.
- Falling onto a dangerous surface may inflict additional damage at the GM's discretion.
- Catching a falling character or object requires a Dexterity check (DC 5); the catcher subtracts their Strength rank from falling damage rank — both catcher and caught suffer any remaining damage.
- A power (Flight, Move Object) may substitute its rank for Strength when catching, at the GM's discretion.

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

A fall inflicts damage rank 4 plus twice the distance rank fallen, to a maximum of rank 16 damage. Characters with the Acrobatics skill can fall greater distances without risk of damage. Falling into or onto a dangerous surface may cause additional damage, at the GMâ€™s discretion.

Catching a falling person or object requires a Dexterity check  (DC  5).  If  you  successfully  catch  a  falling  object, subtract  your  Strength  rank  from  the  falling  damage rank. Both you and the object suffer any remaining damage.
```

---

### suffocation

#### Domain Language

- Characters may hold their breath for 10 rounds + (2 × Stamina rank) rounds before needing to check.
- After the limit, Fortitude check (DC 10, +1 per previous success) each round; failure → incapacitated.
- The following round after failure, the character becomes dying and cannot stabilize until able to breathe.
- Holding breath in vacuum additionally risks lung damage: Fortitude DC 15 (+1 per round); success causes loss of one Stamina rank; failure begins suffocation.
- Immunity to Suffocation removes this hazard entirely.

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

### Suffocation

Characters can hold their breath for ten rounds (one minute) plus a number of rounds equal to twice their Stamina. After that time they must make a Fortitude check (DC 10) each round to continue holding their breath. The DC increases  by  +1  for  each  previous  success.  Failure  on  the Fortitude check means the character becomes incapacitated. On the following round the character is dying. A dying character cannot stabilize until able to breathe again. Heroes with Immunity to Suffocation can go an unlimited time without air.
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

A character who attempts to hold his breath must make a Fortitude check (DC 15) every round; the DC increases by 1 each round, and on a successful check the character loses a rank of Stamina (from the pressure on the linings of his lungs). If the check fails, or when the character simply stops holding his breath, he begins to suffocate: the next round, he becomes incapacitated. The following round, heâ€™s dying and cannot stabilize until returned to a normal atmosphere.
```

---

### damaging objects

#### Domain Language

- Objects (targets lacking a Stamina rank) take damage similarly to characters but dazed and staggered results have no practical effect on inanimate targets.
- Inanimate objects are defenseless by definition and subject to finishing attacks: attacker may choose a routine check (auto-hit) or roll normally (auto-crit on any hit for +5 DC).
- Attacking an object held or worn by a character is a smash action (attack vs. character's defense at −5 if held; damage applied to the object).
- Two degrees of failure on the object's Toughness check causes a break; three or more degrees destroys the object.
- Objects cannot recover on their own — they must be repaired (Technology skill).

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

Objects  (targets  lacking  a  Stamina  rank)  take  damage similar to other targets. Dazed and staggered results have no real effect on inanimate targets, since they do not take actions.

Inanimate objects are defenseless by definition and therefore subject to finishing attacks: essentially, you can choose between making your attack on the object as a routine check or, if you make the  attack  check  normally,  gaining  an  automatic  critical hit if your attack hits, for a +5 bonus to effect.

Attacking an object held or worn by another character is a smash action (see the Smash maneuver).

If an attackerâ€™s intention is to bend, break or destroy an object, then two degrees of failure on the Toughness check results  in  a  break while three or more degrees of failure means the object is destroyed.

The  Toughness  ranks  of  some  common  materials  are shown on the Material Toughness table. The listed ranks are for about an inch thickness of the material: apply a +1 per doubling of thickness or a â€"1 per halving of it.

Objects, having no Stamina, do not recover from damage unless they have an effect like Regeneration. Instead, they must be repaired. See the guidelines under the Technology skill when repairing damaged objects.
```

---

### Material Toughness

#### Domain Language

- Material Toughness is the Toughness rank of a common material at approximately one inch (distance rank −7) of thickness.
- Each doubling of thickness adds +1 Toughness; each halving subtracts −1.
- Example ranks: paper/soil 0, glass/ice/rope 1, wood 3, stone 5, iron 7, reinforced concrete 8, steel 9, titanium 15, super-alloys 20+.
- Equipment has Toughness based on its material; devices have base Toughness = total power points ÷ 5 (round down, minimum 1).

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

### Material Toughness

The  Toughness  ranks  of  some  common  materials  are shown on the Material Toughness table. The listed ranks are for about an inch (distance rank â€"7) thickness of the material: apply a +1 per doubling of thickness or a â€"1 per halving of it. So a foot of stone is Toughness 8. Equipment has Toughness based on its material. Devices have a base Toughness equal to the total points in the device divided by 5 (rounded down, minimum of 1).

Material values: Paper 0, Soil 0, Glass 1, Ice 1, Rope 1, Wood 3, Stone 5, Iron 7, Reinforced Concrete 8, Steel 9, Titanium 15, Super-alloys 20+.
```

---

## Hero Resources

Hero Resources are the meta-level economy that gives heroes the ability to transcend normal limits. Hero points are a narrative currency earned through complications and heroic play, spent as reactions to re-roll dice, edit scenes, gain temporary advantages, get inspiration, counter effects, or instantly recover conditions. Extra effort is a within-turn free action that sacrifices the next turn's condition to gain a power boost now — an additional action, a skill bonus, a temporary power rank increase, or a power stunt. Power stunt is the specific extra effort option that instantiates a temporary Alternate Effect of an existing power. All three work together: hero points are the safety net that removes extra effort's fatigue cost, and power stunt is extra effort's most tactically complex option. Hero Resources are not bounded by power level — their effects can exceed what normal powers allow — and they apply as a layer on top of all other combat mechanics, never replacing them.

#### Decisions made

- hero point, extra effort, and power stunt pass both tests — they are fully independent concepts fundamental to the combat loop in MM3E; the existing story map's Consolidation Notes confirm their assignment to this module.
- hero point's non-combat spend types (Edit Scene, Inspiration) are still part of hero point as defined here — the concept is defined whole, not just the combat slice.
- power stunt is kept as its own term (not just a sub-bullet of extra effort) because the partition lists it explicitly and it has its own rules (scene duration, permanent effects exclusion, critical hit free variant).

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

### Extra Effort

Heroes  are  sometimes  called  upon  to  perform  feats  beyond even their amazing abilities. This calls for extra effort. Players can use extra effort to improve a heroâ€™s abilities in exchange for the hero suffering some fatigue. The benefits of extra effort are not limited by power level.

### Using Extra Effort

Players  can  have  their  heroes  use  extra  effort  simply  by declaring  they  are  doing  so.  Extra  effort  is  a  free  action and can be performed at any time during the heroâ€™s turn (but is limited to once per turn). A hero using extra effort gains one of the following benefits:

Action: Gain an additional standard action during your turn.

Bonus: Perform one check with a bonus (+2 circumstance bonus) or improve an existing bonus to a major bonus (+5 circumstance bonus).

Power: Increase one of your heroâ€™s power effects by +1 rank until the start of the heroâ€™s next turn. Permanent effects cannot be increased in this way.

Power Stunt: Temporarily  gain  and  use  an  Alternate  Effect. The  Alternate  Effect lasts until the end of the scene or until its duration expires, whichever comes first. Permanent effects cannot be used for power stunts.

Resistance: Gain an immediate additional resistance check against an ongoing effect.

Retry: Certain effects require extra effort to retry after a certain degree of failure.

Speed: Increase the heroâ€™s speed rank by +1 until the start of the heroâ€™s next turn.

Strength: Increase the heroâ€™s Strength rank by +1 until the start of the heroâ€™s next turn.

### Cost Of Extra Effort

At the start of the turn immediately after using extra effort, the hero becomes fatigued. A fatigued hero who uses extra effort becomes exhausted and an exhausted hero who uses extra effort is incapacitated. If you spend a hero point at the start of the turn following the extra effort to remove the fatigue, the hero suffers no adverse effects.
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

Unless otherwise noted, spending a hero point is a reaction, taking no time, and you can spend as many hero points as you have. You can spend hero points for any of the following:

### Edit Scene

You can â€œeditâ€ a scene to grant your hero an advantage by adding or changing certain details.

### Heroic Feat

You  can  spend  a  hero  point  to  gain  the  benefits  of  one rank of a advantage you donâ€™t already have until the end of your next turn. You must be capable of using the advantage and cannot gain the benefits of fortune advantages, only other types. If the advantage has any prerequisites, you must have them to gain the benefits of the advantage as a heroic feat.

### Hero Points

Players start each game session with 1 hero point. During the adventure they get opportunities to earn more hero points. Unspent hero points donâ€™t carry over to the next adventure; the heroes start out with 1 point again.
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

One hero point allows you to re-roll any die roll you make and take the better of the two rolls. On a result of 1 through 10 on the second roll, add 10 to the result, an 11 or higher remains as-is (so the re-roll is always a result of 11-20). You must spend the hero point to improve a roll before the GM announces the outcome of your initial roll.

### Inspiration

You can spend a hero point to get sudden inspiration in the form of a hint, clue, or bit of help from the GM.

### Instant Counter

You can spend a hero point to attempt to counter an effect  used  against  you  as  a  reaction.

### Recover

You can spend a hero point to recover faster. A hero point allows you to immediately remove a dazed, fatigued, or stunned condition, without taking an action. Spending a hero point to recover also lets you convert an exhausted condition into a fatigued condition.

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

### Using Extra Effort

Extra effort is a free action and can be performed at any time during the heroâ€™s turn (but is limited to once per turn). A hero using extra effort gains one of the following benefits:

Action: Gain an additional standard action during your turn, which can be exchanged for a move or free action, as usual.

Bonus: Perform one check with a bonus (+2 circumstance bonus) or improve an existing bonus to a major bonus (+5 circumstance bonus).

Power: Increase one of your heroâ€™s power effects by +1 rank until the start of the heroâ€™s next turn. Permanent effects cannot be increased in this way.

Power Stunt: Temporarily gain and use an Alternate Effect. The Alternate Effect lasts until the end of the scene or until its duration expires, whichever comes first.

Resistance: Gain an immediate additional resistance check against an ongoing effect.

Speed: Increase the heroâ€™s speed rank by +1 until the start of the heroâ€™s next turn.

Strength: Increase the heroâ€™s Strength rank by +1 until the start of the heroâ€™s next turn.

### Cost Of Extra Effort

At the start of the turn immediately after using extra effort, the hero becomes fatigued. A fatigued hero who uses extra effort becomes exhausted and an exhausted hero who uses extra effort is incapacitated. If you spend a hero point at the start of the turn following the extra effort to remove the fatigue, the hero suffers no adverse effects.
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

### Cost Of Extra Effort

At the start of the turn immediately after using extra effort, the hero becomes fatigued. A fatigued hero who uses extra effort becomes exhausted and an exhausted hero who uses extra effort is incapacitated. If you spend a hero point at the start of the turn following the extra effort to remove the fatigue, the hero suffers no adverse effects. In essence, spending a hero point lets you use extra effort without suffering fatigue.
```

---

### power stunt

#### Domain Language

- A power stunt uses extra effort to temporarily gain an Alternate Effect of one of the hero's existing powers.
- The stunt lasts until the end of the scene or until the effect's normal duration expires, whichever comes first.
- Permanent effects cannot be used as the basis for a power stunt.
- A power stunt gained via a critical hit's Alternate Effect option costs no fatigue.

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

### Power Stunt

Temporarily  gain  and  use  an  Alternate  Effect  (see  Alternate Effect in  the  Powers chapter). The  Alternate  Effect lasts until the end of the scene or until its duration expires, whichever comes first. Permanent effects cannot be used for power stunts.

### Alternate Effect (from Critical Hit)

Alternate  Effect: The  critical  hit  results  in  an  alternate effect for the attack, like a use of extra effort for a power stunt (see Extra Effort in The Basics chapter), except the character suffers no fatigue as a result.
```

---

# Boundary Domain

## condition

Owned by: Check Resolution

#### Domain Language

- Conditions (dazed, staggered, stunned, vulnerable, defenseless, incapacitated, dying, prone, hindered, impaired, etc.) are game-state modifiers imposed by combat outcomes, power effects, and hazards.
- Combat causes, references, and escalates conditions; their authoritative definitions and supersession chains live in Check Resolution.
- The dying and incapacitated conditions are triggered by Toughness resistance check outcomes defined in Combat, but their modifier bundles are owned by Check Resolution.

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

Heroes  run  into  their  share  of  difficulties  in  their  work. One way MUTANTS & MASTERMINDS measures this is with different conditions. They are shorthand for the different game modifiers imposed by things from power effects to injuries or fatigue.

â€¢  Dazed:  A  dazed  character  is  limited  to  free  actions and a single standard action per turn. Stunned supersedes dazed.

â€¢  Stunned: Stunned characters cannot take any actions, including free actions.

â€¢  Vulnerable:  Vulnerable  characters  are  limited  in their  ability  to  defend  themselves,  halving  their  active defenses (round up the final value). Defenseless supersedes vulnerable.

â€¢  Defenseless: A defenseless character has active defense bonuses of 0. Attackers can make attacks on defenseless opponents as routine checks.

â€¢  Hindered: A hindered character moves at half normal speed (â€"1 speed rank). Immobile supersedes hindered.

â€¢  Immobile: Immobile characters have no movement speed.

â€¢  Impaired:  An  impaired  character  is  at  a  â€"2  circumstance penalty on checks.
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

Failure (one degree): The target has a â€"1 circumstance penalty to further resistance checks against damage.
Failure (two degrees): The target is dazed until the end of their next turn.
Failure (three degrees): The target is staggered.
Failure (four degrees): The target is incapacitated.

If an incapacitated target fails a resistance check against Damage, the targetâ€™s condition shifts to dying. A dying target who fails a resistance check against Damage is dead.
```

---

## Toughness

Owned by: Character Construction

#### Domain Language

- Toughness is the physical resistance defense stat used as the basis for all Toughness resistance checks against Damage effects.
- Its rank is set during character construction; temporary −1 penalties from failed Toughness checks accumulate in combat and recover with rest.

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

Success: The damage has no effect.

Failure (one degree): The target has a â€"1 circumstance penalty to further resistance checks against damage.
```

---

## Dodge

Owned by: Character Construction

#### Domain Language

- Dodge is the active defense providing the defense class against ranged attacks (Dodge + 10).
- Combat halves Dodge rank (round up) when a character is vulnerable; reduces it to 0 when defenseless.

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

When you are defenseless, your active defense ranks are reduced to zero, meaning the base difficulty class to hit you is just 10!
```

---

## Parry

Owned by: Character Construction

#### Domain Language

- Parry is the active defense providing the defense class against close attacks (Parry + 10).
- Combat halves Parry rank (round up) when a character is vulnerable; reduces it to 0 when defenseless.

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

Most attacks target your active defenses, Dodge and Parry: close attacks target Parry while ranged attacks target Dodge.

Defense Class = defense + 10

So a hero with Parry 11 has a defense class of 21 (11 + 10) against close attacks. If the same hero has Dodge 9, that is a defense class of 19 (9 + 10) against ranged attacks.
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

When you are vulnerable, your active defense ranks are halved (round up fractions). So the aforementioned hero with Parry 11 and Dodge 9 would have ranks of Parry 6 and Dodge 5 while vulnerable.
```

---

## Fortitude

Owned by: Character Construction

#### Domain Language

- Fortitude is the physical resistance defense used for hazard checks (heat, cold, suffocation, disease, poison, vacuum, radiation) and ongoing physical effect resistance checks.

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

### Heat And Cold

Characters in hot or cold conditions must make Fortitude checks (DC 10, +1 per previous check) to avoid becoming fatigued.

### Suffocation

After that time they must make a Fortitude check (DC 10) each round to continue holding their breath.

### Disease

When heroes come into contact with a disease they must make a Fortitude check (DC 10 + the diseaseâ€™s rank) to avoid becoming infected.
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

On the third round of exposure to vacuum, a character must succeed on a Fortitude check (DC 20) each round or suffer from aeroembolism.

A character who attempts to hold his breath must make a Fortitude check (DC 15) every round.
```

---

## Strength

Owned by: Character Construction

#### Domain Language

- Strength provides a built-in close-range Damage effect; its rank adds to Damage rank for Strength-based weapons.
- Strength is used in grab checks (attacker vs. target Strength or Dodge), disarm opposed checks (damage vs. Strength), trip opposed checks (Acrobatics/Athletics vs. Acrobatics/Athletics), and dragging during grab.

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

Strength provides a â€œbuilt-inâ€ Damage effect: the ability to hit things! You add your Strength and Damage ranks together when determining the rank of the attack.
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

If successful, the target makes a resistance check against your Strength (or the rank of a grabbing effect) using the better of Strength or Dodge.

You can drag a restrained or bound target along with you when you move. The target gets a Strength resistance check against your Strength. If it fails, you move and the target moves along with you.
```

---

## power effect

Owned by: Power

#### Domain Language

- A power effect's rank determines the resistance DC (effect rank + 10 for most; Damage uses effect rank + 15).
- Combat resolves power effects when activated as attacks; area and perception-range effects bypass attack checks and automatically affect targets.

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

An attack check represents an attempt to hit a target with an attack. When you make an attack check, roll the die and add your bonus with that attack. If your result equals or exceeds the targetâ€™s defense, your attack hits and may have some effect.

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

A successful attack has some effect on the target. Typically this is an effect from the Powers chapter, such as Damage or Affliction. The effect has a rank, used to determine a difficulty class for the targetâ€™s resistance check.

Resistance Difficulty = effect rank + 10
```

---

## advantage

Owned by: Advantages

#### Domain Language

- Combat advantages (Improved Initiative, Improved Critical, Takedown, Move-by Action, etc.) modify combat mechanics; their definitions and prerequisites are owned by the Advantages module.
- Heroic Feat (a hero point spend) grants temporary access to one rank of an advantage for one turn.

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

Base  initiative  bonus  is  equal  to the  characterâ€™s  Agility  rank.  Many  characters  have  advantages or powers that modify their initiative, such as Improved Initiative.
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

### Heroic Feat

You  can  spend  a  hero  point  to  gain  the  benefits  of  one rank of a advantage you donâ€™t already have until the end of your next turn. You must be capable of using the advantage and cannot gain the benefits of fortune advantages, only other types. If the advantage has any prerequisites, you must have them to gain the benefits of the advantage as a heroic feat.
```
