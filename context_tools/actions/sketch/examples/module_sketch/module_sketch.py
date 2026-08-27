"""Example: produce a rough module-design sketch via an interactive grill loop."""

from __future__ import annotations

from sketch.sketch import Sketch


class ModuleSketch(Sketch):
    """Draft a module-design sketch and persist it to the session docs dir."""

    def draft(self, path: str, slug: str) -> str:
        """Sketch the module identified by *slug* with *path* as the destination.

        Calls ``sketch_session`` which grills for shape, drafts a rough design
        from the built-in template, and writes ``{slug}-sketch.md`` under the
        destination docs dir immediately on the first draft and after each
        refinement pass.

        Returns the action result string confirming the sketch was saved.
        """
        return self.sketch_session(slug=slug, destination=path)
