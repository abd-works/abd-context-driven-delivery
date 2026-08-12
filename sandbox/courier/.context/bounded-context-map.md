<!--
  Bounded Context Map — Courier Ops
  Sources: .context/sessions/courier-ops/cdd-sketch.md
  CE contracts: .context/clean-engineering-model.md
-->

# Bounded Context Map — Courier Ops

**Sources / context:** `.context/sessions/courier-ops/cdd-sketch.md` (Plan Delivery Routes specification sketch; Staff Routes scaffold for Fleet)
**CE contracts:** `.context/clean-engineering-model.md`

---

## Context Map

```
  ┌──────────────────────────────────────────┐
  │  PackageIntake                           │
  │  team: Courier ops intake                │
  │  packages/                               │
  │                                          │
  │  Package — registers + resolves address  │
  └──────────────────┬───────────────────────┘
                     │ Customer/Supplier (upstream)
                     │ Address → Stop create/reuse
                     │ PackageId + StopId → assignment
                     ▼
  ┌──────────────────────────────────────────┐
  │  Routing                                 │
  │  team: Courier dispatch                  │
  │  routes/, zones/                         │
  │                                          │
  │  Route, Zone, Stop — plan + path         │
  └──────────────────────────────────────────┘
                     ▲
                     │ Customer/Supplier (upstream)
                     │ DriverId + VehicleId → staffing
                     │ (scaffold — Staff Routes not yet generated)
  ┌──────────────────┴───────────────────────┐
  │  Fleet                                   │
  │  team: Courier fleet                     │
  │  fleet/                                  │
  │                                          │
  │  Driver, Vehicle — identity for staffing │
  └──────────────────────────────────────────┘
```

### Context inventory

| Context | Team | Scope | Implementation |
| Routing | Courier dispatch | Routes, zones, stops, path, package assignments | monolith module |
| PackageIntake | Courier ops intake | Register and import packages; resolve address to stop | monolith module |
| Fleet | Courier fleet | Drivers and vehicles available to staff routes | monolith module (scaffold) |

### Integration arcs

| Arc | Pattern | What crosses | How |
| PackageIntake → Routing | Customer/Supplier | `Address` → Stop creation/reuse; `PackageId` + `StopId` → route assignment | Synchronous call: `Zone.find_or_create_stop(address)` at register/import; `Route.assign_package` at planning |
| Fleet → Routing | Customer/Supplier | `DriverId`, `VehicleId` → route staffing | Synchronous call at assign-driver/assign-vehicle on Route (scaffold — not yet integrated) |

---

## Routing

- **Owning team:** Courier dispatch
- **Scope:** Delivery routes that enter ordered zones; stops that fall in zones; route path calculated from zone order then shorter-path check; packages hung on on-route stops
- **Implementation:** monolith module (`routes/`, `zones/`)

### Route

- **Root:** Route
- **Boundary members:** RouteZoneSequence, RoutePath, RoutePackageAssignment — zone order, path, and package hangs must stay consistent for one route
- **Protected invariants:** zones are ordered; a stop is on the route iff its zone is entered; path is calculated from zone order then shorter-path check; packages hang only on stops on the route
- **Cross-aggregate refs:** Zone (by ZoneId) — consistency: immediate; Stop (by StopId) — derived membership when zone entered; Package (by PackageId) — snapshot on assign

#### **Route** <<Aggregate Root>> <<Entity>>

*CE contracts: `.context/clean-engineering-model.md` § IRoute / Route*

- **Key domain invariants:**
  - Zones are ordered; stop membership is derived, not manually placed.
  - Path is absent until at least one zone is entered; recalculated on every zone change.
  - A package may only be assigned to a stop that is on the route.

#### **RouteZoneSequence** <<Value Object>>

- **Key domain invariant:** Ordered; immutable — replace, never mutate in place.

#### **RoutePath** <<Value Object>>

- **Key domain invariant:** Calculated from zone order then shortened when adjacent zones allow a shorter driver path; immutable — replace after each recalculation.

#### **RoutePackageAssignment** <<Value Object>>

- **Key domain invariant:** Immutable pair — replace on move or unassign.

#### **RouteRepository** <<Repository>>

*CE contracts: `.context/clean-engineering-model.md` § IRouteRepository / RouteRepository*

#### **RoutePathCalculator** <<Service>>

