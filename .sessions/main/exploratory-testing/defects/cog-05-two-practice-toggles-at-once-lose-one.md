# cog-05 Two practice toggles sent at once both answer success, but one of them is undone

**Title** - Turning UX off and DDD off at the same moment (two callers, such as the chat bar and the Files app, or two presses in quick succession) leaves only one of them off: each answer shows its own change made, then the second write puts the first practice back.

**Charter** - theme 7. **Tester** - Cog.

**Story** - Choose Session Practices (chat bar) and Choose Ticket Practices (board). No scenario covers two toggles at once. The selection's own docstring says a page waiting on `guidance_selection_after` hears "a selection made anywhere", so several callers are expected.

**Module and class** - `space/session/practices/guidance_selection.py` *GuidanceSelection.toggle* reads the selected practices (`self.practices`) outside the record's update, then `select` writes the whole practice list inside `self._session.record.update(...)`. The read-then-write is not one step, so the later write is built from a list that does not hold the earlier change. (`changed()` raises the version inside the update correctly; only the practice list is lost.)

**Severity** - wrong result (a practice the person turned off comes back on, or one turned on goes back off, while both callers were told their change was made).

## Steps

Sandbox and server as in cog-01. Session `.sessions/checkout-flow/session.json` with Stories, DDD and UX on.

```python
import asyncio, json, sys
sys.path.insert(0, r"C:\dev\_et\after-1-2-1\cog\scripts")
from cdd import call   # MCP Streamable HTTP client for 127.0.0.1:8961
S = ".sessions/checkout-flow/session.json"
async def m():
    res = await asyncio.gather(*[call("session.toggle_guidance", {"session": S, "part": "practice", "name": n}) for n in ["ux", "ddd"]])
    final = json.loads((await call("session.guidance_selection", {"session": S}))["text"])
    print([p for p in final["practices"] if p["key"] in ("ux", "ddd")])
asyncio.run(m())
```

## Expected

Both changes kept: UX off and DDD off (each toggle is applied to the selection as it is when that toggle writes).

## Actual

Four runs, each starting from the state the run before left:

```
start ddd on,  ux on : answers [ddd on, ux OFF] and [ddd OFF, ux on]  -> final ddd OFF, ux on   (version 26)
start ddd on,  ux on : answers [ddd on, ux OFF] and [ddd OFF, ux on]  -> final ddd OFF, ux on   (version 29)
start ddd off, ux on : answers [ddd off, ux OFF] and [ddd ON, ux on]  -> final ddd ON,  ux on   (version 31)
start ddd on,  ux on : answers [ddd on, ux OFF] and [ddd OFF, ux on]  -> final ddd OFF, ux on   (version 33)
```

The version rises by two each time, so every waiting page redraws twice and ends on a selection neither caller asked for.

## Tier that should catch it

Unit (two toggles against one session record with a fake that interleaves the read and the write) or heavy (two real calls at once through the cdd server). No spec runs two toggles together.
