<!-- @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering -->

---
fidelity: [spec]
artifact: [clean_engineering]
format: md
---

**Sources / context:** `.context/sessions/courier-ops/cdd-sketch.md` (Plan Delivery Routes specification sketch); `.context/bounded-context-map.md`

## Language companion

*Route* holds an ordered sequence of zones. Every stop whose zone appears in that sequence is on the route. The route calculates a path from the zone order, then checks whether any adjacent zones allow a shorter driver path.

- **route** — Holds an ordered `RouteZoneSequence`; a stop is on the route iff its zone is in that sequence. Carries a `RoutePath`. Collects `RoutePackageAssignment` entries. Invariant: Packages may only hang on stops that are on the route.
- **zone** — Owns a geographic `ZoneBoundary` and the `Stop` entities that fall inside it. Invariant: An address maps to exactly one zone.
- **stop** — Records one delivery address; belongs to exactly one zone. Created or reused from a package's recipient address at intake — never placed by a dispatcher.
- **package** — Carries a recipient address; resolves to a zone stop on registration.
- **route_path_calculator** — Computes a `RoutePath` from an ordered zone list; applies a shorter-path check — may reorder adjacent zones when a shorter driver path exists.

## Modules

Build order: `zones` → `packages` → `routes`

---

# routes

- **Purpose:** Manages delivery routes — zone sequence, derived stop membership, path calculation, and package-on-stop assignments.
- **Seam (terms):** Route, RouteZoneSequence, RoutePath, RoutePackageAssignment, RouteRepository, RoutePathCalculator, RoutePathRecalculated
- **Dependencies (one-way):** zones, packages

## IRoute

IRoute()
------
id: RouteId
zone_sequence: IRouteZoneSequence
path: IRoutePath | None
	Invariant: Absent until at least one zone is entered.
package_assignments: list[IRoutePackageAssignment]
----
add_zone(zone: ZoneId): None
	Invariant: Zone appended to sequence; path recalculates.
remove_zone(zone: ZoneId): None
	Invariant: Stops in only the removed zone leave the route; path recalculates.
reorder_zones(zones: list[ZoneId]): None
	Invariant: New order becomes the sequence; path recalculates.
recalculate_path(): None
	Invariant: Path and zone order may both change when a shorter adjacent sequence exists.
stops_on_route(zones: IZoneRepository): list[StopId]
	Invariant: Returns only stops whose zone is in zone_sequence.
assign_package(package: PackageId, stop: StopId): None
	Invariant: Stop must be on the route; package hangs on that stop.
unassign_package(package: PackageId, stop: StopId): None
move_package(package: PackageId, to_stop: StopId): None
	Invariant: Destination stop must be on the route.

## Route

+ Route()
------
+ << identifier >> id: RouteId
+ << composition >> zone_sequence: RouteZoneSequence
+ << composition >> path: RoutePath | None
	Invariant: Absent until at least one zone is entered; recalculated after every zone change.
+ << composition >> package_assignments: list[RoutePackageAssignment]
----
+ add_zone(zone: ZoneId): None
	Invariant: Zone appended to sequence; path recalculates.
	Interaction:
		zone_sequence = zone_sequence.with_zone_appended(zone)
		path = RoutePathCalculator().calculate(zone_sequence.zones)
+ remove_zone(zone: ZoneId): None
	Invariant: Stops that fall only in the removed zone leave the route; path recalculates.
	Interaction:
		zone_sequence = zone_sequence.with_zone_removed(zone)
		path = RoutePathCalculator().calculate(zone_sequence.zones)
+ reorder_zones(zones: list[ZoneId]): None
	Invariant: New zone order becomes the sequence; path recalculates.
	Interaction:
		zone_sequence = zone_sequence.reordered(zones)
		path = RoutePathCalculator().calculate(zone_sequence.zones)
+ recalculate_path(): None
	Invariant: Path and zone order may both change when a shorter adjacent sequence exists.
	Interaction:
		path = RoutePathCalculator().shorten(zone_sequence.zones)
