# Rule: Background vs scenario setup

**Background** contains only **Given** / **And** lines (state), never **When** or **Then**. Use it only when three or more scenarios share the same starting state. Do not repeat Background lines inside individual scenarios.

In a **plain scenario** (`specification-by-example.md`), Background steps use real values inline with **bold** concept names and *italic* values.

In an **outline scenario** (`specification-by-example-outline.md`), Background steps use `{column_name}` tokens with the domain concept name beside each brace.

## DO

- Model shared state once in Background when many scenarios need the same starting world.
- Keep Background free of actions; the first behavior under test belongs in **When** inside each scenario.

Plain example:
``Background:
  Given a **User** *Jane Doe* is logged into ChannelOne 2.0
  And that **User** *Jane Doe* is representing **Enterprise** *Acme Corp* with **Role** *Wire Operator*
``
Outline example:
``Background:
  Given a User {user_name} is logged into ChannelOne 2.0
  And that User {user_name} is representing an Enterprise {enterprise_name} with the Role {user_role}
``
## DON'T

- Put **When** / **Then** in Background, or encode actions inside **Given** lines.
- Duplicate a Background **Given** inside a scenario's own steps.

``# WRONG — action in Background
Background:
  When user logs in

# WRONG — repeats Background
Scenario: Pay wire
  Given user is logged into ChannelOne 2.0
  When ...
``