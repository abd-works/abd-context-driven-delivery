---
fidelity: specification
artifact: story-scenarios
format: md
story: Simulation Engine --> Fire Laser Cannons
---

# Fire Laser Cannons

System story: after movement, the Simulation Engine fires at the laser target named in the committed ++Activation Orders++.

### Evidence

| Source | Note |
|--------|------|
| `sandbox/space-battle/story-map.md` § Walking skeleton | intended |
| `sandbox/space-battle/story-map.md` § Decisions | user: fix scenario validate failures; Fire Laser Cannons is a system story |
| `../../examples/starfighters.examples.md` | intended laser range *3* and 90° firing arc for both types |

### Background

*Given* the ++Engagement++ *Dogfight One* is in progress with ++Red Five++ active  
  *And* ++Red Five++ (*X-wing*) has moved this activation and is at *(5,10)* with ++Heading++ *90*  
  *And* ++Red Five++'s ++Activation Orders++ name ++Black Two++ as laser target  

## Behaviors

#### Scenario 1: Simulation Engine fires at a target in range and in arc

*Given* ++Black Two++ is at *(7,10)*, ++Range++ *2*, straight ahead  
*When* the **Simulation Engine** fires ++Red Five++'s laser cannons at ++Black Two++  
*Then* a laser shot at ++Black Two++ from ++Range++ *2* is recorded  
  *And* the Simulation Engine continues with **Resolve Shot Hit**

#### Scenario 2: Simulation Engine holds fire at a target out of range

*Given* ++Black Two++ is at *(10,10)*, ++Range++ *5*  
*When* the **Simulation Engine** fires ++Red Five++'s laser cannons at ++Black Two++  
*Then* the shot is refused with *"Black Two is out of range (5 > 3)"*  
  *And* no shot is recorded  
  *And* the next starfighter in the activation order is asked to **Commit Activation Orders**

#### Scenario 3: Simulation Engine holds fire at a target outside the firing arc

*Given* ++Black Two++ is at *(5,8)*, ++Range++ *2*, due south  
*When* the **Simulation Engine** fires ++Red Five++'s laser cannons at ++Black Two++  
*Then* the shot is refused with *"Black Two is outside the firing arc"*  
  *And* no shot is recorded
