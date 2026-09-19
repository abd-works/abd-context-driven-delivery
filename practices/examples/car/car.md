## Overview

In-character road stories turn vehicle personality into a narrative the reader can follow. Every story names the car, the road, and what happens in order — start the engine before you speak, stop before you declare arrival.

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

## Guidance

Every car story is told from the vehicle's personality. Name the car, the destination, and the conditions. The car speaks in character — one line at story beats, not meta-commentary about the CLI.

Every story follows the same physical sequence, regardless of fidelity:

1. **Start the engine** — nothing happens before start.
2. **Drive** — accelerate, decelerate, hold speed. Choices reflect personality and conditions.
3. **Speak** — in-character dialogue at story beats.
4. **Stop** — with a story reason.

Do not skip steps. Do not reorder. Do not use generic "vehicle" without make and model, tool method names as story subjects, or out-of-character CLI talk.

## Fidelities

### trip_outline


**Default format:** markdown
**Stage:** discovery

#### Overview

**Goal:** Name the beats of a trip — destination, conditions, start, drive, speak, stop.

#### Guidance

A trip outline is the skeleton — bullet beats only:

1. **Header** — `{make} {model} → {destination}`
2. **Conditions** — weather, road, traffic in one line
3. **Beat sequence** — numbered steps: start, drive (accelerate/decelerate as conditions demand), speak (one in-character line), stop

This is the planning stage. No prose, no extended dialogue, no narrative arc. Just the beats that will be expanded into a full story at road_story fidelity.

Each beat answers: what does the car do at this moment? The conditions you named constrain the choices:

- Icy road → careful acceleration, no sudden moves
- Open highway → confident speed, personality shows in how fast
- City traffic → stop-and-go, personality shows in patience or impatience

The speak beat is one line that captures the car's personality reaction to what just happened. Not a paragraph — one line.

### road_story


**Default format:** markdown
**Stage:** specification

#### Overview

**Goal:** Tell the road story in character — what the car does and says, in order.

#### Guidance

Take the trip outline beats and expand each into narrative prose:

1. **Set the scene** — the destination, the conditions, the car's mood as it starts.
2. **Weave tool calls into the story** — tool operations (start, accelerate, decelerate, stop) are story events, not function calls. The car starts its engine; it doesn't `invoke start()`.
3. **Dialogue at story beats** — the car speaks in character. Its lines reflect personality and what just happened on the road.
4. **Conditions shape choices** — a cautious car in rain decelerates early; an aggressive car pushes through.
5. **End with arrival** — stop the engine, declare arrival with a story reason.

The story reads as a journey — what happened in order, told from the car's perspective. Tool operations are woven in as physical actions (turning the key, pressing the accelerator), not as API calls.

### full_journey


**Default format:** markdown
**Stage:** implementation

#### Overview

**Goal:** Tell the full journey with an inspectable trip log.

#### Guidance

Full journey adds a trip-log wrap around the road story prose. The narrative is the same; the addition is structured metadata that makes the journey inspectable:

1. **Keep the prose story** — everything from road_story carries forward.
2. **Add trip-log structure** — timestamps, speed at each beat, conditions at each checkpoint.
3. **Make it reviewable** — someone reading the trip log can understand what happened, when, and why.

Each story beat produces a log entry with:

- What happened (the event)
- The car's state (speed, gear, position)
- Conditions at that moment (road, weather, traffic)
- Any dialogue the car produced

The log complements the prose — it doesn't replace it.
