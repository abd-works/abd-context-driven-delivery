# Deployable plugins from the harness — research

**Date:** 2026-09-01  
**Status:** research only. No harness code changed.  
**Question:** Can `primitives/harness` emit installable Agent Plugins (and client-native plugins) so each context guidance — and later other combinations — can be offered as an isolated bundle of skills, commands, hooks, and whatever else each client actually loads?

This note also evaluates three related problems that keep showing up in this workspace:

1. Rules, hooks, and agents do not reliably make the model follow CDD process.
2. Most “dynamism” is already a compile-time graph in Python; the agent still has to interpret a catalog skill and run `tools.ps1`.
3. MCP is unused. Could it replace the interpretive manifest path?

---

## 1. What the conversation got right, and what it flattened

Reverse-domain folders are real. Agent Plugins 1.0 (published 2026-08-06; Copilot GA 2026-08-12) is a **packaging floor**, not a full agent OS.

Portable, every conformant client:

| Location | What it is |
|---|---|
| `plugin.json` | Closed-schema identity (`$schema`, `name`, plus a short metadata list). Unknown top-level fields are ignored. |
| `skills/` | Agent Skills. Each immediate child directory with `SKILL.md` is one skill. |
| `mcp.json` | Optional MCP server map. A skills-only client may ignore it and still conform. |

Not portable in v1 (commands, hooks, agents, rules, LSP, canvases). Those live in **client extension** space:

- Manifest: `plugin.json` → `extensions["com.example.client"]`
- Files: top-level directory named exactly `com.example.client/`

A client **must ignore** namespaces it does not implement, without validating their contents. That is the isolation sandbox.

The conversation’s mapping is only half-true:

| Client | Reverse-domain (spec) | What actually loads extras today |
|---|---|---|
| GitHub Copilot / VS Code | `com.github.copilot` | Documented: `com.github.copilot/{agents,commands,rules,hooks}/`. Hooks at `com.github.copilot/hooks/hooks.json`. |
| Cursor | often cited as `com.cursor.ide` | **Official Cursor docs do not load rules/commands/hooks from `com.cursor.ide/` inside an Agent Plugin.** Cursor Agent Plugins load **skills + MCP only**. Rich extras need a **Cursor Plugin**: `.cursor-plugin/plugin.json` plus `rules/`, `commands/`, `agents/`, `hooks/`. |
| Claude Code | often cited as `com.anthropic.claude` | **Not an Agent Plugins launch client.** Native format is `.claude-plugin/plugin.json` with `skills/`, `commands/`, `agents/`, `hooks/hooks.json`, `.mcp.json`. Install into Claude is a translator, not native spec support. |
| ChatGPT / Codex | `com.openai.chatgpt` (informal) | Skills + MCP via Agent Plugins. Codex also has `/import` bridges from Claude/Cursor native setups. |

So: **one folder with `com.github.copilot/` extras is a real Copilot strategy. Putting Cursor `.mdc` files in `com.cursor.ide/rules/` is not, by itself, a documented Cursor load path.** For Cursor you either:

- ship a **Cursor Plugin** (native, full component set), or
- ship an **Agent Plugin** (portable skills + MCP) and accept that Cursor will not pick up rules/commands/hooks from that package,

or emit **both artifacts** from the same harness generate.

Anthropic created Agent Skills and MCP but is not on the Agent Plugins TSC. Skills still travel; the **wrapper** does not.

---

## 2. Current harness: local IDE deploy, not a plugin

Harness today (`Harness.type` ∈ `{Cursor, VS Code}`) walks `context_tools/` and `utilities/`, then writes into a workspace IDE folder:

| Source | Cursor write | VS Code write |
|---|---|---|
| context tool | `.cursor/skills/{slug}/SKILL.md` | `.github/skills/{slug}/SKILL.md` |
| action / fidelity / format | `.cursor/commands/{name}.md` | `.github/prompts/{name}.prompt.md` |
| `@instruction` | `.cursor/rules/{name}.mdc` | `.github/instructions/{name}.instructions.md` |

