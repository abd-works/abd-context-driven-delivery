---
fidelity: specification
artifact: story-scenarios
format: md
story: Simulation Engine --> Resolve Shot Hit
---

# Resolve Shot Hit

### Evidence

| Source | Note |
|--------|------|
| `sandbox/space-battle/story-map.md` § Walking skeleton | intended |
| — | **flagged:** a shot hits on a 1–100 roll at or under the hit chance for its range (range 1: *90*, 2: *70*, 3: *50*). The roll and the chances are proposals. The user has not said whether combat is random or deterministic. |

## Behaviors

#### Scenario Outline: Simulation Engine resolves a laser shot by range and roll

*Given* the ++Engagement++ *Dogfight One* is in progress with ++Red Five++ active  
  *And* a laser shot from ++Red Five++ at ++Black Two++ from ++Range++ {`range`}  
  *And* the Simulation Engine's roll for the shot is {`roll`}  
*When* the **Simulation Engine** resolves the shot  
*Then* the shot is a {`result`}  
  *And* {`next`}

#### Examples

| scenario | `range` | `roll` | `result` | `next` |
|----------|---------|--------|----------|--------|
| ++Close hit++ | *1* | *85* | hit | the Simulation Engine applies *1* damage to Black Two with **Damage Hull** |
| ++Mid-range hit++ | *2* | *70* | hit | the Simulation Engine applies *1* damage to Black Two with **Damage Hull** |
| ++Mid-range miss++ | *2* | *71* | miss | the next starfighter is asked to **Commit Activation Orders** |
| ++Long-range miss++ | *3* | *51* | miss | the next starfighter is asked to **Commit Activation Orders** |
