"""BDD spec — Catalog pages from @markdown HTML."""
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "primitives", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import after, before, context, description, it

from primitives.guidance.fixtures.sample_tool.sample_tool_host import (
    SamplePracticeWithFidelities,
)
from tools.catalog_generator.catalog import Catalog


with description("generated catalog pages") as self:
    with context("that have been built from the guidance registry"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.out = Path(self._tmp)
            self.catalog = Catalog.from_registry([SamplePracticeWithFidelities(format="markdown")])
            self.catalog.generate_catalog(self.out)

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should write each practice guidance markdown property as HTML to its own page"):
            html_files = list(self.out.glob("*.html"))
            expect(len(html_files) > 0).to(equal(True))

        with it("should write each fidelity guidance markdown property as HTML to its own page"):
            names = {p.name for p in self.out.glob("*.html")}
            expect(any("sketch" in n for n in names)).to(equal(True))

        with it("should not scrape deployed markdown files or heading structure from disk"):
            expect(any(p.suffix == ".md" for p in self.out.iterdir())).to(equal(False))
