---
state: domain-language
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

---

# Core Domain

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

**Ref — Skill Basics**
Source: context/rules/HeroesHandbook-rules__chunk_042.md
Locator: lines 2736-2796
Extract: whole

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

**Ref — Skill Basics**
Source: context/rules/HeroesHandbook-rules__chunk_042.md
Locator: lines 2736-2796
Extract: whole

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

**Ref — Skill Basics**
Source: context/rules/HeroesHandbook-rules__chunk_042.md
Locator: lines 2736-2796
Extract: whole

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

**Ref — Manipulation Skills**
Source: context/rules/HeroesHandbook-rules__chunk_043.md
Locator: lines 2797-2849
Extract: whole

---

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

---

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

**Ref — Ranged Combat**
Source: context/rules/HeroesHandbook-rules__chunk_059.md
Locator: lines 3762-3826
Extract: partial
Part: Sleight of Hand example referencing Skill Mastery for Stealth.

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

**Ref — Finding The Skill You Want**
Source: context/rules/HeroesHandbook-rules__chunk_044.md
Locator: lines 2850-2893
Extract: whole

---

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

**Ref — Balancing Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_045.md
Locator: lines 2894-2994
Extract: whole

**Ref — Climbing Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_046.md
Locator: lines 2995-3065
Extract: whole

**Ref — Acrobatics Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_047.md
Locator: lines 3066-3117
Extract: whole

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

**Ref — Swimming**
Source: context/rules/HeroesHandbook-rules__chunk_048.md
Locator: lines 3118-3168
Extract: whole

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

**Ref — Deception Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_049.md
Locator: lines 3169-3225
Extract: whole

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

**Ref — Life Skills**
Source: context/rules/HeroesHandbook-rules__chunk_050.md
Locator: lines 3226-3283
Extract: whole

**Ref — Innuendo Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_051.md
Locator: lines 3284-3373
Extract: whole

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

**Ref — Resist Influence**
Source: context/rules/HeroesHandbook-rules__chunk_053.md
Locator: lines 3441-3484
Extract: whole

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

**Ref — Intimidating Minions**
Source: context/rules/HeroesHandbook-rules__chunk_054.md
Locator: lines 3485-3527
Extract: whole

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

**Ref — Search Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_055.md
Locator: lines 3528-3571
Extract: whole

**Ref — Evidence Difficulties**
Source: context/rules/HeroesHandbook-rules__chunk_056.md
Locator: lines 3572-3638
Extract: whole

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

**Ref — Stealth**
Source: context/rules/HeroesHandbook-rules__chunk_060.md
Locator: lines 3827-3895
Extract: whole

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

**Ref — Building Items**
Source: context/rules/HeroesHandbook-rules__chunk_062.md
Locator: lines 3944-3994
Extract: whole

**Ref — Security Levels**
Source: context/rules/HeroesHandbook-rules__chunk_063.md
Locator: lines 3995-4045
Extract: whole

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

**Ref — Provide Care**
Source: context/rules/HeroesHandbook-rules__chunk_064.md
Locator: lines 4046-4106
Extract: whole

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

**Ref — Provide Care**
Source: context/rules/HeroesHandbook-rules__chunk_064.md
Locator: lines 4046-4106
Extract: whole

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

**Ref — Manipulation Skills**
Source: context/rules/HeroesHandbook-rules__chunk_043.md
Locator: lines 2797-2849
Extract: whole

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
