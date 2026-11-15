"""The time limit git gets for each command: a short one for reads, a long one for commands that write the whole
working tree or reach origin, which take many seconds in a large checkout."""
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from harness.process.git import Git


class TimedGit(Git):
    """Git that records the limit each command was given instead of running it."""

    def _run_process(self, argv: list[str], timeout: float, env: dict[str, str] | None = None) -> tuple[int, str, str]:
        self.limit = timeout
        return 0, "", ""


with description("a git command's time limit") as self:
    with before.each:
        self.git = TimedGit(Path("."))

    with context("that only reads"):
        with it("should get the short limit"):
            self.git.run("status", "--porcelain")
            expect(self.git.limit).to(equal(10))

    with context("that stages the working tree"):
        with it("should get the long limit"):
            self.git.run("add", "-A")
            expect(self.git.limit).to(equal(180))

    with context("that commits"):
        with it("should get the long limit"):
            self.git.run("commit", "-m", "work")
            expect(self.git.limit).to(equal(180))
