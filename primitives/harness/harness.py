# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# @toolset-manifest python -m tools manifest harness.harness:Harness
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
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
from tools.tool import _ToolsetLoader, agent_tool
from tools.toolset_header import manifest_commands

from harness.agent import Agent
from harness.agent_guidance import AgentGuidance
from harness.command import Command
from harness.harness_tool import operation_writes, required_init_params
from harness.instruction import Instruction
from harness.prompt import Prompt, prompt
from harness.returned_guidance import _DEFAULT_CODE_LANGUAGE, compound_guidance
from harness.context_tool_rules import (
    ContextToolRuleSpec,
    all_context_tool_mdc_specs,
    all_context_tool_procedure_specs,
    all_context_tool_rule_specs,
    all_rules_folder_specs,
    rules_from_repo_rules_folder,
)
from harness.rule import Rule
from harness.skill import Skill

_REPO_ROOT = Path(__file__).resolve().parents[2]
_IMPLEMENTED = frozenset({"Cursor", "VS Code", "Kilo"})
_SKIP_DIRS = frozenset({"__pycache__", "examples"})
_COMPOSER_CLASSES = frozenset({"BaseContextTool", "LifecycleAction"})
_WALK_TREES = ("context_tools", "utilities", "primitives")
_FORMATS = (
    "markdown",
    "code",
    "drawio",
    "miro",
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


def _is_dev_only_class(tree: ast.AST, class_name: str) -> bool:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return any(_deco_id(dec) == "dev_only" for dec in node.decorator_list)
    return False


def _class_slug(name: str) -> str:
    stepped = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    stepped = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", stepped)
    stepped = re.sub(r"[_.:/\\\s]+", "-", stepped)
    stepped = re.sub(r"-+", "-", stepped)
    return stepped.strip("-").lower()


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


def _inferred_class_names(tree: ast.AST, source_path: Path) -> list[str]:
    """Infer likely toolset classes from file name when headers/decorators are absent."""
    expected_stem = source_path.parent.name if source_path.stem == "__init__" else source_path.stem
    expected_slug = _class_slug(expected_stem)
    classes = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
    if not classes:
        return []
    matching = [name for name in classes if _class_slug(name) == expected_slug]
    if matching:
        return matching
    if len(classes) == 1:
        return classes
    return []


@agentic_toolset
class Harness:
    """Deploy workspace toolsets as IDE skills, prompts, and instructions."""

    def __init__(self, type: str, repo_root: Path | str | None = None) -> None:
        if not type:
            raise TypeError("type is required")
        self.type = type
        self.repo_root = Path(repo_root) if repo_root is not None else _REPO_ROOT
        self._extended = False
        self._prod = False
        self._no_manifest = False
        self._mcp = False
        self._transport = "cli"
        self._code_language = _DEFAULT_CODE_LANGUAGE
        self.skills: list[Skill] = []
        self.prompts: list[Prompt] = []
        self.commands: list[Command] = []
        self.instruction_files: list[Instruction] = []
        self.rules: list[Rule] = []
        self.agents: list[Agent] = []
        self._hook_events: set[str] = set()
        self.agent_guidance: list[AgentGuidance] = []

    def _require_implemented(self) -> None:
        if self.type not in _IMPLEMENTED:
            raise NotImplementedError(self.type)

    def _state_path(self) -> Path:
        return self.repo_root / "primitives" / "harness" / ".deploy-state.json"

    def _deploy_slug(self, value: str) -> str:
        return _class_slug(value or "")

    def _ide_folder(self) -> str:
        if self.type == "Kilo":
            return ".kilo"
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
            root = Path(deploy_path.strip())
            ide = self._ide_folder()
            if root.name != ide and root.name not in (".kilo", ".cursor", ".github"):
                root = root / ide
            return [root]
        return [self._suggested_deploy_path()]

    def _constructor_context(self, path: Path, class_name: str) -> dict[str, str]:
        """Return {param: ''} for each required __init__ param of the class at path."""
        params = required_init_params(path, class_name)
        return {p: "" for p in params}

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
                "fidelities": [],
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
            guidance_doc = ""
            for item in node.body:
                if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if item.name != "guidance":
                    continue
                guidance_doc = (ast.get_docstring(item) or "").strip()
                break
            if guidance_doc:
                overview = guidance_doc.splitlines()[0].strip()
                guidance = guidance_doc
            break
        return {
            "overview": overview,
            "class_string": class_string,
            "guidance": guidance,
            "fidelities": self._fidelity_option_names(path, class_name),
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

    def _dict_values(self, node: ast.Dict) -> list[str]:
        names: list[str] = []
        for value in node.values:
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

    def _unique_names(self, names: list[str]) -> list[str]:
        seen: set[str] = set()
        unique: list[str] = []
        for name in names:
            if name in seen:
                continue
            seen.add(name)
            unique.append(name)
        return unique

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
        return self._unique_names(names)

    def _fidelity_option_names(self, path: Path, class_name: str = "") -> list[str]:
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
                if isinstance(item, ast.Assign) and any(
                    self._assign_target_name(target) == "fidelities" for target in item.targets
                ):
                    if isinstance(item.value, ast.Dict):
                        names.extend(self._dict_values(item.value))
                elif isinstance(item, ast.AnnAssign) and item.value is not None:
                    target = self._assign_target_name(item.target)
                    if target == "fidelities" and isinstance(item.value, ast.Dict):
                        names.extend(self._dict_values(item.value))
        return self._unique_names(names)

    def _has_agent_instructions(self, path: Path, class_name: str) -> bool:
        """True when the class at path has an @agent_instructions operation."""
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            return False
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if class_name and node.name != class_name:
                continue
            for item in node.body:
                if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if any(_deco_id(dec) == "agent_instructions" for dec in item.decorator_list):
                    return True
        return False

    def _action_option_names(self) -> list[str]:
        names: list[str] = []
        for entry in json.loads(self.walk()):
            path = Path(entry["file_path"])
            if self._classify_path(str(path)) != "action":
                continue
            slug = entry["skill_slug"]
            class_name = entry.get("class_name") or ""
            if class_name in _COMPOSER_CLASSES:
                continue
            writes = operation_writes(path, class_name, repo_root=self.repo_root)
            if writes:
                for vehicle, deploy_name, _operation, _doc, _invoke in writes:
                    if vehicle != "prompt":
                        continue
                    names.append(self._deploy_slug(deploy_name or slug))
            else:
                names.append(self._deploy_slug(slug))
        return sorted(self._unique_names(names))

    def _context_tool_option_names(self) -> list[str]:
        names: list[str] = []
        for entry in json.loads(self.walk()):
            path = Path(entry["file_path"])
            if self._classify_path(str(path)) != "context_tool":
                continue
            slug = entry["skill_slug"]
            if entry.get("class_name") in _COMPOSER_CLASSES:
                continue
            names.append(self._deploy_slug(slug))
        return sorted(self._unique_names(names))

    def _drop_action_skill(self, slug: str, roots: list[Path]) -> None:
        for root in roots:
            for candidate in (
                root / "skills" / slug,
                root / "skills" / "context_tools" / slug,
                root / "skills" / "context-tools" / slug,
                root / "skills" / "actions" / slug,
            ):
                if candidate.is_dir():
                    shutil.rmtree(candidate)

    def _drop_source_slug(self, slug: str, roots: list[Path]) -> None:
        self._drop_action_skill(slug, roots)
        for root in roots:
            for leftover in (
                root / "commands" / f"{slug}.md",
                root / "prompts" / f"{slug}.prompt.md",
            ):
                if leftover.is_file():
                    leftover.unlink()

    def _drop_unwritten_skills(self, roots: list[Path], written: set[str]) -> None:
        """Remove skill folders not in ``written``.

        ``written`` contains relative keys of the form ``"<folder...>/<name>"``
        matching ``Skill.relative_path()`` minus the leading ``skills/`` and
        trailing ``/SKILL.md``.  Works at any nesting depth.
        """
        for root in roots:
            skills_root = root / "skills"
            if not skills_root.is_dir():
                continue
            # Collect all SKILL.md files and compute their key
            for skill_md in list(skills_root.rglob("SKILL.md")):
                rel = skill_md.relative_to(skills_root)
                # key is everything except the trailing SKILL.md
                key = "/".join(rel.parts[:-1])
                if key not in written:
                    try:
                        shutil.rmtree(skill_md.parent)
                    except OSError:
                        pass
            # Prune empty directories bottom-up
            for dirpath in sorted(skills_root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                if dirpath.is_dir():
                    try:
                        dirpath.rmdir()
                    except OSError:
                        pass

    def _prompt_stem(self, path: Path) -> str | None:
        name = path.name
        if name.endswith(".prompt.md"):
            return name[: -len(".prompt.md")]
        if path.suffix == ".md":
            return path.stem
        return None

    def _drop_unwritten_prompts(self, roots: list[Path], written: set[str]) -> None:
        for root in roots:
            for folder in ("commands", "prompts"):
                folder_path = root / folder
                if not folder_path.is_dir():
                    continue
                for child in folder_path.iterdir():
                    if not child.is_file():
                        continue
                    stem = self._prompt_stem(child)
                    if stem is not None and stem not in written:
                        child.unlink()

    def _drop_unwritten_rules(self, roots: list[Path], written: set[str]) -> None:
        for root in roots:
            for folder_name in ("rules", "instructions"):
                rules_root = root / folder_name
                if not rules_root.is_dir():
                    continue
                for rule_file in list(rules_root.rglob("*.mdc")) + list(rules_root.rglob("*.md")):
                    key = rule_file.relative_to(rules_root).as_posix()
                    if key.endswith(".mdc"):
                        key = key[: -len(".mdc")]
                    elif key.endswith(".md"):
                        key = key[: -len(".md")]
                    if key not in written:
                        rule_file.unlink()
                for dirpath in sorted(rules_root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                    if dirpath.is_dir():
                        try:
                            dirpath.rmdir()
                        except OSError:
                            pass

    def _write_rule_spec(
        self,
        spec: ContextToolRuleSpec,
        roots: list[Path],
        seen: set[tuple[str, str]],
        seen_key: tuple[str, str],
    ) -> str | None:
        if seen_key in seen:
            return None
        seen.add(seen_key)
        rule = Rule(self.type, spec.name)
        rule.description = spec.description
        rule.globs = spec.globs
        rule.always_apply = spec.always_apply
        rule.body = spec.body
        if spec.tool_slug:
            rule.subfolder = f"{spec.folder}/{spec.tool_slug}" if spec.folder else spec.tool_slug
        else:
            rule.subfolder = spec.folder
        rule.write(roots)
        self.rules.append(rule)
        return spec.name

    def _write_repo_rules(
        self,
        roots: list[Path],
        seen: set[tuple[str, str]],
    ) -> list[str]:
        """Write repo-level ``rules/*.md`` as top-level rules."""
        if self.type not in ("Cursor", "Kilo", "VS Code"):
            return []
        names: list[str] = []
        for spec in rules_from_repo_rules_folder(self.repo_root):
            written = self._write_rule_spec(spec, roots, seen, (spec.name, "repo-rule"))
            if written:
                names.append(written)
        return names

    def _write_context_tool_mdcs(
        self,
        roots: list[Path],
        wanted: str,
        seen: set[tuple[str, str]],
    ) -> list[str]:
        """Write scoped rules and procedures under `rules/context_tools/{slug}/` or `instructions/context_tools/{slug}/`."""
        if self.type not in ("Cursor", "Kilo", "VS Code"):
            return []
        names: list[str] = []
        for spec in all_context_tool_rule_specs(self.repo_root):
            if wanted and wanted != spec.tool_slug and not wanted.startswith(f"{spec.tool_slug}-"):
                continue
            written = self._write_rule_spec(
                spec, roots, seen, (f"{spec.tool_slug}-{spec.name}", "rule")
            )
            if written:
                names.append(f"{spec.tool_slug}/{written}")
        for spec in all_context_tool_procedure_specs(self.repo_root):
            if wanted and wanted != spec.tool_slug and not wanted.startswith(f"{spec.tool_slug}-"):
                continue
            written = self._write_rule_spec(
                spec, roots, seen, (f"{spec.tool_slug}-{spec.name}", "procedure")
            )
            if written:
                names.append(f"{spec.tool_slug}/{written}")
        for spec in all_rules_folder_specs(self.repo_root):
            if wanted and wanted != spec.tool_slug and not wanted.startswith(f"{spec.tool_slug}-"):
                continue
            written = self._write_rule_spec(
                spec, roots, seen, (f"{spec.tool_slug}-{spec.name}", "rules-folder")
            )
            if written:
                names.append(f"{spec.tool_slug}/{written}")
        return names

    def _write_context_tool_rules(
        self,
        roots: list[Path],
        wanted: str,
        seen: set[tuple[str, str]],
    ) -> list[str]:
        """Write scoped rules under `rules/context_tools/{slug}/`."""
        return self._write_context_tool_mdcs(roots, wanted, seen)

    def _update_kilo_json(self, roots: list[Path]) -> None:
        if self.type != "Kilo":
            return
        patterns = [".kilo/rules/**/*.md", "rules/**/*.md"]
        target_files: set[Path] = set()
        for root in roots:
            target_files.add(root / "kilo.json")
        if (self.repo_root / "kilo.json").is_file():
            target_files.add(self.repo_root / "kilo.json")

        for path in target_files:
            data: dict = {}
            if path.is_file():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    data = {}
            instructions = data.get("instructions")
            if not isinstance(instructions, list):
                instructions = []
            for p in patterns:
                if p not in instructions:
                    instructions.append(p)
            data["instructions"] = instructions
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def _update_copilot_instructions(self, roots: list[Path]) -> None:
        if self.type != "VS Code":
            return
        content = (
            "# GitHub Copilot Workspace Instructions\n\n"
            "This repository uses context-driven delivery instructions located in `.github/instructions/`.\n"
            "Refer to `.github/instructions/**/*.md` for coding standards, architectural rules, and context-tool procedures.\n"
        )
        for root in roots:
            copilot_file = root / "copilot-instructions.md"
            if not copilot_file.is_file():
                copilot_file.parent.mkdir(parents=True, exist_ok=True)
                copilot_file.write_text(content, encoding="utf-8")

    def _wanted(self, wanted: str, name: str, source_slug: str, derived: str) -> bool:
        if not wanted:
            return True
        wanted_slug = self._deploy_slug(wanted)
        name_slug = self._deploy_slug(name)
        source_slug_norm = self._deploy_slug(source_slug)
        if name == wanted or name_slug == wanted_slug:
            return True
        if derived == "fidelity":
            short = name.rsplit("-", 1)[-1]
            if wanted == short or wanted_slug == self._deploy_slug(short):
                return True
        return source_slug == wanted or source_slug_norm == wanted_slug

    def _emit(self, kind: str, source: dict, roots: list[Path], seen: set[tuple[str, str]]) -> str | None:
        name = self._deploy_slug(source["name"])
        source = {**source, "name": name}
        key = (name, kind)
        if key in seen:
            return None
        seen.add(key)
        if kind == "skill":
            skill_file = Skill(self.type, name)
            skill_file.generate(source, roots)
            self.skills.append(skill_file)
            return name
        if kind == "hook":
            from hooks.dispatch import hook_skill_sources

            payloads, events = hook_skill_sources(source)
            for payload in payloads:
                payload_name = self._deploy_slug(payload.get("name", ""))
                payload = {**payload, "name": payload_name}
                skill_file = Skill(self.type, payload_name)
                skill_file.disable_model_invocation = True
                skill_file.generate(payload, roots)
                self.skills.append(skill_file)
            self._hook_events.update(events)
            return self._deploy_slug(payloads[0]["name"]) if payloads else name
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
        if isinstance(written, Skill):
            self.skills.append(written)
        elif isinstance(written, Command):
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
        if class_name in _COMPOSER_CLASSES:
            if self._wanted(wanted, slug, slug, "source"):
                self._drop_source_slug(slug, roots)
            return []
        if self._prod:
            try:
                tree_ast = ast.parse(path.read_text(encoding="utf-8"))
                if _is_dev_only_class(tree_ast, class_name):
                    return []
            except (OSError, SyntaxError):
                pass
        kind = self._classify_path(str(path))
        if self._no_manifest:
            if self._no_manifest_slug_blocked(slug):
                if self._wanted(wanted, slug, slug, "source"):
                    self._drop_source_slug(slug, roots)
                return []
            if kind == "utility":
                if self._wanted(wanted, slug, slug, "source"):
                    self._drop_source_slug(slug, roots)
                return []
            if kind not in {"action", "context_tool"}:
                if self._wanted(wanted, slug, slug, "source"):
                    self._drop_source_slug(slug, roots)
                return []
            if kind == "action" and "scanner" in slug:
                if self._wanted(wanted, slug, slug, "source"):
                    self._drop_source_slug(slug, roots)
                return []
        meta = self._read_meta(path, slug, class_name)
        toolset = entry.get("toolset_ref") or entry.get("manifest_command", "").rsplit(" ", 1)[-1]
        names: list[str] = []

        _BASE_FOLDER = {"context_tool": "context_tools", "action": "actions", "utility": "utilities"}

        def _folder_for(k: str, s: str) -> str:
            if k == "context_tool":
                return f"{_BASE_FOLDER['context_tool']}/{s}"
            if k == "action":
                return _BASE_FOLDER["action"]
            if k == "utility":
                return _BASE_FOLDER["utility"]
            return ""

        def source_for(name: str, guidance: str, *, operation: str = "", invoke: str = "action") -> dict:
            payload = {
                **meta,
                "name": name,
                "toolset": toolset,
                "guidance": guidance,
                "source_kind": kind,
                "operation": operation,
                "invoke": invoke,
                "folder": _folder_for(kind, slug),
                "transport": self._transport,
            }
            if self._extended:
                payload["extended"] = True
            if kind == "action":
                payload["action"] = True
                payload["context_tools"] = (
                    self._context_tools_for_ask
                    if hasattr(self, "_context_tools_for_ask")
                    else self._context_tool_option_names()
                )
            elif kind == "context_tool":
                payload["actions"] = (
                    self._actions_for_ask
                    if hasattr(self, "_actions_for_ask")
                    else self._action_option_names()
                )
            return payload

        cc = self._constructor_context(path, class_name)
        writes = operation_writes(path, class_name, repo_root=self.repo_root)
        if writes:
            for vehicle, deploy_name, operation, doc, invoke in writes:
                name = self._deploy_slug(deploy_name or slug)
                if vehicle == "hook":
                    name = self._deploy_slug(operation or deploy_name or slug)
                if not self._wanted(wanted, name, slug, "source"):
                    continue
                payload = source_for(name, doc or meta["guidance"], operation=operation, invoke=invoke)
                if self._no_manifest and kind in {"action", "utility"}:
                    payload["body"] = self._direct_skill_body(
                        name=name,
                        source_text=doc,
                        path=path,
                        slug=slug,
                        class_name=class_name,
                        fallback=meta.get("guidance", ""),
                    )
                if vehicle == "hook":
                    payload["event"] = deploy_name or ""
                    payload["owner"] = class_name
                    payload["slug"] = slug
                    payload["operation"] = operation
                    base_folder = payload.get("folder") or ""
                    if base_folder and slug and not base_folder.endswith(f"/{slug}"):
                        payload["folder"] = f"{base_folder}/{slug}"
                if cc:
                    payload["constructor_context"] = cc
                written = self._emit(
                    vehicle,
                    payload,
                    roots,
                    seen,
                )
                if written:
                    names.append(written)
        elif kind == "action":
            if self._wanted(wanted, slug, slug, "source"):
                payload = source_for(slug, meta["guidance"])
                if self._no_manifest:
                    payload["body"] = self._direct_skill_body(
                        name=slug,
                        source_text=meta.get("guidance", ""),
                        path=path,
                        slug=slug,
                        class_name=class_name,
                        fallback=meta.get("class_string", ""),
                    )
                written = self._emit("prompt", payload, roots, seen)
                if written:
                    names.append(written)
        elif kind == "context_tool":
            if self._wanted(wanted, slug, slug, "source"):
                payload = source_for(slug, meta["guidance"])
                if self._no_manifest:
                    payload["body"] = self._direct_skill_body(
                        name=slug,
                        source_text=meta.get("guidance", ""),
                        path=path,
                        slug=slug,
                        class_name=class_name,
                        fallback=meta.get("overview", ""),
                    )
                written = self._emit("skill", payload, roots, seen)
                if written:
                    names.append(written)
        elif kind == "utility":
            default_name = self._deploy_slug(toolset.rsplit(":", 1)[0].rsplit(".", 1)[-1] or slug)
            if self._wanted(wanted, default_name, slug, "source") and self._has_agent_instructions(
                path, class_name
            ):
                payload = source_for(default_name, meta["guidance"])
                if self._no_manifest:
                    payload["body"] = self._direct_skill_body(
                        name=default_name,
                        source_text=meta.get("guidance", ""),
                        path=path,
                        slug=slug,
                        class_name=class_name,
                        fallback=meta.get("class_string", ""),
                    )
                if cc:
                    payload["constructor_context"] = cc
                written = self._emit("prompt", payload, roots, seen)
                if written:
                    names.append(written)
        if kind != "action":
            for fidelity_name in self._fidelity_option_names(path, class_name):
                deploy_name = self._deploy_slug(f"{slug}-{fidelity_name}")
                if not self._wanted(wanted, deploy_name, slug, "fidelity"):
                    continue
                payload = source_for(deploy_name, meta["guidance"])
                payload["extended"] = self._extended
                if cc:
                    payload["constructor_context"] = cc
                if self._extended:
                    payload["returned"] = compound_guidance(
                        path,
                        class_name,
                        fidelity_name,
                        cc or None,
                        toolset=toolset,
                        code_language=self._code_language,
                    )
                payload["fidelity"] = True
                payload["fidelity_slug"] = fidelity_name
                written = self._emit("prompt", payload, roots, seen)
                if written:
                    names.append(written)
        if self._wanted(wanted, slug, slug, "source") and slug not in names:
            self._drop_source_slug(slug, roots)
        return names

    def _write_harness_files(self, roots: list[Path], seen: set[tuple[str, str]]) -> list[str]:
        names: list[str] = []
        path = Path(__file__)
        harness_cc = self._constructor_context(path, "Harness")
        for vehicle, deploy_name, operation, doc, invoke in operation_writes(
            path, "Harness", repo_root=self.repo_root
        ):
            name = self._deploy_slug(deploy_name or operation)
            if vehicle == "skill":
                continue
            if not deploy_name and operation == "generate":
                continue
            cli_operation = operation
            cli_invoke = invoke
            if operation == "generate":
                cli_operation = "write_deploy"
                cli_invoke = "tool"
            payload = {
                "name": name,
                "overview": doc or name,
                "guidance": doc or name,
                "toolset": "harness.harness:Harness",
                "source_kind": "utility",
                "folder": "",
                "operation": cli_operation,
                "invoke": cli_invoke,
                "transport": self._transport,
            }
            if harness_cc:
                payload["constructor_context"] = harness_cc
            if operation == "generate":
                transport_ask = (
                    "With no transport given, AskQuestion: MCP (recommended) | CLI. "
                    "When MCP is chosen, pass arguments.mcp=true to write_deploy. "
                )
                payload["guidance"] = (
                    "With no IDE given, AskQuestion: Which IDE? Cursor | VS Code | Kilo. "
                    + transport_ask
                    + "With no name filter given, AskQuestion: all toolsets (recommended) / enter a substring. "
                    "With no deploy path given, call suggested_deploy_path, then AskQuestion: "
                    "deploy to that suggested path (recommended) / enter another path. "
                    "With no code_language given, AskQuestion: Python (recommended) | TypeScript. "
                    "Set context.type to the chosen IDE. Pass the chosen language as "
                    "arguments.code_language to write_deploy."
                )
            emitted = self._emit(vehicle, payload, roots, seen)
            if emitted:
                names.append(emitted)
        return names

    def _remove_unprefixed_fidelity_files(self, roots: list[Path]) -> None:
        kept = {item.name for item in self.commands} | {item.name for item in self.prompts}
        shorts: set[str] = set()
        for entry in json.loads(self.walk()):
            path = Path(entry["file_path"])
            if self._classify_path(str(path)) != "context_tool":
                continue
            class_name = entry.get("class_name") or ""
            shorts.update(self._fidelity_option_names(path, class_name))
            shorts.update(self._fidelity_names(path, class_name))
        for root in roots:
            for short in shorts:
                short = self._deploy_slug(short)
                if short in kept:
                    continue
                for leftover in (
                    root / "commands" / f"{short}.md",
                    root / "prompts" / f"{short}.prompt.md",
                ):
                    if leftover.is_file():
                        leftover.unlink()

    def _deploy_agents(self, roots: list[Path]) -> None:
        """Copy context_tools/*/agents/*.md → agents/{name}.md or {name}.agent.md in each deploy root."""
        agent_sources: list[Path] = []
        ct_root = self.repo_root / "context_tools"
        if ct_root.is_dir():
            for ct_dir in ct_root.iterdir():
                agents_dir = ct_dir / "agents"
                if agents_dir.is_dir():
                    agent_sources.extend(agents_dir.glob("*.md"))
        written_names = set()
        for src in agent_sources:
            stem = src.stem
            if self.type == "VS Code":
                dest_name = f"{stem}.agent.md" if not stem.endswith(".agent") else src.name
            else:
                dest_name = src.name
            written_names.add(dest_name)

        for root in roots:
            agents_root = root / "agents"
            agents_root.mkdir(parents=True, exist_ok=True)
            # remove stale items (subdirectories or old agent files no longer in source)
            for item in list(agents_root.iterdir()):
                if item.is_dir():
                    try:
                        shutil.rmtree(item)
                    except OSError:
                        pass
                elif item.name not in written_names:
                    try:
                        item.unlink()
                    except OSError:
                        pass
            for src in agent_sources:
                stem = src.stem
                if self.type == "VS Code":
                    dest_name = f"{stem}.agent.md" if not stem.endswith(".agent") else src.name
                else:
                    dest_name = src.name
                dest = agents_root / dest_name
                dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    def _prune_vscode_agent_clones(self, roots: list[Path]) -> None:
        """Remove legacy plain .md agent clones when .agent.md exists (VS Code only)."""
        if self.type != "VS Code":
            return
        for root in roots:
            agents_root = root / "agents"
            if not agents_root.is_dir():
                continue
            for plain in agents_root.glob("*.md"):
                if plain.name.endswith(".agent.md"):
                    continue
                twin = agents_root / f"{plain.stem}.agent.md"
                if twin.is_file():
                    try:
                        plain.unlink()
                    except OSError:
                        pass

    def _save_ide(self, deploy_path: str = "") -> None:
        path = self._state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"type": self.type}
        if deploy_path:
            payload["deploy_path"] = deploy_path
        if not self._extended:
            payload["legacy"] = True
        if self._code_language != _DEFAULT_CODE_LANGUAGE:
            payload["code_language"] = self._code_language
        if self._no_manifest:
            payload["no_manifest"] = True
        if self._mcp:
            payload["mcp"] = True
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _mcp_python_executable(self) -> str:
        import sys

        for candidate in (
            self.repo_root / ".venv" / "Scripts" / "python.exe",
            self.repo_root / ".venv" / "bin" / "python",
        ):
            if candidate.is_file():
                return str(candidate.resolve())
        return sys.executable

    def _mcp_pythonpath(self) -> str:
        import os

        roots = (
            self.repo_root,
            self.repo_root / "primitives",
            self.repo_root / "utilities",
            self.repo_root / "context_tools",
        )
        return os.pathsep.join(str(path.resolve()) for path in roots)

    def _mcp_startable_toolset_refs(
        self,
        toolset_refs: list[str],
        walk_entries: list[dict],
    ) -> list[str]:
        """Keep only toolsets the MCP host can construct with no arguments."""
        ref_meta = {
            entry["toolset_ref"]: entry
            for entry in walk_entries
            if entry.get("toolset_ref")
        }
        loader = _ToolsetLoader.instance()
        startable: list[str] = []
        seen: set[str] = set()
        for ref in toolset_refs:
            if not ref or ref in seen:
                continue
            seen.add(ref)
            entry = ref_meta.get(ref)
            if entry:
                if required_init_params(Path(entry["file_path"]), entry["class_name"]):
                    continue
            try:
                loader.load(ref)()
            except Exception:
                continue
            startable.append(ref)
        return startable

    def _write_mcp_json(
        self,
        toolset_refs: list[str],
        walk_entries: list[dict],
        cursor_root: Path,
    ) -> None:
        unique_refs = self._mcp_startable_toolset_refs(toolset_refs, walk_entries)
        if not unique_refs:
            return
        path = cursor_root / "mcp.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "mcpServers": {
                "cdd": {
                    "command": self._mcp_python_executable(),
                    "args": [
                        "-m",
                        "mcp_server",
                        "--toolsets",
                        ",".join(unique_refs),
                    ],
                "cwd": str(cursor_root.parent.resolve()),
                    "env": {"PYTHONPATH": self._mcp_pythonpath()},
                }
            }
        }
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def _toolset_ref_from_path(self, path: Path, class_name: str) -> str:
        """Build module:Class from the source file path."""
        try:
            relative = path.resolve().relative_to(self.repo_root.resolve())
        except ValueError:
            relative = path
        module_parts = list(relative.with_suffix("").parts)
        if module_parts and module_parts[-1] == "__init__":
            module_parts = module_parts[:-1]
        module = ".".join(module_parts)
        return f"{module}:{class_name}" if module and class_name else (module or class_name)

    def _no_manifest_source_allowed(self, path: Path, tree_name: str) -> bool:
        """Limit no-manifest deploys to context-tool modules and action folders only."""
        if tree_name == "utilities":
            return False
        if tree_name != "context_tools":
            return True
        try:
            parts = path.resolve().relative_to(self.repo_root.resolve()).parts
        except ValueError:
            return False
        if len(parts) == 3:
            return path.parent.name == path.stem
        if len(parts) == 4 and parts[1] == "actions":
            return path.parent.name == path.stem
        return False

    def _no_manifest_slug_blocked(self, slug: str) -> bool:
        """Block selected skills/actions from no-manifest deployment."""
        slug_norm = self._deploy_slug(slug)
        blocked_exact = {
            "create-rule",
            "partition",
            "repair",
            "render",
            "satisfy",
            "scan",
            "travel-to",
        }
        blocked_prefixes = ("car", "cdd")
        if slug_norm in blocked_exact:
            return True
        return any(slug_norm == prefix or slug_norm.startswith(f"{prefix}-") for prefix in blocked_prefixes)

    def _markdown_file_text(self, path: Path, slug: str, class_name: str) -> str:
        """Load direct markdown guidance from sibling files when present."""
        class_slug = _class_slug(class_name)
        candidates = [
            path.with_suffix(".md"),
            path.parent / f"{slug}.md",
            path.parent / f"{slug.replace('_', '-')}.md",
            path.parent / f"{class_slug}.md",
            path.parent / "README.md",
        ]
        seen: set[Path] = set()
        for candidate in candidates:
            if candidate in seen:
                continue
            seen.add(candidate)
            if not candidate.is_file():
                continue
            try:
                text = candidate.read_text(encoding="utf-8")
            except OSError:
                continue
            if text.strip():
                return text.strip()
        for candidate in sorted(path.parent.glob("*.md")):
            if candidate.name.startswith(".") or candidate in seen:
                continue
            try:
                text = candidate.read_text(encoding="utf-8")
            except OSError:
                continue
            if text.strip():
                return text.strip()
        return ""

    def _direct_skill_body(
        self,
        *,
        name: str,
        source_text: str,
        path: Path,
        slug: str,
        class_name: str,
        fallback: str = "",
    ) -> str:
        """Build direct skill markdown without CLI invoke instructions."""
        content = self._markdown_file_text(path, slug, class_name)
        if not content:
            content = (source_text or "").strip()
        if not content:
            content = (fallback or "").strip()
        if not content:
            content = name
        if content.lstrip().startswith("#"):
            return content
        return f"# {name}\n\n{content}"

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
                if self._no_manifest and not self._no_manifest_source_allowed(py_file, tree_name):
                    continue
                try:
                    text = py_file.read_text(encoding="utf-8")
                    tree_ast = ast.parse(text)
                except (OSError, SyntaxError):
                    continue
                commands = manifest_commands(text)
                default_manifest = commands[0] if commands else ""
                if not self._no_manifest and "{" in default_manifest:
                    continue
                manifest_by_class = {
                    _header_class(cmd): cmd
                    for cmd in commands
                    if _header_class(cmd)
                }
                classes = _agentic_class_names(tree_ast)
                if not classes:
                    if self._no_manifest:
                        classes = _inferred_class_names(tree_ast, py_file)
                    else:
                        named = _header_class(default_manifest)
                        defined = {
                            node.name
                            for node in tree_ast.body
                            if isinstance(node, ast.ClassDef)
                        }
                        if named and named in defined:
                            classes = [named]
                if not classes:
                    continue
                for class_name in classes:
                    slug = _class_slug(class_name)
                    key = f"{py_file}:{class_name}"
                    if key in seen:
                        continue
                    if needle and needle not in slug and needle not in class_name.lower() and needle not in str(py_file).lower():
                        continue
                    seen.add(key)
                    results.append(
                        {
                            "skill_slug": slug,
                            "class_name": class_name,
                            "manifest_command": manifest_by_class.get(
                                class_name, default_manifest
                            ),
                            "toolset_ref": self._toolset_ref_from_path(py_file, class_name),
                            "file_path": str(py_file),
                        }
                    )
        return json.dumps(results, indent=2)

    @agent_tool
    def suggested_deploy_path(self) -> str:
        """Suggested IDE folder to write skills, commands, and prompts."""
        return str(self._suggested_deploy_path())

    def _deploy_cursor_hooks(self, wanted: str = "") -> None:
        """Sync ``dispatch.py`` in ``.cursor/hooks.json`` for registered hook events.

        Partial deploys that do not emit any ``@hook`` sources leave hooks.json
        unchanged so an earlier full deploy is not stripped.
        """
        from hooks.dispatch import deploy_dispatch, load
        from hooks.hook import Hook

        if wanted.strip() and not self._hook_events:
            return

        load()
        events = {entry["event"] for entry in Hook.registered()} | set(self._hook_events)
        if not events:
            return
        deploy_dispatch(self.repo_root, events)

    @agent_tool
    def write_deploy(
        self,
        source: str = "",
        name_filter: str = "",
        deploy_path: str = "",
        extended: bool = True,
        prod: bool = False,
        code_language: str = _DEFAULT_CODE_LANGUAGE,
        no_manifest: bool = False,
        legacy: bool = False,
        mcp: bool = False,
    ) -> str:
        """Walk if needed, then write sources plus Harness prompts into the deploy area.

        By default bakes ct-fidelity guidance into skills ({context_tool}-{fidelity}).
        legacy=True reverts to the old stub-only fidelity skills that call the tool at runtime.
        prod=True skips any class decorated with @dev_only.
        code_language selects python (default) or typescript for inlined code templates.
        mcp=True emits MCP tool references in skills and writes .cursor/mcp.json for Cursor.
        """
        self._require_implemented()
        self._extended = not legacy if extended else False
        self._prod = bool(prod)
        self._no_manifest = bool(no_manifest)
        self._mcp = bool(mcp)
        self._transport = "mcp" if self._mcp else "cli"
        normalized = (code_language or _DEFAULT_CODE_LANGUAGE).strip().lower()
        if normalized not in {"python", "typescript"}:
            raise ValueError(
                f"Unsupported code_language {code_language!r}. Choose from: python, typescript"
            )
        self._code_language = normalized
        self.skills = []
        self.prompts = []
        self.commands = []
        self.instruction_files = []
        self.rules = []
        self.agents = []
        self._hook_events = set()
        self.agent_guidance = []
        self._actions_for_ask = self._action_option_names()
        self._context_tools_for_ask = self._context_tool_option_names()
        roots = self._write_root_paths(deploy_path)
        wanted = source.strip()
        seen: set[tuple[str, str]] = set()
        names: list[str] = []
        walk_entries = json.loads(self.walk(name_filter))
        toolset_refs: list[str] = []
        for entry in walk_entries:
            ref = entry.get("toolset_ref")
            if ref:
                toolset_refs.append(ref)
            names.extend(self._generate_entry(entry, roots, wanted, seen))
        if not self._no_manifest and self.type in ("Cursor", "Kilo", "VS Code"):
            names.extend(self._write_repo_rules(roots, seen))
            if not wanted or any(
                wanted == spec.tool_slug or wanted.startswith(f"{spec.tool_slug}-")
                for spec in all_context_tool_mdc_specs(self.repo_root)
            ):
                names.extend(self._write_context_tool_mdcs(roots, wanted, seen))
            if self.type == "Kilo":
                self._update_kilo_json(roots)
            elif self.type == "VS Code":
                self._update_copilot_instructions(roots)
        if not self._no_manifest:
            for fmt in _FORMATS:
                if wanted and fmt != wanted:
                    continue
                written = self._emit(
                    "prompt",
                    {
                        "name": fmt,
                        "format": fmt,
                        "folder": "formats",
                        "transport": self._transport,
                    },
                    roots,
                    seen,
                )
                if written:
                    names.append(written)
            names.extend(self._write_harness_files(roots, seen))
            if not wanted:
                self._deploy_agents(roots)
        skill_names = {
            "/".join(item.relative_path().parts[1:-1])
            for item in self.skills
        }
        skill_name_only = {item.name for item in self.skills}
        prompt_names = {item.name for item in self.prompts} | {item.name for item in self.commands}
        rule_names = set()
        rules_folder = "instructions" if self.type == "VS Code" else "rules"
        for item in self.rules:
            rel = item.relative_path()
            try:
                rel = rel.relative_to(rules_folder)
            except ValueError:
                pass
            key = rel.as_posix()
            if key.endswith(".mdc"):
                key = key[: -len(".mdc")]
            elif key.endswith(".md"):
                key = key[: -len(".md")]
            rule_names.add(key)
        for prompt_file in self.prompts:
            if prompt_file.name not in skill_name_only:
                self._drop_action_skill(prompt_file.name, roots)
        if not wanted and not self._no_manifest:
            self._drop_unwritten_skills(roots, skill_names)
            self._drop_unwritten_prompts(roots, prompt_names)
            self._drop_unwritten_rules(roots, rule_names)
        self._prune_vscode_agent_clones(roots)
        self._remove_unprefixed_fidelity_files(roots)
        self._save_ide(str(roots[0]))
        if self._mcp and self.type == "Cursor":
            self._write_mcp_json(toolset_refs, walk_entries, roots[0])
        if self.type == "Cursor" and not self._no_manifest:
            self._deploy_cursor_hooks(wanted)
        return json.dumps(
            {
                "roots": [str(r) for r in roots],
                "sources": names,
            }
        )

    @prompt(name="deploy-harness")
    @agent_instructions
    def generate(
        self,
        source: str | None = None,
        name_filter: str | None = None,
        deploy_path: str | None = None,
        code_language: str | None = None,
    ) -> str:
        """With no IDE given, AskQuestion: Which IDE? Cursor | VS Code | Kilo."""
        """Set context.type to the chosen IDE before running."""
        self._require_implemented()
        """With no name filter given, AskQuestion: all toolsets (recommended) / enter a substring."""
        """With no deploy path given, call suggested_deploy_path, then AskQuestion: deploy to that suggested path (recommended) / enter another path."""
        """With no code_language given, AskQuestion: Python (recommended) | TypeScript."""
        """With no transport given, AskQuestion: MCP (recommended) | CLI. When MCP is chosen, pass arguments.mcp=true to write_deploy."""
        """When requested, pass arguments.no_manifest=true to write_deploy for path-based no-manifest deployment."""
        """Pass the chosen language as arguments.code_language to write_deploy."""
        self.suggested_deploy_path()
        """With no source: walk context_tools/ and utilities/, generate each source into the deploy area, also write Harness prompts (/deploy-harness, /clean-harness). Generate is the deploy — no separate deploy. Do not confirm the scanned list. Overwrite generated files. Remove files this generate did not write. Save the IDE."""
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
            legacy = bool(state.get("legacy"))
            code_language = state.get("code_language") or _DEFAULT_CODE_LANGUAGE
            no_manifest = bool(state.get("no_manifest"))
            mcp = bool(state.get("mcp"))
        except (OSError, json.JSONDecodeError):
            saved = None
            deploy_path = ""
            legacy = False
            code_language = _DEFAULT_CODE_LANGUAGE
            no_manifest = False
            mcp = False
        if not saved:
            raise RuntimeError("no saved IDE")
        self.type = saved
        return self.write_deploy(
            deploy_path=deploy_path,
            legacy=legacy,
            code_language=code_language,
            no_manifest=no_manifest,
            mcp=mcp,
        )

    @prompt(name="clean-harness")
    @agent_tool
    def clean(self) -> str:
        """Remove this Harness type's deploy files only — not the other IDE."""
        self._require_implemented()
        deploy_path = ""
        path = self._state_path()
        if path.is_file():
            try:
                state = json.loads(path.read_text(encoding="utf-8"))
                saved = state.get("type")
                if saved:
                    self.type = saved
                deploy_path = state.get("deploy_path") or ""
            except (OSError, json.JSONDecodeError):
                deploy_path = ""
        roots = self._write_root_paths(deploy_path)
        removed: list[str] = []
        for root in roots:
            for folder in ("skills", "commands", "prompts", "instructions", "rules"):
                target = root / folder
                if target.is_dir():
                    shutil.rmtree(target)
                    removed.append(str(target))
        if self.type == "Cursor":
            from hooks.dispatch import deploy_dispatch

            hooks_json = self.repo_root / ".cursor" / "hooks.json"
            deploy_dispatch(self.repo_root, set())
            removed.append(str(hooks_json))
        return json.dumps({"roots": [str(r) for r in roots], "removed": removed})
