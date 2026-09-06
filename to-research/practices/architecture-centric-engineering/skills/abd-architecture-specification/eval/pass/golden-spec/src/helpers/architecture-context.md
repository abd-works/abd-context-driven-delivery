# Helpers

Grab-bag of utility modules. Each folder (and loose file) is independent -- there is no shared abstraction across them.

---

**`error/`**
Core error handling mechanism -- `Err`, `ErrorRequest`, and `handleError`. Full spec: [`error/architecture-context.md`](./error/architecture-context.md)

**`validation/`**
`validatePayload` runs a Joi schema against a payload and throws `Err` on failure. `joiTypes` provides reusable Joi primitives (trimmed string, nullable variants). Used by controllers before calling downstream.

**`JWT/`**
`JwtHelper.extractTokenFromHeader` pulls the raw token from `Authorization`/`idtoken` headers. Used by Auth middleware.

**`Customer/`**
`CustomerHelper.extractCustomerData` extracts `customerId` and `email` from a decoded JWT payload. Used by Auth middleware.

**`axios/`**
A bare cached axios instance with a response error interceptor. Older, lower-level wrapper -- separate from `services/Axios/AxiosFactory`. Used by the legacy `responses.ts` path.

**`responses.ts`**
Legacy response builder (`success`, `forbidden`, `badRequest`, `failed`, etc.) that predates `handleError`. Still used by older controllers that haven't migrated to the current error handling pattern.

**`HttpStatusCodes.ts`**
`@deprecated` numeric status code constants, superseded by the `StatusCode` enum in `http.ts`. Only consumed by `responses.ts`.

**`http.ts`**
`Method` and `StatusCode` enums, plus `checkResponse` which throws `HttpResponseError` if status >= 300. Used by older controllers.

**`DateHelper.ts`**
Exports `currentDate` -- an ISO timestamp string pinned to `2021-01-01` in the test environment. Used by entity controllers that need a stable current date.

**`Promises/`**
`allHashes` resolves a keyed `{ [key]: Promise }` object into a `{ [key]: result }` object. Used in scattered controller code where multiple async calls are batched.
