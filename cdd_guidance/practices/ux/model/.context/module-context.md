# ux_model (canonical UX map)

**Purpose:** Keep the information architecture as one UX map — screens, regions, controls, and the transitions between screens — so a diagram, a JSON file, and an HTML mockup stay the same hierarchy every later fidelity reads.

**Seam (terms):** UxModelFactory, UxMap, Screen, Region, Control, StoryDemoControl, Interaction, Transition, ContentType, NavComponent, UxContext

**Dependencies (one-way):** *(none)*

The walk is `ux-model.md` in this folder. `UxModelFactory.load` returns a `UxMap`. The channel class is that map. Each node loads its own children. A channel overrides `has_more_*` and `get_next_*_from_file`. Every channel saves through `save()`.
