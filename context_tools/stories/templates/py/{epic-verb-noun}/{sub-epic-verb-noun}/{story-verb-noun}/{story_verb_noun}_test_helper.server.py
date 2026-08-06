# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: server - {EpicVerbNoun}Helper backed by the real HTTP route + test DB.
# Real: domain + repository + test DB. Stubbed: nothing.

"""Server tier test-helper for `{Story Name}`."""

from __future__ import annotations

from {story_verb_noun}_story import create_{story_verb_noun}_story


class ServerHelper:
    def given_precondition(self) -> None:
        raise NotImplementedError("not implemented: given_precondition")

    def when_action(self) -> None:
        raise NotImplementedError("not implemented: when_action")

    def then_outcome(self) -> None:
        raise NotImplementedError("not implemented: then_outcome")


globals().update(create_{story_verb_noun}_story(ServerHelper()))
