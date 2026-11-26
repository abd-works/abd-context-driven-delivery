# ---
# fidelity: [specification]
# artifact: [story-scenarios]
# format: py
# ---
#
# Generate Fidelity Artifacts, as GWT structure only. Generated from the markdown beside it, which holds the domain
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
