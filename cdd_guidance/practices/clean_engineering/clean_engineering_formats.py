"""Clean Engineering's formats: the class model of each format, and the module a render of code files is written as."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from harness.guidance.practice_formats import PracticeFormats, RenderRequest


class CleanEngineeringFormats(PracticeFormats):
    """The formats Clean Engineering reads and writes. A code file names no module, since its folder does, so a render
    of the code files of one folder into another code format names the module they form after that folder: the code is
    written under that module's banner, which names the file the fidelity declares for the module
    (``{module}/{module}.py``). Code rendered from text names no folder and stays one text."""

    def render(self, request: RenderRequest) -> dict:
        return super().render(self._naming_the_folders_module(request))

    def _naming_the_folders_module(self, request: RenderRequest) -> RenderRequest:
        """request with the code it converts read into its class model and each module no file names called after the
        folder the files are in; request itself when it converts no code files of this practice's own fidelity."""
        source = request.source_format or self._practice.format
        own = request.fidelity is not None and request.fidelity.practice_guidance is self._practice
        if not (own and request.folder and request.format.is_code and source.is_code and isinstance(request.content, str) and request.content.strip()):
            return request
        model = self.parse(source, request.content)
        for module in model.modules:
            module.name = module.name or Path(request.folder).name
        return replace(request, content=model)
