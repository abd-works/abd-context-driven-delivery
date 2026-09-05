---
scanner: canonical-examples-production-ready
---

### Rule: Canonical Patterns code blocks would pass production code review

Code blocks in a mechanism's Canonical Patterns section (and any code samples in package or test-helpers context files) MUST be production-ready in the project's coding and testing standards — same naming, same dependency injection style, same error handling, same types, same test framework. Aspirational pseudo-code, `// TODO`, `// in production you would...`, `any` placeholders, omitted return types, or "for brevity we skip the imports" are not canonical: they encode the wrong shape and the next engineer copies the wrong shape. Passing means the example could be pasted into the codebase and only the placeholder names (`{Partner}`, `{Operation}`) would change before a clean review. Failing means the example skips concerns the production standard requires or introduces conventions the project does not actually follow.

#### DO

- Ship examples that would land a PR with no review changes other than placeholder renaming.

  **Example (pass):**
  ```typescript
  // /src/integrations/{Partner}/handler.ts
  import { AxiosFactory } from '/src/services/Axios/AxiosFactory';
  import { Logger } from '/src/services/Logger/Logger';
  import { handleError } from '/src/helpers/error/handleError';
  import { {Partner}Request, {Partner}Response } from './types';

  export class {Partner}Handler {
    constructor(
      private readonly http: AxiosFactory,
      private readonly logger: Logger,
    ) {}

    async handle(request: {Partner}Request): Promise<{Partner}Response> {
      try {
        const response = await this.http.post('/{partner}/op', request);
        return this.map(response.data);
      } catch (error) {
        return handleError(error, '{Partner}Handler.handle');
      }
    }

    private map(raw: unknown): {Partner}Response {
      // mapping per /docs/integrations/{Partner}.md
      ...
    }
  }
  ```
  Constructor injection, named errors, full types, real imports, real error handler — would pass review.

- Cite the standards the examples obey at the top of the section or context file.

  **Example (pass):** "Examples follow `abd-clean-code` (constructor injection, named operations, no anemic data bags) and `abd-story-acceptance-test` (helper-driven test classes)."

- When the project's standard differs from the agilebydesign defaults, name the standard explicitly so the example's shape is justified.

  **Example (pass):** "Coding standard: `agents/coding-standards.md` (corporate Java guide). Testing standard: in-house JUnit patterns. Examples obey both."

#### DO NOT

- Ship aspirational pseudo-code.

  **Example (fail):**
  ```typescript
  function handle(data: any) {
    // TODO: validate input
    const result = doStuff(data);
    // TODO: error handling
    return result;
  }
  ```
  Two TODOs, `any`, undefined `doStuff` — the next engineer copies the gaps.

- Skip concerns the production standard requires.

  **Example (fail):**
  ```typescript
  export class RecipientManager {
    process(data: any) { /* ... */ }
  }
  ```
  Project uses `abd-clean-code`: `Manager` class, `process` method, `any` parameter, no constructor dependencies. Violates the standard.

- Ship test snippets with patterns the testing standard forbids.

  **Example (fail):**
  ```typescript
  try {
    const r = await svc.createInvoice(input);
    if (r.ok) expect(r.value).toBeDefined();
  } catch (e) { /* ignore */ }
  ```
  Defensive try, conditional assertion, swallowed exception — violates `abd-story-acceptance-test` and any sensible testing guide.

- Strip imports "for brevity".

  **Example (fail):** A canonical example missing imports and `extends` declarations. The reader cannot tell what the class inherits or where dependencies come from; the example is not actually canonical.

**Source:** "Documentation as code" — examples in architecture documentation are templates that get copied; they encode the standard the team is held to.
