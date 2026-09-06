# Mechanism: System Entity Controllers

### Overview

System Entity Controllers are the mechanism by which pml-midtier proxies requests to downstream systems. Each downstream system gets its own folder under `src/entities/{System}/`; the folder owns everything needed to receive an inbound HTTP request, validate it, call the downstream system, and return a mapped response. Nothing else in the codebase owns that responsibility.

`app.ts` is the composition root -- it wires the middleware chain and registers every route group. Authentication middleware (`src/middlewares/Auth/`) is applied there as a route-group prefix before dispatch reaches any controller. Every folder follows the same three-file skeleton -- index, routes, controller -- and adds optional files only when the story requires them. The controller is the conductor: it receives `req`/`res`, calls its supporting files in sequence, and returns `res.json`.

### File Structure

```
src/
+-- app.ts                          <- composition root; all middleware + route registration
+-- server.ts                       <- entry point; loadRuntimeEnv -> app.listen
+-- entities/
    +-- {System}/
        +-- index.ts                <- re-exports routes (universal)
        +-- {system}.routes.ts      <- URL bindings (universal)
        +-- controller.ts           <- request handler (universal)
        +-- {system}.factory.ts     <- optional: constructor injection
        +-- validations.ts          <- optional: Joi schemas for incoming request shape
        +-- types.ts                <- optional: TypeScript shapes for outbound API objects
        +-- utils.ts                <- optional: builder/parser helpers (maps between types)
        +-- {system}.service.ts     <- optional: extracted business logic
```

### Participants

All entity files live under `src/entities/{System}/` where `{System}` is the folder name (e.g. `Mavenir`, `Cognito`, `Fygaro`).

**`{system}/index.ts`** -- what `app.ts` imports; re-exports the route group so the composition root stays clean.

**`{system}/{system}.routes.ts`** -- binds URL paths to handler functions; when a factory is present, it calls the factory here to obtain a controller instance before wiring routes.

**`{system}/{system}.factory.ts`** *(optional)* -- constructs the controller with its injected dependencies: logger, axios instance, service. Present only when the controller needs constructor injection (Cognito, Persona).

**`{system}/controller.ts`** -- the entry point for every request; validates input, calls `AxiosFactory.getInstance(baseURL).{method}(path)` to reach the downstream system, maps the response, and returns. Every catch block ends in `handleError`.

**`{system}/validations.ts`** *(optional)* -- Joi schemas consumed by `validatePayload` inside the controller; validates the shape of the **incoming request** (headers, body, params) using primitive Joi types. Independent of types.ts -- it does not import from it. Present when request inputs need schema validation (Fygaro, Mavenir, MdeAdmin, My, Voucher, Zoho).

**`{system}/types.ts`** *(optional)* -- TypeScript shapes for the **outbound midtier API objects** and the external system contract; describes what the controller returns to callers and what it receives from downstream. Present when the response shape needs explicit typing (Mavenir, Voucher, Webflow, Zoho).

**`{system}/utils.ts`** *(optional)* -- builder and parser functions the controller calls to map between the external system contract and the midtier API types. Present when transformation logic would clutter the controller (Fygaro, Mavenir, My).

**`{system}/{system}.service.ts`** *(optional)* -- extracted business logic delegated to by the controller when the handler grows too large. Present when the controller needs a collaborator (Persona, MdeAdmin, Zoho).


### Class Specification

```
## {System}Controller  << Controller >>
Initialisation: instantiated by factory or directly by routes
------
+ async {operation}(req: {Request}, res: Response): Promise<any>
    // {Request}: AuthRequest (protected route) | Request (unprotected route)
    Interaction:
        validatePayload({schema}, {payload})     // {payload}: req.headers | req.body | req.params
        {credentials} = req.headers.credentials  // omitted on unprotected routes
        response = downstream.{method}({url}, {config})   // {method}: get | post | patch | delete
        if response.status === 4xx -> return res.status(4xx).json(...)
        return res.json(this.{build{Domain}}(response.data))
    catch (error) -> return {catchHandler}(res, error)
    // {catchHandler}: handleError (conforming) | custom inline (Cognito, Persona, MdeAdmin, My)
----
- {build{Domain}}(raw: {System}Response): {Domain}Response
    Interaction:
        return {System}Utils.{build{Domain}}(raw)   // delegates to utils
----

## {System}Routes  << Router >>
Initialisation: Router() wired in app.ts via {System}Routes export
------
+ register(): void
    Interaction:
        controller = {System}Factory.create() | new {System}Controller(...)
        router.{method}('{path}', controller.{operation})
        export default router
----

## {System}Factory  << Factory >>  [optional]
Initialisation: called once at app startup
------
+ create(): {System}Controller
    Interaction:
        logger  = LoggerFactory.getInstance()
        axios   = AxiosFactory.getInstance(baseUrl, entityName)
        service = new {System}Service(...)
        return new {System}Controller(logger, axios, service)
----

## {System}Validations  << Schema >>  [optional]
------
+ {operation}Schema: Joi.ObjectSchema
----

## {System}Types  << ValueObject >>  [optional]
------
+ {Domain}Response: { ... }   // midtier API shape
+ {System}Response: { ... }   // external system contract
----

## {System}Utils  << Utility >>  [optional]
------
+ {build{Domain}}(raw: {System}Response): {Domain}Response
```


