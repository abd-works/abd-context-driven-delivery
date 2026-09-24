# Acceptance Criteria — MM3E Advantage Module

Covers all stories from `docs/advantage/story-map.md`. One section per story.
Source module: `docs/advantage/advantage-domain-sketch.md`

---

## Epic: Select Advantages

---

### Sub-Epic: Acquire Advantage

---

#### Story: Purchase Advantage Rank

**Story type:** user

**Domain terms**

- *Advantage* — named special capability purchased with power points at character creation or advancement
- *Advantage Rank* — the scalar level of a ranked advantage; each rank costs 1 power point
- *Ranked Advantage* — an advantage that may be purchased multiple times with cumulative effect
- *Non-ranked Advantage* — an advantage acquired once at effective rank 1; re-purchase is not allowed
- *Advantage Cost* — always 1 power point per rank for any advantage
- *Power Points* — acquisition currency spent to purchase advantage ranks

**Acceptance criteria**

1. **WHEN the player selects a *Ranked Advantage* and specifies a rank on the character sheet**
   **THEN the system records the *Advantage* at that *Advantage Rank* and deducts (rank × 1) *Power Points* from the available budget**
   **AND the character's advantage list displays the *Advantage* name with its rank number (e.g., "Defensive Roll 2")**
   Evidence: HeroesHandbook-rules__chunk_065.md, lines 4107–4148 — Acquiring Advantages; Advantage Cost formula

2. **WHEN the player selects a *Non-ranked Advantage***
   **THEN the system records the *Advantage* at effective rank 1 and deducts exactly 1 *Power Point***
   **BUT the system does not allow the same *Non-ranked Advantage* to be purchased a second time for the same character**
   Evidence: HeroesHandbook-rules__chunk_065.md, lines 4107–4148 — "Some advantages have no ranks and are acquired only once"

3. **WHEN the player increases the *Advantage Rank* of an already-purchased *Ranked Advantage***
   **THEN the system adds the increment to the existing rank and deducts 1 *Power Point* per additional rank**
   **AND the character's advantage list shows the updated rank number**
   Evidence: HeroesHandbook-rules__chunk_065.md, lines 4107–4148 — Advantage Descriptions: ranks notation

4. **WHEN the player attempts to purchase an *Advantage Rank* but the character has insufficient *Power Points***
   **THEN the system blocks the purchase and shows the current *Power Points* total alongside the required *Advantage Cost***
   **BUT no rank is recorded and no *Power Points* are deducted**
   Evidence: HeroesHandbook-rules__chunk_065.md, lines 4107–4148 — Advantage Cost = 1 power point per rank

5. **WHEN a *Ranked Advantage* specifies a maximum rank in its heading (e.g., "Ranked (2)")**
   **THEN the system prevents purchasing a rank that would exceed that declared maximum**
   **AND displays the maximum rank alongside the advantage name**
   Evidence: HeroesHandbook-rules__chunk_065.md, lines 4107–4148 — "If there is a maximum number of ranks... it's listed in parentheses"

---

#### Story: Validate Power Point Cost for Advantage

**Story type:** system

**Domain terms**

- *Advantage Cost* — 1 power point per rank; enforced by the system at the point of purchase
- *Power Points* — the budget from which advantage costs are deducted
- *Cost Formula* — Advantage Cost = 1 power point per advantage rank; applies uniformly to all advantages
- *Purchase Attempt* — a player's request to record an advantage or increase a rank

**Acceptance criteria**

1. **WHEN the system evaluates a *Purchase Attempt* for any advantage**
   **THEN the system applies the *Cost Formula* (1 *Power Point* per rank) uniformly regardless of advantage category or type**
   **AND deducts the correct number of *Power Points* before confirming the purchase**
   Evidence: HeroesHandbook-rules__chunk_065.md, lines 4107–4148 — "Advantages cost 1 power point per rank"

2. **WHEN the system evaluates a *Purchase Attempt* and *Power Points* are exactly sufficient**
   **THEN the system allows the purchase and the available budget reaches zero**
   **BUT the system does not allow a purchase that would leave the *Power Points* budget below zero**
   Evidence: HeroesHandbook-rules__chunk_065.md, lines 4107–4148 — cost formula

3. **WHEN the system processes a purchase of a *Non-ranked Advantage***
   **THEN the system treats the effective rank as 1 and deducts exactly 1 *Power Point* regardless of any other factor**
   Evidence: HeroesHandbook-rules__chunk_065.md, lines 4107–4148 — "acquired only once, effectively at rank 1"

4. **WHEN the player views the character sheet after a purchase**
   **THEN the system displays the updated available *Power Points* balance reflecting all deductions**
   Evidence: HeroesHandbook-rules__chunk_065.md, lines 4107–4148 — purchasing mechanics

---

#### Story: Enforce Power Level Cap on Attack Advantage Bonus

**Story type:** system

**Domain terms**

- *Attack Advantage Bonus* — the flat bonus granted by Close Attack or Ranged Attack per rank (+1/rank)
- *Total Attack Bonus* — sum of all sources contributing to attack checks for a given type (ability, skill, advantage)
- *Power Level Cap* — series-wide ceiling on total attack bonus; owned by Character Construction, consumed here
- *Close Attack* — ranked advantage granting +1 to all close attack checks per rank
- *Ranged Attack* — ranked advantage granting +1 to all ranged attack checks per rank

**Acceptance criteria**

1. **WHEN the system calculates a character's total close attack bonus (including *Close Attack* advantage ranks)**
   **THEN the system compares the total against the *Power Level Cap***
   **AND caps the effective attack bonus at the *Power Level Cap* if the total would exceed it**
   Evidence: HeroesHandbook-rules__chunk_070.md, lines 4451–4494 — "Your total attack bonus is still limited by power level"

2. **WHEN the system calculates a character's total ranged attack bonus (including *Ranged Attack* advantage ranks)**
   **THEN the system applies the same *Power Level Cap* enforcement as for close attacks**
   Evidence: HeroesHandbook-rules__chunk_078.md, lines 4852–4908 — "Your total attack bonus is still limited by power level"

3. **WHEN purchasing additional *Close Attack* or *Ranged Attack* ranks would bring the *Total Attack Bonus* to or below the *Power Level Cap***
   **THEN the system permits the purchase without restriction**
   **AND records the new rank**
   Evidence: HeroesHandbook-rules__chunk_065.md — power level cap applies only at the ceiling

4. **WHEN the system enforces the *Power Level Cap* during combat calculation**
   **THEN the cap is applied to the final total; the advantage ranks themselves remain on the character record unchanged**
   **BUT the capped value — not the raw total — is the attack bonus used in the resolution**
   Evidence: HeroesHandbook-rules__chunk_070.md — power level limits attack checks, not rank storage

5. **WHEN a circumstance bonus from *Favored Environment* or *Favored Foe* is also active**
   **THEN the system applies those circumstance bonuses without applying the *Power Level Cap* to them**
   **AND documents that those bonuses are explicitly exempt from the cap**
   Evidence: HeroesHandbook-rules__chunk_073.md — "This circumstance bonus is not affected by power level"

---

#### Story: Cap Luck Maximum Rank at Half Power Level

**Story type:** system

**Domain terms**

- *Luck* — ranked fortune advantage with a power-level-derived rank ceiling
- *Luck Rank Maximum* — half the series *Power Level* rounded down; the absolute cap on Luck ranks purchasable
- *Series Power Level* — the campaign-wide numeric limit that determines the *Luck Rank Maximum*
- *Rank Cap Enforcement* — system check blocking rank purchases beyond the computed maximum

**Acceptance criteria**

1. **WHEN the system evaluates a purchase of a *Luck* rank**
   **THEN the system computes the *Luck Rank Maximum* as floor(Series Power Level / 2)**
   **AND blocks any purchase that would bring the *Luck* rank above that computed ceiling**
   Evidence: HeroesHandbook-rules__chunk_077.md, lines 4799–4851 — "LUCK FORTUNE, RANKED (1/2 PL)"

