# edges-approach-perpendicular

- **tool:** CleanEngineering
- **error:** Repair→Mistake exits Repair right side (exitX=1) then runs vertical at x=620 parallel to the box flank (~490px) — reads as overlapping the border; should exit Repair top and route to Mistake without a segment parallel to the exit side.
- **rule:** edges-approach-perpendicular
- **how:** Manual draw.io routing — Repair→Mistake exits horizontally at y=1247 instead of running vertical along Repair's right flank.
