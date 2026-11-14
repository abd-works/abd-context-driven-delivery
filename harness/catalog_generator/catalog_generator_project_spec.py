"""BDD spec - the catalog is generated for the project the call acts on, never for the checkout serving the tools."""
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.catalog_generator.catalog_generator import Catalog


with description("a catalog generated for a project") as self:
    with before.each:
        self.tmp = Path(tempfile.mkdtemp()).resolve()

    with after.each:
        shutil.rmtree(self.tmp, ignore_errors=True)

    with context("that is not a CDD checkout"):
        with before.each:
            self.project = self.tmp / "product"
            self.project.mkdir()

        with it("should write its pages under the project's catalog folder"):
            out_root = Catalog(repo_url="https://example.com/cdd", ref="abc", project=self.project).out_root
            expect(out_root).to(equal(self.project / "catalog"))

    with context("that is the checkout serving the tools"):
        with it("should write its pages under that checkout's cdd_guidance/catalog folder"):
            out_root = Catalog(repo_url="https://example.com/cdd", ref="abc", project=_REPO_ROOT).out_root
            expect(out_root).to(equal(_REPO_ROOT / "cdd_guidance" / "catalog"))

    with context("that a tool call names"):
        with before.each:
            self.project = self.tmp / "product"
            self.project.mkdir()

        with it("should write its pages under that project's catalog folder"):
            expect(Catalog.load(project=self.project).out_root).to(equal(self.project / "catalog"))

    with context("with an output folder named by the caller"):
        with it("should write its pages into that folder"):
            out_root = Catalog(repo_url="https://example.com/cdd", ref="abc", out_root=str(self.tmp / "out"), project=self.tmp).out_root
            expect(out_root).to(equal(self.tmp / "out"))
