# Acceptance Criteria — Power Module (Exploration)

Module scope: Power effects (Affliction through Weaken), power types, action/range/duration defaults, Extras, Flaws, Descriptors, and modifier math.
Actors: **Player** (human building/playing a hero), **GM** (Gamemaster), **System** (rules engine / application).

---

## Epic: Configure Attack Effect

---

## Story: Select Affliction Effect and Configure Condition Set

**Story type:** user

### Domain terms

- *Affliction* — Attack effect that imposes progressive conditions on failed resistance checks
- *Condition Set* — the three ordered conditions chosen at acquisition (degree 1, 2, 3)
- *Resistance Type* — Fortitude or Will; chosen at acquisition and fixed thereafter
- *Degree of Failure* — how far the target failed the resistance check; maps to condition tier
- *Third-Degree Condition* — the most severe condition; requires special recovery after effect ends

### Acceptance criteria

1. **WHEN** the Player selects the *Affliction* effect for a power  
   **THEN** the system prompts for exactly three conditions in degree order (first, second, third)  
   **AND** the system prompts for a *Resistance Type* (Fortitude or Will) to be fixed at acquisition  
   **AND** the configured *Affliction* displays as type Attack, action Standard, range Close, cost 1 pp/rank  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — Affliction effect: conditions, degrees, resistance, recovery

2. **WHEN** the Player specifies fewer than three conditions or leaves any degree blank  
   **THEN** the system rejects the configuration  
   **BUT** no *Affliction* effect is saved with an incomplete *Condition Set*  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — Affliction requires exactly three conditions in degree order

3. **WHEN** the *Condition Set* is configured with all three conditions in valid degree order  
   **THEN** the system confirms the *Affliction* is ready to add to the power  
   **AND** the *Resistance Type* is locked and cannot be changed without rebuilding the effect  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — Affliction: resistance chosen at acquisition

4. **WHEN** the Player attempts to set condition 3 as less severe than condition 2  
   **THEN** the system alerts that conditions must be progressively worse per degree  
   **BUT** does not save the configuration until the degree ordering is corrected  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — each condition must be progressively worse

5. **WHEN** the Player reviews the configured *Affliction*  
   **THEN** the display shows condition 1 at first degree, condition 2 at second, condition 3 at third  
   **AND** the *Resistance Type* is shown alongside the effect stat block  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — three-condition structure with degree mapping

---

## Story: Select Damage Effect for Close Combat

**Story type:** user

### Domain terms

- *Damage* — foundational Attack effect for close-range physical harm
- *Toughness DC* — resistance check difficulty; equals 15 + Damage rank
- *Damage Condition* — one of four progressive harm states applied on failed Toughness check
- *Strength Bonus* — character's Strength rank added to unarmed Damage

### Acceptance criteria

1. **WHEN** the Player selects the *Damage* effect for a power  
   **THEN** the system configures it as type Attack, action Standard, range Close, resistance Toughness, cost 1 pp/rank  
   **AND** the *Toughness DC* is displayed as 15 + effect rank  
   **Evidence:** HeroesHandbook-rules__chunk_097.md — Damage effect stat block and DC formula

2. **WHEN** the *Damage* effect is used for an unarmed attack  
   **THEN** the system adds the character's Strength rank to the *Damage* rank for the *Toughness DC*  
   **AND** the stacked total is used as the final DC value  
   **Evidence:** HeroesHandbook-rules__chunk_097.md — Damage stacks with Strength for unarmed

3. **WHEN** the Player reviews the *Damage* effect  
   **THEN** the system shows range as Close by default  
   **AND** an informational note indicates the Ranged extra converts it to Blast at 2 pp/rank  
   **Evidence:** HeroesHandbook-rules__chunk_097.md — Damage is Close range; Ranged extra required for Blast

4. **WHEN** the Player wants ranged damage capability  
   **THEN** the system directs the Player to apply the Ranged extra rather than treating *Damage* as Ranged natively  
   **BUT** does not allow the *Damage* effect to be configured as Ranged without the extra  
   **Evidence:** HeroesHandbook-rules__chunk_097.md — Damage has Close range by default

---

## Story: Select Blast Effect for Ranged Energy Attack

**Story type:** user

### Domain terms

- *Blast* — Damage with Ranged extra preconfigured; 2 pp/rank
- *Ranged Attack Check* — required attack roll vs. target's Dodge defense
- *Toughness Check* — target resistance; DC = 15 + effect rank

### Acceptance criteria

1. **WHEN** the Player selects the *Blast* effect configuration  
   **THEN** the system presents it as Damage (1 pp/rank) + Ranged extra (1 pp/rank) = 2 pp/rank total  
   **AND** the attack type is set to Ranged, requiring a *Ranged Attack Check* vs. Dodge  
   **Evidence:** HeroesHandbook-rules__chunk_090.md — Blast is Damage + Ranged extra; 2 pp/rank

2. **WHEN** a *Blast* attack hits  
   **THEN** the target makes a *Toughness Check* against DC 15 + *Blast* rank  
   **AND** *Damage Conditions* apply per degree of failure using the standard Damage table  
   **Evidence:** HeroesHandbook-rules__chunk_090.md — Blast resistance is Toughness; DC 15 + rank

3. **WHEN** the Player reviews the *Blast* cost  
   **THEN** the system confirms the 2 pp/rank cost is pre-calculated (no additional modifiers needed to reach Ranged)  
   **Evidence:** HeroesHandbook-rules__chunk_090.md — Blast is a named combination; cost already factored

4. **WHEN** the Player applies additional extras to *Blast*  
   **THEN** the system calculates from the 2 pp/rank base, not from Damage's 1 pp/rank base  
   **Evidence:** HeroesHandbook-rules__chunk_082.md — modifier math applies to current cost per rank

---

## Story: Select Deflect Effect for Ranged Protection

**Story type:** user

### Domain terms

- *Deflect* — Defense effect that substitutes its rank for the protected target's active defense
- *Active Defense Value* — Dodge or Parry; replaced by Deflect rank during interception
- *Range Penalty* — penalty applied for medium or long range interceptions

### Acceptance criteria

1. **WHEN** the Player selects the *Deflect* effect  
   **THEN** the system configures it as type Defense, action Standard, range Ranged, cost 1 pp/rank  
   **AND** notes that it intercepts incoming ranged attacks as its primary function  
   **Evidence:** HeroesHandbook-rules__chunk_087.md — Deflect entry in power effects summary table

2. **WHEN** the Player configures *Deflect* to protect nearby allies  
   **THEN** the system confirms *Deflect* rank substitutes for the ally's active defense during interception  
   **AND** the character must use their Standard action to activate the interception  
   **Evidence:** HeroesHandbook-rules__chunk_087.md — Deflect substitutes defense value; protects others in range

3. **WHEN** the target of interception is at medium or long range  
   **THEN** the system applies the standard *Range Penalty* to the *Deflect* rank used as defense  
   **Evidence:** HeroesHandbook-rules__chunk_087.md — range penalties apply at medium and long range

4. **WHEN** the Player reviews *Deflect*  
   **THEN** the system notes the Reaction extra is required to use *Deflect* as a free reaction  
   **BUT** by default *Deflect* costs a Standard action to activate  
   **Evidence:** HeroesHandbook-rules__chunk_087.md — Standard action by default; Reaction extra available

---

## Story: Select Nullify Effect and Define Target Descriptor

**Story type:** user

### Domain terms

- *Nullify* — Attack effect that suppresses power effects matching a chosen descriptor
- *Target Descriptor* — the descriptor(s) the Nullify can counter; defined at acquisition
- *Opposed Check* — Nullify rank vs. target effect rank (or Will); determines success
- *Counter State* — effect is turned off; target may reactivate on next action

### Acceptance criteria

1. **WHEN** the Player selects the *Nullify* effect  
   **THEN** the system prompts for a *Target Descriptor* to define what effects this Nullify suppresses  
   **AND** configures it as type Attack, action Standard, range Ranged, cost 1 pp/rank  
   **Evidence:** HeroesHandbook-rules__chunk_125.md — Nullify: descriptor targeting at acquisition

2. **WHEN** the *Target Descriptor* is defined  
   **THEN** the system displays the full Nullify sequence: ranged attack check → opposed check (Nullify rank vs. effect rank or Will)  
   **AND** notes that success puts the targeted effect into *Counter State*  
   **Evidence:** HeroesHandbook-rules__chunk_125.md — Nullify attack check then opposed check sequence

3. **WHEN** the Player wants to expand targeting to multiple effects simultaneously  
   **THEN** the system notes the Broad extra covers all effects of a type and the Simultaneous extra allows multiple effects at once  
   **BUT** base Nullify targets only one active effect per use without these extras  
   **Evidence:** HeroesHandbook-rules__chunk_125.md — Broad and Simultaneous extras for wider targeting

4. **WHEN** *Nullify* succeeds against a sustained effect  
   **THEN** the countered effect is turned off; the target can attempt to reactivate on their next action  
   **Evidence:** HeroesHandbook-rules__chunk_125.md — success counters the effect; reactivation on next action

5. **WHEN** *Nullify* succeeds against a permanent effect  
   **THEN** the countered effect is suppressed for one round only; it cannot be "destroyed" permanently  
   **BUT** Nullify does not remove the effect from the target permanently  
   **Evidence:** HeroesHandbook-rules__chunk_125.md — Nullify suppresses, does not destroy

---

## Story: Select Weaken Effect and Define Target Trait

**Story type:** user

### Domain terms

- *Weaken* — Attack effect that temporarily reduces a target trait
- *Target Trait* — the specific trait reduced; chosen at acquisition
- *Reduction Amount* — equals degree of failure on resistance check, up to Weaken rank maximum
- *Cumulative Stacking* — multiple Weaken applications stack up to rank maximum

### Acceptance criteria

1. **WHEN** the Player selects the *Weaken* effect  
   **THEN** the system prompts for the *Target Trait* to be reduced and the resistance type (Fortitude or Will)  
   **AND** configures it as type Attack, action Standard, range Close, cost 1 pp/rank  
   **Evidence:** HeroesHandbook-rules__chunk_139.md — Weaken: trait chosen at acquisition; Fort or Will resistance

2. **WHEN** the *Target Trait* is defined  
   **THEN** the system confirms *Weaken* is cumulative — repeat applications stack up to the rank maximum  
   **AND** shows the recovery rule: target recovers 1 point of the reduced trait per round automatically  
   **Evidence:** HeroesHandbook-rules__chunk_139.md — cumulative to rank maximum; 1 point/round auto-recovery

3. **WHEN** the Player reviews the *Weaken* configuration  
   **THEN** the system shows that reduction = degree of failure on the resistance check, capped at *Weaken* rank  
   **Evidence:** HeroesHandbook-rules__chunk_139.md — reduction equals degree of failure, up to rank maximum

4. **WHEN** a second *Weaken* application would push total reduction beyond the rank maximum  
   **THEN** the system caps the total reduction at the *Weaken* rank  
   **BUT** does not apply additional reduction beyond the cap  
   **Evidence:** HeroesHandbook-rules__chunk_139.md — Weaken cumulative to rank maximum; no effect beyond cap

---

## Story: Resolve Affliction Resistance Check and Apply Condition Degree

**Story type:** system

### Domain terms

- *Resistance Check* — Fort or Will roll made by the target; result determines degree of failure
- *Condition Degree* — one, two, or three tiers of condition applied on failure
- *Applied Condition* — game state placed on target per the configured Condition Set
- *Degree of Failure* — how many points the check missed the DC by; maps to condition tier

### Acceptance criteria

1. **WHEN** an *Affliction* attack hits its target  
   **THEN** the system prompts (or resolves) the target's resistance check (Fortitude or Will vs. *Affliction* rank + 10)  
   **AND** maps the result to a *Condition Degree*: success = no condition, miss by ≤ 4 = first degree, miss by 5–9 = second degree, miss by ≥ 10 = third degree  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — Affliction: degree-of-failure mapping to conditions

2. **WHEN** the target fails the resistance check by first degree  
   **THEN** the system applies condition 1 from the *Condition Set*  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — first-degree failure applies first condition

3. **WHEN** the target fails by second degree  
   **THEN** the system applies both condition 1 and condition 2 cumulatively  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — conditions are cumulative per degree

4. **WHEN** the target fails by third degree  
   **THEN** the system applies all three conditions  
   **AND** flags the target for special recovery rules (requires full minute or outside aid after effect ends)  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — third-degree full condition set; special recovery required

5. **WHEN** the target succeeds the resistance check  
   **THEN** no condition is applied  
   **BUT** the attack is not negated — the target simply resisted the Affliction  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — resistance check success = no conditions applied

---

## Story: Recover from Affliction Condition at End of Turn

**Story type:** system

### Domain terms

- *End-of-Turn Recovery Check* — resistance check the target makes at end of each of their turns
- *Degree Removal* — one degree of condition removed on recovery success
- *Third-Degree Recovery Rule* — special requirement: one minute (or outside aid) after Affliction ends

### Acceptance criteria

1. **WHEN** a target has one or more *Affliction* conditions active  
   **THEN** the system triggers an *End-of-Turn Recovery Check* for the target at the end of each of their turns  
   **AND** on success, removes one condition degree starting from the worst  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — end-of-turn recovery check; removes one degree on success

2. **WHEN** the recovery check succeeds and removes the third-degree condition  
   **THEN** the target still retains second-degree and first-degree conditions  
   **AND** must succeed additional checks to recover those as well  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — removal is one degree per success, from worst

3. **WHEN** the target was at third degree and all Affliction conditions have been removed naturally  
   **THEN** the system enforces the *Third-Degree Recovery Rule*: full minute (or outside aid) required before the target is fully clear  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — third-degree recovery: full minute after effect ends

4. **WHEN** the *Affliction* effect itself ends (not maintained)  
   **THEN** conditions already applied remain until removed by recovery checks  
   **BUT** no new conditions are applied after the effect ends  
   **Evidence:** HeroesHandbook-rules__chunk_089.md — Instant duration means conditions persist after application

---

## Story: Resolve Damage Resistance Check and Apply Damage Condition

**Story type:** system

### Domain terms

- *Toughness Check* — resistance check against DC 15 + Damage rank
- *Damage Condition* — progressive harm state: bruised → dazed+penalized → staggered+penalized → incapacitated
- *Toughness Penalty* — cumulative –1 Toughness per prior non-lethal failure

### Acceptance criteria

1. **WHEN** a *Damage* attack hits  
   **THEN** the system resolves a *Toughness Check* for the target against DC 15 + *Damage* rank  
   **AND** applies *Damage Conditions* based on degree of failure  
   **Evidence:** HeroesHandbook-rules__chunk_097.md — Toughness DC = 15 + rank; degree-of-failure damage table

2. **WHEN** the target fails by one degree  
   **THEN** the system applies a –1 *Toughness Penalty* (bruised condition)  
   **Evidence:** HeroesHandbook-rules__chunk_097.md — first-degree failure: –1 Toughness penalty

3. **WHEN** the target fails by two degrees  
   **THEN** the system applies dazed and an additional –1 *Toughness Penalty*  
   **Evidence:** HeroesHandbook-rules__chunk_097.md — second-degree failure: dazed + penalized

4. **WHEN** the target fails by three or more degrees  
   **THEN** the system applies staggered and an additional –1 *Toughness Penalty*  
   **Evidence:** HeroesHandbook-rules__chunk_097.md — third-degree: staggered + penalized

5. **WHEN** the target is already staggered and fails again by three+ degrees  
   **THEN** the system applies incapacitated  
   **AND** the target begins dying if the condition is exceeded again  
   **Evidence:** HeroesHandbook-rules__chunk_097.md — fourth degree: incapacitated; further: dying/dead

---

## Story: Resolve Weaken Resistance Check and Reduce Target Trait

**Story type:** system

### Domain terms

- *Weaken Resistance Check* — Fortitude or Will check by target vs. Weaken rank + 10
- *Trait Reduction* — temporary decrease applied to the chosen trait
- *Cumulative Cap* — Weaken rank; total reduction cannot exceed this across stacked applications

