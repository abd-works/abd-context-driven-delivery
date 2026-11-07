"""Writing an operation's skill or slash-command markdown at install."""

import tempfile

from expects import expect, raise_error
from mamba import before, context, description, it

from harness.agent_tools.agent_tools import agent_instructions, agent_toolset
from harness.installation.files import FileInstallation, InstructionsUnreadableAtInstall, command


@agent_toolset
class _UnreadableInstructions:
    """A toolset whose instructions cannot be read outside a session."""

    @property
    @command
    @agent_instructions
    def instructions(self) -> str:
        """overview"""
        raise RuntimeError("no session open")


with description("an operation installed as a slash command"):
    with context("with instructions that fail when they are read"):
        with before.each:
            self.tool = _UnreadableInstructions().tools["instructions"]
            self.installation = FileInstallation("Claude", tempfile.mkdtemp(), "command")

        with it("should stop the install instead of writing the docstring as the command"):
            expect(lambda: self.installation.install(self.tool)).to(raise_error(InstructionsUnreadableAtInstall))

        with it("should name the operation and the failure"):
            expect(lambda: self.installation.install(self.tool)).to(
                raise_error(
                    InstructionsUnreadableAtInstall,
                    "_UnreadableInstructions.instructions: reading its instructions to write its slash command "
                    "failed: RuntimeError: no session open",
                )
            )
