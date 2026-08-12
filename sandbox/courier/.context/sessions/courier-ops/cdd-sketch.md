fidelity: spec
scope: entire courier ops solution — drivers, vehicles, packages, routes
# Plan Delivery Routes deepened to specification sketch; sibling themes remain discovery scaffold

flow:
  status: complete
  recommend: next-stage
  next: advance to engineer — acceptance tests, implementation
  note: All specification artifacts generated for Plan Delivery Routes.
  open: []
  done:
    - pass #specification-sketch-deepen
    - pass #gen-stories scenarios for Plan Delivery Routes
    - pass #gen-ddd building_blocks bounded-context-map
    - pass #gen-ux information-architecture mockup
    - pass #gen-ce clean-engineering-model spec
    - pass #gen-bdd bdd-behavior behavior

# Locked decisions
# - surfaces: dispatcher app + driver app (co-equal)
# - work model: route enters ordered zones; packages hang on stops
# - intake: ops/clerk registers packages (no customer self-serve booking)
# - stop origin: register/import package creates or reuses Stop at recipient address inside a Zone
# - stop-on-route: a stop is on a route iff it falls into a zone that the route enters
# - zone order: ordered sequence; path calculated from zone order then checked/optimized for shorter driver path (adjacent zones may make naive order suboptimal); dispatcher may reorder when it shortens the path
# - retracted: stop-first manual place-stop-on-route

=========
theme: Register Packages  (epic)
---------
stories:
    Register Packages                         < scaffold
        Capture Package Details               < scaffold
            Clerk --> Register Incoming Package  < scaffold
            * approx 2-3 more stories (label, weight/size, recipient address)  < scaffold
        Import Warehouse Package List         < scaffold
            Clerk --> Import Package Batch    < scaffold
            * approx 1-2 more stories (validate rows, fix rejects)  < scaffold
---
ddd:
    PackageIntake                             < scaffold
      aggregates: Package                    < scaffold
---
ux:
    Dispatcher Home                           < scaffold
      └─ [nav] Packages ──────────→ Package List  < scaffold
    Package List                              < scaffold
      ├─ [action] Register package ─→ Register Package  < scaffold
      └─ [action] Import batch ─────→ Import Packages  < scaffold
---
ce:
    packages/                                 < scaffold
=========

=========
theme: Plan Delivery Routes  (epic)
---------
stories:
    Plan Delivery Routes
        * approx 11-13 total stories
        Build Route By Zones
            Dispatcher --> Create Delivery Route
                route created empty ready for zones
                    given a Dispatcher
                    when the Dispatcher creates a Delivery Route
                    then a Route exists with no zones and no path
            Dispatcher --> Add Zone To Route
                zone added recalculates path from order then shorter check
                    given a Route with ordered Zones North, East
                        and Zone West adjacent to Zone North
                        and Stops in West from prior package intake
                    when the Dispatcher adds Zone West to the Route
                    then Route.zones include West in order
                        and Stops that fall in West appear on the Route
                        and Route.path is calculated from zone order then shorter-path check
            Dispatcher --> Remove Zone From Route
                removing zone drops its stops from the route
                    given a Route that enters Zones North, West
                        and Stop Dock-9 falls in West
                    when the Dispatcher removes Zone West
                    then West is not on the Route
                        and Dock-9 is not on the Route
                        and Route.path is recalculated
            Dispatcher --> Reorder Route Zones
                reorder kept when it shortens driver path
                    given a Route with Zones North, East, West
                        and a shorter path exists as North, West, East
                    when the Dispatcher reorders zones to North, West, East
                    then Route.zones order is North, West, East
                        and Route.path matches the shorter sequence
            Dispatcher --> Recalculate Route Path
                adjacent zones trigger shorter-path improvement
                    given a Route with zone order East, North, West
                        and North is adjacent to West such that North, West, East is shorter
                    when the Dispatcher recalculates the Route path
                    then Route.path uses the shorter zone sequence
                        and Route.zones order reflects that sequence
            Dispatcher --> View Stops On Route
                stops listed are only those in entered zones
                    given a Route that enters Zone North
                        and Stop A falls in North
                        and Stop B falls in East
                    when the Dispatcher views stops on the Route
                    then Stop A is listed
                        and Stop B is not listed
            * approx 1-2 more stories (define / edit zone boundary)
        Attach Packages To Stops
            Dispatcher --> Assign Package To Stop
                package hangs only on a stop already on the route
                    given a Route that enters Zone North
                        and Stop Dock-9 falls in North (on the Route)
                        and Package P-100 at Dock-9 is unassigned
                    when the Dispatcher assigns Package P-100 to Stop Dock-9
                    then Package P-100 is hung on Dock-9 for that Route
            Dispatcher --> Unassign Package From Stop
            Dispatcher --> Move Package Between Stops
                move only between stops on the same route
                    given Package P-100 on Stop Dock-9 on the Route
                        and Stop Dock-12 also on the Route
                    when the Dispatcher moves P-100 to Dock-12
                    then P-100 hangs on Dock-12
                        and Dock-9 no longer holds P-100 for that Route
            * approx 1 more story (list packages for stops on this route)
    ~> Increment 1: Create Delivery Route, Add Zone To Route, Recalculate Route Path, Assign Package To Stop
