---
fidelity: specification
artifact: story-scenarios
format: md
story: Simulation Engine --> Adjust Throttle
---

# Adjust Throttle

System story: the Simulation Engine applies the throttle from committed ++Activation Orders++.

### Evidence

| Source | Note |
|--------|------|
| `sandbox/space-battle/story-map.md` § Decisions | user: system story applied from Commit Activation Orders |
| `../../examples/starfighters.examples.md` | intended top speeds: X-wing *4*, TIE fighter *5* |
| — | **flagged:** no limit on how much speed can change in one activation; not confirmed |

## Behaviors

#### Scenario Outline: Simulation Engine sets speed from the ordered throttle

*Given* the ++Engagement++ *Dogfight One* is in progress with {`starfighter`} active  
  *And* {`starfighter`} (*{`type`}*) has ++Speed++ {`speed_before`}  
  *And* its committed ++Activation Orders++ set throttle {`throttle`}  
*When* the **Simulation Engine** adjusts the throttle of {`starfighter`}  
*Then* {`starfighter`} has ++Speed++ {`speed_after`}  
  *And* the Simulation Engine continues with **Maneuver Starfighter**

#### Examples

| scenario | `starfighter` | `type` | `speed_before` | `throttle` | `speed_after` |
|----------|---------------|--------|----------------|------------|---------------|
| ++Speed up++ | Red Five | X-wing | *0* | *3* | *3* |
| ++Capped at X-wing top speed++ | Red Five | X-wing | *3* | *6* | *4* |
| ++TIE at full throttle++ | Black Two | TIE fighter | *2* | *5* | *5* |
| ++Full stop++ | Black Two | TIE fighter | *5* | *0* | *0* |
