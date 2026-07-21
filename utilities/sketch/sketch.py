# @toolset-manifest python -m tools manifest sketch.sketch:Sketcher
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Sketch a solution interactively before generating the formal artifact.

Sketcher is a standalone toolset. Any agent or human can invoke its tools and
sketch_session action directly without decorating anything.

The complementary @sketch decorator (see _decorator.py, re-exported from the
package root) marks a generator's @action so framework-level composition can
prepend the sketch loop automatically — that integration is a deferred slice.
"""
from __future__ import annotations

from pathlib import Path

from primitives.actions.action import action
from tools.tool import tool, toolset


_DEFAULT_TEMPLATE = Path(__file__).parent / "sketch-template.md"


def _context_dir(destination: str) -> Path:
    """Resolve the .context directory under destination (pure)."""
    return Path(destination) / ".context"


def _sketch_path(destination: str, slug: str) -> Path:
    """Resolve the persistence path for a sketch inside destination/.context/ (pure)."""
    return _context_dir(destination) / f"{slug}-sketch.md"


@toolset
class Sketcher:
    """Sketch a solution interactively before generating the formal artifact."""

    @tool
    def find_template(self, agent_dir: str = "") -> str:
        """Locate a sketch template using tiered discovery.
        1. Session context — the caller passes an example directly (skip this tool).
        2. Convention — {agent_dir}/sketch-template.* alongside the wrapped agent's module.
        3. Default — sketch/sketch-template.md (this toolset's canonical terse-indent notation).
        Returns the resolved template contents as a string."""
        if agent_dir:
            root = Path(agent_dir)
            if root.is_dir():
                for path in sorted(root.glob("sketch-template.*")):
                    return path.read_text(encoding="utf-8")
        return _DEFAULT_TEMPLATE.read_text(encoding="utf-8")

    @tool
    def save_sketch(
        self,
        destination: str,
        slug: str,
        content: str,
    ) -> str:
        """Persist a sketch to {destination}/.context/{slug}-sketch.md.
        destination is the folder of the thing being sketched (e.g. ooad/, sketch/).
        Creates .context/ inside destination if missing. Overwrites an existing file at the same path.
        Returns the resolved sketch path."""
        target = _sketch_path(destination, slug)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return str(target)

    @tool
    def list_sketches(self, destination: str, slug: str = "") -> str:
        """List sketch files under {destination}/.context/.
        If slug is provided, filters to sketches matching that slug prefix.
        Returns newline-separated paths; empty string if the folder is missing or empty."""
        context_dir = _context_dir(destination)
        if not context_dir.is_dir():
            return ""
        pattern = f"{slug}-sketch.md" if slug else "*-sketch.md"
        return "\n".join(str(path) for path in sorted(context_dir.glob(pattern)))

    @action
    def sketch_session(self, slug: str, destination: str, agent_dir: str = "") -> str:
        """Sketch {{slug}} interactively — produce a rough artifact through a grill loop, save as soon as the first interim draft is ready, then overwrite on every refinement."""
        """Step 1 — locate the sketch template via find_template(agent_dir=agent_dir). The decorator supplies agent_dir pointing to the wrapped agent's module directory. If the caller supplied a template directly in context (as an attachment or prior artifact), use that instead."""
        self.find_template(agent_dir)
        """Step 2 — draft a rough sketch inspired by the template. Show it in chat, then immediately call save_sketch to persist the interim draft."""
        self.save_sketch()
        """Step 3 — grill the user with 1-3 targeted questions to refine the sketch. Ask ONE question, wait for the answer. Never present bare options."""
        """Step 3a — Frame the decision (2–5 sentences): name the unresolved sketch branch, restate what the current sketch already agrees, and ground the choice in concepts from the wrapped agent's practice material (via agent_dir template/docs — e.g. module rules, OOAD class design). Cite concepts by name."""
        """Step 3b — Present 3–5 options; recommended first with "(Recommended)"; each option gets one short concept-tied rationale (seam, ownership, coupling, or class boundaries). Always end with "Other / I'll specify." """
        """Step 4 — regenerate the sketch after each answer, show it in chat, and call save_sketch again to overwrite the previous draft. Repeat Step 3–4 until the sketch is stable or the user is satisfied. Every new question must repeat Step 3a–3b with a fresh frame for the new branch."""
        self.save_sketch()
        return "Sketch saved for {{slug}}."
