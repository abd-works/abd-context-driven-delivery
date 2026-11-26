"""Which files BDD reads a describe tree from, and which code it never links an observation to: one definition, Clean
Engineering's, that both practices ask."""

from expects import be_false, be_true, expect
from mamba import context, description, it

import tempfile
from pathlib import Path

from cdd_guidance.practices.source_code import ProjectTestCode

# A project's test code, read by name for files that are not there: a project with no config, in an empty folder.
_NAMED = ProjectTestCode(Path(tempfile.mkdtemp()), [])

with description("a file in a working copy BDD reads"):
    with context("that is an end-to-end spec"):
        with it("should be a spec file"):
            expect(_NAMED.is_spec("app/tests/kanban/move_ticket.behavior.e2e.ts")).to(be_true)

    with context("that is the page driver an end-to-end spec drives its pages through"):
        with it("should be no spec file"):
            expect(_NAMED.is_spec("app/tests/kanban/move_ticket.page-driver.ts")).to(be_false)

        with it("should be test code wherever it sits"):
            expect(_NAMED.is_test_code("app/kanban/move_ticket.page-driver.ts")).to(be_true)

    with context("that is a helper under test-utils"):
        with it("should be test code"):
            expect(_NAMED.is_test_code("app/test-utils/board-page-support.ts")).to(be_true)

    with context("that is a fixtures module"):
        with it("should be no spec file"):
            expect(_NAMED.is_spec("shop/fixtures.py")).to(be_false)

        with it("should be test code"):
            expect(_NAMED.is_test_code("shop/fixtures.py")).to(be_true)

    with context("that is production code"):
        with it("should be no test code"):
            expect(_NAMED.is_test_code("shop/cart.py")).to(be_false)
