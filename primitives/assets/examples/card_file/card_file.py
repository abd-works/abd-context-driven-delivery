# @toolset-manifest python -m tools manifest primitives.assets.examples.card_file:CardFile
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
"""Example showing AssetLocator and Asset — load named markdown cards from local files."""
from __future__ import annotations

import inspect
from pathlib import Path

from primitives.assets.assets import Asset, AssetCollection, AssetLocator
from tools.tool import resource, agent_tool, toolset


@toolset
class CardFile:
    """Look up reference cards stored as local markdown files.

    Each card is a .md file beside this class. AssetLocator resolves the file
    by label; Asset reads it; AssetCollection reads all cards in a folder.
    """

    def __init__(self, topic: str = "quick-start") -> None:
        self._topic = topic
        super().__init__()

    @property
    def module_dir(self) -> Path:
        """Directory of this module — AssetLocator resolves card files relative to here."""
        return Path(inspect.getfile(type(self))).resolve().parent

    @property
    def domain_slug(self) -> str:
        """Slug used as the fallback section-file name."""
        return "card-file"

    @property
    @resource
    def topic(self) -> str:
        """The label of the card currently set as the default topic."""
        return self._topic

    @agent_tool
    def read_card(self, label: str) -> str:
        """Read a reference card by label. Returns its full markdown content."""
        locator = AssetLocator(self, label=label)
        return Asset(locator.locate()).collect()

    @agent_tool
    def read_all(self) -> str:
        """Read every card in the cards/ subfolder and return them merged."""
        locator = AssetLocator(self, label="cards")
        return AssetCollection(locator.locate()).merged()

    @agent_tool
    def set_topic(self, label: str) -> str:
        """Switch the default topic to a different card label."""
        self._topic = label
        return f"Topic set to: {label}"
