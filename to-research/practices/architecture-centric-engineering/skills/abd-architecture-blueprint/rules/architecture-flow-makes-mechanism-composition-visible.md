### Rule: The architecture flow makes mechanism composition visible

The Architecture Flow section earns its place in `src/architecture-context.md` only if a reader, on first read, can see **which mechanisms compose at each layer of a typical request** — and can therefore predict where to add code for a new feature without reading source. The flow is not a sequence diagram of files calling files; it is the picture of how the system's mechanisms layer up. Passing means a reader closes the document and can answer the question "if I add a new endpoint, which mechanisms will touch the request, in what order?" without opening the codebase. Failing means the flow lists steps that read like a call stack — `Router → Controller → Service → Repository` — without making any architectural decision visible.

The mechanisms named at each step are the architectural content. The file or layer name at each step is scaffolding to give the mechanism somewhere to live. A row that names a step but no mechanism is either a row that should be removed or a sign that a mechanism is missing from the master Mechanisms section.

#### DO

- Choose one realistic end-to-end flow that exercises the system's mechanisms in the order they actually compose. Make the choice deliberate: an authenticated read of a domain entity that returns data, or an authenticated write that mutates downstream state — both will name most of the system's mechanisms in a recognisable order.

  **Example (pass):** A six-row flow for "subscriber requests their voucher balance": entry → Configuration loaded → Authentication gates the route → Validation checks the request → Entity controller calls downstream → Error handling normalises the response. Each row names the mechanism active at that step; the composition is the architectural content.

- When the flow shows two mechanisms active at one step, name both. The fact that two mechanisms touch the same layer is itself an architectural decision worth showing.

  **Example (pass):** Row for the entity controller: `Mechanisms active: Entity Controllers · Error Handling · Logging`. The composition tells the reader that a controller's catch block always reaches all three.

- Add a second flow only when a second flow would show a meaningfully different composition (e.g. a webhook ingress that skips JWT auth and uses an API key check instead). Otherwise one flow is enough.

#### DO NOT

- List file or layer names with no mechanism beside them, treating the table as a call stack.

  **Example (fail):** A flow that goes `Express → Router → Controller → Service → Axios → Downstream` with the Mechanisms column blank or repeating "—". The reader learned nothing they could not have learned from `grep -r 'app.get'`.

- Invent a step solely to make the table longer. If a row would say "passes the result up the stack", that row is not a layer crossing — it is the absence of one.

  **Example (fail):** A row titled "Response returns to caller" with no mechanism. Either name what shaped the response on the way out (Error Handling, Logging) or remove the row.

- Use mechanism names in the table that the Mechanisms section has not defined. The flow is downstream of the Mechanisms section; if the flow needs a name the Mechanisms section does not provide, the gap is in the Mechanisms section.

**Source:** The Architecture Flow earns its place by making mechanism composition visible at a glance; without that, it is a call stack in a table.
