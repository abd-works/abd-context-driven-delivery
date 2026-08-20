# use-explicit-dependencies

- **entry_id:** c8e14a02
- **artifact:** tests/domain/prospect/prospect.ts, tests/onboard-a-customer/*.e2e.ts
- **rule:** use-explicit-dependencies — a repository load must receive the identity reference already in hand; never load an aggregate from ambient session state
- **wrong:** prospectRepository.load() with no arguments after register/verify — an orphaned load that only works because the browser session secretly knows who is logged in
- **status:** open