+ stops_on_route(zones: IZoneRepository): list[StopId]
	Invariant: Returns only stops whose zone is in zone_sequence.
+ assign_package(package: PackageId, stop: StopId): None
	Invariant: Stop must be on the route; package hangs on that stop.
+ unassign_package(package: PackageId, stop: StopId): None
+ move_package(package: PackageId, to_stop: StopId): None
	Invariant: Destination stop must be on the route.

## IRouteZoneSequence

IRouteZoneSequence(zones: list[ZoneId])
------
zones: list[ZoneId]
	Invariant: Ordered; immutable — replace, do not mutate in place.
----
with_zone_appended(zone: ZoneId): IRouteZoneSequence
with_zone_removed(zone: ZoneId): IRouteZoneSequence
reordered(zones: list[ZoneId]): IRouteZoneSequence

## RouteZoneSequence

+ RouteZoneSequence(zones: list[ZoneId])
------
+ zones: list[ZoneId]
	Invariant: Ordered; immutable — replace, do not mutate in place.
----
+ with_zone_appended(zone: ZoneId): RouteZoneSequence
+ with_zone_removed(zone: ZoneId): RouteZoneSequence
+ reordered(zones: list[ZoneId]): RouteZoneSequence

## IRoutePath

IRoutePath(zone_order: list[ZoneId])
------
zone_order: list[ZoneId]
	Invariant: Immutable — replace after calculate or shorten.
----

## RoutePath

+ RoutePath(zone_order: list[ZoneId])
------
+ zone_order: list[ZoneId]
	Invariant: Immutable — replace after calculate or shorten.
----

## IRoutePackageAssignment

IRoutePackageAssignment(package: PackageId, stop: StopId)
------
package: PackageId
stop: StopId
	Invariant: Immutable — replace on move or unassign.
----

## RoutePackageAssignment

+ RoutePackageAssignment(package: PackageId, stop: StopId)
------
+ package: PackageId
+ stop: StopId
	Invariant: Immutable — replace on move or unassign.
----

## IRouteRepository

IRouteRepository()
------
----
add(route: IRoute): None
remove(route: IRoute): None
update(route: IRoute): None
find_by_id(id: RouteId): IRoute | None

## RouteRepository

+ RouteRepository()
------
----
+ add(route: IRoute): None
+ remove(route: IRoute): None
+ update(route: IRoute): None
+ find_by_id(id: RouteId): IRoute | None

## IRoutePathCalculator

IRoutePathCalculator()
------
----
calculate(zones: list[ZoneId]): IRoutePath
shorten(zones: list[ZoneId]): IRoutePath
	Invariant: May reorder adjacent zones when a shorter driver path exists.

## RoutePathCalculator

+ RoutePathCalculator()
------
----
+ calculate(zones: list[ZoneId]): RoutePath
	Invariant: Derives path from the zone order as supplied.
+ shorten(zones: list[ZoneId]): RoutePath
	Invariant: May reorder adjacent zones when a shorter driver path exists; returns the shortened path.

## RoutePathRecalculated

RoutePathRecalculated(route_id: RouteId, zone_order: list[ZoneId])
------
route_id: RouteId
zone_order: list[ZoneId]
	Invariant: Raised after recalculate_path or any zone membership change alters the path.
	Invariant: Consumers are driver app and live oversee views.
----

---

# zones

- **Purpose:** Owns zones (name, boundary) and the stops that fall inside each zone; provides stop lookup and creation from an address.
- **Seam (terms):** Zone, ZoneBoundary, Stop, Address, ZoneRepository
- **Dependencies (one-way):** *(none)*

## IZone

IZone(name: str, boundary: IZoneBoundary)
------
id: ZoneId
name: str
boundary: IZoneBoundary
stops: list[IStop]
	Invariant: Boundary contains zero or more stops.
