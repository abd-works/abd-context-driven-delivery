from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Generate Fidelity Outputs
# Map: ../../../.context/story-map.md#s-claude-code----resolve-fidelity-output-paths
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Resolve Fidelity Output Paths
# Actor: Claude Code
with story("Resolve Fidelity Output Paths"):
    with scenario("Put a fidelity's files under its practice's root"):
        # Evidence: observed: space/session/session_spec.py 'should put each format's file under the practice's root folder'; harness/guidance/fidelity_outputs_spec.py 'should name the file for each format'.
        with given("the [session](../../../.context/kanban-model.md#session) alpha works in /work"):
            pass
        with and_("the story_map fidelity declares markdown .context/story-map.md and drawio .context/story-map.drawio"):
            pass
        with when("Claude Code asks where story_map's files go"):
            # Generate -> Session.fidelity_outputs(Stories story_map)
            # Session -> FidelityGuidance.outputs
            # Session <- markdown /work/.context/story-map.md, drawio /work/.context/story-map.drawio
            pass
        with then("the markdown file is /work/.context/story-map.md"):
            pass
    with scenario("Use the practice's root named in session.json"):
        # Evidence: observed: session_spec.py 'with session.json naming a root folder for the practice' — 'should use that root'.
        with given("alpha's session.json names docs/stories as the stories root"):
            pass
        with when("Claude Code asks where story_map's files go"):
            # Generate -> Session.fidelity_outputs(Stories story_map)
            pass
        with then("the markdown file is /work/docs/stories/.context/story-map.md"):
            pass
    with scenario("Prefer the fidelity's own root"):
        # Evidence: observed: session_spec.py 'with session.json naming a root folder for the fidelity too' — 'should prefer the fidelity's root'.
        with given("alpha's session.json names docs/stories for stories and docs/map for story_map"):
            pass
        with when("Claude Code asks where story_map's files go"):
            # Generate -> Session.fidelity_outputs(Stories story_map)
            pass
        with then("the drawio file is /work/docs/map/.context/story-map.drawio"):
            pass
    with scenario("Rename a single-file output and keep a pattern"):
        # Evidence: observed: session_spec.py 'with session.json naming a file for a single-file output' — 'should use that file name', 'should keep the declared name for the other formats'; 'with session.json naming a file for a patterned output' — 'should keep the declared pattern'.
        with given("alpha's session.json names our-map.md for story_map's markdown and one-file.py for scenarios' python"):
            pass
        with when("Claude Code asks where story_map's and scenarios' files go"):
            # Generate -> Session.fidelity_outputs(Stories story_map)
            # Generate -> Session.fidelity_outputs(Stories scenarios)
            pass
        with then("story_map's markdown is /work/.context/our-map.md and its drawio stays /work/.context/story-map.drawio"):
            pass
        with and_("scenarios' python keeps its declared name, such as archive_ticket_story.test.py for the story Archive Ticket"):
            pass
