# Cached knowledge graph that filters never rebuild

A format or filter change works from the graph already built and never rebuilds it; a file change re-reads only that file and re-links its edges.

Plan: harness/graph/.context/cdr/0005-session-graph-is-cached-and-filters-never-build.md (b4b14fe11, branch ui-fixes-as-i-use-it). Today a format toggle takes 18-47 s and a one-file change 25 s; target under 0.5 s and under 3 s.

Differential spec harness/graph/graph_incremental_heavy_spec.py (482bb82bc) shows today's Graph.refresh equals a full build for only 4 of 17 edits. Fix refresh first, faults hit on every refresh: stories only in scenario files dropped; BDD spec subject flips; model-document nodes keep stale written_in. Then cross-file relinking: module facts on add/delete/rename, renamed class heading, renamed Python operation (model_written on 54 steps), renamed bounded context (4 edges lost), renamed TS file, fact order.

Then the plan's manifest with content hashes, loud fallback to a full build, change check (a git checkout is caught), whole graph with filters only, rules cut to those a change reaches, timings. Not built yet: the 30-edit random sequence and the same-findings validate check.

The person said: it can't introduce bugs.
