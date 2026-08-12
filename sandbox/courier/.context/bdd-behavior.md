---
fidelity: [behavior]
artifact: [bdd]
format: md
---

# BDD — Courier Ops: Plan Delivery Routes

**Sources / context:** `.context/sessions/courier-ops/cdd-sketch.md` (Plan Delivery Routes specification sketch); `.context/bounded-context-map.md`

---

Fidelity: behavior

a delivery route
  -> route = new Route()

  that has zones added in sequence
    it should hold the zones in the order they were added
      -> expect(route.zone_sequence.zones).to equal [North, West, East]

  that recalculates its path from zone order
    it should derive a path matching the zone sequence
      -> expect(route.path.zone_order).to equal route.zone_sequence.zones

  that has adjacent zones where a shorter path exists
    with North–West adjacent allowing North → West → East to beat North → East → West
      it should recalculate to the shorter zone sequence
        -> route.recalculate_path()
        -> expect(route.path.zone_order).to equal [North, West, East]
        -> expect(route.zone_sequence.zones).to equal [North, West, East]

  that has stops only in entered zones
    with Stop A in Zone North (entered) and Stop B in Zone South (not entered)
      it should list Stop A and omit Stop B
        -> expect(route.stops_on_route(zones)).to include(stop_a)
        -> expect(route.stops_on_route(zones)).not_to include(stop_b)

  that has a zone removed
    with stops falling only in the removed zone
      it should drop those stops from the route
        -> route.remove_zone(West)
        -> expect(route.stops_on_route(zones)).not_to include(dock_9)
      it should recalculate the path without the removed zone
        -> expect(route.path.zone_order).not_to include(West)

  that has zones reordered by the dispatcher
    with the new order creating a shorter path
      it should accept the reorder and recalculate the path
        -> route.reorder_zones([North, West, East])
        -> expect(route.zone_sequence.zones).to equal [North, West, East]

  that has a stop on the route
    with an unassigned package at that stop's address
      it should allow assigning the package to that stop
        -> route.assign_package(package_id, stop_id)
        -> expect(route.package_assignments).to include(assignment_for(package_id, stop_id))

    with a package hung on one on-route stop
      it should allow moving it only to another on-route stop
        -> route.move_package(package_id, to_stop: dock_12)
        -> expect(route.package_assignments).to include(assignment_for(package_id, dock_12))
        -> expect(route.package_assignments).not_to include(assignment_for(package_id, dock_9))

    with a package assigned to a stop
      it should allow unassigning the package from that stop
        -> route.unassign_package(package_id, stop_id)
        -> expect(route.package_assignments).not_to include(assignment_for(package_id, stop_id))

a zone
  -> zone = new Zone(name: "North", boundary: north_boundary)

  that contains an address falling inside its boundary
    it should report the address as within the zone
      -> expect(zone.contains_address(oak_st_address)).to be true

  that receives a new package recipient address
    with no existing stop at that address
      it should create a new stop for the address
        -> stop = zone.find_or_create_stop(oak_st_address)
        -> expect(stop.address).to equal oak_st_address
        -> expect(stop.zone).to equal zone.id

    with an existing stop at that address
      it should reuse the existing stop
        -> stop_a = zone.find_or_create_stop(oak_st_address)
        -> stop_b = zone.find_or_create_stop(oak_st_address)
        -> expect(stop_a.id).to equal stop_b.id

a package at intake
  -> package = new Package(label: "P-100", recipient: oak_st_address)

  that is registered with a recipient address falling in a known zone
    it should resolve the zone and create or reuse a stop
      -> package.register(zones)
      -> expect(package.stop).not_to be nil

  that is registered with a recipient address matching an existing stop
    it should reuse that stop (not create a duplicate)
      -> package_a.register(zones)
      -> package_b.register(zones)   // same address
      -> expect(package_a.stop).to equal package_b.stop

a route path calculator
  -> calculator = new RoutePathCalculator()

  that calculates a path from an ordered zone list
    it should return a path whose zone order matches the input
      -> path = calculator.calculate([North, East, West])
      -> expect(path.zone_order).to equal [North, East, West]

  that shortens a path when adjacent zones allow a better sequence
    with North adjacent to West such that [North, West, East] beats [North, East, West]
      it should return the shorter zone order
        -> path = calculator.shorten([North, East, West])
        -> expect(path.zone_order).to equal [North, West, East]
