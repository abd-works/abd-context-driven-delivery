# @toolset-manifest python -m tools manifest agent_skills.agent_skills:AgentSkills
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Deploy workspace toolsets as IDE skill shims; action kits as skills+commands."""
from __future__ import annotations

import ast
import json
from pathlib import Path

from primitives.actions.action import action
from focus._decorator import _default_filter_key
from tools.tool import tool, toolset
from tools.toolset_header import read_toolset_header

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STATE_FILE = Path(__file__).resolve().parent / ".deploy-state.json"

_SKIP_DIRS = frozenset({"__pycache__", "examples", "primitives"})
_WORKSPACE_SEARCH_DEPTH = 5


def _home() -> Path:
    """User home directory. Patchable in tests."""
    return Path.home()

_CHAIN_TOOLS = """\
If the chat names **one or more** context tools (for example `/stories /ddd /iterate`), run **each** named toolset **in that order** with the same action and fidelity. Do not pick only the first. If AskQuestion is needed, the user may select more than one — still run them in the order listed.
"""

_SHIM_TEMPLATE = """\
---
name: {skill_slug}
description: "{description}"
disable-model-invocation: true
---

# {class_name}

This skill **is** this context tool. Do not ask which context tool to run.

**Step 1 — Identify the action.**
Check whether an action was provided alongside this command (in the user message or chat context). If one is found, use it. If not, use the `AskQuestion` tool to let the user choose:

```
Question: "What action should {class_name} run?"
Options:
  - partition — index source material and extract chunks
  - grill — context-grounded Q&A
  - sketch — grill plus a persisted rough draft
  - generate — produce the formal artifact
  - document — describe existing code/tests/docs
  - iterate — generate one small slice at a time
  - validate — scan and report pass/fail
  - satisfy — validate, fix, validate again until clean
  - repair — root-cause and fix why the tool produced a violation
  - improve — log mistake, repair, capture regression
```

**Step 2 — Identify the fidelity.**
Check whether a fidelity was provided alongside this command (in the user message or chat context). If one is found, use it. If not, use the `AskQuestion` tool to let the user choose from this tool's available fidelities or from the CDD stage names (`discovery`, `specification`, `engineering`).

**Step 3 — Run the manifest and invoke.**
Load this tool's manifest:

```
{manifest_command}
```

Follow `response.instructions` before doing anything else. Write the request to
a YAML file (e.g. `_req.yaml`) and run:

```
python -m tools run _req.yaml
```

Delete the file after the call. Request format:

```yaml
toolset: {toolset_ref}
context:
  fidelity: <selected fidelity>
action: <selected action>
```

Read `examples/` before guessing any field shape.
"""

# Host lifecycle actions on BaseContextTool. Deployed as both skills and
# Cursor commands / VS Code prompts. Skill/command name matches the action.
# Do not run the peer kit; use the in-scope context tool's matching action
# (e.g. /cdd + /sketch → run the CDD toolset with action: sketch).
_HOST_ACTION_COMMANDS: tuple[str, ...] = (
    "partition",
    "grill",
    "sketch",
    "generate",
    "document",
    "iterate",
    "validate",
    "satisfy",
    "repair",
    "improve",
)

# Companion toolsets under context_tools/actions/ — not Base @actions; still get
# IDE skills + commands that run the companion in the current context-tool session.
_COMPANION_ACTION_COMMANDS: tuple[tuple[str, str, str], ...] = (
    # (command_slug, manifest_ref, class_name)
    ("echo", "echo.echo:Echoer", "Echoer"),
    ("handoff", "handoff.handoff:Handoff", "Handoff"),
)

# Package-slug skills that are not the action name — remove on deploy.
_STALE_ACTION_SKILL_SLUGS: tuple[str, ...] = (
    "grill-context",
    "workspace",
)

_ACTION_INVOKE_BODY = """\
Do not run this as its own toolset.

""" + _CHAIN_TOOLS + """
**Step 1 — Identify the context tool(s).**
Check whether one or more context tools are already in scope — passed in (path / session / toolset) or named in this chat. If one or more are found, use them. If none is found, use the `AskQuestion` tool to let the user choose:

```
Question: "Which context tool should run `{action}`?"
Options:
  - /cdd — orchestrate all child tools at one stage
  - /stories — who does what, in what sequence
  - /clean-engineering — module boundaries and OO design
  - /ux — navigation, screens, front end
  - /bdd — observable behavior and tests
  - /ddd — bounded contexts and domain building blocks
```

**Step 2 — Identify the fidelity.**
Check whether a fidelity was provided alongside this command (in the user message or chat context). If one is found, use it. If not, use the `AskQuestion` tool to let the user choose from the selected context tool's available fidelities (see the quick-reference table), or from the CDD stage names (`discovery`, `specification`, `engineering`).

**Step 3 — Run the action.**
For **each** selected context tool, in the order named, invoke with `action: {action}` and the chosen fidelity:

```yaml
toolset: <this context tool>
context:
  fidelity: <selected fidelity>
action: {action}
```

Follow that context-tool skill's instructions: run its manifest, obey `response.instructions`, then invoke via `_req.yaml` + `python -m tools run`. Then the next named tool. Do not skip remaining tools after the first. Read `examples/` before guessing field shape.
"""

_ACTION_SKILL_TEMPLATE = """\
---
name: {action}
description: "Run the in-scope context tool's {action} action."
disable-model-invocation: true
---

# {action}

{body}
"""

_CURSOR_ACTION_COMMAND_TEMPLATE = """\
# {action}

{body}
"""

_VSCODE_ACTION_PROMPT_TEMPLATE = """\
---
description: "Run the in-scope context tool's {action} action"
name: "{action}"
argument-hint: "Describe what to {action}"
agent: agent
---

