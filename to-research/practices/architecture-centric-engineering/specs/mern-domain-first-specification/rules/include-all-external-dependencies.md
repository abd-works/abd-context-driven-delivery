---
scanner: dependency_declarations_scanner.py
---

# Rule: Include All External Dependencies

Every `package.json` must declare **all** external packages that its source files import. After `npm install`, the project must compile with zero unresolved module errors. This is non-negotiable — generated code that cannot compile is useless.

## Required Dependencies by Tier

| Tier | Required dependencies | Required devDependencies |
|------|----------------------|--------------------------|
| **shared/** | `zod` | — |
| **server/** | `express`, `mongodb`, workspace shared package | `@types/express` |
| **client/** | `react`, `react-dom`, workspace shared package | `@types/react`, `@types/react-dom` |
| **root** | — | `typescript`, test framework packages (see below) |

### Test Dependencies (root devDependencies)

When generating test files, the root `package.json` must include:

| Test framework | Required packages |
|---|---|
| **Server tests** | `vitest`, `jsdom` |
| **Client tests** (React component tests) | `vitest`, `jsdom`, `@testing-library/react`, `@testing-library/jest-dom` |
| **E2E tests** (Playwright) | `@playwright/test` |

**Never use `node:test` in Vitest-managed test files.** All `*_server.test.ts` and `*_client.test.tsx` files must import `describe`, `it`, `expect`, `beforeEach`, and `vi` from `'vitest'` — not `'node:test'`. Mixing test runners causes "No test suite found" failures and ESM/CJS conflicts.

### Test Runner Config Files

The project **must** include both a `vitest.config.ts` and a `playwright.config.ts` at the root to prevent each runner from picking up the other's test files:

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: {
    include: ['tests/**/*_server.test.ts', 'tests/**/*_client.test.tsx'],
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
  },
});

// playwright.config.ts
import { defineConfig } from '@playwright/test';
export default defineConfig({
  testMatch: '**/*_e2e.spec.ts',
  use: { baseURL: 'http://localhost:3000' },
});
```

Without these configs:
- Playwright picks up `*_client.test.tsx` Vitest files → ESM/CJS import error on `vitest` module
- Vitest picks up `*_e2e.spec.ts` Playwright files → "No test suite found" failure

The `tsconfig.json` must also include test type declarations:
```json
{
  "compilerOptions": {
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  },
  "include": [
    "packages/**/*.ts",
    "packages/**/*.tsx",
    "tests/**/*.ts",
    "tests/**/*.tsx"
  ]
}
```

### Test Import Paths

Test files use the same package-name-based imports as production code. The `tsconfig.json` must include path aliases for **all** tier packages (shared, server, client) so tests can resolve them:

```json
{
  "compilerOptions": {
    "paths": {
      "@appName/domain-shared": ["./packages/domain/shared/index.ts"],
      "@appName/domain-server": ["./packages/domain/server/index.ts"],
      "@appName/domain-client": ["./packages/domain/client/index.ts"],
      "@appName/domain-client/*": ["./packages/domain/client/*"]
    }
  }
}
```

The wildcard path (`@appName/domain-client/*`) is needed when test files import sub-modules (e.g., `import * as api from '@appName/domain-client/todoLists.api'`).

Add additional packages when the generated code imports them (e.g., `crypto` for Node.js UUID, `@tanstack/react-query` for data fetching).

## DO

- List every imported external module in `dependencies` or `devDependencies`.
- Include `@types/*` packages for libraries that don't ship their own type declarations.
- Use caret ranges (`^`) for version flexibility: `"zod": "^3.22.0"`.
- Include `typescript` in the root `package.json` devDependencies.
- Verify the project compiles after generation by running `npx tsc --noEmit`.
- Verify all modules resolve after `npm install` by checking for `Cannot find module` errors.

```json
// packages/{domain}/shared/package.json — CORRECT: includes zod
{
  "name": "@appName/domain-shared",
  "dependencies": {
    "zod": "^3.22.0"
  }
}

// packages/{domain}/server/package.json — CORRECT: includes express + mongodb + types
{
  "name": "@appName/domain-server",
  "dependencies": {
    "@appName/domain-shared": "*",
    "express": "^4.18.0",
    "mongodb": "^6.0.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.0"
  }
}

// packages/{domain}/client/package.json — CORRECT: includes react + types
{
  "name": "@appName/domain-client",
  "dependencies": {
    "@appName/domain-shared": "*",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0"
  }
}
```

## DON'T

- Omit external packages from `dependencies` and rely on hoisting or implicit resolution.
- Generate source files that import modules not listed in any `package.json`.
- Skip `@types/*` packages — TypeScript will report `Could not find a declaration file`.
- Use `*` or `latest` for external packages (only for workspace internal references).
- Assume any dependency is "already installed" — declare everything explicitly.

```json
// WRONG — missing zod, express, react, mongodb
{
  "name": "@appName/domain-server",
  "dependencies": {
    "@appName/domain-shared": "*"
  }
}
```

## Validation After Generation

After generating all files, the agent MUST:

1. Run `npm install` from the workspace root — must exit with code 0.
2. Run `npx tsc --noEmit` — must report zero errors.
3. If either step fails, diagnose and fix before considering implementation complete.

Compilation failures caused by missing dependencies are **blocking violations** — the generated module is not done until it compiles.