----
contains_address(address: IAddress): bool
define_boundary(boundary: IZoneBoundary): None
edit_boundary(boundary: IZoneBoundary): None
find_or_create_stop(address: IAddress): IStop
	Invariant: Address maps to exactly one stop in this zone; reuse when address already known.

## Zone

+ Zone(name: str, boundary: IZoneBoundary)
------
+ << identifier >> id: ZoneId
+ name: str
+ << composition >> boundary: ZoneBoundary
+ << composition >> stops: list[Stop]
	Invariant: Boundary contains zero or more stops.
----
+ contains_address(address: IAddress): bool
+ define_boundary(boundary: IZoneBoundary): None
+ edit_boundary(boundary: IZoneBoundary): None
+ find_or_create_stop(address: IAddress): Stop
	Invariant: Address maps to exactly one stop in this zone; reuse when address already known.

## IZoneBoundary

IZoneBoundary(geometry: str)
------
geometry: str
	Invariant: Immutable — replace, do not mutate.
----

## ZoneBoundary

+ ZoneBoundary(geometry: str)
------
+ geometry: str
	Invariant: Immutable — replace, do not mutate.
----

## IStop

IStop(address: IAddress, zone: ZoneId)
------
id: StopId
address: IAddress
zone: ZoneId
	Invariant: Address maps to exactly one zone; created or reused from package recipient address at intake.
----

## Stop

+ Stop(address: IAddress, zone: ZoneId)
------
+ << identifier >> id: StopId
+ << composition >> address: Address
+ << association >> zone: ZoneId
	Invariant: Address maps to exactly one zone; created or reused from package recipient address at intake.
----

## IAddress

IAddress(line: str)
------
line: str
	Invariant: Immutable — replace, do not mutate.
----

## Address

+ Address(line: str)
------
+ line: str
	Invariant: Immutable — replace, do not mutate.
----

## IZoneRepository

IZoneRepository()
------
----
add(zone: IZone): None
remove(zone: IZone): None
update(zone: IZone): None
find_by_id(id: ZoneId): IZone | None
find_zone_for_address(address: IAddress): IZone | None

## ZoneRepository

+ ZoneRepository()
------
----
+ add(zone: IZone): None
+ remove(zone: IZone): None
+ update(zone: IZone): None
+ find_by_id(id: ZoneId): IZone | None
+ find_zone_for_address(address: IAddress): IZone | None

---

# packages

- **Purpose:** Registers and imports packages; resolves recipient address to a stop on intake.
- **Seam (terms):** Package, PackageRepository
- **Dependencies (one-way):** zones

## IPackage

IPackage(label: str, recipient: IAddress)
------
id: PackageId
label: str
recipient: IAddress
stop: StopId | None
	Invariant: On register or import, recipient address resolves to a Zone and creates or reuses a Stop.
----
register(zones: IZoneRepository): None
import_batch_row(zones: IZoneRepository): None

## Package

+ Package(label: str, recipient: IAddress)
------
+ << identifier >> id: PackageId
+ label: str
+ << composition >> recipient: Address
+ << association >> stop: StopId | None
	Invariant: On register or import, recipient address resolves to a Zone and creates or reuses a Stop.
----
+ register(zones: IZoneRepository): None
	Invariant: Sets stop via zones.find_zone_for_address(recipient).find_or_create_stop(recipient).
	Interaction:
		zone: IZone = zones.find_zone_for_address(recipient)
		stop = zone.find_or_create_stop(recipient)
+ import_batch_row(zones: IZoneRepository): None
	Invariant: Same stop resolution as register.

## IPackageRepository

IPackageRepository()
------
----
add(package: IPackage): None
remove(package: IPackage): None
update(package: IPackage): None
find_by_id(id: PackageId): IPackage | None

## PackageRepository

+ PackageRepository()
------
----
+ add(package: IPackage): None
+ remove(package: IPackage): None
+ update(package: IPackage): None
+ find_by_id(id: PackageId): IPackage | None
