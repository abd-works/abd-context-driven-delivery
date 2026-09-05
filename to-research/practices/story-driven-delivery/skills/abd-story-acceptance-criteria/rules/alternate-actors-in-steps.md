---
scanner: actor-alternation
---

# Rule: Alternate actors in steps

**Scanner:** `scanners/actor-alternation-scanner.py` — **`ActorAlternationScanner`**

Alternate between actors every 1–2 steps. Show back-and-forth between user and system. System may chain 1–2 sequential actions before returning to the user.

## DO

- When the actor acts, the system responds; when the system completes, the user reacts (or the system continues briefly).
- Allow short system chains (e.g. validate → save) before the next user-visible step.

## DON'T

- Run more than **two** consecutive steps from the same actor without switching (warning heuristic in scanner).
- Stack many user-only lines without system response.
