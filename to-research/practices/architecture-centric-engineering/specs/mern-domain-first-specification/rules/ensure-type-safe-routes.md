---
scanner: type_safety_scanner.py
---

# Rule: Ensure Type-Safe Routes

Route handlers in `<<domain>>.routes.ts` must compile without implicit `any` types or missing property errors. When handlers access extended Express `Request` properties (e.g., `req.user`), include the necessary type declarations.

## Express Type Augmentation

When a route accesses properties not in the base Express `Request` type, include a **global type augmentation** at the top of the routes file:

```typescript
// packages/recipients/server/recipients.routes.ts

import { Router } from 'express';

declare global {
  namespace Express {
    interface Request {
      user?: { enterpriseId: string; token: string };
    }
  }
}
```

## DO

- Include `declare global { namespace Express { ... } }` when accessing `req.user`, `req.session`, or middleware-injected properties.
- Type callback parameters explicitly when `noImplicitAny` or `strict` is enabled.
- Use domain types from `shared/` for parsed bodies and responses.

## DON'T

- Access `req.user` without a type declaration — causes TS2339.
- Use `(req as any).user` to bypass type checking — augment the type instead.
- Suppress errors with `// @ts-ignore` instead of providing proper types.
