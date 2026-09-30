## Story: Reserve Msisdn Resource

### Scenario: Reserve MSISDN resource as temporary port-in number

*Given* ++MSISDN++ ++available number++ ++held available number++ is locked in Mavenir inventory
*When* Mavenir is asked to reserve ++available number++ ++held available number++ with `kv_tempNumber: true` (`/updateResources`, locked → reserved, relatedParty: Paradise Mobile)
*Then* Mavenir transitions ++available number++ ++held available number++ from locked to reserved
*And* Mavenir marks ++available number++ ++held available number++ as a temporary port-in number (`kv_tempNumber`)

### Scenario: Reserve MSISDN resource

*Given* ++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory
*When* Mavenir is asked to reserve ++available number++ ++chosen available number++ (`/updateResources`, locked → reserved, relatedParty: Paradise Mobile)
*Then* Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved
*And* Mavenir attaches the Paradise Mobile service provider to ++available number++ ++chosen available number++

### Scenario: Reserve MSISDN resource — release previous

*Given* ++MSISDN++ ++available number++ ++chosen available number++ is locked
*And* ++MSISDN++ ++available number++ ++held available number++ is reserved
*When* Mavenir is asked to reserve ++available number++ ++chosen available number++ and release previous ++available number++ ++held available number++
*Then* Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved
*And* Mavenir transitions ++available number++ ++held available number++ from reserved to available
