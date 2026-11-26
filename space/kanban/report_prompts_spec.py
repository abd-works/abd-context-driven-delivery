"""What a validation report's Fix, False, and Fix all buttons send a ticket's chat, as the board reads the report from
fidelity-progress.report: Python writes every word, and the board only sends them (pinned word for word 2026-11-22).
The rule's own text comes from its practice's guidance, so it is read from the report, not written here."""

from pathlib import Path

from expects import equal, expect
from mamba import after, before, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from space.kanban.board_tools_examples import DISCOVERY_DONE, ProjectTools, STORY_MAP_GRAPH  # noqa: E402
from space.session.spec_support.throwaway_project import OPEN_PROJECTS  # noqa: E402

_REPORT = ".sessions/pet-visits/validation-reports/stories-story-map-20261031T041200.md"
_SESSION = " session=.sessions/pet-visits/session.json"
_EVERY_FORMAT = "Fix every format of the fidelity: its documents, its diagrams, and its code."
_KEEP_BEHAVIOUR = (
    "Keep what the code does: before changing code, name the scenarios and tests that state what it does today, write the missing test first "
    "where none covers the behaviour you are about to reshape and see it pass on the code as it is, and run them again after the change. "
    "A finding cleared by changing what the code does is not fixed."
)
_ERROR = "docs/map.md:12: Name the story with a verb\n  10 | line 10\n  11 | line 11\n> 12 | line 12\n  13 | line 13\n  14 | line 14\n  15 | line 15\n  16 | line 16"


with description("a validation report's prompts on the board") as self:
    with before.all:
        project = ProjectTools()
        project.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
        (project.root / "docs").mkdir()
        (project.root / "docs" / "map.md").write_text("".join(f"line {number}\n" for number in range(1, 21)), encoding="utf-8")
        project.report("pet-visits", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
        self.report = project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")
        self.rule = self.report["rules"][0]
        self.described = f"verb-noun-format: {self.rule['rule']['body']}"

    with after.all:
        OPEN_PROJECTS.close_all()

    with it("should ask one violation's Fix to fix it in every format, keeping what the code does, then validate the rule on the files changed"):
        expect(self.rule["violation_prompts"][0]["fix"]).to(equal(
            f"Fix this violation of the stories-story-map rule.\n\n{self.described}\n\n1. {_ERROR}\n\n"
            f"Change each file so the content marked > follows the rule, and change nothing the errors do not name. {_EVERY_FORMAT} {_KEEP_BEHAVIOUR} "
            f"Then validate stories-story-map with rule verb-noun-format on the files you changed.{_SESSION}"
        ))

    with it("should ask one violation's False to investigate the rule and leave the content alone"):
        expect(self.rule["violation_prompts"][0]["false"]).to(equal(
            f"This violation of the stories-story-map rule is false. Investigate the rule for errors.\n\n{self.described}\n\n{_ERROR}\n\n"
            "Find why verb-noun-format reported this: read the rule's text and the check that judges it, and run it on the content marked >. "
            "Say whether the rule's wording, its check, or what the check read is wrong, then correct that test first. Change none of the content "
            f"the finding names. If the finding turns out to be right, say why and change nothing.{_SESSION}"
        ))

    with it("should ask a rule's Fix all to fix every violation of the rule the report it names found"):
        expect(self.rule["fix_prompt"]).to(equal(f"Fix all violations of verb-noun-format found in this report: {_REPORT}. {_EVERY_FORMAT} {_KEEP_BEHAVIOUR}{_SESSION}"))

    with it("should ask the report's Fix all to fix every violation the report it names found"):
        expect(self.report["fix_prompt"]).to(equal(f"Fix all violations found in this report: {_REPORT}. {_EVERY_FORMAT} {_KEEP_BEHAVIOUR}{_SESSION}"))