`Hook`, `Agent`, and `AgentGuidance` exist as classes and are explicitly **later** (`NotImplementedError`). `clean` only removes `skills`, `commands`, `prompts`, `instructions`, `rules`.

That is **project-local customization**, the same kind of files a plugin would contain, but:

- there is no `plugin.json` / `.cursor-plugin/plugin.json`
- there is no `mcp.json`
- there is no reverse-domain directory
- the bundle is not installable from a marketplace or `~/.cursor/plugins/local`
- Claude / Codex / ChatGPT are named in the sketch and **must not implement yet**

The generated skill is a **catalog pointer**, not the domain guidance. Example (`bdd` skill as deployed today):

1. Confirm action via `AskQuestion`.
2. Confirm fidelity via `AskQuestion`.
3. Pipe a YAML fence to `.\tools.ps1 run -` with `toolset: context_tools.bdd.bdd:Bdd`.
4. Follow `response.instructions` only. Do not remanifest.

The real BDD/CE prose, companion graph, contexts, examples, and templates are produced **at run time** by the Python toolset. The skill file does not contain them.

That design is why “remind the agent of the rules” keeps happening even when a skill, rule, or hook is present: **the file that got loaded is not the rulebook.**

---

## 3. First option: one plugin per context guidance

Try this first, as asked.

Context guidances in this repo (each is already one `@agentic_toolset` with one skill today):

| Plugin id (proposed) | Source | Companions already in Python |
|---|---|---|
| `cdd` | `context_tools.cdd.cdd:Cdd` | stage children: Stories, Ddd, Ux, CleanEngineering, Bdd |
| `stories` | stories | — |
| `ddd` | ddd | — |
| `ux` | ux | — |
| `clean-engineering` | clean_engineering | — |
| `bdd` | bdd | **calls CE guidance** as a separate tools run |
| `agent-bdd` | agent_bdd | **composes Bdd** (which composes CE) |
| `car` | car | — |
| `create-context-tool` | create_context_tool | — |

### Why isolated first

- A consumer can install **only BDD** (or only Stories) without the whole CDD orchestra.
- Failures are diagnosable: if BDD process is skipped, it is the BDD plugin, not a 40-file mega-bundle.
- Matches how skills are already one-per-toolset.
- Lets the harness grow a `Plugin` write-vehicle without solving “all-in” composition on day one.

### What an isolated guidance plugin should contain

**Portable core (Agent Plugins 1.0)** — every client:

```
plugins/bdd/
  plugin.json
  skills/bdd/SKILL.md          # compiled guidance, not just the catalog pointer
  skills/bdd/references/       # optional: contexts, examples, templates extracted at generate
  mcp.json                     # optional; see §7
```

**Copilot extras** (same package, ignored elsewhere):

```
  com.github.copilot/
    commands/                  # /bdd, /bdd.behavior, … if you want slash without relying on skill auto-attach
    agents/                    # optional persona that always runs BDD
    rules/                     # Copilot rules, not Cursor .mdc
    hooks/hooks.json           # mechanical only (see §5)
```

**Cursor extras** — do **not** assume `com.cursor.ide/` is enough. Emit a **Cursor Plugin** (same tree or a sibling artifact):

```
plugins/bdd/
  .cursor-plugin/plugin.json
  rules/                       # .mdc — only for always-on mechanical constraints, kept tiny
  commands/                    # current /bdd.* fidelity commands
  agents/                      # later
  hooks/hooks.json             # later, mechanical
  skills/                      # shared with the Agent Plugin layout
```

Dual-manifest in one directory is a format-detection risk (Cursor keys off **which** manifest file exists; VS Code keys off `$schema`). Safer first experiment: **two outputs from one source**:

- `plugins/bdd/` — Agent Plugin (portable)
- `plugins/bdd-cursor/` — Cursor Plugin (rules/commands/hooks)

