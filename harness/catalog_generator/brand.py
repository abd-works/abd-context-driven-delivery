"""The catalog's shared files (styles, scripts, and the brand's marks) and the brands a catalog can wear."""
from __future__ import annotations

import shutil
from pathlib import Path

_TEMPLATES = Path(__file__).resolve().parent / "templates"
_COMMONS = _TEMPLATES / "commons"
_BUNDLED_BRAND = _COMMONS / "brand"
_BUNDLED_BRAND_NAME = "abd-works"
_BRANDS = _TEMPLATES / "brands"
_STYLESHEETS = ("foundry-catalog.css", "cdd-board.css")


class UnknownBrand(ValueError):
    """A brand name that is neither a folder nor a brand in the collection; the message lists the known brands."""


class Brand:
    """A brand overlay for the catalog's shared files. ``collection`` is a folder whose children are named brand
    folders; the bundled ``abd-works`` brand is always one of them. ``folder`` is the brand this catalog wears; none
    wears the bundled one."""

    def __init__(self, collection: Path | None = None, folder: Path | None = None) -> None:
        self.collection = Path(collection) if collection is not None else _BRANDS
        self.folder = Path(folder) if folder is not None else None

    def folders(self) -> dict[str, Path]:
        folders = {_BUNDLED_BRAND_NAME: _BUNDLED_BRAND}
        if not self.collection.is_dir():
            return folders
        for child in sorted(self.collection.iterdir()):
            if child.is_dir() and not child.name.startswith("."):
                folders[child.name] = child
        return folders

    def resolve(self, name: str) -> Path | None:
        """The brand folder ``name`` names: a folder path, or a brand in the collection; none for no name."""
        if not name:
            return None
        if Path(name).is_dir():
            return Path(name)
        folders = self.folders()
        if name in folders:
            return folders[name]
        raise UnknownBrand(f"Unknown brand {name!r}. Known brands: {', '.join(sorted(folders))}")

    def apply(self, commons: Path) -> Path:
        """Copy the brand's marks into the catalog's ``commons/brand``."""
        destination = Path(commons) / "brand"
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.folder if self.folder is not None else _BUNDLED_BRAND, destination, dirs_exist_ok=True)
        return destination

    def apply_named(self, out_root: Path, name: str) -> Path:
        commons = Path(out_root) / "commons"
        commons.mkdir(parents=True, exist_ok=True)
        self.folder = self.resolve(name)
        return self.apply(commons)

    def copy_commons(self, out_root: Path) -> Path:
        """Copy the shared styles and scripts into ``out_root/commons``, then the brand's marks over them."""
        commons = Path(out_root) / "commons"
        commons.mkdir(parents=True, exist_ok=True)
        shutil.copytree(_COMMONS, commons, dirs_exist_ok=True)
        for stylesheet in _STYLESHEETS:
            shutil.copy2(_TEMPLATES / stylesheet, commons / stylesheet)
        self.apply(commons)
        return commons