# {action}

{body}
"""

_COMPANION_SKILL_TEMPLATE = """\
---
name: {command_name}
description: "Run companion {class_name} in the current context-tool session."
disable-model-invocation: true
---

# {class_name}

A context-tool skill/session is already in play. Run this companion toolset in
that frame (same path / session / workspace as the context tool):

```
python -m tools manifest {toolset_ref}
```

Follow `response.instructions`. Invoke via `_req.yaml` + `python -m tools run`:

```yaml
toolset: {toolset_ref}
context:
  path: <active context-tool path>
  session: <active session name>
action: <action from this companion's manifest>
```

Delete the request file after the call. Read `examples/` before guessing field shape.
"""

_CURSOR_COMPANION_COMMAND_TEMPLATE = """\
# {class_name}

A context-tool skill/session is already in play. Run this companion toolset in
that frame (same path / session / workspace as the context tool):

```
python -m tools manifest {toolset_ref}
```

Follow `response.instructions`. Invoke via `_req.yaml` + `python -m tools run`:

```yaml
toolset: {toolset_ref}
context:
  path: <active context-tool path>
  session: <active session name>
action: <action from this companion's manifest>
```

Delete the request file after the call. Read `examples/` before guessing field shape.
"""

_VSCODE_COMPANION_PROMPT_TEMPLATE = """\
---
description: "Run companion {class_name} in the current context-tool session"
name: "{command_name}"
argument-hint: "Describe what to do with {class_name}"
agent: agent
---

# {class_name}

A context-tool skill/session is already in play. Run this companion toolset in
that frame (same path / session / workspace as the context tool):

```
python -m tools manifest {toolset_ref}
```

Follow `response.instructions`. Invoke via `_req.yaml` + `python -m tools run`:

```yaml
toolset: {toolset_ref}
context:
  path: <active context-tool path>
  session: <active session name>
action: <action from this companion's manifest>
```

Delete the request file after the call. Read `examples/` before guessing field shape.
"""

# Fidelity slash commands — CDD stage names plus concrete fidelities.
# Each context tool resolves stage names via its ``fidelities`` table (e.g. Stories:
# discovery→story_map; CleanEngineering: specification→model). Concrete slugs
# (scaffold, story_map, …) are passed through unchanged.
_STAGE_FIDELITY_COMMANDS: tuple[tuple[str, str], ...] = (
    # (command_slug, fidelity value passed in context.fidelity)
    ("scaffold", "scaffold"),
    ("discovery", "discovery"),
    ("specification", "specification"),
    ("engineering", "engineering"),
    ("story_map", "story_map"),
    ("scenarios", "scenarios"),
    ("acceptance_tests", "acceptance_tests"),
    ("bounded_context", "bounded_context"),
    ("building_blocks", "building_blocks"),
    ("tactics", "tactics"),
)

_STAGE_FIDELITY_INVOKE_BODY = """\
Do not run this as its own toolset. This command sets the CDD stage to `{fidelity}`.

The context tool maps this stage name to its own concrete fidelity (Stories: discovery→story_map, specification→scenarios, engineering→acceptance_tests; CleanEngineering: discovery→modules, specification→model, engineering→code; and so on).

""" + _CHAIN_TOOLS + """
**Step 1 — Identify the context tool(s).**
Check whether one or more context tools are already in scope — passed in (path / session / toolset) or named in this chat. If one or more are found, use them. If none is found, use the `AskQuestion` tool to let the user choose:

```
Question: "Which context tool should work at the `{fidelity}` stage?"
Options:
  - /cdd — orchestrate all child tools at one stage
  - /stories — who does what, in what sequence
  - /clean-engineering — module boundaries and OO design
  - /ux — navigation, screens, front end
  - /bdd — observable behavior and tests
  - /ddd — bounded contexts and domain building blocks
```

**Step 2 — Identify the action.**
Check whether an action was provided alongside this command (in the user message or chat context). If one is found, use it. If not, use the `AskQuestion` tool to let the user choose:

```
Question: "What action should run at `{fidelity}`?"
Options:
  - partition — index source material and extract chunks
  - grill — context-grounded Q&A
  - sketch — grill plus a persisted rough draft
  - generate — produce the formal artifact
  - document — describe existing code/tests/docs
  - iterate — generate one small slice at a time
  - validate — scan and report pass/fail
  - satisfy — validate, fix, validate again until clean
  - repair — root-cause and fix why the tool produced a violation
  - improve — log mistake, repair, capture regression
```

**Step 3 — Run the action at this stage.**
For **each** selected context tool, in the order named, invoke with the chosen action and `{fidelity}` as fidelity:

```yaml
toolset: <this context tool>
context:
  fidelity: {fidelity}
action: <selected action>
```

Follow that context-tool skill's instructions: run its manifest, obey `response.instructions`, then invoke via `_req.yaml` + `python -m tools run`. Then the next named tool. Do not skip remaining tools after the first. Read `examples/` before guessing field shape.
"""

_CURSOR_STAGE_COMMAND_TEMPLATE = """\
# {stage}

{body}
"""

_VSCODE_STAGE_PROMPT_TEMPLATE = """\
---
description: "Set the in-scope context tool fidelity to CDD stage {stage}"
name: "{stage}"
argument-hint: "Optional action to run at {stage}"
agent: agent
---

# {stage}

{body}
"""

_CURSOR_COMMAND_TEMPLATE = """\
# {class_name} - {action} at {focus_value} fidelity

Run the manifest to load tools, actions, and instructions:

```
{manifest_command}
```