or a generate flag `format: agent-plugin | cursor-plugin | copilot-namespace`.

**Claude extras** are a third emitter (`.claude-plugin/plugin.json`, `.mcp.json`), not a reverse-domain folder, until Claude natively reads Agent Plugins.

### Composition vs isolation

Python already encodes “agent_bdd includes bdd includes clean_engineering” and “cdd includes stage children.” Isolated plugins should **not** pretend those edges do not exist. Two honest shapes:

| Shape | Isolated plugin contains | Consumer installs |
|---|---|---|
| **Thin isolated** | Only that tool’s skill. Companion text says “also install `clean-engineering`.” | User / marketplace dependency (Agent Plugins v1 has **no** portable depends-on field). |
| **Compiled isolated** | That tool’s skill **plus** inlined companion skills (bdd plugin also ships `skills/clean-engineering/`). | One install; larger package; duplicates if they also install CE alone. |

**First experiment: compiled isolated.** Marketplace plugins cannot declare dependencies in v1. Inlining the companion graph at generate time matches the Python graph (`Bdd.guidance` → `ce().guidance()`, `AgentBdd._bdd()`, `Cdd.context_tools()`) and is the only way an isolated plugin is actually usable.

Keep the Python graph as the **source of truth**. Generate snapshots it. Do not hand-maintain a second companion list in plugin YAML.

---

## 4. Other combinations to try after isolated

| Combo | Bundle | When it is worth it |
|---|---|---|
| **A. Isolated per guidance** (first) | One plugin per context tool, companions compiled in | Offering BDD or Stories to a team that does not run CDD |
| **B. Isolated + shared actions plugin** | `cdd-actions` with generate/validate/satisfy/document/render/createRule as skills or MCP tools; guidances stay thin | Same actions today live as slash commands; they are not domain knowledge |
| **C. Stage plugins** | `cdd-discovery`, `cdd-spec`, `cdd-engineer` | Matches `Cdd.fidelities` and `_CONTEXT_TOOLS_BY_STAGE` |
| **D. All-in `cdd`** | Every guidance + actions + formats | Authors of this repo; onboarding; “just install CDD” |
| **E. Authoring vs consumer** | Authoring plugin keeps CLI/MCP; consumer plugin is compiled skills only | Consumer may not have this repo or `tools.ps1` |

Harness generate already has `name_filter` / `source`. Plugin emit can reuse that: `write_deploy(source="bdd", package="plugin")`.

---

## 5. Consistency of rules / hooks / agents — why reminding never stops

This is not a harness bug first. It is how these clients treat the primitives.

### Reliability ladder (high → low) for “the agent actually does X”

1. **User types a slash command** (`/bdd`, `/generate`). The file is in the prompt because the user put it there.
2. **MCP / function tool the model is trained to call**, if the tool is registered and the schema is small enough to stay in context.
3. **Skill auto-attach** via `description` matching. Progressive disclosure: cheap until selected, then the body loads. Still optional. Bad descriptions → never fires.
4. **Custom agent** the user (or a command) selected. Same as a long system prompt. Better than a buried rule; still LLM-follows-prompt.
5. **`alwaysApply` / always-on rules**. Loaded as **hints**. Cursor forum + staff: agents ignore them; `alwaysApply` means “injected,” not “enforced.” Long rules lose. User prompt beats rules. Multi-root workspaces drop rules. Legacy `.cursorrules` is worse than `.mdc`.
6. **Hooks**. **Do not inject process into reasoning.** They run around lifecycle events (`beforeShellExecution`, `afterFileEdit`, `PreToolUse`). Excellent for **deny `rm -rf`**, **run prettier**, **block `git push`**. Useless as a substitute for “remember BDD companion CE.” A hook that never “fires” on guidance is expected: there is no “about to ignore BDD” event.

`createRule` in this repo already aims at the only kind of rule that can be made consistent: a **named mechanical scanner** in the context tool, re-run via `scan`. That is closer to a hook/test than to an `.mdc` sermon.