---
ddd:
    Routing
      Route <<Aggregate Root>> <<Entity>>
        invariants: zones are ordered; stop on route iff stop.zone is entered; path from zone order then shorter-path check
        members: RouteZoneSequence <<Value Object>>; RoutePath <<Value Object>>
        cross-agg:
          → Zone (by ZoneId) — immediate — entered zones
          → Stop (by StopId) — derived — stops whose zone is entered
        repo: RouteRepository
        events: RoutePathRecalculated — consumers: driver app / live oversee
      Zone <<Aggregate Root>> <<Entity>>
        invariants: boundary contains zero or more stops
        members: ZoneBoundary <<Value Object>>; name
        repo: ZoneRepository
      Stop <<Entity>>
        invariants: address maps to exactly one Zone; created/reused from Package recipient address
        members: Address <<Value Object>>; ZoneId
        // owned/resolved under Routing; created at package intake time
    PackageIntake
      Package <<Aggregate Root>>
        invariants: recipient address resolves to a Zone and creates or reuses Stop
        cross-bc:
          → Routing.Stop via Address — on register/import
    PackageIntake → Routing
      direction: upstream / downstream
      crosses: Package, Address, StopId
      integrate: register/import Package creates/reuses Stop; Assign Package To Stop
      pattern: Customer/Supplier
    architecture: default domain modules + app services
      repos: RouteRepository, ZoneRepository → persistence
      events: RoutePathRecalculated → publish for live views
      sync across BC: StopId, PackageId via Assign Package To Stop
---
ux:
    Fidelity: mockup | specification
    Dispatcher Home
      ├─ [nav] Routes ────────────→ Route List
      └─ [nav] Zones ─────────────→ Zone List
    Route List
      ├─ [action] Create route ───→ Route Planner
      └─ [action] Open route ─────→ Route Planner

    [ Route Planner ]                              split-screen
      ┌──────────────┬─────────────────────────────┐
      │ Zones (order)│ Path + stops on route       │
      │ 1 ›North‹    │ path: North → West → East   │
      │ 2  West      │ (optimized from adjacency)  │
      │ 3  East      │                             │
      │ [ + Zone ]   │ Stops                       │
      │ [ ↑ ][ ↓ ]   │ ›Dock-9‹  2 pkgs            │
      │ [ Recalc ]   │  Dock-12  0 pkgs            │
      │ [ Remove ]   │ [ Open stop ]               │
      └──────────────┴─────────────────────────────┘
      Stories (~4): Add Zone To Route · Reorder Route Zones · Recalculate Route Path · View Stops On Route
      Domain terms: Zone order, Route path, Stop on route
      key:
        ›sel‹ selected · [ btn ] · path line = calculated then shortened
        on [ Recalc ] → same screen, path/zone order may change
        on [ Open stop ] → Stop Packages

    [ Stop Packages ]                              list
      ┌────────────────────────────────────────────┐
      │ Stop Dock-9  (Zone North)                  │
      │ Packages on stop                           │
      │  P-100  Acme · 12 Oak St                   │
      │  P-101  Beta · 12 Oak St                   │
      │ Unassigned in zone                         │
      │  P-108  …                                  │
      │ [ Assign ] [ Unassign ] [ Move ]           │
      └────────────────────────────────────────────┘
      Stories (~3): Assign Package To Stop · Unassign · Move Package Between Stops
      Domain terms: Package, Stop, Zone
      key: on [ Assign ] → package hangs on this stop for the route
---
ce:
    routes/
      Route
        zones                    // ordered ZoneIds
        path                     // calculated then optimized
        create
        add_zone zone
        remove_zone zone
        reorder_zones zones
        recalculate_path
        stops_on_route           // derived via zones
        assign_package package stop
        unassign_package package stop
        move_package package to_stop
      RoutePathCalculator
        calculate zones
        shorten zones            // adjacent-zone shorter path check
    zones/
      Zone
        name
        boundary
        contains_address address
      Stop
        address
        zone
        // created/reused when Package is registered
    routes/ -> zones/
    routes/ -> packages/
---
bdd:
    a delivery route
      that has ordered zones
        with an adjacent zone that shortens the path
          it should recalculate to the shorter zone sequence
        with stops only in entered zones
          it should list those stops and omit stops in other zones
      that has a stop on the route
        with an unassigned package at that stop address
          it should allow assigning the package to that stop
        with a package hung on one on-route stop
          it should allow moving it only to another on-route stop
    a package at intake
      that is registered with a recipient address
        with the address falling in an existing zone
          it should create or reuse a stop in that zone
=========

