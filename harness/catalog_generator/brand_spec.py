"""BDD specs for the brand a catalog wears over its shared files."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.catalog_generator.brand import Brand, UnknownBrand
from harness.catalog_generator.catalog_generator import Catalog


with description("foundry chrome brand"):
    with before.each:
        self._tmp = tempfile.TemporaryDirectory()
        self.out = Path(self._tmp.name)

    with after.each:
        self._tmp.cleanup()

    with context("that copies commons with the bundled brand"):
        with it("should place abd.works wordmarks under commons/brand"):
            dest = Brand().copy_commons(self.out)
            expect((dest / "brand" / "abd.works.wordmark.black.svg").is_file()).to(
                equal(True)
            )

    with context("that applies a brand folder from elsewhere"):
        with it("should overlay that folder onto commons/brand"):
            other = self.out / "other-brand"
            other.mkdir()
            (other / "mark.txt").write_text("alt", encoding="utf-8")
            commons = Brand().copy_commons(self.out / "catalog")
            Brand(folder=other).apply(commons)
            expect((commons / "brand" / "mark.txt").read_text(encoding="utf-8")).to(
                equal("alt")
            )


with description("a catalog brands collection"):
    with before.each:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.client = self.root / "brands" / "acme"
        self.client.mkdir(parents=True)
        (self.client / "mark.txt").write_text("acme", encoding="utf-8")
        self.out_root = self.root / "catalog"
        Brand().copy_commons(self.out_root)

    with after.each:
        self._tmp.cleanup()

    with context("that has named brand folders"):
        with it("should refuse a name that is neither a folder nor a brand in it"):
            expect(lambda: Brand(collection=self.root / "brands").resolve("no-such-brand")).to(raise_error(UnknownBrand))

        with it("should list each folder name"):
            expect("acme" in Brand(collection=self.root / "brands").folders()).to(equal(True))

        with it("should include the bundled abd-works brand"):
            expect("abd-works" in Brand(collection=self.root / "brands").folders()).to(equal(True))

    with context("with apply_brand given a collection name"):
        with it("should copy that folder onto the catalog commons brand"):
            Brand(collection=self.root / "brands").apply_named(self.out_root, "acme")
            expect(
                (self.out_root / "commons" / "brand" / "mark.txt").read_text(
                    encoding="utf-8"
                )
            ).to(equal("acme"))

    with context("with Catalog apply_brand given a collection name"):
        with it("should overlay that brand onto the catalog out_root commons"):
            catalog = Catalog(
                out_root=str(self.out_root),
                brands_root=self.root / "brands",
            )
            catalog.apply_brand("acme")
            expect(
                (self.out_root / "commons" / "brand" / "mark.txt").read_text(
                    encoding="utf-8"
                )
            ).to(equal("acme"))

        with it("should list known brands when apply_brand is given an empty name"):
            catalog = Catalog(
                out_root=str(self.out_root),
                brands_root=self.root / "brands",
            )
            expect(catalog.apply_brand("")).to(contain("acme"))
            expect(catalog.apply_brand("")).to(contain("abd-works"))
