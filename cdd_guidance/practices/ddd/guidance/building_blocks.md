# DDD — Procedural Guidance (building_blocks fidelity)

## How to classify a concept

For every concept on your context map, ask these questions in order:

1. **Does it have identity that transcends its attributes?** If you change every field on it but it's still "the same thing" (Invoice #12345), it's an **Entity**. If replacing one instance with another identical one is meaningless, it's a **Value Object**.
2. **Default to Value Object.** Most things are VOs — Money, Address, DateRange, PhoneNumber. Only promote to Entity when identity truly matters across time.
3. **Is it the gateway to a consistency cluster?** If this entity is the one thing you load to enforce invariants across a group, it's an **Aggregate Root**.
4. **Does it have complex birth?** If creating a valid instance requires invariant checks, subtype selection, or assembly of parts, add a **Factory**.
5. **Is there a collection lifecycle?** If the business finds, stores, and retires this aggregate independently (not just as a part of something else), add a **Repository**. No repository if there's no independent lookup.
6. **Is there a homeless verb?** If an operation genuinely cannot sit on any single domain object, it's a **Service**. These are rare — most "services" should be operations on an aggregate.
7. **Is there a significant moment?** A domain-relevant past-tense fact (`PaymentApproved`, `SubscriptionCancelled`) is a **Domain Event**.

## Thinking about Services — they are rare

The test for a Service: take the verb and try to put it on every domain object involved. If it fits cleanly on one of them, it's not a service. `CheckoutService.placeOrder()` is really `Cart.checkout()`. `AuthenticationService.signIn()` is really `Customer.signIn()`.

A legitimate Service example: `TransferService.transfer(fromAccount, toAccount, amount)` — the operation genuinely spans two aggregates and doesn't belong on either one.

## Thinking about Repositories — they require a lifecycle

Not every aggregate needs a repository. Ask: does the business independently find, store, and retire this thing?

- **Cart** created during checkout, never retrieved as a collection afterward → no CartRepository.
- **Customer** found by email, stored independently, deactivated → CustomerRepository.
- **Subscription** that's always an attribute of Subscriber → no top-level SubscriptionRepository.

## Flaccid data objects

If a class only has fields and getters but no operations, it's a data bag. Fix it: the operations that work with those fields belong on this class. `Order.total()` not `OrderCalculator.calculateTotal(order)`.

## Every concept gets classified

When harvesting from a sketch, every named type in the sketch must appear in the model with a stereotype. Don't cherry-pick a handful — the model covers the full map.
