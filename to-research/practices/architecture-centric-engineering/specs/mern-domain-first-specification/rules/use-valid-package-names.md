---
scanner: package_names_scanner.py
---

# Rule: Use Valid Package Names

Package names in `package.json` must be valid npm package names that pass `npm install` without errors. Derive the scope name from the **application's purpose** — not from generic placeholders.

## Naming Pattern

npm scoped packages allow exactly **one** slash: `@scope/package-name`. For a domain-first monorepo with tier subfolders, flatten the path into the package name using hyphens:

```
@{app-name}/{domain}-{tier}
```

Where:
- `{app-name}` is derived from the application's purpose (e.g., `taskflow`, `payhub`, `channelone`)
- `{domain}` is the domain module name (e.g., `recipients`, `todo-lists`, `payments`)
- `{tier}` is `shared`, `server`, or `client`

## DO

- Derive the app scope name from the application's business purpose: `@taskflow`, `@payhub`, `@shopfront`.
- Use the pattern `@{app-name}/{domain}-{tier}` for tier packages.
- Ensure every `package.json` name passes `npm install` without `EINVALIDPACKAGENAME`.
- Keep names lowercase, URL-friendly (alphanumeric, hyphens, dots only after scope).
- Use the same scope across all packages in the monorepo for consistent imports.

```json
// packages/todo-lists/shared/package.json — CORRECT
{
  "name": "@taskflow/todo-lists-shared",
  "version": "0.0.0",
  "private": true,
  "main": "index.ts",
  "types": "index.ts"
}

// packages/todo-lists/server/package.json — CORRECT
{
  "name": "@taskflow/todo-lists-server",
  "dependencies": {
    "@taskflow/todo-lists-shared": "*"
  }
}
```

```typescript
// Import using the valid package name
import { TodoList } from '@taskflow/todo-lists-shared';
```

## Import Path Consistency

**All `import ... from` statements in TypeScript source files must use the package name** — the exact string from the target package's `package.json` `"name"` field. Never use filesystem-style paths or placeholder scope names in import paths.

**This applies equally to production code AND test files.** Test helpers and test specs import from the same package names as production code.

```typescript
// CORRECT — matches "name": "@taskflow/todo-lists-shared" in package.json
import { TodoList } from '@taskflow/todo-lists-shared';
import { CreateTodoListSchema } from '@taskflow/todo-lists-shared';

// CORRECT — test file importing from server/client packages
import { TodoListsService } from '@taskflow/todo-lists-server';
import { TodoListList } from '@taskflow/todo-lists-client';
import * as api from '@taskflow/todo-lists-client/todoLists.api';

// WRONG — filesystem-style path with multiple slashes
import { TodoList } from '@project/todo-lists/shared';
import { TodoListsService } from '@project/todo-lists/server';

// WRONG — placeholder scope name
import { TodoList } from '@acme/todo-lists-shared';
```

**When generating server/ or client/ source files**, look at the `shared/package.json` `"name"` field to determine the correct import path. Do not construct import paths from the folder structure — derive them from the declared package name.

## DON'T

- Use `@project`, `@acme`, or other **generic placeholder** scope names. Always derive from app purpose.
- Put multiple slashes in a package name: `@project/todo-lists/shared` is **invalid npm**.
- Use `@` scopes with paths that contain more than one `/` — npm only allows `@scope/name`.
- Leave template placeholder names (`@project/domainName/shared`) in generated output.
- Use filesystem-style paths (e.g., `@scope/domain/tier`) as TypeScript import specifiers — use the package name (`@scope/domain-tier`).

```json
// WRONG — multiple slashes, invalid npm package name
{ "name": "@project/todo-lists/shared" }

// WRONG — generic placeholder scope
{ "name": "@acme/todo-lists-shared" }

// WRONG — not URL-friendly
{ "name": "@My App/Todo Lists" }
```

## How to Derive App Name

1. Identify the application's core purpose (e.g., "task management", "payment processing", "e-commerce").
2. Create a short, memorable, lowercase name: `taskflow`, `payhub`, `shopfront`, `docvault`.
3. Use that as the `@scope` across all packages in the monorepo.

If the user has not specified an app name, **ask** or infer from the domain being built. Never default to `@project` or `@acme`.
