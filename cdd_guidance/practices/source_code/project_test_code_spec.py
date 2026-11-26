"""The test code of one project: every file its name marks as test code, and the files the project's
``.context/config.json`` names as test code under ``test_code``, such as spec support kept under a production name."""

import json
import tempfile
from pathlib import Path

from expects import be_false, be_true, equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.practices.source_code.test_files import ProjectTestCode

# Seed: a project's spec support kept under a production name, and the config that names it as test code.
_SUPPORT = "checks/template_checks.py"
_CONFIG = {"test_code": {"files": ["checks/template_*.py"]}}


def _project(config: dict | None) -> Path:
    root = Path(tempfile.mkdtemp())
    if config is not None:
        (root / ".context").mkdir()
        (root / ".context" / "config.json").write_text(json.dumps(config), encoding="utf-8")
    return root


with description("the test code of a project") as self:
    with context("whose config names its spec support as test code"):
        with before.all:
            self.test_code = ProjectTestCode.from_project(_project(_CONFIG))

        with it("should read the file the config names as test code"):
            expect(self.test_code.is_test_code(_SUPPORT)).to(be_true)

        with it("should read it as test or example code too, which no rule judges as production"):
            expect(self.test_code.is_example_code(_SUPPORT)).to(be_true)

        with it("should still read a file its name marks as test code"):
            expect(self.test_code.is_test_code("checks/order_spec.py")).to(be_true)

        with it("should read a production file the config does not name as production code"):
            expect(self.test_code.is_test_code("checks/order.py")).to(be_false)

    # pytest collects `test_*.py` wherever it is, so such a file is a test where it holds tests, in a folder of tests or
    # not; a production module whose name starts with the word holds none.
    with context("with a file named test_ outside a folder of tests"):
        with before.all:
            root = _project(None)
            (root / "shop").mkdir()
            (root / "shop" / "test_cart.py").write_text("class TestCart:\n    def test_total(self):\n        assert 1 == 1\n", encoding="utf-8")
            (root / "shop" / "test_runs.py").write_text("class TestRunRecord:\n    def kept(self):\n        return []\n", encoding="utf-8")
            (root / "shop" / "test_files.py").write_text("class HoldsTestCode:\n    def test_code(self):\n        return None\n", encoding="utf-8")
            self.test_code = ProjectTestCode.from_project(root)

        with it("should read one whose test class declares a test function as a test"):
            expect(self.test_code.is_test_code("shop/test_cart.py")).to(be_true)

        with it("should read one that declares no test function as production code, though a class of it starts with Test"):
            expect(self.test_code.is_test_code("shop/test_runs.py")).to(be_false)

        with it("should read one whose method named test_ sits in a class pytest does not collect as production code"):
            expect(self.test_code.is_test_code("shop/test_files.py")).to(be_false)

    with context("whose config names no test code"):
        with it("should read the spec support as production code, as its name says"):
            expect(ProjectTestCode.from_project(_project(None)).is_test_code(_SUPPORT)).to(equal(False))