### Acceptance criteria

1. **WHEN** a *Weaken* attack hits  
   **THEN** the system resolves the target's resistance check (Fort or Will vs. rank + 10)  
   **AND** reduces the target's chosen trait by degree of failure, up to the *Cumulative Cap*  
   **Evidence:** HeroesHandbook-rules__chunk_139.md — Weaken resistance check; reduction = degree of failure

2. **WHEN** a second *Weaken* application targets the same trait  
   **THEN** the system adds the new reduction to the existing reduction  
   **AND** caps the combined total at the *Weaken* rank  
   **BUT** does not reduce the trait below zero  
   **Evidence:** HeroesHandbook-rules__chunk_139.md — cumulative stacking to rank maximum

3. **WHEN** the target recovers at end of a round  
   **THEN** the system automatically restores 1 point of the reduced trait without requiring an action  
   **Evidence:** HeroesHandbook-rules__chunk_139.md — 1 point auto-recovery per round

---

## Story: Recover Weakened Trait at One Point per Round

**Story type:** system

### Domain terms

- *Auto-Recovery* — 1 point of reduced trait restored per round; requires no action from the target
- *Recovery Rate* — fixed at 1 per round regardless of Weaken rank

### Acceptance criteria

1. **WHEN** a target has a *Weakened* trait  
   **THEN** the system restores 1 point of that trait at the start (or end) of each of the target's turns  
   **AND** this recovery requires no action from the target  
   **Evidence:** HeroesHandbook-rules__chunk_139.md — Weaken recovery: 1 point per round, automatic

2. **WHEN** the target's weakened trait has been partially recovered  
   **THEN** the remaining reduction continues to apply until fully recovered  
   **Evidence:** HeroesHandbook-rules__chunk_139.md — recovery is incremental, 1 per round

3. **WHEN** multiple *Weaken* effects on the same trait reduce it below zero after recovery  
   **THEN** the system applies only the net reduction (already capped by the cumulative rule)  
   **BUT** does not allow negative trait values  
   **Evidence:** HeroesHandbook-rules__chunk_139.md — cumulative cap prevents exceeding rank maximum

---

## Story: Resolve Nullify Opposed Check Against Target Effect Rank

**Story type:** system

### Domain terms

- *Nullify Opposed Check* — Nullify rank vs. target's effect rank (or Will, whichever is higher)
- *Counter State* — the targeted effect is suppressed; target can reactivate on next action
- *Reactivation* — target attempts to bring a countered effect back on their next action

### Acceptance criteria

1. **WHEN** a *Nullify* ranged attack hits  
   **THEN** the system resolves the *Nullify Opposed Check*: Nullify rank vs. the higher of target effect rank or target Will  
   **AND** success puts the targeted effect into *Counter State*  
   **Evidence:** HeroesHandbook-rules__chunk_125.md — Nullify: attack check hit triggers opposed check; higher of rank or Will

2. **WHEN** the *Nullify Opposed Check* succeeds  
   **THEN** the system marks the specific effect as countered (turned off)  
   **AND** the target may attempt *Reactivation* on their next action as a free action  
   **Evidence:** HeroesHandbook-rules__chunk_125.md — success: effect countered; reactivation on next action

3. **WHEN** the *Nullify Opposed Check* fails  
   **THEN** the targeted effect continues operating normally  
   **BUT** the *Nullify* use is expended for that action  
   **Evidence:** HeroesHandbook-rules__chunk_125.md — failed opposed check leaves effect active

4. **WHEN** the target is currently Nullified and attempts *Reactivation*  
   **THEN** the system re-resolves an opposed check (effect rank vs. original Nullify rank) on the target's action  
   **AND** success re-activates the effect  
   **Evidence:** HeroesHandbook-rules__chunk_125.md — reactivation opposed check on target's action

---

## Epic: Configure Defense Effect

---

## Story: Select Protection Effect for Toughness Bonus

**Story type:** user

### Domain terms

- *Protection* — Defense effect adding +1 Toughness per rank
- *Toughness* — resistance to damage; stacks with Stamina-derived base
- *Permanent Duration* — always on; cannot be deactivated or boosted by extra effort

### Acceptance criteria

1. **WHEN** the Player selects the *Protection* effect  
   **THEN** the system configures it as type Defense, action None, range Personal, duration Permanent, cost 1 pp/rank  
   **AND** shows the bonus as +1 *Toughness* per rank stacked with the character's Stamina-derived Toughness  
   **Evidence:** HeroesHandbook-rules__chunk_126.md — Protection: +1 Toughness/rank; permanent; stacks with Stamina

2. **WHEN** the Player reviews *Protection* during power construction  
   **THEN** the system notes it is always active and cannot be deactivated  
   **BUT** clarifies that *Protection* cannot be boosted by extra effort  
   **Evidence:** HeroesHandbook-rules__chunk_126.md — Protection permanent, cannot benefit from extra effort

3. **WHEN** the Player combines *Protection* with the Impervious extra  
   **THEN** the system allows the combination; *Protection* with Impervious resists attacks below a threshold rank  
   **Evidence:** HeroesHandbook-rules__chunk_126.md — can combine with Impervious extra

---

## Story: Select Immunity Effect and Define Covered Effect Set

**Story type:** user

### Domain terms

- *Immunity* — Defense effect granting automatic resistance success against a defined set
- *Covered Effect Set* — the specific descriptors or effect categories the Immunity protects against
- *Immunity Scope* — determines cost: narrow (1 rank) through all Toughness effects (80 ranks)

### Acceptance criteria

1. **WHEN** the Player selects the *Immunity* effect  
   **THEN** the system prompts for the *Covered Effect Set* (descriptor or effect category)  
   **AND** configures cost based on *Immunity Scope*: 1 rank for narrow, up to 80 ranks for all Toughness effects  
   **Evidence:** HeroesHandbook-rules__chunk_112.md — Immunity: scope-based cost; narrow=1 rank

2. **WHEN** the *Covered Effect Set* includes a common scope (e.g., Life Support = 10 ranks, all Fortitude = 30 ranks)  
   **THEN** the system applies the pre-defined rank cost from the immunity scope table  
   **Evidence:** HeroesHandbook-rules__chunk_112.md — predefined scopes: Life Support 10, all Fortitude 30

3. **WHEN** the Player activates a power with *Immunity*  
   **THEN** the system grants automatic success against any effect matching the *Covered Effect Set* with no roll required  
   **Evidence:** HeroesHandbook-rules__chunk_112.md — Immunity: automatic success, no check required

4. **WHEN** an effect outside the *Covered Effect Set* targets the character  
   **THEN** the *Immunity* provides no protection and normal resistance checks apply  
   **BUT** the *Immunity* is not consumed — it remains active for its defined scope  
   **Evidence:** HeroesHandbook-rules__chunk_112.md — Immunity works only against specified set

---

## Story: Configure Partial Immunity for Half-Effect Protection

**Story type:** user

### Domain terms

- *Partial Immunity* — reduced version granting half-effect protection against the covered set
- *Half-Effect* — effect rank is halved (round down) against the target; not a resistance bonus
- *Partial Cost* — half the full rank cost of the same Immunity scope

### Acceptance criteria

1. **WHEN** the Player selects Partial *Immunity*  
   **THEN** the system prices it at half the full rank cost for the same *Covered Effect Set*  
   **AND** notes that protection means the attacking effect is treated as half rank, not that the character gets a resistance bonus  
   **Evidence:** HeroesHandbook-rules__chunk_113.md — partial immunity costs half; effect is halved, not bonus granted

2. **WHEN** a covered effect targets a character with *Partial Immunity*  
   **THEN** the system halves the incoming effect rank (round down, minimum 1)  
   **AND** applies the resulting lower-rank effect normally  
   **Evidence:** HeroesHandbook-rules__chunk_113.md — partial immunity: effect reduced to half rank

3. **WHEN** the Player compares full vs. *Partial Immunity* costs  
   **THEN** the system shows full immunity at the scope rank cost and partial at half that cost  
   **Evidence:** HeroesHandbook-rules__chunk_113.md — partial = half cost of full

---

## Story: Select Regeneration Effect for Progressive Damage Recovery

**Story type:** user

### Domain terms

- *Regeneration* — Defense effect removing damage conditions progressively over time
- *Toughness Penalty Recovery* — first recovery phase; removes –Toughness modifiers
- *Condition Recovery* — second recovery phase; removes damage conditions from most severe

### Acceptance criteria

1. **WHEN** the Player selects the *Regeneration* effect  
   **THEN** the system configures it as type Defense, action None, range Personal, duration Permanent, cost 1 pp/rank  
   **AND** explains the two-phase recovery: phase 1 removes *Toughness Penalties*, phase 2 removes *Damage Conditions*  
   **Evidence:** HeroesHandbook-rules__chunk_127.md — Regeneration: two-phase recovery; permanent

2. **WHEN** the Player reviews *Regeneration* recovery speed  
   **THEN** the system shows Toughness penalties are removed at rank per minute and conditions at rank per minute from most severe  
   **Evidence:** HeroesHandbook-rules__chunk_127.md — recovery rate: rank × minutes for each phase

3. **WHEN** the Player's character is undamaged  
   **THEN** *Regeneration* has no effect — it only repairs existing damage  
   **Evidence:** HeroesHandbook-rules__chunk_127.md — Regeneration cannot affect conditions not yet incurred

---

## Story: Select Immortality Effect for Death Recovery

**Story type:** user

### Domain terms

- *Immortality* — Defense effect enabling return from death after a time period
- *Recovery Time* — time rank 19 − Immortality rank; at rank 20, one action round
- *Death Trigger* — Immortality activates only after death occurs, not before

### Acceptance criteria

1. **WHEN** the Player selects the *Immortality* effect  
   **THEN** the system configures it as type Defense, action None, range Personal, duration Permanent, cost 2 pp/rank  
   **AND** displays the *Recovery Time* formula: time rank = 19 − *Immortality* rank  
   **Evidence:** HeroesHandbook-rules__chunk_111.md — Immortality: 2 pp/rank; recovery time = 19 – rank

2. **WHEN** the Player asks what happens at rank 20  
   **THEN** the system indicates recovery occurs each action round (immediate return after one round of death)  
   **Evidence:** HeroesHandbook-rules__chunk_111.md — rank 20: recovers each action round

3. **WHEN** the Player reviews *Immortality*  
   **THEN** the system notes it does not prevent death — it only enables return afterward  
   **BUT** a character with *Immortality* still dies normally and follows the death trigger before recovery begins  
   **Evidence:** HeroesHandbook-rules__chunk_111.md — Immortality does not prevent death; only post-death return

4. **WHEN** a character with *Immortality* is killed  
   **THEN** the system begins the *Recovery Time* countdown based on the configured rank  
   **AND** the character returns to life at the end of that period with damage conditions cleared  
   **Evidence:** HeroesHandbook-rules__chunk_111.md — Immortality: return after time rank elapses

---

## Story: Apply Immunity Check Against Matching Power Descriptor

**Story type:** system

### Domain terms

- *Descriptor Match* — whether the attacking power's descriptor falls within the Immunity's covered set
- *Automatic Success* — no resistance check rolled; immunity is absolute for matched descriptors

### Acceptance criteria

1. **WHEN** an effect with a matching *Descriptor* targets an immune character  
   **THEN** the system grants automatic resistance success without requiring a roll  
   **AND** no *Damage Condition* or other effect is applied  
   **Evidence:** HeroesHandbook-rules__chunk_112.md — Immunity: automatic success; no check for matched descriptors

2. **WHEN** the attacking effect's descriptor is adjacent but not matching  
   **THEN** the system does not grant immunity and normal resistance applies  
   **AND** notes that the GM is the final arbitrator of descriptor matching  
   **Evidence:** HeroesHandbook-rules__chunk_155.md — descriptor matching is GM-adjudicated for borderline cases

3. **WHEN** a *Partial Immunity* character is targeted by a matching effect  
   **THEN** the system halves the effect rank before applying normal resistance  
   **BUT** does not grant automatic success — the character still makes a resistance check  
   **Evidence:** HeroesHandbook-rules__chunk_113.md — partial immunity: half rank, not automatic success

---

## Story: Remove Toughness Penalty via Regeneration Recovery Phase

**Story type:** system

### Domain terms

- *Phase 1 Recovery* — Toughness penalty removal; proceeds first before condition removal
- *Recovery Rate* — rank per minute; number of penalty points healed per minute

### Acceptance criteria

1. **WHEN** a character with *Regeneration* has *Toughness Penalties* (bruised conditions)  
   **THEN** the system removes penalties at the rate of *Regeneration* rank per minute  
   **AND** phase 1 completes before phase 2 begins  
   **Evidence:** HeroesHandbook-rules__chunk_127.md — Regeneration phase 1: Toughness penalties removed first

2. **WHEN** all *Toughness Penalties* are removed  
   **THEN** the system begins phase 2: removing *Damage Conditions* from most severe first  
   **Evidence:** HeroesHandbook-rules__chunk_127.md — phase 2 begins after penalties cleared

---

## Story: Remove Damage Condition via Regeneration Condition Phase

**Story type:** system

### Domain terms

- *Phase 2 Recovery* — damage condition removal, starting from most severe
- *Condition Removal Order* — most severe condition removed first

### Acceptance criteria

1. **WHEN** phase 2 of *Regeneration* is active  
   **THEN** the system removes the most severe *Damage Condition* first at the rate of rank per minute  
   **AND** works down toward less severe conditions after each removal  
   **Evidence:** HeroesHandbook-rules__chunk_127.md — condition phase removes from most severe; rank per minute rate

2. **WHEN** all conditions are removed  
   **THEN** the character's condition track is clear; *Regeneration* continues monitoring passively  
   **Evidence:** HeroesHandbook-rules__chunk_127.md — Regeneration permanent; monitors continuously

---

## Story: Recover from Death via Immortality After Time Elapses

**Story type:** system

### Domain terms

- *Death Recovery* — character returns to life after recovery time elapses
- *Time Rank* — 19 − Immortality rank; maps to a time interval on the time rank table
- *Revival State* — state after recovery; damage conditions are cleared on return

### Acceptance criteria

1. **WHEN** a character with *Immortality* dies  
   **THEN** the system begins counting down the *Time Rank* (19 − *Immortality* rank)  
   **AND** the character returns to life when the countdown expires  
   **Evidence:** HeroesHandbook-rules__chunk_111.md — Immortality: death triggers countdown; return after time rank

2. **WHEN** the *Recovery Time* elapses  
   **THEN** the system restores the character to life with damage conditions cleared  
   **Evidence:** HeroesHandbook-rules__chunk_111.md — return to life; conditions reset on revival

3. **WHEN** Immortality rank is 20  
   **THEN** the system applies a 1-action-round recovery time (effectively immediate)  
   **Evidence:** HeroesHandbook-rules__chunk_111.md — rank 20: recovers each action round

4. **WHEN** a character with *Immortality* is prevented from returning (e.g., held in stasis)  
   **THEN** the system notes the countdown restarts each time the trigger conditions are met  
   **BUT** environmental constraints on return are a GM narrative call, not a mechanical override  
   **Evidence:** HeroesHandbook-rules__chunk_111.md — Immortality mechanics; edge cases are GM-adjudicated

---

## Epic: Configure Mobility Effect

---

## Story: Select Flight Effect for Aerial Movement

**Story type:** user

### Domain terms

- *Flight* — Movement effect granting aerial locomotion at speed rank = effect rank
- *Hover* — default capability; the character can remain stationary in midair
- *Sustained Duration* — character falls if effect is not maintained

### Acceptance criteria

1. **WHEN** the Player selects the *Flight* effect  
   **THEN** the system configures it as type Movement, action Free, range Personal, duration Sustained, cost 2 pp/rank  
   **AND** displays speed rank equal to *Flight* rank  
   **Evidence:** HeroesHandbook-rules__chunk_107.md — Flight: 2 pp/rank; speed rank = effect rank; sustained

