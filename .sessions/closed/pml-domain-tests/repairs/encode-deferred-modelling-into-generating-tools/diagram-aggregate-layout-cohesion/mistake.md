# diagram-aggregate-layout-cohesion

- **entry_id:** e3f08080
- **artifact:** tests/domain/.context/domain-model.drawio
- **rule:** (diagram) aggregate-layout-cohesion
- **wrong:** Aggregate roots are not clustered with their invariants and repositories. Customer-related aggregate (Prospect) is separated from its value objects (Identity, Address, Metadata) by a large vertical gap with authentication objects inserted between them. Repositories (ProspectRepository, SubscriberRepository) are not positioned beside their aggregates as a cluster.
- **status:** fixed