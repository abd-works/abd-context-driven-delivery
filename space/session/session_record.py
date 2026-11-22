"""SessionRecord - one session's ``session.json``: its typed fields, and each change to it saved on main."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Generic, Iterator, TypeVar

from harness.installation.json_file import HeldJsonFile, JsonFile
from harness.process.answer_reads import ANSWER_READS, HeldForAnswer
from space.session.session_saves import SessionSaves

if TYPE_CHECKING:
    from space.session.session import Session

SESSION_FILE = "session.json"
# How much of a saved value a save's commit message shows: a workpath or a list can be long.
_SHOWN_CHARACTERS = 40
# Keys an older session.json holds that no reader needs any more: what a practice chose was kept apart from whether it
# was on (``outputs``), and the checkout's folder was written and never read (``repo_path``). Both go on the next save.
_RETIRED_KEYS = ("outputs", "repo_path")
_PRACTICES = "practices"
_FIDELITIES = "fidelities"
_TEST_TIERS = "test_tiers"
# The tiers a module's tests can use: unit for every module, server for one that publishes operations through a server,
# web for one that shows a page.
TEST_TIERS = ("unit", "server", "web")

# What a change to session.json leaves beside it, which no save commits: the lock file a change holds it by, and the
# text a writer staged and was killed before it swapped it in.
SessionSaves.leave_out(f"**/{SESSION_FILE}.lock")
SessionSaves.leave_out(f"**/{SESSION_FILE}.*.tmp")

Value = TypeVar("Value")


class _Field(Generic[Value]):
    """One top-level field of session.json, read with its default when the file does not hold it."""

    def __init__(self, key: str, default: Value) -> None:
        self.key = key
        self._default = default

    def __get__(self, fields: SessionFields | None, owner: type) -> Value:
        if fields is None:
            return self  # type: ignore[return-value]
        found = fields.raw.get(self.key)
        return self._default if found is None else found

    def __set__(self, fields: SessionFields, value: Value) -> None:
        fields.raw[self.key] = value


class FidelityFields:
    """What session.json keeps for one fidelity of a practice: the formats chosen for it (none before anyone chose), the
    folders it writes under when it has its own, and the file name chosen for each format of a single-file output."""

    def __init__(self, raw: dict) -> None:
        self._raw = raw

    @property
    def formats(self) -> list[str] | None:
        chosen = self._raw.get("formats")
        return None if chosen is None else list(chosen)

    @formats.setter
    def formats(self, chosen: list[str]) -> None:
        self._raw["formats"] = list(chosen)

    @property
    def roots(self) -> list[str]:
        return list(self._raw.get("roots", []))

    @roots.setter
    def roots(self, folders: list[str]) -> None:
        self._raw["roots"] = list(folders)

    @property
    def file_names(self) -> dict[str, str]:
        return dict(self._raw.get("file_names", {}))


class PracticeFields:
    """What session.json keeps for one practice: whether the session works on it, the root a person chose for it, and
    what it keeps for each of its fidelities."""

    def __init__(self, raw: dict) -> None:
        self._raw = raw

    @property
    def enabled(self) -> bool:
        return bool(self._raw.get("enabled", True))

    @enabled.setter
    def enabled(self, is_enabled: bool) -> None:
        self._raw["enabled"] = is_enabled

    @property
    def root(self) -> str:
        return str(self._raw.get("root", "") or "")

    @root.setter
    def root(self, folder: str) -> None:
        if folder:
            self._raw["root"] = folder
        else:
            self._raw.pop("root", None)

    def fidelity(self, name: str) -> FidelityFields:
        """What the practice keeps for its fidelity called name, kept from now on once it is changed."""
        return FidelityFields(self._raw.setdefault(_FIDELITIES, {}).setdefault(name, {}))


class SelectionFields:
    """The session's guidance selection as session.json keeps it: the stages selected (none before anyone chose), and
    the version every change raises."""

    def __init__(self, raw: dict) -> None:
        self._raw = raw

    @property
    def stages(self) -> list[str] | None:
        chosen = self._raw.get("stages")
        return None if chosen is None else list(chosen)

    @stages.setter
    def stages(self, chosen: list[str]) -> None:
        self._raw["stages"] = list(chosen)

    @property
    def version(self) -> int:
        return int(self._raw.get("version", 0))

    @version.setter
    def version(self, number: int) -> None:
        self._raw["version"] = number


class SessionFields:
    """What one session.json holds, each field typed: the session's name, title, scope, workpath, tags, overlays, parent
    and whether it was pulled out of it, the branch, worktree and chat its checkout recorded, its guidance selection, and
    what it keeps for each practice. A file in an older shape is upgraded as it is read; what other owners keep there,
    such as the board's stage, is kept as it is and changed only through their own part (``SessionRecord.extra``)."""

    KEYS = frozenset({"name", "title", "scope", "workpath", "tags", "overlays", "parent", "pulled_out", "branch", "worktree", "chat", "guidance", _PRACTICES, _TEST_TIERS})

    name = _Field("name", "")
    title = _Field("title", "")
    scope = _Field("scope", "")
    workpath = _Field("workpath", "")
    tags = _Field[list]("tags", [])
    overlays = _Field[list]("overlays", [])
    parent = _Field("parent", "")
    pulled_out = _Field("pulled_out", False)
    branch = _Field("branch", "")
    worktree = _Field("worktree", "")
    chat = _Field("chat", "")

    def __init__(self, raw: dict) -> None:
        self.raw = _upgraded(raw)

    @property
    def guidance(self) -> SelectionFields:
        return SelectionFields(self.raw.setdefault("guidance", {}))

    def practice(self, key: str) -> PracticeFields:
        """What session.json keeps for the practice whose key is key; nothing saved yet reads as the defaults."""
        return PracticeFields(self.raw.setdefault(_PRACTICES, {}).setdefault(key, {}))

    @property
    def test_tiers(self) -> dict[str, dict[str, str]]:
        """The test tiers each module uses, by the module's path from the project, each tier with its test tool; none
        before a generate or a render recorded any. A record in another shape is refused with MisshapenTestTiersError,
        never read as no tiers chosen, which would let a story of an app pass with no server or web test."""
        held = self.raw.get(_TEST_TIERS)
        if held is None:
            return {}
        if not isinstance(held, dict):
            raise MisshapenTestTiersError(held)
        return {module: self._tiers_of(module, tiers) for module, tiers in held.items()}

    @test_tiers.setter
    def test_tiers(self, recorded: dict[str, dict[str, str]]) -> None:
        self.raw[_TEST_TIERS] = {module: dict(tiers) for module, tiers in recorded.items()}

    def _tiers_of(self, module: str, tiers: object) -> dict[str, str]:
        if not isinstance(tiers, dict):
            raise MisshapenTestTiersError({module: tiers})
        misshapen = {tier: tool for tier, tool in tiers.items() if tier not in TEST_TIERS or not isinstance(tool, str) or not tool}
        if misshapen:
            raise MisshapenTestTiersError({module: misshapen})
        return dict(tiers)

    def as_dict(self) -> dict:
        """The fields as session.json writes them, empty parts left out."""
        written = {key: value for key, value in self.raw.items() if key not in _RETIRED_KEYS}
        if not written.get("guidance"):
            written.pop("guidance", None)
        if _TEST_TIERS in written and not written[_TEST_TIERS]:
            written.pop(_TEST_TIERS)
        practices = {key: _kept(practice) for key, practice in dict(written.get(_PRACTICES) or {}).items()}
        practices = {key: practice for key, practice in practices.items() if practice}
        if practices:
            written[_PRACTICES] = practices
        else:
            written.pop(_PRACTICES, None)
        return written


