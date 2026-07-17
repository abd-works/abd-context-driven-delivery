"""BDD spec for asset.py — AssetLocation, AssetLocator, Asset, AssetCollection."""
import sys
import tempfile
from pathlib import Path

from expects import be_empty, be_none, contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_CLEAN_ENGINEERING_DIR = _REPO_ROOT / "clean_engineering"
_BDD_DIR = _REPO_ROOT / "bdd"


with description("AssetLocator"):
    with context("locating shared examples on a clean-engineering host"):
        with before.each:
            from primitives.asset_location import AssetLocator

            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                fidelity = "language"
                format = "python"

            self.location = AssetLocator(_Host(), "examples").locate()

        with it("should resolve to kind folder"):
            expect(self.location.kind).to(equal("folder"))

        with it("should resolve to clean_engineering/examples"):
            expect(self.location.folder).to(equal((_CLEAN_ENGINEERING_DIR / "examples").resolve()))

    with context("locating concepts on a clean-engineering host"):
        with before.each:
            from primitives.asset_location import AssetLocator

            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"
                toolset_name = "clean_engineering"

            self.location = AssetLocator(_Host(), "concepts").locate()

        with it("should resolve to kind section"):
            expect(self.location.kind).to(equal("section"))

        with it("should point at the clean_engineering markdown file"):
            expect(self.location.section_file.is_file()).to(equal(True))

    with context("locating shared templates on a clean-engineering host"):
        with before.each:
            from primitives.asset_location import AssetLocator

            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"
                toolset_name = "clean_engineering"

            self.location = AssetLocator(_Host(), "templates").locate()

        with it("should resolve to kind folder"):
            expect(self.location.kind).to(equal("folder"))

        with it("should resolve to clean_engineering/templates"):
            expect(self.location.folder).to(equal((_CLEAN_ENGINEERING_DIR / "templates").resolve()))

    with context("locating a label that resolves to a folder"):
        with before.each:
            from primitives.asset_location import AssetLocator

            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"

            self.location = AssetLocator(_Host(), "fidelities").locate()

        with it("should resolve to kind folder"):
            expect(self.location.kind).to(equal("folder"))

        with it("should have a non-None folder path"):
            expect(self.location.folder).not_to(be_none)


with description("Asset"):
    with context("a file-kind location pointing at an existing file"):
        with before.each:
            from primitives.asset import Asset
            from primitives.asset_location import AssetLocation

            with tempfile.TemporaryDirectory() as tmp:
                f = Path(tmp) / "note.md"
                f.write_text("asset content", encoding="utf-8")
                location = AssetLocation("file", Path(tmp), "note", path=f)
                self.result = Asset(location).collect()

        with it("should return the file content"):
            expect(self.result).to(equal("asset content"))

    with context("a file-kind location pointing at a missing file"):
        with before.each:
            from primitives.asset import Asset
            from primitives.asset_location import AssetLocation

            location = AssetLocation(
                "file", Path("/nonexistent"), "x", path=Path("/nonexistent/x.md")
            )
            self.result = Asset(location).collect()

        with it("should return an empty string"):
            expect(self.result).to(be_empty)

    with context("a section-kind location pointing at the clean-engineering concepts section"):
        with before.each:
            from primitives.asset import Asset
            from primitives.asset_location import AssetLocation

            location = AssetLocation(
                "section",
                _CLEAN_ENGINEERING_DIR,
                "clean_engineering",
                section_file=_CLEAN_ENGINEERING_DIR / "clean_engineering.md",
                section_heading="Concepts",
            )
            self.result = Asset(location).collect()

        with it("should return content containing Concepts"):
            expect(self.result).to(contain("Concepts"))


with description("AssetCollection"):
    with context("a folder-kind location pointing at the bdd rules folder"):
        with before.each:
            from primitives.asset_collection import AssetCollection
            from primitives.asset_location import AssetLocation

            location = AssetLocation("folder", _BDD_DIR, "bdd", folder=_BDD_DIR / "rules")
            self.collection = AssetCollection(location)

        with it("should collect a non-empty dict of rule files"):
            result = self.collection.collect()
            expect(len(result) > 0).to(equal(True))

        with it("should merge all collected items into a single non-empty string"):
            merged = self.collection.merged()
            expect(len(merged) > 0).to(equal(True))
