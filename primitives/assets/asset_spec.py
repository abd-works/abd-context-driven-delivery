"""BDD spec for asset.py — AssetLocation, AssetLocator, Asset, AssetCollection."""
import sys
import tempfile
from pathlib import Path

from expects import be_empty, be_none, contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "contexts"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

_CLEAN_ENGINEERING_DIR = _REPO_ROOT / "contexts" / "clean_engineering"
_BDD_DIR = _REPO_ROOT / "contexts" / "bdd"


with description("AssetLocator"):
    with context("locating shared examples on a clean-engineering host"):
        with before.each:
            from primitives.assets import AssetLocator

            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                fidelity = "language"
                format = "python"

            self.location = AssetLocator(_Host(), "examples").locate()

        with it("should resolve to kind folder"):
            expect(self.location.kind).to(equal("folder"))

        with it("should resolve to contexts/clean_engineering/examples"):
            expect(self.location.folder).to(equal((_CLEAN_ENGINEERING_DIR / "examples").resolve()))

    with context("locating contexts on a clean-engineering host"):
        with before.each:
            from primitives.assets import AssetLocator

            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"
                toolset_name = "clean_engineering"

            self.location = AssetLocator(_Host(), "contexts").locate()

        with it("should resolve to kind file when contexts.md exists"):
            expect(self.location.kind).to(equal("file"))

        with it("should point at contexts/clean_engineering/contexts.md"):
            expect(self.location.path).to(equal((_CLEAN_ENGINEERING_DIR / "contexts.md").resolve()))

    with context("locating shared templates on a clean-engineering host"):
        with before.each:
            from primitives.assets import AssetLocator

            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"
                toolset_name = "clean_engineering"

            self.location = AssetLocator(_Host(), "templates").locate()

        with it("should resolve to the python template file when format is python"):
            expect(self.location.kind).to(equal("file"))
            expect(self.location.path).to(
                equal((_CLEAN_ENGINEERING_DIR / "templates" / "clean_engineering-templates.py").resolve())
            )

    with context("locating a label that resolves to a folder"):
        with before.each:
            from primitives.assets import AssetLocator

            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"

            self.location = AssetLocator(_Host(), "scanners").locate()

        with it("should resolve to kind folder"):
            expect(self.location.kind).to(equal("folder"))

        with it("should have a non-None folder path"):
            expect(self.location.folder).not_to(be_none)


with description("Asset"):
    with context("a file-kind location pointing at an existing file"):
        with before.each:
            from primitives.assets import Asset
            from primitives.assets import AssetLocation

            with tempfile.TemporaryDirectory() as tmp:
                f = Path(tmp) / "note.md"
                f.write_text("asset content", encoding="utf-8")
                location = AssetLocation("file", Path(tmp), "note", path=f)
                self.result = Asset(location).collect()

        with it("should return the file content"):
            expect(self.result).to(equal("asset content"))

    with context("a file-kind location pointing at a missing file"):
        with before.each:
            from primitives.assets import Asset
            from primitives.assets import AssetLocation

            location = AssetLocation(
                "file", Path("/nonexistent"), "x", path=Path("/nonexistent/x.md")
            )
            self.result = Asset(location).collect()

        with it("should return an empty string"):
            expect(self.result).to(be_empty)

    with context("a section-kind location pointing at the clean-engineering contexts section"):
        with before.each:
            from primitives.assets import Asset
            from primitives.assets import AssetLocation

            location = AssetLocation(
                "section",
                _CLEAN_ENGINEERING_DIR,
                "clean_engineering",
                section_file=_CLEAN_ENGINEERING_DIR / "clean_engineering.md",
                section_heading="Contexts",
            )
            self.result = Asset(location).collect()

        with it("should return content containing Contexts"):
            expect(self.result).to(contain("Contexts"))


with description("AssetCollection"):
    with context("a folder-kind location pointing at the bdd formats folder"):
        with before.each:
            from primitives.assets import AssetCollection
            from primitives.assets import AssetLocation

            location = AssetLocation("folder", _BDD_DIR, "bdd", folder=_BDD_DIR / "formats")
            self.collection = AssetCollection(location)

        with it("should collect a non-empty dict of format files"):
            result = self.collection.collect()
            expect(len(result) > 0).to(equal(True))

        with it("should merge all collected items into a single non-empty string"):
            merged = self.collection.merged()
            expect(len(merged) > 0).to(equal(True))
