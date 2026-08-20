# tier-agnostic-test-entry-point

- **entry_id:** 6fb56a15
- **artifact:** tests/onboard-a-customer/sign-up-select-plan.e2e.ts (and all story files)
- **rule:** tier-agnostic-test-entry-point — story files must not import from browser-session, Domain wiring class, or any implementation-tier type; all domain objects come off a single tier-agnostic factory (ParadiseMobile)
- **wrong:** describe('tier: e2e') wrapper, sandbox = await openSandbox(), domain = new Domain(sandbox) used directly in story files; imports from browser-session.e2e and domain/index exposed the e2e tier to story logic
- **status:** open
