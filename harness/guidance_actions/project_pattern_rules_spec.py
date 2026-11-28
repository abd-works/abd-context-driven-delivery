"""The written rules an action holds the agent to in a session overlaying a pattern its project keeps in its own
guidelines folder: the pattern's shared rules, each replacing a practice's rule of the same name."""

import shutil
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.actions  # noqa: F401 - registers the actions with the action catalogue
import cdd_guidance.patterns  # noqa: F401 - registers the patterns CDD ships
from cdd_guidance.actions.generate.generate import Generate
from harness.agent_tools.tool_call import ToolCall
from space.session import Sessions
from space.session.session import NotAPatternError
from space.session.spec_support.throwaway_project import OPEN_PROJECTS, ThrowawayProject

# A project that keeps acme_domain_driven in its guidelines folder and disables lern_domain_driven.
_ACME = Path(__file__).resolve().parents[1] / "graph" / "_examples" / "project_guidelines"
# The DDD model rule acme's shared rule of the same name replaces, and one it leaves standing.
_REPLACED = "`repository-is-crud`"
_KEPT = "`root-card-carries-repository`"


def _session(project: Path, overlays: list[str]):
    """A session of project overlaying overlays, and the session word a call names it by."""
    (project / ".git").mkdir()
    session = Sessions(project).create("models", project)
    session.choose_overlays(overlays)
    return session, f"session={(project / '.sessions' / 'models' / 'session.json').as_posix()}"


with description("an action in a session that overlays its project's own pattern"):
    with after.all:
        OPEN_PROJECTS.close_all()

    with context("with a project that keeps the pattern and disables the LERN pattern"):
        with before.all:
            self.project = ThrowawayProject().root
            shutil.copytree(_ACME / "guidelines", self.project / "guidelines")
            (self.project / ".context").mkdir(exist_ok=True)
            shutil.copy(_ACME / ".context" / "config.json", self.project / ".context" / "config.json")
            self.session, word = _session(self.project, ["acme_domain_driven"])
            self.generate = Generate().for_call(ToolCall({"guidance": f"ddd-model {word}"}, self.project))
            self.rules = self.generate.rules_to_follow

        with it("should offer the project's own pattern to choose"):
            expect(self.session.pattern_overlays([]).names).to(contain("acme_domain_driven"))

        with it("should refuse the pattern the project disables"):
            expect(lambda: self.session.choose_overlays(["lern_domain_driven"])).to(raise_error(NotAPatternError))

        with it("should hold the agent to the pattern's shared rules"):
            expect(self.generate.brief.overlay_rules()).to(contain("root-saves-itself"))

        with it("should leave out the practice's rule the pattern replaces"):
            expect(_REPLACED in self.rules).to(equal(False))

        with it("should keep the practice's rules the pattern does not replace"):
            expect(self.rules).to(contain(_KEPT))

    with context("with another project that keeps no pattern of its own"):
        with before.all:
            self.project = ThrowawayProject().root
            self.session, word = _session(self.project, [])
            self.generate = Generate().for_call(ToolCall({"guidance": f"ddd-model {word}"}, self.project))

        with it("should not offer the first project's pattern"):
            expect("acme_domain_driven" in self.session.pattern_overlays([]).names).to(equal(False))

        with it("should keep the practice's rule"):
            expect(self.generate.rules_to_follow).to(contain(_REPLACED))
