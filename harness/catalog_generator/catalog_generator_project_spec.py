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

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from harness.catalog_generator.catalog_generator import Catalog

# A CDD checkout's own catalog generator, cut down to what the spec observes: it shows the guidance found in its own
# checkout, so a page naming the project's guidance proves the catalog was read from the project.
_PROJECT_GENERATOR = '''\
import argparse
from pathlib import Path

checkout = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--out")
parser.add_argument("--brand", default=None)
args = parser.parse_args()
out = checkout / args.out
out.mkdir(parents=True, exist_ok=True)
guidance = (checkout / "cdd_guidance" / "practices" / "stories" / "stories.md").read_text(encoding="utf-8")
(out / "index.html").write_text("<p>" + guidance + "</p>", encoding="utf-8")
print("Catalog regenerated into " + str(out))
'''

_PROJECT_GUIDANCE = "Stories guidance written on the project's branch"


def _cdd_checkout(root: Path) -> Path:
    generator = root / "harness" / "catalog_generator" / "generate_cdd_catalog.py"
    generator.parent.mkdir(parents=True)
    generator.write_text(_PROJECT_GENERATOR, encoding="utf-8")
    guide = root / "cdd_guidance" / "practices" / "stories" / "stories.md"
    guide.parent.mkdir(parents=True)
    guide.write_text(_PROJECT_GUIDANCE, encoding="utf-8")
    return root


def _serving_catalog_files() -> dict[str, float]:
    folders = (_REPO_ROOT / "cdd_guidance" / "catalog", _REPO_ROOT / "catalog")
    return {
        str(path): path.stat().st_mtime
        for folder in folders if folder.is_dir()
        for path in folder.rglob("*") if path.is_file()
    }


with description("a catalog generated for a project") as self:
    with before.each:
        self.tmp = Path(tempfile.mkdtemp()).resolve()

    with after.each:
        shutil.rmtree(self.tmp, ignore_errors=True)

    with context("that is a CDD checkout other than the one serving the tools"):
        with before.each:
            self.project = _cdd_checkout(self.tmp / "branch-worktree")
            self.serving_before = _serving_catalog_files()
            self.message = Catalog(repo_url="https://example.com/cdd", ref="abc", project=self.project).generate_catalog()

        with it("should write its pages under the project's cdd_guidance/catalog folder"):
            expect((self.project / "cdd_guidance" / "catalog" / "index.html").is_file()).to(equal(True))

        with it("should show the guidance read from the project's own checkout"):
            page = (self.project / "cdd_guidance" / "catalog" / "index.html").read_text(encoding="utf-8")
            expect(page).to(contain(_PROJECT_GUIDANCE))

        with it("should report the folder it wrote into"):
            expect(self.message).to(contain(str(self.project / "cdd_guidance" / "catalog")))

        with it("should write nothing under the checkout serving the tools"):
            expect(_serving_catalog_files()).to(equal(self.serving_before))

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
