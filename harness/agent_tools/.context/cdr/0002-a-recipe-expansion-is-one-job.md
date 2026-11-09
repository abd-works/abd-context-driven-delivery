# A recipe expansion is one job

*RecipeExpansion* (`recipe.py`) has 45 methods and total complexity 192, the second largest class in harness core. The round-9 review found it has a single connected group of methods: it interprets one recipe body, and recipes are a small language (lines, loops over items, providers on other toolsets, results).

## Decision

It stays one class in round 9. Its loop walking (`_walk_loop*`, `_loop_item_*`) and its provider lookup (`_provider`, `_attribute_chain`, `_roots_at`, `_expand_cross_arg`) are the two parts it could hold, each made once per expansion. That split is its next step, taken when a change to recipes touches those parts, so it is tested against the recipes that change.
