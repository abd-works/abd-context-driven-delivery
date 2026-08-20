# when-adding-an-env-var-driven-toggle-to-playwright-test-infr

- **entry_id:** 8e544d0c
- **artifact:** pml-my/tests/domain/browser-session/browser-session.e2e.ts
- **rule:** when adding an env-var-driven toggle to Playwright test infra, check first whether Playwright itself already reserves that variable name (e.g. PWDEBUG, DEBUG, PWTEST_*) before reusing it for a custom flag
- **wrong:** Named the custom headed/slowMo toggle PWDEBUG without checking that Playwright itself already reserves that exact env var name. Setting PWDEBUG=500 didn't just flip headless/slowMo as intended -- Playwright's own runtime detected it and auto-opened the Inspector, pausing execution at the first action waiting for a manual "resume" click. This silently manifested as the beforeAll hook (which runs the story's given/when steps) timing out after the full 60s hookTimeout, with no direct error pointing at the real cause -- it looked like a generic hang/timeout, not an env-var name collision. Root cause was only found by recognizing PWDEBUG as a Playwright-reserved name. Renamed the toggle to WATCH to fix.
- **status:** open
