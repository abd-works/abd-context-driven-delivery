"""The roots one fidelity proposes for the pieces a ticket works on: the narrowest folder that holds each piece."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Iterable

from cdd_guidance.practices.clean_engineering.model.production_code import is_test_code
from harness.guidance.declared_outputs import DeclaredFile
from harness.markdown.format import Format

if TYPE_CHECKING:
    from space.session.practice_session_output import FidelitySessionOutput

_NAMED_FOLDER = re.compile(r"^\{[^{}/]+\}$")
_FILLED_IN = re.compile(r"[{*?]")
# A code format whose files also carry a second extension, such as React components in TypeScript; any other code format
# is its own extension alone.
_CODE_EXTENSIONS = {"typescript": (".ts", ".tsx"), "javascript": (".js", ".jsx")}
# The root of the project, which a document declared under `.context` at the top proposes.
PROJECT_TOP = "."


class ProposedRoots:
    """The folders one fidelity proposes to write under in a session, for the pieces its ticket works on: for each file
    it declares, the narrowest folder holding the piece that file is part of, as the fidelity's own declared outputs
    name it. A path such as ``story_tests/{epic}/{sub-epic}/...`` names a sub-epic's folder, ``{bounded_context}/
    {aggregate}/...`` an aggregate's, and code written as a folder per module the package the file is in. Each folder
    is a path from the project, as ``choose_root`` and ``add_root`` take it."""

    def __init__(self, output: FidelitySessionOutput) -> None:
        self._output = output

    @property
    def _session(self):
        return self._output.practice.session

    def proposed(self, names: list[str]) -> list[str]:
        """The folders holding what the session's branch changed and the pieces names name, such as the aggregate a
        ticket's text names: what an agent setting up a session shows the person before setting any root."""
        changed = self._session.session_files.branch_changes.files()
        return sorted(set(self.holding(changed)) | set(self.named(names)))

    def holding(self, files: Iterable[Path]) -> list[str]:
        """The narrowest folder holding the piece of each of files this fidelity writes, each once; none for a file it
        does not write."""
        claimed = (file for file in files if self._is_own(Path(file)))
        folders = (self._piece_folder(self._session.repo.path_from_top(file)) for file in claimed)
        return sorted({folder for folder in folders if folder is not None})

    def _is_own(self, file: Path) -> bool:
        """Whether file is a piece of this fidelity's: one its practice claims, and, for a practice that claims all code,
        one no other practice the session works on claims as its narrower piece, such as DDD an aggregate's code."""
        practice = self._output.fidelity.practice_guidance
        if practice is None:
            return True
        if not practice.claims(file):
            return False
        if practice.claims_some_code:
            return True
        narrower = (output.guidance for output in self._session.own_practices.values() if output.enabled and output.guidance is not practice)
        return not any(other.claims_some_code and other.claims(file) for other in narrower)

    def named(self, names: list[str]) -> list[str]:
        """The folders of the pieces this fidelity holds in the project whose own name holds one of names, as text
        with case and separators ignored, so Refund names domain/orders/refund and story_tests/manage-orders/refund-order."""
        wanted = [squashed for squashed in (self._squashed(name) for name in names) if squashed]
        if not wanted:
            return []
        return [folder for folder in self.holding(self._project_files()) if any(name in self._squashed(PurePosixPath(folder).name) for name in wanted)]

    def _squashed(self, text: str) -> str:
        """text in lower case with everything but letters and digits left out, so names compare across case and separators."""
        return re.sub(r"[^a-z0-9]", "", text.lower())

    def _project_files(self) -> list[Path]:
        """Every file in the project a declared path of this fidelity can name, and its code where it writes a folder
        per module."""
        globs = [DeclaredFile(template).glob for template in self._declared_files()]
        globs += [f"**/*{extension}" for extension in self._code_extensions()]
        return [file for found in self._session.session_files.find_each(globs).values() for file in found]

    def _piece_folder(self, path: str) -> str | None:
        """The narrowest folder holding the piece path is part of, path being from the project: through the deepest
        named folder its declared path shares with the fidelity's other paths under the same fixed folder, else the
        folder the declared path hangs off; for code written as a folder per module, its own folder."""
        for template in self._declared_files():
            match = DeclaredFile(template).pattern.search(path)
            if match is not None:
                piece = self._piece_name(template)
                return path[: match.end(piece) if piece else match.start()] or PROJECT_TOP
        if self._writes_code(path):
            return PurePosixPath(path).parent.as_posix()
        return None

    def _piece_name(self, template: str) -> str:
        """The group naming the folder of the piece a file at template is part of: template's deepest named folder,
        or the named folder above it while that one holds other declared paths of this fidelity and nothing is
        declared below the deeper one. So ``story_tests/{epic}/{sub-epic}/{story}/...`` names ``sub_epic``, whose
        folder also holds the sub-epic's tier files, a story directly under an epic
        (``story_tests/{epic}/{story}/...``) names ``epic``, and ``{bounded_context}/{aggregate}/...`` names
        ``aggregate``, whose context holds nothing else. Empty when template names no folder."""
        folders = PurePosixPath(template).parts[:-1]
        head = self._fixed_head(template)
        siblings = [PurePosixPath(other).parts[:-1] for other in self._declared_files() if self._fixed_head(other) == head]
        named = [index for index, part in enumerate(folders) if _NAMED_FOLDER.match(part)]
        while len(named) > 1 and named[-2] == named[-1] - 1 and self._is_part_of_folder_above(folders[: named[-1] + 1], siblings):
            named.pop()
        return re.sub(r"\W", "_", folders[named[-1]].strip("{}")) if named else ""

    def _is_part_of_folder_above(self, folder: tuple[str, ...], declared: list[tuple[str, ...]]) -> bool:
        """Whether folder, a declared path's folders down to a named one, is part of the piece the folder above it
        names: nothing is declared below folder, and the folder above holds other declared paths."""
        below = [folders for folders in declared if folders[: len(folder)] == folder and folders != folder]
        beside = [folders for folders in declared if folders[: len(folder) - 1] == folder[:-1] and folders[: len(folder)] != folder]
        return not below and bool(beside)

    def _fixed_head(self, template: str) -> tuple[str, ...]:
        """The folders a declared path names outright before its first named or wildcard part."""
        parts = PurePosixPath(template).parts[:-1]
        return tuple(part for part in parts[: next((index for index, part in enumerate(parts) if _FILLED_IN.search(part)), len(parts))])

    def _declared_files(self) -> list[str]:
        """The files this fidelity's outputs declare, each once; a folder declared per module names no file."""
        declared = (names for names in self._output.fidelity.outputs.values())
        every = (name for names in declared for name in ([names] if isinstance(names, str) else names))
        return list(dict.fromkeys(name for name in every if name and not name.endswith("/")))

    def _code_extensions(self) -> list[str]:
        """The extensions of the code this fidelity writes as a folder per module, such as Clean Engineering's
        ``{module}/``."""
        return [extension for label in self._output.fidelity.declared.code_folders() for extension in code_extensions(label)]

    def _writes_code(self, path: str) -> bool:
        """Whether path is production code this fidelity writes as a folder per module."""
        return not is_test_code(path) and PurePosixPath(path).suffix in self._code_extensions()


def code_extensions(label: str) -> tuple[str, ...]:
    """The extensions of the files a code format such as python writes."""
    return _CODE_EXTENSIONS.get(Format(label).name, (Format(label).extension,))
