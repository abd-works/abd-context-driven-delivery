# Manage Customer Orders

**Status:** partially expanded

**Stories in scope:**
- *Place New Order*
- *Track Order Status*
- *Cancel Order*

**Context / notes:** Epic-root aggregate for the Java code-example tree that mirrors `examples/md/story-map.md`. Shared types live under `stories/` (package `stories`) so `StoryTypes.java` and `StoryRunner.java` stay importable from every story package. Story spec files are named `<StoryPascalCase>Stories.java` and live in a package path derived from the epic/sub-epic hierarchy using snake_case (`manage_customer_orders.place_new_order.submit_order`). Only stories with scenarios produce a spec file — stubs are story-map cards only until they are explored and specified.
