# Module: connect-story-examples

**Purpose:** Hold regeneratable story-map data that demonstrates connecting stories to example factories (interface / factory-mode extensions).

**Primary use case:** Clean engineering + stories generators read these story constants when emitting "Generate Type Extending Interface" scenarios at Fake / Isolated / Production **modes**.

**Rationale:** Story data is regeneratable and must not invent Fake/Isolated/Production subclasses — those are factory modes on `{Type}ExampleFactory`.

## Seam

`GENERATE_TYPE_EXTENDING_INTERFACE` constant — story metadata + three mode scenarios (fake / isolated / production).

## Public API

- `GENERATE_TYPE_EXTENDING_INTERFACE` (Final dict)

## Dependencies

None (data only). Pattern owned by clean_engineering + stories generators.