def _kept(practice: dict) -> dict:
    """A practice's entry with no empty fidelity left in it, as a read that asked for one before it was saved leaves."""
    fidelities = {name: fidelity for name, fidelity in dict(practice.get(_FIDELITIES) or {}).items() if fidelity}
    kept = {key: value for key, value in practice.items() if key != _FIDELITIES}
    return {**kept, _FIDELITIES: fidelities} if fidelities else kept


def _upgraded(raw: dict) -> dict:
    """raw in today's shape: a practice's chosen root and each fidelity's roots and file names, kept apart under
    ``outputs`` by older files, and its formats, kept under the practice's ``formats``, are merged into one entry per
    fidelity under the practice. A file already in today's shape is answered as it is."""
    held = dict(raw)
    practices = {key: dict(value) for key, value in dict(held.get(_PRACTICES) or {}).items()}
    outputs = dict(held.pop("outputs", None) or {})
    for key, practice in practices.items():
        formats = practice.pop("formats", None)
        for name, chosen in dict(formats or {}).items():
            practice.setdefault(_FIDELITIES, {}).setdefault(name, {})["formats"] = [chosen] if isinstance(chosen, str) else list(chosen)
    for key, chosen in outputs.items():
        practice = practices.setdefault(key, {})
        for name, value in dict(chosen).items():
            if name == "root":
                practice.setdefault("root", value)
                continue
            fidelity = practice.setdefault(_FIDELITIES, {}).setdefault(name, {})
            for part, kept in dict(value).items():
                if part == "root":
                    fidelity["roots"] = [kept]
                elif part == "roots":
                    fidelity["roots"] = list(kept)
                else:
                    fidelity.setdefault("file_names", {})[part] = kept
    if practices:
        held[_PRACTICES] = practices
    held.pop("repo_path", None)
    return held


