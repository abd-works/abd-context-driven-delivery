"""What the Render action answers for one guidance: the render, and what it saved.

A render of paths ends in saved files, which the result names; only a render into a data format a program reads, such
as json, answers its content. Each kind of result writes itself as the fields the Render action has always answered,
so an agent reads ``path`` for a saved drawing or document, ``paths`` for saved code, ``migrate`` for what waits for a
person in a file already there, and ``board``, ``batches`` and ``publish`` for a whiteboard's board in Claude.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness.guidance.practice_formats import Rendered
from harness.installation.data_class import data_field
from harness.markdown.format import Format


# What a result that kept something tells the agent to do with each entry of migrate. The person's ruling of
# 2026-11-22: no rule tells what a render drew from what a person added; an agent decides each entry by reading it.
DECIDE_EACH = (
    "Each entry of migrate is something a file held that the source it was rendered from no longer holds, or writes "
    "otherwise. The render kept it where it was, so nothing is lost, and hands it to you to decide. Go through every "
    "entry of migrate, open its file, and decide by reading the leftover against what the source now holds and against "
    "may_have_replaced_it, the things the render added: its functionality or content moved somewhere, so move it there "
    "and take the leftover out; it was merged into something else, so fold it in and take the leftover out; it is no "
    "longer needed, so remove it; or it is still wanted and the source is behind, so put it back in the source and "
    "render again. An entry that names signature_differs is decided the same way: whether the file's line or the "
    "source's model_has is right, and bring the other up to date. Decide each by reading both: who added it or who "
    "removed it plays no part, and no rule decides it for you. Where reading both does not tell you, ask the person, "
    "naming the file, the leftover and what may have replaced it. Until you have decided an entry, it stays where it is."
)

# What a whiteboard render whose file was never published tells the agent: the render ends with the board in Claude.
PUBLISH_NEW_BOARD = (
    "This render is not finished until the whiteboard file is on a board in Claude. Create a Whiteboard artifact "
    "with Claude's Artifact tool, titled exactly title, the file's name without its .whiteboard ending (such as "
    "story-map or ordering-model), so a person can tell boards apart and match each to its file. Write each batch to "
    "its store in order with ArtifactData batch, then call record_board with this file's path and the board's address, which keeps the address in the file "
    "so the next render updates the same board and the Files app opens it. A robot or sub-agent that cannot reach the "
    "Artifact tool reports that the board is unpublished, naming the file, rather than leave it out."
)
# What a whiteboard render whose file is already on a board in Claude tells the agent.
PUBLISH_TO_BOARD = (
    "This render is not finished until the board in Claude shows it: write each batch to the store of the board at "
    "board, in order, with ArtifactData batch. The batches change only what the render changed, so what people moved "
    "or added on the board stays."
)


class Migration:
    """One thing a render left in a file already there for a person or an agent to move: the file it is in."""

    def __init__(self, file: Path) -> None:
        self._file = file

    @property
    @data_field
    def file(self) -> str:
        return str(self._file)

    @property
    def member(self) -> str:
        """The member, line, cell, or element this names in the file."""
        raise NotImplementedError(f"{type(self).__name__} names no member")


class KeptMember(Migration):
    """What only the file held, kept in it though the source no longer holds it: a member of code, kept marked, a line
    of a markdown document kept below it, or a cell or element of a drawing kept where it was; with what the render
    added that may have replaced it, for the agent who decides where it goes."""

    def __init__(self, file: Path, kept: str, may_have_replaced_it: list[str] | None = None) -> None:
        super().__init__(file)
        self._kept = kept
        self._replaced_by = list(may_have_replaced_it or [])

    @property
    @data_field
    def kept(self) -> str:
        return self._kept

    @property
    @data_field
    def may_have_replaced_it(self) -> list[str]:
        return list(self._replaced_by)

    @property
    def member(self) -> str:
        return self._kept


class SignatureDiffers(Migration):
    """A member the file and the model both hold, whose opening line the model writes otherwise: the file kept its own
    line, and the model has model_has."""

    def __init__(self, file: Path, member: str, model_has: str) -> None:
        super().__init__(file)
        self._member = member
        self._model_has = model_has

    @property
    @data_field
    def signature_differs(self) -> str:
        return self._member

    @property
    @data_field
    def model_has(self) -> str:
        return self._model_has

    @property
    def member(self) -> str:
        return self._member



class RenderResult:
    """What the Render action answers for one guidance: the render (``rendered``) and the files it saved
    (``saved``)."""

    def __init__(self, rendered: Rendered) -> None:
        self.rendered = rendered

    @property
    @data_field
    def format(self) -> Format:
        return self.rendered.format

    @property
    def saved(self) -> list[Path]:
        """The files this render saved; none for a render that answers its content."""
        return []

    @property
    def migrate(self) -> list[Migration]:
        """What the render left in files already there for a person or an agent to move; none for a render that
        saved nothing."""
        return []


class AnsweredContent(RenderResult):
    """A render that saved nothing and answers its content: into a data format a program reads, or of content the
    call sent rather than files."""

    @property
    @data_field
    def content(self) -> Any:
        return self.rendered.content


class SavedFile(RenderResult):
    """A render saved as one drawing or document, with what only the file already there held, kept in it."""

    def __init__(self, rendered: Rendered, path: Path, migrate: list[Migration] | None = None) -> None:
        super().__init__(rendered)
        self._path = path
        self._migrate = list(migrate or [])

    @property
    @data_field
    def path(self) -> str:
        return str(self._path)

    @property
    @data_field
    def migrate(self) -> list[Migration]:
        return list(self._migrate)

    @property
    @data_field
    def decide(self) -> str:
        """What the agent does with each entry of migrate; nothing when the render kept nothing."""
        return DECIDE_EACH if self._migrate else ""

    @property
    def saved(self) -> list[Path]:
        return [self._path]


class SavedBoard(SavedFile):
    """A whiteboard saved as a file, with the board in Claude kept for it, and the store writes that put the file on
    that board."""

    def __init__(self, rendered: Rendered, path: Path, migrate: list[Migration], board: str | None, batches: list, title: str) -> None:
        super().__init__(rendered, path, migrate)
        self._board = board
        self._batches = batches
        self._title = title

    @property
    @data_field
    def board(self) -> str | None:
        """The address of the board the file was published to; none for a file not published yet."""
        return self._board

    @property
    @data_field
    def batches(self) -> list:
        return self._batches

    @property
    @data_field
    def title(self) -> str:
        """What the board in Claude is titled: the file's name without its .whiteboard ending
        (``Whiteboard.title_of``), the same title the board's meta holds."""
        return self._title

    @property
    @data_field
    def publish(self) -> str:
        """What the agent does to finish the render: put the file on a new board and record its address when it was
        never published, else write the batches to its board."""
        return PUBLISH_TO_BOARD if self._board else PUBLISH_NEW_BOARD


