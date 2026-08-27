## Experiments (current)

See [options.md](options.md) for the grouped bundles. See [experiments.md](experiments.md) for timings.

| Bundle | Old ids | Status |
|---|---|---|
| Walker (list tools + inline host guidance) | 3c, 7f (as already-implemented expand) | **Done** — first generate lists tools |
| Single-command | 1b, 1c, 4c, 5a | **Done** — 00:51 / 00:37 |
| Thin first expand | issue 17 restated (not 4a-as-hop-2-cache) | Next if we keep cutting generate clock |
| Channel write | 6c, 3a | Viable |
| Same-kit tool list | 2d | Viable (different clock than story-map generate) |
| Lifecycle in-process | 2b, 7g | Viable (hygiene / later hops) |
| Grill explore | 2a, 2c, 7e | Viable (own corpus) |

---

## Deferred — settled by experiment

Do not re-evaluate these as new courier rows.

| Id | Name | Why parked |
|---|---|---|
| 1b | `run` implies a slim header | In single-command |
| 1c | Stdin only (`run -`) | In single-command |
| 4c | Skill already is the catalog | In single-command |
| 5a | Harness emits the invoke block | In single-command |
| 3c | Nested action expand in-process | Already how Generate works; walker bug was empty `tools:` |
| 7f | Nested `@agent_instructions` become text | Same as 3c; leftover is payload **size** |

---

## Deferred — will not move the remaining generate clock

Measured: one `run -` is ~0.1s; ~51s is reading ~74k chars and writing the map. These cut CLI/manifest/startup, which is already gone on this pair.

| Id | Name | Why parked |
|---|---|---|
| 1a | One-shot flags in skills | Alternate to 1c; no second process to save |
| 1d | Combined `invoke` subcommand | Same as single-command with a new name |
| 1e | Keep two commands, drop `_req.yaml` | We already dropped the extra command |
| 4a | Session cache for later hops | No hop 2 on the generate pair |
| 4b | Slim manifest | We are not remanifesting |
| 4d | Long-lived `tools serve` | Interpreter startup is not the 51s |
| 5b | Cursor MCP `tools.run` | Same 74k still lands in the model |
| 5c | Rule: never remanifest | Already true on the single-command run |
| 6a | Read `.py` and invent | Rejected — breaks the seam |
| 6b | Read `.py` only as diagnose | Fine as diagnose; not an experiment |

---

## Deferred — real taxes, not this generate pair

| Id | Name | Why parked |
|---|---|---|
| 3b | `@agent_instructions` only at choice points | Policy; overlaps Channel write / Lifecycle |
| 7a | AskQuestion tax | Courier protocol already forbids AskQuestion |
| 7b | Cross-workspace roots | Ticket/start-ticket, not generate clock |
| 7c | Project Status names | `gh` board mapping |
| 7d | `gh` / `git` discovery | Spawn per ticket op |
| 7h | Multi-folder workspace | Harness deploy trees |

---

## Flatten note (not a courier row yet)

Old flatten pile (2a + 2b + 2c + 7g) is split across **Lifecycle in-process**, **Same-kit tool list**, and **Grill explore** in [options.md](options.md). Do not run them as one unnamed bundle.