### Rules

- **`app.ts` is the only place routes are registered.** New route groups live at `src/entities/{System}/{system}.routes.ts` and are imported into `app.ts`. If both protected and unprotected variants exist for the same prefix (e.g. `/mv`), register **unprotected first**.
- **Middleware factories are static class methods** (`Auth.getMiddleware()`, `Zoho.getMiddleware()`) -- never plain module-scope functions.
- **Controllers receive pre-decoded credentials** via `req.headers.credentials` (typed `Credentials`). Controllers must never read `req.headers.idtoken`, import `CognitoServiceFactory`, or call `validateToken`.
- **Start with the 3-file skeleton.** Add optional files only when a story explicitly requires them.
- **Every catch block ends in `return handleError(res, error)`.** No inline status construction.
- **4xx is a resolved value, not a throw.** `validateStatus: status < 500` -- branch on `response.status` explicitly; never let a 4xx propagate to catch.
- **No `axios` imports in controllers.** All outbound HTTP goes through `AxiosFactory.getInstance(baseURL)`.
- **No `console.log` in `src/`.** All logging through `LoggerFactory.getInstance()`.

### Canonical Patterns

```typescript
// {system}/{system}.routes.ts -- URL bindings; factory call if dependencies needed
const router = Router();
const controller = {System}Factory.create();           // or: new {System}Controller(...)
router.get('/{path}', controller.{operation}.bind(controller));
export const {System}Routes = router;

// {system}/{system}.factory.ts [optional] -- constructor injection
export class {System}Factory {
  static create(): {System}Controller {
    return new {System}Controller(
      LoggerFactory.getInstance(),
      AxiosFactory.getInstance(BASE_URL, '{System}'),
      new {System}Service(),
    );
  }
}

// {system}/controller.ts -- canonical handler
export class {System}Controller {
  constructor(
    private logger: ILogger,
    private axios: IAxios<unknown>,
  ) {}

  async {operation}(req: {Request}, res: Response): Promise<any> {
    // {Request}: AuthRequest (protected) | Request (unprotected)
    try {
      validatePayload({schema}, {payload});              // {payload}: req.headers | req.body | req.params
      const { {credential} } = req.headers.credentials; // omit on unprotected routes
      const response = await this.axios.{method}('{url}', { headers: {config} });
      if (response.status >= 400) return res.status(response.status).json(response.data);
      return res.json(this.{buildDomain}(response.data));
    } catch (error) {
      return handleError(res, error);                    // {catchHandler}: handleError | custom inline
    }
  }

  private {buildDomain}(raw: {System}Response): {Domain}Response {
    return {System}Utils.{buildDomain}(raw);
  }
}
```

### Across the Codebase

No two system controllers are identical. The skeleton is universal; everything below it varies. The table shows which optional files each system uses, and where a system deviates from the standard pattern, what it does instead.

**Mavenir** is the pattern applied recursively. The `Mavenir/` entity holds no single `controller.ts`; instead it contains a `controllers/{area}/` folder per domain area, each of which is its own System Entity Controller. All three areas share entity-level `utils/` (getAuthHeaders, axiosHandleError) and split routes (`mavenir.routes.ts` + `mavenir.routes.unprotected.ts`). The common deviations across all Mavenir areas: `axiosHandleError` from entity-level utils replaces `handleError`; raw `axios` import replaces `AxiosFactory`.

| System | factory | controller | validations | service | utils | types |
|---|:---:|---|:---:|:---:|:---:|:---:|
| Apple | - | Serves static Apple cert from in-memory object; no validation | - | - | - | - |
| Cognito | yes | signUp + resendPassword via Amplify; inline success/failed envelopes | manual `if` guards | - | - | - |
| Fygaro | - | Signs JWT locally; no outbound HTTP | `validateHeaders` not `validatePayload` | - | yes | - |
| MdeAdmin | - | Delegates all business logic to service | yes | yes | - | - |
| Mavenir/customer | - | Orchestrates customer CRUD; calls multiple Mavenir endpoints per operation;<br>builds CustomerResponse via utils/buildCustomer | yes | - | yes + payloads/ | multiple files in types/ |
| Mavenir/inventory | - | Number/SIM operations; uses payloads to build Mavenir request bodies | yes | - | yes + payloads/ | yes |
| Mavenir/gateway | - | Fetches + filters plan catalog; cached `axios.request`; rambda for transforms | - | - | config.ts | yes |
| My | - | Client-facing Zendesk routes; directly instantiates `CustomerController` from Mavenir | yes | - | yes | - |
| Persona | Amplify + Axios | Retrieves + ownership-verifies Persona documents; re-validates JWT inside controller | - | yes | - | - |
| Voucher | - | Validates and creates vouchers | yes | - | - | yes |
| Webflow | - | Fetches roaming countries; raw `axios` import; no `AxiosFactory` | - | - | - | yes |
| Zoho | - | Delegates catalog and inventory fetches to service | yes | yes | - | yes |
