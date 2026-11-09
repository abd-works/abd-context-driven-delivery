"""Capturing documents end to end, each step answered the way the MCP host answers it, with the arguments the step
before tells the agent to pass: convert, then partition, then the segment files the partition wrote, then embed. Each
step must read what the step before wrote, so a recipe that restates another action's output location wrongly fails
here instead of building an empty index with no error."""
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
import mcp.types  # noqa: F401 - the SDK, before harness/mcp is on the import path
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect, have_len
from mamba import after, before, context, description, it

import cdd_guidance.actions  # noqa: F401 - registers the actions and the practices
from cdd_guidance.actions.partition.partition import Partition
from cdd_guidance.context_setup.context_index import ContextIndex
from cdd_guidance.context_setup.context_setup import ContextSetup
from harness.agent_tools.tool_call import ToolCall
from space.session.throwaway_project import ThrowawayProject


class FakeEmbeddingProvider:
    """One small vector per text, so embedding needs no API."""

    def embed_texts(self, texts: list) -> list:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list:
        return [float(len(text) % 7 + 1), 1.0, 0.5, 0.25]

_FOLDER = "docs"
# Where the partition's reply says each segment goes; the agent fills in the artifact its practice's Scaffold names.
_SEGMENT_PLACE = re.compile(r"written as (\S+-segment\.md)")


def _answered(toolset, name: str, arguments: dict, project: Path):
    """The answer the MCP host gives a call of toolset's tool name, sending only arguments."""
    return toolset.tools[name].answer(ToolCall(arguments, project))


with description("documents captured into an index"):
    with before.all:
        self.throwaway = ThrowawayProject()
        self.root = self.throwaway.root
        documents = self.root / _FOLDER
        documents.mkdir()
        (documents / "brief.md").write_text("# Checkout\n\nA shopper pays for the order in the cart.\n", encoding="utf-8")
        self.recipe = _answered(ContextSetup(), "capture_from_documents", {"folder_path": _FOLDER}, self.root)
        self.converted = _answered(ContextSetup(), "convert", {"folder_path": _FOLDER}, self.root)
        # Step 3 as the recipe says: the files convert returned, out_root the documents' folder.
        arguments = {"guidance": ["stories"], "paths": list(self.converted.markdown_files), "out_root": _FOLDER}
        self.partitioned = _answered(Partition(), "partition", arguments, self.root)
        # The agent writes one segment where the partition's reply places it.
        place = _SEGMENT_PLACE.search(self.partitioned).group(1)
        self.written = Path(place.replace("{artifact}", "checkout"))
        self.written.parent.mkdir(parents=True)
        self.written.write_text("# Checkout\n\nA shopper pays for the order in the cart.\n", encoding="utf-8")
        # Step 4 as the recipe says: the segment files partition lists, embedded beside the documents.
        self.segments = _answered(Partition(), "segment_files", {"out_root": _FOLDER}, self.root)
        embed = {"segments_paths": self.segments, "out_path": f"{_FOLDER}/rag"}
        self.embedded = _answered(ContextIndex(FakeEmbeddingProvider()), "embed", embed, self.root)

    with after.all:
        self.throwaway.close()

    with context("whose capture recipe is answered with only the folder"):
        with it("should tell the agent to partition the files convert returned"):
            expect(self.recipe).to(contain("paths = the markdown_files convert returned"))

        with it("should tell the agent to write the partition beside the documents"):
            expect(self.recipe).to(contain(f"out_root = {_FOLDER}"))

        with it("should tell the agent to embed the segment files the partition lists"):
            expect(self.recipe).to(contain(f"Call partition.segment_files with out_root={_FOLDER}"))

        with it("should not tell the agent to partition with no guidance"):
            expect(self.recipe).not_to(contain("with no guidance"))

    with context("whose partition is answered with the converted files"):
        with it("should name every file convert wrote as the corpus"):
            expect(all(file in self.partitioned for file in self.converted.markdown_files)).to(equal(True))

        with it("should place the segments under the documents' folder"):
            expect(self.written.resolve().is_relative_to((self.root / _FOLDER).resolve())).to(equal(True))

    with context("whose segment files are listed"):
        with it("should list the segment the agent wrote where the partition placed it"):
            expect(self.segments).to(equal([self.written.resolve().as_posix()]))

    with context("whose segments are embedded"):
        with it("should index every segment the partition wrote"):
            expect(self.embedded.segment_count).to(equal(1))

        with it("should write the index beside the documents"):
            expect(Path(self.embedded.index_path).resolve()).to(equal((self.root / _FOLDER / "rag").resolve()))


