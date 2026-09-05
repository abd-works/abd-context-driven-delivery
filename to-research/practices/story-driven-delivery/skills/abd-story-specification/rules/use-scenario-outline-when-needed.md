# Rule: Scenario Outline is the default notation

**Scenario Outline is the default.** Every story with more than one scenario must use `Scenario Outline` with normalised `Examples` tables. Plain `Scenario` blocks are the exception, not the rule.

## DO

- Use **Scenario Outline** for all multi-scenario stories — happy path, failure, edge cases, boundary sweeps, flag variants.
- Organise Examples tables by domain concept (one table per concept), linked by a `scenario` column.
- Use `{column_name}` tokens in steps that match Examples table headers exactly.
- Use a plain **Scenario** only when a story has exactly one scenario and adding a one-row Examples table provides no value.

```
Scenario Outline: Authenticate Subscriber
  Given a **Subscriber** {email} with account status {account_status}
  When the **Subscriber** submits {email} and {password}
  Then the system navigates to {expected_destination}

  Examples:
  | scenario   | email                    | account_status | password | expected_destination |
  | Scenario 1 | alex.chen@paradise.bm    | active         | correct  | /my                  |
  | Scenario 2 | new@paradise.bm          | first_time     | correct  | /my/setup            |
  | Scenario 3 | alex.chen@paradise.bm    | active         | wrong    | sign-in              |
```

## DON'T

- Do not write multiple plain `Scenario` blocks for the same story when they differ only in data.
- Do not use a flat single table mixing multiple domain concepts — normalise into separate per-concept tables.
- Do not skip Outline because paths "feel different" — if data varies across paths, Outline rows capture that variation.

```
# WRONG — multiple plain Scenarios when Outline rows would do
### Scenario 1: Valid credentials navigate home
Given a Subscriber alex.chen@paradise.bm …
### Scenario 2: Wrong password shows error
Given a Subscriber alex.chen@paradise.bm …
```
