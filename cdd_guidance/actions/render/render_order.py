"""RenderOrder and WorkerRender: a render to a diagram, drawn in a worker process for a call the cdd server answers for
a chat.

Every chat shares the cdd server's one interpreter. Laying out a class diagram routes each arrow across a grid of the
page, and for a large model that is minutes of CPU-bound Python: run in the server, it holds the interpreter while every
other chat's calls time out. So for a chat's call the server reads the files to render, which is quick, and writes what
to draw as a *RenderOrder*; a worker process makes the same fidelity, draws the diagram, and writes what it drew back,
which the server then saves beside the source as it saves any render.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import TypedDict

from harness.agent_tools.worker_process import WorkerProcess
from harness.guidance.guidance import FidelityGuidance
from harness.guidance.practice_formats import RenderRequest
from harness.markdown.format import Format

# The module a worker process runs, which draws one order.
WORKER_MODULE = "cdd_guidance.actions.render.render_worker"
class RenderFailed(RuntimeError):
    """The worker process drawing a render exited with an error. The message says what failed in one line, the last
    line the worker wrote, which is the error it raised; ``errors`` holds everything it wrote."""

    def __init__(self, exit_code: int, errors: str) -> None:
        written = [line.strip() for line in errors.splitlines() if line.strip()]
        super().__init__(f"the render's worker process exited with {exit_code}: {written[-1] if written else 'it wrote no error'}")
        self.exit_code = exit_code
        self.errors = errors


class RenderOrderDocument(TypedDict):
    """A render order as the server writes it for the worker: the fidelity to render at, by its slug, and the module
    that registers its practice; the format to write; the text to convert and the format it is in; the target file as
    it is now; and the folder the files it links to are in."""

    fidelity: str
    module: str
    format: str
    content: str
    source: str
    previous: str
    folder: str


class RenderOrder:
    """One render as a worker process draws it, read from the document the server writes for it."""

    def __init__(self, document: RenderOrderDocument) -> None:
        self._document = document

    @classmethod
    def from_request(cls, fidelity: FidelityGuidance, request: RenderRequest) -> RenderOrder:
        """request, whose content is the text read from its files, as a worker draws it at fidelity."""
        return cls({
            "fidelity": fidelity.slug,
            "module": type(fidelity.practice_guidance).__module__,
            "format": request.format,
            "content": str(request.content),
            "source": request.source,
            "previous": request.previous,
            "folder": request.folder,
        })

    @classmethod
    def from_text(cls, text: str) -> RenderOrder:
        return cls(json.loads(text))

    @property
    def fidelity(self) -> str:
        """The slug of the fidelity the render works at, such as ``clean-engineering-model``."""
        return self._document["fidelity"]

    @property
    def module(self) -> str:
        """The module whose import registers the fidelity's practice with the practice catalogue."""
        return self._document["module"]

    @property
    def request(self) -> RenderRequest:
        """The render the order asks for, at no fidelity yet: the fidelity the worker makes renders it."""
        document = self._document
        return RenderRequest(
            Format(document["format"]), document["content"], Format(document["source"]), document["previous"], document["folder"],
        )

    @property
    def text(self) -> str:
        return json.dumps(self._document, separators=(",", ":"))


class WorkerRender:
    """One render drawn by a worker process: the server writes the order, the worker draws it at the same fidelity and
    writes what it drew to an answer file, and the server reads that back as the render's result."""

    def __init__(self, fidelity: FidelityGuidance) -> None:
        self._fidelity = fidelity

    def takes(self, request: RenderRequest) -> bool:
        """Whether a worker draws request: a diagram, whose class layout can take minutes, converted from text the
        server read. Content read some other way, such as Stories' story tests merged onto their maps, stays in the
        server."""
        return request.format.group == "diagram" and isinstance(request.content, str)

    def render(self, request: RenderRequest) -> dict:
        """What request renders to, drawn by a worker process; ``RenderFailed`` when the worker exits with an error."""
        with tempfile.TemporaryDirectory(prefix="cdd-render-") as folder:
            order_file, answer_file, errors_file = (Path(folder) / name for name in ("order.json", "answer.json", "errors.txt"))
            order_file.write_text(RenderOrder.from_request(self._fidelity, request).text, encoding="utf-8")
            with open(errors_file, "w", encoding="utf-8") as errors:
                exit_code = WorkerProcess(WORKER_MODULE).run([str(order_file), str(answer_file)], errors)
            if exit_code != 0:
                raise RenderFailed(exit_code, errors_file.read_text(encoding="utf-8", errors="replace"))
            return json.loads(answer_file.read_text(encoding="utf-8"))
