# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Scenario template — refer to context_tools/language-tools.md for tooling.
#
# ```
# epic:      {epic-verb-noun}
# sub_epic:  {sub-epic-verb-noun}
# story:     {story-verb-noun}
# file:      tests/{epic-verb-noun}/{sub-epic-verb-noun}/{story_verb_noun}.{tier}.py
# tier:      front-end | back-end | external-system
# ```
#
"""Story: {Story Verb-Noun}"""

from __future__ import annotations


def test_main_flow() -> None:
    """SCENARIO: {main-flow outcome}"""
    # Given {given step text}
    ...
    # When {when step text}
    ...
    # Then {then step text}
    ...
