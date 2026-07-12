---
name: oo-api-design
---

# Rule: OO API Design (Ask, Don't Tell)

When tests drive a class, the class manages its own state, initializes completely on construction, exposes state through properties, and places operations on the closest domain object. Methods use internal state rather than receiving it as parameters.

## DO

- Initialize completely on construction — the object is usable immediately after `new`.
- Use properties (not getter methods) for state and computed values.
- Use simple verb names for actions: `build()`, `save()`, `validate()`.
- Place operations on the object that owns the concept in the domain model.

```typescript
const agent = new Agent('test');
agent.start('shape');                      // method — changes state
agent.assumptions = { key: 'value' };      // property — sets state
const result = agent.build();              // method — uses internal state
const instructions = agent.instructions;  // property — computed from state
```

## DO NOT

- Require setup calls after construction: `agent.loadConfiguration()`.
- Pass internal state as parameters to methods: `agent.build('shape', assumptions)`.
- Use getter-method names for property access: `agent.getPromptTemplates()`.
- Place child-domain operations on the parent object.

```typescript
// WRONG
const agent = new Agent('test');
agent.loadConfiguration();                    // should happen in constructor
agent.build('shape', assumptions, criteria);  // state should be internal
agent.getPromptTemplates();                   // should be a property
agent.savesContentData();                     // save belongs to contents, not agent
```

**Example (pass):**
Every class in the production module initializes fully in the constructor. No `load*()`-style post-construction calls in any test. Every property access uses `object.property` not `object.getProperty()`. PASS.

**Example (fail):**
A test calls `object.initialize()` or `object.load()` after `new`. FAIL — the object is not self-managing.
