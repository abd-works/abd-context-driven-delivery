# Grill answers — single client view

## Active lenses

Confirmed: **stories** (story map), **ce** (object model).

Out of this sketch: ddd, ux, modules, bdd.

## View Client Perspective

Display, dashboard render, and integration are separate stories.

- One display story for every unique perspective on every system that belongs to a bank. Named so far: prospect, onboarding, subscription, active account. Bank names and system names are still unknown, so those story titles stay `{Bank} {System}`.
- One story renders that view on the dashboard: Render Client Dashboard.
- Integration is its own story per system, not part of the display story.
- Add another story when something must be called out later.

## Banks and systems

- Banks: PC Bank, EQ Bank. Instances of Bank, not subtypes.
- One prospect system per bank. System name unknown.
- Onboarding and account each have a system per line: retail deposits, business banking, international banking.
- Display story per bank × perspective × system. Render Client Dashboard is separate. Integration is a separate story per system.
