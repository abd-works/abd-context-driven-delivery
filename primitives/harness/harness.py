# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# @toolset-manifest python -m tools manifest harness.harness:Harness
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Harness — deploy context tools and actions into an IDE."""

from __future__ import annotations

import ast
import json
import re
import shutil
from pathlib import Path

from primitives.actions.action import agent_instructions, agentic_toolset
from tools.tool import agent_tool
from tools.toolset_header import read_toolset_header

from harness.agent import Agent
from harness.agent_guidance import AgentGuidance
from harness.bodies import ActionBody
from harness.command import Command
from harness.harness_tool import operation_writes
from harness.hook import Hook
from harness.instruction import Instruction
from harness.prompt import Prompt, prompt
from harness.rule import Rule
from harness.skill import Skill, skill

_REPO_ROOT = Path(__file__).resolve().parents[2]
_IMPLEMENTED = frozenset({"Cursor", "VS Code"})
_SKIP_DIRS = frozenset({"__pycache__", "examples", "primitives"})
_STALE_ACTION_SKILL_SLUGS = ("grill-context", "workspace", "workflow")
_WALK_TREES = ("context_tools", "utilities")
_FORMATS = (
    "markdown",
    "json",
    "drawio",
    "miro",
    "python",
    "typescript",
    "java",
    "javascript",
)


_CLASS_DECOS = frozenset({"agentic_toolset", "toolset"})
_METHOD_DECOS = frozenset({"agent_tool", "agent_instructions", "skill", "prompt"})


def _deco_id(node: ast.expr) -> str | None:
    target = node.func if isinstance(node, ast.Call) else node
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return None


def _class_slug(name: str) -> str:
    stepped = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", stepped).lower()


def _header_class(manifest_command: str) -> str:
    ref = manifest_command.strip().rsplit(" ", 1)[-1]
    if ":" not in ref:
        return ""
    return ref.split(":")[-1]


def _agentic_class_names(tree: ast.AST) -> list[str]:
    names: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if any(_deco_id(dec) in _CLASS_DECOS for dec in node.decorator_list):
            names.append(node.name)
            continue
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if any(_deco_id(dec) in _METHOD_DECOS for dec in item.decorator_list):
                names.append(node.name)
                break
    return names


@agentic_toolset
class Harness:
    """Deploy workspace toolsets as IDE skills, prompts, and instructions."""

    def __init__(self, type: str, repo_root: Path | str | None = None) -> None:
        if not type:
            raise TypeError("type is required")
        self.type = type
        self.repo_root = Path(repo_root) if repo_root is not None else _REPO_ROOT
        self.skills: list[Skill] = []
        self.prompts: list[Prompt] = []
        self.commands: list[Command] = []
        self.instruction_files: list[Instruction] = []
        self.rules: list[Rule] = []
        self.agents: list[Agent] = []
        self.hooks: list[Hook] = []
        self.agent_guidance: list[AgentGuidance] = []

    def _require_implemented(self) -> None:
        if self.type not in _IMPLEMENTED:
            raise NotImplementedError(self.type)

    def _state_path(self) -> Path:
        return self.repo_root / "primitives" / "harness" / ".deploy-state.json"

    def _ide_folder(self) -> str:
        return ".cursor" if self.type == "Cursor" else ".github"

    def _should_skip(self, path: Path) -> bool:
        try:
            relative = path.relative_to(self.repo_root)
        except ValueError:
            return True
        if len(relative.parts) > 4:
            return True
        for part in relative.parts:
            if part in _SKIP_DIRS or part.startswith("_"):
                return True
        name = path.name
        return name.endswith(("_spec.py", "_agent_spec.py", "_ground_truth.py"))

    def _workspace_files(self) -> list[Path]:
        found: list[Path] = []
        try:
            found.extend(sorted(self.repo_root.glob("*.code-workspace")))
        except OSError:
            pass
        parent = self.repo_root.parent
        try:
            found.extend(sorted(parent.glob("*.code-workspace")))
        except OSError:
            pass
        try:
            found.extend(sorted(parent.glob("*/*.code-workspace")))
        except OSError:
            pass
        return found

    def _workspace_covers(self, ws: Path) -> tuple[bool, int]:
        try:
            data = json.loads(ws.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return (False, 0)
        raw_folders = [
            entry.get("path") for entry in data.get("folders", []) if entry.get("path")
        ]
        if len(raw_folders) < 2:
            return (False, 0)
        repo = self.repo_root.resolve()
        for raw in raw_folders:
            path = Path(raw)
            folder = path.resolve() if path.is_absolute() else (ws.parent / path).resolve()
            try:
                if folder == repo or repo.is_relative_to(folder) or folder.is_relative_to(repo):
                    return (True, len(raw_folders))
            except (ValueError, OSError):
                continue
        return (False, 0)

    def _suggested_deploy_path(self) -> Path:
        umbrellas: list[tuple[int, Path]] = []
        repo = self.repo_root.resolve()
        for ws in self._workspace_files():
            covers, folder_count = self._workspace_covers(ws)
            if not covers:
                continue
            parent = ws.parent.resolve()
            if parent == repo:
                continue
            umbrellas.append((folder_count, parent))
        if umbrellas:
            umbrellas.sort(key=lambda item: item[0], reverse=True)
            return umbrellas[0][1] / self._ide_folder()
        return self.repo_root / self._ide_folder()

    def _write_root_paths(self, deploy_path: str = "") -> list[Path]:
        if deploy_path.strip():
            return [Path(deploy_path.strip())]
        return [self._suggested_deploy_path()]

    def _classify_path(self, file_path: str) -> str:
        try:
            parts = Path(file_path).resolve().relative_to(self.repo_root.resolve()).parts
        except ValueError:
            parts = Path(file_path).parts
        if "utilities" in parts:
            return "utility"
        if "actions" in parts:
            return "action"
        return "context_tool"

    def _read_meta(self, path: Path, fallback_name: str, class_name: str = "") -> dict:
        overview = fallback_name
        class_string = fallback_name
        guidance = "guidance"
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            return {
                "overview": overview,
                "class_string": class_string,
                "guidance": guidance,
            }
        module_doc = ast.get_docstring(tree) or ""
        if module_doc.strip():
            overview = module_doc.strip().splitlines()[0]
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if class_name and node.name != class_name:
                continue
            class_string = (ast.get_docstring(node) or node.name).strip()
            for item in node.body:
                if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                doc = ast.get_docstring(item)
                if doc:
                    guidance = doc.strip()
                    break
            break
        return {
            "overview": overview,
            "class_string": class_string,
            "guidance": guidance,
        }

    def _literal_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Attribute):
            return node.attr.lower()
        return None

    def _assign_target_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _dict_names(self, node: ast.Dict) -> list[str]:
        names: list[str] = []
        for key, value in zip(node.keys, node.values):
            if key is not None:
                read = self._literal_name(key)
                if read:
                    names.append(read)
            read = self._literal_name(value)
            if read:
                names.append(read)
        return names

    def _names_from_assign(self, node: ast.Assign, attr: str) -> list[str]:
        if not any(self._assign_target_name(target) == attr for target in node.targets):
            return []
        if isinstance(node.value, ast.Dict):
            return self._dict_names(node.value)
        return []

    def _fidelity_names(self, path: Path, class_name: str = "") -> list[str]:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            return []
        names: list[str] = []
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if class_name and node.name != class_name:
                continue
            for item in node.body:
                if isinstance(item, ast.Assign):
                    names.extend(self._names_from_assign(item, "fidelities"))
                    names.extend(self._names_from_assign(item, "STAGE_ALIASES"))
                elif isinstance(item, ast.AnnAssign) and item.value is not None:
                    target = self._assign_target_name(item.target)
                    if target in {"fidelities", "STAGE_ALIASES"} and isinstance(item.value, ast.Dict):
                        names.extend(self._dict_names(item.value))
        seen: set[str] = set()
        unique: list[str] = []
        for name in names:
            if name in seen:
                continue
            seen.add(name)
            unique.append(name)
        return unique

    def _instruction_operations(self, path: Path, class_name: str = "") -> list[tuple[str, str]]:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            return []
        found: list[tuple[str, str]] = []
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if class_name and node.name != class_name:
                continue
            for item in node.body:
                if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if item.name.startswith("_"):
                    continue
                deco_names: list[str] = []
                for dec in item.decorator_list:
                    target = dec.func if isinstance(dec, ast.Call) else dec
                    if isinstance(target, ast.Name):
                        deco_names.append(target.id)
                    elif isinstance(target, ast.Attribute):
                        deco_names.append(target.attr)
                if "agent_instructions" not in deco_names:
                    continue
                found.append((item.name, ast.get_docstring(item) or ""))
        return found

    def _drop_action_skill(self, slug: str, roots: list[Path]) -> None:
        for root in roots:
            skill_dir = root / "skills" / slug
            if skill_dir.is_dir():
                shutil.rmtree(skill_dir)

    def _wanted(self, wanted: str, name: str, source_slug: str, derived: str) -> bool:
        if not wanted:
            return True
        if name == wanted:
            return True
        return source_slug == wanted and derived != "fidelity"

    def _emit(self, kind: str, source: dict, roots: list[Path], seen: set[tuple[str, str]]) -> str | None:
        name = source["name"]
        key = (name, kind)
        if key in seen:
            return None
        seen.add(key)
        if kind == "skill":
            skill_file = Skill(self.type, name)
            skill_file.generate(source, roots)
            self.skills.append(skill_file)
            return name
        if kind == "instruction":
            instruction_file = Instruction(self.type, name)
            written = instruction_file.generate(source, roots)
            self.instruction_files.append(instruction_file)
            if isinstance(written, Rule):
                self.rules.append(written)
            return name
        prompt_file = Prompt(self.type, name)
        written = prompt_file.generate(source, roots)
        self.prompts.append(prompt_file)
        if isinstance(written, Command):
            self.commands.append(written)
        return name

    def _generate_entry(
        self,
        entry: dict,
        roots: list[Path],
        wanted: str,
        seen: set[tuple[str, str]],
    ) -> list[str]:
        path = Path(entry["file_path"])
        slug = entry["skill_slug"]
        class_name = entry.get("class_name") or ""
        kind = self._classify_path(str(path))
        meta = self._read_meta(path, slug, class_name)
        toolset = entry.get("manifest_command", "").rsplit(" ", 1)[-1]
        names: list[str] = []

        def source_for(name: str, guidance: str) -> dict:
            payload = {**meta, "name": name, "toolset": toolset, "guidance": guidance}
            if kind == "action":
                payload["action"] = True
            return payload

        writes = operation_writes(path, class_name)
        if writes:
            for vehicle, deploy_name, _operation, doc in writes:
                name = deploy_name or slug
                if not self._wanted(wanted, name, slug, "source"):
                    continue
                written = self._emit(vehicle, source_for(name, doc or meta["guidance"]), roots, seen)
                if written:
                    names.append(written)
        elif kind == "action":
            if self._wanted(wanted, slug, slug, "source"):
                written = self._emit("prompt", source_for(slug, meta["guidance"]), roots, seen)
                if written:
                    names.append(written)
        else:
            if self._wanted(wanted, slug, slug, "source"):
                written = self._emit("skill", source_for(slug, meta["guidance"]), roots, seen)
                if written:
                    names.append(written)
        if kind != "action":
            for fidelity_name in self._fidelity_names(path, class_name):
                if not self._wanted(wanted, fidelity_name, slug, "fidelity"):
                    continue
                if fidelity_name == "scaffold":
                    guidance = f"Run {fidelity_name}."
                else:
                    guidance = f"Run at fidelity {fidelity_name}. Do not treat this as a format."
                written = self._emit("prompt", source_for(fidelity_name, guidance), roots, seen)
                if written:
                    names.append(written)
        else:
            for operation, doc in self._instruction_operations(path, class_name):
                if operation == slug or (
                    class_name and operation.casefold() == class_name.casefold()
                ):
                    continue
                if not self._wanted(wanted, operation, slug, "operation"):
                    continue
                written = self._emit(
                    "prompt",
                    source_for(operation, doc or f"Run {operation}."),
                    roots,
                    seen,
                )
                if written:
                    names.append(written)
        return names

    def _write_harness_files(self, roots: list[Path], seen: set[tuple[str, str]]) -> list[str]:
        body = ActionBody.from_source(
            name="harness",
            class_string="Deploy workspace toolsets as IDE skills, prompts, and instructions.",
            operation_instructions=(
                "With no IDE given, AskQuestion: Which IDE? Cursor | VS Code. "
                "With no name filter given, AskQuestion: all toolsets (recommended) / enter a substring. "
                "With no deploy path given, call suggested_deploy_path, then AskQuestion: "
                "deploy to that suggested path (recommended) / enter another path."
            ),
            toolset="harness.harness:Harness",
        )
        source = {
            "name": "harness",
            "overview": "Deploy workspace toolsets as IDE skills, prompts, and instructions.",
            "body": body,
        }
        skill_file = Skill(self.type, "harness")
        skill_file.generate(source, roots)
        self.skills.append(skill_file)
        prompt_file = Prompt(self.type, "harness")
        written = prompt_file.generate(source, roots)
        self.prompts.append(prompt_file)
        if isinstance(written, Command):
            self.commands.append(written)
        seen.add(("harness", "skill"))
        seen.add(("harness", "prompt"))
        names: list[str] = []
        path = Path(__file__)
        for vehicle, deploy_name, operation, doc in operation_writes(path, "Harness"):
            name = deploy_name or operation
            if name in {"harness", "generate"} or operation == "generate":
                continue
            payload = {
                "name": name,
                "overview": doc or name,
                "guidance": doc or name,
                "toolset": "harness.harness:Harness",
            }
            emitted = self._emit(vehicle, payload, roots, seen)
            if emitted:
                names.append(emitted)
        return names

    def _remove_stale(self, roots: list[Path]) -> None:
        for root in roots:
            for slug in _STALE_ACTION_SKILL_SLUGS:
                skill_dir = root / "skills" / slug
                if skill_dir.is_dir():
                    shutil.rmtree(skill_dir)
                for leftover in (
                    root / "commands" / f"{slug}.md",
                    root / "prompts" / f"{slug}.prompt.md",
                ):
                    if leftover.is_file():
                        leftover.unlink()

    def _save_ide(self, deploy_path: str = "") -> None:
        path = self._state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"type": self.type}
        if deploy_path:
            payload["deploy_path"] = deploy_path
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def walk(self, name_filter: str = "") -> str:
        """Walk context_tools/ and utilities/ for agentic classes. Returns a JSON array."""
        results: list[dict] = []
        seen: set[str] = set()
        needle = name_filter.strip().lower()
        for tree_name in _WALK_TREES:
            tree = self.repo_root / tree_name
            if not tree.is_dir():
                continue
            for py_file in sorted(tree.rglob("*.py")):
                if self._should_skip(py_file):
                    continue
                try:
                    tree_ast = ast.parse(py_file.read_text(encoding="utf-8"))
                except (OSError, SyntaxError):
                    continue
                manifest = ""
                try:
                    header = read_toolset_header(py_file)
                    manifest = header.manifest_command
                except ValueError:
                    manifest = ""
                if "{" in manifest:
                    continue
                classes = _agentic_class_names(tree_ast)
                if not classes:
                    named = _header_class(manifest)
                    if named:
                        classes = [named]
                if not classes:
                    continue
                for class_name in classes:
                    slug = _class_slug(class_name)
                    if slug in seen:
                        continue
                    if needle and needle not in slug and needle not in class_name.lower() and needle not in str(py_file).lower():
                        continue
                    seen.add(slug)
                    results.append(
                        {
                            "skill_slug": slug,
                            "class_name": class_name,
                            "manifest_command": manifest,
                            "file_path": str(py_file),
                        }
                    )
        return json.dumps(results, indent=2)

    @agent_tool
    def suggested_deploy_path(self) -> str:
        """Suggested IDE folder to write skills, commands, and prompts."""
        return str(self._suggested_deploy_path())

    @agent_tool
    def write_deploy(self, source: str = "", name_filter: str = "", deploy_path: str = "") -> str:
        """Walk if needed, then write sources plus Harness skill and prompt into the deploy area."""
        self._require_implemented()
        self.skills = []
        self.prompts = []
        self.commands = []
        self.instruction_files = []
        self.rules = []
        self.agents = []
        self.hooks = []
        self.agent_guidance = []
        roots = self._write_root_paths(deploy_path)
        wanted = source.strip()
        seen: set[tuple[str, str]] = set()
        names: list[str] = []
        for entry in json.loads(self.walk(name_filter)):
            names.extend(self._generate_entry(entry, roots, wanted, seen))
        for fmt in _FORMATS:
            if wanted and fmt != wanted:
                continue
            written = self._emit("prompt", {"name": fmt, "format": fmt}, roots, seen)
            if written:
                names.append(written)
        skill_names = {item.name for item in self.skills}
        for prompt_file in self.prompts:
            if prompt_file.name not in skill_names:
                self._drop_action_skill(prompt_file.name, roots)
        names.extend(self._write_harness_files(roots, seen))
        self._remove_stale(roots)
        self._save_ide(str(roots[0]))
        return json.dumps(
            {
                "roots": [str(r) for r in roots],
                "sources": names,
            }
        )

    @skill
    @prompt
    @agent_instructions
    def generate(
        self,
        source: str | None = None,
        name_filter: str | None = None,
        deploy_path: str | None = None,
    ) -> str:
        """With no IDE given, AskQuestion: Which IDE? Cursor | VS Code."""
        self._require_implemented()
        """With no name filter given, AskQuestion: all toolsets (recommended) / enter a substring."""
        """With no deploy path given, call suggested_deploy_path, then AskQuestion: deploy to that suggested path (recommended) / enter another path."""
        self.suggested_deploy_path()
        """With no source: walk context_tools/ and utilities/, generate each source into the deploy area, also write a Harness skill and a Harness prompt. Generate is the deploy — no separate deploy. Do not confirm the scanned list. Overwrite generated files. Remove stale shortcuts and old slugs. Save the IDE."""
        """With a source: write that source into the deploy area."""
        """With type Claude, Codex, or ChatGPT: must not implement yet."""
        self.write_deploy()
        return ""

    @agent_tool
    def generateAgain(self) -> str:
        """Write using the saved IDE. No questions."""
        path = self._state_path()
        if not path.is_file():
            raise RuntimeError("no saved IDE")
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            saved = state.get("type")
            deploy_path = state.get("deploy_path") or ""
        except (OSError, json.JSONDecodeError):
            saved = None
            deploy_path = ""
        if not saved:
            raise RuntimeError("no saved IDE")
        self.type = saved
        return self.write_deploy(deploy_path=deploy_path)

    @prompt
    @agent_tool
    def clean(self) -> str:
        """Remove this Harness type's deploy files only — not the other IDE."""
        self._require_implemented()
        roots = self._write_root_paths()
        removed: list[str] = []
        for root in roots:
            for folder in ("skills", "commands", "prompts", "instructions", "rules"):
                target = root / folder
                if target.is_dir():
                    shutil.rmtree(target)
                    removed.append(str(target))
        return json.dumps({"roots": [str(r) for r in roots], "removed": removed})
