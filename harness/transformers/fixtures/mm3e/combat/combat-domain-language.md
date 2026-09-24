---
state: domain-language
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

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195-1237
Extract: whole

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

**Ref — Taking Actions**
Source: context/rules/HeroesHandbook-rules__chunk_198.md
Locator: lines 14175-14218
Extract: whole

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

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195-1237
Extract: whole

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

**Ref — Taking Actions**
Source: context/rules/HeroesHandbook-rules__chunk_198.md
Locator: lines 14175-14218
Extract: whole

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

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195-1237
Extract: whole

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

**Ref — Reactions**
Source: context/rules/HeroesHandbook-rules__chunk_017.md
Locator: lines 1238-1344
Extract: whole

---

### attack check

#### Domain Language

- An attack check determines whether an attack hits: d20 + attack bonus vs. target's defense class; equal or exceeding means a hit.
- A natural 20 on the d20 always hits regardless of defense and may be a critical hit.
- A natural 1 on the d20 always misses regardless of the total — reflecting combat's unpredictability.
- Area and perception-range effects do not require attack checks; they automatically affect the target or area and cannot score critical hits or misses.

#### References

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195-1237
Extract: whole

**Ref — Conflicts**
Source: context/rules/HeroesHandbook-rules__chunk_202.md
Locator: lines 14386-14434
Extract: whole

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

**Ref — Standard Action**
Source: context/rules/HeroesHandbook-rules__chunk_214.md
Locator: lines 14999-15043
Extract: whole

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

**Ref — Vulnerable And Defenseless**
Source: context/rules/HeroesHandbook-rules__chunk_209.md
Locator: lines 14791-14830
Extract: whole

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

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195-1237
Extract: whole

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

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195-1237
Extract: whole

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

**Ref — Critical Misses**
Source: context/rules/HeroesHandbook-rules__chunk_203.md
Locator: lines 14435-14489
Extract: whole

---

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

**Ref — Vulnerable And Defenseless**
Source: context/rules/HeroesHandbook-rules__chunk_209.md
Locator: lines 14791-14830
Extract: whole

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

**Ref — Example Of Conflict**
Source: context/rules/HeroesHandbook-rules__chunk_204.md
Locator: lines 14490-14552
Extract: whole

**Ref — Example Of Conflict**
Source: context/rules/HeroesHandbook-rules__chunk_205.md
Locator: lines 14553-14630
Extract: whole

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

**Ref — Recovery**
Source: context/rules/HeroesHandbook-rules__chunk_216.md
Locator: lines 15092-15151
Extract: whole

---

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

**Ref — Light And Darkness**
Source: context/rules/HeroesHandbook-rules__chunk_200.md
Locator: lines 14260-14332
Extract: whole

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

**Ref — Lasting Injuries**
Source: context/rules/HeroesHandbook-rules__chunk_216.md
Locator: lines 15092-15151
Extract: whole

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

---

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

**Ref — Standard Action**
Source: context/rules/HeroesHandbook-rules__chunk_214.md
Locator: lines 14999-15043
Extract: whole

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

**Ref — Lasting Injuries**
Source: context/rules/HeroesHandbook-rules__chunk_216.md
Locator: lines 15092-15151
Extract: whole

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

---

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

**Ref — Light And Darkness**
Source: context/rules/HeroesHandbook-rules__chunk_200.md
Locator: lines 14260-14332
Extract: whole

**Ref — Radiation Example**
Source: context/rules/HeroesHandbook-rules__chunk_201.md
Locator: lines 14333-14385
Extract: whole

**Ref — Vacuum**
Source: context/rules/HeroesHandbook-rules__chunk_202.md
Locator: lines 14386-14434
Extract: whole

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

**Ref — Vacuum**
Source: context/rules/HeroesHandbook-rules__chunk_202.md
Locator: lines 14386-14434
Extract: whole

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

**Ref — Lasting Injuries**
Source: context/rules/HeroesHandbook-rules__chunk_216.md
Locator: lines 15092-15151
Extract: whole

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

**Ref — Vacuum**
Source: context/rules/HeroesHandbook-rules__chunk_202.md
Locator: lines 14386-14434
Extract: whole

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

**Ref — Recovery**
Source: context/rules/HeroesHandbook-rules__chunk_207.md
Locator: lines 14690-14737
Extract: whole

**Ref — Recovery**
Source: context/rules/HeroesHandbook-rules__chunk_216.md
Locator: lines 15092-15151
Extract: whole

---

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

**Ref — Using Hero Points**
Source: context/rules/HeroesHandbook-rules__chunk_020.md
Locator: lines 1476-1515
Extract: whole

**Ref — Improve Roll**
Source: context/rules/HeroesHandbook-rules__chunk_021.md
Locator: lines 1516-1555
Extract: whole

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

**Ref — Using Hero Points**
Source: context/rules/HeroesHandbook-rules__chunk_020.md
Locator: lines 1476-1515
Extract: whole

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

**Ref — Critical Misses**
Source: context/rules/HeroesHandbook-rules__chunk_203.md
Locator: lines 14435-14489
Extract: whole

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

**Ref — Vulnerable And Defenseless**
Source: context/rules/HeroesHandbook-rules__chunk_209.md
Locator: lines 14791-14830
Extract: whole

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

**Ref — Vulnerable And Defenseless**
Source: context/rules/HeroesHandbook-rules__chunk_209.md
Locator: lines 14791-14830
Extract: whole

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

**Ref — Vacuum**
Source: context/rules/HeroesHandbook-rules__chunk_202.md
Locator: lines 14386-14434
Extract: whole

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

**Ref — Drop An Item**
Source: context/rules/HeroesHandbook-rules__chunk_212.md
Locator: lines 14915-14958
Extract: whole

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

**Ref — Vulnerable And Defenseless**
Source: context/rules/HeroesHandbook-rules__chunk_209.md
Locator: lines 14791-14830
Extract: whole

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

**Ref — Using Hero Points**
Source: context/rules/HeroesHandbook-rules__chunk_020.md
Locator: lines 1476-1515
Extract: whole
