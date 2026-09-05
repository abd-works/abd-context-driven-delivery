---
name: runnable-green-bar
---

# Runnable Green Bar

## DO

- Install all project dependencies (`npm install` or equivalent) after generating code so the project is runnable.
- Execute the full test suite (`npm test` or equivalent) after generation and confirm a passing result.
- Fix all infrastructure issues (missing packages, wrong `package.json` references, module resolution errors, JSX file extensions, test config, missing setup files) until the test runner loads and executes every suite.
- Fix assertion misalignments (wrong API paths, wrong response shapes, incorrect imports) revealed by running the tests — iterate until the bar is green.
- Confirm the dev server starts without errors if the spec includes a client or server composition root.

## DO NOT

- Do not declare work "done" when tests have never been executed.
- Do not leave `workspace:*` or other package-manager-specific protocols that the project's package manager does not support.
- Do not generate test files that import libraries not listed in `devDependencies`.
- Do not generate test helpers with `.ts` extensions when they contain JSX — use `.tsx`.
- Do not rely on the user to debug missing dependencies, port conflicts, or test setup — resolve them as part of generation.
