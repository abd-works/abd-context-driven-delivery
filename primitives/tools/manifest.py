"""Assemble toolset manifest signatures from self-describing members."""
from __future__ import annotations

from typing import Any, Protocol

from tools.types import ManifestDocument, SignatureEntry


class _SignatureContributor(Protocol):
    """One manifest member - adds its own entry under its name."""

    name: str

    @property
    def signature_entry(self) -> SignatureEntry: ...

    def add_to_signature(self, signature: ManifestDocument) -> None:
        signature[self.name] = self.signature_entry


class _ManifestBuilder:
    """Build a toolset signature - each member adds itself."""

    def __init__(self, instance: Any) -> None:
        self._instance = instance

    def build(self) -> ManifestDocument:
        from tools.tool import _SignatureReader

        signature: ManifestDocument = {"instructions": self._instance.instructions}
        self._add_meta(signature)
        self._add_constructor(signature, _SignatureReader.instance())
        for contributor in self._contributors():
            contributor.add_to_signature(signature)
        return signature

    def _contributors(self) -> list[_SignatureContributor]:
        from tools.extensions import ToolsetExtensions
        from tools.tool import _discover_resources, _discover_tools

        members: list[_SignatureContributor] = []
        members.extend(_discover_tools(self._instance).values())
        members.extend(_discover_resources(self._instance).values())
        members.extend(ToolsetExtensions.instance().signature_contributors(self._instance))
        return members

    def _add_meta(self, signature: ManifestDocument) -> None:
        cls = self._instance.__class__
        signature["read_manifest"] = {
            "kind": "meta",
            "instructions": (
                "Author/hook only. Agents must not remanifest — "
                "use the slash/skill catalog and pipe the fence to tools.ps1 run -."
            ),
            "cmd": cls.manifest_command,
            "returns": "manifest",
        }
        signature["invoke"] = {
            "kind": "meta",
            "instructions": (
                "Pipe the YAML fence to stdin from the repo root. "
                "Do not write a request file. Follow response.instructions only."
            ),
            "cmd": cls.run_command,
        }

    def _add_constructor(self, signature: ManifestDocument, reader: Any) -> None:
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
