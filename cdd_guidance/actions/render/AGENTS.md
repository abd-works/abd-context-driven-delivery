# render

- Render only converts. Do not call `run`, `begin`, or `end`: it opens no session and commits nothing.
- Pass `source` through to `PracticeGuidance.render`. When `source` is omitted, the content is read as the guidance's current format.
