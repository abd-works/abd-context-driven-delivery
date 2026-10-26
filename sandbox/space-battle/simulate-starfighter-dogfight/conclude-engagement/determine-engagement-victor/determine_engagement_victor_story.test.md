---
fidelity: specification
artifact: story-scenarios
format: md
story: Simulation Engine --> Determine Engagement Victor
---

# Determine Engagement Victor

### Evidence

| Source | Note |
|--------|------|
| `sandbox/space-battle/story-map.md` § Walking skeleton | intended — last step of the skeleton |
| — | **flagged:** "a side wins when the other side has no starfighters left" is a proposal |

## Behaviors

#### Scenario 1: X-wing side wins when the last TIE fighter is destroyed

*Given* the ++Engagement++ *Dogfight One* is at ++Turn++ *4*  
  *And* ++Red Five++ (*X-wing*) has ++Hull++ *2*  
  *But* ++Black Two++, the only *TIE fighter*, is destroyed  
*When* the **Simulation Engine** determines the engagement victor  
*Then* *Dogfight One* is over with victor *X-wing side*  
  *And* the Commander can **Report Battle Statistics**

#### Scenario 2: TIE fighter side wins when the Pilot's X-wing is destroyed

*Given* the ++Engagement++ *Dogfight One* is at ++Turn++ *6*  
  *And* ++Black Two++ (*TIE fighter*) has ++Hull++ *1*  
  *But* ++Red Five++, the only *X-wing*, is destroyed  
*When* the **Simulation Engine** determines the engagement victor  
*Then* *Dogfight One* is over with victor *TIE fighter side*

#### Scenario 3: Engagement continues while both sides have starfighters

*Given* the ++Engagement++ *Dogfight One* is at ++Turn++ *2*  
  *And* ++Red Five++ has ++Hull++ *4* and ++Black Two++ has ++Hull++ *2*  
*When* the **Simulation Engine** determines the engagement victor  
*Then* *Dogfight One* has no victor yet  
  *And* once every starfighter has activated, ++Turn++ *3* starts with **Order Starfighter Activations**
