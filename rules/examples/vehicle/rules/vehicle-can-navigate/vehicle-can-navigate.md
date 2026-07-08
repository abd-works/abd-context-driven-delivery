---
rule: vehicle-can-navigate
kind: quality
fidelity: [specification, engineering]
artifact: scenarios/*.md
scanner: vehicle-can-navigate-scanner.py
---

# Rule: Vehicle Can Navigate

Every scenario that describes a **Vehicle** MUST declare its navigation capability —
the system or mechanism that directs the vehicle toward a destination. A vehicle with
no stated navigation capability cannot be confirmed as operationally usable.

## DO

- Name the navigation system explicitly: *GPS navigation with lane-assist*, *manual steering*, *autopilot mode*, *compass-guided*, *waypoint routing*
- State navigation in a **Given** step as part of the **Vehicle**'s known properties

## DON'T

- Describe a **Vehicle** without any indication of how it is directed or steered
- Assume navigation is implied by the vehicle type

## Example (pass)

*Given* a **Vehicle** *ElectraVan Model-7* with navigation *GPS navigation with lane-assist*

## Example (fail)

*Given* a **Vehicle** *ElectraVan Model-7* with means of propulsion *electric motor 150 kW*
*(no navigation capability stated)*
