"""cdd-capability — discover, parse, deploy, and clean CDD capabilities."""
from __future__ import annotations

import argparse
import json
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

_CONFIG_FILE = ".cdd-config.json"

class IDE(str, Enum):
    CURSOR = "cursor"
    VSCODE = "vscode"

@dataclass(frozen=True)
class CapabilityCommand:
    title: str
    description: str

    @property
    def slug(self) -> str:
        return "-".join(
            part
            for part in "".join(
                ch.lower() if ch.isalnum() else " " for ch in self.title
            ).split()
        )

@dataclass(frozen=True)
class InjectedEntry:
    """One entry in the capability's `injected` config list."""
    capability: str          # name of the source capability (must be deployed to skills/)
    commands: list[str]      # slugs to inject; empty = inject all injectable commands

    @classmethod
    def from_dict(cls, data: dict) -> InjectedEntry:
        return cls(
            capability=data["capability"],
            commands=data.get("commands", []),
        )

    def to_dict(self) -> dict:
        return {"capability": self.capability, "commands": self.commands}


@dataclass
class Capability:
    path: Path

    def __post_init__(self) -> None:
        self.path = self.path.resolve()

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def md_surface(self) -> Path:
        return self.path / f"{self.name}.md"

    @property
    def api_surface(self) -> Path:
        return self.path / f"{self.name}.py"

    @property
    def is_valid(self) -> bool:
        return (self.path / ".cdd-config.json").is_file()

    @property
    def description(self) -> str:
        """First non-heading line from the capability .md."""
        if not self.md_surface.is_file():
            return ""
        for raw in self.md_surface.read_text(encoding="utf-8").splitlines():
            stripped = raw.strip()
            if stripped and not stripped.startswith("#"):
                return stripped
        return ""

    @property
    def commands(self) -> list[CapabilityCommand]:
        """Sections before the first `---` separator in the capability .md."""
        if not self.md_surface.is_file():
            return []
        cmds: list[CapabilityCommand] = []
        current_title: str | None = None
        current_desc: str = ""
        for raw in self.md_surface.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line == "---":
                break
            if raw.startswith("## "):
                if current_title:
                    cmds.append(CapabilityCommand(current_title, current_desc))
                current_title = raw[3:].strip()
                current_desc = ""
                continue
            if current_title and not current_desc and line and not line.startswith("#"):
                current_desc = line
        if current_title:
            cmds.append(CapabilityCommand(current_title, current_desc))
        return cmds

    @property
    def injectable_commands(self) -> list[str]:
        """Command slugs this capability allows others to inject (from config)."""
        return _read_config(self).get("injectable", [])

    @property
    def injected(self) -> list[InjectedEntry]:
        """Capabilities injected into this one (from config)."""
        return [InjectedEntry.from_dict(e) for e in _read_config(self).get("injected", [])]

    def assert_valid(self) -> None:
        if not self.is_valid:
            raise RuntimeError(
                f"'{self.path}' is not a CDD capability (.cdd-config.json missing)."
            )

@dataclass(frozen=True)
class DeployTarget:
    ide: IDE
    root: Path

    @property
    def skills_dir(self) -> Path:
        if self.ide == IDE.CURSOR:
            return self.root / ".cursor" / "skills"
        return self.root / ".github" / "skills"

    @property
    def commands_dir(self) -> Path:
        if self.ide == IDE.CURSOR:
            return self.root / ".cursor" / "commands"
        return self.root / ".github" / "prompts"

    @property
    def command_suffix(self) -> str:
        return ".md" if self.ide == IDE.CURSOR else ".prompt.md"

    @property
    def cdd_dir(self) -> Path:
        """Shared .cdd/ folder where full capability source is copied."""
        return self.root / ".cdd"

@dataclass
class DeployRecord:
    ide: IDE
    target_root: Path
    deployed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def load(cls, capability: Capability) -> DeployRecord | None:
        config = _read_config(capability)
        data = config.get("deploy")
        if not data:
            return None
        try:
            return cls(
                ide=IDE(data["ide"]),
                target_root=Path(data["target_root"]),
                deployed_at_utc=data.get("deployed_at_utc", ""),
            )
        except (KeyError, ValueError):
            return None

    def save(self, capability: Capability) -> None:
        config = _read_config(capability)
        config["deploy"] = {
            "ide": self.ide.value,
            "target_root": str(self.target_root.resolve()),
            "deployed_at_utc": self.deployed_at_utc,
        }
        _write_config(capability, config)

    def as_target(self) -> DeployTarget:
        return DeployTarget(ide=self.ide, root=self.target_root)