2. **WHEN** the Player reviews *Flight* capabilities  
   **THEN** the system notes hovering is included by default — no additional purchase required  
   **Evidence:** HeroesHandbook-rules__chunk_107.md — Flight includes hovering by default

3. **WHEN** the character's *Flight* effect is disrupted (Nullified or fails concentration)  
   **THEN** the system applies normal falling rules from the character's current altitude  
   **BUT** the character does not retain any aerial position when the effect ends  
   **Evidence:** HeroesHandbook-rules__chunk_107.md — sustained; character falls if effect ends mid-air

4. **WHEN** the character moves while airborne  
   **THEN** the character must spend a move action for actual movement (as with all movement effects)  
   **Evidence:** HeroesHandbook-rules__chunk_107.md — move action required for movement while airborne

---

## Story: Select Speed Effect for Ground Velocity Enhancement

**Story type:** user

### Domain terms

- *Speed* — Movement effect that increases ground movement speed rank
- *Ground Speed Rank* — speed rank = *Speed* effect rank; replaces normal ground speed if higher

### Acceptance criteria

1. **WHEN** the Player selects the *Speed* effect  
   **THEN** the system configures it as type Movement, action Free, range Personal, duration Sustained, cost 1 pp/rank  
   **AND** sets ground speed rank equal to *Speed* rank  
   **Evidence:** HeroesHandbook-rules__chunk_128.md — Speed: 1 pp/rank; speed rank = effect rank

2. **WHEN** the Player asks about other movement modes  
   **THEN** the system notes *Speed* only enhances ground movement; Flight, Swimming, and other modes require separate purchases  
   **Evidence:** HeroesHandbook-rules__chunk_128.md — Speed is ground-only; each mode is separate

3. **WHEN** the character uses *Speed* for travel  
   **THEN** the system applies the speed rank to all ground movement actions and overland travel calculations  
   **Evidence:** HeroesHandbook-rules__chunk_128.md — Speed enhances all ground movement actions

---

## Story: Select Burrowing Effect for Underground Movement

**Story type:** user

### Domain terms

- *Burrowing* — Movement effect for underground locomotion
- *Burrowing Speed Rank* — Burrowing rank − 5; further penalized by terrain type
- *Tunnel Permanence* — character chooses on each use whether the tunnel remains or collapses

### Acceptance criteria

1. **WHEN** the Player selects the *Burrowing* effect  
   **THEN** the system configures it as type Movement, action Free, range Personal, duration Sustained, cost 1 pp/rank  
   **AND** displays *Burrowing Speed Rank* as Burrowing rank − 5  
   **Evidence:** HeroesHandbook-rules__chunk_092.md — Burrowing: speed rank = effect rank – 5; sustained

2. **WHEN** the character burrows through clay or solid rock  
   **THEN** the system applies terrain penalties: clay −1, solid rock −2 to the speed rank  
   **Evidence:** HeroesHandbook-rules__chunk_092.md — terrain penalties for clay and solid rock

3. **WHEN** the character burrows  
   **THEN** the Player (or character) may choose whether the tunnel is permanent or collapses behind them  
   **Evidence:** HeroesHandbook-rules__chunk_092.md — tunnel permanence is a per-use choice

4. **WHEN** the Player reviews *Burrowing*  
   **THEN** the system notes it does not grant underwater breathing or other survival enhancements  
   **BUT** the character can still die from suffocation in an airtight tunnel unless they have appropriate Immunity  
   **Evidence:** HeroesHandbook-rules__chunk_092.md — Burrowing provides no survival capability

---

## Story: Select Swimming Effect for Aquatic Movement

**Story type:** user

### Domain terms

- *Swimming* — Movement effect for aquatic locomotion
- *Water Speed Rank* — Swimming rank − 2 on the speed table
- *Routine Athletics Check* — routine swimming checks become automatic with this effect

### Acceptance criteria

1. **WHEN** the Player selects the *Swimming* effect  
   **THEN** the system configures it as type Movement, action Free, range Personal, duration Sustained, cost 1 pp/rank  
   **AND** displays *Water Speed Rank* as Swimming rank − 2  
   **Evidence:** HeroesHandbook-rules__chunk_131.md — Swimming: water speed rank = effect rank – 2

2. **WHEN** the character swims  
   **THEN** the system makes routine Athletics (Swimming) checks automatic — no roll required  
   **Evidence:** HeroesHandbook-rules__chunk_131.md — Swimming makes Athletics (Swimming) automatic

3. **WHEN** the Player asks about underwater breathing  
   **THEN** the system notes *Swimming* does not grant it; *Immunity* (Suffocation) must be purchased separately  
   **Evidence:** HeroesHandbook-rules__chunk_131.md — Swimming: no underwater breathing; Immunity required

---

## Story: Select Leaping Effect for Extended Jumping

**Story type:** user

### Domain terms

- *Leaping* — Movement effect extending jump distance to superhuman scale
- *Jump Distance Rank* — Leaping rank − 2 on the distance table
- *Ballistic Arc* — no mid-air direction change; jump is one committed trajectory

### Acceptance criteria

1. **WHEN** the Player selects the *Leaping* effect  
   **THEN** the system configures it as type Movement, action Free, range Personal, duration Instant, cost 1 pp/rank  
   **AND** displays *Jump Distance Rank* as Leaping rank − 2  
   **Evidence:** HeroesHandbook-rules__chunk_116.md — Leaping: Instant duration; jump distance = rank – 2

2. **WHEN** the character lands within maximum jump distance  
   **THEN** the system negates fall damage  
   **Evidence:** HeroesHandbook-rules__chunk_116.md — Leaping: fall damage prevented within jump range

3. **WHEN** the character is airborne from a *Leaping* jump  
   **THEN** the system enforces the *Ballistic Arc* rule — the character cannot change direction mid-jump  
   **BUT** this is distinct from *Flight* which allows hovering and direction changes  
   **Evidence:** HeroesHandbook-rules__chunk_116.md — Leaping: ballistic arc; no direction change mid-air

---

## Story: Select Teleport Effect for Instantaneous Relocation

**Story type:** user

### Domain terms

- *Teleport* — Movement effect providing instantaneous point-to-point relocation
- *Destination Knowledge* — must be well-known or accurately sensed; unperceived destinations risk error
- *Momentum Conservation* — character retains velocity from before the teleport

### Acceptance criteria

1. **WHEN** the Player selects the *Teleport* effect  
   **THEN** the system configures it as type Movement, action Move, range Personal, duration Instant, cost 2 pp/rank  
   **AND** notes that range (maximum teleport distance) is determined by effect rank on the distance table  
   **Evidence:** HeroesHandbook-rules__chunk_134.md — Teleport: Instant duration; range from rank

2. **WHEN** the Player reviews teleport destination rules  
   **THEN** the system explains that destinations must be well-known or accurately sensed; otherwise teleport error risk applies  
   **Evidence:** HeroesHandbook-rules__chunk_134.md — Teleport destination: well-known or accurately sensed

3. **WHEN** the character teleports  
   **THEN** the system preserves *Momentum Conservation* — velocity from before the teleport is retained  
   **Evidence:** HeroesHandbook-rules__chunk_134.md — Teleport: momentum conserved

4. **WHEN** the Player asks about carrying others  
   **THEN** the system notes default carries mass rank 0; Mass extra extends carrying capacity  
   **Evidence:** HeroesHandbook-rules__chunk_134.md — Teleport: carries mass rank 0; Mass extra for more

---

## Story: Select Movement Effect and Choose Special Movement Mode

**Story type:** user

### Domain terms

- *Movement* — Movement effect granting one special movement mode per rank
- *Movement Mode* — specific capability from the defined list (Dimension Travel, Wall-Crawling, etc.)
- *Mode Independence* — each rank grants exactly one independent mode

### Acceptance criteria

1. **WHEN** the Player selects the *Movement* effect  
   **THEN** the system presents the mode list: Dimension Travel, Environmental Adaptation, Permeate, Safe Fall, Slithering, Space Travel, Sure-Footed, Swinging, Time Travel, Trackless, Wall-Crawling, Water-Walking  
   **AND** requires selection of one mode per rank purchased  
   **Evidence:** HeroesHandbook-rules__chunk_122.md — Movement: modes list; one mode per rank

2. **WHEN** the Player selects Wall-Crawling  
   **THEN** the system grants the ability to move at half speed along vertical and overhead surfaces  
   **Evidence:** HeroesHandbook-rules__chunk_122.md — Wall-Crawling: vertical/overhead at half speed

3. **WHEN** the Player selects Dimension Travel or Time Travel  
   **THEN** the system notes these modes interact with GM setting conventions and may require additional adjudication  
   **Evidence:** HeroesHandbook-rules__chunk_122.md — Dimension/Time Travel: GM interaction required

4. **WHEN** the Player purchases multiple *Movement* ranks  
   **THEN** the system allows a different mode for each rank; modes are independent  
   **BUT** the same mode cannot be selected twice (each rank must cover a distinct mode)  
   **Evidence:** HeroesHandbook-rules__chunk_122.md — each rank = one mode; modes are independent

---

## Story: Calculate Flight Speed Rank from Effect Rank

**Story type:** system

### Domain terms

- *Speed Rank* — derived value; equals Flight rank
- *Distance Per Move Action* — determined from the speed rank on the distance table

### Acceptance criteria

1. **WHEN** a character with *Flight* takes a move action to fly  
   **THEN** the system sets speed rank = *Flight* rank  
   **AND** calculates distance covered from the speed rank table  
   **Evidence:** HeroesHandbook-rules__chunk_107.md — Flight speed rank = effect rank; move action covers distance per rank

2. **WHEN** *Flight* rank changes (e.g., after Enhanced Trait application)  
   **THEN** the system immediately recalculates *Speed Rank* and maximum movement distance  
   **Evidence:** HeroesHandbook-rules__chunk_107.md — Flight speed scales directly with rank

---

## Story: Calculate Burrowing Speed Rank with Terrain Penalty

**Story type:** system

### Domain terms

- *Base Burrowing Speed* — rank − 5
- *Terrain Penalty* — clay: −1, solid rock: −2 applied to base speed

### Acceptance criteria

1. **WHEN** the character activates *Burrowing* in standard earth/soil  
   **THEN** the system sets speed rank = *Burrowing* rank − 5  
   **Evidence:** HeroesHandbook-rules__chunk_092.md — Burrowing speed = rank – 5

2. **WHEN** the terrain is clay  
   **THEN** the system subtracts an additional 1 from speed rank (total = rank − 6)  
   **Evidence:** HeroesHandbook-rules__chunk_092.md — clay penalty: −1 to speed rank

3. **WHEN** the terrain is solid rock  
   **THEN** the system subtracts an additional 2 from speed rank (total = rank − 7)  
   **Evidence:** HeroesHandbook-rules__chunk_092.md — solid rock penalty: −2 to speed rank

4. **WHEN** the calculated speed rank is 0 or below  
   **THEN** the system marks the character as unable to burrow through that terrain at current rank  
   **Evidence:** HeroesHandbook-rules__chunk_092.md — speed rank below 1 means terrain is impassable

---

## Story: Calculate Jump Distance Rank from Leaping Rank

**Story type:** system

### Domain terms

- *Jump Distance Rank* — Leaping rank − 2; used on distance table for actual distance
- *Fall Damage Suppression* — no fall damage when landing within maximum jump distance

### Acceptance criteria

1. **WHEN** the character uses *Leaping*  
   **THEN** the system calculates *Jump Distance Rank* = Leaping rank − 2  
   **AND** applies the distance table to convert jump rank to feet/meters  
   **Evidence:** HeroesHandbook-rules__chunk_116.md — jump distance = Leaping rank – 2 on distance table

2. **WHEN** the character lands within the maximum *Jump Distance Rank* range  
   **THEN** the system suppresses fall damage  
   **BUT** landing outside that range triggers normal fall damage calculation  
   **Evidence:** HeroesHandbook-rules__chunk_116.md — fall damage prevented within jump range

---

## Story: Validate Teleport Destination as Known or Accurately Sensed

**Story type:** system

### Domain terms

- *Destination Validation* — check whether the destination is known or accurately perceived
- *Teleport Error* — consequence of teleporting to an unvalidated destination
- *Sense Accuracy* — the sensing must be accurate; vague or imprecise sensing is insufficient

### Acceptance criteria

1. **WHEN** a character attempts to *Teleport* to a destination  
   **THEN** the system checks whether the destination is well-known or currently and accurately sensed  
   **AND** proceeds normally if validated  
   **Evidence:** HeroesHandbook-rules__chunk_134.md — Teleport: destination must be known or accurately sensed

2. **WHEN** the destination is not well-known and not currently sensed  
   **THEN** the system triggers *Teleport Error* rules (random arrival point, or GM adjudication)  
   **Evidence:** HeroesHandbook-rules__chunk_134.md — unperceived destinations risk teleport error

3. **WHEN** the destination is obscured or blocked (inside a solid object)  
   **THEN** the system applies error rules; the character cannot safely materialize in solid matter  
   **Evidence:** HeroesHandbook-rules__chunk_134.md — Teleport: destination accuracy required to avoid solid matter

---

## Epic: Configure Sensory Effect

---

## Story: Select Senses Effect and Allocate Sense Enhancements

**Story type:** user

### Domain terms

- *Senses* — Sensory effect; each rank purchases one enhancement from the defined menu
- *Sense Enhancement* — specific capability from the list (Darkvision, Tracking, Counters Illusion, etc.)
- *Permanent Activation* — all purchased enhancements are always active

### Acceptance criteria

1. **WHEN** the Player selects the *Senses* effect  
   **THEN** the system presents the full enhancement menu and requires selection of one enhancement per rank  
   **AND** configures cost at 1 pp/rank  
   **Evidence:** HeroesHandbook-rules__chunk_129.md — Senses: 1 pp/rank; one enhancement per rank

2. **WHEN** the Player allocates multiple ranks  
   **THEN** each rank adds one independent *Sense Enhancement* from the list  
   **AND** all purchased enhancements are active simultaneously without requiring activation  
   **Evidence:** HeroesHandbook-rules__chunk_129.md — Senses: permanent; all enhancements always on

3. **WHEN** the Player selects Counters Concealment or Counters Illusion  
   **THEN** the system notes these enhancements apply to the specific sense type for which they are purchased  
   **Evidence:** HeroesHandbook-rules__chunk_129.md — Counters Concealment/Illusion tied to specific sense type

4. **WHEN** the Player reviews the configured *Senses*  
   **THEN** all selected enhancements are listed and marked as always-active  
   **Evidence:** HeroesHandbook-rules__chunk_129.md — Senses: permanent duration; no activation required

---

## Story: Select Concealment Effect and Choose Hidden Sense Type

**Story type:** user

### Domain terms

- *Concealment* — Sensory effect granting total concealment from a chosen sense type
- *Hidden Sense Type* — the sense from which the character is concealed
- *Concealment Cost* — 2 ranks per visual sense; 1 rank for most other sense types

### Acceptance criteria

1. **WHEN** the Player selects the *Concealment* effect  
   **THEN** the system prompts for the *Hidden Sense Type* and calculates cost (2 ranks for visual, 1 rank for others)  
   **Evidence:** HeroesHandbook-rules__chunk_095.md — Concealment: visual = 2 ranks; other senses = 1 rank

2. **WHEN** the *Hidden Sense Type* is a visual sense  
   **THEN** the system charges 2 ranks for concealment from that visual sense  
   **AND** notes that attackers relying on that sense are effectively blinded  
   **Evidence:** HeroesHandbook-rules__chunk_095.md — visual concealment costs 2 ranks; blind attacker rule

3. **WHEN** the Player asks about concealment from touch (tactile sense)  
   **THEN** the system notes tactile concealment is not possible  
   **Evidence:** HeroesHandbook-rules__chunk_095.md — Concealment: tactile sense is excluded

