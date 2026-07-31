"""Extension hooks so peer packages can attach to toolsets without Tools importing them.

Actions, sub-agents, and similar packages register discoverers / handlers here at
import time. Tools only iterates the registry - it never names those packages.
"""
from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping

from tools.types import (
    ManifestDocument,
    RunRequestDocument,
    RunResponseDocument,
    ToolsetInstance,
)

# discoverer(instance) -> mapping of name -> SignatureContributor-like member
MemberDiscoverer = Callable[[ToolsetInstance], Mapping[str, Any]]
CapabilityDetector = Callable[[ToolsetInstance], Iterable[str]]
ToolsetValidator = Callable[[type], None]
RunHandler = Callable[..., RunResponseDocument]


class ToolsetExtensions:
    """Process-wide registry of optional toolset extensions."""

    _instance: ToolsetExtensions | None = None

    def __init__(self) -> None:
        self._signature_discoverers: list[MemberDiscoverer] = []
        self._member_discoverers: dict[str, MemberDiscoverer] = {}
        self._capability_detectors: list[CapabilityDetector] = []
        self._toolset_validators: list[ToolsetValidator] = []
        self._run_handlers: dict[str, RunHandler] = {}

    @classmethod
    def instance(cls) -> ToolsetExtensions:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, extensions: ToolsetExtensions | None) -> None:
        cls._instance = extensions

    def register_signature_discoverer(self, discoverer: MemberDiscoverer) -> MemberDiscoverer:
        self._signature_discoverers.append(discoverer)
        return discoverer

    def register_members(self, key: str, discoverer: MemberDiscoverer) -> MemberDiscoverer:
        self._member_discoverers[key] = discoverer
        return discoverer

    def register_capability_detector(self, detector: CapabilityDetector) -> CapabilityDetector:
        self._capability_detectors.append(detector)
        return detector

    def register_toolset_validator(self, validator: ToolsetValidator) -> ToolsetValidator:
        self._toolset_validators.append(validator)
        return validator

    def register_run_handler(self, kind: str, handler: RunHandler) -> RunHandler:
        self._run_handlers[kind] = handler
        return handler

    def signature_contributors(self, instance: ToolsetInstance) -> list[Any]:
        members: list[Any] = []
        for discoverer in self._signature_discoverers:
            members.extend(discoverer(instance).values())
        return members

    def members(self, key: str, instance: ToolsetInstance) -> Mapping[str, Any]:
        discoverer = self._member_discoverers.get(key)
        if discoverer is None:
            return {}
        return discoverer(instance)

    def extra_capabilities(self, instance: ToolsetInstance) -> list[str]:
        caps: list[str] = []
        for detector in self._capability_detectors:
            caps.extend(detector(instance))
        return caps

    def validate_toolset(self, toolset_cls: type) -> None:
        for validator in self._toolset_validators:
            validator(toolset_cls)

    def run(
        self,
        kind: str,
        request: RunRequestDocument,
        **kwargs: Any,
    ) -> RunResponseDocument:
        handler = self._run_handlers.get(kind)
        if handler is None:
            from tools.tool import RunError

            raise RunError(
                f"no run handler registered for {kind!r}",
                response={"ok": False, "error": f"no run handler for {kind}"},
            )
        return handler(request, **kwargs)
