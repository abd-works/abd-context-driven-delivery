Run the action on car at full_journey fidelity through the tools cli

Provide guidance for in-character road stories at the current fidelity.
At trip_outline fidelity: write bullet beats only — destination, conditions, tool order.
At road_story fidelity: write full prose with start, drive, speak, and stop woven in.
At full_journey fidelity: write prose and call wrap_story when a trip log is needed for inspection.
Every tool call uses this toolset with context make, model, year, and personality.
When the story needs a scripted trip, call travelTo on the CarStory companion and pass this Car as a tool argument.

Provide guidance from contexts, examples, and templates.

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

# Car story examples

## travelTo — muddy pursuit to the courthouse

General Lee roared off the farm lane with Rosco's siren wailing behind us. I called start, punched the throttle on the back roads, and spoke over the engine: "Hold on, cousin — courthouse ain't far if the mud don't lie." We slid through Hazzard square and stopped at the steps just as Rosco's cruiser bogged down in the ditch.

## travelTo — night run to Atlanta

Engine first — always. I eased onto the highway, kept the speed honest, and let the Charger talk when the moon cleared the pines: "Atlanta lights don't scare a Dodge that's seen worse."


# Trip outline template

```markdown
# {make} {model} → {destination}

**Conditions:** {conditions}

1. start
2. accelerate / decelerate as the road demands
3. speak — one line in character
4. stop
```

Use at **trip_outline** fidelity. Expand into prose at **road_story**.


Every tool call uses this shape - set `tool` and `arguments`, pipe to CLI:

```yaml
toolset: context_tools.car.car:Car
context:
  fidelity: full_journey
tool: <tool name>
arguments:
  <if needed>
```

Run: python -m tools run -

Suggested flow (repeat and reorder as the story needs):

Read `resources` from each response before choosing the next tool.

With a straight prompt passed, take the action from the prompt. If you took an action from the context versus being given a straight prompt, confirm the use of the context. AskQuestion constrained to these actions: car-inspect | createRule | document | generate | grill | iterate | partition | render | repair | satisfy | scan | sketch | travel-to | validate.
Then run:
Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.car.car:Car
context:
  fidelity: full_journey
action: generate
```
.\tools.ps1 run -
