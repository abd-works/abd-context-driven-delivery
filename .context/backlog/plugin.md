# Claude Code plugin

## Goal

Anyone can install CDD into Claude Code from this public repo with two commands, no clone and no `install.py`:

```
/plugin marketplace add abd-works/abd-context-driven-delivery
/plugin install cdd@abd-works
```

Skills then appear as `/cdd:practices-stories`, `/cdd:actions-generate`, and so on. Agents appear as `cdd:<agent>`.

The installer stays the one way to build every IDE's files. The plugin is one more install target, and each installation subtype owns writing its own piece into it — the same code that writes `.claude/` and `.cursor/` today.

## Plan: "Claude Plugin" as an install target

`python scripts/install.py --ide "Claude Plugin"` writes the plugin.

| Installation subtype | Writes into the plugin |
|---|---|
| `FileInstallation` (skills) | `skills/<name>/SKILL.md`, flattened as for Claude |
| `FileInstallation` (commands) | `commands/*.md` |
| `FileInstallation` (references) | `references/`; links become `${CLAUDE_PLUGIN_ROOT}/references/…` |
| `AgentInstallation` (new; today `Installer._install_agents`) | `agents/*.md` |
| `McpInstallation` | the plugin `.mcp.json`, paths from `${CLAUDE_PLUGIN_ROOT}` |
| `HookInstallation` | `hooks/hooks.json` in Claude's hook format |
| `PluginManifestInstallation` (new) | `.claude-plugin/plugin.json`, and the repo-root `.claude-plugin/marketplace.json` |

## Recommendations

1. **The repo root is the plugin root.** The MCP host needs `harness/`, `cdd_guidance/`, `space/`, and `tools/` at runtime, and a plugin `source` path cannot contain `..`. So `marketplace.json` names `"source": "./"` and `plugin.json` points its skills, agents, and commands at a generated `plugin/` folder. No Python is copied.
   - Check first: custom component paths must keep the repo's existing root `skills/` and `agents/` folders from loading as plugin components.
2. **Python dependencies bootstrap on first start.** The MCP command runs a small launcher that creates a venv in `${CLAUDE_PLUGIN_DATA}` (kept across plugin updates), runs `pip install`, then starts the host.
   - Cost: the first start takes a minute or two, and users need Python 3.11 or newer.
3. **Rules.** Plugins cannot ship rules or CLAUDE.md memory.
   - The always-on rules in `cdd_guidance/rules/` load through a plugin `SessionStart` hook that returns them as `additionalContext`.
   - Path-scoped practice rules already sit inside the practice skills, so they apply when a skill runs. They do not apply automatically by file path.
   - Anyone who wants path-scoped rules runs the installer for their IDE as well.
4. **`plugin/` is committed.** The marketplace installs from the repo, so the generated plugin has to be checked in, unlike `.claude/` and `.cursor/`.
   - Regenerate it with the installer before a release.
   - Add a spec that fails when the committed plugin differs from a fresh install.

## Facts this rests on (Claude Code docs, checked 2026-10-31)

- Plugin layout: `.claude-plugin/plugin.json` (only `name` required); `skills/`, `commands/`, `agents/`, `hooks/hooks.json`, `.mcp.json`, `bin/` at the plugin root.
- No rules directory; a `CLAUDE.md` in a plugin is not loaded.
- `${CLAUDE_PLUGIN_ROOT}` is the installed version's folder and changes on update. `${CLAUDE_PLUGIN_DATA}` (`~/.claude/plugins/data/<id>/`) persists across updates. Both reach MCP servers and hooks, and are substituted in skill and agent markdown.
- A `SessionStart` command hook can add context with `hookSpecificOutput.additionalContext`.
- A marketplace can live in a public GitHub repo at `.claude-plugin/marketplace.json`; the entry `name` must equal the plugin's manifest `name`.
- Project `.claude/settings.json` `enabledPlugins` turns a plugin on for collaborators but does not download it; each still runs `/plugin install` once.

Docs: https://code.claude.com/docs/en/plugins/manifest-reference.md, https://code.claude.com/docs/en/plugins/create-marketplace.md, https://code.claude.com/docs/en/plugins/install.md, https://code.claude.com/docs/en/hooks.md

## Open

- Confirm recommendation 1's custom-path check before building.
- Claude Code hooks are not wired for the `.claude/` install yet (`installations_for` skips the hook channel for Claude); the plugin's `HookInstallation` work covers both.