4. **WHEN** *Concealment* is active  
   **THEN** the character has total concealment from the chosen sense — characters relying on it cannot perceive the character at all  
   **Evidence:** HeroesHandbook-rules__chunk_095.md — total concealment against chosen sense type

---

## Story: Select Remote Sensing Effect for Displaced Perception

**Story type:** user

### Domain terms

- *Remote Sensing* — Sensory effect displacing the character's perception to a remote location
- *Sense Suppression* — normal senses are suppressed while Remote Sensing is active
- *Vulnerable Condition* — character's active defenses are halved during Remote Sensing

### Acceptance criteria

1. **WHEN** the Player selects the *Remote Sensing* effect  
   **THEN** the system configures cost at 1–5 pp/rank based on sense type coverage  
   **AND** notes that sensing through a remote point suppresses normal senses  
   **Evidence:** HeroesHandbook-rules__chunk_128b.md — Remote Sensing: 1-5 pp/rank; suppresses normal senses

2. **WHEN** the Player reviews the *Vulnerable Condition* risk  
   **THEN** the system confirms active defenses (Dodge and Parry) are halved while *Remote Sensing* is active  
   **Evidence:** HeroesHandbook-rules__chunk_128b.md — Remote Sensing: character is vulnerable (halved active defenses)

3. **WHEN** the Player configures the sense types covered  
   **THEN** the system adds 1 pp/rank per additional sense type beyond the first  
   **Evidence:** HeroesHandbook-rules__chunk_128b.md — Remote Sensing: cost scales with sense types covered

---

## Story: Select Mind Reading Effect for Mental Contact

**Story type:** user

### Domain terms

- *Mind Reading* — Sensory effect accessing a target's thoughts via opposed check
- *Mental Contact* — sustained link established on successful opposed check
- *Depth of Access* — 4 degrees: surface thoughts, personal thoughts, memories, subconscious

### Acceptance criteria

1. **WHEN** the Player selects the *Mind Reading* effect  
   **THEN** the system configures it as type Sensory, range Perception, duration Sustained, cost 2 pp/rank  
   **AND** explains the opposed check: *Mind Reading* rank vs. target Will  
   **Evidence:** HeroesHandbook-rules__chunk_120.md — Mind Reading: 2 pp/rank; opposed check vs. Will

2. **WHEN** the Player reviews depth levels  
   **THEN** the system shows the four degrees: degree 1 = surface thoughts; degree 2 = personal thoughts; degree 3 = memories; degree 4 = subconscious  
   **Evidence:** HeroesHandbook-rules__chunk_120.md — Mind Reading: four depth levels from degrees of success

3. **WHEN** the Player reviews target recovery  
   **THEN** the system notes the target makes a Will check at end of each of their turns; success breaks *Mental Contact*  
   **Evidence:** HeroesHandbook-rules__chunk_120.md — target can break contact with Will check each turn

4. **WHEN** the Player asks about harm  
   **THEN** the system confirms *Mind Reading* cannot directly harm the target — information access only  
   **Evidence:** HeroesHandbook-rules__chunk_120.md — Mind Reading: no direct harm; information extraction only

---

## Story: Select Communication Effect and Choose Sense Type Medium

**Story type:** user

### Domain terms

- *Communication* — Sensory effect for long-distance information exchange
- *Sense Type Medium* — the channel (radio, mental, visual, etc.) chosen at acquisition
- *Language Dependency* — sender and receiver must share a language unless modified

### Acceptance criteria

1. **WHEN** the Player selects the *Communication* effect  
   **THEN** the system prompts for the *Sense Type Medium* to be locked at acquisition  
   **AND** configures range from effect rank on the distance table  
   **Evidence:** HeroesHandbook-rules__chunk_094.md — Communication: sense type at acquisition; range from rank

2. **WHEN** the Player reviews range  
   **THEN** the system displays the distance from the rank table and notes the medium is point-to-point by default  
   **Evidence:** HeroesHandbook-rules__chunk_094.md — Communication: point-to-point by default

3. **WHEN** sender and receiver do not share a language  
   **THEN** the system flags the *Language Dependency* — communication fails without a shared language unless modified  
   **Evidence:** HeroesHandbook-rules__chunk_094.md — Communication requires shared language

---

## Story: Select Comprehend Effect and Choose Communication Type

**Story type:** user

### Domain terms

- *Comprehend* — Sensory effect granting understanding of and communication with inaccessible beings
- *Communication Type* — one per rank: Animals, Languages, Machines, Objects, Plants, Spirits

### Acceptance criteria

1. **WHEN** the Player selects the *Comprehend* effect  
   **THEN** the system presents the communication type list and requires one type per rank purchased  
   **AND** configures it as permanent — always active  
   **Evidence:** HeroesHandbook-rules__chunk_096.md — Comprehend: one type per rank; permanent

2. **WHEN** the Player selects Languages  
   **THEN** the system grants understanding of and ability to speak any language  
   **Evidence:** HeroesHandbook-rules__chunk_096.md — Comprehend Languages: any language

3. **WHEN** multiple ranks are purchased  
   **THEN** each rank covers an independent *Communication Type*; one rank cannot cover two types  
   **Evidence:** HeroesHandbook-rules__chunk_096.md — each rank covers exactly one type; no stacking

---

## Story: Grant Total Concealment Against Chosen Sense Type

**Story type:** system

### Domain terms

- *Total Concealment* — characters relying on the concealed sense cannot perceive the character at all
- *Blind Attacker* — attackers using the concealed sense are effectively blind; attack penalties apply

### Acceptance criteria

1. **WHEN** a character's *Concealment* effect is active  
   **THEN** the system marks that character as totally concealed from the *Hidden Sense Type*  
   **AND** applies standard blind attacker penalties to any attack relying on that sense  
   **Evidence:** HeroesHandbook-rules__chunk_095.md — total concealment; blind attacker rules apply

2. **WHEN** an attacker has Counters Concealment for the affected sense  
   **THEN** the concealment does not apply to that attacker  
   **Evidence:** HeroesHandbook-rules__chunk_095.md — Counters Concealment negates concealment from that sense

---

## Story: Suppress Normal Senses During Remote Sensing

**Story type:** system

### Domain terms

- *Sense Suppression* — normal senses deactivated while Remote Sensing is active
- *Remote Perception Point* — the displaced location from which sensing occurs

### Acceptance criteria

1. **WHEN** *Remote Sensing* is activated  
   **THEN** the system suppresses the character's normal senses matching those used by the effect  
   **AND** the character perceives only through the *Remote Perception Point*  
   **Evidence:** HeroesHandbook-rules__chunk_128b.md — Remote Sensing: normal senses suppressed while active

2. **WHEN** *Remote Sensing* is deactivated  
   **THEN** normal senses are immediately restored  
   **Evidence:** HeroesHandbook-rules__chunk_128b.md — normal senses return when Remote Sensing ends

---

## Story: Mark Character as Vulnerable During Remote Sensing

**Story type:** system

### Domain terms

- *Vulnerable Status* — active defenses (Dodge and Parry) halved
- *Vulnerability Window* — the duration that *Remote Sensing* is active

### Acceptance criteria

1. **WHEN** a character activates *Remote Sensing*  
   **THEN** the system applies the *Vulnerable Status* condition — active defenses are halved for the duration  
   **AND** the character remains physically present and subject to attack  
   **Evidence:** HeroesHandbook-rules__chunk_128b.md — Remote Sensing: character is vulnerable

2. **WHEN** *Remote Sensing* ends  
   **THEN** the system removes the *Vulnerable Status* and restores full active defenses  
   **Evidence:** HeroesHandbook-rules__chunk_128b.md — vulnerable condition ends with the effect

---

## Story: Resolve Mind Reading Opposed Check Against Will Defense

**Story type:** system

### Domain terms

- *Mind Reading Opposed Check* — *Mind Reading* rank vs. target Will
- *Contact Success* — degree of success determines depth of access granted

### Acceptance criteria

1. **WHEN** *Mind Reading* targets a character in perception range  
   **THEN** the system resolves the opposed check: *Mind Reading* rank vs. target Will  
   **AND** maps degrees of success to depth: 1 degree = surface thoughts; 2 = personal; 3 = memories; 4 = subconscious  
   **Evidence:** HeroesHandbook-rules__chunk_120.md — Mind Reading: opposed check; depth from degree of success

2. **WHEN** the opposed check fails  
   **THEN** no *Mental Contact* is established and no thoughts are accessed  
   **Evidence:** HeroesHandbook-rules__chunk_120.md — failed check: no contact

3. **WHEN** contact is established  
   **THEN** the system marks the connection as *Sustained* and begins tracking the target's recovery attempts  
   **Evidence:** HeroesHandbook-rules__chunk_120.md — Mind Reading: sustained duration while contact holds

---

## Story: Break Mind Reading Contact on Target Will Check Success

**Story type:** system

### Domain terms

- *End-of-Turn Will Check* — target's attempt to break *Mental Contact* each turn
- *Contact Break* — contact ends; no more thoughts accessible without re-establishing

### Acceptance criteria

1. **WHEN** a target has active *Mental Contact* from *Mind Reading*  
   **THEN** the system triggers an *End-of-Turn Will Check* at the end of each of the target's turns  
   **AND** success breaks *Mental Contact* immediately  
   **Evidence:** HeroesHandbook-rules__chunk_120.md — target Will check at end of each turn; success breaks contact

2. **WHEN** *Mental Contact* is broken  
   **THEN** the *Mind Reading* user must establish a new opposed check to re-read the target  
   **AND** existing information gathered is retained  
   **Evidence:** HeroesHandbook-rules__chunk_120.md — break ends contact; re-establish requires new check

---

## Epic: Configure Control Effect

---

## Story: Select Create Effect and Set Volume Parameters

**Story type:** user

### Domain terms

- *Create* — Control effect forming solid objects with Toughness and volume from rank
- *Object Volume* — maximum volume from rank on the volume table
- *Object Toughness* — equals *Create* rank; determines how durable created objects are
- *Permanence Option* — spend PP equal to rank to make the object permanent

### Acceptance criteria

1. **WHEN** the Player selects the *Create* effect  
   **THEN** the system configures it as type Control, action Standard, range Close, duration Sustained, cost 2 pp/rank  
   **AND** sets *Object Toughness* = rank and displays maximum *Object Volume* from the volume table  
   **Evidence:** HeroesHandbook-rules__chunk_096b.md — Create: 2 pp/rank; Toughness = rank; volume from rank table

2. **WHEN** the Player reviews permanence  
   **THEN** the system notes the *Permanence Option*: spend power points equal to rank to make the object permanent  
   **Evidence:** HeroesHandbook-rules__chunk_096b.md — Create: permanence by spending PP = rank

3. **WHEN** the *Create* effect is not maintained  
   **THEN** the system dissolves the created object automatically  
   **AND** any characters or objects inside or restrained by it are released  
   **Evidence:** HeroesHandbook-rules__chunk_096b.md — Create: sustained; objects dissolve when not maintained

4. **WHEN** the Player uses *Create* to restrain a target  
   **THEN** the system uses effect rank as effective Strength for the restraint check  
   **Evidence:** HeroesHandbook-rules__chunk_096b.md — Create: rank = effective Strength for restraint

---

## Story: Select Move Object Effect for Telekinetic Manipulation

**Story type:** user

### Domain terms

- *Move Object* — Control effect providing telekinetic force at effective Strength = rank
- *Strength Check Resistance* — unwilling targets may resist with a Strength check vs. effect rank
- *Combat Applications* — disarm, grab, or trip only; cannot deal direct Damage

### Acceptance criteria

1. **WHEN** the Player selects the *Move Object* effect  
   **THEN** the system configures it as type Control, action Standard, range Ranged, duration Sustained, cost 2 pp/rank  
   **AND** sets effective Strength = *Move Object* rank for all lifting and moving purposes  
   **Evidence:** HeroesHandbook-rules__chunk_121.md — Move Object: 2 pp/rank; Str rank = effect rank

2. **WHEN** the Player reviews combat applications  
   **THEN** the system confirms only disarm, grab, and trip are available; direct Damage is not an option  
   **Evidence:** HeroesHandbook-rules__chunk_121.md — Move Object: disarm/grab/trip; no direct Damage

3. **WHEN** an unwilling target is grabbed or moved  
   **THEN** the system resolves the target's Strength check vs. *Move Object* rank to resist  
   **Evidence:** HeroesHandbook-rules__chunk_121.md — unwilling targets resist with Strength check

4. **WHEN** the *Move Object* effect is not maintained  
   **THEN** the held object or creature is released and falls to the ground  
   **Evidence:** HeroesHandbook-rules__chunk_121.md — sustained; held objects released when effect ends

---

## Story: Select Environment Effect and Choose Environmental Changes

**Story type:** user

### Domain terms

- *Environment* — Control effect altering conditions in an area
- *Environmental Change* — Cold, Heat, Light, Visibility impairment, or Movement impede
- *Effect Radius* — determined from rank on the area table

### Acceptance criteria

1. **WHEN** the Player selects the *Environment* effect  
   **THEN** the system presents the change options: Cold, Heat, Light, Visibility, Movement impede  
   **AND** calculates *Effect Radius* from rank on the area table  
   **Evidence:** HeroesHandbook-rules__chunk_103.md — Environment: change options; radius from rank; 1 pp/rank

2. **WHEN** the Player selects multiple *Environmental Changes*  
   **THEN** the system charges additional ranks for each additional change beyond the first  
   **Evidence:** HeroesHandbook-rules__chunk_103.md — additional changes cost additional ranks

3. **WHEN** the *Environment* effect is active  
   **THEN** the system applies the environmental conditions to all characters in the radius  
   **AND** notes *Environment* does not deal direct damage — it creates hazardous conditions  
   **Evidence:** HeroesHandbook-rules__chunk_103.md — Environment: conditions only; no direct damage

---

## Story: Select Illusion Effect and Choose Sense Type Coverage

**Story type:** user

### Domain terms

- *Illusion* — Control effect creating false sensory impressions for targets in perception range
- *Sense Type Coverage* — number of senses affected; cost increases with coverage
- *Insight Check* — DC 10 + rank; success reveals falsehood but doesn't remove it

### Acceptance criteria

1. **WHEN** the Player selects the *Illusion* effect  
   **THEN** the system prompts for *Sense Type Coverage* and prices at 1–5 pp/rank (1 base + 1 per additional sense)  
   **Evidence:** HeroesHandbook-rules__chunk_114.md — Illusion: 1-5 pp/rank depending on sense types

2. **WHEN** the Player reviews the *Insight Check* rule  
   **THEN** the system confirms the DC = 10 + *Illusion* rank; success reveals the illusion as false but does not dispel it  
   **Evidence:** HeroesHandbook-rules__chunk_114.md — Insight check: DC 10 + rank; success reveals but doesn't remove

3. **WHEN** the *Illusion* effect is maintained  
   **THEN** the character may alter the illusion as a free action each turn  
   **AND** the illusion has no physical substance — it cannot block movement, cause damage, or provide cover  
   **Evidence:** HeroesHandbook-rules__chunk_114.md — Illusion: free action alteration; no physical substance

4. **WHEN** the *Illusion* effect ends (not maintained)  
   **THEN** the false sensory impressions vanish immediately  
   **Evidence:** HeroesHandbook-rules__chunk_114.md — sustained duration; illusion ends when not maintained

---

## Story: Select Luck Control Effect and Define Hero Point Capability

**Story type:** user

### Domain terms

- *Luck Control* — Control effect manipulating the hero point economy at perception range
- *Hero Point Capability* — one capability per rank from the defined list
- *Reaction Trigger* — *Luck Control* is a Reaction; activates in response to hero point use

### Acceptance criteria

1. **WHEN** the Player selects the *Luck Control* effect  
   **THEN** the system presents the capability list per rank: spend hero point on behalf of another, transfer hero point, negate hero point use, or force re-roll  
   **AND** configures it as a Reaction effect at perception range  
   **Evidence:** HeroesHandbook-rules__chunk_116b.md — Luck Control: one capability per rank; Reaction

