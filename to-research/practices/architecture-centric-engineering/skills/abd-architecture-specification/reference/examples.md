# Examples — abd-architecture-specification

## Mechanism-tier context file

~~~markdown
# Mechanism: System Entity Controllers

### Overview

System Entity Controllers are the mechanism by which pml-midtier proxies requests to downstream systems. Each downstream system gets its own folder under `src/entities/{System}/`; the folder owns everything needed to receive an inbound HTTP request, validate it, call the downstream system, and return a mapped response. Nothing else in the codebase owns that responsibility.

`app.ts` is the composition root — it wires the middleware chain and registers every route group. Every folder follows the same three-file skeleton — index, routes, controller — and adds optional files only when the story requires them.

### File Structure

```
src/
+-- entities/
    +-- {System}/
        +-- index.ts                <- re-exports routes (universal)
        +-- {system}.routes.ts      <- URL bindings (universal)
        +-- controller.ts           <- request handler (universal)
        +-- {system}.factory.ts     <- optional: constructor injection
        +-- validations.ts          <- optional: Joi schemas
        +-- types.ts                <- optional: TypeScript shapes
        +-- utils.ts                <- optional: builder/parser helpers
```

### Participants

**`{system}/index.ts`** — re-exports the route group so the composition root stays clean.

**`{system}/{system}.routes.ts`** — binds URL paths to handler functions.

**`{system}/controller.ts`** — validates input, calls the downstream system, maps the response.

### Class Specification

```
## {System}Controller  << Controller >>
------
+ async {operation}(req: {Request}, res: Response): Promise<any>
    validatePayload({schema}, {payload})
    response = downstream.{method}({url}, {config})
    if response.status === 4xx -> return res.status(4xx).json(...)
    return res.json(this.{build{Domain}}(response.data))
    catch (error) -> return handleError(res, error)
----
```

### Rules

- **`app.ts` is the only place routes are registered.**
- **Start with the 3-file skeleton.** Add optional files only when a story requires them.
- **Every catch block ends in `return handleError(res, error)`.**

### Canonical Patterns

```typescript
export class {System}Controller {
  async {operation}(req: AuthRequest, res: Response): Promise<any> {
    try {
      validatePayload({schema}, req.body);
      const response = await this.axios.{method}('{url}');
      if (response.status >= 400) return res.status(response.status).json(response.data);
      return res.json(this.{buildDomain}(response.data));
    } catch (error) {
      return handleError(res, error);
    }
  }
}
```

### Across the Codebase

| System | factory | validations | service | utils | types |
|---|:---:|:---:|:---:|:---:|:---:|
| Cognito | yes | manual guards | - | - | - |
| Fygaro | - | yes | - | yes | - |
| MdeAdmin | - | yes | yes | - | - |
| Voucher | - | yes | - | - | yes |
~~~

## Package-tier context file

~~~markdown
# Zendesk Service

Zendesk REST API client used exclusively by the Mavenir customer controller (`src/entities/Mavenir/controllers/customer/controller.ts`). Provides a library of payload-builder methods that construct typed ticket bodies from `CustomerResponse` domain objects, then posts them via `Zendesk.createTicket()`.

**`trialPayload`** — called during onboarding when the customer's voucher is a trial; creates a sales task ticket for the customer success team.

**`defaultPayload('id')`** — called during onboarding when the customer needs identity verification.

**`roamingPlanTicket`** — called when a customer activates a roaming plan; creates an internal ticket instructing the team to issue a roaming-enabled eSIM.

**`paymentFailedPayload`** — called when a recurring payment fails; creates an outbound-call task ticket.
~~~

## Miscellaneous-tiny context file

~~~markdown
# Logger Service

Cross-cutting logging singleton. `LoggerFactory.getInstance()` returns a `LoggerService` in production (writes to `info.log`, `error.log`, `audit.log`, level-gated by `LOG_LEVEL`) and a no-op `LoggerMock` in test. Used by controllers, services, and helpers throughout the codebase.
~~~

## Miscellaneous-grab-bag context file

~~~markdown
# Helpers

Mixed utilities with no shared abstraction.

**`axios`** — bare Axios instance used by legacy packages that predate `AxiosFactory`. New code must not import from here.

**`dateHelpers`** — date formatting utilities used by report generation.

**`tokenUtils`** [legacy] — JWT decode helpers superseded by `Auth` middleware; nothing new imports these.
~~~
