### Rule: A mechanism's context file names how a new instance becomes live

A mechanism produces multiple instances; each new instance has to *activate* somehow — actually run as part of the system. The activation style varies: a **composition root** registers instances explicitly (DI container, route table, plugin registry, dispatcher); an **inheritance-based** mechanism activates by being extended and consumed (extend `BaseValidator`, import the subclass where it's used); a **convention-based** mechanism activates by file-system discovery (place a file matching a glob, framework auto-discovers it); a **decorator/annotation-based** mechanism activates by metadata the framework scans for (`@Controller`, `@Provider`). The context file MUST name which style this mechanism uses and the concrete location or contract a new instance needs to satisfy. Without this the reader who writes a new instance cannot tell whether/how it joins the running system — they ship code that compiles but never executes, or worse, get a runtime "no handler registered" they cannot trace. Passing means a reader can answer "what do I have to do for this new instance to be live?" from the context file alone. Failing means the file shows the pattern and stops short of saying how it runs.

#### DO

- Name an explicit composition root for register-style mechanisms.

  **Example (pass):** "Activation: register `{Partner}Handler` in `/src/composition.ts` via `handlers.register('{partner}', new {Partner}Handler(http))`. The dispatcher resolves handlers by name from this registry."

- Name the base class and consumer pattern for inheritance-style mechanisms.

  **Example (pass):** "Activation: extend `BaseValidator<T>` and export the subclass. There is no registry — consumers import the validator class directly at the call site (e.g. `new EmailValidator().validate(input)`); usage by the consumer is what makes the instance live."

- Name the discovery contract for convention-style mechanisms.

  **Example (pass):** "Activation: place the controller file at `/src/controllers/{Resource}/{Resource}Controller.ts` matching the glob `**/*Controller.ts`. The bootstrap scanner in `/src/bootstrap.ts` registers any class matching this glob and decorated with `@Controller`. No manual wiring step is needed."

- Name the metadata contract for decorator/annotation-style mechanisms.

  **Example (pass):** "Activation: decorate the class with `@Provider({ scope: 'request' })` and place it under `/src/providers/`. NestJS's module scanner (configured in `/src/app.module.ts`) picks up decorated classes at startup and injects them where requested."

#### DO NOT

- Show the pattern without naming the activation path.

  **Example (fail):** The context file shows `{Partner}Handler` and its canonical implementation, then stops. A new engineer writes `MavenirHandler.ts`, runs the system, and nothing happens — there is no clue whether they should have registered it somewhere, decorated it, extended a discoverable base, or imported it from a specific consumer.

- Assume "instantiate at the call site" without saying so.

  **Example (fail):** "`{Partner}Handler` is a class consumers can use." Used where? Imported how? Constructed by whom? If the activation is "consumer instantiates directly at the usage site," say that explicitly and name a representative call site.

- Mix activation styles inside one mechanism without naming each.

  **Example (fail):** Some handlers are registered in `composition.ts`; others are auto-discovered by file glob; others are instantiated at the consumer's call site. The mechanism documentation shows one canonical handler and is silent about activation. The mechanism is either incoherent (three patterns posing as one) or the documentation is hiding the variation; both fail the reader.

**Source:** A mechanism is the *pattern*; an instance is *live code*. Activation is the bridge between them. Without naming the bridge the documentation describes shape but not behaviour, and the reader can produce code that exists without running.
