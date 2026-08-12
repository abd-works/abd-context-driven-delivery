---
fidelity: [scenarios]
artifact: [thin-slice]
format: md
section: body
---

# Thin slicing — Courier Ops incremental backlog

## Product / context

**Product:** Courier ops — manage drivers, vehicles, packages, and delivery routes

**Slicing intent:** Prove route-by-zone planning and package hang before staffing, driver execution, or fleet master data.

**Spine vs optional:** Create route → add zones → recalculate path → assign package sits on the spine. Zone browsing, path detail, package search, zone shape tools, and staffing are real work but not required for the smallest marketable planning slice.

## Increments

### Increment 1: Dispatcher plans a zoned route and hangs packages

**Outcome:** Dispatcher creates a delivery route, enters zones so stops appear, recalculates a shorter path when adjacency allows, and hangs a package on an on-route stop.

**Slicing notes:** Ops intake assumed to have already created/reused stops from package addresses; no customer booking; no driver app in this slice.

**Decision prompt:** Ready to complete zone and stop management after this slice?

**Stories in this increment** *(order reflects flow within the slice):*

- *Create Delivery Route*
- *Add Zone To Route*
- *Recalculate Route Path*
- *Assign Package To Stop*

### Increment 2: Complete zone and stop management on a route

**Outcome:** Dispatcher can remove zones, reorder them, view stops, see the path, and fully manage package assignments on stops.

**Slicing notes:** Builds directly on Increment 1; no new infrastructure needed — all mechanics are extensions of the route planner screen.

**Decision prompt:** Ready to add zone discovery and package search after this slice?

**Stories in this increment** *(order reflects flow within the slice):*

- *Remove Zone From Route*
- *View Stops On Route*
- *Reorder Route Zones*
- *View Route Path*
- *View Stop Order*
- *Unassign Package From Stop*
- *Move Package Between Stops*
- *List Packages On Route*

### Increment 3: Zone discovery and package search

**Outcome:** Dispatcher can browse and search zones before adding them, preview which stops a zone would contribute, and search packages by label when assigning.

**Slicing notes:** These stories enhance the zone picker and package assignment UX; they share screens from Increment 1–2 but add search/filter behaviour.

**Decision prompt:** Ready to understand why paths change and add zone shape tools after this slice?

**Stories in this increment** *(order reflects flow within the slice):*

- *Search Zones*
- *Preview Zone Stops*
- *Search Packages*
- *View Path Change Summary*

### Increment 4: Zone shape tools

**Outcome:** Dispatcher can define and edit zone boundaries (draw polygon, import from file) and preview coverage before committing.

**Slicing notes:** Requires map/boundary UI infrastructure; deferred until core planning flow is stable. View Zone Detail and List Zones are read-only prerequisites included here.

**Decision prompt:** Ready to staff and dispatch routes after this slice?

**Stories in this increment** *(order reflects flow within the slice):*

- *List Zones*
- *View Zone Detail*
- *Define Zone Boundary*
- *Preview Zone Coverage*
- *Edit Zone Boundary*
- *Import Zone Boundary*

### Increment 5: Staff and release the route

**Outcome:** Dispatcher assigns driver and vehicle and dispatches the route to the driver.

**Slicing notes:** Deferred — Staff Routes theme still scaffold in the sketch. Requires fleet registry (Maintain Fleet theme).

**Decision prompt:** Ready to open the driver app after this slice?

**Stories in this increment:**

- *Assign Driver To Route*
- *Assign Vehicle To Route*
- *Dispatch Route*
- *Recall Dispatched Route*