=========
theme: Staff Routes  (epic)
---------
stories:
    Staff Routes                              < scaffold
        Assign Driver And Vehicle             < scaffold
            Dispatcher --> Assign Driver To Route  < scaffold
            Dispatcher --> Assign Vehicle To Route  < scaffold
            * approx 1-2 more stories (reassign, clear assignment)  < scaffold
        Release Route To Driver               < scaffold
            Dispatcher --> Dispatch Route     < scaffold
            * approx 1 more story (recall dispatched route)  < scaffold
---
ddd:
    Routing                                   < scaffold
      aggregates: Route                      < scaffold
    Fleet → Routing                           < scaffold
      direction: upstream / downstream        < scaffold
      crosses: Driver, Vehicle                < scaffold
      pattern: Customer/Supplier              < scaffold
---
ux:
    Route Planner                             < scaffold
      ├─ [action] Assign driver ──→ Route Planner  < scaffold
      ├─ [action] Assign vehicle ─→ Route Planner  < scaffold
      └─ [action] Dispatch ───────→ Route List  < scaffold
---
ce:
    routes/                                   < scaffold
    routes/ -> fleet/                         < scaffold
=========

=========
theme: Run Delivery Route  (epic)
---------
stories:
    Run Delivery Route                        < scaffold
        Start And Follow Route                < scaffold
            Driver --> Start Assigned Route   < scaffold
            Driver --> Navigate To Next Stop  < scaffold
            * approx 1-2 more stories (skip stop, view stop packages)  < scaffold
        Complete Stop Deliveries              < scaffold
            Driver --> Mark Package Delivered  < scaffold
            Driver --> Mark Package Failed    < scaffold
            * approx 1-2 more stories (partial stop, finish route)  < scaffold
---
ddd:
    Routing                                   < scaffold
      aggregates: Route                      < scaffold
---
ux:
    Driver Home                               < scaffold
      └─ [nav] My Route ──────────→ Active Route  < scaffold
    Active Route                              < scaffold
      └─ [action] Open stop ──────→ Stop Detail  < scaffold
    Stop Detail                               < scaffold
      ├─ [action] Mark delivered ─→ Stop Detail  < scaffold
      └─ [action] Mark failed ────→ Stop Detail  < scaffold
---
ce:
    routes/                                   < scaffold
=========

=========
theme: Oversee Deliveries  (epic)
---------
stories:
    Oversee Deliveries                        < scaffold
        Watch Live Route Progress             < scaffold
            Dispatcher --> View Live Routes   < scaffold
            Dispatcher --> Inspect Route Progress  < scaffold
            * approx 1-2 more stories (filter by status, open driver route)  < scaffold
---
ddd:
    Routing                                   < scaffold
      aggregates: Route                      < scaffold
---
ux:
    Dispatcher Home                           < scaffold
      └─ [nav] Live Routes ───────→ Live Routes  < scaffold
    Live Routes                               < scaffold
      └─ [action] Open route ─────→ Route Progress  < scaffold
---
ce:
    routes/                                   < scaffold
=========

=========
theme: Maintain Fleet  (epic)
---------
stories:
    Maintain Fleet                            < scaffold
        Manage Drivers                        < scaffold
            FleetManager --> Register Driver  < scaffold
            * approx 2-3 more stories (update driver, deactivate driver)  < scaffold
        Manage Vehicles                       < scaffold
            FleetManager --> Register Vehicle  < scaffold
            * approx 2-3 more stories (update vehicle, retire vehicle)  < scaffold
---
ddd:
    Fleet                                     < scaffold
      aggregates: Driver, Vehicle             < scaffold
---
ux:
    Dispatcher Home                           < scaffold
      └─ [nav] Fleet ─────────────→ Fleet Home  < scaffold
    Fleet Home                                < scaffold
      ├─ [nav] Drivers ───────────→ Driver List  < scaffold
      └─ [nav] Vehicles ──────────→ Vehicle List  < scaffold
    Driver List                               < scaffold
      └─ [action] Register driver → Register Driver  < scaffold
    Vehicle List                              < scaffold
      └─ [action] Register vehicle → Register Vehicle  < scaffold
---
ce:
    fleet/                                    < scaffold
      drivers                                 < scaffold
      vehicles                                < scaffold
=========

## log
- discovery / solution / scaffold / pass #scaffold-whole-design
- discovery / solution / Plan Delivery Routes / pass #stop-first-mechanic
- discovery / solution / Plan Delivery Routes / pass #zone-enters-stop-derived
- discovery / solution / Plan Delivery Routes / pass #zone-order-then-optimize-path
- spec / Plan Delivery Routes / pass #stop-from-package-address
- spec / Plan Delivery Routes / pass #specification-sketch-deepen
- spec / generate / pass #gen-stories
- spec / generate / pass #gen-ddd
- spec / generate / pass #gen-ux
- spec / generate / pass #gen-ce
- spec / generate / pass #gen-bdd