### Why this repo feels worse than a typical “use const” rule

The deployed skill **defers** the real instructions to `tools.ps1`. Failure modes:

- Skill never auto-selected (description too generic: “Provide guidance for…”).
- Skill selected, agent skips the CLI and improvises from the heading.
- CLI runs, agent ignores `response.instructions`.
- Companion line (“call guidance on Clean Engineering as a separate tools run”) is a second interpretive hop.

Rules/hooks/agents layered on top of that still point at a process the model was never forced through. Reminding is the only remaining enforcement.

### Easiest consistent path (practical ranking)

**Do this, in order:**

1. **Start work with a command, not a rule.** `/bdd` or `/cdd` as the entry. Do not rely on always-on `.mdc` for orchestration.
2. **Compile the actual guidance into the skill body** (and into `references/`) so that *if* the skill loads, the rulebook is already in context. Stop shipping catalog-only skills for consumer plugins.
3. **Expose live operations as tools (MCP or existing CLI as one tool)**, not as “please paste YAML.” Models skip recipes; they call tools.
4. **Use hooks only for mechanical gates** (format, scan, deny). Pair with existing `createRule` scanners.
5. **Keep always-on rules tiny** (≤ a few dozen lines) and phrased as hard constraints (“never remanifest”), not process manuals.
6. **Treat custom agents as optional personas**, not as the compliance layer.

There is no client primitive that makes a coding agent obey a long process document the way a test suite does. The closest substitutes are: **user-invoked command**, **compiled skill text in context**, **callable tool**, **deterministic scanner**.

---

## 6. Compiled vs interpretive (the manifest path)

### What is already compiled

The Python is the compiler:

- Which classes are agentic (`walk`)
- Write vehicles (`@skill` / `@prompt` / `@instruction`)
- Fidelities tables and slash names (`bdd.behavior`, `stories.story_map`)
- Companion graph (`Bdd.ce()`, `AgentBdd._bdd()`, `Cdd.context_tools()`)
- Action vs guidance `AskQuestion` option lists baked into bodies at generate

That compile-time graph is worth keeping **in code**. It is how agent_bdd includes bdd includes CE without a second YAML product.

### What is interpretive today

At chat time the agent must:

1. Choose a skill/command (or be reminded).
2. Run `tools.ps1` with a fence.
3. Follow expanded `response.instructions` (contexts, examples, templates, companion calls).

Most of that expansion does **not** depend on live chat state. `guidance()` for BDD is the same prose every time, plus inlined context files for the current path. Constructor params (`fidelity`, `path`, `session`) are the live bits.

### Where to compile more

| Surface | Compile into the plugin | Keep dynamic |
|---|---|---|
| Context-tool **guidance** (what BDD/CE/Stories *is*) | Yes. Snapshot `guidance()` + contexts/examples/templates into `SKILL.md` / `references/`. Isolated plugins are otherwise empty. | Path/session-specific corpus that truly changes per workspace |
| Companion graph | Yes. Inline companion skills or a single compiled “run BDD then CE” skill. | Do not ask the agent to discover companions |
| Fidelity menus | Yes. Already in slash names and AskQuestion lists. | — |
| **Actions** (generate / validate / satisfy / document / render) | Compile the *recipe* (steps, constraints). | The *execution* must hit the live tool: it writes files, scans, uses current `path` |
| Constructor context (`type`, `fidelity`, `path`) | Defaults and required-param AskQuestion can be compiled. | Actual values |
| Workspace / turn / handoff | No | Session state |

### Where dynamic construction still wins

- **Authoring in this monorepo:** generate/validate must run against the current tree. A static SKILL.md cannot write the next harness slice.
- **New context tools:** adding a class + `fidelities` + generate is cheaper than maintaining parallel plugin markdown.
- **Agent BDD:** specs target a live harness; the skill can describe the method, but running still needs the CLI/MCP.

