"""The practices CDD ships. Importing this package registers them with the framework's practice catalogue, in the order
the approach walks them, so the framework works with the practices without naming them."""

from harness.guidance.practice_catalogue import PracticeCatalogue

from cdd_guidance.practices.stories.stories import Stories
from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.ux.ux import Ux
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.bdd.bdd import Bdd

PracticeCatalogue.register(Stories, Ddd, Ux, CleanEngineering, Bdd)
