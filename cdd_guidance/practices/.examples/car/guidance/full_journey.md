# Car — Procedural Guidance (full_journey fidelity)

## From road story to inspectable journey

Full journey adds a trip-log wrap around the road story prose. The narrative is the same; the addition is structured metadata that makes the journey inspectable:

1. **Keep the prose story** — everything from road_story carries forward.
2. **Add trip-log structure** — timestamps, speed at each beat, conditions at each checkpoint.
3. **Make it reviewable** — someone reading the trip log can understand what happened, when, and why.

## Thinking about the log entries

Each story beat produces a log entry with:
- What happened (the event)
- The car's state (speed, gear, position)
- Conditions at that moment (road, weather, traffic)
- Any dialogue the car produced

The log complements the prose — it doesn't replace it.
