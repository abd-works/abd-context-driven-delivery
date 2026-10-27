# DDD — Procedural Guidance (model fidelity)

## What the view is for

The model is one view of the core domain with everything else taken out: aggregate roots, the entities and values they own, their repositories, the domain operations, and the arrows between aggregates. It is where the domain gets argued, merged, and simplified — before factories, events, ports, or frameworks make every change expensive.

Golden example: `bounded-context-key-entities-with-operations.drawio` — bounded contexts as outer containers, aggregates as inner containers, one root card per aggregate with its repository section underneath, members composed beside it, and arrows only where one aggregate needs another.

## How to draw an aggregate

For each aggregate on the bounded-context map, in this order:

1. **Root card** — `<<Aggregate Root>> <<Entity>>`, the root's name, its identity and properties, then its domain operations.
2. **Repository section in the same card** — below the operations: `<<Repository>> {Root}Repository`, then `create`, `load`, `update`, and `search` / `retire` only when the business does them. One below the other, so lifecycle and behaviour read together.
3. **Members** — each owned entity (`<<Entity>>`) or value (`<<Value Object>>`) as its own card, composed by the root or by the member that owns it. Give a member operations only when it owns the state they change.
4. **Arrows out** — for each operation that needs another aggregate, an arrow from the class that depends to the root it depends on, holding that root by identity.

Same order, same place, every aggregate. A reader comparing two aggregates sees their differences, not differences in drawing.

## Finding the operations

Walk the stories and scenarios. Every verb the business performs on the aggregate is a public operation on the class that owns the state it changes, named with the scenario's verb. Then sort them:

- **Creates, finds, changes as a whole, retires** → repository (`create`, `load`, `search`, `update`, `retire`).
- **Anything with a rule** → domain operation on the root or a member.

A rule on the repository runs only when the aggregate is saved and cannot be found where the aggregate lives.

## Thinking about Repositories — they require a lifecycle

Not every aggregate needs a repository. Ask: does the business independently find, store, and retire this thing?

- **Cart** created during checkout, never retrieved as a collection afterward → no CartRepository.
- **Customer** found by email, stored independently, deactivated → CustomerRepository.
- **Subscription** that's always an attribute of Subscriber → no top-level SubscriptionRepository.

## Flaccid data objects

If a class only has fields and getters but no operations, it's a data bag. Fix it: the operations that work with those fields belong on this class. `Order.total()` not `OrderCalculator.calculateTotal(order)`.

## Simplify before you detail

Read every aggregate back and push:

- Are two operations really one with a parameter?
- Is this member entity really a value — does anyone ever ask "which one"?
- Does this class exist only to hold another class's fields?
- Is this aggregate really a member of another — do they always change together?
- Does this arrow exist because of the domain, or because of how a screen or a vendor API happened to work?

Each merge removes code, tests, and screens that would otherwise be written.

## What stays out

Constructors, private helpers, ports, event publishers, DTOs, request and response shapes, framework types, persistence and transport detail. Factories, specifications, domain services, and event classes wait for **tactics** — unless the code being described already has them, in which case show them as they are so the model matches the code.

## Model and code move together

Each aggregate is a folder, each root a class with these operations, each repository the collection the model shows. When the model changes, the code changes with it; when the code already splits an aggregate into more pieces, the model shows those pieces.
