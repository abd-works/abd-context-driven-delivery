"""BDD for work session guidance — behavior fidelity."""

import os
import subprocess
import tempfile
from pathlib import Path

from expects import be_none, contain, equal, expect
from mamba import after, before, context, description, it

from workspace.workspace import Example, WorkSession, WorkSessionRule

_SLUG = "put-logic-on-the-owning-resource"
_BODY = (
    "Put logic on the object that owns the invariant. Do not infer ownership "
    "from a route name, Story actor, or Given subject."
)
_MISTAKE = (
    "client.validateLastTransactionForPrimaryAccount() put the check on the client"
)
_CORRECTION = (
    "client.accounts[id].transactions.last.validate() keeps the check on the transaction"
)
_CODE_RULE = f"""\
#### Rules

- `{_SLUG}` - {_BODY}
  star: 2
  guidance: clean_engineering
  fidelity: code
  last-fail: 1
  mistake: parked the check on the client
  correction: call validate on the transaction
"""
_OTHER_RULE = """\
#### Rules

- `hide-inner-details` - Expose behavior through named operations.
  star: 1
  guidance: clean_engineering
  fidelity: code
"""
_PRACTICE_WIDE = f"""\
#### Rules

- `{_SLUG}` - {_BODY}
  star: 3
  guidance: clean_engineering
  last-fail: 1
  mistake: {_MISTAKE}
  correction: {_CORRECTION}
"""
_GLOBAL = f"""\
#### Rules

- `{_SLUG}` - {_BODY}
  star: 4
  last-fail: 1
  mistake: {_MISTAKE}
  correction: {_CORRECTION}
"""
_GLOBAL_AHEAD = f"""\
#### Rules

- `{_SLUG}` - {_BODY}
  star: 5
  last-fail: 1
  mistake: {_MISTAKE}
  correction: {_CORRECTION}

- `hide-inner-details` - Expose behavior through named operations.
  star: 2
  guidance: clean_engineering
  fidelity: code
  last-fail: 1
"""
_FAILED_ONE_EARLIER = f"""\
#### Rules

- `{_SLUG}` - {_BODY}
  star: 2
  guidance: clean_engineering
  fidelity: code
  last-fail: 2
  mistake: {_MISTAKE}
  correction: {_CORRECTION}
"""
_FAILED_IN_CONTEXT = f"""\
#### Rules

- `{_SLUG}` - {_BODY}
  star: 2
  guidance: clean_engineering
  fidelity: code
  last-fail: 3
  mistake: {_MISTAKE}
  correction: {_CORRECTION}
"""
_FAILED_FIVE_AGO = f"""\
#### Rules

- `{_SLUG}` - {_BODY}
  star: 2
  guidance: clean_engineering
  fidelity: code
  last-fail: 5
  mistake: {_MISTAKE}
  correction: {_CORRECTION}
"""
_INJECT = {"guidance": "clean_engineering", "fidelity": "code"}
_OTHER_FIDELITY = {"guidance": "clean_engineering", "fidelity": "model"}
_PRACTICE_BODY = "practice body of put-logic-on-the-owning-resource"
_OTHER_INJECTED = "Expose behavior through named operations."
_INJECTED_MARKDOWN = f"""\
- `{_SLUG}` - {_PRACTICE_BODY}
- `hide-inner-details` - {_OTHER_INJECTED}
"""
_INJECT_MERGED = {
    "guidance": "clean_engineering",
    "fidelity": "code",
    "additional_context": _INJECTED_MARKDOWN,
}


def _incoming(**fields: object) -> WorkSessionRule:
    values = {
        "slug": _SLUG,
        "body": _BODY,
        "guidance": "clean_engineering",
        "fidelity": "code",
        "examples": [Example(mistake=_MISTAKE, correction=_CORRECTION)],
    }
    values.update(fields)
    return WorkSessionRule(**values)


def _load(
    name: str,
    guidelines_path: Path,
    markdown: str,
) -> WorkSession:
    guidelines_path.parent.mkdir(parents=True, exist_ok=True)
    guidelines_path.write_text(markdown, encoding="utf-8")
    return WorkSession(name=name)


