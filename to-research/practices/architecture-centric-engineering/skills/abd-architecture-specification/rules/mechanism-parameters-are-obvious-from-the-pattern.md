---
scanner: mechanism-parameters-obvious
---

### Rule: The mechanism's parameters are obvious from its participants and canonical pattern

A mechanism is a templated pattern, which means it has *parameters* — the parts that vary per instance — and a *fixed shape* — the parts that stay the same. A reader of the context file MUST be able to identify both by reading Participants, File Structure, Class Specification, and Canonical Patterns alone. The mechanism template uses placeholder names (`{Partner}`, `{System}`, `{Operation}`) in these sections specifically so the parameters are visible; when those sections are written with one specific instance's concrete names instead, the pattern's variables become invisible and the reader cannot tell whether they should change a file name, a class name, a method name, all three, or none. A separate numbered "Adding a new instance" recipe is *one* way to make extension explicit — useful when extension touches files outside the mechanism folder (composition root, OpenAPI, tests) — but it's not required: well-parameterized sections often make a recipe unnecessary. Passing means a reader, given only the context file, can list the pattern's parameters and produce a new instance. Failing means the reader cannot tell what is parameter and what is fixed.

#### DO

- Use placeholder names consistently across File Structure, Participants, Class Specification, and Canonical Patterns so the parameters are visible.

  **Example (pass):**
  ```
  src/integrations/{Partner}/
  +-- handler.ts          <- {Partner}Handler implements Handler
  +-- mapper.ts           <- {Partner}Mapper transforms request → response
  +-- types.ts            <- {Partner}Request, {Partner}Response
  ```
  ```typescript
  export class {Partner}Handler implements Handler<{Partner}Request, {Partner}Response> {
    constructor(private readonly http: AxiosFactory) {}
    async handle(request: {Partner}Request): Promise<{Partner}Response> { ... }
  }
  ```
  A reader sees `{Partner}` is the single parameter; the recipe falls out without a numbered list.

- Provide an explicit "Adding a new instance" recipe when extension touches files OUTSIDE the mechanism folder.

  **Example (pass):** The parameterized sections cover the new files inside `src/integrations/{Partner}/`; a short recipe adds the three external steps — register `{Partner}Handler` in `/src/composition.ts`, add the route to `/docs/api/openapi.yaml`, mirror `/tests/integrations/{ExistingPartner}.spec.ts` to `/tests/integrations/{Partner}.spec.ts`.

- Use multiple placeholder names when the pattern has more than one parameter.

  **Example (pass):** A handler mechanism parameterized by `{System}` (the downstream system) and `{Operation}` (the operation on that system). Every section uses both placeholders; the reader sees two parameters.

#### DO NOT

- Write Participants or Canonical Patterns with one specific instance's concrete names.

  **Example (fail):**
  ```
  src/integrations/Mavenir/
  +-- handler.ts          <- MavenirHandler implements Handler
  +-- mapper.ts           <- MavenirMapper transforms request → response
  ```
  Is `Mavenir` a parameter or is it fixed? The reader has to infer by analogy with other instances; the pattern's parameters are not visible from this section alone.

- Show three instances side by side instead of one parameterized pattern.

  **Example (fail):** The Canonical Patterns section shows the full code of Mavenir, Zoho, and Cognito as separate examples. The reader is expected to spot the differences and infer the pattern — but if any one instance is non-canonical (uses an extra file, has a different signature), the inference goes wrong.

- Mix placeholders with concrete names in the same section.

  **Example (fail):** "`{Partner}Handler` registers the Mavenir client in `composition.ts`." Half parameterized, half hard-coded; the reader cannot tell which `Mavenir`s are examples and which are fixed wiring.

**Source:** A mechanism is a template; templates have visible parameters. The reader's first question — "what do I change to add a new one?" — is answered by parameter visibility, not by step-by-step instructions.
