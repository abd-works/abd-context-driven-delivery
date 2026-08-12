---
fidelity: [scenarios]
artifact: [story-map]
format: md
section: body
---

# Story Map — Courier Ops

**Sources / context:** `.context/sessions/courier-ops/cdd-sketch.md`; `.context/information-architecture.md`

---

(E) Plan Delivery Routes
    **Sources / context:** `cdd-sketch.md` theme Plan Delivery Routes
    (E) Enter Zones On Route
        (S) Dispatcher --> Create Delivery Route
        (S) Dispatcher --> Add Zone To Route
        (S) Dispatcher --> Remove Zone From Route
        (S) Dispatcher --> View Stops On Route
        (S) Dispatcher --> Search Zones
        (S) Dispatcher --> Preview Zone Stops
    (E) Sequence Route Path
        (S) Dispatcher --> Reorder Route Zones
        (S) Dispatcher --> Recalculate Route Path
        (S) Dispatcher --> View Route Path
        (S) Dispatcher --> View Stop Order
        (S) Dispatcher --> View Path Change Summary
    (E) Hang Packages On Stops
        (S) Dispatcher --> Assign Package To Stop
        (S) Dispatcher --> Unassign Package From Stop
        (S) Dispatcher --> Move Package Between Stops
        (S) Dispatcher --> List Packages On Route
        (S) Dispatcher --> Search Packages
    (E) Shape Delivery Zones
        (S) Dispatcher --> Define Zone Boundary
        (S) Dispatcher --> Edit Zone Boundary
        (S) Dispatcher --> List Zones
        (S) Dispatcher --> View Zone Detail
        (S) Dispatcher --> Import Zone Boundary
        (S) Dispatcher --> Preview Zone Coverage

---

## Scope boundary

**In scope:** Dispatcher plans routes by entering ordered zones; stops appear when they fall in entered zones; packages hang on on-route stops; path from zone order then shorter-path check.

**Out of scope:** Customer booking; staffing; driver execution; fleet registry (other sketch themes, not yet generated).
