---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Get Number

## Epic: Keep Current Number

### Story: Keep Current Number

**Story type:** pml-my

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/LineNumber/ProspectLineNumberSelector.tsx` (`Keep current number` → `../onboarding/select-sim`)
- Granola: `.context/granola-notes/screenshot-wall.md` L32 · `miro-areas/02-pick-number.png`
- Run: `.context/sandbox-walkthrough/live.log` L3261 (`Keep current number` on `/onboarding`) · `.context/sandbox-walkthrough/walk-checkout.md` L25–L28 · L105

Keep current number GWT is on Choose a Number in this file.
## Epic: Sweep Stale Reservations

### Story: Sweep Stale Number Reservations

**Story type:** Care

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/inventory/payloads/msisdn.ts` `msisdnReservePayload` (`previousNumber` reserved→available)
- Granola: `.context/granola-notes/screenshot-wall.md` L77 · `miro-areas/03-resource-inventory-dashboard.png` · `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L65 · `.context/granola-notes/weird-stuff.md` L19

**Flagged: No dedicated midtier endpoint found for a Care sweep action. The `msisdnReservePayload` `previousNumber` mechanism (reserved → available) releases an individual reservation when a new number is reserved; no batch sweep route exists. Intended: Care views mass Reserved ++MSISDN++ resources in the Mavenir DEP Resource Inventory and releases them to available.**

#### Scenario: Sweep stale number reservations

*Given* ++MSISDN++ resources have been reserved but have no active order  
  *And* Care observes mass Reserved ++MSISDN++ resources in the Mavenir DEP Resource Inventory  
*When* Care sweeps stale ++MSISDN++ reservations  
*Then* Mavenir transitions the stale ++MSISDN++ resources from reserved to available  
  *And* the released ++MSISDN++ resources are visible as available in the Mavenir DEP Resource Inventory
