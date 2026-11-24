# ---
# fidelity: [specification]
# artifact: [story-scenarios]
# format: py
# ---
#
# Produce Formal Artifacts, as GWT structure only. Generated from the markdown beside it, which holds the domain
# terms, the evidence and the examples. Each scenario is proven by the specs its story's evidence names.

from __future__ import annotations

from story_test import and_, given, scenario, story, then, when


with story("Generate Fidelity Artifact"):
    with scenario("Refuse a misspelt slug sent alone"):
        with given('the bookshop session works on Stories'):
            pass
        with when('Claude Code generates with guidance stories_story_map'):
            pass
        with then('the call is refused, saying no practice or fidelity has the slug stories_story_map'):
            pass
        with and_('the refusal lists stories-story-map among the slugs there are'):
            pass
    with scenario("Run prose once as text"):
        with given('the bookshop session works on Stories'):
            pass
        with when('Claude Code generates with guidance write the story map'):
            pass
        with then('the answer holds write the story map'):
            pass
    with scenario("Work on the practice a mapping names by its slug"):
        with given('the bookshop session works on Stories'):
            pass
        with when('Claude Code generates with the guidance mapping {toolset: stories, fidelity: story_map}'):
            pass
        with then('the answer holds the rules of stories-story-map'):
            pass
    with scenario("Refuse a mapping that names no toolset"):
        with given('the bookshop session works on Stories'):
            pass
        with when('Claude Code generates with the guidance mapping {foo: bar}'):
            pass
        with then('{foo: bar} is refused, saying a mapping names its practice in toolset'):
            pass
        with and_('the refusal lists stories-story-map among the slugs there are'):
            pass

with story("Render Artifact Into Another Format"):
    with scenario("Save another file's drawing under that file's own name"):
        with given(".context/story-map.drawio holds the story map's drawing, with Place Order moved by a person"):
            pass
        with and_('.context/returns.md holds another story map'):
            pass
        with when('Claude Code renders .context/returns.md to drawio at stories-story-map'):
            pass
        with then('the saved file is .context/returns.drawio, which draws Return Damaged Book'):
            pass
        with and_('.context/story-map.drawio is as the person left it'):
            pass
    with scenario("Refuse to render an empty file"):
        with given(".context/story-map.drawio holds the story map's drawing"):
            pass
        with and_('.context/empty.md holds nothing'):
            pass
        with when('Claude Code renders .context/empty.md to drawio at stories-story-map'):
            pass
        with then('the call is refused, naming .context/empty.md as empty'):
            pass
        with and_('.context/story-map.drawio is as it was'):
            pass
    with scenario("Refuse a path outside the session's root"):
        with given('../outside/story-map.md holds a story map in a folder beside the project'):
            pass
        with when('Claude Code renders ../outside/story-map.md to drawio at stories-story-map'):
            pass
        with then("../outside/story-map.md is refused as not under the session's root"):
            pass
        with and_('no drawing is saved beside ../outside/story-map.md'):
            pass
    with scenario("Read a file's format from its name when no source is named"):
        with given(".context/story-map.whiteboard holds the story map's whiteboard"):
            pass
        with when('Claude Code renders .context/story-map.whiteboard to drawio at stories-story-map, naming no source'):
            pass
        with then('the saved file is .context/story-map.drawio, which draws Place Order'):
            pass