Rule of thumb: **compile knowledge, keep a tool for side effects.** Today both knowledge and side effects are behind one interpretive CLI hop. Split them.

---

## 7. MCP: can it replace the manifest?

Short answer: **MCP can replace the “pipe YAML to tools.ps1” hop. It cannot replace skills, and it will not by itself make the model follow process.** Agent Plugins v1 treats skills and MCP as the **only** portable pair — that is the intended split.

### What MCP is good for here

The tools CLI already has:

- a machine-readable manifest (`python -m tools manifest …`)
- a run contract (`python -m tools run -` / `tool` / `action`)
- JSON-ish signatures for tools and constructor params

That is an MCP server waiting to happen: stdio process wrapping `_ToolsCli` / `_ToolsetRunner`.

Useful shapes:

| MCP design | Pros | Cons |
|---|---|---|
| **One tool** `run_toolset({toolset, action, context})` | Tiny schema; same as today’s fence; easy to put in `mcp.json` | Agent must still know legal toolset/action names (skill supplies that) |
| **One tool per action** (`generate`, `validate`, …) | Matches how models use tools | Many tools × many toolsets = token burn (GitHub’s official MCP is the cautionary tale) |
| **Resources** for compiled guidance | Agent can `read` BDD guidance without a skill fire | Still must choose to read; not a process enforcer |
| **Prompts** (MCP prompts) | Named prompts ≈ commands, but MCP-prompt support varies by client | Not a portable Agent Plugins component |

### What MCP is not

- Not a rules engine. Tool descriptions are more hints.
- Not reliable enough to be the *only* interface: stdio on Windows, plugin start/stop, `${PLUGIN_ROOT}` vs repo root, clients that are skills-only and skip `mcp.json`.
- Not a replacement for the Python graph. The server would **call** the existing runner.
- Not a substitute for compiled consumer skills. A plugin installed in ChatGPT without this repo cannot spawn `tools.ps1`.

### Reliability vs the current path

| Path | Reliability of “guidance actually used” | Reliability of “generate actually ran” |
|---|---|---|
| Catalog skill → agent runs CLI | Low (skip / improvise) | Medium if they run it |
| Compiled skill in context | High for knowledge | None (no side effects) |
| MCP `run_toolset` | Medium (must call the tool) | **High** if the server is up |
| alwaysApply rule | Low | None |
| Hook after edit | None for guidance | High for scan/format |

**Recommended hybrid, not a replacement:**

- **Consumer isolated plugin:** compiled `SKILL.md` (+ references). No MCP required. Works in skills-only clients.
- **Authoring / this repo:** keep Python as compiler; add optional `mcp.json` pointing at a stdio wrapper of `python -m tools run` so the agent has a real tool instead of a recipe. Skills tell the model *when* and *which* action; MCP performs it.
- **Do not** dump the full per-member manifest into the system prompt. That is the thing you already told agents not to remanifest.

MCP is “open to options” in the sense that it is the **portable side-effect channel** the plugin spec already standardized. It is not mature enough or cheap enough to be the knowledge channel. Skills remain the knowledge channel.

---

## 8. How to extend the harness (when we implement)

Sketch-level only. Hook/Agent/AgentGuidance stay “later” until plugin emit exists.

1. **New generate target** alongside IDE folders: `package=plugin` writes `plugins/{slug}/` instead of (or in addition to) `.cursor/` / `.github/`.
2. **`PluginManifest` write-vehicle:** `plugin.json` with Agent Plugins `$schema`; optional `.cursor-plugin/plugin.json` when `type=Cursor` or `format=cursor-plugin`.
3. **Bodies:** add `CompiledContextToolBody` (snapshot guidance + references) vs keep `ContextToolBody` (catalog + CLI) for in-repo authoring deploy.
4. **Client emitters:**
   - Copilot: `com.github.copilot/{commands,agents,rules,hooks}`
   - Cursor: native Cursor Plugin dirs, not `com.cursor.ide/` until Cursor documents that namespace as a loader
   - Claude: separate emitter, later