_OPTIONS = re.compile(r"Options: (.+)")


def _partitioned(word: str, project: Path) -> str:
    """The partition's reply to a call naming word as its one guidance, or the error it raised."""
    try:
        return _answered(Partition(), "partition", {"guidance": [word], "paths": [_FOLDER]}, project)
    except Exception as failure:  # noqa: BLE001 - the error is what the example reads
        return f"raised {type(failure).__name__}: {failure}"


# The agent offers the user exactly the words the recipe lists and passes the choice to partition, so each must partition.
with description("the indexers a capture recipe offers"):
    with before.all:
        self.throwaway = ThrowawayProject()
        recipe = _answered(ContextSetup(), "capture_from_documents", {"folder_path": _FOLDER}, self.throwaway.root)
        self.offered = [word.strip() for word in _OPTIONS.search(recipe).group(1).split("|")]
        self.replies = {word: _partitioned(word, self.throwaway.root) for word in self.offered}

    with after.all:
        self.throwaway.close()

    with it("should offer every practice partition indexes by"):
        expect(self.offered).to(equal(["stories", "ddd", "ux", "clean-engineering", "bdd"]))

    with it("should offer only words partition accepts"):
        expect([word for word, reply in self.replies.items() if reply.startswith("raised")]).to(equal([]))


# embed requires out_path; a step that leaves it out fails the MCP call or leaves the agent guessing where the index goes.
with description("a live-app capture recipe answered with only the application's folder"):
    with before.all:
        self.throwaway = ThrowawayProject()
        self.recipe = _answered(ContextSetup(), "capture_from_live_app", {"repo_path": "app"}, self.throwaway.root)
        self.embeds = re.findall(r"context_index\.embed\(([^)]*)\)", self.recipe)

    with after.all:
        self.throwaway.close()

    with it("should tell the agent to embed what it captured"):
        expect(self.embeds).not_to(equal([]))

    with it("should name where each embed writes its index"):
        expect([call for call in self.embeds if "out_path=" not in call]).to(equal([]))


with description("an index embedded from a capture's extraction overview"):
    with before.all:
        self.throwaway = ThrowawayProject()
        overview = self.throwaway.root / "capture" / "extraction-overview.md"
        overview.parent.mkdir(parents=True)
        overview.write_text("# Extraction overview\n\n## Checkout page\n\nA pay button.\n", encoding="utf-8")
        embed = {"segments_paths": ["capture/extraction-overview.md"], "out_path": "capture/rag"}
        self.embedded = _answered(ContextIndex(FakeEmbeddingProvider()), "embed", embed, self.throwaway.root)

    with after.all:
        self.throwaway.close()

    with it("should index the overview as one markdown file"):
        expect(self.embedded.segment_count).to(equal(1))


with description("a partition answered with only its guidance"):
    with before.all:
        self.throwaway = ThrowawayProject()
        self.reply = _answered(Partition(), "partition", {"guidance": ["stories"]}, self.throwaway.root)

    with after.all:
        self.throwaway.close()

    with it("should ask for the corpus rather than name a blank one"):
        expect(self.reply).to(contain("ask which files or folder"))

    with it("should leave no blank where the corpus is named"):
        expect(self.reply).not_to(contain("at  under"))
