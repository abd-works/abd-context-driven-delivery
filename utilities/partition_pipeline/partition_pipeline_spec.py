"""BDD spec for PartitionPipeline — kit prose on ContextTool hosts."""

import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_false, be_true, equal, expect
from mamba import before, context, description, it

from primitives.actions.action import _ActionRunRequest, _ActionRunner
from primitives.instructions import Instruction
from primitives.instructions import _path_for_name
from tools.tool import Toolset, _ToolsetLoader

_KIT_DIR = Path(__file__).resolve().parent
_CAR_CHRONICLE_TOOLSET = (
    "context_tools.base.examples.car_chronicle.car_chronicle:CarChronicle"
)
_STORIES_TOOLSET = "context_tools.stories.stories:Stories"
_DEFAULT_PARTITION_SNIPPET = "Determine top-level structure based on user suggestion"
_STORIES_PARTITION_SNIPPET = "**Epics**"


def _expand(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _ActionRunner.instance().run(
        _ActionRunRequest(
            request={"toolset": toolset_path, "context": {}},
            toolset_path=toolset_path,
            action_name=action_name,
            context={},
            arguments=arguments or {},
            instance=instance,
        )
    )


def _section(name: str) -> str:
    return Instruction(_path_for_name(_KIT_DIR, name), _KIT_DIR).expand()


with description("PartitionPipeline kit prose"):
    with it("should resolve partition / index / segment from partition_pipeline.md"):
        expect(_section("partition").startswith("# Partition")).to(be_true)
        expect(_section("index").startswith("# Index")).to(be_true)
        expect(_section("segment").startswith("# Segment")).to(be_true)


with description("PartitionPipeline on a ContextTool host"):
    with context("partition expanded on CarChronicle"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)
            self.host = cls()
            self.response = _expand(
                self.host,
                "partition",
                toolset_path=_CAR_CHRONICLE_TOOLSET,
                arguments={"context": "corpus/", "mode": "one_go"},
            )

        with it("should set action to partition"):
            expect(self.response["action"]).to(equal("partition"))

        with it("should inline Partition section"):
            expect("# Partition" in self.response["instructions"]).to(be_true)
            expect(
                "thin partition of source material" in self.response["instructions"]
            ).to(be_true)

        with it("should nest Index and Segment sections"):
            expect("# Index" in self.response["instructions"]).to(be_true)
            expect("# Segment" in self.response["instructions"]).to(be_true)
            expect("named segment files" in self.response["instructions"]).to(be_true)

        with it("should inline default partition guidance when domain has no partition.md"):
            expect(
                _DEFAULT_PARTITION_SNIPPET in self.response["instructions"]
            ).to(be_true)

        with it("should name the index file after the corpus subject"):
            expect("{subject}-index.md" in self.response["instructions"]).to(be_true)
            expect("corpus basename" in self.response["instructions"]).to(be_true)
            expect(
                "car_chronicle-index.md" in self.response["instructions"]
            ).to(be_false)

    with context("index expanded on Stories"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_STORIES_TOOLSET)
            self.host = cls()
            self.response = _expand(
                self.host,
                "index",
                toolset_path=_STORIES_TOOLSET,
                arguments={"context": "corpus/"},
            )

        with it("should inline stories domain partition.md guidance"):
            expect(_STORIES_PARTITION_SNIPPET in self.response["instructions"]).to(
                be_true
            )

        with it("should name the index after the corpus subject not the skill"):
            expect("{subject}-index.md" in self.response["instructions"]).to(be_true)
            expect("corpus basename" in self.response["instructions"]).to(be_true)
            expect("stories-index.md" in self.response["instructions"]).to(be_false)
