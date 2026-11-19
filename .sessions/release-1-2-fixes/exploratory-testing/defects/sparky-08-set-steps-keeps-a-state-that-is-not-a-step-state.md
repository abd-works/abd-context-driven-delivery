# prompt-queue.set_steps through the cdd server keeps a step whose state is not pending, in_progress or done

- **Charter:** Round 1 - explore the prompt queue as several robots and a person changing one chat's queue at the same time (card 7887d9ffe762)
- **Tester:** Sparky
- **Story:** Queue Prompts For Later / Nest Prompt Steps In Queue / Set Steps Of Queued Prompt. No scenario gives a state outside the three.
- **Module and class:** `tools/prompt_queue/prompt_queue.py` `PromptQueue.set_steps`; the tool's schema, which the server builds from `PromptStep` (`state: StepState`), requires `state` but does not limit its values.
- **Severity:** wrong result

## Steps

`C:\dev\_et\sparky\work\t\server.py` (environment as in sparky-01, `CDD_CHATS_FOLDER=C:\dev\_et\sparky\work\chats-server`): starts a real cdd server with `SpecServer(("tools.prompt_queue.prompt_queue:PromptQueue",))` and calls, as a chat:

1. `prompt-queue.add_all chat="" texts=["one", "   ", "/push", "two"]`
2. `prompt-queue.set_steps chat="" prompt=<id of one> steps=[{"text": "s", "state": "bogus"}]`

## Expected

A refusal naming the three states, as the same call without `state` is refused (`Input validation error: 'state' is a required property`). The operation's own text says "each its text and its state: pending, in_progress, or done".

## Actual

```
{"prompts": [{"id": "fa77f8150e28", "text": "one", "steps": [{"text": "s", "state": "bogus"}]}, ...]}
```

The queue file keeps `bogus`, and the mod that draws the steps reads a state it does not know. Likely spellings from an agent: `in-progress`, `completed`, `Done`.

## Tier that should catch it

Heavy: `prompt_queue_heavy_spec.py`, since the schema is the server's. It sets steps only with the three states.
