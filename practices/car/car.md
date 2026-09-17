# Contexts

In-character road stories turn vehicle personality into a narrative the reader can follow. Every story names the car, the road, and what happens in order — start the engine before you speak, stop before you declare arrival.

## Story shape (required)

```
{make} {model} at {destination}
  under {conditions}
    start the engine
    drive according to personality
    speak in character at story beats
    stop when the scene ends
```

Read top-down as a **driving sequence**: what the car does first, how conditions change choices, what the car says, when the engine stops. Nest by **real road events** — not by internal tool names alone.

| Beat | Names | Never names |
| --- | --- | --- |
| **setup** | Make, model, destination, conditions | Generic "vehicle"; tool method names as the story subject |
| **drive** | Accelerate, decelerate, or hold speed in character | Abstract "invoke start" without story context |
| **speak** | A line that fits personality | Out-of-character meta about the CLI |
| **finish** | Stop with a story reason | Ending mid-scene without stop |

## Fidelities

| Fidelity | Artifact |
| --- | --- |
| **trip_outline** | Bullet beats only — destination, conditions, tool order |
| **road_story** | Full prose story with tool calls woven in |
| **full_journey** | Prose plus trip-log wrap for inspection |
