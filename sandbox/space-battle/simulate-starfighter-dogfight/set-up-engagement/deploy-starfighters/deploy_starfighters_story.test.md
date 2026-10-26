---
fidelity: specification
artifact: story-scenarios
format: md
story: Commander --> Deploy Starfighters
---

# Deploy Starfighters

### Evidence

| Source | Note |
|--------|------|
| `sandbox/space-battle/story-map.md` § Walking skeleton | intended — first step of the skeleton |
| `../../examples/starfighters.examples.md` | intended values: Dogfight One, Red Five, Black Two |

## Behaviors

#### Scenario 1: Commander deploys an X-wing and a TIE fighter into the arena

*Given* the ++Engagement++ *Dogfight One* is in setup with a *20 × 20* ++Arena++  
  *But* no ++Starfighter++ is deployed yet  
*When* the **Commander** deploys ++Red Five++ (*X-wing*, flown by the Pilot) at *(2,10)* heading *90*  
  *And* the **Commander** deploys ++Black Two++ (*TIE fighter*, flown by an AI Pilot) at *(17,10)* heading *270*  
*Then* *Dogfight One* lists ++Red Five++ at *(2,10)* heading *90* with ++Hull++ *4*  
  *And* *Dogfight One* lists ++Black Two++ at *(17,10)* heading *270* with ++Hull++ *3*  
  *And* *Dogfight One* is ready for the Commander to **Launch Engagement**

#### Scenario 2: Commander cannot deploy a starfighter outside the arena

*Given* the ++Engagement++ *Dogfight One* is in setup with a *20 × 20* ++Arena++  
*When* the **Commander** deploys ++Red Five++ at *(25,10)*  
*Then* the deployment is rejected with *"Position (25,10) is outside the arena"*  
  *And* *Dogfight One* lists no ++Starfighter++

#### Scenario 3: Commander cannot deploy two starfighters on the same cell

*Given* the ++Engagement++ *Dogfight One* has ++Red Five++ deployed at *(2,10)*  
*When* the **Commander** deploys ++Black Two++ at *(2,10)*  
*Then* the deployment is rejected with *"(2,10) is already occupied by Red Five"*  
  *And* *Dogfight One* lists only ++Red Five++
