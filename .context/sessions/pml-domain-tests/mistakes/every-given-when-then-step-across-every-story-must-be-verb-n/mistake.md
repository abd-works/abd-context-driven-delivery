# every-given-when-then-step-across-every-story-must-be-verb-n

- **entry_id:** 373093cd
- **artifact:** .context/sessions/pml-my-current-state/cdd-sketch.md — DDD section (Customer, Plan, Subscription, Order BCs), built against Stories
- **rule:** every Given/When/Then step across every story must be verb-noun-analyzed and traced to a specific DDD operation or property; if a step's action or assertion can't be mapped to an existing entry point, that IS the modeling gap and must be fixed (missing operation/property/repository/domain-service method), not glossed over
- **wrong:** Built and iterated the DDD model (Customer, Plan, Subscription, Order/Cart, Billing) from general domain reasoning and ad hoc code spelunking, without ever doing a systematic, exhaustive verb-noun pass over every Given/When/Then step in every story to confirm each step's verb maps to a real operation and each step's noun/assertion maps to a real property. Several read-only Then steps (Dashboard, Billing view, Past Payments/Invoices lists, Support links, Feedback ticket creation) and several action steps (viewing catalog with formatting rules like hiding zero-price plans, composing a resume-redirect target) were never checked against the model at all, so gaps could be sitting undetected.
- **status:** open
