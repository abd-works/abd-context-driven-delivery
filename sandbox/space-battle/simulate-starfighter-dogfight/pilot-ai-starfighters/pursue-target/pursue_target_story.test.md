---
fidelity: specification
artifact: story-scenarios
format: md
story: AI Pilot --> Pursue Target
---

# Pursue Target

The AI Pilot plans ++Activation Orders++ that close on its target, then commits them like the Pilot does.

### Evidence

| Source | Note |
|--------|------|
| `sandbox/space-battle/story-map.md` § Walking skeleton | intended — the AI side of the skeleton |
| — | **flagged:** pursuit tactics (full throttle, turn toward target, fire when in arc and range) are proposals, not user decisions |

### Background

*Given* ++Black Two++ (*TIE fighter*) is the active starfighter, flown by the AI Pilot  
  *And* ++Red Five++ is ++Black Two++'s target  

## Behaviors

#### Scenario 1: AI Pilot closes head-on and fires when in range

*Given* ++Black Two++ is at *(10,10)* with ++Heading++ *270*  
  *And* ++Red Five++ is at *(7,10)*, in ++Black Two++'s ++Firing Arc++ at ++Range++ *3*  
*When* the **AI Pilot** plans ++Black Two++'s ++Activation Orders++  
*Then* the orders are throttle *1*, turn *none*, fire lasers at ++Red Five++  
  *And* the AI Pilot commits them through **Commit Activation Orders**

#### Scenario 2: AI Pilot turns toward a target it is not facing

*Given* ++Black Two++ is at *(17,10)* with ++Heading++ *270*  
  *And* ++Red Five++ is at *(17,2)*, due south  
*When* the **AI Pilot** plans ++Black Two++'s ++Activation Orders++  
*Then* the orders are throttle *5*, turn *90 left*, no laser target  
  *And* the AI Pilot commits them through **Commit Activation Orders**

#### Scenario 3: AI Pilot closes at full throttle when the target is out of range

*Given* ++Black Two++ is at *(17,10)* with ++Heading++ *270*  
  *And* ++Red Five++ is at *(5,10)*, ahead at ++Range++ *12*  
*When* the **AI Pilot** plans ++Black Two++'s ++Activation Orders++  
*Then* the orders are throttle *5*, turn *none*, no laser target  
  *And* the AI Pilot commits them through **Commit Activation Orders**
