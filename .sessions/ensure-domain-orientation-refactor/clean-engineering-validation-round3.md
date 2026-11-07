# Clean Engineering re-validation, round 3

Branch `ensure-domain-orientation-refactor` at `42ab935c`, after every item in `clean-engineering-validation.md` was worked. Validate ran again at the modules, model and code fidelities across `harness/`, `space/`, `tools/` and `cdd_guidance/`, with an AI judge on every call, and a cross-file pass read the whole repository for problems that show only across files. The 130 reports are in `validation-reports/` (`clean-engineering-*-20261107T09*.md`, `cross-file-round3.md`).

**Limitation.** The CDD MCP host serves the pinned main runtime, so validate's graph scanners are main's older ones. The judges applied this branch's rules, which they read from the worktree, and treated graph hits as leads. Serving from this checkout would have switched every open chat to it.

**The short answer.** The round-1 and round-2 items hold: no global current objects, one registry, one Violation, no module cycles, Session and Repo split, all 34 bugs fixed. Round 3 found a second layer: round trips that still lose data, failures still swallowed, a few copies that came back, and paths resolved against the host's folder. Four of the mistakes the corrections logs record have come back. Every finding below is being fixed (task list at the end).

Severity: **high** means wrong behaviour or a second object model; **medium** a rule plainly broken; **low** naming or documentation. **New** means found this round; **left** means it was in rounds 1–2 and is not finished.

---

## 1. Wrong behaviour

| Where | What goes wrong | Sev | New/left |
|---|---|---|---|
| `granola.py:26`, `grill_context.py:51,77`, `partition.py:79,38,85`, `context_setup.py:97`, `sketch.py:59` | Relative paths resolve against the MCP host's folder, not the call's session root; notes and partitions land in the CDD runtime checkout (B31/B34 again) | high | new |
| `access_facts.py:15` | The web-access rule matches only `@mcp`, so every `@Mcp` operation passes it silently | high | new |
| `hooks.py:176` | A malformed `hooks.json` is rewritten, erasing the person's hooks (B6 again) | high | new |
| `hook_server.py:785` | `session.session_path` with no session open raises, and the hook answers nothing | high | new |
| `agent_tools_probe.py:345` | A hung tool still hangs diagnostics: the timeout is raised inside the executor's `with` | high | new |
| `guidance_probe.py:90, :173` | Probes report green even when a subsection is red | high | new |
| CE `base_class_model.py:260` | `update_self`, `clone`, `as_record` drop `bases`; every cross-format render and JSON lose base classes | high | new |
| CE `diagram_node.py:62`, `drawio_class_model.py:215` | Stereotypes are read from the class name, so draw.io and Miro lose them both ways | high | new |
| CE `markdown_class_model.py:68` | `## A : B, C` reads as one base; render writes one base; stereotypes never round-trip | high | new |
| Stories `drawio/nodes.py:123` | An actor is dropped at the third nested sub-epic level and deeper | high | new |
| Stories `code_story_model.py:335` | All four code adapters lose `story_type` | high | new |
| UX `html/nodes.py:46` | `story_outline` is never set, so the story explorer never nests screens under stories | medium | new |
| CE `drawio_class_model.py:129`, `graph_practice.py:244`, `python_class_model.py:135` | A malformed file reads as empty or is skipped silently (a `sync` would delete every class; validate skips the file) | medium | new |
| `mcp_server.py:732` and ~11 other `except Exception` | Errors reach the caller as ordinary answers; `isError` never set | medium | new / left B7 |
| `repo.py:224`, `worktree.py:166` | `needs_push` answers False on any git error; `Worktrees.remove` reports a close it did not do | medium | new |
| `installer.py:115` | A corrupt install record is overwritten and `clean` leaves files behind | medium | new |
| `prompt_notify.py:315` | The toast is always written to the CDD checkout | medium | new |

## 2. Second object models and copies

- `ToolRequest` copies what `ToolCall` owns (`tool_calls.py:34`) — high, new.
- PracticeGuidance still knows its session three ways (`guidance.py:84`) — high, left (task 7 had been ticked too early).
- A practice's folder is stored in three files and worked out four ways (`practice_session_output.py:245`) — high, new (B11 one level down; corrections log).
- Board: `FidelityProgress.ticket/slug/practice` string copies, `ReportRule`, `rule_descriptions`, `Ticket.next` and `Board.active` sent whole beside their owners — high, new and left (K-F21).
- Chat bar hand-copies the generated types (`FidelityJson`, `StageJson`, an invented `validated` state) — high, left (corrections log `contract-comes-from-the-adapter`).
- `session.files` returns a 3-level dict beside `FidelitySessionOutput` — medium, new.
- UX screen story links held as name strings — medium, left (decided in round 2; judged again as worse than a reference, so it is being changed).
- Saved graph read by position in 4 places, three graph JSON shapes; explorer `*Entry` family; the framework names Stories, UX, DDD and Clean Engineering in `bound_node.py`, `Node.place`, `_CLASS_KINDS`, `rules.py`, `schema_rules`, `schema_edges` — medium, new and left.
- Spec-only factories beside `formats=` (CE, Stories); ~570 unreachable lines of the CE Miro adapter — medium, new.