2. **WHEN the series *Power Level* is an odd number**
   **THEN the system rounds down the result when computing the *Luck Rank Maximum***
   **AND applies the floor value as the ceiling**
   Evidence: HeroesHandbook-rules__chunk_077.md — "(rounded down)"

3. **WHEN a player's *Luck* rank equals the *Luck Rank Maximum***
   **THEN the system displays the advantage as fully ranked with no further purchase available**
   **BUT the system does not block increases in other advantages**
   Evidence: HeroesHandbook-rules__chunk_077.md — rank (1/2 PL) constraint

4. **WHEN the *Series Power Level* changes (e.g., a campaign upgrades its power level)**
   **THEN the system recalculates the *Luck Rank Maximum* and updates enforcement accordingly**
   Evidence: HeroesHandbook-rules__chunk_077.md — "The GM may choose to set a different limit on ranks in this advantage"

---

### Sub-Epic: Apply Combat Advantage

---

#### Sub-Sub-Epic: Execute Attack Trade-Off Maneuver

---

#### Story: Execute Attack Trade-Off Maneuver (accurate, all-out, defensive, power)

**Story type:** user

**Domain terms**

- *Trade-Off Maneuver* — Accurate Attack, All-out Attack, Defensive Attack, or Power Attack
- *Trade-Off Amount* — the declared penalty/bonus magnitude (1–5); must be declared before the attack roll
- *Effect Modifier* — the offensive power of the attack affected by Accurate Attack and Power Attack
- *Attack Bonus* — the attack check modifier affected by All-out Attack and Defensive Attack (as penalty source) or Accurate Attack and Power Attack (as bonus source)
- *Active Defenses* — Dodge and Parry; affected by All-out Attack (penalty) and Defensive Attack (bonus)
- *Symmetric Exchange* — the core rule: penalty taken must equal bonus gained; neither may exceed 5

**Acceptance criteria**

1. **WHEN the player declares an Accurate Attack and specifies a *Trade-Off Amount* (1–5)**
   **THEN the system accepts the declaration if the *Trade-Off Amount* does not exceed 5**
   **AND records that the attack's *Effect Modifier* is reduced by the *Trade-Off Amount* and the *Attack Bonus* is increased by the same amount for this attack**
   Evidence: HeroesHandbook-rules__chunk_066.md, lines 4149–4188 — "penalty of up to –5 on the effect modifier... add the same number (up to +5) to your attack bonus"

2. **WHEN the player declares an All-out Attack with *Trade-Off Amount* (1–5)**
   **THEN the system reduces both *Active Defenses* (Dodge and Parry) by the *Trade-Off Amount* and increases the *Attack Bonus* by the same amount for this attack**
   Evidence: HeroesHandbook-rules__chunk_066.md — All-out Attack: "penalty of up to –5 on your active defenses... add the same number (up to +5) to your attack bonus"

3. **WHEN the player declares a Defensive Attack with *Trade-Off Amount* (1–5)**
   **THEN the system reduces the *Attack Bonus* by the *Trade-Off Amount* and increases both *Active Defenses* by the same amount for this round**
   Evidence: HeroesHandbook-rules__chunk_071.md, lines 4495–4547 — "penalty of up to –5 on your attack bonus... add the same number (up to +5) to both your active defenses"

4. **WHEN the player declares a Power Attack with *Trade-Off Amount* (1–5)**
   **THEN the system reduces the *Attack Bonus* by the *Trade-Off Amount* and increases the attack's *Effect Modifier* by the same amount**
   Evidence: HeroesHandbook-rules__chunk_078.md, lines 4852–4908 — "penalty of up to –5 on your attack bonus... add the same number (up to +5) to the effect bonus"

5. **WHEN the player attempts to declare a *Trade-Off Amount* greater than 5**
   **THEN the system rejects the declaration and shows that the maximum *Trade-Off Amount* is 5**
   **BUT no modified values are applied to the attack**
   Evidence: HeroesHandbook-rules__chunk_066.md — "up to –5... up to +5" — hard ceiling at 5 in both directions

6. **WHEN the player declares a *Trade-Off Maneuver* without possessing the corresponding advantage**
   **THEN the system does not allow the trade-off and indicates the advantage is required**
   Evidence: HeroesHandbook-rules__chunk_067.md, lines 4189–4286 — combat advantages table; maneuvers require the matching advantage

---

#### Story: Adjust Attack and Defense Values by Trade-Off Amount

**Story type:** system

**Domain terms**

- *Adjusted Attack Bonus* — the attack check value after applying trade-off penalty or bonus for the current attack
- *Adjusted Effect Modifier* — the effect value after applying Accurate or Power Attack trade-off
- *Adjusted Active Defenses* — Dodge and Parry after applying All-out or Defensive Attack trade-off
- *Trade-Off Amount* — the declared magnitude; enforced to be symmetric and ≤5
- *Single-Attack Scope* — the adjustment applies only for the declared attack, not the whole round (except Defensive Attack which grants defense bonus for the round)

**Acceptance criteria**

1. **WHEN the system applies a declared trade-off for this attack**
   **THEN the system modifies the relevant stat exactly by the declared *Trade-Off Amount* — no rounding, no approximation**
   **AND applies the adjustment symmetrically (the same number added to the other stat)**
   Evidence: HeroesHandbook-rules__chunk_066.md, lines 4149–4188 — "take a penalty of up to –5... add the same number"

2. **WHEN the system applies an All-out Attack trade-off penalty**
   **THEN the system reduces both Dodge and Parry by the full *Trade-Off Amount* together — not split between them**
   Evidence: HeroesHandbook-rules__chunk_066.md — "penalty of up to –5 on your active defenses (Dodge and Parry)"

3. **WHEN the system applies a Defensive Attack trade-off bonus**
   **THEN both Dodge and Parry are increased by the full *Trade-Off Amount* for the round**
   Evidence: HeroesHandbook-rules__chunk_071.md — "add the same number (up to +5) to both your active defenses (Dodge and Parry)"

4. **WHEN the current attack resolves**
   **THEN the system reverts the *Adjusted Attack Bonus* and *Adjusted Effect Modifier* to base values for the next attack**
   **BUT Defensive Attack's defense bonus persists until the start of the character's next round**
   Evidence: HeroesHandbook-rules__chunk_067.md — trade-off maneuver scope is the declared attack; Defensive Attack defense bonus is round-scoped

5. **WHEN a *Trade-Off Amount* of 0 is declared**
   **THEN the system allows the maneuver with no adjustment applied**
   **BUT confirms the character still possesses the advantage**
   Evidence: HeroesHandbook-rules__chunk_066.md — "up to –5" implies 0 is valid but trivial

---

### Sub-Sub-Epic: Apply Passive Combat Bonus

---

#### Story: Apply Ranked Attack Bonus to Close or Ranged Attack Check

**Story type:** system

**Domain terms**

- *Close Attack Bonus* — passive +1 per rank to all close attack checks granted by the Close Attack advantage
- *Ranged Attack Bonus* — passive +1 per rank to all ranged attack checks granted by the Ranged Attack advantage
- *Broad Combat Bonus* — applies to all attacks of the relevant type (not limited to one weapon or style)
- *Power Level Cap* — ceiling on total attack bonus; enforced during calculation

**Acceptance criteria**

1. **WHEN the system calculates an attack check for any close attack**
   **THEN the system adds the character's *Close Attack Bonus* (rank × 1) to the total attack bonus automatically**
   **AND applies the sum to the attack roll without requiring player declaration**
   Evidence: HeroesHandbook-rules__chunk_070.md, lines 4451–4494 — "You have a +1 bonus to close attacks checks per rank"

2. **WHEN the system calculates an attack check for any ranged attack**
   **THEN the system adds the character's *Ranged Attack Bonus* (rank × 1) to the total attack bonus automatically**
   Evidence: HeroesHandbook-rules__chunk_078.md, lines 4852–4908 — "You have a +1 bonus to ranged attacks checks per rank"

