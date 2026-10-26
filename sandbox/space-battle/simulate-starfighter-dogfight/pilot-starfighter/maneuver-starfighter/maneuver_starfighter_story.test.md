---
fidelity: specification
artifact: story-scenarios
format: md
story: Simulation Engine --> Maneuver Starfighter
---

# Maneuver Starfighter

System story: the Simulation Engine turns the starfighter by the ordered amount. In 2D, maneuvering changes ++Heading++.

### Evidence

| Source | Note |
|--------|------|
| `sandbox/space-battle/story-map.md` § Decisions | user: 2D battle; system story applied from Commit Activation Orders |
| `../../examples/starfighters.examples.md` | intended max turn: X-wing *90°*, TIE fighter *135°*; headings in 45° steps |

## Behaviors

#### Scenario Outline: Simulation Engine turns the starfighter within its max turn

*Given* the ++Engagement++ *Dogfight One* is in progress with {`starfighter`} active  
  *And* {`starfighter`} (*{`type`}*) has ++Heading++ {`heading_before`}  
  *And* its committed ++Activation Orders++ turn {`ordered_turn`}  
*When* the **Simulation Engine** maneuvers {`starfighter`}  
*Then* {`starfighter`} has ++Heading++ {`heading_after`}  
  *And* the Simulation Engine continues with **Resolve Starfighter Movement**

#### Examples

| scenario | `starfighter` | `type` | `heading_before` | `ordered_turn` | `heading_after` |
|----------|---------------|--------|------------------|----------------|-----------------|
| ++Turn right within limit++ | Red Five | X-wing | *90* | *45 right* | *135* |
| ++X-wing turn clipped to 90°++ | Red Five | X-wing | *90* | *135 right* | *180* |
| ++TIE turns tighter++ | Black Two | TIE fighter | *270* | *135 left* | *135* |
| ++Turn wraps past north++ | Black Two | TIE fighter | *315* | *90 right* | *45* |
