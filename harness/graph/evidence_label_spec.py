"""A story with assertions is observed. An unlabeled placeholder must say the label is missing."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import description, it

from practices.stories.rules.story_map import EvidenceDistinguishesObservedInferredAndIntended


class _Story:
    def __init__(self, name: str, evidence: list[str] | None = None) -> None:
        self.type = "Story"
        self.name = name
        self.data = {"evidence": evidence or []}


class _Context:
    def __init__(self, text: str) -> None:
        self._text = text

    def span(self, node) -> str:
        return self._text


def _check(name: str, text: str, evidence: list[str] | None = None) -> list[str]:
    return EvidenceDistinguishesObservedInferredAndIntended().check(
        _Story(name, evidence),
        _Context(text),
    )


_ENTER_VALIDATION = """
shareStory('Enter Validation Code', () => {
  scenario('Enter validation code', ({ given, when, then }) => {
    then('the account is verified', () => {
      expect(accountCredentials.verified).toBe(true);
    });
  });
});
"""

_PLACEHOLDER = """
shareStory('Handle Request', () => {
  scenario('Accept the request', ({ when, then }) => {
    when('the system handles the request', () => undefined);
    then('the request is accepted', () => undefined);
  });
});
"""


with description("evidence-distinguishes-observed-inferred-and-intended"):
    with it("should accept a story whose scenarios assert the behaviour"):
        expect(_check("Enter Validation Code", _ENTER_VALIDATION)).to(equal([]))

    with it("should accept a story labeled observed"):
        expect(_check("Submit Order", "shareStory('Submit Order', () => {});", ["observed"])).to(equal([]))

    with it("should name a placeholder story that has no evidence label"):
        expect(_check("Handle Request", _PLACEHOLDER)).to(equal([
            "story 'Handle Request' has no evidence label. Mark it observed, inferred, or intended."
        ]))

    with it("should name an evidence label that is not observed, inferred, or intended"):
        expect(_check("Enter Validation Code", _ENTER_VALIDATION, ["workshop notes"])).to(equal([
            "story 'Enter Validation Code': evidence 'workshop notes' must be observed, inferred, or intended."
        ]))
