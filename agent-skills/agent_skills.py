# @toolset-manifest python -m tools manifest agent_skills.agent_skills:AgentSkills
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Deploy workspace toolsets as IDE shims — one skill per toolset."""
from __future__ import annotations

import ast
import json
from pathlib import Path

from action.action import action
from focus._decorator import _default_filter_key
from tools.tool import tool, toolset
from tools.toolset_header import read_toolset_header

_REPO_ROOT = Path(__file__).resolve().parent.parent
_STATE_FILE = Path(__file__).resolve().parent / ".deploy-state.json"

_SKIP_DIRS = frozenset({"__pycache__", "examples", "primitives"})

_SHIM_TEMPLATE = """\
---
name: {skill_slug}
description: "{description}"
disable-model-invocation: true
---

# {class_name}

Run the manifest to load tools, actions, and instructions:

```
{manifest_command}
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
"""

_CURSOR_COMMAND_TEMPLATE = """\
# {class_name} — {action} at {focus_value} fidelity

Run the manifest to load tools, actions, and instructions:

```
{manifest_command}
```

Follow `response.instructions` before doing anything else. Invoke via:

```
python -m tools run -
```
```yaml
toolset: {toolset_ref}
new:
  {filter_key}: {focus_value}
action: {action}
```
"""

_VSCODE_PROMPT_TEMPLATE = """\
---
description: "{class_name} — {action} at {focus_value} fidelity"
name: "{command_name}"
argument-hint: "Describe what to {action}"
agent: agent
---

# {class_name} — {action} at {focus_value} fidelity

Run the manifest to load tools, actions, and instructions:

```
{manifest_command}
```

Follow `response.instructions` before doing anything else. Invoke via:

```yaml
toolset: {toolset_ref}
new:
  {filter_key}: {focus_value}
