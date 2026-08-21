# edges-do-not-overlap-edges

- **tool:** CleanEngineering
- **error:** Long orthogonal edge runs share the same rows/columns (e.g. WorkSession→Turn at y=978/2384, BaseContextTool→Turn at y=208/2252, Repair→GitRepo at y=986/878) so edge segments stack on top of each other and read as overlapping lines.
- **rule:** edges-do-not-overlap-edges
- **how:** Manual draw.io layout — separated edge corridors by repositioning classes so orthogonal segments no longer stack on shared rows/columns.
