"""The tiers the Session Board's story tests replay their scenarios on, organised by what a tier hands a scenario."""
from pathlib import Path

from expects import be, expect
from mamba import after, before, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from space.kanban.session_board_examples import PET_VISITS  # noqa: E402
from space.kanban.session_board_tiers import DomainTier  # noqa: E402
from space.session import Sessions  # noqa: E402

with description("the domain tier of the session board's story tests") as self:
    with before.each:
        self.tier = DomainTier()
        self.world = self.tier.open()
        self.world.project.seed_session(PET_VISITS)

    with after.each:
        self.tier.close(self.world)

    # The cdd server works on one Sessions per checkout; a story test that made its own would act on a second Session
    # object for a folder the board reads through the first.
    with it("should act on the session the board reads, the one this process holds for the project"):
        held = Sessions.of_project(self.world.project.root)
        expect(self.world.Validate().session).to(be(held.current()))

    with it("should hand a scenario the sessions the board reads"):
        expect(self.world.sessions).to(be(Sessions.of_project(self.world.project.root)))