class CapabilityDeployer:
    """Copies a Capability to an IDE target and generates IDE wrappers."""

    def deploy(self, capability: Capability, target: DeployTarget) -> None:
        capability.assert_valid()
        # 1. Full capability source → .cdd/{name}/
        cdd_dst = target.cdd_dir / capability.name
        self._copy_capability(capability, cdd_dst)
        # 2. Thin SKILL.md → .cursor/skills/{name}/SKILL.md
        self._write_skill_wrapper(capability, target)
        # 3. Thin command file per ## section → .cursor/commands/
        self._write_command_wrappers(capability, target)
        DeployRecord(ide=target.ide, target_root=target.root).save(capability)

    def clean(self, capability: Capability, target: DeployTarget) -> None:
        capability.assert_valid()
        cdd_dst = target.cdd_dir / capability.name
        if cdd_dst.exists():
            shutil.rmtree(cdd_dst)
        skill_dst = target.skills_dir / capability.name
        if skill_dst.exists():
            shutil.rmtree(skill_dst)
        for cmd in capability.commands:
            cmd_file = (
                target.commands_dir
                / f"{capability.name}-{cmd.slug}{target.command_suffix}"
            )
            if cmd_file.exists():
                cmd_file.unlink()

    def deploy_like_last(self, capability: Capability) -> DeployTarget:
        """Repeat the most recent recorded deployment. Returns the target used."""
        record = DeployRecord.load(capability)
        if record is None:
            raise RuntimeError(
                f"No previous deployment for '{capability.name}'. "
                "Run deploy <ide> <target> first."
            )
        target = record.as_target()
        self.deploy(capability, target)
        return target

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _copy_capability(self, capability: Capability, dst: Path) -> None:
        if dst.exists():
            shutil.rmtree(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(capability.path, dst)

    def _write_skill_wrapper(self, capability: Capability, target: DeployTarget) -> None:
        """SKILL.md listing own commands then injected commands per entry."""
        skill_dir = target.skills_dir / capability.name
        skill_dir.mkdir(parents=True, exist_ok=True)
        cdd_rel = f".cdd/{capability.name}/{capability.name}.md"

        lines = [
            f"# {capability.name}",
            "",
            capability.description,
            "",
            f"read in full → `{cdd_rel}`",
            "",
        ]

        # Own commands
        own_slugs = {cmd.slug for cmd in capability.commands}
        for cmd in capability.commands:
            lines.append(f"## {cmd.title}")
            if cmd.description:
                lines.append(cmd.description)
            lines.append(f"read `@{capability.name}` §{cmd.title}")
            lines.append("")

        # Injected commands — collision: if same slug exists in own, append "also" reference
        for entry in capability.injected:
            source = entry.capability
            effective = entry.commands if entry.commands else _resolve_injectable(source, target)
            for slug in effective:
                title = slug.replace("-", " ").title()
                if slug in own_slugs:
                    # Collision — append to the existing own section by noting base
                    lines.append(f"<!-- {source} also provides {slug} — see @{source} §{title} -->")
                else:
                    lines.append(f"## {title}")
                    lines.append(f"read `@{source}` §{title}")
                    lines.append("")

        (skill_dir / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")

    def _write_command_wrappers(self, capability: Capability, target: DeployTarget) -> None:
        """Command files for own + injected commands. Collision → merged file."""
        target.commands_dir.mkdir(parents=True, exist_ok=True)
        cdd_rel = f".cdd/{capability.name}/{capability.name}.md"
        own_slugs = {cmd.slug: cmd for cmd in capability.commands}

        # Own command files
        for cmd in capability.commands:
            path = target.commands_dir / f"{capability.name}-{cmd.slug}{target.command_suffix}"
            path.write_text(
                f"# {capability.name} — {cmd.title}\n\n"
                f"{cmd.description or ''}\n\n"
                f"read `@{capability.name}` §{cmd.title}\n",
                encoding="utf-8",
            )

        # Injected command files — collision → add base reference to existing file
        for entry in capability.injected:
            source = entry.capability
            effective = entry.commands if entry.commands else _resolve_injectable(source, target)
            for slug in effective:
                title = slug.replace("-", " ").title()
                path = target.commands_dir / f"{capability.name}-{slug}{target.command_suffix}"
                if slug in own_slugs:
                    # Append base reference to the already-written own command file
                    existing = path.read_text(encoding="utf-8").rstrip()
                    path.write_text(
                        existing + f"\n\nalso read `@{source}` §{title}\n",
                        encoding="utf-8",
                    )
                else:
                    path.write_text(
                        f"# {capability.name} — {title}\n\n"
                        f"read `@{source}` §{title}\n",
                        encoding="utf-8",
                    )

class CapabilityCli:
    """Parses argv and dispatches to CapabilityDeployer or subclass commands."""

    def __init__(self, capability: Capability) -> None:
        self._capability = capability
        self._deployer = CapabilityDeployer()

    def execute(self, argv: list[str]) -> int:
        parser = self._build_parser()
        args = parser.parse_args(argv)
        return self._dispatch(args, parser)

    def _dispatch(self, args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
        cmd = args.command

        if cmd == "list":
            for c in self._capability.commands:
                print(f"{c.slug}: {c.title}")
            return 0

        if cmd == "deploy":
            if not args.ide:
                target = self._prompt_deploy()
            else:
                target = DeployTarget(
                    ide=IDE(args.ide),
                    root=Path(args.target_root) if args.target_root else Path.cwd(),
                )
            self._deployer.deploy(self._capability, target)
            print(f"deployed '{self._capability.name}' → {target.ide.value} {target.root}")
            return 0

        if cmd == "clean":
            if args.ide and args.target_root:
                target = DeployTarget(ide=IDE(args.ide), root=Path(args.target_root))
                self._deployer.clean(self._capability, target)
            else:
                record = DeployRecord.load(self._capability)
                if record is None:
                    parser.error(f"No deploy record for '{self._capability.name}'.")
                self._deployer.clean(self._capability, record.as_target())
            print(f"cleaned '{self._capability.name}'")
            return 0

        if cmd == "inject":
            source_path = Path(args.source).resolve()
            source = Capability(source_path)
            source.assert_valid()
            requested = [s.strip() for s in args.commands.split(",")] if args.commands else []
            _cmd_inject(self._capability, source, requested)
            injected_str = ", ".join(requested) if requested else "all injectable"
            print(f"injected '{source.name}' ({injected_str}) → '{self._capability.name}'")
            return 0

        parser.error(f"unknown command: {cmd}")
        return 2

    def _prompt_deploy(self) -> DeployTarget:
        """Interactive questionnaire: IDE → target root → confirm."""
        last = DeployRecord.load(self._capability)

        # --- IDE ---
        detected = _detect_ide()
        ide_options = list(IDE)
        print("\nWhich IDE are you deploying to?")
        for i, opt in enumerate(ide_options, 1):
            suffix = ""
            if detected and opt == detected:
                suffix = "  (detected)"
            elif last and opt == last.ide:
                suffix = "  (last used)"
            print(f"  {i}) {opt.value}{suffix}")
        default_ide = detected or (last.ide if last else IDE.CURSOR)
        raw = input(f"IDE [{default_ide.value}]: ").strip().lstrip("\ufeff")
        if raw == "":
            ide = default_ide
        elif raw.isdigit() and 1 <= int(raw) <= len(ide_options):
            ide = ide_options[int(raw) - 1]
        elif raw in (o.value for o in IDE):
            ide = IDE(raw)
        else:
            raise ValueError(f"Invalid IDE choice: {raw!r}")

        # --- Target root ---
        workspace_roots = _detect_workspace_roots()
        CUSTOM = len(workspace_roots) + 1
        print("\nWhere is the workspace root to deploy into?")
        for i, root in enumerate(workspace_roots, 1):
            suffix = "  (last used)" if last and root == last.target_root.resolve() else ""
            print(f"  {i}) {root}{suffix}")
        print(f"  {CUSTOM}) Enter a custom path")
        last_root = last.target_root.resolve() if last else None
        default_root = last_root if last_root and last_root in workspace_roots else workspace_roots[0]
        raw = input(f"Root [{default_root}]: ").strip().lstrip("\ufeff")
        if raw == "":
            target_root = default_root
        elif raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(workspace_roots):
                target_root = workspace_roots[idx]
            else:
                target_root = Path(input("Custom path: ").strip().lstrip("\ufeff")).resolve()
        else:
            target_root = Path(raw).resolve()

        # --- Confirm ---
        print(f"\nDeploy '{self._capability.name}' → {ide.value} @ {target_root}")
        confirm = input("Confirm? [Y/n]: ").strip().lower()
        if confirm not in ("", "y", "yes"):
            raise SystemExit("Deploy cancelled.")

        return DeployTarget(ide=ide, root=target_root)

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description=f"{self._capability.name} capability CLI"
        )
        sub = parser.add_subparsers(dest="command")
        sub.required = True

        sub.add_parser("list", help="List parsed commands from the capability .md")

        deploy_p = sub.add_parser("deploy", help="Deploy capability to IDE area")
        deploy_p.add_argument("ide", nargs="?", choices=("cursor", "vscode"),
                              help="Target IDE (omit to repeat last deployment)")
        deploy_p.add_argument("target_root", nargs="?", help="Workspace root to deploy into")

        clean_p = sub.add_parser("clean", help="Remove deployed artefacts")
        clean_p.add_argument("ide", nargs="?", choices=("cursor", "vscode"))
        clean_p.add_argument("target_root", nargs="?")

        inject_p = sub.add_parser("inject", help="Inject commands from another capability")
        inject_p.add_argument("source", help="Path to the source capability")
        inject_p.add_argument("--commands", default="", help="Comma-separated slugs to inject (default: all injectable)")

        return parser

def _cmd_inject(target: Capability, source: Capability, requested: list[str]) -> None:
    """Add or update an injected entry in target's .cdd-config.json."""
    injectable = source.injectable_commands
    if not injectable:
        raise RuntimeError(f"'{source.name}' declares no injectable commands.")
    if requested:
        invalid = [s for s in requested if s not in injectable]
        if invalid:
            raise RuntimeError(
                f"'{source.name}' does not allow injecting: {', '.join(invalid)}. "
                f"Injectable: {', '.join(injectable)}"
            )
    config = _read_config(target)
    entries = config.get("injected", [])
    # Update existing entry for this source or append new one
    for entry in entries:
        if entry.get("capability") == source.name:
            entry["commands"] = requested
            break
    else:
        entries.append({"capability": source.name, "commands": requested})
    config["injected"] = entries
    _write_config(target, config)


def _resolve_injectable(source_name: str, target: DeployTarget) -> list[str]:
    """Read injectable commands from deployed source capability in .cdd/."""
    source_config = target.cdd_dir / source_name / _CONFIG_FILE
    if not source_config.is_file():
        return []
    try:
        data = json.loads(source_config.read_text(encoding="utf-8"))
        return data.get("injectable", [])
    except json.JSONDecodeError:
        return []


def _read_config(capability: Capability) -> dict:
    config_path = capability.path / _CONFIG_FILE
    if not config_path.is_file():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

def _write_config(capability: Capability, config: dict) -> None:
    config_path = capability.path / _CONFIG_FILE
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

def _detect_workspace_roots() -> list[Path]:
    """Return candidate deploy-target workspace roots.

    Strategy (in priority order):
    1. Sibling git repos next to the current working directory.
    2. Git repos found by walking up from cwd.
    3. Fallback: cwd itself.

    Excludes the cdd-capability source repo itself.
    """
    roots: list[Path] = []
    seen: set[Path] = set()
    cwd = Path.cwd().resolve()

    def _add(p: Path) -> None:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            roots.append(rp)

    # 1. Siblings of cwd that are git repos.
    for sibling in sorted(cwd.parent.iterdir()):
        if sibling.is_dir() and (sibling / ".git").exists() and sibling != cwd:
            _add(sibling)

    # 2. Walk up from cwd — each git repo found is a candidate.
    current = cwd
    while True:
        if (current / ".git").exists():
            _add(current)
        parent = current.parent
        if parent == current:
            break
        current = parent

    if not roots:
        _add(cwd)

    return roots

def _detect_ide() -> IDE | None:
    """Best-effort: check env vars set by Cursor and VS Code."""
    term_prog = os.environ.get("TERM_PROGRAM", "")
    if "cursor" in term_prog.lower():
        return IDE.CURSOR
    if "vscode" in term_prog.lower():
        return IDE.VSCODE
    return None

def is_capability(path: Path) -> bool:
    """Return True if path is a CDD capability (has .cdd-config.json)."""
    return Capability(path).is_valid

def list_capabilities(root: Path, *, recursive: bool = False) -> list[Path]:
    """Return all capability folders under root."""
    pattern = "**/.cdd-config.json" if recursive else "*/.cdd-config.json"
    return sorted(p.parent for p in root.glob(pattern))

def main(argv: list[str] | None = None) -> int:
    capability = Capability(Path(__file__).resolve().parent)
    cli = CapabilityCli(capability)
    return cli.execute(argv if argv is not None else __import__("sys").argv[1:])

if __name__ == "__main__":
    raise SystemExit(main())
