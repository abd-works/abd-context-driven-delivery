---
rule: vehicle-has-means
kind: quality
fidelity: [specification, engineering]
artifact: scenarios/*.md
scanner: vehicle-has-means-scanner.py
---

# Rule: Vehicle Has Means of Transportation

Every scenario that describes a **Vehicle** MUST declare its means of propulsion —
the mechanism that moves the vehicle. A vehicle without a stated propulsion mechanism
is under-specified and cannot be validated for fitness-for-purpose.

## DO

- Name the propulsion type explicitly: *electric motor 150 kW*, *diesel engine 2.0L*, *hydrogen fuel cell*, *pedal-driven*, *sail-powered*
- State the propulsion in a **Given** step as part of the **Vehicle**'s known properties

## DON'T

- Describe a **Vehicle** only by its brand or model without stating how it moves
- Leave propulsion implied ("a car", "a truck") without a concrete mechanism

## Example (pass)

*Given* a **Vehicle** *ElectraVan Model-7* with means of propulsion *electric motor 150 kW*

## Example (fail)

*Given* a **Vehicle** *ElectraVan Model-7* registered for fleet use
*(no means of propulsion stated)*
