## Story: Sweep Stale Number Reservations

### Scenario: Sweep stale number reservations

*Given* ++MSISDN++ resources have been reserved but have no active order
*And* Care observes mass Reserved ++MSISDN++ resources in the Mavenir DEP Resource Inventory
*When* Care sweeps stale ++MSISDN++ reservations
*Then* Mavenir transitions the stale ++MSISDN++ resources from reserved to available
*And* the released ++MSISDN++ resources are visible as available in the Mavenir DEP Resource Inventory
