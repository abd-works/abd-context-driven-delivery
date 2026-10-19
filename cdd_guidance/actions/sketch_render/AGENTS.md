# sketch_render

- Same sketch cadence as `sketch` — grill, `save_sketch`, `review_sketch`.
- Render only after review confirms the sketch; never render before approval.
- `build_render_calls` owns render parameters — the sub-agent runs that JSON verbatim.
- Required format pairs: discovery → drawio + markdown (both); specification → typescript + markdown (both). Pass both to `build_render_calls` unless a listed Guidance lacks that channel.
