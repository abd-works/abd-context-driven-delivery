---
fidelity: specification
artifact: story-scenarios
format: md
story: Simulation Engine --> Order Starfighter Activations
---

# Order Starfighter Activations

### Evidence

| Source | Note |
|--------|------|
| `sandbox/space-battle/story-map.md` § Decisions | user: starfighters act one at a time each turn, fastest first |
| — | **flagged:** "fastest" is taken as current ++Speed++, ties broken by higher top speed, then by name. The user has not confirmed this yet. |

### Background

*Given* the ++Engagement++ *Dogfight One* is in progress  
  *And* ++Red Five++ (*X-wing*, top speed *4*) and ++Black Two++ (*TIE fighter*, top speed *5*) are in the arena  

## Behaviors

#### Scenario Outline: Simulation Engine orders the turn fastest first

*Given* ++Red Five++ ended the last turn at ++Speed++ {`red_five_speed`}  
  *And* ++Black Two++ ended the last turn at ++Speed++ {`black_two_speed`}  
*When* the **Simulation Engine** orders the activations for ++Turn++ {`turn`}  
*Then* the activation order is {`activation_order`}  
  *And* the pilot of {`first`} is asked to **Commit Activation Orders**

#### Examples

| scenario | `turn` | `red_five_speed` | `black_two_speed` | `activation_order` | `first` |
|----------|--------|------------------|-------------------|--------------------|---------|
| ++TIE faster++ | *2* | *2* | *4* | Black Two, Red Five | Black Two |
| ++X-wing faster++ | *3* | *4* | *1* | Red Five, Black Two | Red Five |
| ++Same speed, TIE has higher top speed++ | *4* | *3* | *3* | Black Two, Red Five | Black Two |
| ++First turn, both stationary++ | *1* | *0* | *0* | Black Two, Red Five | Black Two |

#### Scenario 2: A destroyed starfighter gets no activation

*Given* ++Black Two++ has been destroyed  
*When* the **Simulation Engine** orders the activations for ++Turn++ *5*  
*Then* the activation order is *Red Five* only
