## Story: Submit Reserve Msisdn

### Scenario: Reserve temporary MSISDN for porting

*Given* ++MSISDN++ ++available number++ ++held available number++ is locked
*When* Midtier reserves ++available number++ ++held available number++ as a port-in temporary number (`portin: true`)
*Then* Midtier reserves ++available number++ ++held available number++ in Mavenir with the port-in flag
*And* Midtier returns 204

### Scenario: Reserve MSISDN

*Given* ++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory
*When* Midtier is asked to reserve ++MSISDN++ ++available number++ ++chosen available number++
*Then* Midtier reserves ++available number++ ++chosen available number++ in Mavenir
*And* Midtier returns 204 to My Paradise

### Scenario: Reserve MSISDN — release previous

*Given* ++MSISDN++ ++available number++ ++chosen available number++ is locked
*And* ++MSISDN++ ++available number++ ++held available number++ is reserved
*When* Midtier is asked to reserve ++available number++ ++chosen available number++ releasing previous ++available number++ ++held available number++
*Then* Midtier reserves ++available number++ ++chosen available number++ and releases ++available number++ ++held available number++ in Mavenir
*And* Midtier returns 204 to My Paradise
