---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Apply Tool Penalty

**Evidence:** observed — HeroesHandbook.md lines 1166–1172. Missing tools are a -5 penalty when the Gamemaster allows the attempt. Makeshift tools reduce that penalty to -2. The Gamemaster may forbid the attempt.

### Domain terms

- ++Tool Penalty++ — -5 without the tools the task requires, or -2 with makeshift tools

## Behaviors

#### Scenario: Missing tools impose a major penalty when the attempt is allowed

*Given* the task requires tools
  *But* the ++Character++ does not have those tools
  *And* the **Gamemaster** allows the attempt
  *And* the check's other terms total *15* and the ++Difficulty Class++ is *15*
*When* the **Gamemaster** applies the tool penalty
*Then* the ++Check Result++ is *10*
  *And* the check fails
  *And* the outcome continues in Lead Team Check

#### Scenario: Makeshift tools reduce the penalty to two

*Given* the ++Character++ has makeshift tools
  *And* the **Gamemaster** allows the makeshift tools
  *And* the check's other terms total *15* and the ++Difficulty Class++ is *15*
*When* the **Gamemaster** applies the tool penalty
*Then* the ++Check Result++ is *13*
  *And* the check fails by less than the missing-tool penalty

#### Scenario: The Gamemaster can forbid the attempt

*Given* the task requires tools
  *But* the ++Character++ does not have those tools
*When* the **Gamemaster** forbids the attempt
*Then* the task does not get a check
  *But* no tool penalty is applied because there is no check

#### Scenario: The proper tools add no tool penalty

*Given* the ++Character++ has the tools the task names
  *And* the check's other terms total *15*
*When* the **Gamemaster** applies tool circumstances
*Then* the ++Check Result++ stays *15*
  *But* no ++Tool Penalty++ is applied
