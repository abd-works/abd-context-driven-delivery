from __future__ import annotations

from pathlib import Path
from typing import Any

from .declared_member import DeclaredMember
from .instruction import Instruction
from .instruction_routing import active_resource, format_keys, path_for_name, path_for_template


class DeclaredProperty(DeclaredMember):
    def __init__(
        self,
        name: str | None = None,
        *,
        label: str | None = None,
        target: str | None = None,
        active_key: str | None = None,
        member_type: str = "Instruction",
    ) -> None:
        super().__init__(name=name or "", label=label, target=target)
        self.active_key = active_key
        self.member_type = member_type
        self._name_from_attribute = name is None

    def __set_name__(self, owner: type[Any], attribute_name: str) -> None:
        if self._name_from_attribute:
            object.__setattr__(self, "name", attribute_name)

    def route(self, instance: Any) -> Instruction:
        module_dir = Path(getattr(instance, "module_dir", Path(".")))
        domain_slug = getattr(instance, "toolset_name", getattr(instance, "domain_slug", module_dir.name))
        if self.target:
            target_value = getattr(instance, self.target, None)
            if callable(target_value):
                target_value = target_value()
            if isinstance(target_value, str) and target_value.strip():
                return Instruction(target_value.strip(), module_dir, domain_slug=domain_slug)
        if self.name == "template":
            path_text = path_for_template(
                module_dir,
                domain_slug,
                active_resource(instance, self.active_key),
            )
        else:
            path_text = path_for_name(module_dir, self.name)
        return Instruction(path_text, module_dir, domain_slug=domain_slug)

    def discover_keys(self, instance: Any) -> list[str] | None:
        module_dir = Path(getattr(instance, "module_dir", Path(".")))
        keys = format_keys(module_dir)
        return keys if keys else []

    def resolve_root(self, instance: Any) -> Path:
        module_dir = Path(getattr(instance, "module_dir", Path(".")))
        instruction = self.route(instance)
        if instruction.text.startswith("§"):
            return module_dir
        normalized = instruction.text.rstrip("/")
        return (module_dir / normalized).resolve()