Follow `response.instructions` before doing anything else. Write the request YAML
to `_req.yaml`, then run:

```
python -m tools run _req.yaml
```

Delete the file after the call. Request format:

```yaml
toolset: {toolset_ref}
new:
  {filter_key}: {focus_value}
action: {action}
```
"""

_VSCODE_PROMPT_TEMPLATE = """\
---
description: "{class_name} - {action} at {focus_value} fidelity"
name: "{command_name}"
argument-hint: "Describe what to {action}"
agent: agent
---

# {class_name} - {action} at {focus_value} fidelity

Run the manifest to load tools, actions, and instructions:

```
{manifest_command}
```

Follow `response.instructions` before doing anything else. Write the request YAML
to `_req.yaml`, then run:

```
python -m tools run _req.yaml
```

Delete the file after the call. Request format:

```yaml
toolset: {toolset_ref}
new:
  {filter_key}: {focus_value}
action: {action}
```
"""


@toolset
class AgentSkills:
    """Deploy context-tool skills plus action skills/commands for Cursor and VS Code."""

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _skill_slug(self, module_dir_name: str) -> str:
        return module_dir_name.replace("_", "-")

    def _command_prefix(self, module_dir_name: str) -> str:
        return module_dir_name.split("_")[0]

    def _command_name(self, prefix: str, focus_value: str, action: str) -> str:
        return f"{prefix} {focus_value} {action}"

    def _toolset_ref(self, manifest_command: str) -> str:
        return manifest_command.strip().rsplit(" ", 1)[-1]

    def _decorator_name(self, node: ast.expr) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        if isinstance(node, ast.Call):
            return self._decorator_name(node.func)
        return None

    def _decorator_keywords(self, node: ast.expr) -> dict[str, ast.expr]:
        if isinstance(node, ast.Call):
            return {kw.arg: kw.value for kw in node.keywords if kw.arg}
        return {}

    def _str_constant(self, node: ast.expr) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    def _parse_focus_actions(self, py_file: Path) -> list[dict[str, str]]:
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        results: list[dict[str, str]] = []
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            for item in node.body:
                if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                has_action = False
                focus_group: str | None = None
                filter_key: str | None = None
                for dec in item.decorator_list:
                    name = self._decorator_name(dec)
                    if name == "action":
                        has_action = True
                    if name == "focus":
                        kws = self._decorator_keywords(dec)
                        fg = self._str_constant(kws.get("focus")) if "focus" in kws else None
                        if fg:
                            focus_group = fg
                        fk = self._str_constant(kws.get("filter_key")) if "filter_key" in kws else None
                        if fk:
                            filter_key = fk
                if has_action and focus_group:
                    results.append({
                        "action": item.name,
                        "focus_group": focus_group,
                        "filter_key": filter_key or _default_filter_key(focus_group),
                    })
        return results

    def _list_focus_values(self, module_dir: Path, focus_group: str) -> list[str]:
        """List filter values under a focus group - subdirs first, then legacy *.md stems."""
        group_dir = module_dir / focus_group
        if not group_dir.is_dir():
            return []
        values = {
            p.name
            for p in group_dir.iterdir()
            if p.is_dir() and not p.name.startswith((".", "_"))
        }
        values.update(p.stem for p in group_dir.glob("*.md") if p.is_file())
        return sorted(values)

    def _stale_focus_skill_slugs(self, command_prefix: str, focus_values: list[str]) -> list[str]:
        return [f"{command_prefix}-{value}" for value in focus_values]

    def _is_self_manifest(self, py_file: Path, manifest_command: str) -> bool:
        """Return True only if the manifest command refers to this file's own module."""
        try:
            module_class = manifest_command.strip().rsplit(" ", 1)[-1]
            module_path = module_class.split(":")[0]
            parts = module_path.split(".")
            search_roots = [_REPO_ROOT] + [
                _REPO_ROOT / name for name in ("primitives", "utilities", "context_tools", "context_tools/actions")
            ]
            for root in search_roots:
                search = root
                for part in parts[:-1]:
                    hyphenated = part.replace("_", "-")
                    candidate_dir = search / hyphenated
                    search = candidate_dir if candidate_dir.is_dir() else search / part
                candidate = search / f"{parts[-1]}.py"
                if candidate.resolve() == py_file.resolve():
                    return True
        except Exception:
            pass
        return False

    def _merge_hooks(self, existing: dict, new: dict) -> dict:
        """Merge new hooks config into existing without duplicating commands."""
        result = dict(existing)
        existing_hooks: dict = dict(result.get("hooks", {}))
        for event, entries in new.get("hooks", {}).items():
            if event not in existing_hooks:
                existing_hooks[event] = list(entries)
            else:
                present_cmds = {e.get("command") for e in existing_hooks[event]}
                for entry in entries:
                    if entry.get("command") not in present_cmds:
                        existing_hooks[event] = existing_hooks[event] + [entry]
        result["hooks"] = existing_hooks
        return result

    def _actions_root(self) -> Path:
        return _REPO_ROOT / "context_tools" / "actions"

    def _is_under_actions(self, path: Path) -> bool:
        """True when path lives under context_tools/actions/ (peer action kits)."""
        for actions_form in self._path_variants(self._actions_root()):
            for path_form in self._path_variants(path):
                try:
                    path_form.relative_to(actions_form)
                    return True
                except ValueError:
                    continue
        return False

    def _should_skip(self, path: Path) -> bool:
        try:
            relative = path.relative_to(_REPO_ROOT)
        except ValueError:
            return True
        if len(relative.parts) > 4:
            return True
        for part in relative.parts:
            if part in _SKIP_DIRS or part.startswith("_"):
                return True
        name = path.name
        return name.endswith(("_spec.py", "_agent_spec.py", "_ground_truth.py"))

    def _enrich_toolset_entry(self, entry: dict) -> dict:
        py_file = Path(entry["file_path"])
        module_dir = py_file.parent
        focus_actions = self._parse_focus_actions(py_file)
        shortcuts: list[dict] = []
        prefix = self._command_prefix(entry["module_dir"])
        for fa in focus_actions:
            values = self._list_focus_values(module_dir, fa["focus_group"])
            for value in values:
                shortcuts.append({
                    "action": fa["action"],
                    "focus_group": fa["focus_group"],
                    "filter_key": fa["filter_key"],
                    "focus_value": value,
                    "command_name": self._command_name(prefix, value, fa["action"]),
                })
        enriched = dict(entry)
        enriched["skill_slug"] = self._skill_slug(entry["module_dir"])
        enriched["command_prefix"] = prefix
        enriched["toolset_ref"] = self._toolset_ref(entry["manifest_command"])
        enriched["focus_shortcuts"] = shortcuts
        enriched["stale_focus_skill_slugs"] = self._stale_focus_skill_slugs(
            prefix,
            sorted({s["focus_value"] for s in shortcuts}),
        )
        return enriched

    def _path_variants(self, path: Path) -> list[Path]:
        """Return absolute and resolve() forms when they differ (junction-aware)."""
        variants: list[Path] = []
        seen: set[Path] = set()
        for form in (path.absolute(), path.resolve()):
            if form not in seen:
                seen.add(form)
                variants.append(form)
        return variants

    def _iter_workspace_files(self) -> list[Path]:
        """Find nearby *.code-workspace files by walking ancestors and siblings.

        Starts from the repo root and the process cwd. Keeps both absolute and
        resolve() forms so a junction checkout (c:\\dev -> OneDrive) still
        discovers sibling workspaces like paradise-mobile/.
        """
        found: list[Path] = []
        seen: set[Path] = set()

        def _add(ws: Path) -> None:
            resolved = ws.resolve()
            if resolved not in seen:
                seen.add(resolved)
                found.append(resolved)

        starts: list[Path] = []
        start_seen: set[Path] = set()
        for raw in [_REPO_ROOT, Path.cwd()]:
            try:
                for form in self._path_variants(raw):
                    if form not in start_seen:
                        start_seen.add(form)
                        starts.append(form)
            except OSError:
                continue

        for start in starts:
            current = start
            for _ in range(_WORKSPACE_SEARCH_DEPTH + 1):
                for ws in sorted(current.glob("*.code-workspace")):
                    _add(ws)
                # Cousin layouts: parent/sibling/*.code-workspace (e.g. paradise-mobile/)
                if current.parent != current:
                    try:
                        children = sorted(
                            p for p in current.iterdir()
                            if p.is_dir() and not p.name.startswith(".")
                        )
                    except OSError:
                        children = []
                    for child in children:
                        for ws in sorted(child.glob("*.code-workspace")):
                            _add(ws)
                if current.parent == current:
                    break
                current = current.parent
        return found

    def _resolve_workspace_folders(self, workspace_file: Path) -> list[Path]:
        """Resolve absolute folder paths from a VS Code/Cursor .code-workspace file."""
        data = json.loads(workspace_file.read_text(encoding="utf-8"))
        base = workspace_file.parent
        folders: list[Path] = []
        for entry in data.get("folders", []):
            raw = entry.get("path")
            if not raw:
                continue
            path = Path(raw)
            folders.append(path.resolve() if path.is_absolute() else (base / path).resolve())
        return folders

    def _path_covers_repo(self, folder: Path, repo: Path) -> bool:
        try:
            if folder == repo or repo.is_relative_to(folder) or folder.is_relative_to(repo):
                return True
        except (ValueError, OSError):
            pass
        # Same checkout exposed via two roots (junction / OneDrive sync path)
        try:
            marker = Path("utilities") / "agent_skills" / "agent_skills.py"
            folder_marker = folder / marker
            repo_marker = repo / marker
            if folder_marker.is_file() and repo_marker.is_file():
                return folder_marker.samefile(repo_marker)
        except OSError:
            pass
        return False

    def _repo_identities(self) -> list[Path]:
        """Repo roots that represent this checkout (module path + cwd checkout).

        Keeps absolute and resolve() forms so junction checkouts match workspace
        folder entries that still point at the logical c:\\dev path.
        """
        identities: list[Path] = []
        seen: set[Path] = set()
        marker = Path("utilities") / "agent_skills" / "agent_skills.py"

        def _add(path: Path) -> None:
            for form in self._path_variants(path):
                if form not in seen:
                    seen.add(form)
                    identities.append(form)

        _add(_REPO_ROOT)
        repo_marker = _REPO_ROOT / marker
        try:
            cwd = Path.cwd()
        except OSError:
            return identities
        for base in self._path_variants(cwd):
            for candidate in [base, *base.parents]:
                candidate_marker = candidate / marker
                if not candidate_marker.is_file():
                    continue
                try:
                    if not repo_marker.is_file() or not candidate_marker.samefile(repo_marker):
                        break
                except OSError:
                    break
                _add(candidate)
                break
        return identities

    def _find_multi_folder_workspaces(self) -> list[dict]:
        """Return every multi-folder workspace that includes this repo."""
        repos = self._repo_identities()
        matches: list[dict] = []
        for ws_file in self._iter_workspace_files():
            try:
                folders = self._resolve_workspace_folders(ws_file)
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                continue
            if len(folders) < 2:
                continue
            if any(
                self._path_covers_repo(folder, repo)
                for folder in folders
                for repo in repos
            ):
                matches.append({
                    "workspace_file": str(ws_file),
                    "folders": [str(f) for f in folders],
                    "shared_root": str(ws_file.parent.resolve()),
                })
        return matches

    def _find_multi_folder_workspace(self) -> dict | None:
        """Return the richest multi-folder workspace that includes this repo.

        Prefers the match with the most folders (typical multi-root product
        workspace over a smaller sibling workspace file).
        """
        matches = self._find_multi_folder_workspaces()
        if not matches:
            return None
        return max(matches, key=lambda m: len(m["folders"]))

    def _ide_config_roots(self, ide: str) -> list[Path]:
        """IDE config roots (.cursor or .github) where shims should be written.

        Always includes the repo root. For Cursor multi-folder workspaces, also
        includes ~/.cursor (user-level, available in every project) and each
        matching .code-workspace parent's .cursor (shared sibling layouts).
        """
        name = ".cursor" if ide == "cursor" else ".github"
        roots: list[Path] = [_REPO_ROOT / name]
        if ide == "cursor":
            multis = self._find_multi_folder_workspaces()
            if multis:
                roots.append(_home() / ".cursor")
                for multi in multis:
                    roots.append(Path(multi["shared_root"]) / ".cursor")
        deduped: list[Path] = []
        seen: set[Path] = set()
        for root in roots:
            resolved = root.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            deduped.append(root)
        return deduped

    # ------------------------------------------------------------------ #
    # Tools                                                                #
    # ------------------------------------------------------------------ #

    @tool
    def resolve_deploy_targets(self, ide: str = "cursor") -> str:
        """Resolve where skill shims will be written for the given IDE.
        Returns JSON with ide_config_roots, multi_folder_workspaces, and primary workspace."""
        return json.dumps(
            {
                "ide": ide,
                "repo_root": str(_REPO_ROOT),
                "cwd": str(Path.cwd()),
                "repo_identities": [str(p) for p in self._repo_identities()],
                "workspace_files": [str(p) for p in self._iter_workspace_files()],
                "multi_folder_workspaces": self._find_multi_folder_workspaces(),
                "primary_multi_folder_workspace": self._find_multi_folder_workspace(),
                "ide_config_roots": [str(p) for p in self._ide_config_roots(ide)],
            },
            indent=2,
        )

    @tool
    def scan_toolsets(self) -> str:
        """Scan the workspace for Python toolset files. Returns a JSON array of
        {module_dir, skill_slug, manifest_command, class_name, description, file_path,
        focus_shortcuts, stale_focus_skill_slugs} objects.
        Skips _retired, examples, primitives, __pycache__, spec, and nested files."""
        results: list[dict] = []
        seen: set[str] = set()
        for py_file in sorted(_REPO_ROOT.rglob("*.py")):
            if self._should_skip(py_file):
                continue
            try:
                header = read_toolset_header(py_file)
            except ValueError:
                continue
            if "{" in header.manifest_command:
                continue
            if not self._is_self_manifest(py_file, header.manifest_command):
                continue
            module_dir = py_file.parent.name
            if module_dir in seen:
                continue
            seen.add(module_dir)
            class_name = header.manifest_command.rsplit(":", 1)[-1].strip()
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
                module_doc = (ast.get_docstring(tree) or "").splitlines()[0].strip()
            except Exception:
                module_doc = ""
            entry = {
                "module_dir": module_dir,
                "manifest_command": header.manifest_command,
                "class_name": class_name,
                "description": module_doc,
                "file_path": str(py_file),
            }
            results.append(self._enrich_toolset_entry(entry))
        return json.dumps(results, indent=2)

    @tool
    def write_skill_shim(
        self,
        skill_slug: str,
        manifest_command: str,
        class_name: str,
        description: str,
        ide: str,
    ) -> str:
        """Write a skill shim SKILL.md with a hardcoded manifest call.
        ide=cursor -> .cursor/skills/{skill_slug}/SKILL.md
        ide=vscode -> .github/skills/{skill_slug}/SKILL.md
        For Cursor multi-folder workspaces, also writes to ~/.cursor/skills and
        the .code-workspace parent .cursor/skills.
        Returns the absolute path of the primary (repo) written file."""
        safe_description = description.replace('"', "'")
        content = _SHIM_TEMPLATE.format(
            skill_slug=skill_slug,
            class_name=class_name,
            manifest_command=manifest_command,
            toolset_ref=self._toolset_ref(manifest_command),
            description=safe_description,
        )
        written: list[str] = []
        for ide_root in self._ide_config_roots(ide):
            skill_dir = ide_root / "skills" / skill_slug
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(content, encoding="utf-8")
            written.append(str(skill_md))
        return written[0]

    @tool
    def write_action_command(self, action: str, ide: str) -> str:
        """Write a host-action command/prompt composable with a context-tool skill.
        ide=cursor -> .cursor/commands/{action}.md
        ide=vscode -> .github/prompts/{action}.prompt.md
        For Cursor multi-folder workspaces, also writes to every deploy root.
        Returns the absolute path of the primary (repo) written file."""
        written: list[str] = []
        body = _ACTION_INVOKE_BODY.format(action=action)
        for ide_root in self._ide_config_roots(ide):
            if ide == "cursor":
                target_dir = ide_root / "commands"
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / f"{action}.md"
                content = _CURSOR_ACTION_COMMAND_TEMPLATE.format(action=action, body=body)
            else:
                target_dir = ide_root / "prompts"
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / f"{action}.prompt.md"
                content = _VSCODE_ACTION_PROMPT_TEMPLATE.format(action=action, body=body)
            target.write_text(content, encoding="utf-8")
            written.append(str(target))
        return written[0]

    @tool
    def write_action_skill_shim(self, action: str, ide: str) -> str:
        """Write a skill shim that routes to the in-scope context tool's matching action.
        Do not run the action kit as its own toolset.
        ide=cursor -> .cursor/skills/{action}/SKILL.md
        ide=vscode -> .github/skills/{action}/SKILL.md
        For Cursor multi-folder workspaces, also writes to every deploy root.
        Returns the absolute path of the primary (repo) written file."""
        body = _ACTION_INVOKE_BODY.format(action=action)
        content = _ACTION_SKILL_TEMPLATE.format(action=action, body=body)
        written: list[str] = []
        for ide_root in self._ide_config_roots(ide):
            skill_dir = ide_root / "skills" / action
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(content, encoding="utf-8")
            written.append(str(skill_md))
        return written[0]

    @tool
    def write_companion_skill_shim(
        self,
        command_name: str,
        toolset_ref: str,
        class_name: str,
        ide: str,
    ) -> str:
        """Write a companion skill shim (echo/handoff) for the current context-tool session.
        ide=cursor -> .cursor/skills/{command_name}/SKILL.md
        ide=vscode -> .github/skills/{command_name}/SKILL.md
        Returns the absolute path of the primary (repo) written file."""
        content = _COMPANION_SKILL_TEMPLATE.format(
            command_name=command_name,
            class_name=class_name,
            toolset_ref=toolset_ref,
        )
        written: list[str] = []
        for ide_root in self._ide_config_roots(ide):
            skill_dir = ide_root / "skills" / command_name
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(content, encoding="utf-8")
            written.append(str(skill_md))
        return written[0]

    @tool
    def write_companion_command(
        self,
        command_name: str,
        toolset_ref: str,
        class_name: str,
        ide: str,
    ) -> str:
        """Write a companion toolset command/prompt for echo/handoff-style kits.
        ide=cursor -> .cursor/commands/{command_name}.md
        ide=vscode -> .github/prompts/{command_name}.prompt.md
        Returns the absolute path of the primary (repo) written file."""
        written: list[str] = []
        for ide_root in self._ide_config_roots(ide):
            if ide == "cursor":
                target_dir = ide_root / "commands"
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / f"{command_name}.md"
                content = _CURSOR_COMPANION_COMMAND_TEMPLATE.format(
                    class_name=class_name,
                    toolset_ref=toolset_ref,
                )
            else:
                target_dir = ide_root / "prompts"
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / f"{command_name}.prompt.md"
                content = _VSCODE_COMPANION_PROMPT_TEMPLATE.format(
                    class_name=class_name,
                    toolset_ref=toolset_ref,
                    command_name=command_name,
                )
            target.write_text(content, encoding="utf-8")
            written.append(str(target))
        return written[0]

    @tool
    def write_stage_fidelity_command(self, stage: str, fidelity: str, ide: str) -> str:
        """Write a fidelity command/prompt (CDD stages and concrete fidelities).
        Sets context.fidelity on the in-scope context tool; that tool maps stage
        names to concrete fidelities via BaseContextTool.resolve_fidelity.
        ide=cursor -> .cursor/commands/{stage}.md
        ide=vscode -> .github/prompts/{stage}.prompt.md
        Returns the absolute path of the primary (repo) written file."""
        written: list[str] = []
        body = _STAGE_FIDELITY_INVOKE_BODY.format(fidelity=fidelity)
        for ide_root in self._ide_config_roots(ide):
            if ide == "cursor":
                target_dir = ide_root / "commands"
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / f"{stage}.md"
                content = _CURSOR_STAGE_COMMAND_TEMPLATE.format(stage=stage, body=body)
            else:
                target_dir = ide_root / "prompts"
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / f"{stage}.prompt.md"
                content = _VSCODE_STAGE_PROMPT_TEMPLATE.format(stage=stage, body=body)
            target.write_text(content, encoding="utf-8")
            written.append(str(target))
        return written[0]

    @tool
    def write_focus_shortcut(
        self,
        command_name: str,
        manifest_command: str,
        toolset_ref: str,
        class_name: str,
        action: str,
        filter_key: str,
        focus_value: str,
        ide: str,
    ) -> str:
        """Write a focus shortcut for an @focus action.
        ide=cursor -> .cursor/commands/{command_name}.md
        ide=vscode -> .github/prompts/{command_name}.prompt.md
        Returns the absolute path of the primary (repo) written file."""
        written: list[str] = []
        for ide_root in self._ide_config_roots(ide):
            if ide == "cursor":
                target_dir = ide_root / "commands"
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / f"{command_name}.md"
                content = _CURSOR_COMMAND_TEMPLATE.format(
                    class_name=class_name,
                    action=action,
                    focus_value=focus_value,
                    manifest_command=manifest_command,
                    toolset_ref=toolset_ref,
                    filter_key=filter_key,
                )
            else:
                target_dir = ide_root / "prompts"
                target_dir.mkdir(parents=True, exist_ok=True)
                safe_description = f"{class_name} - {action} at {focus_value} fidelity".replace('"', "'")
                target = target_dir / f"{command_name}.prompt.md"
                content = _VSCODE_PROMPT_TEMPLATE.format(
                    class_name=class_name,
                    action=action,
                    focus_value=focus_value,
                    manifest_command=manifest_command,
                    toolset_ref=toolset_ref,
                    filter_key=filter_key,
                    command_name=command_name,
                    description=safe_description,
                )
            target.write_text(content, encoding="utf-8")
            written.append(str(target))
        return written[0]

    @tool
    def remove_focus_shortcut(self, command_name: str, ide: str) -> str:
        """Remove a deployed focus shortcut.
        ide=cursor -> .cursor/commands/{command_name}.md
        ide=vscode -> .github/prompts/{command_name}.prompt.md
        Removes from every configured deploy root. Returns a summary."""
        results: list[str] = []
        for ide_root in self._ide_config_roots(ide):
            if ide == "cursor":
                target = ide_root / "commands" / f"{command_name}.md"
            else:
                target = ide_root / "prompts" / f"{command_name}.prompt.md"
            if not target.exists():
                results.append(f"not found: {target}")
                continue
            target.unlink()
            results.append(f"removed: {target}")
        return "\n".join(results)

    @tool
    def save_state(
        self,
        ide: str,
        name_filter: str,
        deployed_skills: str,
        deployed_commands: str = "[]",
    ) -> str:
        """Persist last deploy parameters to .deploy-state.json next to this file.
        deployed_skills is a JSON array of skill_slug strings.
        deployed_commands is a JSON array of command_name strings.
        Also stores resolved deploy_roots for multi-folder cleanup.
        Returns the state file path."""
        state = {
            "ide": ide,
            "name_filter": name_filter,
            "deployed": json.loads(deployed_skills),
            "deployed_commands": json.loads(deployed_commands),
            "deploy_roots": [str(r) for r in self._ide_config_roots(ide)],
        }
        multi = self._find_multi_folder_workspace()
        if multi:
            state["multi_folder_workspace"] = multi
        multis = self._find_multi_folder_workspaces()
        if multis:
            state["multi_folder_workspaces"] = multis
        _STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return str(_STATE_FILE)

    @tool
    def load_state(self) -> str:
        """Load last deploy parameters from .deploy-state.json.
        Returns JSON with {ide, name_filter, deployed, deployed_commands} or '{}' if not found."""
        if not _STATE_FILE.exists():
            return "{}"
        return _STATE_FILE.read_text(encoding="utf-8")

    @tool
    def deploy_hooks(self, ide: str) -> str:
        """Deploy primitives/tools/hooks/manifest-gate.json to the IDE hooks location.
        ide=cursor -> merges into .cursor/hooks.json (creates if absent).
        ide=vscode -> copies to .github/hooks/manifest-gate.json.
        For Cursor multi-folder workspaces, merges into every deploy root.
        Returns the paths written, or 'not found: <path>' if the source is missing."""
        source = _REPO_ROOT / "primitives" / "tools" / "hooks" / "manifest-gate.json"
        if not source.exists():
            return f"not found: {source}"
        gate_config = json.loads(source.read_text(encoding="utf-8"))
        written: list[str] = []
        for ide_root in self._ide_config_roots(ide):
            if ide == "cursor":
                target = ide_root / "hooks.json"
                target.parent.mkdir(parents=True, exist_ok=True)
                existing = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
                merged = self._merge_hooks(existing, gate_config)
                target.write_text(json.dumps(merged, indent=2), encoding="utf-8")
                written.append(str(target))
            else:
                target = ide_root / "hooks" / "manifest-gate.json"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
                written.append(str(target))
        return "\n".join(written)

    @tool
    def remove_skill_shim(self, skill_slug: str, ide: str) -> str:
        """Remove .cursor/skills/{skill_slug}/ (ide=cursor) or .github/skills/{skill_slug}/ (ide=vscode).
        Removes from every configured deploy root. Returns a summary."""
        import shutil
        import subprocess
        results: list[str] = []
        for ide_root in self._ide_config_roots(ide):
            skill_dir = ide_root / "skills" / skill_slug
            if not skill_dir.exists():
                results.append(f"not found: {skill_dir}")
                continue
            try:
                shutil.rmtree(skill_dir)
            except OSError:
                subprocess.run(
                    ["powershell", "-Command", f"Remove-Item -LiteralPath '{skill_dir}' -Recurse -Force"],
                    check=True,
                )
            results.append(f"removed: {skill_dir}")
        return "\n".join(results)

    def _deploy_entries(self, entries: list[dict], ide: str) -> tuple[list[str], list[str]]:
        deployed_skills: list[str] = []
        deployed_commands: list[str] = []
        for entry in entries:
            if self._is_under_actions(Path(entry["file_path"])):
                # Action kits get host-action / companion shims below, not a kit-manifest skill.
                self.remove_skill_shim(skill_slug=entry["skill_slug"], ide=ide)
                continue
            self.write_skill_shim(
                skill_slug=entry["skill_slug"],
                manifest_command=entry["manifest_command"],
                class_name=entry["class_name"],
                description=entry["description"],
                ide=ide,
            )
            deployed_skills.append(entry["skill_slug"])
            for stale_slug in entry.get("stale_focus_skill_slugs", []):
                self.remove_skill_shim(skill_slug=stale_slug, ide=ide)
            # Drop legacy per-focus×action commands/prompts - not a good IDE fit.
            for shortcut in entry.get("focus_shortcuts", []):
                self.remove_focus_shortcut(
                    command_name=shortcut["command_name"],
                    ide=ide,
                )
        for stale_slug in _STALE_ACTION_SKILL_SLUGS:
            self.remove_skill_shim(skill_slug=stale_slug, ide=ide)
        for action_name in _HOST_ACTION_COMMANDS:
            self.write_action_skill_shim(action=action_name, ide=ide)
            self.write_action_command(action=action_name, ide=ide)
            deployed_skills.append(action_name)
            deployed_commands.append(action_name)
        for stage, fidelity in _STAGE_FIDELITY_COMMANDS:
            self.write_stage_fidelity_command(stage=stage, fidelity=fidelity, ide=ide)
            deployed_commands.append(stage)
        for command_name, toolset_ref, class_name in _COMPANION_ACTION_COMMANDS:
            self.write_companion_skill_shim(
                command_name=command_name,
                toolset_ref=toolset_ref,
                class_name=class_name,
                ide=ide,
            )
            self.write_companion_command(
                command_name=command_name,
                toolset_ref=toolset_ref,
                class_name=class_name,
                ide=ide,
            )
            deployed_skills.append(command_name)
            deployed_commands.append(command_name)
        return deployed_skills, deployed_commands

    @tool
    def deploy_filtered_toolsets(self, entries_json: str, ide: str) -> str:
        """Write skill shims, action skills, and action commands for confirmed scan entries.
        entries_json is a JSON array of scan_toolsets objects (already filtered).
        Returns a summary of deployed skill slugs and command names."""
        entries = json.loads(entries_json)
        deployed_skills, deployed_commands = self._deploy_entries(entries, ide=ide)
        return (
            f"Deployed {len(deployed_skills)} skill(s): {', '.join(deployed_skills)}. "
            f"Deployed {len(deployed_commands)} command(s): {', '.join(deployed_commands)}."
        )

    @action
    def deploy_tools_as_skills(self, name_filter: str, ide: str) -> str:
        """Deploy workspace toolsets as IDE shims. ide={ide}, filter={name_filter}."""
        """Step 1 - If ide is empty, ask: Which IDE? cursor (Recommended) / vscode."""
        """Step 2 - If name_filter is empty, ask: Deploy all toolsets (Recommended) / enter a module_dir substring."""
        self.scan_toolsets()
        """Step 3 - Apply name_filter: keep entries whose module_dir or skill_slug contains it; skip if filter is empty (= all)."""
        """Step 4 - Present the filtered list of skills and ask the user to confirm before writing."""
        """Step 5 - Call deploy_filtered_toolsets with the confirmed entries as JSON and ide. That writes: context-tool skill shims; host-action skill shims (do not run the kit — use the in-scope context tool's matching action); host-action Cursor commands / VS Code prompts with the same text; CDD stage-fidelity commands (discovery / specification / engineering); companion skill+command shims. Cursor multi-folder: every ide_config_root. Removes stale package-slug action skills (grill-context, workspace)."""
        self.deploy_filtered_toolsets()
        """Step 6 - Call deploy_hooks(ide) to install hooks/manifest-gate.json into the IDE hooks location."""
        self.deploy_hooks()
        """Step 7 - Call save_state with ide, name_filter, deployed skill_slugs, and deployed action command names."""
        self.save_state()
        return (
            "IDE skill shims written. Context-tool action skills and commands/prompts written. "
            "Hooks deployed. State saved. Reload the IDE to pick them up."
        )

    @tool
    def deploy_again(self) -> str:
        """Re-deploy using the exact parameters saved by the last deploy_tools_as_skills run.
        No questions asked. Scans for new toolsets, writes all shims, saves updated state.
        Returns a summary of deployed skill slugs."""
        raw = self.load_state()
        state = json.loads(raw)
        if not state:
            return "No saved deploy parameters. Run deploy_tools_as_skills first."
        ide: str = state.get("ide", "cursor")
        name_filter: str = state.get("name_filter", "")
        # Remove any previously deployed per-arg commands before re-deploy.
        for command_name in state.get("deployed_commands", []):
            self.remove_focus_shortcut(command_name=command_name, ide=ide)
        all_toolsets: list[dict] = json.loads(self.scan_toolsets())
        matched = [
            t for t in all_toolsets
            if not name_filter
            or name_filter in t["module_dir"]
            or name_filter in t["skill_slug"]
        ]
        deployed_skills, deployed_commands = self._deploy_entries(matched, ide=ide)
        self.deploy_hooks(ide=ide)
        self.save_state(
            ide=ide,
            name_filter=name_filter,
            deployed_skills=json.dumps(deployed_skills),
            deployed_commands=json.dumps(deployed_commands),
        )
        roots = ", ".join(str(r) for r in self._ide_config_roots(ide))
        multi = self._find_multi_folder_workspace()
        multi_note = (
            f" Multi-folder workspace detected ({Path(multi['workspace_file']).name})."
            if multi and ide == "cursor"
            else ""
        )
        return (
            f"Re-deployed {len(deployed_skills)} skill(s): {', '.join(deployed_skills)}. "
            f"Commands: {', '.join(deployed_commands)}."
            f"{multi_note} Roots: {roots}."
        )

    @tool
    def clean_skills(self) -> str:
        """Remove all deployed skill shims and focus shortcuts from both IDE locations.
        No questions asked. Uses saved state; falls back to scan_toolsets.
        Returns a summary of removed paths."""
        raw = self.load_state()
        state = json.loads(raw)
        if state and state.get("deployed"):
            skill_slugs: list[str] = state["deployed"]
            command_names: list[str] = state.get("deployed_commands", [])
        else:
            all_toolsets: list[dict] = json.loads(self.scan_toolsets())
            skill_slugs = [t["skill_slug"] for t in all_toolsets]
            command_names = [
                s["command_name"]
                for t in all_toolsets
                for s in t.get("focus_shortcuts", [])
            ]
        results: list[str] = []
        for skill_slug in skill_slugs:
            for ide in ("cursor", "vscode"):
                results.append(self.remove_skill_shim(skill_slug=skill_slug, ide=ide))
        for command_name in command_names:
            for ide in ("cursor", "vscode"):
                results.append(self.remove_focus_shortcut(command_name=command_name, ide=ide))
        return "\n".join(results)