2. **WHEN** the Player purchases multiple ranks  
   **THEN** each rank selects one capability from the list  
   **AND** all selected capabilities are available as reactions  
   **Evidence:** HeroesHandbook-rules__chunk_116b.md — each rank grants one capability; multiple capabilities possible

3. **WHEN** another character uses a hero point within perception range  
   **THEN** the *Luck Control* user may activate their reaction  
   **AND** the chosen capability takes effect  
   **Evidence:** HeroesHandbook-rules__chunk_116b.md — Luck Control: reaction to hero point use

---

## Story: Select Summon Effect and Define Minion Parameters

**Story type:** user

### Domain terms

- *Summon* — Control effect calling an independently acting minion
- *Minion PP* — fixed at effect rank × 15 power points
- *Minion PL* — capped at *Summon* effect rank
- *Dazed Condition* — applied to the minion on arrival (standard action only on first turn)

### Acceptance criteria

1. **WHEN** the Player selects the *Summon* effect  
   **THEN** the system configures *Minion PP* = rank × 15 and *Minion PL* ≤ rank  
   **AND** notes the *Dazed Condition* on arrival rule  
   **Evidence:** HeroesHandbook-rules__chunk_130.md — Summon: PP = rank × 15; PL ≤ rank; dazed on arrival

2. **WHEN** the Player reviews directing the minion  
   **THEN** the system notes directing costs a move action each turn; the minion follows last instructions otherwise  
   **Evidence:** HeroesHandbook-rules__chunk_130.md — Summon: directing = move action; follows last orders without direction

3. **WHEN** the minion is incapacitated  
   **THEN** the system dismisses the minion; the character may re-summon later  
   **Evidence:** HeroesHandbook-rules__chunk_130.md — Summon: dismissed on incapacitation; re-summon available

4. **WHEN** the Player tries to build a minion with PL higher than the *Summon* rank  
   **THEN** the system rejects the configuration  
   **BUT** the Player may build a lower-PL minion within the allowed PP pool  
   **Evidence:** HeroesHandbook-rules__chunk_130.md — Minion PL cap = Summon rank; PP = rank × 15

---

## Story: Select Transform Effect and Set Transformation Scope

**Story type:** user

### Domain terms

- *Transform* — Control effect changing one type of object into another at close range
- *Transformation Scope* — narrow (one to one) through broad (anything to anything); determines cost per rank
- *Fortitude Resistance* — living targets resist with Fortitude; inanimate objects do not resist

### Acceptance criteria

1. **WHEN** the Player selects the *Transform* effect  
   **THEN** the system prompts for *Transformation Scope* and sets cost: 2 pp/rank (narrow) through 5 pp/rank (broad)  
   **AND** displays maximum transformable mass from rank on the mass table  
   **Evidence:** HeroesHandbook-rules__chunk_135.md — Transform: 2-5 pp/rank by scope; mass from rank

2. **WHEN** *Transform* targets a living creature  
   **THEN** the system prompts for *Fortitude Resistance* check; inanimate objects are transformed without a roll  
   **Evidence:** HeroesHandbook-rules__chunk_135.md — Transform: living targets make Fortitude check; inanimate no check

3. **WHEN** the *Transform* effect is sustained and then ends  
   **THEN** the transformation reverts unless the Continuous extra was applied  
   **Evidence:** HeroesHandbook-rules__chunk_135.md — Transform: sustained by default; reverts when effect ends

---

## Story: Enforce Created Object Volume and Toughness from Effect Rank

**Story type:** system

### Domain terms

- *Volume Enforcement* — system ensures created object does not exceed rank-based volume
- *Toughness Assignment* — object Toughness = Create rank; set at creation

### Acceptance criteria

1. **WHEN** a character uses *Create*  
   **THEN** the system enforces a volume ceiling from the rank-based volume table  
   **AND** sets *Object Toughness* = effect rank  
   **Evidence:** HeroesHandbook-rules__chunk_096b.md — Create enforces volume and Toughness from rank

2. **WHEN** the Player requests an object larger than the rank allows  
   **THEN** the system rejects the creation  
   **BUT** allows a smaller object within the volume limit  
   **Evidence:** HeroesHandbook-rules__chunk_096b.md — volume is rank-gated; excess volume not allowed

---

## Story: Dissolve Created Object When Effect is Not Maintained

**Story type:** system

### Domain terms

- *Dissolution Trigger* — effect not maintained (end of turn, concentration broken, Nullified)
- *Object Disappearance* — object vanishes at the dissolution trigger point

### Acceptance criteria

1. **WHEN** the *Create* effect is no longer maintained  
   **THEN** the system immediately dissolves the created object  
   **AND** releases any restrained targets  
   **Evidence:** HeroesHandbook-rules__chunk_096b.md — Create: dissolution on loss of maintenance

2. **WHEN** the *Create* effect has a permanent object (PP spent)  
   **THEN** the object persists after the effect ends  
   **BUT** it is no longer under the character's control once permanent  
   **Evidence:** HeroesHandbook-rules__chunk_096b.md — permanence via PP spending overrides dissolution

---

## Story: Resolve Move Object Strength Check for Resisting Targets

**Story type:** system

### Domain terms

- *Resistance Check* — target's Strength check vs. *Move Object* rank to resist movement
- *Object Resistance* — inanimate objects do not resist; living targets may

### Acceptance criteria

1. **WHEN** *Move Object* targets a living creature  
   **THEN** the system resolves the target's Strength check vs. *Move Object* rank  
   **AND** on failure, the creature is moved or manipulated as intended  
   **Evidence:** HeroesHandbook-rules__chunk_121.md — Move Object: Strength check for living targets

2. **WHEN** *Move Object* targets an inanimate object  
   **THEN** the system moves the object without a resistance check  
   **Evidence:** HeroesHandbook-rules__chunk_121.md — inanimate objects: no resistance check

3. **WHEN** the target's Strength check succeeds  
   **THEN** the target resists the telekinetic force and is not moved  
   **Evidence:** HeroesHandbook-rules__chunk_121.md — successful Strength check blocks movement

---

## Story: Resolve Insight Check to Detect Illusion

**Story type:** system

### Domain terms

- *Insight Check* — DC 10 + *Illusion* rank; made to detect the illusion
- *Detection* — reveals illusion as false but does not remove it

### Acceptance criteria

1. **WHEN** a character is in the presence of an active *Illusion*  
   **THEN** the system allows an *Insight Check* against DC 10 + *Illusion* rank  
   **AND** on success, the character recognizes the illusion as false  
   **BUT** the illusion remains visible — detection does not dispel it  
   **Evidence:** HeroesHandbook-rules__chunk_114.md — Insight check: reveals falsehood; does not remove illusion

2. **WHEN** the *Insight Check* fails  
   **THEN** the character cannot distinguish the illusion from reality  
   **Evidence:** HeroesHandbook-rules__chunk_114.md — failed Insight: character treats illusion as real

---

## Story: Apply Summon Dazed Condition on Minion Arrival

**Story type:** system

### Domain terms

- *Arrival Daze* — minion gains dazed condition on the turn it appears; can take only a standard action

### Acceptance criteria

1. **WHEN** a minion is summoned  
   **THEN** the system applies the *Arrival Daze* condition — the minion is dazed on its first turn  
   **AND** the dazed condition limits the minion to one standard action on that first turn  
   **Evidence:** HeroesHandbook-rules__chunk_130.md — Summon: dazed on arrival; standard action only first turn

2. **WHEN** the minion's first turn ends  
   **THEN** the system removes the *Arrival Daze* and the minion acts normally thereafter  
   **Evidence:** HeroesHandbook-rules__chunk_130.md — daze is one-turn only on arrival

---

## Story: Dismiss Summon When Minion is Incapacitated

**Story type:** system

### Domain terms

- *Incapacitation Trigger* — the minion reaches the incapacitated damage condition
- *Automatic Dismissal* — minion disappears when incapacitated

### Acceptance criteria

1. **WHEN** a summoned minion reaches *Incapacitated* condition  
   **THEN** the system automatically dismisses it (removes from play)  
   **AND** the summoner may attempt to re-summon later  
   **Evidence:** HeroesHandbook-rules__chunk_130.md — Summon: dismissed on incapacitation; re-summon allowed

2. **WHEN** the summoner voluntarily dismisses the minion  
   **THEN** the system removes the minion from play as a free action  
   **Evidence:** HeroesHandbook-rules__chunk_130.md — summoner may dismiss minion voluntarily

---

## Story: Resolve Transform Fortitude Resistance for Living Targets

**Story type:** system

### Domain terms

- *Transform Resistance Check* — Fortitude check by living target vs. *Transform* rank + 10
- *Transform Success* — target is transformed to the defined target type

### Acceptance criteria

1. **WHEN** *Transform* targets a living creature  
   **THEN** the system resolves a Fortitude check by the target vs. DC 10 + *Transform* rank  
   **AND** on failure, the target is transformed into the specified result type  
   **Evidence:** HeroesHandbook-rules__chunk_135.md — Transform: Fortitude check DC = 10 + rank for living targets

2. **WHEN** the Fortitude check succeeds  
   **THEN** the transformation does not occur  
   **Evidence:** HeroesHandbook-rules__chunk_135.md — successful Fortitude check prevents transformation

3. **WHEN** an inanimate object is targeted  
   **THEN** no resistance check is made — transformation succeeds automatically  
   **Evidence:** HeroesHandbook-rules__chunk_135.md — inanimate objects: no Fortitude check

---

## Story: Revert Transformation When Sustained Effect Ends

**Story type:** system

### Domain terms

- *Reversion Trigger* — *Transform* effect not maintained
- *Reversion* — transformed object/creature returns to original form

### Acceptance criteria

1. **WHEN** the *Transform* effect ends (not maintained)  
   **THEN** the system reverts the transformed target to its original form  
   **Evidence:** HeroesHandbook-rules__chunk_135.md — Transform: sustained; reverts when effect ends

2. **WHEN** the Continuous extra has been applied to *Transform*  
   **THEN** the transformation persists even after the effect ends — no reversion  
   **Evidence:** HeroesHandbook-rules__chunk_135.md — Continuous extra: makes transformation permanent

---

## Epic: Configure General Effect

---

## Story: Select Variable Effect and Define Effect Type Pool

**Story type:** user

### Domain terms

- *Variable* — General effect providing a power point pool allocatable to effects of a defined type
- *Pool Size* — rank × 5 power points
- *Reallocation Action* — standard action to redistribute the pool
- *PL Limits* — apply to all effects built from the *Variable* pool

### Acceptance criteria

1. **WHEN** the Player selects the *Variable* effect  
   **THEN** the system sets *Pool Size* = rank × 5 power points  
   **AND** prompts for the defined effect type or descriptor scope  
   **Evidence:** HeroesHandbook-rules__chunk_136.md — Variable: pool = rank × 5; type/descriptor defined at acquisition

2. **WHEN** the Player reviews reallocation rules  
   **THEN** the system confirms reallocation costs a standard action  
   **AND** all effects built from the pool must comply with PL limits  
   **Evidence:** HeroesHandbook-rules__chunk_136.md — Variable: standard action to reallocate; PL limits apply

3. **WHEN** the *Variable* effect is not maintained  
   **THEN** all active allocated effects end and the pool resets  
   **Evidence:** HeroesHandbook-rules__chunk_136.md — Variable: pool resets when effect not maintained

4. **WHEN** the Player attempts to build an effect from the pool that exceeds PL limits  
   **THEN** the system blocks the configuration and indicates the PL violation  
   **Evidence:** HeroesHandbook-rules__chunk_136.md — Variable-built effects subject to PL limits

---

## Story: Select Growth Effect for Physical Size Increase

**Story type:** user

### Domain terms

- *Growth* — General effect increasing size rank with stat bonuses and penalties
- *Growth Bonuses* — +1 Strength, +1 Stamina, +1 mass rank, −1 Stealth per rank
- *Growth Penalties* — −1 Dodge and −1 Parry per 2 ranks; −1 Intimidation per 2 ranks (reversed)

### Acceptance criteria

1. **WHEN** the Player selects the *Growth* effect  
   **THEN** the system configures it as type General, duration Sustained, cost 1 pp/rank  
   **AND** displays per-rank bonuses: +1 Strength, +1 Stamina, +1 mass rank, −1 Stealth  
   **AND** per-2-rank changes: −1 Dodge, −1 Parry, +1 Intimidation  
   **Evidence:** HeroesHandbook-rules__chunk_109.md — Growth: bonuses/penalties per rank schedule

2. **WHEN** the *Growth* effect is disrupted  
   **THEN** the system immediately reverts the character to normal size  
   **Evidence:** HeroesHandbook-rules__chunk_109.md — Growth: sustained; disruption causes immediate reversion

3. **WHEN** the Player reviews size rank 8+  
   **THEN** the system notes an additional +1 Speed rank bonus per 8 ranks  
   **Evidence:** HeroesHandbook-rules__chunk_109.md — Growth: +1 Speed per 8 ranks

---

## Story: Select Shrinking Effect for Physical Size Reduction

**Story type:** user

### Domain terms

- *Shrinking* — General effect decreasing size rank improving defenses and stealth
- *Shrinking Bonuses* — +1 Stealth per rank; +1 Dodge, +1 Parry per 2 ranks
- *Shrinking Penalties* — −1 Speed per 2 ranks; −1 Intimidation per 2 ranks; reduced Strength for size

### Acceptance criteria

1. **WHEN** the Player selects the *Shrinking* effect  
   **THEN** the system configures it as type General, duration Sustained, cost 1 pp/rank  
   **AND** displays per-rank bonus (+1 Stealth) and per-2-rank changes (+1 Dodge, +1 Parry, −1 Speed, −1 Intimidation)  
   **Evidence:** HeroesHandbook-rules__chunk_129b.md — Shrinking: bonuses/penalties per rank schedule

2. **WHEN** the Player reviews reach implications  
   **THEN** the system notes Shrinking reduces effective Strength for size-based purposes  
   **Evidence:** HeroesHandbook-rules__chunk_129b.md — Shrinking reduces size-based Strength

3. **WHEN** the *Shrinking* effect is disrupted  
   **THEN** the system reverts the character to normal size as a free action (or immediately if disrupted)  
   **Evidence:** HeroesHandbook-rules__chunk_129b.md — Shrinking: sustained; returning to normal is free action

---

## Story: Select Insubstantial Effect and Choose Physical Form

**Story type:** user

### Domain terms

- *Insubstantial* — General effect with 4 progressive forms of decreasing physicality
- *Form Rank* — 1 (Fluid), 2 (Gaseous), 3 (Energy), 4 (Incorporeal); each costs 5 pp/rank
- *Form Switching* — free action; can switch among purchased forms

### Acceptance criteria

1. **WHEN** the Player selects the *Insubstantial* effect  
   **THEN** the system presents the 4 forms and prices each at 5 pp/rank  
   **AND** notes higher forms include all lower-form capabilities (must purchase in order)  
   **Evidence:** HeroesHandbook-rules__chunk_115.md — Insubstantial: 5 pp/rank; 4 forms; progressive capability

2. **WHEN** the Player selects form 4 (Incorporeal)  
   **THEN** the system notes the character can pass through solid matter and ignore most physical effects  
   **AND** the Affects Insubstantial extra is required for others to affect an Incorporeal character  
   **Evidence:** HeroesHandbook-rules__chunk_115.md — Incorporeal: pass through matter; Affects Insubstantial extra required

3. **WHEN** the *Insubstantial* effect is disrupted  
   **THEN** the character reverts to their normal physical form  
   **Evidence:** HeroesHandbook-rules__chunk_115.md — Insubstantial: sustained; reverts when not maintained

---

## Story: Select Enhanced Trait Effect and Choose Target Trait

**Story type:** user

### Domain terms