class SavedFiles(RenderResult):
    """A render saved as one file for each piece of it at the paths the fidelity declares: code, or a document the
    fidelity writes as one file for each named part, such as one card file for each module."""

    def __init__(self, rendered: Rendered, paths: list[Path], migrate: list[Migration]) -> None:
        super().__init__(rendered)
        self._paths = list(paths)
        self._migrate = list(migrate)

    @property
    @data_field
    def paths(self) -> list[str]:
        return [str(path) for path in self._paths]

    @property
    @data_field
    def migrate(self) -> list[Migration]:
        return list(self._migrate)

    @property
    @data_field
    def decide(self) -> str:
        """What the agent does with each entry of migrate; nothing when the render kept nothing."""
        return DECIDE_EACH if self._migrate else ""

    @property
    def saved(self) -> list[Path]:
        return list(self._paths)


class SavedCode(SavedFiles):
    """A render to code, saved as one file for each piece of it at the paths the fidelity declares."""

    def with_test_tiers(self, test_tiers: str) -> SavedTests:
        """This render as one that saved tests, naming what the session records of their module's test tiers."""
        return SavedTests(self.rendered, self._paths, self._migrate, test_tiers)


class SavedTests(SavedCode):
    """A render to code that saved tests at a fidelity whose supplement keeps the test tiers of the module each test is
    for: beside the files, it answers what the session's record of those tiers holds now and what the render could not
    tell, which the agent decides and records."""

    def __init__(self, rendered: Rendered, paths: list[Path], migrate: list[Migration], test_tiers: str) -> None:
        super().__init__(rendered, paths, migrate)
        self._test_tiers = test_tiers

    @property
    @data_field
    def test_tiers(self) -> str:
        return self._test_tiers
