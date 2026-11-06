"""Probe the installed guidance for ``/guidance-diagnostics``: read each practice's and fidelity's instructions, and call
each guidance action with arguments made for the probe."""

from __future__ import annotations

import inspect
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

# The guidance probed when the caller names none: one practice and one fidelity of another practice.
GUIDANCE_PROBE = ["stories", "clean-engineering-model"]
GUIDANCE_SECTION = "guidance"


class GuidanceProbe:
    """A probe of one install, made for its Installer and the guidance slugs that filter what it calls. The probe makes
    temporary files and folders for the actions it calls, and ``cleanup`` removes them."""

    def __init__(self, installer: Any, slugs: list[str]) -> None:
        self.installer = installer
        self.slugs = list(slugs)
        self._created: list[Path] = []

    @classmethod
    def filtered_by(cls, installer: Any, guidance: list[str] | None) -> GuidanceProbe:
        """The probe for a diagnostics call, which probes ``GUIDANCE_PROBE`` when it names no guidance."""
        return cls(installer, list(guidance or GUIDANCE_PROBE))

    @property
    def guidance_folder(self) -> str:
        """The repository's ``cdd_guidance`` folder. Probes pass it as ``paths`` rather than relying on an action's
        default."""
        return str(Path(self.installer.repo) / "cdd_guidance")

    @property
    def repo_root(self) -> str:
        return str(Path(self.installer.repo))

    @property
    def prefixes(self) -> list[str]:
        """Each slug, then the slug of the practice it names or whose fidelity it names: `stories-story-map` adds
        `stories`, so the practice's own instructions are probed with its fidelity's."""
        from harness.guidance.practice_catalogue import PracticeCatalogue

        prefixes: list[str] = []
        for slug in self.slugs:
            practice = PracticeCatalogue.practice_named(slug)
            for prefix in (slug, practice.slug if practice is not None else ""):
                if prefix and prefix not in prefixes:
                    prefixes.append(prefix)
        return prefixes

    def matches(self, mcp_name: str) -> bool:
        """True when the MCP operation is the instructions of a practice or fidelity this probe's slugs name."""
        return any(
            mcp_name == prefix or mcp_name == f"{prefix}.instructions" or mcp_name.startswith(f"{prefix}-")
            for prefix in self.prefixes
        )

    @property
    def content_paths(self) -> list[str]:
        """The folder of each practice the slugs name, or of the practice whose fidelity they name: explicit ``paths``
        targets, text-safe. The practices folder when no slug names a practice."""
        from harness.guidance.practice_catalogue import PracticeCatalogue

        base = Path(self.guidance_folder) / "practices"
        found: list[str] = []
        for slug in self.slugs:
            practice = PracticeCatalogue.practice_named(slug)
            folder = str(base / practice.key) if practice is not None else ""
            if folder and folder not in found:
                found.append(folder)
        return found or [str(base)]

    def instructions(self) -> str:
        """Read the installed practice and fidelity instructions the slugs name, and write the result under
        ``guidance`` in diagnostics.json."""
        names = self.installer.installed_items("mcp")
        probes = [self._instructions_of(name) for name in names if self.matches(name)]
        subsection = probe_subsection("instructions", self.slugs, probes)
        self.installer.write_diagnostics_section(GUIDANCE_SECTION, {"filter": self.slugs, "instructions": subsection})
        return f"green\n{subsection['report']}"

    def actions(self) -> str:
        """Call each installed guidance action's MCP operations, and write the result under ``guidance`` in
        diagnostics.json."""
        published = set(self.installer.installed_items("mcp"))
        probes: list[dict[str, Any]] = []
        try:
            for ref in self.installer.installed_items("toolset"):
                if "cdd_guidance.actions." not in ref or "cdd_guidance.actions.improvement." in ref:
                    continue
                probes.extend(self._action_toolset(ref, published))
        finally:
            self.cleanup()
        subsection = probe_subsection("actions", self.slugs, probes)
        self.installer.write_diagnostics_section(GUIDANCE_SECTION, {"filter": self.slugs, "actions": subsection})
        return f"green\n{subsection['report']}"

    def arguments_for(self, mcp_name: str, member: Any) -> tuple[dict[str, Any], list[str]]:
        """The arguments to probe an MCP operation with, and the names of the required ones the probe cannot make.
        Corpus and sketches use explicit ``paths``, never action defaults."""
        try:
            signature = inspect.signature(member)
        except (TypeError, ValueError):
            return {}, ["callable"]
        param_names = {
            name
            for name, param in signature.parameters.items()
            if name != "self"
            and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        }
        content_paths = self.content_paths
        args: dict[str, Any] = {}
        if "guidance" in param_names:
            args["guidance"] = self.slugs

        if mcp_name == "render.render":
            args["format"] = "markdown"
            args["paths"] = content_paths
            args["content"] = ""
        elif mcp_name == "document.document":
            args["paths"] = content_paths
        elif mcp_name == "partition.verify_segment_completeness":
            args["segment_path"] = self._temp_segment_file()
        elif mcp_name in {"partition.index", "partition.partition"}:
            args["paths"] = content_paths
            if "context" in param_names:
                args.setdefault("context", "")
            if "mode" in param_names:
                args.setdefault("mode", "index_only")
        elif mcp_name == "grill-context.explore_context_files":
            args["root"] = self.repo_root
        elif mcp_name == "grill-context.read_context_file":
            args["path"] = self._sample_guidance_file()
        elif mcp_name == "grill-context.write_grill_answer":
            args["root"] = self._temp_dir()
            args["heading"] = "diagnostic-probe"
            args["body"] = "probe"
        elif mcp_name == "sketch.list_sketches":
            args["destination"] = self.guidance_folder
            if "slug" in param_names:
                args.setdefault("slug", "")
        elif mcp_name == "sketch.save_sketch":
            args["destination"] = self._temp_dir()
            args["slug"] = "diagnostic-probe"
            args["paths"] = content_paths
            if "content" in param_names:
                args.setdefault("content", "")
        elif "paths" in param_names and mcp_name.startswith("sketch."):
            args["paths"] = content_paths

        missing = [name for name in self._required_parameters(member) if name not in args]
        return args, missing

    def cleanup(self) -> None:
        """Remove the files and folders the probe made."""
        for path in reversed(self._created):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            elif path.is_file():
                path.unlink(missing_ok=True)
        self._created.clear()

    def _instructions_of(self, mcp_name: str) -> dict[str, Any]:
        slug = mcp_name[: -len(".instructions")] if mcp_name.endswith(".instructions") else mcp_name
        try:
            from harness.agent_tools.agent_tools import AgentToolSet
            from harness.guidance_actions.guidance_actions import GuidanceCatalog

            ref = GuidanceCatalog.ref_for(slug)
            if ref is None:
                return {"mcp": mcp_name, "color": "red", "failure": "not a guidance slug"}
            text = AgentToolSet.instantiate(ref).instructions
        except Exception as exc:
            return {"mcp": mcp_name, "color": "red", "failure": failure_text(exc)}
        return instruction_result(mcp_name, text)

    def _action_toolset(self, ref: str, published: set[str]) -> list[dict[str, Any]]:
        from harness.agent_tools.agent_tools import AgentToolSet

        try:
            toolset = AgentToolSet.instantiate(ref)
        except Exception as exc:
            return [{"toolset": ref, "color": "red", "failure": failure_text(exc)}]
        return [
            self._action(toolset, tool)
            for tool in toolset.tools.values()
            if tool.install_to_mcp and tool.mcp_name in published
        ]

    def _action(self, toolset: Any, tool: Any) -> dict[str, Any]:
        member = getattr(toolset, tool.name)
        arguments, missing = self.arguments_for(tool.mcp_name, member)
        if missing:
            return {"mcp": tool.mcp_name, "color": "red", "failure": "needs " + ", ".join(missing)}
        try:
            if tool.kind != "tool":
                result = tool.invoke(arguments)
            elif arguments:
                result = member(**arguments)
            else:
                result = member()
        except Exception as exc:
            return {"mcp": tool.mcp_name, "color": "red", "failure": failure_text(exc)}
        item = instruction_result(tool.mcp_name, result)
        if arguments.get("paths"):
            item["paths"] = arguments["paths"]
        return item

    def _temp_dir(self) -> str:
        path = Path(tempfile.mkdtemp(prefix="cdd-guidance-probe-"))
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
        candidate = Path(self.guidance_folder) / "practices" / "bdd" / "bdd.md"
        if candidate.is_file():
            return str(candidate)
        for path in sorted(Path(self.guidance_folder).rglob("*.md")):
            if path.is_file():
                return str(path)
        return self.guidance_folder

    @staticmethod
    def _required_parameters(member: Any) -> list[str]:
        try:
            signature = inspect.signature(member)
        except (TypeError, ValueError):
            return []
        return [
            name
            for name, param in signature.parameters.items()
            if name != "self"
            and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            and param.default is inspect.Parameter.empty
        ]


def probe_subsection(kind: str, slugs: list[str], probes: list[dict[str, Any]]) -> dict[str, Any]:
    """One diagnostics.json subsection: red when nothing was probed or any probe failed."""
    failed = [item for item in probes if item.get("color") == "red"]
    color = "red" if not probes or failed else "green"
    report = (
        f"{kind}: {len(probes) - len(failed)} returned instructions, "
        f"{len(failed)} failed, filter {', '.join(slugs)}"
    )
    return {"color": color, "report": report, "items": probes}


def instruction_result(mcp_name: str, result: Any) -> dict[str, Any]:
    """The probe record for what an operation returned: green with a preview, or red when it returned nothing."""
    if isinstance(result, str):
        text = result.strip()
    elif result is None:
        text = ""
    else:
        text = json.dumps(result, default=str)
    if not text:
        if mcp_name == "sketch.list_sketches":
            return {"mcp": mcp_name, "color": "green", "chars": 0, "preview": "no sketches"}
        return {"mcp": mcp_name, "color": "red", "failure": "no instructions", "chars": 0}
    return {"mcp": mcp_name, "color": "green", "chars": len(text), "preview": text[:180]}


def failure_text(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"[:400]
