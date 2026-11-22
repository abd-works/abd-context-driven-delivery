"""The files a render to code saves: one for each piece of the rendered code, at the path the fidelity declares for it.

A render to Python, TypeScript or JavaScript ends in saved files, as a render to a drawing or a document does, and its
result names them; no code is answered for an agent to save. The rendered code comes in one of five shapes, and each
piece of it is placed by the fidelity's declared paths for the format alone:

- **A file for each name** (a path with its text, as a practice whose formats write several files answers): each path
  one of the declared paths matches is saved under the fidelity's root.
- **One text with a section for each piece**, each under a banner comment naming it (``# === Ordering · Cart ===``, the
  banner the code class model writes between modules): the text is cut at the banners, each section keeps the text's
  opening lines, and the names of its banner fill the named parts of the declared path in the order they come, so
  ``{bounded_context}/{aggregate}/{aggregate}.py`` writes ``ordering/cart/cart.py``.
- **One text of one piece from one of the fidelity's own files**: saved as that file in the other format, the named
  parts read off the source's declared path, so ``catalogue/book/book.ts`` is saved as ``catalogue/book/book.py`` and
  ``src/ordering/.context/ordering-model.md`` as ``src/ordering/ordering.py``.
- **One text of one piece from a source that is not one of the fidelity's files**, such as a sketch: named for the
  source, not for its banner, which may carry a name the reader gave it because the source names none (a sketch of
  Cart is read into a module called KnowledgeGraph). It is saved beside the source at the declared path with one named
  part, so ``design/cart-sketch.md`` against ``{module}/{module}.py`` writes ``design/cart/cart.py``.
- **One text from one source file no named path places**: saved beside the source under the name the fidelity declares for the format, the
  source's own name read off the path the fidelity declares for the source, so ``CartView.tsx`` against
  ``**/*View.tsx`` is saved as ``CartView.jsx`` for ``**/*View.jsx``, and ``cart_spec.py`` as ``cart.spec.ts``. A
  source that is a document in a ``.context`` folder, such as ``.context/bookshop-bdd-realization.md``, describes the
  folder that ``.context`` sits in, so its code is saved there, named for its scope: ``bookshop_spec.py``.

A piece the declared paths cannot place is refused with *RenderHasNoDeclaredPlace*, and nothing is saved: a file
written under a name nobody declared is read by no practice.

A code file already there is never replaced: the render is written onto it (*ReshapedCode*, ``reshaped_code.py``). The
file takes the new shape, a member the source added arriving empty, and keeps everything only it holds: bodies,
comments, imports, helpers, decorators, the text between members. A member the model no longer holds stays in the file,
marked, and the result lists it under ``migrate`` with the added members that may have replaced it, for whoever moves
its body there. A file that already holds exactly the rendered text is left as it is.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from harness.annotations.name import Name
from cdd_guidance.actions.render.reshaped_code import Reshape, ReshapedCode
from harness.guidance.declared_outputs import DeclaredFile
from cdd_guidance.actions.render.render_result import KeptCodeMember, Migration, SavedCode, SignatureDiffers
from harness.guidance.practice_formats import Rendered, Reshaped
from harness.installation.context_config import CONTEXT_FOLDER
from harness.markdown.format import Format

# A banner comment between the sections of one rendered text: ``# === Ordering | custom · Cart ===`` in Python,
# ``// === ... ===`` in TypeScript and JavaScript.
_BANNER = re.compile(r"^\s*(?:#|//)\s*===\s*(.+?)\s*===\s*$")
# What parts a banner's names: the bounded context from its aggregate.
_NAME_SEPARATOR = " · "
# What a heading writes after a name, such as a bounded context's kind (``Ordering | custom``), which is no part of it.
_NAME_NOTE = " | "
_NAMED_PART = re.compile(r"\{([^{}/]+)\}")
_ONE_NAME = "*"


def own_name(source: Path, declared: list[str]) -> str | None:
    """The source's own name, read off the first of the declared paths that names it: ``Cart`` for ``CartView.tsx``
    against ``**/*View.tsx``, ``cart`` for ``cart_spec.py`` against ``**/*_spec.py``, and ``bookshop`` for
    ``.context/bookshop-bdd-realization.md`` against ``.context/{scope}-bdd-realization.md``. None when no declared
    path names it, or the one that does leaves where the name ends unsaid."""
    for path in declared:
        before, found, after = PurePosixPath(path).name.partition(_ONE_NAME)
        if found and _ONE_NAME not in after and _says_where_name_ends(before, after):
            named = re.fullmatch(re.escape(before) + "(.+)" + re.escape(after), source.name)
            if named is not None:
                return named.group(1)
        parts = set(DeclaredFile(path).parts_of(source.as_posix()).values()) if _NAMED_PART.search(path) and not path.endswith("/") else set()
        if len(parts) == 1:
            return parts.pop()
    return None


def _says_where_name_ends(before: str, after: str) -> bool:
    """Whether a declared file name says where the name in it ends: what follows the name starts with a mark or a
    capital, as ``_spec.py``, ``.spec.ts`` and ``View.jsx`` do. ``*spec.ts`` does not: ``cartspec.ts`` and
    ``cart.spec.ts`` both fit it."""
    return bool(before) or (bool(after) and not (after[0].islower() or after[0].isdigit()))


class RenderHasNoDeclaredPlace(ValueError):
    """A render to code made a piece the fidelity's declared paths for that format cannot place: nothing says which
    file it is, so it is not saved, and neither is the rest of the render."""

    def __init__(self, piece: str, format: Format, declared: list[str], reason: str) -> None:
        places = ", ".join(declared) or "no path"
        super().__init__(f"The render to {format.name} made {piece}, which the paths the fidelity declares for {format.name} ({places}) cannot place: {reason}")
        self.piece = piece
        self.format = format
        self.declared = list(declared)


class RenderedCode:
    """The files one render to code saves under a fidelity's root: where each piece of the rendered code goes by the
    paths the fidelity declares for the format, and the write that keeps a code file already there."""

    def __init__(
        self, root: Path, declared: list[str], format: Format, source: Path | None = None, source_declared: list[str] | None = None,
        source_name: str = "", reshape: Reshape | None = None,
    ) -> None:
        self._root = root
        # The paths the fidelity declares for the format, as it writes them, such as ``{module}/{class}.py``.
        self._declared = list(declared)
        self._format = format
        # The one source file the code was rendered from, and every path the fidelity declares, which name it.
        self._source = source
        self._source_declared = list(source_declared or [])
        # The source's name without what its format's files end with: ``cart`` for the sketch ``cart-sketch.md``.
        self._source_name = source_name
        # The format's own way to write a rendered shape onto a file already there, when its adapter has one.
        self._reshape = reshape

    def save(self, rendered: Rendered) -> SavedCode:
        """Write each piece of the rendered code at its declared path and answer the files: ``paths`` the files that
        now hold the render, and ``migrate`` what waits for a person or an agent in a file already there: each
        member it keeps though its model no longer holds it (``kept``, with ``may_have_replaced_it``, the members added
        beside it), and each member whose opening line the model now writes otherwise (``signature_differs``, with
        ``model_has``, the model's line; the file's own line stays). A piece whose file is already there is written onto it,
        losing nothing. Every piece is placed, and every file's new text made, before any is written, so a render that
        cannot be placed whole, or that would lose a line a file holds, saves nothing."""
        written = {file: self._written_onto(file, text) for file, text in self._placed(rendered.content).items()}
        for file, reshaped in written.items():
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(reshaped.text, encoding="utf-8")
        migrate: list[Migration] = [self._migration(file, kept, reshaped) for file, reshaped in written.items() for kept in reshaped.left_to_move]
        migrate += [SignatureDiffers(file, member, line) for file, reshaped in written.items() for member, line in reshaped.changed.items()]
        return SavedCode(rendered, list(written), migrate)

    def _written_onto(self, file: Path, text: str) -> Reshaped:
        """What file holds once text is rendered to it: text itself for a file not there yet, else the file in text's
        shape."""
        if not file.is_file():
            return Reshaped(text, [], [])
        return ReshapedCode(self._format, self._reshape).onto(file.read_text(encoding="utf-8"), text)

    def _migration(self, file: Path, kept: str, reshaped: Reshaped) -> KeptCodeMember:
        """One member to migrate: the file, the member kept, and the members added to the same class, else to the file."""
        owner = kept.rpartition(".")[0]
        beside = [added for added in reshaped.added if owner and added.rpartition(".")[0] == owner]
        return KeptCodeMember(file, kept, beside or ([] if owner else list(reshaped.added)))

    def _placed(self, content: object) -> dict[Path, str]:
        """Each piece of content with the file it goes to."""
        if isinstance(content, dict):
            return {self._declared_file(str(path)): str(text) for path, text in content.items()}
        sections = self._sections(str(content))
        # One text of one piece, rendered from one of the fidelity's own files, is that file in the other format: the
        # source's own path says which folder it is, which a banner's name alone does not (``src/ordering``).
        counterpart = self._counterpart_of(self._source) if self._source is not None and len(sections) <= 1 else None
        if counterpart is not None:
            return {counterpart: str(content)}
        named_for_source = self._named_for_source() if len(sections) == 1 else None
        if named_for_source is not None:
            return {named_for_source: str(content)}
        if sections:
            return {self._section_file(names): text for names, text in sections}
        return {self._beside_source(): str(content)}

    def _declared_file(self, path: str) -> Path:
        """The file at path under the root, a path one of the declared paths matches."""
        if not any(DeclaredFile(declared).pattern.search(path) for declared in self._declared if not declared.endswith("/")):
            raise RenderHasNoDeclaredPlace(path, self._format, self._declared, "none of them matches that file")
        return self._root / path

    def _sections(self, text: str) -> list[tuple[str, str]]:
        """The sections of text, each with its banner's names and its own text under the text's opening lines; none for
        a text with no banner."""
        lines = text.splitlines()
        banners = [index for index, line in enumerate(lines) if _BANNER.match(line)]
        if not banners:
            return []
        opening = lines[: banners[0]]
        ends = [*banners[1:], len(lines)]
        return [(_BANNER.match(lines[start]).group(1), "\n".join([*opening, *lines[start:end]]).rstrip("\n") + "\n") for start, end in zip(banners, ends)]

    def _section_file(self, banner: str) -> Path:
        """The file a section goes to: the first declared path whose named parts the banner's names fill, in order."""
        names = [Name(name.split(_NAME_NOTE)[0]).snake for name in banner.split(_NAME_SEPARATOR)]
        for declared in self._declared:
            parts = list(dict.fromkeys(_NAMED_PART.findall(declared)))
            if parts and len(parts) == len(names) and not declared.endswith("/") and _ONE_NAME not in declared:
                filled = dict(zip(parts, names))
                return self._root / _NAMED_PART.sub(lambda part: filled[part.group(1)], declared)
        raise RenderHasNoDeclaredPlace(f"the section {banner}", self._format, self._declared, "none of them names a file with a part for each of the section's names")

    def _named_for_source(self) -> Path | None:
        """The file one piece rendered from one source goes to when the source names it: beside the source, at the
        first declared path with one named part, filled with the source's own name. None when there is no one source,
        it has no name of its own, or the format declares no such path."""
        name = (own_name(self._source, self._source_declared) or self._source_name) if self._source is not None else ""
        if not name:
            return None
        for declared in self._declared:
            parts = set(_NAMED_PART.findall(declared))
            if len(parts) == 1 and not declared.endswith("/") and _ONE_NAME not in declared:
                return self._source.parent / _NAMED_PART.sub(Name(name).snake, declared)
        return None

    def _counterpart_of(self, source: Path) -> Path | None:
        """The file the format declares for the same named parts the source's declared path reads off it, where the
        source's declared path starts: ``catalogue/book/book.py`` for ``catalogue/book/book.ts`` against
        ``{bounded_context}/{aggregate}/{aggregate}.ts``. None when no declared path with named parts names the source,
        or the format declares none those parts fill."""
        written = source.as_posix()
        for named_by in (DeclaredFile(path) for path in self._source_declared if _NAMED_PART.search(path) and not path.endswith("/")):
            parts = named_by.parts_of(written)
            placed = (DeclaredFile(path).named_with(parts) for path in self._declared if parts and not path.endswith("/"))
            found = next((path for path in placed if path), "")
            if found:
                start = named_by.start_of(written)
                return Path(start) / found if start else self._root / found
        return None

    def _beside_source(self) -> Path:
        """The file one text rendered from one source goes to: beside the source, or beside the ``.context`` folder a
        document sits in, under the declared path's name with the source's own name in it."""
        source = self._source
        if source is None:
            raise RenderHasNoDeclaredPlace("one text from no single source file", self._format, self._declared, "nothing names its file")
        name = own_name(source, self._source_declared)
        if name is None:
            raise RenderHasNoDeclaredPlace(f"code from {source.name}", self._format, self._declared, f"no path the fidelity declares names {source.name}, so its own name cannot be read")
        folder = source.parent.parent if source.parent.name == CONTEXT_FOLDER else source.parent
        for declared in self._declared:
            before, found, after = PurePosixPath(declared).name.partition(_ONE_NAME)
            if found and _ONE_NAME not in after and _says_where_name_ends(before, after):
                return folder / f"{before}{name}{after}"
        raise RenderHasNoDeclaredPlace(f"code from {source.name}", self._format, self._declared, "none of them says how the source's name joins the file's name, as `*.spec.ts` or `*View.jsx` does")
