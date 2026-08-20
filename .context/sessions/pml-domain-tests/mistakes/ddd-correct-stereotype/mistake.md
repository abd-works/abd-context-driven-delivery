# ddd-correct-stereotype

- **entry_id:** 2e50418c
- **artifact:** tests/domain/.context/domain-model.drawio
- **rule:** (ddd) correct-stereotype
- **wrong:** Catalog is stereotyped as <<Domain Service>> but it is a root aggregate AND entity. It holds Plan collection state, exposes catalogue selection behaviour, and is the aggregate boundary for the Plan BC. It should be <<Aggregate Root>> <<Entity>>.
- **status:** open
