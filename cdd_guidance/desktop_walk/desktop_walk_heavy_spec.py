"""A desktop walk's test chat on real git: the throwaway folder is a repository the chat bar can draw a session for."""
import shutil
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.desktop_walk.desktop_walk import DesktopWalk


class OpenedChats:
    """The chats' opener as the walk sees it: no chat is opened in the Claude app."""

    def open_new(self, folder: str, prompt: str) -> str:
        return f"claude://code/new?folder={folder}"


with description("a desktop walk of a project") as self:
    with context("that opens the test chat a walk drives"):
        with before.all:
            self.test_chats = Path(tempfile.mkdtemp(prefix="desktop-walk-chats-"))
            self.test_chat = DesktopWalk(self.test_chats / "project", opener=OpenedChats(), test_chats_folder=self.test_chats).open_test_chat()

        with after.all:
            shutil.rmtree(self.test_chats, ignore_errors=True)

        with it("should make a throwaway git repository for the chat to work in"):
            expect((Path(self.test_chat.folder) / ".git" / "HEAD").is_file()).to(equal(True))
