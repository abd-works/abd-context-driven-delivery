"""BDD generator - multi-fidelity behavior skeletons and development."""

from __future__ import annotations

from cdd_guidance.practices.bdd.model.bdd_model import BddModel
from cdd_guidance.practices.bdd.model.code_spec_model import JavaScriptBddModel, PythonBddModel, TypeScriptBddModel
from cdd_guidance.practices.bdd.model.graph_bdd_model import GraphBddModel
from cdd_guidance.practices.bdd.model.graph_reading import BddGraphReading
from cdd_guidance.practices.bdd.model.nodes import BehaviorNode
from cdd_guidance.practices.bdd.model.sketch.sketch_bdd_model import SketchBddModel
from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class Bdd(PracticeGuidance):
    """# Instructions"""

    # Its section of a sketch is the one its sketch format reads, held as that one lens.
    sketch_lens = SketchBddModel.lens
    SHORT_NAME = "BDD"
    COLOUR = "#00B894"

    # How the catalog shows this practice; the generator discovers it like the installer does.
    catalog_card = {
        "name": "Behavior-Driven Development",
        "label": "behavior-driven-development",
        "family": "aad-fam-bdd",
        "perspective": "bdd",
        "order": 40,
        "blurb": "Specify domain logic through behavioural, automated tests.",
        "spec_blurb": "Nested describe/it behaviour tests that serve as both documentation and automated tests for domain logic",
    }

    first_fidelity = "behavior"

    default_workspace_folder = "src"
    format_adapters = {
        "sketch": SketchBddModel,
        # The describe tree as indented lines: the canonical model spells it itself.
        "markdown": BddModel,
        "python": PythonBddModel,
        "typescript": TypeScriptBddModel,
        "javascript": JavaScriptBddModel,
        # A saved knowledge graph, read only: rendering from it draws the realization fidelity.
        "graph": GraphBddModel,
    }

    # In the knowledge graph: BDD's describe trees, linked to the Clean Engineering members each observation drives.
    reading_type = BddGraphReading


BddModel.practice_class = Bdd
BehaviorNode.practice_class = Bdd
