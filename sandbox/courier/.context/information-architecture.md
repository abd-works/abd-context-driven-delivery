---
fidelity: mockup
artifact: information-architecture
format: md
---

# UX — Courier Ops: Plan Delivery Routes

**Sources / context:** `.context/sessions/courier-ops/cdd-sketch.md` (Plan Delivery Routes specification sketch; locked decisions)

═══════════════════════════════════════════════════════════
  SITE MAP
═══════════════════════════════════════════════════════════

Dispatcher Home
  ├─ [top nav] Routes ────────────────→ Route List
  └─ [top nav] Zones ─────────────────→ Zone List

Route List
  ├─ [action] Create route ───────────→ Route Planner
  └─ [action] Open route ─────────────→ Route Planner

Route Planner
  ├─ [action] Add zone ───────────────→ Add Zone To Route (modal)
  ├─ [action] Reorder zones ──────────→ Route Planner (reordered)
  ├─ [action] Recalculate path ───────→ Route Planner (updated)
  ├─ [action] Remove zone ────────────→ Route Planner (updated)
  ├─ [action] Open stop ──────────────→ Stop Packages
  └─ [secondary nav] Back ────────────→ Route List

Add Zone To Route (modal)
  └─ [action] Save ───────────────────→ Route Planner (updated)

Stop Packages
  ├─ [action] Assign package ─────────→ Stop Packages (updated)
  ├─ [action] Unassign package ───────→ Stop Packages (updated)
  ├─ [action] Move package ───────────→ Move Package (modal)
  └─ [secondary nav] Back ────────────→ Route Planner

Move Package (modal)
  └─ [action] Confirm ────────────────→ Stop Packages (updated)

Zone List
  └─ [action] Open zone ──────────────→ Zone Detail

Zone Detail
  ├─ [action] Edit boundary ──────────→ Zone Detail (updated)
  └─ [secondary nav] Back ────────────→ Zone List

═══════════════════════════════════════════════════════════
  SCREENS
═══════════════════════════════════════════════════════════

[ Dispatcher Home ]                             dashboard
  ┌─────────────────────────────────────────┐
  │ Courier Ops                             │
  │ [ Routes ]  [ Zones ]  [ Fleet ]        │
  │                                         │
  │  Today's routes                         │
  │  RT-001  3 zones  12 stops  Pending     │
  │  RT-002  2 zones   7 stops  Dispatched  │
  │                                         │
  │  [ + New Route ]                        │
  └─────────────────────────────────────────┘
  Stories (~1): Create Delivery Route
  Domain terms: Delivery Route
  key:
    [ btn ] top-nav tabs · [ + ] primary action
    on [ Routes ] → Route List
    on [ Zones ] → Zone List


[ Route List ]                                  list
  ┌─────────────────────────────────────────┐
  │ Routes                  [ + New Route ] │
  │ ─────────────────────────────────────── │
  │ RT-001  3 zones  12 stops  Pending      │
  │ RT-002  2 zones   7 stops  Dispatched   │
  │ RT-003  1 zone    0 stops  Draft        │
  └─────────────────────────────────────────┘
  Stories (~1): Create Delivery Route
  Domain terms: Delivery Route, Zone, Stop
  key:
    on row → Route Planner
    on [ + New Route ] → Route Planner (new)


[ Route Planner ]                               split-screen
  ┌───────────────────┬─────────────────────────┐
  │ Zones (order)     │ Path + Stops on route   │
  │ ─────────────────  ─────────────────────────│
  │ 1 › North ‹       │ path: North → West      │
  │ 2   West          │       → East            │
  │ 3   East          │ (shorter path applied)  │
  │                   │                         │
  │ [ + Zone ]        │ Stops                   │
  │ [ ↑ ] [ ↓ ]       │ › Dock-9 ‹  2 pkgs      │
  │ [ Recalculate ]   │   Dock-12   0 pkgs      │
  │ [ Remove Zone ]   │   Dock-15   1 pkg       │
  │                   │                         │
  │                   │ [ Open Stop ]           │
  └───────────────────┴─────────────────────────┘
  Stories (~4): Add Zone To Route · Reorder Route Zones · Recalculate Route Path · View Stops On Route
  Domain terms: Zone order, Route path, Stop on route
  key:
    ›sel‹ selected · [ btn ] action button · [ ↑ ][ ↓ ] reorder
    path line = calculated from zone order then shortened when adjacent zones allow
    on [ + Zone ] → Add Zone To Route (modal)
    on [ Recalculate ] → same screen; path and zone order may change
    on [ Open Stop ] → Stop Packages


