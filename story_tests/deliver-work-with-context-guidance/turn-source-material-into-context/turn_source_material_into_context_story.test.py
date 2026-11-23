# ---
# fidelity: [specification]
# artifact: [story-scenarios]
# format: py
# ---
#
# Turn Source Material Into Context, as GWT structure only. Generated from the markdown beside it, which holds the domain
# terms, the evidence and the examples. Each scenario is proven by the specs its story's evidence names.

from __future__ import annotations

from story_test import and_, given, scenario, story, then, when


with story("Describe Existing Artifacts"):
    with scenario("Name the paths to scan"):
        with given('.context/story-map.md holds the story map'):
            pass
        with when('Claude Code documents stories-story-map with paths .context/story-map.md'):
            pass
        with then('the instructions name .context/story-map.md as the path to scan'):
            pass
    with scenario("Refuse a path that is not there"):
        with given('nope/missing.md is not in the project'):
            pass
        with when('Claude Code documents stories-story-map with paths nope/missing.md'):
            pass
        with then('the call is refused, naming nope/missing.md as not there'):
            pass
    with scenario("Refuse a path outside the session's root"):
        with given('../outside/story-map.md holds a story map in a folder beside the project'):
            pass
        with when('Claude Code documents stories-story-map with paths ../outside/story-map.md'):
            pass
        with then("../outside/story-map.md is refused as not under the session's root"):
            pass