action: {action}
```
"""


def _skill_slug(module_dir_name: str) -> str:
    return module_dir_name.replace("_", "-")


def _command_prefix(module_dir_name: str) -> str:
    return module_dir_name.split("_")[0]


def _command_name(prefix: str, focus_value: str, action: str) -> str:
    return f"{prefix} {focus_value} {action}"


def _toolset_ref(manifest_command: str) -> str:
    return manifest_command.strip().rsplit(" ", 1)[-1]


def _decorator_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return None


def _decorator_keywords(node: ast.expr) -> dict[str, ast.expr]:
    if isinstance(node, ast.Call):
        return {kw.arg: kw.value for kw in node.keywords if kw.arg}
    return {}


def _str_constant(node: ast.expr) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _parse_focus_actions(py_file: Path) -> list[dict[str, str]]:
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
                name = _decorator_name(dec)
                if name == "action":
                    has_action = True
                if name == "focus":
                    kws = _decorator_keywords(dec)
                    fg = _str_constant(kws.get("focus")) if "focus" in kws else None
                    if fg:
                        focus_group = fg
                    fk = _str_constant(kws.get("filter_key")) if "filter_key" in kws else None
                    if fk:
                        filter_key = fk
            if has_action and focus_group:
                results.append({
                    "action": item.name,
                    "focus_group": focus_group,
                    "filter_key": filter_key or _default_filter_key(focus_group),
                })
    return results


def _list_focus_values(module_dir: Path, focus_group: str) -> list[str]:
    """List filter values under a focus group — subdirs first, then legacy *.md stems."""
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


def _stale_focus_skill_slugs(command_prefix: str, focus_values: list[str]) -> list[str]:
    return [f"{command_prefix}-{value}" for value in focus_values]


def _is_self_manifest(py_file: Path, manifest_command: str) -> bool:
    """Return True only if the manifest command refers to this file's own module."""
    try:
        module_class = manifest_command.strip().rsplit(" ", 1)[-1]
        module_path = module_class.split(":")[0]
        parts = module_path.split(".")
        for first in (parts[0], parts[0].replace("_", "-")):
            candidate = _REPO_ROOT.joinpath(first, *parts[1:]).with_suffix(".py")
            if candidate.resolve() == py_file.resolve():
                return True
    except Exception:
        pass
    return False


def _merge_hooks(existing: dict, new: dict) -> dict:
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


def _should_skip(path: Path) -> bool:
    try:
        relative = path.relative_to(_REPO_ROOT)
    except ValueError:
        return True
    if len(relative.parts) > 2:
        return True
    for part in relative.parts:
        if part in _SKIP_DIRS or part.startswith("_"):
            return True
    name = path.name
    return name.endswith(("_spec.py", "_agent_spec.py", "_ground_truth.py"))


def _enrich_toolset_entry(entry: dict) -> dict:
    py_file = Path(entry["file_path"])
    module_dir = py_file.parent
    focus_actions = _parse_focus_actions(py_file)
    shortcuts: list[dict] = []
    prefix = _command_prefix(entry["module_dir"])
    for fa in focus_actions:
        values = _list_focus_values(module_dir, fa["focus_group"])
        for value in values:
            shortcuts.append({
                "action": fa["action"],
                "focus_group": fa["focus_group"],
                "filter_key": fa["filter_key"],
                "focus_value": value,
                "command_name": _command_name(prefix, value, fa["action"]),
            })
    enriched = dict(entry)
    enriched["skill_slug"] = _skill_slug(entry["module_dir"])
    enriched["command_prefix"] = prefix
    enriched["toolset_ref"] = _toolset_ref(entry["manifest_command"])
    enriched["focus_shortcuts"] = shortcuts
    enriched["stale_focus_skill_slugs"] = _stale_focus_skill_slugs(
        prefix,
        sorted({s["focus_value"] for s in shortcuts}),
    )
    return enriched


@toolset
class AgentSkills:
    """Deploy workspace toolsets — one skill per toolset."""

    @tool
    def scan_toolsets(self) -> str:
        """Scan the workspace for Python toolset files. Returns a JSON array of
        {module_dir, skill_slug, manifest_command, class_name, description, file_path,
        focus_shortcuts, stale_focus_skill_slugs} objects.
        Skips _retired, examples, primitives, __pycache__, spec, and nested files."""
        results: list[dict] = []
        seen: set[str] = set()
        for py_file in sorted(_REPO_ROOT.rglob("*.py")):
            if _should_skip(py_file):
                continue
            try:
                header = read_toolset_header(py_file)
            except ValueError:
                continue
            if "{" in header.manifest_command:
                continue
            if not _is_self_manifest(py_file, header.manifest_command):
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
            results.append(_enrich_toolset_entry(entry))
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
        ide=cursor → .cursor/skills/{skill_slug}/SKILL.md
        ide=vscode → .github/skills/{skill_slug}/SKILL.md
        Returns the absolute path of the written file."""
        base = ".cursor" if ide == "cursor" else ".github"
        skill_dir = _REPO_ROOT / base / "skills" / skill_slug
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_md = skill_dir / "SKILL.md"
        safe_description = description.replace('"', "'")
        content = _SHIM_TEMPLATE.format(
            skill_slug=skill_slug,
            class_name=class_name,
            manifest_command=manifest_command,
            description=safe_description,
        )
        skill_md.write_text(content, encoding="utf-8")
        return str(skill_md)

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
        ide=cursor → .cursor/commands/{command_name}.md
        ide=vscode → .github/prompts/{command_name}.prompt.md
        Returns the absolute path of the written file."""
        if ide == "cursor":
            target_dir = _REPO_ROOT / ".cursor" / "commands"
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
            target_dir = _REPO_ROOT / ".github" / "prompts"
            target_dir.mkdir(parents=True, exist_ok=True)
            safe_description = f"{class_name} — {action} at {focus_value} fidelity".replace('"', "'")
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
        return str(target)

    @tool
    def remove_focus_shortcut(self, command_name: str, ide: str) -> str:
        """Remove a deployed focus shortcut.
        ide=cursor → .cursor/commands/{command_name}.md
        ide=vscode → .github/prompts/{command_name}.prompt.md
        Returns the removed path or 'not found: <path>'."""
        if ide == "cursor":
            target = _REPO_ROOT / ".cursor" / "commands" / f"{command_name}.md"
        else:
            target = _REPO_ROOT / ".github" / "prompts" / f"{command_name}.prompt.md"
        if not target.exists():
            return f"not found: {target}"
        target.unlink()
        return f"removed: {target}"

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
        Returns the state file path."""
        state = {
            "ide": ide,
            "name_filter": name_filter,
            "deployed": json.loads(deployed_skills),
            "deployed_commands": json.loads(deployed_commands),
        }
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
        """Deploy hooks/manifest-gate.json to the IDE hooks location.
        ide=cursor → merges into .cursor/hooks.json (creates if absent).
        ide=vscode → copies to .github/hooks/manifest-gate.json.
        Returns the path written, or 'not found: <path>' if the source is missing."""
        source = _REPO_ROOT / "hooks" / "manifest-gate.json"
        if not source.exists():
            return f"not found: {source}"
        gate_config = json.loads(source.read_text(encoding="utf-8"))
        if ide == "cursor":
            target = _REPO_ROOT / ".cursor" / "hooks.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            existing = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
            merged = _merge_hooks(existing, gate_config)
            target.write_text(json.dumps(merged, indent=2), encoding="utf-8")
            return str(target)
        else:
            target = _REPO_ROOT / ".github" / "hooks" / "manifest-gate.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            return str(target)

    @tool
    def remove_skill_shim(self, skill_slug: str, ide: str) -> str:
        """Remove .cursor/skills/{skill_slug}/ (ide=cursor) or .github/skills/{skill_slug}/ (ide=vscode).
        Returns the removed path or 'not found: <path>'."""
        import shutil
        import subprocess
        base = ".cursor" if ide == "cursor" else ".github"
        skill_dir = _REPO_ROOT / base / "skills" / skill_slug
        if not skill_dir.exists():
            return f"not found: {skill_dir}"
        try:
            shutil.rmtree(skill_dir)
        except OSError:
            subprocess.run(
                ["powershell", "-Command", f"Remove-Item -LiteralPath '{skill_dir}' -Recurse -Force"],
                check=True,
            )
        return f"removed: {skill_dir}"

    def _deploy_entries(self, entries: list[dict], ide: str) -> tuple[list[str], list[str]]:
        deployed_skills: list[str] = []
        for entry in entries:
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
            # Drop legacy per-focus×action commands/prompts — not a good IDE fit.
            for shortcut in entry.get("focus_shortcuts", []):
                self.remove_focus_shortcut(
                    command_name=shortcut["command_name"],
                    ide=ide,
                )
        return deployed_skills, []

    @action
    def deploy_tools_as_skills(self, name_filter: str, ide: str) -> str:
        """Deploy workspace toolsets as IDE shims. ide={ide}, filter={name_filter}."""
        """Step 1 — If ide is empty, ask: Which IDE? cursor (Recommended) / vscode."""
        """Step 2 — If name_filter is empty, ask: Deploy all toolsets (Recommended) / enter a module_dir substring."""
        self.scan_toolsets()
        """Step 3 — Apply name_filter: keep entries whose module_dir or skill_slug contains it; skip if filter is empty (= all)."""
        """Step 4 — Present the filtered list of skills and ask the user to confirm before writing."""
        """Step 5 — For each confirmed entry: write one skill shim, remove stale per-focus skill shims and legacy focus commands."""
        self.write_skill_shim()
        """Step 6 — Call deploy_hooks(ide) to install hooks/manifest-gate.json into the IDE hooks location."""
        self.deploy_hooks()
        """Step 7 — Call save_state with ide, name_filter, deployed skill_slugs, and empty deployed_commands."""
        self.save_state()
        return "IDE shims written. Hooks deployed. State saved. Reload the IDE to pick them up."

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
        return f"Re-deployed {len(deployed_skills)} skill(s): {', '.join(deployed_skills)}."

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
