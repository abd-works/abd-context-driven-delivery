"""Assemble toolset manifest signatures from self-describing members."""
from __future__ import annotations

from typing import Any, Protocol


class SignatureContributor(Protocol):
    """One manifest member — adds its own entry under its name."""

    name: str

    @property
    def signature_entry(self) -> dict[str, Any]: ...

    def add_to_signature(self, signature: dict[str, Any]) -> None:
        signature[self.name] = self.signature_entry


class ManifestBuilder:
    """Build a toolset signature — each member adds itself."""

    def __init__(self, instance: Any) -> None:
        self._instance = instance

    def build(self) -> dict[str, Any]:
        from tools.tool import SignatureReader

        signature: dict[str, Any] = {"instructions": self._instance.instructions}
        self._add_meta(signature)
        self._add_constructor(signature, SignatureReader.instance())
        for contributor in self._contributors():
            contributor.add_to_signature(signature)
        return signature

    def _contributors(self) -> list[SignatureContributor]:
        from agents.discovery import discover_actions
        from sub_agent.sub_agent import discover_sub_agent_tools
        from tools.tool import discover_resources, discover_tools

        members: list[SignatureContributor] = []
        members.extend(discover_tools(self._instance).values())
        members.extend(discover_sub_agent_tools(self._instance).values())
        members.extend(discover_actions(self._instance).values())
        members.extend(discover_resources(self._instance).values())
        return members

    def _add_meta(self, signature: dict[str, Any]) -> None:
        cls = self._instance.__class__
        signature["read_manifest"] = {
            "kind": "meta",
            "instructions": "Get the latest manifest (this document).",
            "cmd": cls.manifest_command,
            "returns": "manifest",
        }
        signature["invoke"] = {
            "kind": "meta",
            "instructions": "Run one tool or action on a toolset instance.",
            "cmd": cls.run_command,
        }

    def _add_constructor(self, signature: dict[str, Any], reader: Any) -> None:
        cls = self._instance.__class__
        parameters = reader.simple_parameters(cls.__init__)
        if not parameters:
            return
        new_instructions = reader.member_instructions(cls.__init__) or "Create a toolset instance."
        signature["new"] = {
            "kind": "constructor",
            "instructions": new_instructions,
            "parameters": parameters,
        }
