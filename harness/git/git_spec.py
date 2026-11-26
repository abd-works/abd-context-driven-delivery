"""The time limit git gets for each command: a short one for reads, a long one for commands that write the whole
working tree or reach origin, which take many seconds in a large checkout. And the entries of a listing git ends with a
NUL each, which names every file as it is on disk."""
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from harness.git.git import Git


class TimedGit(Git):
    """Git that records the limit each command was given instead of running it."""

    def _run_process(self, argv: list[str], timeout: float, env: dict[str, str] | None = None) -> tuple[int, str, str]:
        self.limit = timeout
        return 0, "", ""


# Seed: a file whose name git writes in quotes with octal escapes unless it is asked for NUL-ended entries.
QUOTED_BY_GIT = "src/ünïcödé_日本.py"


class ListingGit(Git):
    """Git that answers one listing's output, as git writes it under ``-z``, and records the command it was given."""

    def __init__(self, output: str) -> None:
        super().__init__(Path("."))
        self._answer = output

    def _run_process(self, argv: list[str], timeout: float, env: dict[str, str] | None = None) -> tuple[int, str, str]:
        self.argv = argv
        return 0, self._answer, ""


with description("a git listing") as self:
    with context("of files, one with letters outside ASCII in its name"):
        with before.each:
            self.git = ListingGit(f"README.md\0{QUOTED_BY_GIT}\0")

        with it("should ask git to end each entry with a NUL, so no name is quoted"):
            self.git.listed("ls-files", "--cached")
            expect(self.git.argv[-3:]).to(equal(["ls-files", "--cached", "-z"]))

        with it("should answer every name as it is on disk"):
            expect(self.git.listed("ls-files", "--cached")).to(equal(["README.md", QUOTED_BY_GIT]))

    with context("of a status whose first entry starts with a space, a file changed and not staged"):
        with it("should keep that space, so the name starts where git puts it"):
            expect(ListingGit(" M a.py\0?? b.py\0").listed("status", "--porcelain")).to(equal([" M a.py", "?? b.py"]))


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
