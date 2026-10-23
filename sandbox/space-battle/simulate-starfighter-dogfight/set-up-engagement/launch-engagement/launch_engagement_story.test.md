---
fidelity: specification
artifact: story-scenarios
format: md
story: Commander --> Launch Engagement
---

# Launch Engagement

### Evidence

| Source | Note |
|--------|------|
| `sandbox/space-battle/story-map.md` § Walking skeleton | intended |
| `sandbox/space-battle/story-map.md` § Decisions | turn-based battle; one person-flown starfighter |
| `../../examples/starfighters.examples.md` | intended values |

## Behaviors

#### Scenario 1: Commander launches an engagement with both sides deployed

*Given* the ++Engagement++ *Dogfight One* is in setup  
  *And* ++Red Five++ (*X-wing*) and ++Black Two++ (*TIE fighter*) are deployed  
*When* the **Commander** launches *Dogfight One*  
*Then* *Dogfight One* is in progress at ++Turn++ *1*  
  *And* the Simulation Engine starts **Order Starfighter Activations** for ++Turn++ *1*

#### Scenario 2: Commander cannot launch without an opposing starfighter

*Given* the ++Engagement++ *Dogfight One* is in setup with ++Red Five++ (*X-wing*) deployed  
  *But* no *TIE fighter* is deployed  
*When* the **Commander** launches *Dogfight One*  
*Then* the launch is rejected with *"An engagement needs at least one X-wing and one TIE fighter"*  
  *And* *Dogfight One* stays in setup

#### Scenario 3: Commander cannot launch without a starfighter for the Pilot

*Given* the ++Engagement++ *Dogfight One* is in setup with ++Red Five++ and ++Black Two++ deployed  
  *But* neither starfighter is flown by the Pilot  
*When* the **Commander** launches *Dogfight One*  
*Then* the launch is rejected with *"One starfighter must be flown by the Pilot"*  
  *And* *Dogfight One* stays in setup