3. **WHEN the combined total attack bonus would exceed the *Power Level Cap***
   **THEN the system caps the effective attack bonus at the *Power Level Cap***
   **AND the *Broad Combat Bonus* does not override the cap**
   Evidence: HeroesHandbook-rules__chunk_070.md — "Your total attack bonus is still limited by power level"

4. **WHEN the character has both a Close Combat skill bonus and a *Close Attack Bonus***
   **THEN the system adds both to the total attack check for the relevant attack type**
   Evidence: HeroesHandbook-rules__chunk_070.md — "This advantage best suits characters with... overall close combat skill... For capability with a particular type of attack, use the Close Combat skill"

---

#### Story: Apply Initiative Bonus from Improved Initiative

**Story type:** system

**Domain terms**

- *Improved Initiative* — ranked combat advantage granting +4 to initiative checks per rank
- *Initiative Check* — the d20 roll + Agility modifier + *Improved Initiative* bonus that determines combat order
- *Cumulative Bonus* — each rank of Improved Initiative adds +4; Improved Initiative 2 = +8, rank 3 = +12
- *Passive Application* — the bonus is always active; no per-round declaration required

**Acceptance criteria**

1. **WHEN the system resolves initiative at the start of combat**
   **THEN the system adds (Improved Initiative rank × 4) to the character's initiative check total automatically**
   Evidence: HeroesHandbook-rules__chunk_075.md, lines 4705–4748 — "You have a +4 bonus to your initiative checks per rank"

2. **WHEN a character has Improved Initiative 2**
   **THEN the system adds +8 to the initiative check (not +4)**
   **AND each further rank adds an additional +4**
   Evidence: HeroesHandbook-rules__chunk_075.md — "per rank in this advantage" — cumulative stacking

3. **WHEN the initiative check resolves**
   **THEN the character's position in the combat order is determined by the modified result**
   **AND no player declaration is needed to apply the bonus**
   Evidence: HeroesHandbook-rules__chunk_075.md — passive bonus (no maneuver required)

4. **WHEN the character does not possess Improved Initiative**
   **THEN the system does not add any *Improved Initiative* bonus to the initiative check**
   Evidence: HeroesHandbook-rules__chunk_075.md — bonus only applies when the advantage is held

---

#### Story: Apply Extended Critical Threat Range via Improved Critical

**Story type:** system

**Domain terms**

- *Improved Critical* — ranked advantage extending the critical threat range for one specified attack type
- *Critical Threat Range* — the natural die roll values that qualify as critical threats (base: natural 20)
- *Specified Attack* — the attack type bound to the advantage at acquisition (e.g., "unarmed", "blast")
- *Critical Hit* — a successful attack that falls within the *Critical Threat Range*; doubles the effect degree
- *Natural 20 Rule* — only a natural 20 is an automatic hit; an attack that misses is never a critical hit

**Acceptance criteria**

1. **WHEN the system resolves an attack of the *Specified Attack* type**
   **THEN the system checks whether the natural die result falls within the extended *Critical Threat Range* (base 20 minus the rank of Improved Critical)**
   Evidence: HeroesHandbook-rules__chunk_074.md, lines 4659–4704 — "Increase your critical threat range with a particular attack... by 1"

2. **WHEN the natural die result falls within the *Critical Threat Range* AND the attack hits**
   **THEN the system treats the result as a *Critical Hit***
   Evidence: HeroesHandbook-rules__chunk_074.md — threat range check plus success required

3. **WHEN the natural die result falls within the *Critical Threat Range* BUT the attack misses**
   **THEN the system does not treat the roll as a *Critical Hit***
   **BUT still records the miss normally**
   Evidence: HeroesHandbook-rules__chunk_074.md — "an attack that misses is not a critical"

4. **WHEN the character has Improved Critical 4 for a *Specified Attack***
   **THEN the *Critical Threat Range* for that attack is 16–20 (the maximum)**
   **AND the system does not extend the range beyond 16–20 regardless of additional ranks**
   Evidence: HeroesHandbook-rules__chunk_074.md — "to a maximum threat range of 16-20 with 4 ranks"

5. **WHEN the character has multiple ranks of Improved Critical each bound to a different attack**
   **THEN each specified attack has its own independent threat range extension**
   **AND attacks not covered by any Improved Critical rank use the base natural 20 only**
   Evidence: HeroesHandbook-rules__chunk_074.md — "Each additional rank applies to a different attack"

---

### Sub-Sub-Epic: Apply Situational Combat Bonus

---

#### Story: Declare Favored Environment Bonus Allocation

**Story type:** user

**Domain terms**

- *Favored Environment* — a designated environment (air, underwater, space, extreme heat, jungle, etc.) in which the character excels
- *Bonus Allocation* — the round-start choice whether the +2 applies to attack checks or to active defenses (Dodge and Parry)
- *Round Start* — the moment the allocation is declared; the choice is locked until the character's next round start
- *In-Environment Condition* — the character must be operating in their designated environment for any bonus to apply

**Acceptance criteria**

1. **WHEN the character with *Favored Environment* is in their designated environment at the start of a round**
   **THEN the system presents the *Bonus Allocation* choice: attack checks or active defenses**
   **AND the player selects one before any other actions in the round**
   Evidence: HeroesHandbook-rules__chunk_073.md, lines 4614–4658 — "Choose at the start of the round whether the bonus applies to attack or defense"

2. **WHEN the player chooses the attack allocation**
   **THEN the system applies a +2 circumstance bonus to the character's attack checks for the remainder of the round**
   Evidence: HeroesHandbook-rules__chunk_073.md — "you gain a +2 circumstance bonus to attack checks or your active defenses"

3. **WHEN the player chooses the defense allocation**
   **THEN the system applies a +2 circumstance bonus to both Dodge and Parry for the remainder of the round**
   Evidence: HeroesHandbook-rules__chunk_073.md — "+2 circumstance bonus to... your active defenses"

4. **WHEN the character is NOT in their designated environment**
   **THEN the system does not apply any *Favored Environment* bonus and no allocation choice is offered**
   **BUT the advantage remains on the character record for when the environment condition is met**
   Evidence: HeroesHandbook-rules__chunk_073.md — "While you are in your favored environment" — condition required

5. **WHEN the round start has passed and the allocation is locked**
   **THEN the player cannot change the allocation until the next round start**
   Evidence: HeroesHandbook-rules__chunk_073.md — "The choice remains until the start of your next round"

---

#### Story: Apply Favored Environment Circumstance Bonus

**Story type:** system

**Domain terms**

- *Circumstance Bonus* — a +2 bonus applied to the allocated stat (attack or defenses) while in the favored environment
- *Power Level Exemption* — the *Favored Environment* +2 circumstance bonus is explicitly exempt from the power level cap
- *Attack Allocation* — the round-start selection to direct the bonus toward attack checks
- *Defense Allocation* — the round-start selection to direct the bonus toward both Dodge and Parry

**Acceptance criteria**

1. **WHEN the player has declared an *Attack Allocation* and the character makes an attack check this round**
   **THEN the system adds +2 to the attack check result**
   **AND does not apply the power level cap to this +2 bonus**
   Evidence: HeroesHandbook-rules__chunk_073.md — "This circumstance bonus is not affected by power level"

2. **WHEN the player has declared a *Defense Allocation***
   **THEN the system adds +2 to both Dodge and Parry for the remainder of the round**
   **AND does not apply the power level cap to these +2 bonuses**
   Evidence: HeroesHandbook-rules__chunk_073.md — circumstance bonus not limited by power level

3. **WHEN multiple circumstance bonuses apply (e.g., Favored Environment + another source)**
   **THEN the system stacks them if they are from different sources per normal circumstance bonus rules**
   Evidence: HeroesHandbook-rules__chunk_073.md — standard MM3E circumstance stacking rules apply

4. **WHEN the character leaves the favored environment mid-round**
   **THEN the system removes the bonus immediately upon leaving**
   **BUT the allocation choice for that round is not transferred to a later round**
   Evidence: HeroesHandbook-rules__chunk_073.md — "While you are in your favored environment" — condition is continuous

---

### Sub-Epic: Activate Fortune Advantage

---

#### Story: Re-Roll Die Using Luck Rank