class OwnedFields:
    """The fields one owner outside the session keeps in its session.json, such as the board's stage and mark for a
    ticket: read and changed by that owner alone, never one of the session's own fields."""

    def __init__(self, record: SessionRecord, owner: str) -> None:
        self._record = record
        self._owner = owner

    def get(self, key: str) -> object:
        return self._record.fields.raw.get(self._owned(key))

    def save(self, **values: object) -> None:
        """Keep values under their keys, committed on main."""
        for key in values:
            self._owned(key)
        self._record.update(lambda fields: fields.raw.update(values), ", ".join(f"{key} {value}" for key, value in values.items()))

    def _owned(self, key: str) -> str:
        if key in SessionFields.KEYS:
            raise SessionFieldOwnedError(self._owner, key)
        return key


class SessionFieldOwnedError(ValueError):
    """An owner outside the session tried to change one of the session's own fields, which only the session's part
    that owns it writes."""

    def __init__(self, owner: str, key: str) -> None:
        super().__init__(f"{owner} cannot change {key}: it is the session's own field")
        self.owner = owner
        self.key = key


class MisshapenTestTiersError(ValueError):
    """A session.json keeps its test tiers in a shape that cannot be read: anything other than, for each module, a test
    tool for each of the tiers unit, server and web it uses."""

    def __init__(self, found: object) -> None:
        super().__init__(
            f"session.json keeps {_TEST_TIERS} as {found!r}: it holds, for each module's path, the test tool of each "
            f'tier the module uses ({", ".join(TEST_TIERS)}), such as {{"space/kanban": {{"unit": "mamba"}}}}'
        )
        self.found = found


