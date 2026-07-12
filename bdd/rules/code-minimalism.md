---
name: code-minimalism
---

# Rule: Code Minimalism

Production code grows only when a failing test demands it. Any property, method, parameter, or branch without a corresponding test is out of scope.

## DO

- Write the simplest code that makes the current failing test GREEN.
- Prefer a function over a class until tests demand state or polymorphism.
- Return only the fields and values the tests assert on.

```typescript
// Minimal — only what the tests assert
function createUser(data: { email: string; name: string }) {
  if (!data.email.includes('@')) throw new Error('Invalid email');
  return { email: data.email, name: data.name, isActive: true };
}
```

## DO NOT

- Add properties, methods, or parameters that no test exercises.
- Pre-emptively design for requirements not yet in a failing test.
- Add configuration options, overloads, or alternative behaviors "for future use".

```typescript
// WRONG — over-engineered; most fields are untested
class User {
  constructor(
    public email: string,
    public name: string,
    public role: string = 'user',         // no test checks role
    public permissions: string[] = [],    // no test checks permissions
    public preferences: {} = {}           // no test checks preferences
  ) {
    this.createdAt = new Date();          // no test checks createdAt
  }

  validatePermissions() { /* no test */ }
  updatePreferences() { /* no test */ }
}
```

**Example (pass):**
Every public property and every code path in the production module has at least one `it` block in the corresponding test file that exercises it and asserts on the result. PASS.

**Example (fail):**
A property or method exists in the production module with no corresponding test assertion. FAIL — remove it or write a test for it first.
