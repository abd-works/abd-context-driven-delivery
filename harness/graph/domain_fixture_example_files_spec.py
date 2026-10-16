"""domain-fixture-example-files checks fixture files. A story file is not one."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import description, it

from practices.stories.rules.acceptance_tests import DomainFixtureExampleFiles


class _Source:
    def __init__(self, file: str) -> None:
        self.file = file


class _Example:
    type = "Example"
    name = "resentValidationCodeHelperMessage"

    def __init__(self, file: str) -> None:
        self.source = _Source(file)


def _check(file: str) -> list[str]:
    return DomainFixtureExampleFiles().check(_Example(file), None)


with description("domain-fixture-example-files"):
    with it("should accept an example used from a story shared file"):
        expect(
            _check("tests/onboard-a-customer/authenticate-user/authenticate_user.story.shared.ts")
        ).to(equal([]))

    with it("should accept an example used from a story file"):
        expect(_check("tests/onboard-a-customer/authenticate-user/authenticate_user_story.ts")).to(equal([]))

    with it("should accept a fixture named .examples.ts under examples"):
        expect(
            _check("tests/onboard-a-customer/authenticate-user/examples/validation-code.examples.ts")
        ).to(equal([]))

    with it("should flag a file in examples that does not end with .examples.ts"):
        expect(_check("tests/onboard-a-customer/authenticate-user/examples/shared-customers.ts")).to(equal([
            "Example file 'shared-customers.ts' should end with .examples.ts under an examples/ folder."
        ]))

    with it("should leave a file outside examples alone"):
        expect(_check("tests/onboard-a-customer/authenticate-user/shared-customers.ts")).to(equal([]))
