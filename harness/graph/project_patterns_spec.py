"""The patterns a graph overlays for a project: those CDD ships and those the project keeps in its own guidelines
folder, less each its .context/config.json disables, read for that project alone."""

import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, context, description, it

import cdd_guidance.patterns  # noqa: F401 - registers the patterns CDD ships with the graph's overlays
from harness.graph.graph import Graph
from harness.graph.graph_build import BuildOrder, BuildStep, BuildTask
from harness.graph.pattern_overlays import PatternOverlays
from harness.graph.saved_graph import SavedGraph
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE

# A project that keeps acme_domain_driven in its guidelines folder and disables lern_domain_driven.
_ACME = Path(__file__).resolve().parent / "_examples" / "project_guidelines"
_REPLACED = "repository-is-collection-lifecycle"


def _ddd():
    return next(practice for practice in PRACTICE_CATALOGUE.create_all(fidelity=None) if practice.key == "ddd")


with description("the patterns a graph overlays for a project"):
    with before.all:
        self.folder = Path(tempfile.mkdtemp(prefix="cdd-project-patterns-"))
        self.acme = self.folder / "acme"
        shutil.copytree(_ACME, self.acme)
        self.other = self.folder / "other"
        self.other.mkdir()
        self.ddd = _ddd()

    with after.all:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("with a project that keeps its own pattern and disables the LERN pattern"):
        with before.all:
            self.overlays = PatternOverlays.from_project(self.acme, ["acme_domain_driven", "lern_domain_driven"])

        with it("should list its own pattern"):
            expect(self.overlays.names).to(contain("acme_domain_driven"))

        with it("should not list the pattern it disables"):
            expect("lern_domain_driven" in self.overlays.names).to(equal(False))

        with it("should apply its own pattern and leave out the disabled one"):
            expect([pattern.pattern for pattern in self.overlays.patterns]).to(equal(["acme_domain_driven"]))

        with it("should check a practice with its own pattern's graph rule in place of the practice's of that name"):
            expect(type(self.overlays.checks_of(self.ddd)[_REPLACED]).__module__).to(contain(".acme_domain_driven.practices.ddd.rules"))

        with it("should read its own pattern's written rules"):
            expect([rule.slug for rule in self.overlays.pattern_named("acme_domain_driven").rules]).to(equal(["repository-is-crud", "root-saves-itself"]))

    with context("with another project the same process serves"):
        with before.all:
            self.overlays = PatternOverlays.from_project(self.other, ["acme_domain_driven", "lern_domain_driven"])

        with it("should not list the first project's pattern"):
            expect("acme_domain_driven" in self.overlays.names).to(equal(False))

        with it("should apply the LERN pattern it does not disable"):
            expect([pattern.pattern for pattern in self.overlays.patterns]).to(equal(["lern_domain_driven"]))

        with it("should check a practice with the practice's own rule"):
            expect(type(self.overlays.checks_of(self.ddd)[_REPLACED]).__module__).to(equal("cdd_guidance.practices.ddd.rules.tactical"))

    with context("with a graph that chooses its patterns among a project's"):
        with before.all:
            self.graph = Graph([_ddd()])
            self.graph.use_patterns_of(self.acme)
            self.graph.overlays = ["acme_domain_driven"]

        with it("should apply the project's own pattern"):
            expect([pattern.pattern for pattern in self.graph.applied_patterns.patterns]).to(equal(["acme_domain_driven"]))

        with it("should tell a worker that builds it which project its patterns are chosen among"):
            order = BuildOrder.from_graph(self.graph, BuildTask(BuildStep.READ), SavedGraph.from_graph(self.graph))
            expect(BuildOrder.from_text(order.text).patterns_project).to(equal(self.acme.resolve()))
