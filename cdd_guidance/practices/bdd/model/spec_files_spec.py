"""Which files BDD reads a describe tree from, and which code it never links an observation to: one definition, Clean
Engineering's, that both practices ask."""

from expects import be_false, be_true, expect
from mamba import context, description, it

from cdd_guidance.practices.clean_engineering.model.production_code import is_spec_file, is_test_code

with description("a file in a working copy BDD reads"):
    with context("that is an end-to-end spec"):
        with it("should be a spec file"):
            expect(is_spec_file("app/tests/kanban/move_ticket.behavior.e2e.ts")).to(be_true)

    with context("that is the page driver an end-to-end spec drives its pages through"):
        with it("should be no spec file"):
            expect(is_spec_file("app/tests/kanban/move_ticket.page-driver.ts")).to(be_false)

        with it("should be test code wherever it sits"):
            expect(is_test_code("app/kanban/move_ticket.page-driver.ts")).to(be_true)

    with context("that is a helper under test-utils"):
        with it("should be test code"):
            expect(is_test_code("app/test-utils/board-page-support.ts")).to(be_true)

    with context("that is a Java test"):
        with it("should be a spec file"):
            expect(is_spec_file("src/test/java/shop/CartTest.java")).to(be_true)

    with context("that is a fixtures module"):
        with it("should be no spec file"):
            expect(is_spec_file("shop/fixtures.py")).to(be_false)

        with it("should be test code"):
            expect(is_test_code("shop/fixtures.py")).to(be_true)

    with context("that is production code"):
        with it("should be no test code"):
            expect(is_test_code("shop/cart.py")).to(be_false)
