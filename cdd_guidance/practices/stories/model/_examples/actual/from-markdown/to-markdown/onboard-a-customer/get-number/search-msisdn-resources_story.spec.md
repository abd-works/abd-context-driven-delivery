## Story: Search Msisdn Resources

### Scenario: Search MSISDN resources by pattern

*Given* ++MSISDN++ resources with available status are in the Mavenir inventory
*When* Mavenir is asked to search ++MSISDN++ resources with `pattern_search: 52637` (`/updateAndGetAvailableResources`)
*Then* Mavenir transitions matching ++MSISDN++ resources from available to locked
*And* Mavenir returns the matching ++available number++ values to Midtier
