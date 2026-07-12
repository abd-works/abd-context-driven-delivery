from __future__ import annotations

from .asset_location import AssetLocation
from .markdown_extractor import extract_collection, merge_collection


class AssetCollection:
    def __init__(self, location: AssetLocation) -> None:
        self.location = location
        self.collection: dict[str, str] = {}

    def collect(self) -> dict[str, str]:
        self.collection = extract_collection(self.location)
        return self.collection

    def merged(self) -> str:
        if not self.collection:
            self.collect()
        return merge_collection(self.collection)