- *Enhanced Trait* — General effect temporarily raising an existing trait above its base
- *Target Trait* — the trait to be enhanced; must already exist on the character sheet
- *PL Limits* — apply to the combined total (base + Enhanced Trait)

### Acceptance criteria

1. **WHEN** the Player selects the *Enhanced Trait* effect  
   **THEN** the system prompts for the *Target Trait* and prices it at the same cost per rank as that trait  
   **AND** notes the trait must already exist on the character sheet  
   **Evidence:** HeroesHandbook-rules__chunk_104.md — Enhanced Trait: cost = target trait's base cost; must already exist

2. **WHEN** the *Enhanced Trait* is applied  
   **THEN** the system adds the enhancement rank to the base trait for all calculations  
   **AND** enforces PL limits on the combined total  
   **Evidence:** HeroesHandbook-rules__chunk_104.md — Enhanced Trait: adds to base; PL limits on total

3. **WHEN** the *Enhanced Trait* effect is not maintained  
   **THEN** the trait drops back to its base value  
   **Evidence:** HeroesHandbook-rules__chunk_104.md — Enhanced Trait: sustained; drops to base when effect ends

---

## Story: Select Healing Effect for Damage Condition Removal

**Story type:** user

### Domain terms

- *Healing* — General effect removing damage conditions from a willing target
- *Healing Check* — roll vs. DC 10; each degree of success removes one condition from most severe
- *Scene Reuse Block* — cannot use *Healing* on the same target more than once per scene

### Acceptance criteria

1. **WHEN** the Player selects the *Healing* effect  
   **THEN** the system configures it as type General, action Standard, range Close, duration Instant, cost 2 pp/rank  
   **Evidence:** HeroesHandbook-rules__chunk_110.md — Healing: 2 pp/rank; standard action; close range

2. **WHEN** *Healing* is used on a target  
   **THEN** the system makes the *Healing Check* vs. DC 10  
   **AND** removes one *Damage Condition* per degree of success from most severe first  
   **Evidence:** HeroesHandbook-rules__chunk_110.md — Healing check vs. DC 10; degree of success = conditions removed

3. **WHEN** the Player attempts to use *Healing* on the same target a second time in the same scene  
   **THEN** the system blocks the second use  
   **BUT** the effect may be used on different targets in the same scene  
   **Evidence:** HeroesHandbook-rules__chunk_110.md — Healing: once per scene per target

4. **WHEN** *Healing* is used on a dying character  
   **THEN** the system stabilizes the character as part of the healing effect  
   **Evidence:** HeroesHandbook-rules__chunk_110.md — Healing: stabilizes dying characters

---

## Story: Select Elongation Effect for Extended Reach

**Story type:** user

### Domain terms

- *Elongation* — General effect extending limbs and reach to superhuman scale
- *Reach* — size rank + *Elongation* rank on the distance table
- *Grab Bonus* — +1 to grab checks per rank from improved leverage

### Acceptance criteria

1. **WHEN** the Player selects the *Elongation* effect  
   **THEN** the system configures it as type General, duration Sustained, cost 1 pp/rank  
   **AND** calculates *Reach* = size rank + *Elongation* rank on the distance table  
   **Evidence:** HeroesHandbook-rules__chunk_102.md — Elongation: reach = size rank + rank; sustained

2. **WHEN** the Player reviews combat benefits  
   **THEN** the system shows +1 to grab checks per rank  
   **AND** notes *Elongation* does not grant Strength, Toughness, or other physical enhancements  
   **Evidence:** HeroesHandbook-rules__chunk_102.md — Elongation: grab bonus +1/rank; no other stat enhancement

---

## Story: Select Quickness Effect for Task Time Reduction

**Story type:** user

### Domain terms

- *Quickness* — General effect reducing time required for routine tasks
- *Routine Task* — task that does not require a check; Quickness reduces its time rank by 1 per rank
- *Non-Routine Exclusion* — tasks requiring checks or movement are unaffected

### Acceptance criteria

1. **WHEN** the Player selects the *Quickness* effect  
   **THEN** the system configures it as type General, duration Sustained, cost 1 pp/rank  
   **AND** explains that *Routine Task* time rank is reduced by 1 per *Quickness* rank  
   **Evidence:** HeroesHandbook-rules__chunk_126b.md — Quickness: 1 pp/rank; reduces routine task time rank

2. **WHEN** the Player asks about non-routine tasks  
   **THEN** the system confirms *Quickness* has no effect on tasks requiring rolls or on movement  
   **Evidence:** HeroesHandbook-rules__chunk_126b.md — Quickness: no effect on check-required tasks or movement

---

## Story: Select Feature Effect and Define Minor Game Capability

**Story type:** user

### Domain terms

- *Feature* — General effect where each rank purchases one minor, always-active game capability
- *Minor Capability* — a concrete but limited game mechanical benefit; approved by GM
- *GM Approval* — required for each Feature definition

### Acceptance criteria

1. **WHEN** the Player selects the *Feature* effect  
   **THEN** the system prompts for the minor capability definition for each rank purchased  
   **AND** configures each rank at 1 pp/rank with permanent duration  
   **Evidence:** HeroesHandbook-rules__chunk_106.md — Feature: 1 pp/rank; one minor capability per rank; permanent

2. **WHEN** the Player defines a *Feature*  
   **THEN** the system flags it for *GM Approval* before the power is finalized  
   **Evidence:** HeroesHandbook-rules__chunk_106.md — Feature: each definition requires GM approval

3. **WHEN** the Player asks about descriptors vs. Features  
   **THEN** the system clarifies: descriptors are free flavor; *Features* cost PP and provide real mechanical benefits  
   **Evidence:** HeroesHandbook-rules__chunk_106.md — Feature vs. descriptor distinction

---

## Story: Apply Growth Ability and Size Bonuses and Penalties per Rank

**Story type:** system

### Domain terms

- *Size Rank Change* — change to the character's effective size category
- *Growth Stat Block* — per-rank bonuses/penalties applied to relevant traits

### Acceptance criteria

1. **WHEN** the *Growth* effect is activated at a given rank  
   **THEN** the system applies the per-rank adjustments: +1 Strength, +1 Stamina, +1 mass rank, −1 Stealth  
   **AND** applies per-2-rank changes: −1 Dodge, −1 Parry, +1 Intimidation  
   **Evidence:** HeroesHandbook-rules__chunk_109.md — Growth: stat adjustments per rank

2. **WHEN** *Growth* rank reaches multiples of 8  
   **THEN** the system applies the +1 Speed rank bonus  
   **Evidence:** HeroesHandbook-rules__chunk_109.md — Growth: +1 Speed per 8 ranks

---

## Story: Apply Shrinking Defense and Stealth Bonuses and Penalties per Rank

**Story type:** system

### Domain terms

- *Shrinking Stat Block* — per-rank and per-2-rank adjustments to active defenses, Stealth, Speed, and Intimidation

### Acceptance criteria

1. **WHEN** the *Shrinking* effect is activated  
   **THEN** the system applies per-rank: +1 Stealth  
   **AND** per-2-rank: +1 Dodge, +1 Parry, −1 Speed, −1 Intimidation  
   **Evidence:** HeroesHandbook-rules__chunk_129b.md — Shrinking: stat adjustments per rank

2. **WHEN** *Shrinking* is deactivated  
   **THEN** all adjustments are removed and traits return to base values  
   **Evidence:** HeroesHandbook-rules__chunk_129b.md — Shrinking: sustained; traits revert on deactivation

---

## Story: Enforce Variable Pool Size as Rank Times Five Points

**Story type:** system

### Domain terms

- *Pool Enforcement* — system ensures total allocated PP does not exceed rank × 5

### Acceptance criteria

1. **WHEN** a character reallocates their *Variable* pool  
   **THEN** the system prevents total allocation from exceeding rank × 5 PP  
   **AND** any unallocated points remain inactive (no effect built from unspent points)  
   **Evidence:** HeroesHandbook-rules__chunk_136.md — Variable: pool = rank × 5; unallocated = inactive

2. **WHEN** reallocation attempts exceed the pool size  
   **THEN** the system rejects the excess and prompts the character to reduce allocation  
   **Evidence:** HeroesHandbook-rules__chunk_136.md — pool cap enforced; excess rejected

---

## Story: Enforce PL Limits on Variable-Built Effects

**Story type:** system

### Domain terms

- *PL Limit Check* — checks each Variable-built effect against Power Level caps
- *Violation Block* — effect cannot be activated if it violates PL limits

### Acceptance criteria

1. **WHEN** a character allocates *Variable* pool to build an effect  
   **THEN** the system checks the resulting effect against current PL limits  
   **AND** blocks activation if any limit is violated  
   **Evidence:** HeroesHandbook-rules__chunk_136.md — Variable-built effects subject to PL limits

2. **WHEN** the built effect falls within PL limits  
   **THEN** the system activates it at the allocated rank  
   **Evidence:** HeroesHandbook-rules__chunk_136.md — compliant effects activate normally

---

## Story: Apply Healing Check and Remove Damage Condition from Most Severe

**Story type:** system

### Domain terms

- *Healing Check Result* — degrees of success determine how many conditions are removed
- *Most Severe First* — removal always starts from the worst condition

### Acceptance criteria

1. **WHEN** *Healing* is used on a target  
   **THEN** the system rolls the *Healing Check* vs. DC 10  
   **AND** removes one condition per degree of success starting with the most severe  
   **Evidence:** HeroesHandbook-rules__chunk_110.md — Healing check vs. DC 10; most severe first; one per degree

2. **WHEN** the *Healing Check* fails (does not meet DC 10)  
   **THEN** no conditions are removed  
   **AND** the once-per-scene restriction is still consumed  
   **Evidence:** HeroesHandbook-rules__chunk_110.md — failed check: no healing; scene limit still applies

---

## Story: Block Healing Reuse on Same Target Within Scene

**Story type:** system

### Domain terms

- *Scene Boundary* — a scene ends when the scene changes context; reuse is tracked per scene
- *Reuse Block* — system prevents a second *Healing* use on the same target within the same scene

### Acceptance criteria

1. **WHEN** *Healing* has been used on a target within the current scene  
   **THEN** the system blocks any further *Healing* attempts on that same target this scene  
   **AND** alerts the user that the target has already been healed this scene  
   **Evidence:** HeroesHandbook-rules__chunk_110.md — Healing: once per scene per target rule

2. **WHEN** a new scene begins  
   **THEN** the system resets the *Healing* reuse restriction for all targets  
   **Evidence:** HeroesHandbook-rules__chunk_110.md — scene reset removes the restriction

---

## Epic: Apply Per-Rank Modifiers

---

## Story: Set Default Action, Range, Duration for Effect Type

**Story type:** system

### Domain terms

- *Effect Type Default* — the standard action, range, and duration values for each power type
- *Attack Default* — Standard action, Close range, Instant duration
- *Defense Default* — None action, Personal range, Permanent duration
- *Movement Default* — Free action, Personal range, Sustained duration

### Acceptance criteria

1. **WHEN** an effect is created  
   **THEN** the system auto-populates action, range, and duration from the *Effect Type Default* for that type  
   **AND** displays these as the starting values before any modifiers are applied  
   **Evidence:** HeroesHandbook-rules__chunk_084.md — Effect Types: each type has default action/range/duration

2. **WHEN** the Player reviews Attack type defaults  
   **THEN** the system shows Standard action, Close range (for most), Instant duration  
   **Evidence:** HeroesHandbook-rules__chunk_084.md — Attack: Standard action required; allow resistance check

3. **WHEN** the Player reviews Defense type defaults  
   **THEN** the system shows None action (passive), Personal range, Permanent duration  
   **Evidence:** HeroesHandbook-rules__chunk_084.md — Defense: passive; permanent most common

4. **WHEN** the Player reviews Movement type defaults  
   **THEN** the system shows Free action, Personal range, Sustained duration  
   **Evidence:** HeroesHandbook-rules__chunk_084.md — Movement: Free action; sustained duration

---

## Story: Calculate Base Cost per Rank from Effect Definition

**Story type:** system

### Domain terms

- *Base Cost* — the unmodified cost per rank as defined for that specific effect
- *Cost Display* — system shows base cost before any modifiers are applied

### Acceptance criteria

1. **WHEN** an effect is selected  
   **THEN** the system displays its *Base Cost* per rank as defined in the effect catalog  
   **AND** uses this as the starting value for all modifier math  
   **Evidence:** HeroesHandbook-rules__chunk_083.md — Acquiring Powers: each effect has a standard base cost

2. **WHEN** no modifiers are applied  
   **THEN** *Cost per rank* equals *Base Cost*  
   **Evidence:** HeroesHandbook-rules__chunk_140.md — Applying Modifiers: modified cost starts from base; no modifiers = base cost

---

## Story: Apply Per-Rank Extra to Raise Cost per Rank

**Story type:** user

### Domain terms

- *Per-Rank Extra* — modifier that adds its rank value (usually +1) to cost per rank
- *Modified Cost per Rank* — base cost + per-rank extras − per-rank flaws

### Acceptance criteria

1. **WHEN** the Player applies a per-rank extra to an effect  
   **THEN** the system adds the extra's value (typically +1) to the *Base Cost*  
   **AND** recalculates *Modified Cost per Rank* = base + extras − flaws  
   **Evidence:** HeroesHandbook-rules__chunk_140.md — Applying Modifiers: extra adds to cost per rank

2. **WHEN** multiple per-rank extras are applied  
   **THEN** the system sums all extras' values and adds to the base cost  
   **Evidence:** HeroesHandbook-rules__chunk_140.md — multiple extras: each adds its value; sum applied

3. **WHEN** the Player reviews the modified cost  
   **THEN** the system shows the breakdown: base + each extra's contribution  
   **Evidence:** HeroesHandbook-rules__chunk_140.md — formula: modified cost = base + extras – flaws

---

## Story: Apply Per-Rank Flaw to Lower Cost per Rank

**Story type:** user

### Domain terms

- *Per-Rank Flaw* — modifier that subtracts its value (usually −1) from cost per rank
- *Minimum Cost Floor* — cost per rank cannot drop below 1 pp/rank

### Acceptance criteria

1. **WHEN** the Player applies a per-rank flaw  
   **THEN** the system subtracts the flaw's value from *Modified Cost per Rank*  
   **AND** enforces the *Minimum Cost Floor* of 1 pp/rank  
   **Evidence:** HeroesHandbook-rules__chunk_140.md — Applying Modifiers: flaw reduces cost; minimum 1 pp/rank

2. **WHEN** flaws would reduce cost per rank below 1  
   **THEN** the system caps cost per rank at 1 pp/rank  
   **AND** notes fractional cost rules apply for each additional flaw beyond the floor  
   **Evidence:** HeroesHandbook-rules__chunk_140.md — Fractional Costs: floor at 1; additional flaws = ranks per pp

3. **WHEN** the Player reviews the fractional cost rule  
   **THEN** the system explains: each additional –1 beyond the floor converts to "1 pp buys N ranks" (N increases by 1 per extra flaw)  
   **Evidence:** HeroesHandbook-rules__chunk_140.md — Fractional Costs section

---

## Story: Enforce Minimum One Point per Rank Floor After Flaws

**Story type:** system

### Domain terms

- *Cost Floor* — minimum 1 pp/rank regardless of flaw count
- *Fractional Cost Rule* — at floor, additional flaws give more ranks per 1 pp instead of reducing cost further

### Acceptance criteria

1. **WHEN** flaw math reduces cost per rank to exactly 1  
   **THEN** the system holds cost per rank at 1 and activates *Fractional Cost Rule* tracking  
   **Evidence:** HeroesHandbook-rules__chunk_140.md — floor at 1; fractional rules engage at floor

2. **WHEN** an additional per-rank flaw is applied at the floor  
   **THEN** the system increases ranks-per-pp (e.g., 1 flaw at floor = 1 pp/2 ranks; 2 flaws = 1 pp/3 ranks)  
   **AND** does not reduce cost per rank below 1  
   **Evidence:** HeroesHandbook-rules__chunk_140.md — fractional cost progression at 1 pp/rank floor

