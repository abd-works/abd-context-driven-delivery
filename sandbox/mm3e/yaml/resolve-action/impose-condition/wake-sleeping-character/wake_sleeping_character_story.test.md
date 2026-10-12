---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Wake Sleeping Character

**Evidence:** observed — HeroesHandbook.md lines 1376. A hearing Perception check with three or more degrees of success wakes the character. So does sudden movement, such as shaking, or an effect that allows a resistance check. Waking removes defenseless, stunned, and unaware.

### Domain terms

- ++Asleep++ — defenseless, stunned, and unaware until the character wakes

## Behaviors

#### Scenario: Three degrees of hearing Perception wake the character

*Given* a ++Character++ who is asleep
  *And* a hearing Perception check has three degrees of success
*When* the **Player** wakes the sleeping character with that check
*Then* the character is awake
  *And* defenseless, stunned, and unaware are removed
  *And* the outcome continues in Stabilize Dying Character

#### Scenario: Fewer than three degrees leave the character asleep

*Given* a ++Character++ who is asleep
  *And* a hearing Perception check has two degrees of success
*When* the **Player** tries to wake the sleeping character with that check
*Then* the character stays asleep
  *And* the character stays defenseless, stunned, and unaware

#### Scenario: Shaking the character wakes them

*Given* a ++Character++ who is asleep
*When* the **Player** shakes the sleeping character
*Then* the character is awake
  *And* defenseless, stunned, and unaware are removed

#### Scenario: An effect that allows a resistance check wakes the character

*Given* a ++Character++ who is asleep
  *And* an effect allows a resistance check
*When* the **Simulator** resolves that effect against the sleeping character
*Then* the character is awake
  *And* defenseless, stunned, and unaware are removed
