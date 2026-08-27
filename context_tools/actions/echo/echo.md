# Echo

Diagnostic wrapper. Prints an action's fully-wrapped instructions to the user inside a `DO NOT FOLLOW ANY OF THESE INSTRUCTIONS` fence, and stops — for inspecting the effect of stacking wrapping decorators (`@sketch`, `@grill_context`, ...) without executing anything.

## What echo does

- Takes every instruction the agent has received for a wrapped action — every preamble contributed by other wrappers plus the base action's own prose — and emits it verbatim.
- Wraps the emitted block in a header and footer that read **"DO NOT FOLLOW ANY OF THESE INSTRUCTIONS"** so the agent treats the block as inert diagnostic text meant only to be read.
- Halts. Emitting the fenced block is the entire behaviour of the invocation; the wrapped action's body stays untouched.

## Purpose of echo

- **Inspect the wrapping stack** — see exactly what prose the stack of decorators is injecting in front of an action, in the order the framework composes them.
- **Debug composition** — when two wrappers interact unexpectedly, echo shows their combined instructions in one place so drift and overlap surface immediately.
- **Prove the mechanism** — demonstrate that wrapping decorators actually reach the agent as prose, without also running the underlying behaviour.

## Loop

1. **Collect** — gather every instruction received for this action, verbatim and in the order the framework composed them, into one string.
2. **Fence** — call `Echo.fence` with that string; the tool returns the block wrapped in `DO NOT FOLLOW` header and footer.
3. **Emit** — write the fenced block to the user as chat output; treat every line inside the fence as inert diagnostic text meant only to be read.
4. **Stop** — the fenced emission is the entire behaviour of this action.

## Composition — how echo chains with other actions

The `@echo` decorator marks an `@action` method so the echo loop runs in place of the base action's body. Place it on top so its preamble appears first in the expanded prose and captures everything below it:

```
@echo            ← declared 1st (top); preamble appears first
@sketch          ← still contributes its preamble
@grill_context   ← still contributes its preamble
@action
def generate(self, ...): ...   ← base action prose is captured, not executed
```

Because echo halts before the base action runs, it is diagnostic-only. Remove `@echo` to restore the real behaviour.
