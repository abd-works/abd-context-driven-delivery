"""A story tree rendered to code keeps every step body and setup it can, in every language, through one render."""

import ast
import sys
from pathlib import Path

from expects import be_true, contain, equal, expect, have_key
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[4]
for _path in (_REPO_ROOT, _REPO_ROOT / "tools", _REPO_ROOT / "cdd_guidance" / "practices"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import cdd_guidance.practices  # noqa: F401
from cdd_guidance.practices.stories.stories import Stories

_TS_PATH = "tests/onboard-a-customer/create-customer/create_customer.story.shared.ts"
_PY_PATH = "tests/onboard-a-customer/create-customer/create_customer_story.test.py"

_CUSTOMER_TYPESCRIPT = """\
/**
 * Sub-epic: Create Customer
 * Evidence: observed
 */

import { ctx, scenario, shareStory } from 'test-utils/story-test/story-test';
import { unverifiedCredentials } from '../../access-my-paradise/examples/credentials.examples';

let credentials: Credentials;

/**
 * Story: Create Customer
 * Actor: My Paradise
 * Evidence: observed
 */
shareStory('Create Customer', () => {
  scenario('Create Customer', ({ given, when, then }) => {
    let customerProfile: CustomerProfile;

    given('an unverified account', async () => {
      credentials = unverifiedCredentials(ctx.credentialsRepository);
      await credentials.register();
    });
    when('the User verifies their account with a valid token', async () => {
      customerProfile = await ctx.customerProfileRepository.create(credentials);
    });
    then('the system creates a new CustomerProfile', () => {
      expect(customerProfile.id).toBeTruthy();
    })
      .and('the CustomerProfile holds the account', async () => {
        expect(customerProfile.credentials.email).toBe(credentials.email);
      });
  });

  scenario('CustomerProfile already exists', ({ given, when, then }) => {
    let caughtError: unknown;

    given('an unverified account', async () => {
      credentials = unverifiedCredentials(ctx.credentialsRepository);
    }).and('a CustomerProfile already exists for that email', () => {
      seedCustomerProfileForEmail(ctx.customerProfileRepository, credentials);
    });
    when('the User verifies their account with a valid token', async () => {
      try {
        await ctx.customerProfileRepository.create(credentials);
      } catch (error) {
        caughtError = error;
      }
    });
    then('the CustomerProfile cannot be created', () => {
      expect(caughtError).toBeInstanceOf(CustomerProfileException);
    });
  });
});
"""

_CUSTOMER_MARKDOWN = """\
# Sub-epic: Create Customer

# Story: Create Customer

#### Scenario: Create Customer

*Given* an unverified account
*When* the User verifies their account with a valid token
*Then* the system creates a new CustomerProfile
*And* the CustomerProfile holds the account
*And* the CustomerProfile is shown on the profile page
"""

_CUSTOMER_PYTHON = '''\
from __future__ import annotations

from story_test import and_, given, scenario, story, then, when

# Epic: Create Customer

# Story: Create Customer
with story("Create Customer"):
    with scenario("Create Customer"):
        with given("an unverified account"):
            credentials = unverified_credentials()
        with when("the User verifies their account with a valid token"):
            profile = create_profile(credentials)
        with then("the system creates a new CustomerProfile"):
            expect(profile.id).to(be_true)
'''

_REGISTER = "await credentials.register();"


def _render(target: str, content, source: str, previous=None) -> dict:
    return Stories(fidelity="acceptance_tests").render(target, content, source=source, previous=previous)["content"]


with description("a story tree rendered to code"):
    with context("that was read from a typescript story file"):
        with context("that is rendered back to typescript"):
            with before.each:
                self.rendered = _render("typescript", {_TS_PATH: _CUSTOMER_TYPESCRIPT}, "typescript")

            with it("should write the file back to the path it was read from"):
                expect(self.rendered).to(have_key(_TS_PATH))

            with it("should write the file back as it was read"):
                expect(self.rendered[_TS_PATH]).to(equal(_CUSTOMER_TYPESCRIPT))

        with context("with one scenario renamed on the model"):
            with before.each:
                stories = Stories(fidelity="acceptance_tests")
                model = stories._to_object_model({_TS_PATH: _CUSTOMER_TYPESCRIPT}, "typescript")
                story = model.epics[0].epics[0].stories[0]
                story.scenarios[1].name = "CustomerProfile exists already"
                self.rendered = stories.render("typescript", model)["content"][_TS_PATH]

            with it("should write the other scenario as it was read"):
                expect(self.rendered).to(contain("    }).and('a CustomerProfile already exists for that email', () => {") | contain(
                    "  scenario('Create Customer', ({ given, when, then }) => {\n    let customerProfile: CustomerProfile;"
                ))

            with it("should keep the renamed scenario's step bodies"):
                expect(self.rendered).to(contain("        caughtError = error;"))

            with it("should write the renamed scenario under its new name"):
                expect(self.rendered).to(contain("scenario('CustomerProfile exists already'"))

        with context("that is rendered to python"):
            with before.each:
                self.rendered = "".join(_render("python", {_TS_PATH: _CUSTOMER_TYPESCRIPT}, "typescript").values())

            with it("should carry each typescript step body commented out inside its step"):
                expect(self.rendered).to(contain(f"# {_REGISTER}"))

            with it("should be python that parses"):
                ast.parse(self.rendered)
                expect(True).to(be_true)

    with context("that was read from a javascript story file"):
        with context("that is rendered back to javascript"):
            with it("should write the file back as it was read"):
                path = "tests/onboard-a-customer/create-customer/create_customer_story.test.js"
                javascript = _CUSTOMER_TYPESCRIPT.replace("let credentials: Credentials;", "let credentials;").replace(
                    "    let customerProfile: CustomerProfile;", "    let customerProfile;"
                ).replace("    let caughtError: unknown;", "    let caughtError;").replace("shareStory", "story")
                expect(_render("javascript", {path: javascript}, "javascript")[path]).to(equal(javascript))

    with context("that was read from a python story file"):
        with context("that is rendered back to python"):
            with it("should write the file back as it was read"):
                expect(_render("python", {_PY_PATH: _CUSTOMER_PYTHON}, "python")[_PY_PATH]).to(equal(_CUSTOMER_PYTHON))

    with context("that was read from scenarios markdown"):
        with context("that is rendered to typescript with the previous typescript files"):
            with before.each:
                previous = {_TS_PATH: _CUSTOMER_TYPESCRIPT}
                self.rendered = _render("typescript", _CUSTOMER_MARKDOWN, "markdown", previous=previous)
                self.file = self.rendered.get(_TS_PATH, "")

            with it("should write to the previous file's path"):
                expect(self.rendered).to(have_key(_TS_PATH))

            with it("should keep the previous file's body for a step the markdown still has"):
                expect(self.file).to(contain(f"      {_REGISTER}"))

            with it("should keep the previous file's imports"):
                expect(self.file).to(contain("import { ctx, scenario, shareStory } from 'test-utils/story-test/story-test';"))

            with it("should mark a step new to the markdown as still to write"):
                expect(self.file).to(contain(".and('the CustomerProfile is shown on the profile page', () => {\n        // TODO: implement step"))