**Story type:** user

**Domain terms**

- *Luck* — fortune advantage with a per-session re-roll pool limited to Luck rank uses
- *Luck Rank Use* — one consumed use from the session pool; drawn when the player invokes a re-roll
- *Re-Roll* — replacing a die roll with a new roll; if the new result is 10 or less, 10 is added to it
- *Session Pool* — the stock of uses available this session; limited to the current Luck rank

**Acceptance criteria**

1. **WHEN the player invokes *Luck* to re-roll a die result during a round**
   **THEN the system rolls the die again**
   **AND if the new result is 10 or less, the system adds 10 to it (same as a hero point re-roll)**
   Evidence: HeroesHandbook-rules__chunk_077.md, lines 4799–4851 — "re-roll a die roll... including adding 10 to re-rolls of 10 or less"

2. **WHEN the system applies the re-roll**
   **THEN it consumes exactly 1 *Luck Rank Use* from the *Session Pool***
   **AND updates the displayed remaining uses**
   Evidence: HeroesHandbook-rules__chunk_077.md — "You can do this a number of times per game session equal to your Luck rank"

3. **WHEN the player attempts to invoke *Luck* but the *Session Pool* is empty (0 uses remaining)**
   **THEN the system blocks the re-roll and notifies the player that no Luck uses remain this session**
   **BUT the original die result stands unchanged**
   Evidence: HeroesHandbook-rules__chunk_077.md — limited to rank uses per session

4. **WHEN the player invokes *Luck* a second time in the same round**
   **THEN the system blocks the second invocation for this round**
   **AND informs the player that Luck may be used only once per round**
   Evidence: HeroesHandbook-rules__chunk_077.md — "Once per round, you can choose to re-roll a die roll"

5. **WHEN the character does not possess the *Luck* advantage**
   **THEN the re-roll mechanic is not available via *Luck***
   Evidence: HeroesHandbook-rules__chunk_077.md — advantage must be held

---

#### Story: Enforce Luck Session-Use Limit and Refresh at Adventure Start

**Story type:** system

**Domain terms**

- *Session Pool* — the per-session stock of Luck uses; size equals current Luck rank
- *Session-Use Limit* — the cap on uses per session; equals the Luck rank (which is itself capped at half power level)
- *Luck Rank Refresh* — restoring the *Session Pool* to full (= Luck rank) at adventure start
- *Adventure Start* — the moment hero points reset; this also triggers the Luck refresh

**Acceptance criteria**

1. **WHEN the adventure (session) begins**
   **THEN the system initializes the *Session Pool* at the current Luck rank (e.g., Luck 3 → 3 uses available)**
   Evidence: HeroesHandbook-rules__chunk_077.md, lines 4799–4851 — "number of times per game session equal to your Luck rank"

2. **WHEN each *Luck Rank Use* is consumed**
   **THEN the system decrements the *Session Pool* by 1 and displays the new remaining count**
   **AND blocks any further *Luck* invocations when the pool reaches 0**
   Evidence: HeroesHandbook-rules__chunk_077.md — session pool mechanics

3. **WHEN an adventure ends and a new adventure begins (hero points reset)**
   **THEN the system restores the *Session Pool* to the full Luck rank value**
   **AND the prior session's used count is discarded**
   Evidence: HeroesHandbook-rules__chunk_077.md — "Your Luck ranks refresh when your hero points 'reset' at the start of an adventure"

4. **WHEN the Luck rank is increased between adventures**
   **THEN the system recomputes the *Session Pool* maximum to the new rank at the next refresh**
   Evidence: HeroesHandbook-rules__chunk_077.md — session pool size is always the current rank

5. **WHEN the *Luck Rank Maximum* (half power level) constrains the rank**
   **THEN the *Session Pool* never exceeds that rank cap regardless of any other setting**
   Evidence: HeroesHandbook-rules__chunk_077.md — "maximum rank of half the series power level (rounded down)"

---

#### Story: Inspire Allies with Hero Point

**Story type:** user

**Domain terms**

- *Inspire* — ranked fortune advantage (max rank 5) granting allies a circumstance bonus when activated
- *Hero Point Spend* — the activation cost; one hero point is consumed
- *Standard Action* — the action type required to activate Inspire
- *Allies in Range* — allies who can interact with the activating character at activation time
- *Inspiration Bonus* — +1 per Inspire rank on all checks; max +5

**Acceptance criteria**

1. **WHEN the player spends a hero point and takes a standard action to activate *Inspire***
   **THEN the system grants all *Allies in Range* a +1 per Inspire rank circumstance bonus on all checks**
   **AND the bonus lasts until the start of the activating character's next round**
   Evidence: HeroesHandbook-rules__chunk_076.md, lines 4749–4798 — "Once per scene, by taking a standard action and spending a hero point, allies... gain a +1 circumstance bonus per Inspire rank"

2. **WHEN the *Inspiration Bonus* is calculated**
   **THEN the system caps the bonus at +5 (Inspire rank is capped at 5)**
   Evidence: HeroesHandbook-rules__chunk_076.md — "with a maximum bonus of +5"

3. **WHEN the activating character performs their own checks during the inspired round**
   **THEN the system does not apply the *Inspiration Bonus* to the activating character's own checks**
   **BUT applies it fully to all qualifying allies**
   Evidence: HeroesHandbook-rules__chunk_076.md — "You do not gain the bonus, only your allies do"

4. **WHEN a second character also activates *Inspire* in the same round**
   **THEN the system applies only the highest *Inspiration Bonus* — multiple Inspire effects do not stack**
   Evidence: HeroesHandbook-rules__chunk_076.md — "Multiple uses of Inspire do not stack, only the highest bonus applies"

---

#### Story: Apply Inspiration Bonus Ignoring Power Level Cap

**Story type:** system

**Domain terms**

- *Inspiration Bonus* — the circumstance bonus (up to +5) granted to allies by the *Inspire* advantage
- *Power Level Cap Exemption* — the *Inspiration Bonus* explicitly bypasses the series power level limit
- *Ally Checks* — any checks made by allies who can interact with the activating character during the bonus window

**Acceptance criteria**

1. **WHEN the system applies the *Inspiration Bonus* to an ally's check**
   **THEN the system does not apply the series *Power Level Cap* to this bonus**
   **AND the full +N bonus (up to +5) is added regardless of the total with cap**
   Evidence: HeroesHandbook-rules__chunk_076.md, lines 4749–4798 — "The inspiration bonus ignores power level limits, like other uses of hero points"

2. **WHEN the ally's check total including the *Inspiration Bonus* would exceed the power level cap**
   **THEN the system still allows the full bonus because of the explicit exemption**
   **AND documents the exemption so it is clear why the cap is not applied**
   Evidence: HeroesHandbook-rules__chunk_076.md — "ignores power level limits"