class SessionRecord:
    """The ``session.json`` in one session's folder, which holds its typed fields (*SessionFields*). It is read once for
    each answer that asks (*AnswerReads*), and between answers again only once the file changes. Every change a session
    makes to its folder is queued to be saved on main through it, so its caller never waits for git. Each part of the
    session changes its own fields through ``update``; an owner outside the session keeps its own through ``extra``."""

    def __init__(self, session: Session) -> None:
        self._session = session
        # Its session.json, read again only once the file changes; none before the session has a folder.
        self._held: HeldJsonFile | None = None
        # The file itself, which a change holds, reads and writes; none before the session has a folder.
        self._kept: JsonFile | None = None
        # What its session.json holds, read into its typed fields once for each answer that asks.
        self._fields = HeldForAnswer[SessionFields]()

    def kept_in(self, folder: Path | None) -> None:
        """Read the session.json of folder from now on, the session's folder since it was given one or moved."""
        self._kept = JsonFile(folder / SESSION_FILE) if folder is not None else None
        self._held = HeldJsonFile(self._kept) if self._kept is not None else None
        self._fields.drop()

    @property
    def fields(self) -> SessionFields:
        """What ``session.json`` holds, read once for each answer that asks; nothing before the session has a folder."""
        held = self._held
        if held is None:
            return SessionFields({})
        return self._fields.get(self._session.answer, lambda: SessionFields(held.read()))

    @property
    def fields_on_disk(self) -> SessionFields:
        """What ``session.json`` holds now, read past this answer's reads: another call changes it."""
        return SessionFields(self._held.read() if self._held is not None else {})

    def read_again(self) -> None:
        """Forget what this answer read, so the next ask reads the file."""
        self._fields.drop()

    def extra(self, owner: str) -> OwnedFields:
        """The fields owner, a module outside the session such as the board's ticket, keeps in this session.json."""
        return OwnedFields(self, owner)

    def update(self, change: Callable[[SessionFields], object], said: str) -> None:
        """Change the fields as ``session.json`` holds them now, not as this answer read them, keeping what others store
        there, and make the session's folder when it has none yet, as a project's main session has none until something
        is saved in it. said names the change in the commit that saves it on main. It begins a new answer, so no read in
        this process answers what the file held before. The file is held from the read to the write (``held``), so a
        change another chat or process makes to the same session at the same moment waits its turn and neither is lost.
        A session.json that is not a readable JSON object, such as one a killed writer left half written, is refused by
        name (*JsonFileUnreadable*) and left as it is, never read as empty and written over."""
        file = self._file
        try:
            with self.held():
                # Read from the file itself, past what a read before the hold kept, which another holder has since changed.
                fields = SessionFields(file.read())
                change(fields)
                file.write(fields.as_dict())
        finally:
            self._forget_what_was_read()
            ANSWER_READS.begin()
        self.saved(self._shown(said))

    @contextmanager
    def held(self) -> Iterator[None]:
        """Hold ``session.json`` for one change, from its read to its write (``JsonFile.held``, the operating system's
        lock on ``session.json.lock`` beside it). Every change to the record goes through ``update``, which holds it,
        so no caller changes it unheld. The lock ends when its holder lets go or its process ends, however it ends, so
        a killed holder blocks nobody; a holder that keeps it past the wait refuses the waiting change (*JsonFileBusy*)."""
        with self._file.held():
            yield

    @property
    def _file(self) -> JsonFile:
        """Its session.json: in the folder it was given, else where the session's file will be once something is saved."""
        return self._kept if self._kept is not None else JsonFile(self._session.session_file)

    def _forget_what_was_read(self) -> None:
        """Read the file again on the next ask, in this answer and between answers."""
        self._fields.drop()
        if self._kept is not None:
            self._held = HeldJsonFile(self._kept)

    def save(self) -> None:
        """Save the session's name and workpath, creating its folder, and keep the fields others store there, such as a
        board ticket's title, scope, and parent."""
        session = self._session
        if session.record_folder is None:
            return
        name, workpath = session.name, session.workpath_from_checkout

        def placed(fields: SessionFields) -> None:
            fields.name = name
            fields.workpath = workpath

        self.update(placed, f"name {name}, workpath {workpath}")

    def saved(self, change: str) -> None:
        """Queue the save on main of change to the session, such as ``stage Specification``: every change to a session
        is kept on main for every chat and worktree, committed and pushed on the saving thread."""
        self._session.sessions.saves.later(f"sessions: {self._session.name} {change}")

    def _shown(self, text: str) -> str:
        """A saved value as a commit message names it, cut short."""
        return text if len(text) <= _SHOWN_CHARACTERS * 3 else f"{text[:_SHOWN_CHARACTERS * 3]}…"
