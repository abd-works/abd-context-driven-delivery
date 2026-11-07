"""The arguments a diagnostics probe calls MCP operations with, and the scratch files and folders they name."""

from __future__ import annotations

import inspect
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from harness.agent_tools.tool_call import ToolCall
from harness.diagnostics.cdd_diagnostic_bridge import CddDiagnosticFixtures


class ProbeArguments:
    """The arguments a probe calls MCP operations with, made for one checkout and the guidance slugs the probe filters
    by, and the scratch files and folders those arguments name; ``cleanup`` removes them. Corpus and sketch operations
    get explicit ``paths``, never an action's default, so a probe never reads or writes the work in progress."""

    def __init__(self, repo: Path | str, slugs: list[str]) -> None:
        self.repo = Path(repo)
        self.slugs = list(slugs)
        self.fixtures = CddDiagnosticFixtures(self.repo)
        self._created: list[Path] = []

    @property
    def guidance_folder(self) -> Path:
        return self.repo / "cdd_guidance"

    @property
    def content_paths(self) -> list[str]:
        """The folder of each practice the slugs name, or of the practice whose fidelity they name; the practices
        folder when no slug names a practice."""
        from harness.guidance.practice_catalogue import PracticeCatalogue

        base = self.guidance_folder / "practices"
        found: list[str] = []
        for slug in self.slugs:
            practice = PracticeCatalogue.practice_named(slug)
            folder = str(base / practice.key) if practice is not None else ""
            if folder and folder not in found:
                found.append(folder)
        return found or [str(base)]

    def for_operation(self, mcp_name: str, member: Any) -> tuple[dict[str, Any], list[str]]:
        """The arguments to call the operation published as mcp_name with, and the names of the required ones the probe
        cannot make. The ``cdd-diagnostic`` fixtures fill in what the probe cannot make itself."""
        parameters = _OperationParameters(member)
        if not parameters.readable:
            return {}, ["callable"]
        arguments = self._made_arguments(mcp_name, parameters.names)
        missing = parameters.missing_from(arguments)
        fixture = self.fixtures.probe_arguments(mcp_name) if missing else None
        if fixture is None:
            return arguments, missing
        fixture_arguments, still_missing = fixture
        return {**arguments, **fixture_arguments}, still_missing

    def work_session(self) -> Any:
        """The main session of a new temp project, for probing operations that write under the session's root, so a
        probe never writes into the session being worked on; ``cleanup`` removes the project, its log included. It is
        opened the way every tool call opens its session."""
        return ToolCall(project=self._temp_dir()).session

    def cleanup(self) -> None:
        """Remove the files and folders the probe made."""
        for path in reversed(self._created):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            elif path.is_file():
                path.unlink(missing_ok=True)
        self._created.clear()

    def _made_arguments(self, mcp_name: str, names: set[str]) -> dict[str, Any]:
        arguments: dict[str, Any] = {"guidance": self.slugs} if "guidance" in names else {}
        if mcp_name == "render.render":
            arguments["paths"] = [self._temp_markdown_file()]
        elif mcp_name in {"document.document", "partition.index", "partition.partition", "sketch.save_sketch"}:
            arguments["paths"] = self.content_paths
        elif "paths" in names and mcp_name.startswith("sketch."):
            arguments["paths"] = self.content_paths
        arguments.update(self._operation_arguments(mcp_name, names))
        return arguments

    def _operation_arguments(self, mcp_name: str, names: set[str]) -> dict[str, Any]:
        """The arguments one operation needs beyond guidance and paths, by its published name."""
        if mcp_name == "render.render":
            return {"format": "markdown", "source": "markdown", "content": ""}
        if mcp_name == "partition.verify_segment_completeness":
            return {"segment_path": self._temp_segment_file()}
        if mcp_name in {"partition.index", "partition.partition"}:
            return {name: value for name, value in (("context", ""), ("mode", "index_only")) if name in names}
        if mcp_name == "grill-context.explore_context_files":
            return {"folder": str(self.repo)}
        if mcp_name == "grill-context.read_context_file":
            return {"path": self._sample_guidance_file()}
        if mcp_name == "grill-context.write_grill_answer":
            return {"heading": "diagnostic-probe", "body": "probe"}
        if mcp_name == "sketch.save_sketch" and "content" in names:
            return {"content": ""}
        if mcp_name == "sessions.switch":
            return {"name": "_cdd_mcp_probe"}
        if mcp_name.startswith("echo.") and "body" in names:
            return {"body": "agent-tools-diagnostics probe"}
        return {}

    def _temp_dir(self) -> str:
        path = Path(tempfile.mkdtemp(prefix="cdd-guidance-probe-"))
        self._created.append(path)
        return str(path)

    def _temp_markdown_file(self) -> str:
        """A one-heading markdown file render reads in the format it is told, so the probe checks the operation runs
        rather than whether a practice folder parses as that practice's current format."""
        handle, name = tempfile.mkstemp(suffix=".md", prefix="cdd-guidance-probe-")
        os.write(handle, b"# Diagnostic probe\n")
        os.close(handle)
        path = Path(name)
        self._created.append(path)
        return str(path)

    def _temp_segment_file(self) -> str:
        handle, name = tempfile.mkstemp(suffix="-segment.md", prefix="cdd-guidance-probe-")
        os.write(handle, b"### diagnostic-probe\n\nprobe body for completeness check.\n")
        os.close(handle)
        path = Path(name)
        self._created.append(path)
        return str(path)

    def _sample_guidance_file(self) -> str:
        candidate = self.guidance_folder / "practices" / "bdd" / "bdd.md"
        if candidate.is_file():
            return str(candidate)
        found = next((path for path in sorted(self.guidance_folder.rglob("*.md")) if path.is_file()), None)
        return str(found or self.guidance_folder)


class _OperationParameters:
    """The parameters a caller passes an operation: every named one, and the ones without a default."""

    def __init__(self, member: Any) -> None:
        try:
            parameters = inspect.signature(member).parameters.values()
        except (TypeError, ValueError):
            self.readable = False
            self._passed: list[inspect.Parameter] = []
            return
        self.readable = True
        variadic = (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        self._passed = [parameter for parameter in parameters if parameter.name not in {"self", "cls"} and parameter.kind not in variadic]

    @property
    def names(self) -> set[str]:
        return {parameter.name for parameter in self._passed}

    def missing_from(self, arguments: dict[str, Any]) -> list[str]:
        """The required parameters arguments leave out."""
        return [parameter.name for parameter in self._passed if parameter.default is inspect.Parameter.empty and parameter.name not in arguments]
