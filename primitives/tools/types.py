"""Domain document types for the tools public seam.

Named aliases commit the public API to concepts (manifest, run request/response,
schema) instead of exposing raw ``dict[str, Any]`` / ``Any`` in signatures.
Runtime values remain ordinary mappings and YAML-friendly objects.
"""
from __future__ import annotations

from typing import Any, TypeAlias

# Toolset signature / YAML front matter
ManifestDocument: TypeAlias = dict[str, Any]
SignatureEntry: TypeAlias = dict[str, Any]

# CLI run envelope
RunRequestDocument: TypeAlias = dict[str, Any]
RunResponseDocument: TypeAlias = dict[str, Any]

# MCP-shaped member docs and JSON Schema fragments
ToolDocument: TypeAlias = dict[str, Any]
ResourceDocument: TypeAlias = dict[str, Any]
JsonSchema: TypeAlias = dict[str, Any]

# Introspection / YAML leaf values
TypeAnnotation: TypeAlias = Any
YamlValue: TypeAlias = Any
ResourceValues: TypeAlias = dict[str, Any]

# Toolset instance passed through extension hooks
ToolsetInstance: TypeAlias = Any
