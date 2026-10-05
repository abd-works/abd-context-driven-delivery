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
- Onboarding and account each have a system per line.
- PC Bank lines include credit cards and exclude mortgages.
- EQ Bank lines include mortgages and exclude credit cards.
- Cross sell is two epics: Cross Sell Credit Cards (PC Bank) and Cross Sell Mortgages (EQ Bank).
- Sales people open the single client view, then cross sell. Two flows in each epic: a client of either bank, and a new client of a single bank.
- Display story per bank × perspective × system. Render Client Dashboard is separate. Integration is a separate story per system.

## Outcomes

Group by the business outcome. Systems and perspectives sit inside the outcome.

- Cross Sell Credit Cards and Cross Sell Mortgages are the two outcomes.
- Each outcome brings one client together across PC Bank and EQ Bank, then follows a sales process and a call-center process. Sales Person and Call Center are the two actors.
- Credit-card systems belong only to the credit-card outcome. Mortgage systems belong only to the mortgage outcome.
- Credit cards: sales person and call center both make the offer.
- Mortgages: call center hands the client to a sales person. Only the sales person offers the mortgage.
- Store is a third actor, the store footprint. The store sees the client across both banks and offers credit cards and mortgages in the store. The call-center handoff stays on the call.
