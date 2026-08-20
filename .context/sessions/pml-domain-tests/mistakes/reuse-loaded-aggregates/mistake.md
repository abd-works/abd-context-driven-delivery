# reuse-loaded-aggregates

- **entry_id:** 042495a0
- **artifact:** tests/onboard-a-customer/*.e2e.ts
- **rule:** reuse-loaded-aggregates — load an aggregate once at the highest given that first needs it and reuse that variable; do not call repository.load in every subsequent given/when/then to reach the same object
- **wrong:** After adding explicit credentials to prospectRepository.load(), stories still called load(accountCredentials) in almost every given/when/then to re-obtain the same prospect, instead of loading once in the background given and reusing `let prospect`
- **status:** open
