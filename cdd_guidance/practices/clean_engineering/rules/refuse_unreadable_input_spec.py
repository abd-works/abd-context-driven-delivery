"""refuse-unreadable-input: a read that catches a parse or decode failure and answers an empty value is reported,
because the caller reads the empty value as nothing there and writes over what could not be read. Exploratory testing,
shortcoming 2: a file read as empty and then written over (`JsonFile.read`, the prompt queue, the record of test runs)."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.rules import BY_SLUG
from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_source, python_example_pair, rule_pair

_SLUG = "refuse-unreadable-input"
_HEAD = "import json\nfrom pathlib import Path\n\n\nclass Settings:\n    def __init__(self, path: Path) -> None:\n        self._path = path\n\n"
_READ_AS_EMPTY = _HEAD + (
    "    def read(self) -> dict:\n        try:\n            return json.loads(self._path.read_text())\n"
    "        except json.JSONDecodeError:\n            return {}\n"
)
_REFUSED_BY_NAME = _HEAD + (
    "    def read(self) -> dict:\n        try:\n            return json.loads(self._path.read_text())\n"
    "        except json.JSONDecodeError as unreadable:\n            raise UnreadableSettings(self._path) from unreadable\n"
)
_MISSING_FILE_IS_EMPTY = _HEAD + (
    "    def read(self) -> dict:\n        try:\n            return json.loads(self._path.read_text())\n"
    "        except FileNotFoundError:\n            return {}\n"
)
_ANY_VALUE_ERROR_AFTER_A_PARSE = _HEAD + (
    "    def read(self) -> dict:\n        try:\n            held = json.loads(self._path.read_text())\n"
    "        except (OSError, ValueError):\n            held = {}\n        return held\n"
)
_NUMBER_WITH_A_DEFAULT = "class Port:\n    def of(self, written: str) -> int:\n        try:\n            return int(written)\n        except ValueError:\n            return 0\n"
_UNDECODABLE_TEXT = (
    "from pathlib import Path\n\n\nclass Note:\n    def text(self, path: Path) -> str:\n        try:\n            return path.read_text(encoding='utf-8')\n"
    "        except UnicodeDecodeError:\n            return ''\n"
)
# A code reader: source that does not parse is skipped, and source-parses reports the file.
_SKIPS_UNPARSABLE_SOURCE = (
    "import ast\n\n\nclass Classes:\n    def named_in(self, source: str) -> list:\n        try:\n            tree = ast.parse(source)\n"
    "        except SyntaxError:\n            return []\n        return [node.name for node in tree.body]\n"
)
_PARSES_SOURCE_IN_A_WIDE_CATCH = (
    "import ast\n\n\nclass Classes:\n    def named_in(self, source: str) -> list:\n        try:\n            tree = ast.parse(source)\n"
    "        except ValueError:\n            return []\n        return [node.name for node in tree.body]\n"
)
_TYPESCRIPT_READ_AS_EMPTY = (
    "export class Settings {\n  read(text: string): Record<string, string> {\n    try {\n      return JSON.parse(text);\n"
    "    } catch (unreadable) {\n      return {};\n    }\n  }\n}\n"
)
_TYPESCRIPT_REFUSED = (
    "export class Settings {\n  read(text: string): Record<string, string> {\n    try {\n      return JSON.parse(text);\n"
    "    } catch (unreadable) {\n      throw new UnreadableSettings(text);\n    }\n  }\n}\n"
)


def _hits(source: str, lang: str = "python") -> list[str]:
    return practice_from_source(source, lang=lang).hits(BY_SLUG[_SLUG])


with description("a read that cannot parse what it was given") as self:
    with context("that catches the parse failure and answers an empty value"):
        with before.all:
            self.pair = rule_pair(_SLUG, _READ_AS_EMPTY, _REFUSED_BY_NAME)
            self.hits = _hits(_READ_AS_EMPTY)

        with it("should be reported, and pass once it refuses with a failure that names the file"):
            self.pair.check()

        with it("should be told to refuse by naming the file or record, and why"):
            expect(self.hits).to(equal([
                "Operation 'read' catches JSONDecodeError, a failure to parse or decode what it read, and answers an empty value. "
                "Raise a failure that names the file or record instead: a caller reads the empty value as nothing there and writes over what could not be read."
            ]))

    with context("that catches any value failure after a parse and carries on with an empty value"):
        with it("should be reported"):
            expect(len(_hits(_ANY_VALUE_ERROR_AFTER_A_PARSE))).to(equal(1))

    with context("that catches text it cannot decode and answers an empty text"):
        with it("should be reported"):
            expect(len(_hits(_UNDECODABLE_TEXT))).to(equal(1))

    with context("written in TypeScript, around JSON.parse"):
        with it("should be reported, and pass once it throws a named failure"):
            rule_pair(_SLUG, _TYPESCRIPT_READ_AS_EMPTY, _TYPESCRIPT_REFUSED, lang="typescript").check()

    with context("as the rule's guidance shows it, in its failing and its repaired example"):
        with it("should be reported in the failing example and pass in the repaired one"):
            python_example_pair(_SLUG).check()


with description("a read of something that is not there") as self:
    with context("that answers an empty value for a missing file"):
        with it("should pass, since nothing there is an empty result"):
            expect(_hits(_MISSING_FILE_IS_EMPTY)).to(equal([]))

    with context("that reads source code and skips a file it cannot parse"):
        with it("should pass, since source that does not parse is reported by source-parses, not saved over"):
            expect(_hits(_SKIPS_UNPARSABLE_SOURCE)).to(equal([]))

    with context("that reads source code with ast.parse inside a wide catch"):
        with it("should pass, since only a JSON read or a decode is a read of stored data"):
            expect(_hits(_PARSES_SOURCE_IN_A_WIDE_CATCH)).to(equal([]))

    with context("that answers a default for a number that does not parse, with no file or record read"):
        with it("should pass, since no stored thing is read as empty"):
            expect(_hits(_NUMBER_WITH_A_DEFAULT)).to(equal([]))
