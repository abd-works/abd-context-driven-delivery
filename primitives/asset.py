from __future__ import annotations

from .asset_location import AssetLocation
from .markdown_extractor import extract_single


class Asset:
    def __init__(self, location: AssetLocation) -> None:
        self.location = location

    def collect(self) -> str:
        return extract_single(self.location)