[ Add Zone To Route ]                           modal-dialog
  ┌────────────────────────────────┐
  │ Add Zone to Route              │
  │                                │
  │ Zone  [ North        ▾ ]       │
  │                                │
  │ ! Zone already on route        │
  │                                │
  │ [ Add ] [ Cancel ]             │
  └────────────────────────────────┘
  Stories (~1): Add Zone To Route
  Domain terms: Zone
  key:
    [▾] dropdown of available zones · ! inline validation
    on [ Add ] → Route Planner (zone appended to order; path recalculates)


[ Stop Packages ]                               list
  ┌─────────────────────────────────────────┐
  │ ← Route Planner                         │
  │ Stop: Dock-9  (Zone North)              │
  │ ─────────────────────────────────────── │
  │ Packages on stop                        │
  │  P-100  Acme Corp · 12 Oak St           │
  │  P-101  Beta Ltd  · 12 Oak St           │
  │                                         │
  │ Unassigned in zone                      │
  │  P-108  Gamma Inc · 14 Oak St           │
  │                                         │
  │ [ Assign ] [ Unassign ] [ Move ]        │
  └─────────────────────────────────────────┘
  Stories (~3): Assign Package To Stop · Unassign Package From Stop · Move Package Between Stops
  Domain terms: Package, Stop, Zone
  key:
    on [ Assign ] → package hangs on this stop for the route
    on [ Unassign ] → package removed from this stop
    on [ Move ] → Move Package (modal)
    // only packages at this stop's address (or unassigned in zone) shown


[ Move Package ]                                modal-dialog
  ┌────────────────────────────────┐
  │ Move Package P-100             │
  │                                │
  │ From: Dock-9 (Zone North)      │
  │ To    [ Dock-12      ▾ ]       │
  │       (Zone North)             │
  │                                │
  │ [ Move ] [ Cancel ]            │
  └────────────────────────────────┘
  Stories (~1): Move Package Between Stops
  Domain terms: Package, Stop
  key:
    [▾] dropdown lists only on-route stops
    on [ Move ] → Stop Packages (package now on new stop)


[ Zone List ]                                   list
  ┌─────────────────────────────────────────┐
  │ Zones                    [ + New Zone ] │
  │ ─────────────────────────────────────── │
  │ North  12 stops                         │
  │ West    7 stops                         │
  │ East    5 stops                         │
  └─────────────────────────────────────────┘
  Stories (~2): List Zones · Define Zone Boundary
  Domain terms: Zone, Stop
  key:
    on row → Zone Detail


[ Zone Detail ]                                 form
  ┌─────────────────────────────────────────┐
  │ ← Zones                                 │
  │ Zone: North                             │
  │ ─────────────────────────────────────── │
  │ Name  [ North_______________ ]          │
  │                                         │
  │ Boundary  [ map / polygon editor ]      │
  │                                         │
  │ Stops in zone  12                       │
  │                                         │
  │ [ Save Boundary ] [ Cancel ]            │
  └─────────────────────────────────────────┘
  Stories (~2): Define Zone Boundary · Edit Zone Boundary
  Domain terms: Zone, Zone boundary, Stop
  key:
    [ map / polygon editor ] = boundary draw tool (placeholder; detail at front_end_code)
    on [ Save Boundary ] → Zone Detail (updated)
