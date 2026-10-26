---
fidelity: specification
artifact: story-scenarios
format: md
story: Simulation Engine --> Resolve Starfighter Movement
---

# Resolve Starfighter Movement

### Evidence

| Source | Note |
|--------|------|
| `sandbox/space-battle/story-map.md` § Decisions | user: each starfighter's movement is resolved on its own activation |
| `../../examples/starfighters.examples.md` | intended grid: x east, y north, diagonal step = 1 cell |
| — | **flagged:** stopping at the arena edge and blocking on an occupied cell are proposals, not user decisions |

## Behaviors

#### Scenario Outline: Simulation Engine moves the starfighter along its heading

*Given* the ++Engagement++ *Dogfight One* is in progress with {`starfighter`} active  
  *And* {`starfighter`} is at {`position_before`} with ++Heading++ {`heading`} and ++Speed++ {`speed`}  
*When* the **Simulation Engine** resolves the movement of {`starfighter`}  
*Then* {`starfighter`} is at {`position_after`}  
  *And* if its ++Activation Orders++ name a laser target, the Simulation Engine continues with **Fire Laser Cannons**; otherwise the next starfighter in the activation order is asked to **Commit Activation Orders**

#### Examples

| scenario | `starfighter` | `position_before` | `heading` | `speed` | `position_after` |
|----------|---------------|-------------------|-----------|---------|------------------|
| ++Fly east++ | Red Five | *(2,10)* | *90* | *3* | *(5,10)* |
| ++Fly west++ | Black Two | *(17,10)* | *270* | *5* | *(12,10)* |
| ++Fly diagonally++ | Red Five | *(5,10)* | *45* | *2* | *(7,12)* |
| ++Stop at the arena edge++ | Black Two | *(2,10)* | *270* | *5* | *(0,10)* |

#### Scenario 2: Starfighter stops short of an occupied cell

*Given* the ++Engagement++ *Dogfight One* is in progress with ++Red Five++ active  
  *And* ++Red Five++ is at *(5,10)* with ++Heading++ *90* and ++Speed++ *4*  
  *And* ++Black Two++ is at *(8,10)*  
*When* the **Simulation Engine** resolves the movement of ++Red Five++  
*Then* ++Red Five++ is at *(7,10)*, the last free cell before ++Black Two++