3. **WHEN the *Inspiration Bonus* window expires (start of activating character's next round)**
   **THEN the system removes the *Inspiration Bonus* from all allies' check totals**
   Evidence: HeroesHandbook-rules__chunk_076.md — "until the start of your next round"

4. **WHEN the Inspire activation is not followed by a standard action (e.g., if only a move action is available)**
   **THEN the system does not apply the *Inspiration Bonus***
   **BUT no hero point is consumed either**
   Evidence: HeroesHandbook-rules__chunk_076.md — "by taking a standard action and spending a hero point"

---

#### Story: Remove Ally Condition via Leadership

**Story type:** user

**Domain terms**

- *Leadership* — fortune advantage allowing removal of one debilitating condition from an ally
- *Hero Point Spend* — the activation cost; one hero point consumed
- *Standard Action* — the action type required to activate *Leadership*
- *Eligible Condition* — one of the three removable conditions: dazed, fatigued, or stunned
- *Interaction Range* — the range within which the ally must be for *Leadership* to apply

**Acceptance criteria**

1. **WHEN the player spends a hero point and takes a standard action to activate *Leadership***
   **THEN the system removes exactly one *Eligible Condition* (dazed, fatigued, or stunned) from one ally within *Interaction Range***
   Evidence: HeroesHandbook-rules__chunk_077.md, lines 4799–4851 — "spend a hero point to remove one of the following conditions from an ally: dazed, fatigued, or stunned"

2. **WHEN the player activates *Leadership* on an ally who has multiple *Eligible Conditions***
   **THEN the player selects which single condition to remove and the system removes only that one**
   Evidence: HeroesHandbook-rules__chunk_077.md — "remove one of the following conditions"

3. **WHEN the ally has a condition that is NOT one of the three *Eligible Conditions***
   **THEN the system cannot remove it via *Leadership***
   **BUT the player may still remove an *Eligible Condition* if the ally also has one**
   Evidence: HeroesHandbook-rules__chunk_077.md — only dazed, fatigued, stunned are eligible

4. **WHEN no ally within *Interaction Range* has an *Eligible Condition***
   **THEN the player may choose not to spend the hero point**
   **BUT the system may still allow the activation with no effect if the player insists**
   Evidence: HeroesHandbook-rules__chunk_077.md — activation requires a qualifying target

5. **WHEN the ally is outside *Interaction Range***
   **THEN the system does not allow *Leadership* to affect that ally**
   Evidence: HeroesHandbook-rules__chunk_077.md — "an ally with whom you can interact"

---

#### Story: Gain Temporary Skill Ranks via Beginner's Luck

**Story type:** user

**Domain terms**

- *Beginner's Luck* — fortune advantage granting effective rank 5 in one chosen skill for a scene
- *Hero Point Spend* — the activation cost; one hero point consumed
- *Qualifying Skill* — any skill the character currently has at 4 or fewer ranks (including 0 ranks, including normally untrained-restricted skills)
- *Temporary Rank 5* — effective rank 5 granted by the advantage; lasts for the scene duration only
- *Scene Duration* — the scene in which Beginner's Luck is activated; temporary ranks expire at scene end

**Acceptance criteria**

1. **WHEN the player spends a hero point to activate *Beginner's Luck* and selects a *Qualifying Skill***
   **THEN the system grants effective rank 5 in that skill for the current scene**
   **AND the player can use the skill as if they have rank 5, including skills that normally cannot be used untrained**
   Evidence: HeroesHandbook-rules__chunk_069.md, lines 4337–4450 — "you gain an effective 5 ranks in one skill of your choice you currently have at 4 or fewer ranks"

2. **WHEN the scene ends**
   **THEN the system removes the temporary rank 5 from the character's skill total**
   **AND the skill returns to its pre-activation rank**
   Evidence: HeroesHandbook-rules__chunk_069.md — "These temporary skill ranks last for the duration of the scene"

3. **WHEN the player attempts to select a skill where the character already has 5 or more ranks**
   **THEN the system rejects the selection and indicates the skill does not qualify**
   **BUT other skills at 4 or fewer ranks remain available choices**
   Evidence: HeroesHandbook-rules__chunk_069.md — "you currently have at 4 or fewer ranks"

4. **WHEN the temporary rank 5 is active**
   **THEN the system treats the character as rank 5 for all skill-related checks in that scene including prerequisites**
   **BUT the character does not gain permanent ranks; advancement records are unchanged**
   Evidence: HeroesHandbook-rules__chunk_069.md — "temporary skill ranks... grant you their normal benefits"

---

### Sub-Epic: Use Skill Advantage

---

#### Story: Use Any Skill Untrained via Jack of All Trades

**Story type:** user

**Domain terms**

- *Jack of All Trades* — skill advantage removing the trained restriction for all skills
- *Untrained Use* — attempting a skill check without any ranks invested in that skill
- *Training Restriction* — the rule preventing untrained use of certain skills or skill aspects
- *Tool Requirement* — a separate prerequisite (still applies even with *Jack of All Trades*)
- *Trained Barrier Removed* — the effect of the advantage; tool requirements are NOT removed

**Acceptance criteria**

1. **WHEN a character with *Jack of All Trades* attempts a skill that normally requires training**
   **THEN the system allows the skill check without penalizing for lack of ranks**
   **AND the character rolls the base ability modifier (no skill rank bonus if truly untrained)**
   Evidence: HeroesHandbook-rules__chunk_069.md, lines 4337–4450 — "You can use any skill untrained, even skills or aspects of skills that normally cannot be used untrained"

2. **WHEN the skill requires tools and the character lacks those tools**
   **THEN the system still applies the tool requirement penalty regardless of *Jack of All Trades***
   **BUT does not apply a separate untrained penalty**
   Evidence: HeroesHandbook-rules__chunk_069.md — "you must still have proper tools if the skill requires them"

3. **WHEN the character has ranks in a skill and also holds *Jack of All Trades***
   **THEN *Jack of All Trades* provides no additional benefit for that skill (ranks already exist)**
   Evidence: HeroesHandbook-rules__chunk_069.md — advantage removes training barrier, not rank benefit

4. **WHEN a character without *Jack of All Trades* attempts an untrained-restricted skill**
   **THEN the system blocks the check or applies the standard untrained penalty as appropriate**
   Evidence: HeroesHandbook-rules__chunk_069.md — the advantage removes what normally blocks untrained use

---

#### Story: Make Routine Skill Check Under Pressure via Skill Mastery

**Story type:** user

**Domain terms**

- *Skill Mastery* — skill advantage removing the pressure restriction for one designated skill
- *Routine Check* — rolling 10 on the d20 in place of a die roll; normally not allowed under pressure
- *Pressure* — a stressful or time-critical situation where routine checks are normally barred
- *Designated Skill* — the specific skill bound to this Skill Mastery advantage at acquisition
- *Categorical Prohibition* — skills that never allow routine checks regardless of conditions; not overridden by Skill Mastery

**Acceptance criteria**

1. **WHEN a character with *Skill Mastery* is in a *Pressure* situation and uses the *Designated Skill***
   **THEN the system allows a *Routine Check* (treating the d20 as 10) for that skill**
   Evidence: HeroesHandbook-rules__chunk_069.md, lines 4337–4450 — "make routine checks with one skill even under pressure"

2. **WHEN the player attempts a routine check on a non-designated skill while under pressure**
   **THEN the system blocks the routine check for that skill; Skill Mastery applies only to the *Designated Skill***
   Evidence: HeroesHandbook-rules__chunk_069.md — advantage applies to "one skill" specified at acquisition

3. **WHEN the *Designated Skill* has a *Categorical Prohibition* against routine checks**
   **THEN *Skill Mastery* does not override that prohibition**
   **BUT the system still allows normal die rolls for that skill**
   Evidence: HeroesHandbook-rules__chunk_069.md — "skills that can never be routine checks regardless"

4. **WHEN *Skill Mastery* is acquired multiple times for different skills**
   **THEN each instance applies to its own *Designated Skill* independently**
   Evidence: HeroesHandbook-rules__chunk_069.md — "This advantage may be taken multiple times, each time selecting a different skill"

---

#### Story: Apply Favored Foe Circumstance Bonus to Qualifying Checks

**Story type:** system

**Domain terms**

- *Favored Foe* — skill advantage granting +2 circumstance bonus against a designated opponent type
- *Favored Foe Type* — a creature type or profession approved by the GM at acquisition; cannot be overly broad
- *Qualifying Check* — one of the four eligible checks: Deception, Intimidation, Insight, Perception
- *Circumstance Bonus* — the +2 bonus applied; not subject to the power level cap
- *Non-qualifying Check* — any check other than the four listed; *Favored Foe* bonus does not apply

**Acceptance criteria**

1. **WHEN the character makes a Deception, Intimidation, Insight, or Perception check involving their *Favored Foe***
   **THEN the system applies a +2 circumstance bonus to that check**
   **AND does not limit the bonus by the series power level cap**
   Evidence: HeroesHandbook-rules__chunk_073.md, lines 4614–4658 — "You gain a +2 circumstance bonus on Deception, Intimidation, Insight, and Perception checks dealing with your Favored Foe. This circumstance bonus is not limited by power level."

2. **WHEN the check involves a target that is NOT of the *Favored Foe Type***
   **THEN the system does not apply the *Favored Foe* bonus**
   Evidence: HeroesHandbook-rules__chunk_073.md — "dealing with your Favored Foe" — target must match

3. **WHEN the character makes a check other than the four *Qualifying Checks* against their *Favored Foe***
   **THEN the system does not apply the *Favored Foe* bonus to that check**
   Evidence: HeroesHandbook-rules__chunk_073.md — bonus applies to exactly Deception, Intimidation, Insight, Perception

4. **WHEN the *Favored Foe Type* was defined too broadly (e.g., "humans" or "villains") at acquisition**
   **THEN the system flags the entry as requiring GM approval before the bonus applies**
   **BUT the advantage is still recorded on the character sheet pending approval**
   Evidence: HeroesHandbook-rules__chunk_073.md — "Especially broad categories like 'humans' or 'villains' are not permitted"

5. **WHEN the character's attack or combat check against a *Favored Foe* is not one of the four listed skills**
   **THEN no *Favored Foe* bonus is applied to that combat check**
   Evidence: HeroesHandbook-rules__chunk_073.md — bonus is skill-based (4 specified skills); not a general attack bonus

---

### Sub-Epic: Manage Character Resources

---

#### Sub-Sub-Epic: Configure Equipment

---

#### Story: Allocate Equipment Points to Gear

**Story type:** user

**Domain terms**

- *Equipment* — ranked general advantage granting 5 equipment points per rank
- *Equipment Points* — the budget derived from rank × 5; used to purchase gear items
- *Gear Item* — any weapon, armor, vehicle, headquarters, or other equipment purchased with points
- *Equipment Point Budget* — total points available = Advantage Rank × 5

**Acceptance criteria**

1. **WHEN the player opens the equipment allocation screen with the *Equipment* advantage active**
   **THEN the system displays the total *Equipment Point Budget* (rank × 5)**
   **AND shows the current allocation and remaining unspent points**
   Evidence: HeroesHandbook-rules__chunk_069.md — "You have 5 points per rank in this advantage to spend on equipment"

2. **WHEN the player selects a *Gear Item* and allocates points to it**
   **THEN the system deducts the item's point cost from the remaining *Equipment Point Budget***
   **AND adds the item to the character's gear list**
   Evidence: HeroesHandbook-rules__chunk_069.md — "spend on equipment... vehicles and headquarters"

3. **WHEN the player removes a previously allocated *Gear Item***
   **THEN the system returns the item's cost to the *Equipment Point Budget***
   **AND removes the item from the gear list**
   Evidence: HeroesHandbook-rules__chunk_069.md — equipment points are re-allocatable during character construction

4. **WHEN the player attempts to purchase a *Gear Item* whose cost exceeds remaining budget**
   **THEN the system blocks the purchase and shows the shortfall**
   **BUT does not modify the current allocation**
   Evidence: HeroesHandbook-rules__chunk_069.md — budget constraint

---

#### Story: Enforce Equipment Point Budget from Rank

**Story type:** system

**Domain terms**

- *Equipment Point Budget* — total available points = Equipment rank × 5; maintained by the system
- *Budget Ceiling* — the maximum points available; any attempt to exceed this is blocked
- *Rank Increase* — when the *Equipment* advantage rank increases, the budget ceiling increases by 5

**Acceptance criteria**

1. **WHEN the system calculates the *Equipment Point Budget***
   **THEN the system computes it as (Equipment advantage rank × 5) — no other formula applies**
   Evidence: HeroesHandbook-rules__chunk_069.md — "5 points per rank in this advantage"

2. **WHEN the total cost of allocated gear equals the *Budget Ceiling***
   **THEN the system does not allow further gear purchases until the rank increases**
   **AND displays the budget as fully spent**
   Evidence: HeroesHandbook-rules__chunk_069.md — budget ceiling hard constraint

3. **WHEN the *Equipment* advantage rank increases during advancement**
   **THEN the system increases the *Equipment Point Budget* by 5 and makes the additional points available**
   Evidence: HeroesHandbook-rules__chunk_069.md — rank × 5 scaling

4. **WHEN gear is described as subject to loss or destruction**
   **THEN the system notes that *Equipment* is not a power effect and gear may be removed from the character record when lost or destroyed**
   **BUT the equipment point budget is unaffected by in-game gear loss (the advantage rank stays)**
   Evidence: HeroesHandbook-rules__chunk_069.md — "Many heroes rely almost solely on Equipment... in conjunction with their skills"

---

#### Sub-Sub-Epic: Manage Minion

---

#### Story: Configure Minion Traits Within Power Point Budget

**Story type:** user

**Domain terms**

- *Minion* — ranked general advantage granting an independent follower character
- *Minion Power Point Budget* — rank × 15 power points for the minion character
- *Power Level Limits* — the minion's traits are subject to series power level constraints
- *Helpful Attitude* — minions capable of independent thought are automatically helpful toward the owner

**Acceptance criteria**

1. **WHEN the player opens the minion configuration screen**
   **THEN the system displays the *Minion Power Point Budget* (rank × 15) and the current allocation**
   **AND allows the player to assign traits within that budget**
   Evidence: HeroesHandbook-rules__chunk_077.md, lines 4799–4851 — "power point total of (advantage rank x 15)"

2. **WHEN the player assigns traits to the minion**
   **THEN the system enforces that the total trait cost does not exceed the *Minion Power Point Budget***
   **AND applies series *Power Level Limits* to the minion's trait values**
   Evidence: HeroesHandbook-rules__chunk_077.md — "Minions are subject to the normal power level limits"

3. **WHEN the minion is fully configured**
   **THEN the system records the minion as an independent character linked to the owner**
   **AND marks the minion with *Helpful Attitude* if it is capable of independent thought**
   Evidence: HeroesHandbook-rules__chunk_077.md — "Your minions... automatically have a helpful attitude toward you"

4. **WHEN the player attempts to give the minion its own Minion advantage**
   **THEN the system blocks this — minions cannot have minions**
   Evidence: HeroesHandbook-rules__chunk_077.md — "cannot have minions themselves"

---

#### Story: Enforce Minion Power Level Limits

**Story type:** system

**Domain terms**

- *Minion Power Level Limits* — the series power level cap applied to the minion's traits
- *Minion Character* — the independent character built on the Minion advantage's point budget
- *Hero Points Restriction* — minions never have hero points; system enforces this

**Acceptance criteria**

1. **WHEN the system validates the minion's trait assignments**
   **THEN it applies series power level limits to attack bonuses, defenses, and effect ranks for the minion**
   **AND rejects any trait that would exceed those limits**
   Evidence: HeroesHandbook-rules__chunk_077.md — "Minions are subject to the normal power level limits"

2. **WHEN the system initializes the minion's resource pool**
   **THEN the system gives the minion no hero points**
   **AND blocks any attempt to give the minion hero points through any mechanism**
   Evidence: HeroesHandbook-rules__chunk_077.md — "Minions also do not have hero points"

3. **WHEN the minion attempts to take a Minion advantage of its own**
   **THEN the system blocks this configuration**
   **AND informs the player that minions cannot have minions**
   Evidence: HeroesHandbook-rules__chunk_077.md — "cannot have minions themselves"

---

#### Story: Replace Lost Minion Between Adventures

**Story type:** system

**Domain terms**

- *Lost Minion* — a minion that has been incapacitated, destroyed, or otherwise removed during an adventure
- *Between Adventures* — the downtime period between sessions when the replacement occurs
- *Replacement Minion* — a new minion with the same traits and budget as the original, approved by the GM

**Acceptance criteria**

1. **WHEN a minion is lost during an adventure**
   **THEN the system marks the minion as lost on the character record**
   **BUT does not remove the Minion advantage rank or reduce the owner's power points**
   Evidence: HeroesHandbook-rules__chunk_077.md — "Any lost minions are replaced in between adventures"

2. **WHEN a new adventure begins (the between-adventures period concludes)**
   **THEN the system prompts the player to configure a replacement minion within the existing budget**
   **AND the replacement minion has similar abilities to the original at the GM's discretion**
   Evidence: HeroesHandbook-rules__chunk_077.md — "replaced in between adventures with other followers with similar abilities at the Gamemaster's discretion"

3. **WHEN the lost minion is replaced**
   **THEN the system records the new minion and removes the "lost" flag from the character record**
   Evidence: HeroesHandbook-rules__chunk_077.md — replacement restores the minion slot

4. **WHEN the player attempts to immediately replace a lost minion during the same adventure**
   **THEN the system defers replacement to the between-adventures period**
   **BUT the owner retains the Minion advantage rank and its associated power point budget**
   Evidence: HeroesHandbook-rules__chunk_077.md — "in between adventures" — not mid-adventure

---

#### Story: Spend Power Points to Improve Minion Rank

**Story type:** user

**Domain terms**

- *Minion Rank Improvement* — increasing the Minion advantage rank, which expands the minion's power point budget
- *Owner's Power Points* — the earned power points the owner spends to buy the rank increase
- *New Minion Budget* — new rank × 15 power points after the rank increase

**Acceptance criteria**

1. **WHEN the player spends earned power points to increase the Minion advantage rank**
   **THEN the system deducts 1 power point per new rank from the owner's earned pool**
   **AND increases the *Minion Power Point Budget* by 15 (new total = new rank × 15)**
   Evidence: HeroesHandbook-rules__chunk_077.md — "you must spend earned power points to increase your rank in this advantage"

2. **WHEN the new *Minion Power Point Budget* is available**
   **THEN the player can assign the additional 15 points to new or upgraded traits in the minion's character**
   Evidence: HeroesHandbook-rules__chunk_077.md — higher rank → bigger budget

3. **WHEN the owner does not have sufficient earned power points**
   **THEN the system blocks the rank increase**
   **AND shows the available earned power points versus the cost**
   Evidence: HeroesHandbook-rules__chunk_077.md — "spend earned power points"

---

#### Sub-Sub-Epic: Manage Sidekick

---

#### Story: Configure Sidekick Traits Within Power Point Budget

**Story type:** user

**Domain terms**

- *Sidekick* — ranked general advantage granting a partner character built with rank × 5 power points
- *Sidekick Power Point Budget* — rank × 5 power points available for sidekick trait assignment
- *Sidekick Character* — a full character (not a minion) under shared GM/player control
- *Owner's Total* — the owning character's own power point total; the sidekick's total must stay below it

**Acceptance criteria**

1. **WHEN the player opens the sidekick configuration screen**
   **THEN the system displays the *Sidekick Power Point Budget* (rank × 5) and allows trait assignment within that budget**
   Evidence: HeroesHandbook-rules__chunk_077.md, lines 4799–4851 — "sidekick with (5 x rank) power points"

2. **WHEN the player assigns traits to the sidekick**
   **THEN the system validates that total trait cost does not exceed the *Sidekick Power Point Budget***
   **AND applies series power level limits to the sidekick's traits**
   Evidence: HeroesHandbook-rules__chunk_077.md — sidekick is subject to series power level

3. **WHEN the sidekick's total power point spend equals the *Owner's Total***
   **THEN the system flags a violation — the sidekick's total must remain strictly less than the owner's**
   **AND prompts the player to reduce the sidekick's budget allocation**
   Evidence: HeroesHandbook-rules__chunk_077.md — "a sidekick with... power points... subject to series power level"

4. **WHEN the sidekick configuration is complete**
   **THEN the system records the sidekick as a linked full character (not a minion)**
   **AND does not apply minion rules to the sidekick**
   Evidence: HeroesHandbook-rules__chunk_077.md — "They are not minions but full characters"

---

#### Story: Enforce Sidekick Power Point Total Below Owner Total

**Story type:** system

**Domain terms**

- *Sidekick Power Point Total* — the total power points spent on the sidekick character's traits
- *Owner's Power Point Total* — the owning character's own total; the sidekick must always stay below this
- *Below-Owner Constraint* — the rule enforced by the system at all times, not just at configuration

**Acceptance criteria**

1. **WHEN the system validates the sidekick's power point allocation**
   **THEN the system confirms that the *Sidekick Power Point Total* is strictly less than the *Owner's Power Point Total***
   **AND blocks any configuration that would make them equal or greater**
   Evidence: HeroesHandbook-rules__chunk_077.md — "power point total... subject to series power level"

2. **WHEN the owner's total decreases (e.g., a complication)**
   **THEN the system checks whether the sidekick's total now violates the *Below-Owner Constraint***
   **AND flags the violation for GM resolution if it does**
   Evidence: HeroesHandbook-rules__chunk_077.md — constraint is ongoing, not just at setup

3. **WHEN the Sidekick advantage rank increases and the new budget (rank × 5) would violate the constraint**
   **THEN the system warns the player before recording the rank increase**
   Evidence: HeroesHandbook-rules__chunk_077.md — budget grows with rank; constraint must hold

---

#### Story: Spend Hero Point on Sidekick's Behalf

**Story type:** user

**Domain terms**

- *Sidekick* — the partner character that can receive hero point benefits from the owner
- *Proxy Hero Point* — a hero point spent from the owner's pool on the sidekick's behalf
- *Hero Point Benefits* — standard effects of spending a hero point (re-roll, recover, etc.) — applied to the sidekick

**Acceptance criteria**

1. **WHEN the player spends a hero point from the owner's pool on behalf of the sidekick**
   **THEN the system applies the selected *Hero Point Benefits* to the sidekick**
   **AND deducts 1 hero point from the owner's pool (not the sidekick's)**
   Evidence: HeroesHandbook-rules__chunk_077.md — "The hero with a sidekick can spend hero points on the sidekick's behalf"

