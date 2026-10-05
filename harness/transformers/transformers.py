"""Transformers — agent toolset that loads a practice transformer and renders logical templates."""

from __future__ import annotations

from pathlib import Path

from jinja2 import ChoiceLoader, Environment, FileSystemLoader

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.mcp.mcp_server import mcp
from harness.sketch.sketch_outline import SketchLens, SketchOutline
from harness.transformers.transformer import Transformer
from installation.files import Skill
from practices.bdd.bdd import Bdd
from practices.clean_engineering.clean_engineering import CleanEngineering
from practices.ddd.ddd import Ddd
from practices.stories.stories import Stories


@agent_toolset
class Transformers:
    domain_slug = "transformers"

    @mcp
    @Skill
    @agent_tool
    def transform_sketch(self, sketch: str) -> list:
        """Load each practice transformer from the sketch and render logical templates on that root."""
        practices = self.determine_practices_from(sketch)
        environment = _environment_for(practices)
        practice_models = []
        for practice in practices:
            transformer_type = getattr(getattr(practice, "model", None), "transformer", None)
            if transformer_type is None:
                continue
            node = transformer_type.load(sketch)
            if not isinstance(node, Transformer):
                continue
            node.attach_environment(environment)
            node.render("logical")
            practice_models.append(node)
        return practice_models

    def determine_practices_from(self, sketch: str) -> list:
        outline = SketchOutline(sketch)
        practices = []
        if outline.holds(SketchLens.stories):
            practices.append(Stories())
        if outline.holds(SketchLens.clean_engineering):
            practices.append(CleanEngineering())
        if outline.holds(SketchLens.behavior_driven_development):
            practices.append(Bdd())
        if outline.holds(SketchLens.domain_driven_design):
            practices.append(Ddd())
        return practices


def _environment_for(practices: list) -> Environment:
    loaders = []
    for practice in practices:
        transformer_type = getattr(getattr(practice, "model", None), "transformer", None)
        root = getattr(transformer_type, "logical_template_root", None)
        if root is None:
            continue
        loaders.append(FileSystemLoader(str(root)))
    loaders.append(FileSystemLoader(str(Path(__file__).resolve().parent)))
    loader = loaders[0] if len(loaders) == 1 else ChoiceLoader(loaders)
    return Environment(loader=loader, autoescape=False)
