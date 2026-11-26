"""ChangedArtifact - a file or folder checked against the graph rules of each fidelity the session shows that declares it."""

from expects import equal, expect

from space.kanban.changed_artifact_examples import ONE_SUB_EPIC_MAP, README, STORY_MAP, checkout_flow_of, edit, reports_written, seed_checkout_flow

# Seed: the folder the story map sits in, as the Files app's file menu names it.
CONTEXT_FOLDER = ".context"
# Seed: a folder holding only files no fidelity declares.
DOCS_FOLDER = "docs"


# The person's answer (2026-11-26): the Files app's file menu validates a file or a folder, through the same check the
# chat bar runs after an edit.
with description("ChangedArtifact") as self:
    with context("that names a folder holding a file a shown fidelity declares"):
        with before.all:
            self.project = seed_checkout_flow()
            edit(self.project, STORY_MAP, ONE_SUB_EPIC_MAP)
            self.checked = checkout_flow_of(self.project).check_changed_artifact(CONTEXT_FOLDER)

        with after.all:
            self.project.close()

        with it("should run that fidelity's graph rules on the folder"):
            expect(self.checked.checked).to(equal(["stories-story-map"]))

        with it("should save a report"):
            expect(len(reports_written(self.project))).to(equal(1))

    with context("that names a folder no shown fidelity declares a file in"):
        with before.all:
            self.project = seed_checkout_flow()
            edit(self.project, f"{DOCS_FOLDER}/{README}", "# Shop" + chr(10))
            self.checked = checkout_flow_of(self.project).check_changed_artifact(DOCS_FOLDER)

        with after.all:
            self.project.close()

        with it("should check it with none"):
            expect(self.checked.checked).to(equal([]))
