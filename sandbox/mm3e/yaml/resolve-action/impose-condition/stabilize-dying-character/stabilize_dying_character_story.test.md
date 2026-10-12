---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Stabilize Dying Character

**Evidence:** observed — HeroesHandbook.md lines 1386–1390. Becoming dying calls for an immediate Fortitude check at DC 15. One degree of success changes nothing. Two degrees stabilize. Failure leaves the character dying. Three or more degrees of failure, including across checks, mean the character dies. A Fortitude check repeats each round. Another character can stabilize with Treatment DC 15. **Flagged** — Healing is named here and specified in the Powers chapter, which this slice does not include.

### Domain terms

- ++Dying++ — incapacitated and near death, checking Fortitude until the character stabilizes or dies

## Behaviors

#### Scenario: One degree of success on the dying check changes nothing

*Given* a ++Character++ has just gained dying
*When* the **Player** rolls Fortitude against ++Difficulty Class++ *15* and the result is *15*
*Then* the character stays dying
  *And* nothing else happens from that success
  *And* the outcome continues in Shake Entranced Character

#### Scenario: Two degrees of success stabilize the character

*Given* a ++Character++ has just gained dying
*When* the **Player** rolls Fortitude against ++Difficulty Class++ *15* and the result is *20*
*Then* the character stabilizes
  *And* dying is removed

#### Scenario: A failed dying check leaves the character dying

*Given* a ++Character++ is dying
*When* the **Player** rolls Fortitude against ++Difficulty Class++ *15* and the result is *14*
*Then* the character stays dying

#### Scenario: Three degrees of failure on one check mean the character dies

*Given* a ++Character++ is dying
  *And* the character's Fortitude is *-5*
*When* the **Player** rolls Fortitude against ++Difficulty Class++ *15* and the die shows *5*
*Then* the ++Check Result++ is *0*, three degrees of failure
  *And* the character dies

#### Scenario: Three failed Fortitude checks mean the character dies

*Given* a ++Character++ is dying
  *And* two earlier Fortitude checks against ++Difficulty Class++ *15* have failed
*When* the **Player** rolls Fortitude against ++Difficulty Class++ *15* and the result is *14*
*Then* this third failed check brings the failure to three checks
  *And* the character dies

#### Scenario: Two checks that add up to three degrees of failure mean the character dies

*Given* a ++Character++ is dying
  *And* an earlier Fortitude check against ++Difficulty Class++ *15* failed with two degrees of failure
*When* the **Player** rolls Fortitude against ++Difficulty Class++ *15* and the result is *14*
*Then* the degrees of failure now total three
  *And* the character dies

#### Scenario: Treatment at difficulty class 15 stabilizes the character

*Given* a ++Character++ is dying
  *And* another character attempts Treatment
*When* the **Player** rolls Treatment against ++Difficulty Class++ *15* and the result is *15*
*Then* the dying character stabilizes
  *And* dying is removed

#### Scenario: The dying character checks Fortitude again next round

*Given* a ++Character++ is dying
  *And* the Fortitude check this round failed with one degree of failure
*When* the **Simulator** starts the character's next round
*Then* the character rolls Fortitude against ++Difficulty Class++ *15* again
  *And* the character is still dying until that check stabilizes or kills
