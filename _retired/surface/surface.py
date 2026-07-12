# generated-using: @surface/surface/surface.py
"""surface — typed API surface; type contract in frontmatter is primary (see surface.md)."""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

_CONFIG_FILE = ".cdd-config.json"
RESERVED_FRONTMATTER_KEYS = frozenset(
    {"type", "type-definitions", "types", "extends", "overrides", "open", "mustOverride", "signature"}
)
EXTENSION_FRONTMATTER_KEYS = frozenset({"extends", "overrides", "open", "mustOverride"})


class IDE(str, Enum):
    CURSOR = "cursor"
    VSCODE = "vscode"

    @classmethod
    def detect(cls) -> IDE | None:
        term_prog = os.environ.get("TERM_PROGRAM", "")
        if "cursor" in term_prog.lower():
            return cls.CURSOR
        if "vscode" in term_prog.lower():
            return cls.VSCODE
        return None


@dataclass
class Surface:
    """Minimal CDD primitive — a folder `{surface}/` with paired agentic and API surfaces."""

    path: Path

    def __post_init__(self) -> None:
        self.path = self.path.resolve()

    def opening_description(self) -> str:
        doc = type(self).__doc__ or ""
        return doc.strip().replace("{surface}", self.name)

    @property
    def folder(self) -> Path:
        return self.path

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def agentic_surface(self) -> Path:
        return self.path / f"{self.name}.md"

    @property
    def api_surface(self) -> Path:
        return self.path / f"{self.name}.py"

    @property
    def type_contract(self) -> Surface.TypeContract:
        return Surface.TypeContract.from_agentic_surface(self.agentic_surface)

    @property
    def scaffold(self) -> Surface.Scaffold:
        return Surface.Scaffold(self)

    @property
    def alignment(self) -> Surface.Alignment:
        return Surface.Alignment(self)

    @property
    def cli(self) -> Surface.Cli:
        return Surface.Cli(self)

    @property
    def deployments(self) -> list[Surface.Deployment]:
        config = self._read_config()
        raw = config.get("deployments")
        if raw is None and config.get("deploy"):
            raw = [config["deploy"]]
        if not raw:
            return []
        deployments: list[Surface.Deployment] = []
        for entry in raw:
            try:
                deployments.append(
                    Surface.Deployment(
                        ide=IDE(entry["ide"]),
                        target_root=Path(entry["target_root"]),
                        deployed_at=entry.get(
                            "deployed_at", entry.get("deployed_at_utc", "")
                        ),
                    )
                )
            except (KeyError, ValueError, TypeError):
                continue
        return deployments

    @property
    def is_satisfied(self) -> Surface.ValidationResult:
        violations = self.alignment_violations()
        return Surface.ValidationResult(success=not violations, violations=violations)

    def _has_required_files(self) -> bool:
        return (
            (self.path / _CONFIG_FILE).is_file()
            and self.agentic_surface.is_file()
            and self.api_surface.is_file()
            and self.name == self.path.name
        )

    def assert_valid(self) -> None:
        result = self.is_satisfied
        if not result.success:
            raise RuntimeError("; ".join(result.violations))

    def alignment_violations(self) -> list[str]:
        return self.alignment.violations()

    def alignment_suggestions(self) -> list[str]:
        return self.alignment.suggestions()

    def deploy(self, target: Surface.DeployTarget) -> None:
        extend_mod = self._extend_module()
        if extend_mod and extend_mod.implements_extend(
            self, extend_mod.search_roots_for(self)
        ):
            extend_mod.deploy(self, target)
            return
        self.assert_valid()
        self._copy_to_cdd(target)
        self._write_skill_pointer(target)
        Surface.DeployRecord(ide=target.ide, target_root=target.root).save(self)

    def clean(self, target: Surface.DeployTarget) -> None:
        extend_mod = self._extend_module()
        if extend_mod and extend_mod.implements_extend(
            self, extend_mod.search_roots_for(self)
        ):
            extend_mod.clean(self, target)
            return
        self._clean(target)

    def _alignment_violations(self) -> list[str]:
        violations: list[str] = []
        if not self._has_required_files():
            if not (self.path / _CONFIG_FILE).is_file():
                violations.append(f"missing {_CONFIG_FILE} in {self.path}")
            if not self.agentic_surface.is_file():
                violations.append(f"missing {self.name}.md")
            if not self.api_surface.is_file():
                violations.append(f"missing {self.name}.py")
            return violations

        md_path = self.agentic_surface
        py_path = self.api_surface
        fm = Surface.TypeContract.read_frontmatter(md_path)

        try:
            contract = self.type_contract
        except ValueError as exc:
            return [str(exc)]

        api_slugs = contract.api_action_slugs()
        agent_slugs = contract.agent_action_slugs()
        property_names = set(contract.properties)

        body_sections = {
            line[3:].strip()
            for line in md_path.read_text(encoding="utf-8").splitlines()
            if line.startswith("## ")
        }
        missing_sections = contract.action_sections() - body_sections
        if missing_sections:
            violations.append(
                f"{md_path.name} missing ## sections: {sorted(missing_sections)}"
            )

        if contract.type_name == "surface" and any(k in fm for k in EXTENSION_FRONTMATTER_KEYS):
            violations.append(
                f"{md_path.name} has extension frontmatter — plain surface has no extends/open"
            )

        sig_key = Surface.TypeContract.signature_key(contract.type_name)
        if sig_key not in fm and any(
            Surface.TypeContract.is_action_spec(v) for k, v in fm.items() if k not in RESERVED_FRONTMATTER_KEYS
        ):
            violations.append(
                f"{md_path.name} must nest actions and properties under `{sig_key}`"
            )

        documented_cli = self._documented_cli(api_slugs)
        if documented_cli != api_slugs:
            violations.append(
                f"{md_path.name} documented CLI {sorted(documented_cli)} "
                f"!= expected {sorted(api_slugs)}"
            )

        try:
            mod = sys.modules.get(self.__class__.__module__)
            if mod is None:
                spec = importlib.util.spec_from_file_location("_surface_align", py_path)
                if spec is None or spec.loader is None:
                    raise RuntimeError(f"cannot load {py_path}")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
            expected_class = Surface.api_class_name(self.name)
            expected_cli = Surface.cli_class_name(self.name)
            source = py_path.read_text(encoding="utf-8")

            if re.search(r"class \w*Deployer\b", source):
                violations.append(
                    f"{py_path.name} must not define *Deployer classes — "
                    f"use {expected_class} api actions"
                )

            if not hasattr(mod, expected_class):
                violations.append(f"{py_path.name} must define class {expected_class}")
                return violations

            api_cls = getattr(mod, expected_class)
            public_props, public_methods = self._public_members(api_cls)

            for slug in api_slugs:
                if slug not in public_methods:
                    violations.append(
                        f"{expected_class} must implement {slug}() for api action"
                    )

            for prop in sorted(property_names):
                api_name = Surface.TypeContract.api_property_name(prop)
                if api_name not in public_props:
                    violations.append(f"{expected_class} must expose property {api_name}")
                elif prop in Surface.TypeContract.surface_path_properties():
                    path_prop = getattr(self, api_name)
                    if not isinstance(path_prop, Path):
                        violations.append(
                            f"{expected_class}.{api_name} must return path for {prop}"
                        )

            for slug in agent_slugs:
                if slug in public_methods:
                    violations.append(
                        f"{expected_class} must not expose method {slug}() "
                        f"for agent action §{Surface.action_section_title(slug)}"
                    )

            cli_cls = Surface.resolve_cli_class(mod, self.name)
            if cli_cls is None:
                violations.append(
                    f"{py_path.name} must define {expected_class}.Cli "
                    f"or {expected_cli}"
                )
            else:
                cli_cmds = self._cli_subcommands(mod, cli_cls)
                if cli_cmds != api_slugs:
                    violations.append(
                        f"{py_path.name} CLI subcommands {sorted(cli_cmds)} "
                        f"!= expected {sorted(api_slugs)}"
                    )
                for slug in agent_slugs:
                    if slug in cli_cmds:
                        violations.append(
                            f"{py_path.name} must not expose CLI for agent "
                            f"§{Surface.action_section_title(slug)}"
                        )

            for slug in agent_slugs:
                if f'add_parser("{slug}"' in source:
                    violations.append(f'{py_path.name} must not add_parser("{slug}")')

        except Exception as exc:
            violations.append(f"cannot inspect API surface {py_path.name}: {exc}")

        return violations

    def _alignment_suggestions(self) -> list[str]:
        suggestions: list[str] = []
        if not self._has_required_files():
            return suggestions
        try:
            contract = self.type_contract
        except ValueError:
            return suggestions
        mod = sys.modules.get(self.__class__.__module__)
        if mod is None:
            return suggestions
        api_cls = getattr(mod, Surface.api_class_name(self.name), None)
        if api_cls is None:
            return suggestions
        public_props, public_methods = self._public_members(api_cls)
        for name in sorted(public_props - set(contract.properties)):
            contract_key = name.replace("_", "-")
            if contract_key in contract.properties:
                continue
            if name not in {"path", "scaffold"}:
                suggestions.append(f"consider adding property `{contract_key}` to type contract")
        for name in sorted(
            public_methods - contract.api_action_slugs() - contract.agent_action_slugs()
        ):
            suggestions.append(f"consider adding action or property `{name}` to type contract")
        return suggestions

    def _documented_cli(self, api_slugs: set[str]) -> set[str]:
        slug_to_section = {slug: Surface.action_section_title(slug) for slug in api_slugs}
        api_sections = set(slug_to_section.values())
        documented: set[str] = set()
        current: str | None = None
        in_fence = False
        prefix = f"python -m {self.name}"
        for line in self.agentic_surface.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                current = line[3:].strip()
                in_fence = False
                continue
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if not in_fence or current not in api_sections or prefix not in line:
                continue
            rest = line.split(prefix, 1)[1].strip()
            token = rest.split()[0] if rest else ""
            if token:
                documented.add(token)
        return documented

    def _public_members(self, api_cls: type) -> tuple[set[str], set[str]]:
        properties: set[str] = set()
        methods: set[str] = set()
        for name, member in inspect.getmembers(api_cls):
            if name.startswith("_"):
                continue
            if isinstance(member, property):
                properties.add(name)
            elif inspect.isfunction(member) or inspect.ismethoddescriptor(member):
                methods.add(name)
        return properties, methods

    def _cli_subcommands(self, mod, cli_cls: type | None = None) -> set[str]:
        cli_cls = cli_cls or Surface.resolve_cli_class(mod, self.name)
        cli = cli_cls(self)
        parser = cli._build_parser()
        sub = parser._subparsers._group_actions[0]  # type: ignore[attr-defined]
        return {action.dest for action in sub._choices_actions}

    def _clean(self, target: Surface.DeployTarget) -> None:
        self.assert_valid()
        cdd_dst = target.cdd_dir / self.name
        if cdd_dst.exists():
            shutil.rmtree(cdd_dst)
        skill_dst = target.skills_dir / self.name
        if skill_dst.exists():
            shutil.rmtree(skill_dst)

    def _copy_to_cdd(self, target: Surface.DeployTarget) -> None:
        dst = target.cdd_dir / self.name
        if dst.exists():
            shutil.rmtree(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.path, dst)

    def _write_skill_pointer(self, target: Surface.DeployTarget) -> None:
        skill_dir = target.skills_dir / self.name
        skill_dir.mkdir(parents=True, exist_ok=True)
        cdd_rel = f".cdd/{self.name}/{self.name}.md"
        lines = [
            f"# {self.name}",
            "",
            f"read in full → `{cdd_rel}`",
            "",
        ]
        (skill_dir / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")

    def _read_config(self) -> dict:
        config_path = self.path / _CONFIG_FILE
        if not config_path.is_file():
            return {}
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _write_config(self, config: dict) -> None:
        config_path = self.path / _CONFIG_FILE
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    def _extend_module(self):
        extend_py = self.path.parent / "extend" / "extend.py"
        if not extend_py.is_file():
            return None
        spec = importlib.util.spec_from_file_location("_extend_deploy", extend_py)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        sys.modules.setdefault("_extend_deploy", mod)
        spec.loader.exec_module(mod)
        return mod

    class Mode(str, Enum):
        NEW = "new"
        SUBSET = "subset"

    @classmethod
    def api_class_name(cls, folder_name: str) -> str:
        return "".join(
            part.capitalize() for part in folder_name.replace("_", "-").split("-")
        )

    @classmethod
    def cli_class_name(cls, folder_name: str) -> str:
        return f"{cls.api_class_name(folder_name)}Cli"

    @classmethod
    def resolve_cli_class(cls, mod, folder_name: str) -> type:
        api_cls = getattr(mod, cls.api_class_name(folder_name))
        nested = getattr(api_cls, "Cli", None)
        if nested is not None:
            return nested
        return getattr(mod, cls.cli_class_name(folder_name))

    @classmethod
    def action_section_title(cls, slug: str) -> str:
        return slug.replace("_", "-").title().replace("-", "")

    @dataclass(frozen=True)
    class ValidationResult:
        success: bool
        violations: list[str]

    @dataclass(frozen=True)
    class Deployment:
        ide: IDE
        target_root: Path
        deployed_at: str

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
        def cdd_dir(self) -> Path:
            return self.root / ".cdd"

    @dataclass
    class DeployRecord:
        ide: IDE
        target_root: Path
        deployed_at_utc: str = field(
            default_factory=lambda: datetime.now(timezone.utc).isoformat()
        )

        @classmethod
        def load(cls, surface: Surface) -> Surface.DeployRecord | None:
            data = surface._read_config().get("deploy")
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

        def save(self, surface: Surface) -> None:
            record = {
                "ide": self.ide.value,
                "target_root": str(self.target_root.resolve()),
                "deployed_at": self.deployed_at_utc,
            }
            config = surface._read_config()
            config["deploy"] = {**record, "deployed_at_utc": self.deployed_at_utc}
            deployments = list(config.get("deployments") or [])
            deployments = [
                d for d in deployments if d.get("target_root") != record["target_root"]
            ]
            deployments.append(record)
            config["deployments"] = deployments
            surface._write_config(config)

        def as_target(self) -> Surface.DeployTarget:
            return Surface.DeployTarget(ide=self.ide, root=self.target_root)

    @dataclass(frozen=True)
    class TypeContract:
        """Parsed type contract (signature) from `{type}-signature` in agentic-surface frontmatter."""

        type_name: str
        actions: dict[str, dict]
        properties: dict[str, object]
        type_definitions: dict[str, object]

        @staticmethod
        def is_action_spec(value: object) -> bool:
            return isinstance(value, dict) and ("returns" in value or "parameters" in value)

        @classmethod
        def signature_key(cls, type_name: str) -> str:
            return f"{type_name}-signature"

        @classmethod
        def _signature_raw(cls, fm: dict) -> tuple[str, dict]:
            type_name = str(fm.get("type") or "")
            key = cls.signature_key(type_name) if type_name else ""
            if key and isinstance(fm.get(key), dict):
                return type_name, dict(fm[key])
            if isinstance(fm.get("signature"), dict):
                return type_name, dict(fm["signature"])
            reserved = set(RESERVED_FRONTMATTER_KEYS)
            if key:
                reserved.add(key)
            return type_name, {
                k: v for k, v in fm.items() if k not in reserved and not k.endswith("-signature")
            }

        @classmethod
        def read_frontmatter(cls, md_path: Path) -> dict:
            text = md_path.read_text(encoding="utf-8")
            if not text.startswith("---") or yaml is None:
                return {}
            parts = text.split("---", 2)
            if len(parts) < 3:
                return {}
            raw = parts[1]
            try:
                data = yaml.safe_load(raw) or {}
                return data if isinstance(data, dict) else {}
            except Exception:
                for marker in ("type-definitions:", "surface-signature:", "capability-signature:"):
                    if marker in raw:
                        try:
                            contract_raw = raw.split(marker, 1)[0]
                            data = yaml.safe_load(contract_raw) or {}
                            if isinstance(data, dict):
                                data[marker.rstrip(":")] = {}
                                return data
                        except Exception:
                            pass
                return {}

        @classmethod
        def from_agentic_surface(cls, md_path: Path) -> Surface.TypeContract:
            fm = cls.read_frontmatter(md_path)
            if not fm:
                raise ValueError(f"cannot parse type contract from {md_path.name}")
            type_name, raw = cls._signature_raw(fm)
            if not isinstance(raw, dict):
                raw = {}
            type_definitions = raw.pop("type-definitions", None)
            if not isinstance(type_definitions, dict):
                root_defs = fm.get("type-definitions")
                type_definitions = root_defs if isinstance(root_defs, dict) else {}
            actions: dict[str, dict] = {}
            properties: dict[str, object] = {}
            for key, value in raw.items():
                if cls.is_action_spec(value):
                    actions[key] = value
                else:
                    properties[key] = value
            if not actions:
                raise ValueError(f"no actions in type contract ({md_path.name})")
            return cls(type_name, actions, properties, type_definitions)

        def with_subset(
            self,
            *,
            actions: dict[str, dict] | None = None,
            properties: dict[str, object] | None = None,
        ) -> Surface.TypeContract:
            merged_actions = {**self.actions, **(actions or {})}
            merged_properties = {**self.properties, **(properties or {})}
            return Surface.TypeContract(
                self.type_name,
                merged_actions,
                merged_properties,
                self.type_definitions,
            )

        def to_frontmatter_dict(self) -> dict:
            signature: dict[str, object] = {}
            signature.update(self.actions)
            signature.update(self.properties)
            if self.type_definitions:
                signature["type-definitions"] = self.type_definitions
            return {
                "type": self.type_name,
                self.signature_key(self.type_name): signature,
            }

        def to_frontmatter_yaml(self) -> str:
            if yaml is None:
                raise RuntimeError("PyYAML required to render type contract")
            return yaml.safe_dump(
                self.to_frontmatter_dict(),
                sort_keys=False,
                default_flow_style=False,
            ).strip()

        def api_action_slugs(self) -> set[str]:
            return {slug for slug, spec in self.actions.items() if "parameters" in spec}

        def agent_action_slugs(self) -> set[str]:
            return set(self.actions) - self.api_action_slugs()

        def action_sections(self) -> set[str]:
            return {Surface.action_section_title(slug) for slug in self.actions}

        @classmethod
        def api_property_name(cls, contract_key: str) -> str:
            return contract_key.replace("-", "_")

        @classmethod
        def surface_path_properties(cls) -> frozenset[str]:
            return frozenset({"agentic-surface", "api-surface"})

    class Scaffold:
        """Association — scaffold api, md, and signature from each other."""

        def __init__(self, surface: Surface) -> None:
            self._surface = surface

        def api_from_signature(
            self,
            *,
            mode: Surface.Mode | None = None,
            contract: Surface.TypeContract | None = None,
            subset: Surface.TypeContract | None = None,
            write: bool = False,
        ) -> str:
            mode = mode or Surface.Mode.NEW
            contract = self._resolve_contract(mode, contract, subset)
            class_name = Surface.api_class_name(self._surface.name)
            cli_name = Surface.cli_class_name(self._surface.name)
            description = self._surface.opening_description()
            lines = [
                f'"""{description}"""',
                "from __future__ import annotations",
                "",
                "from dataclasses import dataclass",
                "from pathlib import Path",
                "",
                "",
                "@dataclass",
                f"class {class_name}:",
                f'    """{description}"""',
                "    path: Path",
                "",
            ]
            for prop in sorted(contract.properties):
                lines.append(f"    @property")
                lines.append(f"    def {prop}(self):")
                lines.append(f"        raise NotImplementedError('{prop}')")
                lines.append("")
            for slug in sorted(contract.api_action_slugs()):
                params = contract.actions[slug].get("parameters") or {}
                if params == "none" or params == {}:
                    arg_list = "self"
                else:
                    arg_list = "self, " + ", ".join(f"{name}: object" for name in params)
                lines.append(f"    def {slug}({arg_list}) -> None:")
                lines.append(f'        """§ {Surface.action_section_title(slug)}."""')
                lines.append("        raise NotImplementedError()")
                lines.append("")
            lines.extend(
                [
                    "",
                    f"class {cli_name}:",
                    f'    """Routes python -m {self._surface.name} to {class_name} api actions."""',
                    "",
                    f"    def __init__(self, surface: {class_name}) -> None:",
                    "        self._surface = surface",
                    "",
                    "    def _build_parser(self):",
                    "        import argparse",
                    "",
                    f'        parser = argparse.ArgumentParser(description="{self._surface.name}")',
                    '        sub = parser.add_subparsers(dest="command")',
                    "        sub.required = True",
                ]
            )
            for slug in sorted(contract.api_action_slugs()):
                lines.append(f'        sub.add_parser("{slug}")')
            lines.append("        return parser")
            content = "\n".join(lines) + "\n"
            if write:
                self._surface.api_surface.write_text(content, encoding="utf-8")
            return content

        def md_from_signature(
            self,
            *,
            mode: Surface.Mode | None = None,
            contract: Surface.TypeContract | None = None,
            subset: Surface.TypeContract | None = None,
            write: bool = False,
        ) -> str:
            mode = mode or Surface.Mode.NEW
            contract = self._resolve_contract(mode, contract, subset)
            body_lines = [
                f"## {Surface.api_class_name(self._surface.name)}",
                "",
                self._surface.opening_description(),
                "",
            ]
            for slug in sorted(contract.actions):
                title = Surface.action_section_title(slug)
                body_lines.append(f"## {title}")
                body_lines.append("")
                body_lines.append(f"{{Describe § {title} behaviour.}}")
                body_lines.append("")
                if slug in contract.api_action_slugs():
                    body_lines.append("```")
                    body_lines.append(f"python -m {self._surface.name} {slug}")
                    body_lines.append("```")
                    body_lines.append("")
            content = (
                "---\n"
                + contract.to_frontmatter_yaml()
                + "\n---\n"
                + "\n".join(body_lines)
            )
            if write:
                self._surface.agentic_surface.write_text(content, encoding="utf-8")
            return content

        def signature_from_api(
            self,
            *,
            mode: Surface.Mode | None = None,
            subset: Surface.TypeContract | None = None,
            write: bool = False,
        ) -> Surface.TypeContract:
            mode = mode or Surface.Mode.NEW
            inferred = self._infer_contract_from_api()
            if mode == Surface.Mode.SUBSET:
                if subset is None:
                    raise ValueError("subset contract required when mode is subset")
                if self._surface.agentic_surface.is_file():
                    try:
                        base = self._surface.type_contract
                    except ValueError:
                        base = inferred
                else:
                    base = inferred
                contract = base.with_subset(
                    actions=subset.actions,
                    properties=subset.properties,
                )
            else:
                contract = inferred
            if write and self._surface.agentic_surface.is_file():
                text = self._surface.agentic_surface.read_text(encoding="utf-8")
                if text.startswith("---"):
                    parts = text.split("---", 2)
                    body = parts[2] if len(parts) > 2 else ""
                else:
                    body = text
                self._surface.agentic_surface.write_text(
                    "---\n" + contract.to_frontmatter_yaml() + "\n---" + body,
                    encoding="utf-8",
                )
            return contract

        def _resolve_contract(
            self,
            mode: Surface.Mode,
            contract: Surface.TypeContract | None,
            subset: Surface.TypeContract | None,
        ) -> Surface.TypeContract:
            if contract is not None:
                base = contract
            elif self._surface.agentic_surface.is_file():
                base = self._surface.type_contract
            else:
                raise ValueError("contract required when agentic surface is missing")
            if mode == Surface.Mode.SUBSET:
                if subset is None:
                    raise ValueError("subset contract required when mode is subset")
                return base.with_subset(
                    actions=subset.actions,
                    properties=subset.properties,
                )
            return base

        def _infer_contract_from_api(self) -> Surface.TypeContract:
            py_path = self._surface.api_surface
            if not py_path.is_file():
                raise ValueError(f"missing API surface {py_path.name}")
            mod = sys.modules.get(self._surface.__class__.__module__)
            if mod is None:
                spec = importlib.util.spec_from_file_location("_surface_scaffold", py_path)
                if spec is None or spec.loader is None:
                    raise RuntimeError(f"cannot load {py_path}")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
            class_name = Surface.api_class_name(self._surface.name)
            api_cls = getattr(mod, class_name)
            public_props, public_methods = self._surface._public_members(api_cls)
            scaffold_assoc = {
                "alignment",
                "cli",
                "scaffold",
                "type_contract",
            }
            properties: dict[str, object] = {
                "agentic-surface": "path",
                "api-surface": "path",
            }
            for name in sorted(public_props - {"path", "agentic_surface", "api_surface"}):
                if name not in scaffold_assoc:
                    properties[name.replace("_", "-")] = "inferred"
            actions: dict[str, dict] = {}
            for name in sorted(public_methods):
                method = getattr(api_cls, name)
                sig = inspect.signature(method)
                params = [
                    p
                    for p in sig.parameters
                    if p not in ("self", "cls") and sig.parameters[p].kind
                    not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
                ]
                if params:
                    actions[name] = {
                        "parameters": {p: "inferred" for p in params},
                        "returns": "void",
                    }
            fm = (
                Surface.TypeContract.read_frontmatter(self._surface.agentic_surface)
                if self._surface.agentic_surface.is_file()
                else {}
            )
            type_name = str(fm.get("type") or self._surface.name)
            type_definitions = fm.get("type-definitions") or {}
            if not isinstance(type_definitions, dict):
                type_definitions = {}
            return Surface.TypeContract(type_name, actions, properties, type_definitions)

    class Alignment:
        """Association — aligns frontmatter type contract with agentic body and API."""

        def __init__(self, surface: Surface) -> None:
            self._surface = surface

        def violations(self) -> list[str]:
            return self._surface._alignment_violations()

        def suggestions(self) -> list[str]:
            return self._surface._alignment_suggestions()

    class Cli:
        """Association — routes `python -m {surface} …` to api actions on the surface."""

        def __init__(self, surface: Surface | None = None) -> None:
            self._surface = surface
            self._source_root = (
                surface.path.parent
                if surface is not None
                else Path(__file__).resolve().parent.parent
            )

        def execute(self, argv: list[str]) -> int:
            parser = self._build_parser()
            args = parser.parse_args(argv)
            return self._dispatch(args, parser)

        def deploy_all(
            self,
            target: Surface.DeployTarget,
            *,
            source_root: Path | None = None,
            recursive: bool = False,
        ) -> int:
            surfaces = self._discover(source_root or self._source_root, recursive=recursive)
            if not surfaces:
                print(f"no surfaces found under {source_root or self._source_root}")
                return 1
            for surface in surfaces:
                surface.deploy(target)
                print(f"deployed '{surface.name}' → {target.ide.value} {target.root}")
            return 0

        def clean_all(
            self,
            target: Surface.DeployTarget | None = None,
            *,
            source_root: Path | None = None,
            recursive: bool = False,
            surfaces: list[Surface] | None = None,
        ) -> int:
            found = surfaces or self._discover(
                source_root or self._source_root, recursive=recursive
            )
            if not found:
                print(f"no surfaces found under {source_root or self._source_root}")
                return 1

            cleaned: list[str] = []
            if target is not None:
                for surface in found:
                    surface.clean(target)
                    cleaned.append(surface.name)
            else:
                for surface in found:
                    record = Surface.DeployRecord.load(surface)
                    if record is None:
                        continue
                    surface.clean(record.as_target())
                    cleaned.append(surface.name)

            if not cleaned:
                print("nothing to clean")
                return 1
            for name in cleaned:
                print(f"cleaned '{name}'")
            return 0

        def _dispatch(
            self, args: argparse.Namespace, parser: argparse.ArgumentParser
        ) -> int:
            if args.command == "deploy":
                if not args.ide:
                    target = self._prompt_deploy(
                        len(self._discover(self._resolve_source_root(args), args.recursive))
                    )
                else:
                    target = Surface.DeployTarget(
                        ide=IDE(args.ide),
                        root=Path(args.target_root).resolve()
                        if args.target_root
                        else Path.cwd(),
                    )
                return self.deploy_all(
                    target,
                    source_root=self._resolve_source_root(args),
                    recursive=args.recursive,
                )

            if args.command == "clean":
                source_root = self._resolve_source_root(args)
                surfaces = self._discover(source_root, args.recursive)
                if not surfaces:
                    print(f"no surfaces found under {source_root}")
                    return 1
                if args.ide and args.target_root:
                    target = Surface.DeployTarget(
                        ide=IDE(args.ide), root=Path(args.target_root).resolve()
                    )
                    return self.clean_all(target, surfaces=surfaces)
                return self.clean_all(surfaces=surfaces)

            parser.error(f"unknown command: {args.command}")
            return 2

        def _resolve_source_root(self, args: argparse.Namespace) -> Path:
            if args.source_root:
                return Path(args.source_root).resolve()
            return self._source_root

        def _discover(self, root: Path, *, recursive: bool = False) -> list[Surface]:
            pattern = "**/.cdd-config.json" if recursive else "*/.cdd-config.json"
            surfaces: list[Surface] = []
            seen: set[Path] = set()
            for config in sorted(root.glob(pattern)):
                if ".cdd" in config.parts or "{" in str(config):
                    continue
                parent = config.parent.resolve()
                if parent in seen:
                    continue
                seen.add(parent)
                surface = Surface(parent)
                if surface._has_required_files():
                    surfaces.append(surface)
            return surfaces

        def _prompt_deploy(self, count: int) -> Surface.DeployTarget:
            sample = self._surface or Surface(self._source_root / "surface")
            last = Surface.DeployRecord.load(sample)
            detected = IDE.detect()
            ide_options = list(IDE)
            print(f"\nDeploy {count} surface(s). Which IDE?")
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

            workspace_roots = self._detect_workspace_roots()
            custom = len(workspace_roots) + 1
            print("\nWhere is the workspace root to deploy into?")
            for i, root in enumerate(workspace_roots, 1):
                suffix = (
                    "  (last used)" if last and root == last.target_root.resolve() else ""
                )
                print(f"  {i}) {root}{suffix}")
            print(f"  {custom}) Enter a custom path")
            last_root = last.target_root.resolve() if last else None
            default_root = (
                last_root if last_root and last_root in workspace_roots else workspace_roots[0]
            )
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

            print(f"\nDeploy {count} surface(s) → {ide.value} @ {target_root}")
            confirm = input("Confirm? [Y/n]: ").strip().lower()
            if confirm not in ("", "y", "yes"):
                raise SystemExit("Deploy cancelled.")
            return Surface.DeployTarget(ide=ide, root=target_root)

        def _detect_workspace_roots(self) -> list[Path]:
            roots: list[Path] = []
            seen: set[Path] = set()
            cwd = Path.cwd().resolve()

            def _add(p: Path) -> None:
                rp = p.resolve()
                if rp not in seen:
                    seen.add(rp)
                    roots.append(rp)

            for sibling in sorted(cwd.parent.iterdir()):
                if sibling.is_dir() and (sibling / ".git").exists() and sibling != cwd:
                    _add(sibling)

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

        def _build_parser(self) -> argparse.ArgumentParser:
            parser = argparse.ArgumentParser(
                description="surface — deploy and clean all surfaces"
            )
            sub = parser.add_subparsers(dest="command")
            sub.required = True

            deploy_p = sub.add_parser("deploy", help="Deploy all surfaces under source root")
            deploy_p.add_argument("ide", nargs="?", choices=("cursor", "vscode"))
            deploy_p.add_argument("target_root", nargs="?")
            deploy_p.add_argument("--source-root")
            deploy_p.add_argument("--recursive", action="store_true")

            clean_p = sub.add_parser("clean", help="Clean deployed artefacts for all surfaces")
            clean_p.add_argument("ide", nargs="?", choices=("cursor", "vscode"))
            clean_p.add_argument("target_root", nargs="?")
            clean_p.add_argument("--source-root")
            clean_p.add_argument("--recursive", action="store_true")

            return parser


def main(argv: list[str] | None = None) -> int:
    surface = Surface(Path(__file__).resolve().parent)
    return surface.cli.execute(argv if argv is not None else sys.argv[1:])
