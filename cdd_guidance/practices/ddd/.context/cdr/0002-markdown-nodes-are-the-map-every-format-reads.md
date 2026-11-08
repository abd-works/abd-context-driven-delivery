# The sketch and draw.io maps read into the markdown context and aggregate

**Status:** decided, round 6 (finding M1).

## Decision

The sketch and draw.io formats name *MarkdownBoundedContext* as their context type, whose aggregate is *MarkdownAggregate*. Those two classes hold the fields every DDD document shares (notes, the module a context is built as, the headings that group aggregates, an aggregate's cards and root lines) and write both the markdown and the sketch notation.

## Why

- Every format renders the map it is given by asking that map's own nodes for their lines (`context.lines()`, `context.sketch_lines()`), so a map read from any format must be made of nodes that can write every document format. Splitting the sketch notation into its own *SketchBoundedContext* would leave a markdown-read map unable to render as a sketch without copying every node into sketch types, and the copy would need every field the markdown node already holds.
- Draw.io holds fewer facts than markdown (no notes, no cards at bounded-context fidelity), so reading it into the base *BoundedContext* would lose nothing today but would stop a drawn map from rendering as markdown or a sketch at all.
- The notation of each document format stays in one place per notation: markdown lines and sketch lines are separate methods on the same node, reading and writing the same fields, so neither is a second model.

## Consequences

A new document format adds its notation to these nodes, or copies the map into its own node types the way the code formats do (cdr 0001); it does not add a third set of context and aggregate fields.
