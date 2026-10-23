---
fidelity: specification
artifact: story-scenarios
format: md
story: Simulation Engine --> Destroy Starfighter
---

# Destroy Starfighter

### Evidence

| Source | Note |
|--------|------|
| `sandbox/space-battle/story-map.md` § Walking skeleton | intended |

## Behaviors

#### Scenario 1: Starfighter with no hull is destroyed

*Given* the ++Engagement++ *Dogfight One* is at ++Turn++ *4* with ++Red Five++ and ++Black Two++ in the arena  
  *And* ++Black Two++ is at *(7,10)* with ++Hull++ *0*  
*When* the **Simulation Engine** destroys ++Black Two++  
*Then* ++Black Two++ is marked destroyed and is no longer in the ++Arena++  
  *And* its cell *(7,10)* is free  
  *And* the Simulation Engine checks for a winner with **Determine Engagement Victor**