- **Key domain invariant:** May reorder adjacent zones when a shorter driver path exists; stateless.

#### **RoutePathRecalculated** <<Domain Event>>

- **Trigger:** `Route.recalculate_path` or any zone membership change that alters the path.
- **Consumers:** driver app, live oversee views.
- **Payload fields:** route_id: RouteId, zone_order: list[ZoneId]

---

### Zone

- **Root:** Zone
- **Boundary members:** ZoneBoundary, Stop — stops fall inside the zone boundary
- **Protected invariants:** address maps to exactly one zone; boundary contains zero or more stops
- **Cross-aggregate refs:** none required for Plan Delivery Routes spine

#### **Zone** <<Aggregate Root>> <<Entity>>

*CE contracts: `.context/clean-engineering-model.md` § IZone / Zone*

- **Key domain invariants:**
  - Boundary contains zero or more stops.
  - An address maps to exactly one stop in this zone; reuse when address already known.

#### **ZoneBoundary** <<Value Object>>

- **Key domain invariant:** Immutable — replace, never mutate in place.

#### **Stop** <<Entity>>

- **Key domain invariant:** Address maps to exactly one zone; created or reused from package recipient address at intake — never placed by a dispatcher directly.

#### **Address** <<Value Object>>

- **Key domain invariant:** Immutable — replace, never mutate in place.

#### **ZoneRepository** <<Repository>>

*CE contracts: `.context/clean-engineering-model.md` § IZoneRepository / ZoneRepository*

---

## PackageIntake

- **Owning team:** Courier ops intake
- **Scope:** Registering and importing packages; resolving recipient address to a zone stop
- **Implementation:** monolith module (`packages/`)

### Package

- **Root:** Package
- **Boundary members:** recipient Address — package identity and destination travel together at intake
- **Protected invariants:** recipient address resolves to a zone and creates or reuses a stop
- **Cross-aggregate refs:** Routing.Stop (by StopId) — consistency: immediate at register/import

#### **Package** <<Aggregate Root>> <<Entity>>

*CE contracts: `.context/clean-engineering-model.md` § IPackage / Package*

- **Key domain invariant:** On register or import, recipient address resolves to a Zone and creates or reuses a Stop — package is never address-only after intake.

#### **PackageRepository** <<Repository>>

*CE contracts: `.context/clean-engineering-model.md` § IPackageRepository / PackageRepository*

---

## Fleet

- **Owning team:** Courier fleet
- **Scope:** Drivers and vehicles available to staff routes (scaffold — Staff Routes theme not yet generated)
- **Implementation:** monolith module (`fleet/`)

### Driver

- **Root:** Driver
- **Boundary members:** identity for route assignment
- **Protected invariants:** a registered driver can be assigned to a route
- **Cross-aggregate refs:** Route (by RouteId) — consistency: eventual on dispatch

#### **Driver** <<Aggregate Root>> <<Entity>>

*(scaffold — CE contracts pending Staff Routes generation)*

---

### Vehicle

- **Root:** Vehicle
- **Boundary members:** identity for route assignment
- **Protected invariants:** a registered vehicle can be assigned to a route
- **Cross-aggregate refs:** Route (by RouteId) — consistency: eventual on dispatch

#### **Vehicle** <<Aggregate Root>> <<Entity>>

*(scaffold — CE contracts pending Staff Routes generation)*

---

## Dependencies

### PackageIntake → Routing

- **Direction:** PackageIntake upstream; Routing downstream for stop creation; Routing is customer for package identity on assign
- **What crosses:** Address into Stop creation/reuse; PackageId and StopId into route package assignment
- **How they integrate:** Synchronous call — at `Package.register` / import, PackageIntake calls `Zone.find_or_create_stop(address)`; at `Route.assign_package`, Routing stores PackageId on the route for an on-route StopId
- **Relationship pattern:** Customer/Supplier
- **Rationale:** Stops are created at intake from recipient address; routes only hang packages on stops already in entered zones

### Fleet → Routing

- **Direction:** Fleet upstream; Routing downstream
- **What crosses:** DriverId and VehicleId onto a route when staffing (Staff Routes scaffold — not yet integrated)
- **How they integrate:** Synchronous call at assign-driver / assign-vehicle on Route (scaffold)
- **Relationship pattern:** Customer/Supplier
- **Rationale:** Fleet owns driver and vehicle identity; Routing references them by id when dispatching
