"""BDD spec for the roots a person or an agent chooses for a practice and a fidelity in a session: what is refused as a
root. Exploratory testing, widget-12: an empty path was kept as a root, and generate then told the agent to write there.
The person's answer (2026-11-26): a practice holds many roots, files as well as folders, each added to every fidelity of
the practice; only the folder a practice writes its documents under (its own root, choose_root) must be a folder."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from space.session.practices.practice_session_output import LastFormatLeftOut, OutputRootRefused
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

    with context("that a person chooses as a file of the project, as the folder the practice writes under"):
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


    # The Files app's file menu: Add to practice puts a file or a folder on the whole practice.
    with context("that a person adds a folder to, beside the roots its fidelities have"):
        with before.each:
            self.stories.add_root(REFUND_DOMAIN)

        with it("should be a root of every fidelity of the practice"):
            fidelities = self.stories.fidelity_outputs
            expect([REFUND_DOMAIN in output.root_paths for output in fidelities]).to(equal([True] * len(fidelities)))

        with it("should keep each fidelity's roots before it"):
            expect(self.refund.roots("stories", "story_map")[0]).not_to(equal(REFUND_DOMAIN))

        with it("should list it among the roots a person added to the practice"):
            expect(self.stories.added_roots).to(equal([REFUND_DOMAIN]))

    with context("that a person adds a file to"):
        with before.each:
            self.stories.add_root(REFUND_AGGREGATE)

        with it("should keep the file itself as a root of every fidelity of the practice"):
            fidelities = self.stories.fidelity_outputs
            expect([REFUND_AGGREGATE in output.root_paths for output in fidelities]).to(equal([True] * len(fidelities)))

        with it("should list it among the roots a person added to the practice"):
            expect(self.stories.added_roots).to(equal([REFUND_AGGREGATE]))

        with it("should be a root the session reads its files under"):
            expect(self.refund.session.session_files.in_root(self.refund.repo / REFUND_AGGREGATE)).to(equal(True))

    # Defect gizmo-7: adding a root the practice already has said it was added, though nothing changed.
    with context("that a person adds a second time"):
        with before.each:
            self.stories.add_root(REFUND_DOMAIN)

        with it("should be refused, saying it is already a root of the practice"):
            expect(lambda: self.stories.add_root(REFUND_DOMAIN)).to(raise_error(OutputRootRefused, contain(f"{REFUND_DOMAIN} is already a root of Stories")))

    # Defect gizmo-4: .git was taken as a root, and All files failed for the whole session from then on.
    with context("that a person adds inside git's own .git folder"):
        with it("should be refused, naming the path"):
            expect(lambda: self.stories.add_root(".git")).to(raise_error(OutputRootRefused, contain(".git is inside a .git folder")))

        with it("should add no root"):
            try:
                self.stories.add_root(".git/hooks")
            except OutputRootRefused:
                pass
            expect(self.stories.added_roots).to(equal([]))

    # Defect gizmo-5: the project's top folder, added, was answered as a root named "".
    with context("that a person adds as the project's top folder, from a session working in a folder below it"):
        with it("should list it among the roots added as ., the project's top"):
            self.refund.session.workpath = self.refund.repo / REFUND_DOMAIN
            self.stories.add_root(".")
            expect(self.stories.added_roots).to(equal(["."]))

    with context("that a person adds from outside the project"):
        with it("should be refused, naming the path"):
            expect(lambda: self.stories.add_root("../outside-root")).to(raise_error(OutputRootRefused, contain("../outside-root is outside the project")))

        with it("should add no root"):
            try:
                self.stories.add_root("../outside-root")
            except OutputRootRefused:
                pass
            expect(self.stories.added_roots).to(equal([]))


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
        with it("should be kept as the fidelity's root"):
            self.tests.choose_root(REFUND_AGGREGATE)
            expect(self.refund.roots("stories", "acceptance_tests")).to(equal([REFUND_AGGREGATE]))

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
        with it("should keep both"):
            self.tests.choose_root(REFUND_STORIES)
            self.tests.add_root(REFUND_AGGREGATE)
            expect(self.refund.roots("stories", "acceptance_tests")).to(equal([REFUND_STORIES, REFUND_AGGREGATE]))

    with context("that has one root, with a folder added beside it"):
        with it("should keep both"):
            self.tests.choose_root(REFUND_STORIES)
            self.tests.add_root(RETURN_PARCEL_STORIES)
            expect(self.refund.roots("stories", "acceptance_tests")).to(equal([REFUND_STORIES, RETURN_PARCEL_STORIES]))


# Exploratory testing, widget-13 and widget-17: every format of a fidelity could be left out, and generate then wrote in
# none; and a format could be chosen for a fidelity of a practice turned off, which every action refuses to work on.
with description("a fidelity's chosen formats in a session") as self:
    with before.each:
        self.refund = RefundOrderSession()
        self.story_map = self.refund.output("stories", "story_map")

    with after.each:
        self.refund.close()

    with context("with one format chosen, left out"):
        with it("should be refused, naming the format and the fidelity"):
            expect(lambda: self.story_map.choose_format("markdown", False)).to(raise_error(LastFormatLeftOut, contain("markdown is the only format chosen for story_map")))

        with it("should keep the format chosen"):
            try:
                self.story_map.choose_format("markdown", False)
            except LastFormatLeftOut:
                pass
            expect(self.refund.output("stories", "story_map").chosen_formats).to(equal(["markdown"]))

    with context("with two formats chosen, one left out"):
        with it("should keep the other"):
            self.story_map.choose_format("drawio", True)
            expect(self.story_map.choose_format("markdown", False).chosen_formats).to(equal(["drawio"]))

    with context("with only the diagram formats chosen, the diagram group left out"):
        with before.each:
            self.story_map.choose_format("drawio", True)
            self.story_map.choose_format("whiteboard", True)
            self.story_map.choose_format("markdown", False)

        with it("should be refused, naming the formats"):
            expect(lambda: self.story_map.formats.choose_from(["drawio", "whiteboard"], False)).to(raise_error(LastFormatLeftOut, contain("drawio, whiteboard")))

        with it("should keep every format of the group chosen"):
            try:
                self.story_map.formats.choose_from(["drawio", "whiteboard"], False)
            except LastFormatLeftOut:
                pass
            expect(self.refund.output("stories", "story_map").chosen_formats).to(equal(["drawio", "whiteboard"]))

    # Reported 2026-11-25: switching a practice off changes only what the board and chat show; an action sent to the
    # agent still works on it, in the format it names, so the format is chosen for it as for any practice.
    with context("of a practice switched off"):
        with before.each:
            self.refund.session.practice("ux").enable(False)
            self.ia = self.refund.output("ux", "ia")

        with it("should keep a format chosen for it in the session's record"):
            self.ia.choose_format("drawio", True)
            expect(self.refund.output("ux", "ia").fields.formats).to(contain("drawio"))