---

## Story: Apply Area Extra to Replace Attack Check with Dodge Save

**Story type:** user

### Domain terms

- *Area Extra* — per-rank extra replacing attack check with area coverage and Dodge save
- *Area DC* — DC 10 + effect rank; target Dodge check for area effect
- *Area Shape* — chosen at acquisition: Burst, Cloud, Cone, Cylinder, Line, Perception, Shapeable

### Acceptance criteria

1. **WHEN** the Player applies the *Area* extra to an effect  
   **THEN** the system removes the attack check requirement and replaces it with area targeting  
   **AND** sets *Area DC* = 10 + effect rank for the Dodge resistance check  
   **AND** prompts for *Area Shape* selection  
   **Evidence:** HeroesHandbook-rules__chunk_143.md — Area extra: removes attack check; Dodge DC = 10 + rank; shape choice

2. **WHEN** the *Area* shape is set to Burst  
   **THEN** the system applies a 30-foot radius (distance rank 0) centered on the target point  
   **Evidence:** HeroesHandbook-rules__chunk_143.md — Burst: 30-foot radius, distance rank 0

3. **WHEN** the *Area* effect is used  
   **THEN** all targets in the area make a Dodge check vs. *Area DC*; success halves the effect rank (round down, min 1)  
   **Evidence:** HeroesHandbook-rules__chunk_143.md — Dodge success: half rank; round down; minimum 1

4. **WHEN** the Player wants to exclude specific targets from the area  
   **THEN** the system notes the Selective extra is required for targeted exclusion  
   **BUT** without it, all targets in the area are affected  
   **Evidence:** HeroesHandbook-rules__chunk_143.md — Area: no exclusion without Selective extra

---

## Story: Apply Area Dodge Save DC as Ten Plus Effect Rank

**Story type:** system

### Domain terms

- *Area Dodge DC* — fixed as 10 + effect rank
- *Dodge Success Result* — effect is applied at half rank (round down, min 1)

### Acceptance criteria

1. **WHEN** an area effect activates  
   **THEN** the system sets the Dodge DC = 10 + current effect rank for all targets in the area  
   **Evidence:** HeroesHandbook-rules__chunk_143.md — Area DC formula: 10 + effect rank

2. **WHEN** a target succeeds the Dodge check  
   **THEN** the system applies the effect at half the current rank (round down, minimum rank 1)  
   **Evidence:** HeroesHandbook-rules__chunk_143.md — Dodge success: half rank, round down, min 1

---

## Story: Reduce Area Effect to Half Rank on Dodge Save Success

**Story type:** system

### Domain terms

- *Half-Rank Application* — effect applied at effect rank ÷ 2, rounded down, minimum 1

### Acceptance criteria

1. **WHEN** a target succeeds the Dodge save against an area effect  
   **THEN** the system applies the effect at half rank (round down)  
   **AND** uses a minimum of rank 1 if the result would be 0  
   **Evidence:** HeroesHandbook-rules__chunk_143.md — half-rank minimum of 1 on Dodge success

2. **WHEN** a target fails the Dodge save  
   **THEN** the system applies the full effect rank  
   **Evidence:** HeroesHandbook-rules__chunk_143.md — failed Dodge: full rank applies

---

## Story: Apply Multiattack Extra for Multiple Target Coverage

**Story type:** user

### Domain terms

- *Multiattack* — per-rank extra enabling multiple-target spray or single-target DC boost
- *Single-Target Mode* — +2 DC at 2 attack degrees; +5 DC at 3+ attack degrees
- *Multi-Target Mode* — one attack roll with penalty = number of targets; each target above Dodge is hit

### Acceptance criteria

1. **WHEN** the Player applies *Multiattack*  
   **THEN** the system notes the two available modes and costs +1 per rank  
   **Evidence:** HeroesHandbook-rules__chunk_143b.md — Multiattack: +1 per rank; two modes

2. **WHEN** the character uses *Single-Target Mode*  
   **THEN** the system adds +2 to effect DC at 2 degrees of attack success and +5 at 3+ degrees  
   **Evidence:** HeroesHandbook-rules__chunk_143b.md — single-target: +2 DC at 2 degrees; +5 at 3+

3. **WHEN** the character uses *Multi-Target Mode*  
   **THEN** the system applies a penalty equal to the number of targets to one attack roll  
   **AND** each target whose Dodge is exceeded is hit  
   **Evidence:** HeroesHandbook-rules__chunk_143b.md — multi-target: one roll; penalty = target count; hits all exceeded

---

## Story: Apply Multiattack Bonus DC on Multiple Success Degrees

**Story type:** system

### Domain terms

- *Degree-Based DC Boost* — additional DC added based on degrees of attack success beyond first

### Acceptance criteria

1. **WHEN** a *Multiattack* effect achieves 2 degrees of success on the attack roll  
   **THEN** the system adds +2 to the effect DC for the single-target use  
   **Evidence:** HeroesHandbook-rules__chunk_143b.md — 2 degrees = +2 DC bonus

2. **WHEN** 3 or more degrees of success are achieved  
   **THEN** the system adds +5 to the effect DC instead  
   **Evidence:** HeroesHandbook-rules__chunk_143b.md — 3+ degrees = +5 DC bonus

---

## Epic: Apply Flat Modifiers

---

## Story: Apply Accurate Extra for Attack Check Bonus

**Story type:** user

### Domain terms

- *Accurate* — flat extra granting +2 attack bonus per rank to a specific effect
- *PL Attack Cap* — Accurate bonus cannot push total attack bonus above PL × 2

### Acceptance criteria

1. **WHEN** the Player applies the *Accurate* extra  
   **THEN** the system adds +2 to attack checks for that effect per Accurate rank  
   **AND** charges 1 flat point per rank of bonus  
   **Evidence:** HeroesHandbook-rules__chunk_141.md — Accurate: flat +1 per rank; +2 attack per rank

2. **WHEN** adding *Accurate* would push total attack bonus above PL × 2  
   **THEN** the system blocks additional *Accurate* ranks beyond the cap  
   **Evidence:** HeroesHandbook-rules__chunk_141.md — Accurate: PL × 2 maximum attack bonus

3. **WHEN** the Player reviews *Accurate*'s scope  
   **THEN** the system confirms the bonus applies only to the specific effect it is applied to  
   **Evidence:** HeroesHandbook-rules__chunk_141.md — Accurate: effect-specific only

---

## Story: Apply Penetrating Extra to Overcome Impervious Defense

**Story type:** user

### Domain terms

- *Penetrating* — flat extra allowing damage to bypass Impervious Toughness up to its rank
- *Impervious Threshold* — attacks below this rank are completely ignored
- *Penetrating Rank* — the number of ranks of Impervious the extra overcomes

### Acceptance criteria

1. **WHEN** the Player applies *Penetrating* to a Damage or Blast effect  
   **THEN** the system charges 1 flat point per *Penetrating* rank  
   **AND** notes the extra allows the attack to affect Impervious targets up to the *Penetrating* rank  
   **Evidence:** HeroesHandbook-rules__chunk_141.md — Penetrating: flat 1 per rank; bypasses Impervious to degree of rank

2. **WHEN** the attack rank equals or exceeds the *Impervious Threshold*  
   **THEN** the character with Impervious must make a resistance check  
   **Evidence:** HeroesHandbook-rules__chunk_141.md — Penetrating: forces resistance check up to its rank

3. **WHEN** the *Penetrating* rank is lower than the Impervious Toughness  
   **THEN** the Impervious still negates damage above the *Penetrating* rank  
   **BUT** does not negate the portion at or below the *Penetrating* rank  
   **Evidence:** HeroesHandbook-rules__chunk_141.md — partial penetration: only up to Penetrating rank is forced through

---

## Story: Apply Activation Flaw to Require Power Preparation

**Story type:** user

### Domain terms

- *Activation* — flat flaw requiring a preparation action before the power's effects are available
- *Activation Cost* — −1 (move action) or −2 (standard action) flat points
- *Reactivation Requirement* — power must be reactivated after Nullification or deactivation

### Acceptance criteria

1. **WHEN** the Player applies the *Activation* flaw  
   **THEN** the system prompts for the activation action type (move or standard) and applies the flat point deduction  
   **AND** marks all effects in the power as unavailable until activated  
   **Evidence:** HeroesHandbook-rules__chunk_141b.md — Activation: flat flaw; −1 move or −2 standard action

2. **WHEN** the power with *Activation* is Nullified  
   **THEN** the system marks it as requiring reactivation  
   **AND** the character must spend the activation action again before using any effects  
   **Evidence:** HeroesHandbook-rules__chunk_141b.md — Activation: reactivation required after Nullify

3. **WHEN** the Player asks what *Activation* applies to  
   **THEN** the system confirms it applies to the entire power — all effects — not individual effects  
   **Evidence:** HeroesHandbook-rules__chunk_141b.md — Activation applies to whole power

---

## Story: Apply Check Required Flaw to Gate Effect on Skill Check

**Story type:** user

### Domain terms

- *Check Required* — flat flaw gating effect activation on a skill or ability check
- *Check DC* — 10 + extra ranks beyond base; natural 1 always fails
- *Effective Rank Bonus* — each point exceeding DC on success grants 1 extra effective rank

### Acceptance criteria

1. **WHEN** the Player applies *Check Required*  
   **THEN** the system charges −1 flat point per rank of the effect and prompts for the check type (skill or ability)  
   **Evidence:** HeroesHandbook-rules__chunk_141c.md — Check Required: −1 per rank; check type at acquisition

2. **WHEN** the check succeeds  
   **THEN** the system activates the effect  
   **AND** grants 1 effective rank per point exceeding the DC  
   **Evidence:** HeroesHandbook-rules__chunk_141c.md — Check Required: success grants extra ranks by margin

3. **WHEN** the check fails (including natural 1)  
   **THEN** the system blocks activation — the effect is not available this action  
   **Evidence:** HeroesHandbook-rules__chunk_141c.md — Check Required: failure blocks activation; natural 1 always fails

4. **WHEN** the effect already normally requires checks (attack checks, resistance checks)  
   **THEN** the *Check Required* check is in addition to those normal checks  
   **Evidence:** HeroesHandbook-rules__chunk_141c.md — Check Required is on top of normal checks

---

## Story: Apply Limited Flaw to Restrict Effect Circumstances

**Story type:** user

### Domain terms

- *Limited* — per-rank flaw restricting the effect to certain circumstances, targets, or conditions
- *Genuine Restriction* — must reduce utility by approximately half or more; GM determines qualification
- *Complication Distinction* — Limited is a mechanical cost reduction; complications are narrative events

### Acceptance criteria

1. **WHEN** the Player applies the *Limited* flaw  
   **THEN** the system charges −1 per rank and prompts for the limiting circumstance  
   **AND** flags the limitation for GM approval to confirm it meets the genuine restriction standard  
   **Evidence:** HeroesHandbook-rules__chunk_141d.md — Limited: −1 per rank; GM approval required

2. **WHEN** the GM reviews the *Limited* restriction  
   **THEN** the system confirms it qualifies if it genuinely reduces utility by approximately half or more  
   **BUT** rejects restrictions that are merely cosmetic or flavor-only  
   **Evidence:** HeroesHandbook-rules__chunk_141d.md — Limited: must be genuine mechanical restriction; ~half utility

3. **WHEN** the Player confuses *Limited* with a complication  
   **THEN** the system explains: *Limited* reduces mechanical cost; complications trigger narrative events and award hero points  
   **Evidence:** HeroesHandbook-rules__chunk_141d.md — Limited vs. complication distinction

---

## Story: Apply Removable Flaw to Convert Power to Device

**Story type:** user

### Domain terms

- *Removable* — flat flaw representing a power built into an item that can be taken
- *Removal Vulnerability* — power can be taken when character is stunned and defenseless, or via disarm/grab
- *Device Toughness* — item Toughness = character's PL

### Acceptance criteria

1. **WHEN** the Player applies the *Removable* flaw  
   **THEN** the system calculates the flat point deduction: −1 per 5 points of final power cost (or −2 if easily removable)  
   **AND** marks all effects in the power as unavailable if the item is taken  
   **Evidence:** HeroesHandbook-rules__chunk_153.md — Removable: flat flaw; –1 per 5 pp final cost; –2 if easily removable

2. **WHEN** the character is both stunned and defenseless  
   **THEN** the system marks the device as vulnerable to removal  
   **AND** allows an opponent to take the item  
   **Evidence:** HeroesHandbook-rules__chunk_153.md — Removable: taken when stunned+defenseless or via disarm/grab

3. **WHEN** the item is targeted for damage  
   **THEN** the system applies object damage rules with *Device Toughness* = character's PL  
   **Evidence:** HeroesHandbook-rules__chunk_153.md — Removable: item Toughness = PL; object damage rules apply

---

## Story: Calculate Final Power Cost with Flat Modifier Adjustments

**Story type:** system

### Domain terms

- *Final Power Cost* — (cost per rank × ranks) + flat extras − flat flaws
- *Flat Modifier Sequence* — flat modifiers applied after the per-rank × rank multiplication

### Acceptance criteria

1. **WHEN** a power has flat modifiers  
   **THEN** the system applies them after the per-rank cost × rank calculation  
   **AND** produces *Final Power Cost* = (cost per rank × ranks) + flat extras − flat flaws  
   **Evidence:** HeroesHandbook-rules__chunk_141.md — Flat-Value Modifiers: applied after per-rank × rank; formula given

2. **WHEN** flat flaws would reduce the final cost below 1 pp  
   **THEN** the system caps the total at 1 pp  
   **Evidence:** HeroesHandbook-rules__chunk_141.md — flat flaw: total cannot drop below 1 pp

---

## Story: Enforce Minimum One Point Total Power Cost After Flat Flaws

**Story type:** system

### Domain terms

- *Total Cost Floor* — minimum 1 pp total regardless of flat flaw count
- *Flat Flaw Cap* — system does not allow flat flaws to bring total below 1 pp

### Acceptance criteria

1. **WHEN** flat flaw math would reduce the total power cost below 1 pp  
   **THEN** the system caps the total at 1 pp  
   **BUT** does not reject the flaw configuration — the cost is simply floored  
   **Evidence:** HeroesHandbook-rules__chunk_141.md — flat flaw: cannot reduce total below 1 pp

2. **WHEN** the total power cost is already 1 pp  
   **THEN** the system prevents any additional flat flaws from reducing it further  
   **Evidence:** HeroesHandbook-rules__chunk_141.md — floor at 1 pp total

---

## Story: Apply Penetrating Rank Against Impervious Toughness Threshold

**Story type:** system

### Domain terms

- *Impervious Check* — applied when attack rank ≤ Impervious rank; normally no check required
- *Penetrating Override* — forces a resistance check up to the *Penetrating* rank even against Impervious

### Acceptance criteria

1. **WHEN** an attack with *Penetrating* targets a character with Impervious Toughness  
   **THEN** the system checks whether the attack rank is within the *Penetrating* rank range  
   **AND** if so, forces a Toughness check at the attack's normal DC  
   **Evidence:** HeroesHandbook-rules__chunk_141.md — Penetrating: forces Toughness check up to Penetrating rank

2. **WHEN** the attack rank exceeds the Impervious threshold without *Penetrating*  
   **THEN** the system already forces a check — *Penetrating* is not needed  
   **Evidence:** HeroesHandbook-rules__chunk_141.md — Impervious only blocks attacks ≤ its rank; Penetrating fills the gap

---

## Story: Require Activation Action Before Power Effects Become Available

**Story type:** system

### Domain terms

- *Activation Gate* — system blocks all power effects until activation action is spent
- *Activation Reset* — gate re-engages after Nullification or voluntary deactivation

### Acceptance criteria

1. **WHEN** a character has a power with *Activation* flaw  
   **THEN** all effects in that power are gated until the character spends the required activation action  
   **Evidence:** HeroesHandbook-rules__chunk_141b.md — Activation: all effects blocked until activation action spent