2. **WHEN the sidekick's own hero point pool is checked**
   **THEN the system confirms the sidekick has no independent hero points**
   **BUT can receive the effects of hero points spent by the owner**
   Evidence: HeroesHandbook-rules__chunk_077.md — "Sidekicks themselves do not have hero points"

3. **WHEN the owner has no hero points available**
   **THEN the system cannot proxy a hero point to the sidekick**
   **AND the sidekick cannot benefit from hero point effects in that situation**
   Evidence: HeroesHandbook-rules__chunk_077.md — benefits come from owner's pool

---

#### Story: Spend Power Points to Improve Sidekick Rank

**Story type:** user

**Domain terms**

- *Sidekick Rank Improvement* — increasing the Sidekick advantage rank, granting 5 additional power points per rank
- *Owner's Earned Power Points* — the pool from which the rank improvement is purchased
- *Expanded Sidekick Budget* — new rank × 5 power points for the sidekick's trait improvement

**Acceptance criteria**

1. **WHEN the player spends earned power points to increase the Sidekick advantage rank**
   **THEN the system deducts 1 power point per new rank from the owner's earned pool**
   **AND increases the sidekick's available power point budget by 5 (new total = new rank × 5)**
   Evidence: HeroesHandbook-rules__chunk_077.md — "spend earned power points to improve the sidekick"

