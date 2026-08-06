# @toolset-manifest python -m tools manifest context_setup.semantic_indexer:SemanticIndexer
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""SemanticIndexer — broad four-view partitioner for ContextSetup's default_indexer slot.

Used when the user does not select a domain-specific context tool.
Inherits partition() from BaseContextTool unchanged; domain_slug resolves
to "semantic_indexer" (Toolset.toolset_name), scaffold is empty (no
domain-specific file to load), so Partition uses its default four-view
guidance — story / domain / architecture / ux tags without a scaffold.
"""
from __future__ import annotations

from context_tools.base.base_context_tool import BaseContextTool


class SemanticIndexer(BaseContextTool):
    """Four-view semantic indexer — no domain scaffold; tags story/domain/architecture/ux broadly."""
