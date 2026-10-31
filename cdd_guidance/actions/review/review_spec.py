"""Review: a person's approval of guidance, recorded in the session log."""
import os
import tempfile
from pathlib import Path

from expects import contain, expect
from mamba import before, context, description, it

from harness.installation.installer import Installer

Installer(repo=Path(__file__).resolve().parents[3]).ensure_import_path()

from review.review import Review  # noqa: E402
from space.session import Session  # noqa: E402

with description("a review of guidance") as self:
    with context("that a person has approved in an open session"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp(prefix="review-session-"))
            (self.repo / ".git").mkdir()
            Session._current = None
            Session.new("pet-visits", self.repo, self.repo)
            transcript = self.repo / ".sessions" / "pet-visits" / "chats" / "review-chat.md"
            transcript.parent.mkdir(parents=True, exist_ok=True)
            transcript.write_text("approved\n", encoding="utf-8")
            os.environ["CDD_REPO"] = str(self.repo)
            os.environ["CDD_PROJECT"] = str(self.repo)
            os.environ["CDD_CONVERSATION_ID"] = "review-chat"
            os.environ["CDD_TRANSCRIPT_PATH"] = str(transcript)
            os.environ["CDD_TRANSCRIPT_LINES"] = "1"
            Session._current = None
            self.log = self.repo / ".sessions" / "pet-visits" / "session.log"
            Review().review("cdd_guidance.practices.stories.stories:Stories")

        with it("should write a review line naming the practice to the session log"):
            expect(self.log.read_text(encoding="utf-8")).to(contain(" review "))