2. **WHEN the *Expanded Sidekick Budget* is available**
   **THEN the player can assign the additional 5 points to new or upgraded traits in the sidekick's character**
   **AND the *Below-Owner Constraint* is re-checked after assignment**
   Evidence: HeroesHandbook-rules__chunk_077.md — rank increase = budget increase; constraint always enforced

3. **WHEN the owner lacks sufficient earned power points**
   **THEN the system blocks the rank increase and shows the shortfall**
   Evidence: HeroesHandbook-rules__chunk_077.md — "spend earned power points"

---

#### Sub-Sub-Epic: Establish Benefit

---

#### Story: Propose Benefit to GM

**Story type:** user

**Domain terms**

- *Benefit* — ranked general advantage representing a narrative perquisite cooperatively defined with the GM
- *Benefit Description* — the player-authored text describing the specific benefit claimed
- *GM Approval* — the required gate before a *Benefit* takes effect
- *Value Ceiling* — the proposed benefit must not exceed any other single advantage or a 1-point power effect

**Acceptance criteria**

1. **WHEN the player selects the *Benefit* advantage and enters a *Benefit Description***
   **THEN the system records the description and marks the benefit as pending GM review**
   **AND deducts 1 power point per rank provisionally (subject to GM approval)**
   Evidence: HeroesHandbook-rules__chunk_069.md, lines 4337–4450 — "significant perquisite or fringe benefit... for you and the Gamemaster to determine"