def _from_file(name: str):
    return WorkSession(name=name).guidance.rules


def _init_repository(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "work-session@test"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "work-session"],
        cwd=root,
        check=True,
        capture_output=True,
    )


with description("a work session"):
    with context("that is open"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self._cwd = Path.cwd()
            self.repo_root = Path(self.tmp.name)
            _init_repository(self.repo_root)
            os.chdir(self.repo_root)
            self.session_name = "work-session"
            self.session_folder = self.repo_root / ".sessions" / self.session_name
            self.guidelines_path = self.session_folder / "work-guidelines.md"

        with after.each:
            os.chdir(self._cwd)
            self.tmp.cleanup()

        with context("that has generated output with clean engineering model"):
            with context("that has a correction for put-logic-on-the-owning-resource"):
                with context("with a matching work session rule"):
                    with before.each:
                        self.work_session = _load(
                            self.session_name,
                            self.guidelines_path,
                            _CODE_RULE,
                        )
                        self.rules = self.work_session.guidance.rules

                    with it("should add the mistake to that work session rule"):
                        matching = self.rules._matching_work_session_rule(_incoming())
                        self.rules.add(_incoming())
                        rule = _from_file(self.session_name)[_SLUG]
                        expect(matching.slug).to(equal(_SLUG))
                        expect(rule.examples[0].mistake).to(
                            equal("parked the check on the client")
                        )
                        expect(rule.examples[0].correction).to(
                            equal("call validate on the transaction")
                        )
                        expect(rule.examples[-1].mistake).to(equal(_MISTAKE))
                        expect(rule.examples[-1].correction).to(equal(_CORRECTION))
                        expect(len(rule.examples)).to(equal(2))
                        text = self.guidelines_path.read_text(encoding="utf-8")
                        expect(text).to(contain("parked the check on the client"))
                        expect(text).to(contain(_MISTAKE))
                        expect(text).to(contain(_CORRECTION))

                    with it("should raise that rule's star"):
                        star = _from_file(self.session_name)[_SLUG].star
                        matching = self.rules._matching_work_session_rule(_incoming())
                        self.rules.add(_incoming())
                        rule = _from_file(self.session_name)[_SLUG]
                        expect(matching.slug).to(equal(_SLUG))
                        expect(rule.star).to(equal(star + 1))

                with context("with no matching work session rule and a matching practice rule"):
                    with before.each:
                        self.work_session = _load(
                            self.session_name,
                            self.guidelines_path,
                            _OTHER_RULE,
                        )
                        self.rules = self.work_session.guidance.rules

                    with it("should add a new work session rule tagged clean_engineering and code"):
                        matching = self.rules._matching_work_session_rule(_incoming())
                        practice_rule = self.rules._matching_practice_rule(_incoming())
                        self.rules.add(_incoming())
                        rule = _from_file(self.session_name)[_SLUG]
                        expect(matching).to(be_none)
                        expect(practice_rule.slug).to(equal(_SLUG))
                        expect(rule.guidance).to(equal("clean_engineering"))
                        expect(rule.fidelity).to(equal("code"))

                    with it("should have the same name as the matching practice rule"):
                        practice_rule = self.rules._matching_practice_rule(_incoming())
                        self.rules.add(_incoming())
                        rule = _from_file(self.session_name)[_SLUG]
                        expect(rule.slug).to(equal(practice_rule.slug))
                        expect(rule.slug).to(equal(_SLUG))

                    with it("should attach the mistake and the correction"):
                        self.rules.add(_incoming())
                        rule = _from_file(self.session_name)[_SLUG]
                        expect(rule.examples[-1].mistake).to(equal(_MISTAKE))
                        expect(rule.examples[-1].correction).to(equal(_CORRECTION))

                    with it("should add a star"):
                        self.rules.add(_incoming())
                        rule = _from_file(self.session_name)[_SLUG]
                        expect(rule.star).to(equal(1))

                with context("with a matching practice rule that is shared across fidelities"):
                    with before.each:
                        self.work_session = _load(
                            self.session_name,
                            self.guidelines_path,
                            _OTHER_RULE,
                        )
                        self.rules = self.work_session.guidance.rules

                    with it("should add the new work session rule for clean engineering with no fidelity tag"):
                        incoming = _incoming(fidelity=None)
                        matching = self.rules._matching_work_session_rule(incoming)
                        practice_rule = self.rules._matching_practice_rule(incoming)
                        self.rules.add(incoming)
                        rule = _from_file(self.session_name)[_SLUG]
                        expect(matching).to(be_none)
                        expect(practice_rule.slug).to(equal(_SLUG))
                        expect(rule.guidance).to(equal("clean_engineering"))
                        expect(rule.fidelity).to(be_none)

                    with it("should attach the mistake and the correction"):
                        self.rules.add(_incoming(fidelity=None))
                        rule = _from_file(self.session_name)[_SLUG]
                        expect(rule.examples[-1].mistake).to(equal(_MISTAKE))
                        expect(rule.examples[-1].correction).to(equal(_CORRECTION))

                    with it("should add a star"):
                        self.rules.add(_incoming(fidelity=None))
                        rule = _from_file(self.session_name)[_SLUG]
                        expect(rule.star).to(equal(1))

                with context("with no matching guideline and no matching fidelity"):
                    with context("that belongs to a guideline and a fidelity"):
                        with before.each:
                            self.work_session = _load(
                                self.session_name,
                                self.guidelines_path,
                                _OTHER_RULE,
                            )
                            self.rules = self.work_session.guidance.rules

                        with it("should create and then add a new work session rule and assign the correct guideline and fidelity"):
                            incoming = _incoming(
                                slug="session-only-cart-owner-check",
                                body="Keep cart owner checks on the cart.",
                            )
                            matching = self.rules._matching_work_session_rule(incoming)
                            practice_rule = self.rules._matching_practice_rule(incoming)
                            self.rules.add(incoming)
                            rule = _from_file(self.session_name)[
                                "session-only-cart-owner-check"
                            ]
                            expect(matching).to(be_none)
                            expect(practice_rule).to(be_none)
                            expect(rule.guidance).to(equal("clean_engineering"))
                            expect(rule.fidelity).to(equal("code"))
                            expect(rule.examples[-1].mistake).to(equal(_MISTAKE))
                            expect(rule.examples[-1].correction).to(equal(_CORRECTION))

                    with context("that does not belong to a guideline and a fidelity"):
                        with before.each:
                            self.work_session = _load(
                                self.session_name,
                                self.guidelines_path,
                                _OTHER_RULE,
                            )
                            self.rules = self.work_session.guidance.rules

                        with it("should create and then add a new work session rule and assign no guideline or fidelity"):
                            incoming = _incoming(
                                slug="session-wide-owner-check",
                                body="Keep owner checks on the owner.",
                                guidance=None,
                                fidelity=None,
                            )
                            matching = self.rules._matching_work_session_rule(incoming)
                            practice_rule = self.rules._matching_practice_rule(incoming)
                            self.rules.add(incoming)
                            rule = _from_file(self.session_name)[
                                "session-wide-owner-check"
                            ]
                            expect(matching).to(be_none)
                            expect(practice_rule).to(be_none)
                            expect(rule.guidance).to(be_none)
                            expect(rule.fidelity).to(be_none)
                            expect(rule.examples[-1].mistake).to(equal(_MISTAKE))

                with context("with that rule having established priority from previous runs"):
                    with before.each:
                        self.work_session = _load(
                            self.session_name,
                            self.guidelines_path,
                            _CODE_RULE,
                        )
                        self.rules = self.work_session.guidance.rules

                    with it("should increase its priority by one"):
                        star = _from_file(self.session_name)[_SLUG].star
                        matching = self.rules._matching_work_session_rule(_incoming())
                        self.rules.add(_incoming())
                        rule = _from_file(self.session_name)[_SLUG]
                        expect(matching.slug).to(equal(_SLUG))
                        expect(rule.star).to(equal(star + 1))

                    with it("should place the rule in the top rules section according to its new priority"):
                        self.rules.add(_incoming())
                        first = self.guidelines_path.read_text(encoding="utf-8").splitlines()[2]
                        expect(first).to(contain(f"`{_SLUG}`"))

        with context("that has announced a new turn"):
            with before.each:
                self.work_session = _load(
                    self.session_name,
                    self.guidelines_path,
                    _CODE_RULE,
                )
                self.rules = self.work_session.guidance.rules

            with it("should announce a new turn"):
                turn = self.work_session.turn()
                expect(turn.work_session).to(equal(self.work_session))
                expect(turn.change_commit.sha).not_to(equal(""))
                expect(self.work_session.completed_turns[-1]).to(
                    equal(turn.change_commit.sha)
                )

            with context("that is generating with clean engineering code"):
                with context("with practice rules being injected for clean engineering code"):
                    with it("should match work session rules for shared practice and fidelity practice rules first in the injected set"):
                        matching = self.rules._matching_rules(_INJECT)
                        expect([rule.slug for rule in matching]).to(contain(_SLUG))

                    with it("should keep put-logic-on-the-owning-resource at the established priority"):
                        star = _from_file(self.session_name)[_SLUG].star
                        self.rules.inject_rules(_INJECT)
                        expect(_from_file(self.session_name)[_SLUG].star).to(equal(star))

                    with it("should overwrite the injected rule of the same name"):
                        result = self.rules.inject_rules(_INJECT_MERGED)
                        text = result.get("additional_context") or ""
                        expect(text).to(contain(_BODY))
                        expect(text).to(contain("parked the check on the client"))
                        expect(text).to(contain("call validate on the transaction"))
                        expect(text).not_to(contain(_PRACTICE_BODY))

                    with it("should put remaining injected rules at the bottom"):
                        result = self.rules.inject_rules(_INJECT_MERGED)
                        text = result.get("additional_context") or ""
                        overwritten = text.find(_BODY)
                        remaining = text.find(_OTHER_INJECTED)
                        expect(overwritten).not_to(equal(-1))
                        expect(remaining).not_to(equal(-1))
                        expect(overwritten < remaining).to(equal(True))

                    with it("should write last-chat-injected-rules with the injected additional context"):
                        result = self.rules.inject_rules(_INJECT_MERGED)
                        text = result.get("additional_context") or ""
                        dumped = (
                            self.session_folder / "last-chat-injected-rules.md"
                        ).read_text(encoding="utf-8")
                        expect(dumped.strip()).to(equal(text.strip()))

                    with context("with a practice-wide work session rule"):
                        with before.each:
                            self.work_session = _load(
                                self.session_name,
                                self.guidelines_path,
                                _PRACTICE_WIDE,
                            )
                            self.rules = self.work_session.guidance.rules

                        with it("should inject that rule in the same star order as fidelity-specific rules"):
                            matching = self.rules._matching_rules(_INJECT)
                            expect([rule.slug for rule in matching]).to(contain(_SLUG))

                    with context("with a global work session rule"):
                        with before.each:
                            self.work_session = _load(
                                self.session_name,
                                self.guidelines_path,
                                _GLOBAL,
                            )
                            self.rules = self.work_session.guidance.rules

                        with it("should inject that rule in the same star order as fidelity-specific rules"):
                            matching = self.rules._matching_rules(_INJECT)
                            expect([rule.slug for rule in matching]).to(contain(_SLUG))

                    with context("with a global rule that has more stars than a fidelity-specific rule"):
                        with before.each:
                            self.work_session = _load(
                                self.session_name,
                                self.guidelines_path,
                                _GLOBAL_AHEAD,
                            )
                            self.rules = self.work_session.guidance.rules

                        with it("should place the global rule first"):
                            matching = self.rules._matching_rules(_INJECT)
                            expect(matching[0].slug).to(equal(_SLUG))

                with context("with practice rules being injected for a different fidelity"):
                    with it("should leave the clean_engineering code work session rules out of that reorder"):
                        matching = self.rules._matching_rules(_OTHER_FIDELITY)
                        expect([rule.slug for rule in matching]).not_to(contain(_SLUG))

                    with context("with a practice-wide work session rule"):
                        with before.each:
                            self.work_session = _load(
                                self.session_name,
                                self.guidelines_path,
                                _PRACTICE_WIDE,
                            )
                            self.rules = self.work_session.guidance.rules

                        with it("should still inject practice-wide clean_engineering rules"):
                            matching = self.rules._matching_rules(_OTHER_FIDELITY)
                            expect([rule.slug for rule in matching]).to(contain(_SLUG))

                    with context("with a global work session rule"):
                        with before.each:
                            self.work_session = _load(
                                self.session_name,
                                self.guidelines_path,
                                _GLOBAL,
                            )
                            self.rules = self.work_session.guidance.rules

                        with it("should still inject global rules"):
                            matching = self.rules._matching_rules(_OTHER_FIDELITY)
                            expect([rule.slug for rule in matching]).to(contain(_SLUG))

                with context("with priority inclusion set to 1"):
                    with context("with priority injection detail set to examples"):
                        with context("with a rule that failed last turn"):
                            with before.each:
                                self.work_session = _load(
                                    self.session_name,
                                    self.guidelines_path,
                                    _CODE_RULE,
                                )
                                self.rules = self.work_session.guidance.rules
                                self.rules.priority_inclusion = 1
                                self.rules.priority_detail = "examples"

                            with it("should treat that rule as priority"):
                                rule = _from_file(self.session_name)[_SLUG]
                                expect(self.rules._band(rule)).to(equal("priority"))

                            with context("with a new generation turn that matches the failed rule"):
                                with it("should inject the full rule plus mistake and correction examples"):
                                    rule = _from_file(self.session_name)[_SLUG]
                                    rendered = self.rules._render(
                                        rule, self.rules.priority_detail
                                    )
                                    expect(self.rules._band(rule)).to(equal("priority"))
                                    expect(rendered).to(contain(_BODY))
                                    expect(rendered).to(
                                        contain("parked the check on the client")
                                    )
                                    expect(rendered).to(
                                        contain("call validate on the transaction")
                                    )

                with context("with relevant inclusion set to 2"):
                    with context("with relevant injection detail set to examples"):
                        with context("with a rule that failed one turn earlier"):
                            with before.each:
                                self.work_session = _load(
                                    self.session_name,
                                    self.guidelines_path,
                                    _FAILED_ONE_EARLIER,
                                )
                                self.rules = self.work_session.guidance.rules
                                self.rules.relevant_inclusion = 2
                                self.rules.relevant_detail = "examples"

                            with it("should treat that rule as relevant"):
                                rule = _from_file(self.session_name)[_SLUG]
                                expect(self.rules._band(rule)).to(equal("relevant"))

                            with it("should inject the full rule plus mistake and correction examples"):
                                rule = _from_file(self.session_name)[_SLUG]
                                rendered = self.rules._render(
                                    rule, self.rules.relevant_detail
                                )
                                expect(rendered).to(contain(_MISTAKE))
                                expect(rendered).to(contain(_CORRECTION))

                with context("with context inclusion set to 3"):
                    with context("with context injection detail set to slug"):
                        with context("with exclude set to 5"):
                            with context("with a rule that failed previous turns inside the context window"):
                                with before.each:
                                    self.work_session = _load(
                                        self.session_name,
                                        self.guidelines_path,
                                        _FAILED_IN_CONTEXT,
                                    )
                                    self.rules = self.work_session.guidance.rules
                                    self.rules.context_inclusion = 3
                                    self.rules.context_detail = "slug"
                                    self.rules.exclude = 5

                                with it("should treat that rule as context"):
                                    rule = _from_file(self.session_name)[_SLUG]
                                    expect(self.rules._band(rule)).to(equal("context"))

                                with it("should inject only the rule slug and its star"):
                                    rule = _from_file(self.session_name)[_SLUG]
                                    rendered = self.rules._render(
                                        rule, self.rules.context_detail
                                    )
                                    expect(rendered).to(contain(_SLUG))
                                    expect(rendered).to(contain(f"★{rule.star}"))

                            with context("with a rule that failed five turns ago"):
                                with before.each:
                                    self.work_session = _load(
                                        self.session_name,
                                        self.guidelines_path,
                                        _FAILED_FIVE_AGO,
                                    )
                                    self.rules = self.work_session.guidance.rules
                                    self.rules.exclude = 5

                                with it("should leave that rule out of the prompt"):
                                    matching = self.rules._matching_rules(_INJECT)
                                    expect([rule.slug for rule in matching]).not_to(
                                        contain(_SLUG)
                                    )

                                with it("should keep that rule on the collection"):
                                    expect(_from_file(self.session_name)[_SLUG].slug).to(
                                        equal(_SLUG)
                                    )
                                    expect(
                                        self.guidelines_path.read_text(encoding="utf-8")
                                    ).to(contain(_SLUG))

                with context("that has changed relevant inclusion to 1"):
                    with context("with a rule that failed one turn earlier"):
                        with before.each:
                            self.work_session = _load(
                                self.session_name,
                                self.guidelines_path,
                                _FAILED_ONE_EARLIER,
                            )
                            self.rules = self.work_session.guidance.rules
                            self.rules.relevant_inclusion = 1
                            self.rules.context_inclusion = 3
                            self.rules.context_detail = "slug"

                        with it("should treat that rule as context"):
                            rule = _from_file(self.session_name)[_SLUG]
                            expect(self.rules._band(rule)).to(equal("context"))
                            rendered = self.rules._render(
                                rule, self.rules.context_detail
                            )
                            expect(rendered).to(contain(_SLUG))
                            expect(rendered).to(contain(f"★{rule.star}"))

                with context("that has changed priority injection detail to slug"):
                    with context("with a rule that failed last turn"):
                        with before.each:
                            self.work_session = _load(
                                self.session_name,
                                self.guidelines_path,
                                _CODE_RULE,
                            )
                            self.rules = self.work_session.guidance.rules
                            self.rules.priority_inclusion = 1
                            self.rules.priority_detail = "slug"

                        with it("should inject only the rule slug and its star"):
                            rule = _from_file(self.session_name)[_SLUG]
                            expect(self.rules._band(rule)).to(equal("priority"))
                            rendered = self.rules._render(
                                rule, self.rules.priority_detail
                            )
                            expect(rendered).to(contain(_SLUG))
                            expect(rendered).to(contain(f"★{rule.star}"))

                with context("that has changed exclude to 2"):
                    with context("with a rule that failed previous turns inside the context window"):
                        with before.each:
                            self.work_session = _load(
                                self.session_name,
                                self.guidelines_path,
                                _FAILED_IN_CONTEXT,
                            )
                            self.rules = self.work_session.guidance.rules
                            self.rules.exclude = 2

                        with it("should leave that rule out of the prompt"):
                            matching = self.rules._matching_rules(_INJECT)
                            expect([rule.slug for rule in matching]).not_to(
                                contain(_SLUG)
                            )

                        with it("should keep that rule on the collection"):
                            expect(
                                self.guidelines_path.read_text(encoding="utf-8")
                            ).to(contain(_SLUG))
                            expect(_from_file(self.session_name)[_SLUG].examples[-1].mistake).to(
                                equal(_MISTAKE)
                            )

                with context("that has changed exclude to 10"):
                    with context("with a rule that failed five turns ago"):
                        with before.each:
                            self.work_session = _load(
                                self.session_name,
                                self.guidelines_path,
                                _FAILED_FIVE_AGO,
                            )
                            self.rules = self.work_session.guidance.rules
                            self.rules.exclude = 10
                            self.rules.context_inclusion = 5
                            self.rules.context_detail = "slug"

                        with it("should treat that rule as context"):
                            rule = _from_file(self.session_name)[_SLUG]
                            expect(self.rules._band(rule)).to(equal("context"))

                        with it("should inject only the rule slug and its star"):
                            rule = _from_file(self.session_name)[_SLUG]
                            rendered = self.rules._render(
                                rule, self.rules.context_detail
                            )
                            expect(rendered).to(contain(_SLUG))
                            expect(rendered).to(contain(f"★{rule.star}"))
