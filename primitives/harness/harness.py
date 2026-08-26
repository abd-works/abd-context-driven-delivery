# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# @toolset-manifest python -m tools manifest harness.harness:Harness
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Harness — deploy context tools and actions into an IDE."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from primitives.actions.action import agent_instructions, agentic_toolset
from tools.tool import agent_tool
from tools.toolset_header import read_toolset_header

_REPO_ROOT = Path(__file__).resolve().parents[2]
_IMPLEMENTED = frozenset({"Cursor", "VS Code"})
_SKIP_DIRS = frozenset({"__pycache__", "examples", "primitives"})
_STALE_ACTION_SKILL_SLUGS = ("grill-context", "workspace", "workflow")
_WALK_TREES = ("context_tools", "utilities")


def _home() -> Path:
    """User home directory. Patchable in tests."""
    return Path.home()


@agentic_toolset
class Harness:
    """Deploy workspace toolsets as IDE skills, prompts, and instructions."""

    def __init__(self, type: str, repo_root: Path | str | None = None) -> None:
        if not type:
            raise TypeError("type is required")
        self.type = type
        self.repo_root = Path(repo_root) if repo_root is not None else _REPO_ROOT

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

    def _is_self_manifest(self, py_file: Path, manifest_command: str) -> bool:
        ref = manifest_command.strip().rsplit(" ", 1)[-1]
        module_path = ref.split(":")[0]
        parts = module_path.split(".")
        if py_file.stem != parts[-1]:
            return False
        if len(parts) >= 2:
            parent = py_file.parent.name.replace("-", "_")
            return parent == parts[-2].replace("-", "_")
        return True

    def _multi_folder_shared_roots(self) -> list[Path]:
        shared: list[Path] = []
        seen: set[Path] = set()
        for base in (self.repo_root, self.repo_root.parent):
            try:
                workspaces = sorted(base.glob("*.code-workspace"))
            except OSError:
                workspaces = []
            for ws in workspaces:
                try:
                    data = json.loads(ws.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                raw_folders = [
                    entry.get("path")
                    for entry in data.get("folders", [])
                    if entry.get("path")
                ]
                if len(raw_folders) < 2:
                    continue
                resolved: list[Path] = []
                for raw in raw_folders:
                    path = Path(raw)
                    resolved.append(
                        path.resolve() if path.is_absolute() else (ws.parent / path).resolve()
                    )
                repo = self.repo_root.resolve()
                covers = False
                for folder in resolved:
                    try:
                        if folder == repo or repo.is_relative_to(folder) or folder.is_relative_to(repo):
                            covers = True
                            break
                    except (ValueError, OSError):
                        continue
                if not covers:
                    continue
                parent = ws.parent.resolve()
                if parent not in seen:
                    seen.add(parent)
                    shared.append(ws.parent)
        return shared

    def _write_root_paths(self) -> list[Path]:
        roots: list[Path] = [self.repo_root / self._ide_folder()]
        if self.type == "Cursor":
            shared = self._multi_folder_shared_roots()
            if shared:
                roots.append(_home() / ".cursor")
                for parent in shared:
                    extra = parent / ".cursor"
                    if extra.resolve() != roots[0].resolve():
                        roots.append(extra)
        deduped: list[Path] = []
        seen: set[Path] = set()
        for root in roots:
            try:
                key = root.resolve()
            except OSError:
                key = root
            if key in seen:
                continue
            seen.add(key)
            deduped.append(root)
        return deduped

    def _source_skill_path(self, ide_root: Path, slug: str) -> Path:
        return ide_root / "skills" / slug / "SKILL.md"

    def _harness_skill_path(self, ide_root: Path) -> Path:
        return ide_root / "skills" / "harness" / "SKILL.md"

    def _harness_prompt_path(self, ide_root: Path) -> Path:
        if self.type == "Cursor":
            return ide_root / "commands" / "harness.md"
        return ide_root / "prompts" / "harness.prompt.md"

    def _write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _write_source_placeholder(self, slug: str, roots: list[Path]) -> None:
        content = f"# {slug}\ngenerated by Harness\n"
        for root in roots:
            self._write_text(self._source_skill_path(root, slug), content)

    def _write_harness_files(self, roots: list[Path]) -> None:
        skill = (
            "# Harness\n"
            "python -m tools manifest harness.harness:Harness\n"
            "python -m tools run _req.yaml\n"
        )
        prompt = skill
        for root in roots:
            self._write_text(self._harness_skill_path(root), skill)
            self._write_text(self._harness_prompt_path(root), prompt)

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

    def _save_ide(self) -> None:
        path = self._state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"type": self.type}, indent=2),
            encoding="utf-8",
        )

    @agent_tool
    def walk(self, name_filter: str = "") -> str:
        """Walk context_tools/ and utilities/ for toolset files. Returns a JSON array."""
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
                    header = read_toolset_header(py_file)
                except ValueError:
                    continue
                if "{" in header.manifest_command:
                    continue
                if not self._is_self_manifest(py_file, header.manifest_command):
                    continue
                slug = py_file.parent.name
                if slug in seen:
                    continue
                if needle and needle not in slug.lower() and needle not in str(py_file).lower():
                    continue
                seen.add(slug)
                results.append(
                    {
                        "skill_slug": slug,
                        "manifest_command": header.manifest_command,
                        "file_path": str(py_file),
                    }
                )
        return json.dumps(results, indent=2)

    @agent_tool
    def write_deploy(self, source: str = "", name_filter: str = "") -> str:
        """Write scanned sources (or one source) plus Harness skill and prompt into the deploy area."""
        self._require_implemented()
        roots = self._write_root_paths()
        if source.strip():
            slugs = [source.strip()]
        else:
            slugs = [entry["skill_slug"] for entry in json.loads(self.walk(name_filter))]
        for slug in slugs:
            self._write_source_placeholder(slug, roots)
        self._write_harness_files(roots)
        self._remove_stale(roots)
        self._save_ide()
        return json.dumps({"roots": [str(r) for r in roots], "sources": slugs})

    @agent_instructions
    def generate(self, source: str | None = None, name_filter: str | None = None) -> str:
        """With no IDE given, AskQuestion: Which IDE? Cursor | VS Code."""
        self._require_implemented()
        """With no name filter given, AskQuestion: all toolsets (recommended) / enter a substring."""
        """With no source: walk context_tools/ and utilities/, generate each source into the deploy area, also write a Harness skill and a Harness prompt. Generate is the deploy — no separate deploy. Do not confirm the scanned list. Overwrite generated files. Remove stale shortcuts and old slugs. Save the IDE."""
        """With a source: write that source into the deploy area."""
        """With type Claude, Codex, or ChatGPT: must not implement yet."""
        self.walk()
        self.write_deploy()
        return ""
