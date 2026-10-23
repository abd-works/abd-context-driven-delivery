---
fidelity: specification
artifact: story-scenarios
format: md
story: Pilot --> Commit Activation Orders
---

# Commit Activation Orders

### Evidence

| Source | Note |
|--------|------|
| `sandbox/space-battle/story-map.md` § Decisions | user: a person flies one starfighter; on its activation its pilot commits orders |
| `sandbox/space-battle/story-map.md` § Decisions | user: throttle, maneuver, power and target lock are system stories applied from these orders |

### Background

*Given* the ++Engagement++ *Dogfight One* is at ++Turn++ *1* with activation order *Black Two, Red Five*  

## Behaviors

#### Scenario 1: Pilot commits orders on Red Five's activation

*Given* ++Black Two++ has finished its ++Activation++  
  *And* ++Red Five++ (*X-wing*) is at *(2,10)* heading *90* with ++Speed++ *0*  
*When* the **Pilot** commits ++Activation Orders++ for ++Red Five++: throttle *3*, turn *none*, fire lasers at ++Black Two++  
*Then* the orders are accepted for ++Red Five++  
  *And* the Simulation Engine applies them, starting with **Adjust Throttle**

#### Scenario 2: Pilot cannot commit orders out of turn

*Given* ++Black Two++ is the active starfighter  
  *But* ++Black Two++ has not finished its ++Activation++  
*When* the **Pilot** commits ++Activation Orders++ for ++Red Five++: throttle *3*  
*Then* the orders are rejected with *"It is Black Two's activation"*  
  *And* ++Red Five++ keeps ++Speed++ *0*

#### Scenario 3: Pilot holds course with no orders changed

*Given* ++Black Two++ has finished its ++Activation++  
  *And* ++Red Five++ is at *(5,10)* heading *90* with ++Speed++ *3*  
*When* the **Pilot** commits ++Activation Orders++ for ++Red Five++ with no throttle, turn or target change  
*Then* the orders are accepted as *hold course*  
  *And* the Simulation Engine goes straight to **Resolve Starfighter Movement** at ++Speed++ *3*
