"""*CatalogPractice*, one practice as the catalog shows it. The catalog's pages and boards, and a project's own approach
page, all read it."""
from __future__ import annotations

import shutil
from functools import cached_property
from pathlib import Path
from typing import Any

from harness.agent_tools.agent_tools import InstallDestination
from harness.annotations.name import Name
from harness.catalog_generator.catalog_examples import EXAMPLES_FOLDER, CatalogFidelity
from harness.catalog_generator.stage_columns import StageColumn
from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.installation.destination import NoCatalog
from harness.installation.files import FileInstallation
from harness.installation.ide_layout import IdeLayout

_REPO_ROOT = Path(__file__).resolve().parents[2]
# The IDE whose skill names the catalog shows as slash commands.
_SLASH_COMMAND_IDE = "Claude"


class CatalogPractice:
    """One practice as the catalog shows it: the live ``PracticeGuidance``, the catalog card it gives itself, its place in
    the practice catalogue, and the catalog's view of each fidelity it shows (a ``CatalogFidelity``), made once and
    kept with the fidelity's board column. Every page, board ticket, and grid card for the practice reads it. Its slash
    command is the name the skill install gives the practice's skill, held in ``skills``, the one skill install the
    practices of one catalog share."""

    _CARD_DEFAULTS: dict[str, Any] = {
        "family": "aad-fam-other",
        "perspective": "other",
        "order": 100,
        "blurb": "",
        "spec_blurb": "",
        "stage_examples": False,
    }

    def __init__(self, practice: PracticeGuidance, skills: FileInstallation | None = None, position: int = 0) -> None:
        self.practice = practice
        self.position = position
        self._skills = skills if skills is not None else self.skill_install()
        self._card = self._card_of(type(practice))

    @staticmethod
    def skill_install() -> FileInstallation:
        """The skill install whose folder names are the slash commands the catalog shows."""
        return FileInstallation(
            IdeLayout(_SLASH_COMMAND_IDE),
            _REPO_ROOT / IdeLayout(_SLASH_COMMAND_IDE).folder_name,
            destination=InstallDestination.SKILL,
            repo=_REPO_ROOT,
        )

    @classmethod
    def load_all(cls) -> list[CatalogPractice]:
        """Every practice in the practice catalogue with a fidelity on the board, unless annotated ``@noCatalog``, in the
        order each practice's catalog card gives. Each keeps its place in the catalogue, the order the approach's grids
        list the practices in, and all share one skill install."""
        skills = cls.skill_install()
        catalogued = enumerate(PracticeCatalogue.practices())
        practices = [
            cls(practice, skills, position) for position, practice in catalogued if not NoCatalog.annotates(type(practice))
        ]
        shown = [practice for practice in practices if practice.on_board]
        return sorted(shown, key=lambda practice: (practice.order, practice.display_name))

    @staticmethod
    def giving_stage_examples(practices: list[CatalogPractice]) -> CatalogPractice | None:
        """Of practices, the one whose card says its artifacts are the approach's stage examples (Stories); none when
        none of them is."""
        return next((practice for practice in practices if practice.gives_stage_examples), None)

    def _card_of(self, practice_class: type) -> dict[str, Any]:
        card = {**self._CARD_DEFAULTS, **(getattr(practice_class, "catalog_card", None) or {})}
        card.setdefault("name", " ".join(word.capitalize() for word in Name(practice_class.__name__).words))
        card.setdefault("label", Name(card["name"]).title_slug)
        return card

    @property
    def key(self) -> str:
        """The practice's key, such as ``clean_engineering``: its page names and board tickets use it."""
        return self.practice.key

    @property
    def display_name(self) -> str:
        return self._card["name"]

    @property
    def label(self) -> str:
        """The practice's kebab-case name on the board's practice rail and approach grids."""
        return self._card["label"]

    @property
    def product_engineering_label(self) -> str:
        """The rail label of the practice's Product Engineering board: its card's, else its key in kebab case."""
        return self._card.get("product_engineering_label") or Name(self.key).kebab

    @property
    def gives_stage_examples(self) -> bool:
        """Whether the approach's stage examples are this practice's artifacts, as its card says."""
        return bool(self._card["stage_examples"])

    @property
    def family(self) -> str:
        """The practice's colour family class on the board."""
        return self._card["family"]

    @property
    def perspective(self) -> str:
        return self._card["perspective"]

    @property
    def order(self) -> int:
        return self._card["order"]

    @property
    def spec_blurb(self) -> str:
        return self._card["spec_blurb"]

    @property
    def href(self) -> str:
        return f"context-tools/{self.key}.html"

    @property
    def skill_name(self) -> str:
        """The slash command that runs the practice: the folder the skill install writes the practice's skill into; its
        key when the practice installs no skill."""
        tool = next((tool for tool in self.practice.tools.values() if tool.install_to_skill), None)
        if tool is None:
            return self.key
        return self._skills.relative_path(self.practice, tool.deploy_name).parent.name

    @property
    def fidelities(self) -> list[FidelityGuidance]:
        """The practice's fidelities in declared order, less those annotated ``@noCatalog``."""
        return [shown.fidelity for shown in self.shown_fidelities]

    @cached_property
    def shown_fidelities(self) -> list[CatalogFidelity]:
        """The catalog's view of each fidelity it shows, in declared order, made once."""
        return [CatalogFidelity(fidelity, self) for fidelity in self.practice.fidelities if not NoCatalog.annotates(fidelity)]

    def fidelity_in(self, column: StageColumn) -> CatalogFidelity | None:
        """The practice's fidelity in ``column``; none when the practice has no fidelity at that stage."""
        return next((shown for shown in self.shown_fidelities if shown.column is column), None)

    def fidelity_at(self, stage: str) -> CatalogFidelity | None:
        """The practice's fidelity at the stage named ``stage``, such as ``discovery``; none when it has none there."""
        return next((shown for shown in self.shown_fidelities if shown.stage == stage), None)

    @property
    def board_fidelities(self) -> list[CatalogFidelity]:
        """The fidelities that have a column on the board."""
        return [shown for shown in self.shown_fidelities if shown.column is not None]

    @property
    def on_board(self) -> bool:
        """Whether any fidelity has a board column; a practice with none, such as a pattern, has no catalog page."""
        return bool(self.board_fidelities)

    def fidelity_href(self, fidelity: FidelityGuidance) -> str:
        return f"fidelities/{self.key}-{fidelity.name}.html"

    @property
    def examples_folder(self) -> Path:
        """The practice's ``catalog-examples`` folder, whose files its fidelities show."""
        return Path(self.practice.module_dir) / EXAMPLES_FOLDER

    def language_of(self, path: Path) -> str | None:
        """The language an example file's code is in: the format of this practice, else of another practice in the
        catalogue, that reads it; none when no practice reads it."""
        return self.practice.format_reading_with(path, PracticeCatalogue.practices())

    def copy_examples_into(self, out_root: Path) -> None:
        """Copy the practice's example files into the catalog's ``examples/{practice}`` folder, where its fidelity
        pages and approach panels link them."""
        if not self.examples_folder.is_dir():
            return
        destination = Path(out_root) / "examples" / self.examples_folder.parent.name
        for path in self.examples_folder.iterdir():
            if path.is_file() and not path.name.startswith("."):
                destination.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination / path.name)

    @property
    def shared_markdown(self) -> str:
        """The practice-level ``##`` sections of the practice guide, each with its heading: everything but
        ``## Fidelities``, whose blocks each fidelity page shows. They are read from the practice's own document,
        which gives each ``FidelityGuidance`` its section too."""
        document = self.practice.document
        names = [name for _start, _end, level, name in document.headings() if level == 2]
        sections = (document.slice_heading(name) for name in names if name.casefold() != "fidelities")
        return "\n\n".join(section for section in sections if section)
