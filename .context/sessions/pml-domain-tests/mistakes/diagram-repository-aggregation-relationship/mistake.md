# diagram-repository-aggregation-relationship

- **entry_id:** 299843ab
- **artifact:** tests/domain/.context/domain-model.drawio
- **rule:** (diagram) repository-aggregation-relationship
- **wrong:** Repositories (ProspectRepository, SubscriberRepository, PlanRepository, etc.) have no aggregation relationship arrow to their aggregate. The definition of a repository is that it acts as a collection — this should be shown with an aggregation (diamond) connector. Most repositories also lack stereotype labels <<Repository>>.
- **status:** open