2. **WHEN the player submits the *Benefit Description***
   **THEN the system validates that the proposed benefit does not reference routine professional credentials (e.g., law or medicine license) as the sole benefit**
   **AND flags such submissions for GM attention if they appear insufficient**
   Evidence: HeroesHandbook-rules__chunk_069.md — "A license to practice law or medicine... should not be considered a Benefit"

3. **WHEN the player proposes a *Benefit* in multiple ranks (e.g., Benefit 2)**
   **THEN the system records the description as a ranked benefit with escalating effect**
   **AND deducts 1 power point per rank provisionally**
   Evidence: HeroesHandbook-rules__chunk_069.md — "Benefits may come in ranks for improved levels of the same benefit"

4. **WHEN the *Benefit Description* appears to exceed the *Value Ceiling***
   **THEN the system surfaces a warning that the GM should evaluate whether the benefit is within bounds**
   Evidence: HeroesHandbook-rules__chunk_069.md — "should not exceed the benefits of any other advantage, or a power effect costing 1 point"

---

#### Story: Approve or Reject Benefit Definition

**Story type:** GM

**Domain terms**

- *GM Approval* — the Gamemaster's explicit decision on whether a proposed *Benefit* is valid
- *Approved Benefit* — a benefit whose description is confirmed as within the *Value Ceiling* and series tone
- *Rejected Benefit* — a benefit the GM deems out of scope, excessive, or inappropriate for the series
- *Value Ceiling* — no *Benefit* may exceed the value of any other advantage or a 1-point power effect

**Acceptance criteria**

1. **WHEN the GM reviews a pending *Benefit* submission**
   **THEN the system presents the *Benefit Description* alongside the *Value Ceiling* guidance**
   **AND offers Approve or Reject actions**
   Evidence: HeroesHandbook-rules__chunk_069.md — "The GM is the final arbiter as to what does and does not constitute a Benefit"

2. **WHEN the GM approves the benefit**
   **THEN the system marks the *Benefit* as *Approved Benefit* and activates it on the character sheet**
   **AND the power points provisionally deducted are confirmed**
   Evidence: HeroesHandbook-rules__chunk_069.md — GM approval gates the benefit taking effect

3. **WHEN the GM rejects the benefit**
   **THEN the system marks the entry as *Rejected Benefit*, removes it from the active advantage list, and refunds the provisionally deducted power points**
   **AND prompts the player to propose an alternative if desired**
   Evidence: HeroesHandbook-rules__chunk_069.md — GM may reject; player can resubmit

4. **WHEN a *Benefit* in multiple ranks is approved**
   **THEN the system activates all ranks together and records all deducted power points as confirmed**
   Evidence: HeroesHandbook-rules__chunk_069.md — ranks are part of one benefit definition

---

### Sub-Epic: Maintain Advantage State

---

#### Story: Persist Advantage Selections on Character Sheet

**Story type:** system

**Domain terms**

- *Advantage Selections* — the complete set of advantages chosen for the character, including ranks and parameters
- *Character Sheet* — the persistent record of the character's current state
- *Advantage Parameters* — per-advantage specifics such as the Favored Foe type, Improved Critical attack, or Skill Mastery skill
- *Advantage State* — the stored representation of each advantage including name, rank, category, and parameters

**Acceptance criteria**

1. **WHEN the player finalizes an advantage selection**
   **THEN the system persists the *Advantage State* (name, category, rank, parameters) to the *Character Sheet***
   **AND the *Advantage Selections* survive session reload without loss**
   Evidence: HeroesHandbook-rules__chunk_065.md — advantages persist as part of the character record

2. **WHEN an advantage has per-instance parameters (Favored Foe type, Improved Critical attack, Skill Mastery skill)**
   **THEN the system stores those *Advantage Parameters* alongside the advantage name and rank**
   **AND the parameters are displayed with the advantage on the character sheet**
   Evidence: HeroesHandbook-rules__chunk_073.md; HeroesHandbook-rules__chunk_074.md; HeroesHandbook-rules__chunk_069.md — parameter-bound advantages

3. **WHEN the player removes an advantage during advancement revision**
   **THEN the system removes the *Advantage State* from the *Character Sheet* and refunds the power points**
   Evidence: HeroesHandbook-rules__chunk_065.md — character advancement rules

4. **WHEN the character sheet is loaded by another user (GM viewing player sheet)**
   **THEN the *Advantage Selections* are displayed correctly with all ranks and parameters**
   **AND no advantage is missing or incorrectly ranked**
   Evidence: HeroesHandbook-rules__chunk_065.md — shared character record

---

#### Story: Track Luck Rank Uses per Session

**Story type:** system

**Domain terms**

- *Luck Session Counter* — the per-session tally of Luck uses consumed this session
- *Session Pool* — the stock of uses available this session; equals Luck rank at session start
- *Use Event* — the moment a player invokes Luck; increments the counter and decrements the pool
- *Session Boundary* — the start/end of an in-game adventure session

**Acceptance criteria**

1. **WHEN the session begins**
   **THEN the system initializes the *Luck Session Counter* to 0 and the *Session Pool* to the current Luck rank**
   Evidence: HeroesHandbook-rules__chunk_077.md — "You can do this a number of times per game session equal to your Luck rank"

2. **WHEN a *Use Event* is recorded**
   **THEN the system increments the *Luck Session Counter* by 1 and decrements the *Session Pool* by 1**
   **AND the character sheet reflects the new remaining count in real time**
   Evidence: HeroesHandbook-rules__chunk_077.md — session tracking of uses

3. **WHEN the *Session Pool* reaches 0**
   **THEN the system disables Luck activation for this session and shows "Luck uses exhausted"**
   **AND does not allow further Luck re-rolls until the next adventure start**
   Evidence: HeroesHandbook-rules__chunk_077.md — limited to rank uses per session

4. **WHEN the session ends without reaching the pool limit**
   **THEN the system preserves the current *Luck Session Counter* until the adventure-start refresh**
   Evidence: HeroesHandbook-rules__chunk_077.md — unused uses do not carry over in a meaningful way; they are simply replaced at refresh

---

#### Story: Refresh Luck Ranks at Start of Adventure

**Story type:** system

**Domain terms**

- *Adventure Start* — the moment a new adventure begins; coincides with hero point reset
- *Luck Refresh* — the restoration of the *Session Pool* to full (= current Luck rank) at *Adventure Start*
- *Hero Point Reset* — the trigger event for *Luck Refresh*; owned by Character Construction

**Acceptance criteria**

1. **WHEN hero points reset at the start of a new adventure**
   **THEN the system simultaneously refreshes the Luck *Session Pool* to the current Luck rank**
   **AND clears the *Luck Session Counter* to 0**
   Evidence: HeroesHandbook-rules__chunk_077.md — "Your Luck ranks refresh when your hero points 'reset' at the start of an adventure"

2. **WHEN the Luck rank has increased since the last refresh**
   **THEN the system refreshes the *Session Pool* to the new (higher) Luck rank value**
   Evidence: HeroesHandbook-rules__chunk_077.md — pool = current rank at refresh time

3. **WHEN the refresh occurs**
   **THEN the character sheet shows the Luck advantage with its full *Session Pool* available**
   **AND the refresh timestamp or "Full" indicator is visible to both player and GM**
   Evidence: HeroesHandbook-rules__chunk_077.md — session tracking requires visibility

4. **WHEN the adventure continues without a formal adventure-start event (mid-campaign continuation)**
   **THEN the system does not refresh Luck uses until an explicit adventure-start trigger occurs**
   **BUT the GM may manually trigger a refresh through a GM override mechanism**
   Evidence: HeroesHandbook-rules__chunk_077.md — "The GM may choose to set a different limit on ranks in this advantage" — GM authority over refresh rules

---
