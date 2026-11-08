"""The formats CDD writes artifacts in, and the short names and file extensions each one goes by."""

from __future__ import annotations


class Format:
    """*Format* is a channel an artifact is written in, such as `markdown`, `python`, or `drawio`. A format goes by its
    name and by a short name, which is also its file extension: `md` is `markdown` and `py` is `python`. Every reader
    of a format, an extension, or a template folder asks this class, so a format means the same thing everywhere.

    Markdown and the code formats keep their templates in a folder named for the short name, such as `templates/py/`,
    with the format's extension; every other format's template is found by its name alone.
    """

    _SHORT_NAMES = {"markdown": "md", "python": "py", "typescript": "ts", "javascript": "js"}
    _NAMES_BY_SHORT_NAME = {short: name for name, short in _SHORT_NAMES.items()}
    CODE = frozenset({"python", "typescript", "java", "javascript"})
    TEMPLATED = frozenset({"markdown", *CODE})
    # The groups a person picks formats by, in the order an action bar offers them: a diagram, the markdown, or the
    # code. Any other format is a group of its own, under its own name.
    GROUPS: dict[str, tuple[str, ...]] = {
        "diagram": ("drawio",),
        "markdown": ("markdown",),
        "code": ("python", "typescript", "javascript", "java", "html"),
    }
    # The order a fidelity's files are shown in, by group: prose first, then the code, then the diagrams drawn from them.
    FILE_ORDER: tuple[str, ...] = ("markdown", "code", "diagram")

    def __init__(self, name: str | None) -> None:
        folded = (name or "").strip().casefold()
        self._name = self._NAMES_BY_SHORT_NAME.get(folded, folded)

    @classmethod
    def from_extension(cls, extension: str) -> Format:
        """The format of a file with this extension, written with or without its dot: `.py` is `python`."""
        return cls(extension.lstrip("."))

    @property
    def name(self) -> str:
        """The format's own name, `markdown` for `md`; empty when no format was given."""
        return self._name

    @property
    def short(self) -> str:
        """The short name, `md` for `markdown`; a format with no short name goes by its name."""
        return self._SHORT_NAMES.get(self._name, self._name)

    @property
    def extension(self) -> str:
        """The extension a file in this format ends with, `.md` for `markdown`; empty when no format was given."""
        return f".{self.short}" if self._name else ""

    @property
    def is_code(self) -> bool:
        return self._name in self.CODE

    @property
    def group(self) -> str:
        """The group a person picks this format by, `code` for `python`; a format in no group is a group of its own."""
        return next((group for group, members in self.GROUPS.items() if self._name in members), self._name)

    @property
    def group_order(self) -> int:
        """Where this format's group comes among the groups an action bar offers; a group of its own comes after them."""
        groups = list(self.GROUPS)
        return groups.index(self.group) if self.group in groups else len(groups)

    @property
    def file_order(self) -> int:
        """Where a file in this format comes among a fidelity's files: by its group in `FILE_ORDER`; a group of its own
        comes after them."""
        return self.FILE_ORDER.index(self.group) if self.group in self.FILE_ORDER else len(self.FILE_ORDER)

    @property
    def is_templated(self) -> bool:
        """Whether this format keeps its templates in its own folder with its own extension."""
        return self._name in self.TEMPLATED

    @property
    def template_folder(self) -> str:
        """The folder under `templates/` that holds this format's templates; empty for a format that has none."""
        return self.short if self.is_templated else ""

    @property
    def template_extension(self) -> str:
        """The extension this format's templates end with; empty for a format whose template is found by name."""
        return self.extension if self.is_templated else ""


# The folder names a practice's templates are kept under, one for each templated format: `md`, `py`, ...
TEMPLATE_FOLDER_NAMES = frozenset(Format(name).short for name in Format.TEMPLATED)
