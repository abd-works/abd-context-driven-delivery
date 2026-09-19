"""Test domain value objects: Tier, Language, TestSuite, TestCase, Test.

These are plain value objects - they are NEVER translated across formats.
They are populated by the workspace loader and copied through `update_self`
as value lists on SubEpic and Story. No `StoryNode` subclassing here.

Discovery rules (applied by the loader):
- `Tier` is discovered from the file-name tier segment
  (e.g. `submit-order-server.test.ts` -> Tier("server")).
- `Language` is discovered from the file extension
  (e.g. `.ts`, `.tsx` -> Language("ts"); `.py` -> Language("py")).
- A test file with no matching `*-stories.<ext>` sibling in the same language
  -> loader error.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .source_location import SourceLocation


@dataclass(frozen=True)
class Tier:
    """Project-specific test tier discovered at load time from the file-name segment.

    Examples: Tier("server"), Tier("client"), Tier("e2e"), Tier("domain").
    """

    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Language:
    """Project-specific test language discovered at load time from the file extension.

    Language is a **tag only** - it is never a transformation axis. The Python
    loader reads `_stories.py`; the TypeScript loader reads `-stories.ts`.

    Examples: Language("ts"), Language("tsx"), Language("py"), Language("js"),
              Language("java").
    """

    name: str

    def __str__(self) -> str:
        return self.name


@dataclass
class Test:
    """One scenario exercised by a TestCase.

    - `scenario_source` - SourceLocation pointing at the Scenario key in the
      sibling `*-stories.<ext>` file (same language as its TestSuite).
    """

    scenario_source: Optional[SourceLocation] = None


@dataclass
class TestCase:
    """One test case (one `it(...)` / `test_...` / `@Test` method) inside a suite.

    - `tier` - inherited from the containing TestSuite
    - `name` - the string label passed to the test framework
    - `tests` - the Scenario-level Tests exercised by this case
    - `assertions_count` - number of expect/assert calls in the body
    - `has_real_assertion` - true if body has any expect/assert (not just mocks)
    - `references_bug_id` - bug id from a comment / docstring; empty if none
    - `story_source` - SourceLocation pointing at the Story constant in the
      sibling `*-stories.<ext>` file (same language as its TestSuite)
    """

    tier: Tier = field(default_factory=lambda: Tier(""))
    name: str = ""
    tests: List[Test] = field(default_factory=list)
    assertions_count: int = 0
    has_real_assertion: bool = False
    has_unimplemented_body: bool = False
    references_bug_id: str = ""
    story_source: Optional[SourceLocation] = None
    # Scenario display name this case covers when the channel can resolve it.
    covers_scenario: str = ""


@dataclass
class TestSuite:
    """One test suite - one per (Tier, Language) pair on a SubEpic.

    - `tier` - discovered from the file-name segment
    - `language` - discovered from the file extension
    - `name` - the describe / class name at the outer scope
    - `cases` - the TestCase entries inside this suite
    - `imports_real` - true if the file imports the real implementation
    - `source` - SourceLocation pointing at the backing test file
    - `unimplemented_steps` - step keys still stubbed (filled by the language channel)
    """

    tier: Tier = field(default_factory=lambda: Tier(""))
    language: Language = field(default_factory=lambda: Language(""))
    name: str = ""
    cases: List[TestCase] = field(default_factory=list)
    imports_real: bool = True
    source: Optional[SourceLocation] = None
    unimplemented_steps: List[str] = field(default_factory=list)


# -- Shared utility -------------------------------------------------------------

import re as _re
_BUG_ID_RE = _re.compile(r"(?:BUG|BUG-|issue\s*)([A-Z]+-\d+|\d+)", _re.IGNORECASE)


def extract_bug_id(text: str) -> str:
    """Extract the first bug/issue reference from a text snippet; empty if none."""
    m = _BUG_ID_RE.search(text)
    return m.group(1) if m else ""
