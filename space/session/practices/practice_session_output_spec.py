"""BDD spec for the roots a person or an agent chooses for a practice and a fidelity in a session: what is refused as a
root. Exploratory testing, widget-12: a file and an empty path were kept as roots, and generate then told the agent to
write there."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from space.session.practices.practice_session_output import OutputRootRefused
from space.session.spec_support.session_roots_examples import REFUND_AGGREGATE, REFUND_DOMAIN, REFUND_STORIES, RETURN_PARCEL_STORIES, RefundOrderSession


with description("a practice's root in a session") as self:
    with before.each:
        self.refund = RefundOrderSession()
        self.stories = self.refund.session.practice("stories")

    with after.each:
        self.refund.close()

    with context("that a person chooses as a folder of the project"):
        with it("should be kept as the practice's root"):
            self.stories.choose_root(REFUND_STORIES)
            expect(self.stories.root).to(equal(REFUND_STORIES))

    with context("that a person chooses as a file of the project"):
        with it("should be refused, naming the file"):
            expect(lambda: self.stories.choose_root(REFUND_AGGREGATE)).to(raise_error(OutputRootRefused, contain(f"{REFUND_AGGREGATE} is a file")))

        with it("should leave the practice's root as it was"):
            before_choice = self.stories.root
            try:
                self.stories.choose_root(REFUND_AGGREGATE)
            except OutputRootRefused:
                pass
            expect(self.stories.root).to(equal(before_choice))

    with context("that a person chooses as a folder beside the project, climbing out of it"):
        with it("should be refused, naming the path as outside the project"):
            expect(lambda: self.stories.choose_root("../outside-root")).to(raise_error(OutputRootRefused, contain("../outside-root is outside the project")))

        with it("should leave no root chosen"):
            try:
                self.stories.choose_root("../outside-root")
            except OutputRootRefused:
                pass
            expect(self.stories.is_root_chosen).to(equal(False))

    with context("that a person chooses as a whole path to a folder outside the project"):
        with it("should be refused, naming the path as outside the project"):
            outside = self.refund.repo.parent.as_posix()
            expect(lambda: self.stories.choose_root(outside)).to(raise_error(OutputRootRefused, contain(f"{outside} is outside the project")))

    with context("that a person chooses with an empty path"):
        with it("should be refused, saying the path is empty"):
            expect(lambda: self.stories.choose_root("  ")).to(raise_error(OutputRootRefused, contain("an empty path names no folder")))

        with it("should leave no root chosen"):
            try:
                self.stories.choose_root("")
            except OutputRootRefused:
                pass
            expect(self.stories.is_root_chosen).to(equal(False))


with description("a fidelity's root in a session") as self:
    with before.each:
        self.refund = RefundOrderSession()
        self.tests = self.refund.output("stories", "acceptance_tests")

    with after.each:
        self.refund.close()

    with context("that a person chooses as a folder of the project"):
        with it("should be kept as the fidelity's root"):
            self.tests.choose_root(REFUND_STORIES)
            expect(self.refund.roots("stories", "acceptance_tests")).to(equal([REFUND_STORIES]))

    with context("that a person chooses as a file of the project"):
        with it("should be refused, naming the file"):
            expect(lambda: self.tests.choose_root(REFUND_AGGREGATE)).to(raise_error(OutputRootRefused, contain(f"{REFUND_AGGREGATE} is a file")))

    with context("that a person chooses with an empty path"):
        with it("should be refused, saying the path is empty"):
            expect(lambda: self.tests.choose_root("")).to(raise_error(OutputRootRefused, contain("an empty path names no folder")))

        with it("should keep no root for the fidelity in the session's record"):
            try:
                self.tests.choose_root("")
            except OutputRootRefused:
                pass
            expect(self.refund.session.practice("stories").fields.fidelity("acceptance_tests").roots).to(equal([]))

    with context("that a person chooses as a folder outside the project"):
        with it("should be refused, naming the path as outside the project"):
            expect(lambda: self.tests.choose_root("../..")).to(raise_error(OutputRootRefused, contain("../.. is outside the project")))

        with it("should keep no root for the fidelity in the session's record"):
            try:
                self.tests.choose_root("../..")
            except OutputRootRefused:
                pass
            expect(self.refund.session.practice("stories").fields.fidelity("acceptance_tests").roots).to(equal([]))

    with context("that a person chooses as a folder of the project, read back from its answer"):
        with it("should show the root it now has"):
            expect(self.tests.choose_root(REFUND_STORIES).root_paths).to(equal([REFUND_STORIES]))

    with context("that has one root, with a folder outside the project added beside it"):
        with it("should refuse the folder by name"):
            self.tests.choose_root(REFUND_STORIES)
            expect(lambda: self.tests.add_root("../outside-root")).to(raise_error(OutputRootRefused, contain("../outside-root is outside the project")))

    with context("that has one root, with a file added beside it"):
        with before.each:
            self.tests.choose_root(REFUND_STORIES)

        with it("should refuse the file by name"):
            expect(lambda: self.tests.add_root(REFUND_AGGREGATE)).to(raise_error(OutputRootRefused, contain(f"{REFUND_AGGREGATE} is a file")))

        with it("should keep the root it had and no other"):
            try:
                self.tests.add_root(REFUND_AGGREGATE)
            except OutputRootRefused:
                pass
            expect(self.refund.roots("stories", "acceptance_tests")).to(equal([REFUND_STORIES]))

    with context("that has one root, with a folder added beside it"):
        with it("should keep both"):
            self.tests.choose_root(REFUND_STORIES)
            self.tests.add_root(RETURN_PARCEL_STORIES)
            expect(self.refund.roots("stories", "acceptance_tests")).to(equal([REFUND_STORIES, RETURN_PARCEL_STORIES]))
