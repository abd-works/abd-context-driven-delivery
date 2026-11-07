"""The toolsets one repository defines, found by reading its source."""
import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets


with description("a repository's toolsets") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="repository-toolsets-"))
        (self.root / "shop").mkdir()

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("with a class whose only mark is the lowercase mcp alias"):
        with before.each:
            (self.root / "shop" / "cart.py").write_text(
                "from harness.mcp.mcp_server import mcp\n\n\nclass Cart:\n    @mcp\n    def total(self) -> int:\n        return 0\n",
                encoding="utf-8",
            )

        with it("should collect the class"):
            expect(RepositoryToolsets(self.root).collect()).to(contain("shop.cart:Cart"))

    with context("with a class whose member carries the Mcp class name"):
        with before.each:
            (self.root / "shop" / "till.py").write_text(
                "from harness.mcp.mcp_server import Mcp\n\n\nclass Till:\n    @Mcp\n    def open(self) -> None:\n        pass\n",
                encoding="utf-8",
            )

        with it("should collect the class"):
            expect(RepositoryToolsets(self.root).collect()).to(contain("shop.till:Till"))

    with context("with a class no mark names"):
        with before.each:
            (self.root / "shop" / "plain.py").write_text("class Plain:\n    def run(self) -> None:\n        pass\n", encoding="utf-8")

        with it("should collect nothing"):
            expect(RepositoryToolsets(self.root).collect()).to(equal([]))
