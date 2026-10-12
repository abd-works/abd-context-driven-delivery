---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Retry Failed Effect

**Evidence:** observed — HeroesHandbook.md lines 1461–1463. Extra effort only permits another attempt. It grants no other benefit. **Flagged** — which effects require extra effort to retry is in the Powers chapter, which this slice does not include.

### Domain terms

- ++Retry++ — another attempt at an effect, permitted by extra effort and nothing more

## Behaviors

#### Scenario: Extra effort permits another attempt and nothing else

*Given* an effect has failed by a degree that requires extra effort to retry
  *And* the hero has not used extra effort this turn
*When* the **Player** uses extra effort to retry the effect
*Then* the hero may attempt the effect again
  *But* the retry grants no bonus, extra action, or rank increase
  *And* the outcome continues in Apply Effort Fatigue

#### Scenario: The new attempt can succeed

*Given* extra effort has permitted a retry
  *And* the ++Difficulty Class++ is *15*
*When* the **Player** retries the effect and the result is *15*
*Then* the effect succeeds

#### Scenario: The new attempt can fail

*Given* extra effort has permitted a retry
  *And* the ++Difficulty Class++ is *15*
*When* the **Player** retries the effect and the result is *10*
*Then* the effect fails

#### Scenario: A failed effect that does not require extra effort is a normal check

*Given* an effect failed
  *But* the effect does not require extra effort to retry
*When* the **Player** attempts the effect again
*Then* the attempt does not spend extra effort