## 3. State and globals

- `serving_mcp_host()` module global; `PracticeCatalogue._shared`; the session opener registered at import; log-line chat from the process environment — medium, new.
- Per-call state on long-lived objects: `expand` writes `_scan_arguments`, `HookServer._payload`, `ContextSetup` capture fields, `PromptNotify` per-call fields, `StoryCanvas.render` overwriting its caller's fields — medium, new.
- Parameters an object already holds: `render(format)`, repo into HookServer/HookDaemon, `_inside(...).x(worked_on)`, `finish_review(slug)`, `activate`/`leave` with `self.name`, chat pointers as three strings, `handoff_session(session)` — medium, mostly left (§3).
- Import side effects on `sys.path` and `PYTHONPYCACHEPREFIX` in hook modules (×3) — medium, new.

## 4. Duplication

Case conversion by hand beside `Name` (~25 sites); git run outside `Git` (no timeout); markdown sections and front matter parsed again (catalog, foundry chrome, schema map); rules assembled three ways (validate, ticket); "is the hook server up" ×3; `hook-handlers.json` in 4 places; the CE `<<…>>` reader in DDD; three copies of one C-family parse call; agent_bdd's two block runners; pattern facts helpers copied; builders as three identical classes — medium.

## 5. Size, structure, names

- Classes with several jobs: AgentInstructions (73 methods), Installer (72), AgentToolSet (50), Graph (47), Session (~44), Validate (~35), Repo (~32), FidelityProgress (~28), CodeStoryModel (37 public) — medium, mostly left (§5).
- Deep-module over 40% public: mcp, marks, process, markdown, hooks, installation, graph, guidance — medium.
- Free-function files: foundry_chrome (71), schema_rules (27), schema_edges (22), language_adapter (19), operation_metrics — medium.
- Module cards: ~12 missing dependencies, internals named, `cdd_guidance/patterns` without its own card, ux/model and CE/model cards describe the old graph — low.
- Mark spelled two ways (`@mcp` 100 / `@Mcp` 50, `@skill`/`@Skill`, `@hook`/`@Hook`), which is what broke the web-access rule — medium.
- Banned words: `BoundNode`, `_bound_callable`, `_unbind_as_serving`, `_is_bindable`, `rows`/`exampleRows`, `kit`, `tick` — low.
- Dead code: catalog and foundry-chrome functions, `enroll_*`, `Board.practice`, `verify_report_links`, the stale 26 MB root `.context/graph.json`, `createRule` still counted as a published action, the `create_context_tool` builder docs — medium.

## 6. Fixed since rounds 1–2 (checked)

B1, B2, B12, B13, B14, B16, B23, B27, B30, B34; no global current object; ToolCall per call; one registry of practices and of actions; one Violation; no module dependency cycle; Session and Repo split; ProjectTicket, the second Echo, GuidanceCatalog, `working_on` and `ChatPointer.serving` gone; hook handlers take `HookPayload`; DDD hidden fields; the scanners that missed copies, cycles and the 40% measure.

---

# Task list

1. ◐ Practices, actions, patterns (one agent): round trips (bases, stereotypes, actors, `story_type`, `story_outline`), swallowed parse errors, paths from the session root, the `@mcp` rule, factories, UX story links as references, DDD Entity by stereotype, duplication, validate's rule assembly.
2. ◐ Board and chat bar (one agent): references instead of string and object copies, the chat bar on generated types, slug lookups, rule assembly once.
3. ◐ Session, repo, tools (one agent): one owner for a practice's folder, `session.files`, chat pointers, Granola's project, named failures in repo and worktree, `Name`, legacy readers, prompt_notify and prompt_log.
4. ◐ Harness (one agent): `ToolRequest`, diagnostics timeout and probes, hook safety and `hooks.json`, swallowed exceptions, per-call state, globals, import side effects, one graph JSON shape, the framework naming practices, duplication, free-function files, large classes, deep modules, dead code, `BoundNode`, module cards.
5. ○ Lead: one mark spelling across the repository (decision 26), reinstall, catalog, full suite including heavy specs, then a short re-check of the fixed areas.
