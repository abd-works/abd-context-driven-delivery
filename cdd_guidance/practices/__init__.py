"""The practices CDD ships. Importing this package registers them with the framework's practice catalogue, in the order
the approach walks them, and the supplements that add to them, such as TDD, so the framework works with the practices
without naming them."""

from pathlib import Path

from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.markdown import SOURCE_STAMPS

from cdd_guidance.practices.stories.stories import Stories
from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.ux.ux import Ux
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.tdd.tdd import Tdd

PracticeCatalogue.register(Stories, Ddd, Ux, CleanEngineering, Bdd)
# Supplements add to the practices' fidelities and are never listed among them.
PracticeCatalogue.register_supplements(Tdd)
# The guidance CDD ships is edited by hand, not by the actions that read it, so its files are looked at again at most once
# a second rather than on every read.
SOURCE_STAMPS.hold_steady(Path(__file__).resolve().parent.parent)
