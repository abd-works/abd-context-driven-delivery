"""A class model written in markdown renders to code that parses: the notes markdown writes after a type, and the words a
heading writes after a class's name, are kept as comments, never as code."""

import ast

from expects import contain, equal, expect
from mamba import before, description, it

from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel

# Seed: a plain model document as the repository's module models write one: a class heading with a note on where the
# class lives, a property whose type carries a note after a dash, and an operation whose return type does.
NOTED_MODEL = "\n".join([
    "# Accounts",
    "",
    "## AccountCredentials",
    "",
    "AccountCredentials(email: string)",
    "------",
    "email: string — identity",
    "----",
    "register(): AccountCredentials — *Access Selfcare*",
    "	-> CredentialsRepository.create(this)",
    "	-> validation.emailValidationCode()",
    "	-> passwordReset.matches(password) — *Access Selfcare*: a temporary password asks for a new one",
    "missingRequirements(): AccountCredentialRequirement[]",
    "",
    "## NoticeWatcher (ide_toast, JavaScript)",
    "",
    "NoticeWatcher()",
    "------",
    "----",
    "watch(): void",
    "",
])


def _class_names(text: str) -> list:
    return [node.name for node in ast.walk(ast.parse(text)) if isinstance(node, ast.ClassDef)]


# Seen 2026-11-17: tools/prompt_notify and the Clean Engineering fixture's models rendered to Python that did not parse.
with description("a markdown class model whose types and headings carry notes, rendered to Python"):
    with before.each:
        model = MarkdownCleanEngineeringModel()
        model.parse(NOTED_MODEL)
        self.python = PythonCleanEngineeringModel().render(model)

    with it("should parse as Python"):
        expect(_class_names(self.python)).to(equal(["AccountCredentials", "NoticeWatcher"]))

    with it("should type the property by the type alone, in Python's spelling"):
        expect(self.python).to(contain("    email: str\n"))

    with it("should keep the property's note as a comment"):
        expect(self.python).to(contain("# identity"))

    with it("should keep the operation's note as a comment"):
        expect(self.python).to(contain("# *Access Selfcare*"))

    with it("should keep the heading's note in the class's description"):
        expect(self.python).to(contain("(ide_toast, JavaScript)"))

    # A model written with another language's types, as the Clean Engineering fixture's TypeScript-style arrays.
    with it("should write an array another language writes as Type[] as a list of that type"):
        expect(self.python).to(contain("def missingRequirements(self) -> list[AccountCredentialRequirement]:"))

    with it("should write an interaction the model writes as a whole call as that call, with no second argument list"):
        expect([self.python.count("CredentialsRepository.create(this)()"), self.python.count("validation.emailValidationCode()()")]).to(equal([0, 0]))

    with it("should leave a note written after an interaction's call out of the code"):
        expect(self.python).to(contain("passwordReset.matches(password)" + chr(10)))
