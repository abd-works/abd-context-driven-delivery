## Story: List Msisdn Resources

### Scenario: List MSISDN resources for porting

*Given* ++MSISDN++ resources with available status are in the Mavenir inventory
*When* Mavenir is asked to list 1 ++MSISDN++ resource (`/updateAndGetAvailableResources`, `size: 1`)
*Then* Mavenir transitions 1 ++MSISDN++ resource from available to locked
*And* Mavenir returns ++available number++ ++held available number++ as the locked resource to Midtier

### Scenario: List MSISDN resources

*Given* ++MSISDN++ resources with available status are in the Mavenir inventory
*When* Mavenir is asked to list ++MSISDN++ resources (`/updateAndGetAvailableResources`, `size: 5`)
*Then* Mavenir transitions 5 ++MSISDN++ resources from available to locked
*And* Mavenir returns the list of locked ++available number++ values to Midtier
