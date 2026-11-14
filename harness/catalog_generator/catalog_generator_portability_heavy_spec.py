"""Acceptance tests for the "Make Catalog Output Portable" epic that read the real checkout with git. Heavy: runs git."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_true, equal, expect
from mamba import description, it

from harness.catalog_generator.git_citation import GitCitation


with description("Regenerate Catalog Via CLI With Default And Override Flags"):
    with description("given the bare command with no flags"):
        with it("resolves repo_url and ref from git remote origin and current HEAD"):
            citation = GitCitation.from_checkout(_REPO_ROOT)
            expect(citation.repo_url.startswith("https://")).to(be_true)
            expect(len(citation.ref)).to(equal(40))