5. **Optional `mcp.json`:** one stdio server, command `./` or `python -m tools`, cwd plugin or repo root, `${PLUGIN_ROOT}` for bundled scripts.
6. **Companion compile:** reuse existing Python companion methods; do not invent a second graph.
7. **Commands** in client folders = current `@prompt` fidelity/action files. They are the consistent trigger.
8. **Hooks** only when there is a deterministic script (scan, format). Do not hook “remember the skill.”
9. **Tests:** generate a fixture plugin tree and assert paths + `plugin.json` schema; do not wait for a live marketplace.

Existing `Harness.type` (Cursor | VS Code) is the wrong axis for plugins. Plugins are **multi-client packages**. Keep `type` for local IDE deploy; add `package` / `clients` for plugin emit.

---

## 9. Suggested experiments (order)

1. **Generate `plugins/bdd/` as an Agent Plugin** with a **compiled** BDD skill (guidance snapshot + CE inlined or as a second skill in the same package). Install via Cursor `~/.cursor/plugins/local` **and** as a folder Copilot can load. Compare: does the agent follow BDD without a reminder?
2. Same source, **Cursor Plugin** sibling with `/bdd` command + a 20-line alwaysApply rule that only says “use the bdd skill; do not remanifest.” Measure whether the command matters more than the rule.
3. **Catalog skill + MCP `run_toolset`** in this repo only. Measure whether generate/validate happen without pasting YAML.
4. **All-in `cdd` plugin** only after isolated BDD is clearly better than today’s `.cursor/skills/bdd`.

Success for (1): isolated install, no `tools.ps1`, agent produces BDD-shaped work from the skill text.  
Success for (3): in this repo, generate runs because a tool was called, not because a markdown recipe was obeyed.

---

## 10. Sources

- Agent Plugins spec: https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md
- Manifest / client extensions: https://agent-plugins.org/plugin-authors/manifest · https://agent-plugins.org/plugin-authors/client-extensions
- VS Code / Copilot layout: https://code.visualstudio.com/docs/agent-customization/agent-plugins
- Copilot GA: https://github.blog/changelog/2026-08-12-agent-plugins-1-0-in-vs-code-copilot-cli-and-the-copilot-app/
- Cursor plugins (two formats): https://cursor.com/docs/plugins · https://cursor.com/docs/reference/plugins
- Claude Code plugins: https://code.claude.com/docs/en/plugins-reference
- Portability gaps: https://www.digitalapplied.com/blog/agent-plugins-1-0-ga-what-still-does-not-port
- MCP vs skills: https://www.developersdigest.tech/blog/mcp-servers-vs-skills-2026
- Cursor rules ignored: https://forum.cursor.com/t/agent-ignoring-rules/148566
- In-repo: `primitives/harness/harness.py`, `bodies.py`, `hook.py` / `agent.py` (stubs), `context_tools/bdd/bdd.py`, `context_tools/cdd/cdd.py`, `context_tools/agent_bdd/agent_bdd.py`, deployed `.cursor/skills/*/SKILL.md`

---

## 11. Bottom line

- **Yes**, the harness is the right compiler for deployable plugins: it already walks toolsets and emits skills/commands/rules. It needs a **plugin package** target, not more always-on `.mdc` files.
- **First ship:** isolated plugin per context guidance, with the Python companion graph **compiled into the package**.
- **Cursor extras** go in a **Cursor Plugin**, Copilot extras in **`com.github.copilot/`**. Do not bet the first experiment on undocumented `com.cursor.ide/` loading.
- **Rules/hooks will not fix reminding.** Commands + compiled skill text + (for this repo) a thin MCP/CLI tool will.
- **MCP complements, does not replace, the manifest-as-compiler.** Use it as the portable way to *run* generate/validate; keep compiled skills as the way to *know* BDD.