2. **WHEN** the activation action is spent  
   **THEN** the system unlocks all effects in the power for use  
   **Evidence:** HeroesHandbook-rules__chunk_141b.md — activation spent: power effects become available

3. **WHEN** the power is Nullified after activation  
   **THEN** the system re-engages the *Activation Gate* — the character must activate again  
   **Evidence:** HeroesHandbook-rules__chunk_141b.md — Nullify resets Activation gate

---

## Story: Gate Effect Activation on Check Required Skill Check Success

**Story type:** system

### Domain terms

- *Check Gate* — system blocks effect until *Check Required* check succeeds
- *Check Failure Block* — effect unavailable this action; character must try again next action

### Acceptance criteria

1. **WHEN** a character attempts to activate an effect with *Check Required*  
   **THEN** the system resolves the required check before allowing the effect  
   **AND** only activates the effect if the check succeeds  
   **Evidence:** HeroesHandbook-rules__chunk_141c.md — Check Required: must succeed check to activate

2. **WHEN** the check fails or rolls a natural 1  
   **THEN** the system blocks activation — the action is expended but the effect does not fire  
   **Evidence:** HeroesHandbook-rules__chunk_141c.md — failure: action expended; effect does not fire

---

## Story: Allow Removal of Device When Character is Stunned and Defenseless

**Story type:** system

### Domain terms

- *Removal Conditions* — stunned + defenseless simultaneously OR via disarm/grab action
- *Device Removal* — item is taken; all associated effects are immediately unavailable

### Acceptance criteria

1. **WHEN** a character with a *Removable* power is both stunned and defenseless  
   **THEN** the system marks the device as available for removal by opponents  
   **AND** an opponent may take the item (standard action)  
   **Evidence:** HeroesHandbook-rules__chunk_153.md — Removable: removal when stunned + defenseless

2. **WHEN** the device is removed  
   **THEN** the system immediately marks all power effects as unavailable  
   **Evidence:** HeroesHandbook-rules__chunk_153.md — removed device: all effects lost

3. **WHEN** the character recovers the device  
   **THEN** all power effects become available again (subject to *Activation* if applicable)  
   **Evidence:** HeroesHandbook-rules__chunk_153.md — recovering device restores effects

---

## Epic: Assign Power Descriptors

---

## Story: Assign Origin Descriptor to Power Set

**Story type:** user

### Domain terms

- *Origin Descriptor* — identifies how the character came to have their powers (narrative)
- *Power Set Scope* — typically applies to the character's entire set of powers, not one effect
- *Narrative Role* — no direct mechanical effect; governs story interactions and GM rulings

### Acceptance criteria

1. **WHEN** the Player assigns an *Origin Descriptor*  
   **THEN** the system records it against the character's power set  
   **AND** notes it costs no power points  
   **Evidence:** HeroesHandbook-rules__chunk_155.md — origin descriptor: narrative; free; covers power set

2. **WHEN** the Player selects an origin (Accidental, Bestowed, Invented, Mutant, Training)  
   **THEN** the system confirms the selection and notes it rarely has direct mechanical effects  
   **AND** flags it as a GM-relevant narrative attribute  
   **Evidence:** HeroesHandbook-rules__chunk_155.md — origin descriptors list; primarily narrative function

3. **WHEN** the *Origin Descriptor* interacts with a setting element  
   **THEN** the GM adjudicates the interaction; the system defers to GM on narrative effects  
   **Evidence:** HeroesHandbook-rules__chunk_155.md — origin descriptor: GM-adjudicated interactions

---

## Story: Assign Source Descriptor to Power Effect

**Story type:** user

### Domain terms

- *Source Descriptor* — identifies the energy or force a power draws upon
- *Mechanical Significance* — Nullify and Immunity match against *Source Descriptor* values
- *Multiple Sources* — a power can have multiple source descriptors if it draws on more than one

### Acceptance criteria

1. **WHEN** the Player assigns a *Source Descriptor*  
   **THEN** the system records it against the specific effect and notes it costs no power points  
   **Evidence:** HeroesHandbook-rules__chunk_155.md — source descriptor: free; per-effect; mechanical significance

2. **WHEN** the *Source Descriptor* is Magical  
   **THEN** Nullify (Magical effects) and Immunity (Magical effects) match against this effect  
   **Evidence:** HeroesHandbook-rules__chunk_155.md — source descriptor: Nullify/Immunity target matching example

3. **WHEN** a power draws on multiple sources (e.g., Psionic and Technological)  
   **THEN** the system allows multiple *Source Descriptors* on the same effect  
   **AND** both descriptors are valid targets for Nullify and Immunity  
   **Evidence:** HeroesHandbook-rules__chunk_155.md — multiple source descriptors allowed on one effect

---

## Story: Assign Result Descriptor to Power Effect

**Story type:** user

### Domain terms

- *Result Descriptor* — identifies the observable output of the effect (Fire, Ice, Lightning, etc.)
- *GM Ruling Target* — result descriptor triggers GM narrative interactions and adjudication

### Acceptance criteria

1. **WHEN** the Player assigns a *Result Descriptor*  
   **THEN** the system records it against the effect and confirms it costs no power points  
   **Evidence:** HeroesHandbook-rules__chunk_155.md — result descriptor: free; observable output label

2. **WHEN** the result descriptor implies environmental interaction (Fire → flammable objects)  
   **THEN** the GM adjudicates the interaction; the system does not auto-resolve narrative effects  
   **Evidence:** HeroesHandbook-rules__chunk_155.md — result descriptor: GM-adjudicated for environmental triggers

---

## Story: Match Power Descriptor Against Immunity Effect Coverage

**Story type:** system

### Domain terms

- *Descriptor Match* — power's source or result descriptor falls within the Immunity scope
- *Automatic Immunity* — no resistance check; effect is fully blocked
- *GM Arbitration* — descriptor matching for borderline cases is GM-adjudicated

### Acceptance criteria

1. **WHEN** a power with a specific descriptor targets an immune character  
   **THEN** the system checks whether the power's descriptor falls within the Immunity's *Covered Effect Set*  
   **AND** grants automatic success if there is a clear match  
   **Evidence:** HeroesHandbook-rules__chunk_155.md — Immunity matching: descriptor-based; automatic on clear match

2. **WHEN** the descriptor match is ambiguous (e.g., "electricity" vs. "lightning")  
   **THEN** the system defers to GM for arbitration  
   **AND** notes that descriptors are intentionally flexible; GM is the final authority  
   **Evidence:** HeroesHandbook-rules__chunk_157.md — Changing Descriptors in Play; GM is final arbiter

3. **WHEN** there is no match  
   **THEN** normal resistance applies — no automatic immunity  
   **Evidence:** HeroesHandbook-rules__chunk_112.md — Immunity only applies to matched descriptors

---

## Story: Match Power Descriptor Against Nullify Effect Target

**Story type:** system

### Domain terms

- *Nullify Target Descriptor* — descriptor defined at acquisition; must match incoming power
- *Match Logic* — same flexible rules as Immunity; GM arbitrates ambiguity

### Acceptance criteria

1. **WHEN** *Nullify* is used against a power  
   **THEN** the system checks whether the power's descriptor matches the *Nullify Target Descriptor*  
   **AND** allows the attack sequence to proceed if there is a match  
   **Evidence:** HeroesHandbook-rules__chunk_125.md — Nullify: targets effects by descriptor

2. **WHEN** the descriptor match is ambiguous  
   **THEN** the system defers to the GM  
   **Evidence:** HeroesHandbook-rules__chunk_157.md — GM adjudicates descriptor interactions

3. **WHEN** the power's descriptor does not match the *Nullify Target Descriptor*  
   **THEN** the system blocks the Nullify attempt — the attack cannot target that effect  
   **Evidence:** HeroesHandbook-rules__chunk_125.md — Nullify cannot target unmatched descriptors

---

## Story: Approve Descriptor Interaction Between Powers

**Story type:** user

### Domain terms

- *GM Approval* — Gamemaster reviews and approves descriptor interactions for series appropriateness
- *Interaction Ruling* — GM decision on whether two descriptors interact narratively or mechanically

### Acceptance criteria

1. **WHEN** two descriptors interact in a non-obvious way  
   **THEN** the GM reviews and provides an *Interaction Ruling*  
   **AND** the ruling is recorded against the powers in question  
   **Evidence:** HeroesHandbook-rules__chunk_157.md — Changing Descriptors in Play; GM final authority on interactions

2. **WHEN** a descriptor is proposed to change during play  
   **THEN** the system requires *GM Approval* before the change takes effect  
   **Evidence:** HeroesHandbook-rules__chunk_157.md — descriptors may not change without GM approval

---

## Epic: Organize Power Arrays

---

## Story: Build Power Array with Base Effect

**Story type:** user

### Domain terms

- *Array* — container grouping multiple effects under mutual exclusivity with shared cost
- *Base Effect* — the primary effect in the array; establishes the cost ceiling for alternates
- *Mutual Exclusivity Rule* — only one non-Dynamic effect in the array can be active at a time

### Acceptance criteria

1. **WHEN** the Player starts building a *Power Array*  
   **THEN** the system prompts for the *Base Effect* as the primary member  
   **AND** calculates the base effect's total cost as the ceiling for *Alternate Effects*  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — Array: base effect establishes cost ceiling for alternates

2. **WHEN** the *Base Effect* is confirmed  
   **THEN** the system displays the array with the base effect's total cost as the maximum alternate budget  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — Array cost structure; base effect cost = alternate budget

3. **WHEN** the Player activates one effect in the array  
   **THEN** the system enforces *Mutual Exclusivity Rule*: all other non-Dynamic effects are inactive  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — Array: one effect active at a time; mutual exclusivity

---

## Story: Add Alternate Effect to Array within Primary Effect Cost Limit

**Story type:** user

### Domain terms

- *Alternate Effect* — variant effect in the array; costs 1 flat point; total cost ≤ primary
- *Total Cost Check* — alternate's total cost (rank × cost/rank + flat modifiers) must ≤ primary total
- *Permanent Effect Restriction* — permanent effects cannot be alternates

### Acceptance criteria

1. **WHEN** the Player adds an *Alternate Effect* to the array  
   **THEN** the system charges 1 flat point for the alternate  
   **AND** validates that the alternate's total cost ≤ primary effect's total cost  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — Alternate Effect: 1 flat point; total cost ≤ primary

2. **WHEN** the alternate's total cost exceeds the primary  
   **THEN** the system rejects the alternate configuration  
   **AND** prompts the Player to reduce rank or remove modifiers to bring the cost within the limit  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — alternate total cost must not exceed primary

3. **WHEN** the Player attempts to add a permanent effect as an alternate  
   **THEN** the system rejects it — permanent effects cannot be switched in/out of arrays  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — permanent effects cannot be alternates

---

## Story: Add Dynamic Alternate Effect for Simultaneous Use

**Story type:** user

### Domain terms

- *Dynamic Alternate Effect* — variant that can operate simultaneously with other Dynamic effects
- *Dynamic Cost* — 2 flat points per Dynamic alternate (base effect costs 1 extra to become dynamic)
- *Simultaneous Use* — Dynamic effects can be active at the same time, sharing the pool

### Acceptance criteria

1. **WHEN** the Player adds a *Dynamic Alternate Effect*  
   **THEN** the system charges 2 flat points per dynamic alternate (or 1 extra to make the base dynamic)  
   **AND** notes that dynamic effects can operate simultaneously, sharing the array's total pool  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — Dynamic Alternate: 2 flat points; simultaneous use allowed

2. **WHEN** multiple *Dynamic Alternate Effects* are active simultaneously  
   **THEN** each operates at whatever rank the allocated points support  
   **AND** combined point allocation cannot exceed the total array pool  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — combined allocation: total cannot exceed pool

3. **WHEN** the Player asks how standard alternates differ from dynamic  
   **THEN** the system confirms standard alternates are mutually exclusive; dynamic ones can run simultaneously  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — standard vs. dynamic distinction

---

## Story: Switch Active Effect in Array as Free Action

**Story type:** user

### Domain terms

- *Array Switch* — free action to change which non-Dynamic effect is active in the array
- *One Switch per Turn* — switching is limited to once per turn as a free action

### Acceptance criteria

1. **WHEN** the Player switches the active effect in an array  
   **THEN** the system allows the switch as a free action, once per turn  
   **AND** the previously active effect deactivates; the newly selected effect activates  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — Array: switch as free action once per turn

2. **WHEN** the Player attempts a second switch in the same turn  
   **THEN** the system blocks it — only one *Array Switch* per turn is allowed  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — once per turn limit on array switching

---

## Story: Enforce Array Mutual Exclusivity Rule for Non-Dynamic Effects

**Story type:** system

### Domain terms

- *Mutual Exclusivity* — only one standard (non-Dynamic) effect active at a time
- *Active Effect Tracking* — system tracks which non-Dynamic effect is currently active

### Acceptance criteria

1. **WHEN** a standard alternate effect is activated  
   **THEN** the system deactivates all other non-Dynamic effects in the array  
   **AND** the newly selected effect takes precedence  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — mutual exclusivity: one non-Dynamic active at a time

2. **WHEN** a Dynamic effect is active alongside standard effects  
   **THEN** the system enforces mutual exclusivity only among non-Dynamic members  
   **AND** allows the Dynamic effect to remain active simultaneously  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — Dynamic effects exempt from mutual exclusivity

---

## Story: Propagate Array Disable Equally to All Alternate Effects

**Story type:** system

### Domain terms

- *Array Disable* — when any effect in the array is Nullified or disabled, all effects are equally affected
- *Propagation* — the disable state spreads to every member of the array

### Acceptance criteria

1. **WHEN** any effect in the array is Nullified  
   **THEN** the system marks the entire array as disabled — all effects are equally affected  
   **AND** the character loses access to all effects in the array until the Nullify is resolved  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — Array: disable propagates equally to all alternates

2. **WHEN** the Nullify is resolved (effect re-activated or Nullify countered)  
   **THEN** the entire array becomes available again  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — array restored when Nullify is resolved

---

## Story: Reallocate Power Points Among Dynamic Array Effects per Turn

**Story type:** user

### Domain terms

- *Dynamic Reallocation* — redistributing the pool among active Dynamic effects once per turn
- *Free Action Reallocation* — costs a free action; once per turn
- *Pool Ceiling* — combined allocation cannot exceed total array pool

### Acceptance criteria

1. **WHEN** the Player reallocates Dynamic effects  
   **THEN** the system allows reallocation once per turn as a free action  
   **AND** the combined allocation must not exceed the total array pool  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — Dynamic reallocation: free action; once per turn

2. **WHEN** the Player sets an allocation below the active effect's current rank  
   **THEN** the system reduces the effect's active rank immediately  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — Dynamic: reduced allocation = reduced active rank

3. **WHEN** the Player does not allocate points to a Dynamic effect  
   **THEN** that effect is inactive at rank 0 for that turn  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — unallocated Dynamic effects are inactive

---

## Story: Enforce Dynamic Effect Point Total Against Array Pool Size

**Story type:** system

### Domain terms

- *Pool Enforcement* — system prevents total dynamic allocation from exceeding array pool
- *Over-Allocation Block* — system rejects allocations that exceed the pool

### Acceptance criteria

1. **WHEN** dynamic allocations are submitted  
   **THEN** the system sums all allocations and compares to the pool size  
   **AND** rejects the submission if the total exceeds the pool  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — Dynamic: combined allocation ≤ pool size enforced

2. **WHEN** an allocation is within the pool limit  
   **THEN** the system applies the allocation; each dynamic effect activates at the allocated rank  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — valid allocation: effects activate at allocated rank

3. **WHEN** the array pool changes (e.g., via Weaken on base effect)  
   **THEN** the system recalculates the ceiling and may force re-allocation if existing allocations exceed the new ceiling  
   **Evidence:** HeroesHandbook-rules__chunk_143c.md — pool ceiling is dynamic; recalculation required on change
