---
fidelity: specification
artifact: story-scenarios
format: md
story: Simulation Engine --> Damage Hull
---

# Damage Hull

### Evidence

| Source | Note |
|--------|------|
| `sandbox/space-battle/story-map.md` § Walking skeleton | intended |
| `../../examples/starfighters.examples.md` | intended hull: X-wing *4*, TIE fighter *3*; laser damage *1* |
| — | X-wing shields are out of the walking skeleton (Absorb Hit With Deflector Shields comes later) |

### Background

*Given* the ++Engagement++ *Dogfight One* is in progress with ++Red Five++ active  

## Behaviors

#### Scenario 1: Hit reduces a TIE fighter's hull

*Given* ++Black Two++ (*TIE fighter*) has ++Hull++ *3*  
*When* the **Simulation Engine** applies *1* laser damage to ++Black Two++  
*Then* ++Black Two++ has ++Hull++ *2*  
  *And* the next starfighter in the activation order is asked to **Commit Activation Orders**

#### Scenario 2: Last hull point lost

*Given* ++Black Two++ (*TIE fighter*) has ++Hull++ *1*  
*When* the **Simulation Engine** applies *1* laser damage to ++Black Two++  
*Then* ++Black Two++ has ++Hull++ *0*  
  *And* the Simulation Engine continues with **Destroy Starfighter** for ++Black Two++
