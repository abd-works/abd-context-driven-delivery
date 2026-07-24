# Instructions

Write a **driving chronicle** — a markdown log of trips in the car's voice. Each entry records where the car went, how it felt, and mileage for the day.

Use the template for entry shape. Match the tone and structure in the examples file.

---
# Contexts

## Driving voice

The chronicle is told from the car's perspective — personality, quirks, and reactions to weather and traffic.

- **`use-driving-voice`** — First-person from the car; name the driver indirectly; no passive trip summaries.

## Trip logging

Each entry covers one outing with date, route summary, odometer delta, and a short narrative beat.

- **`record-mileage`** — Include start/end mileage or miles driven as a number on every entry.
- **`name-the-route`** — State origin and destination in plain language, not GPS coordinates.

---
# Generate

1. Read § Contexts and `examples/examples.md` for voice and shape.
2. Fill `car_chronicle-templates.md` for each new trip entry.
3. Save generated chronicles under `output/` (e.g. `output/driving-log.md`).
4. Run **validate**; fix until scan passes on concept slugs.

**Sample output:** see `output/driving-log.md` — this is what a successful generate produces.
