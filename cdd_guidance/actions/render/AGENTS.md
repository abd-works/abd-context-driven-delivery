# render

- Bind hosts and convert. Do not call `run`, `begin`, or `end` — no session open and no `Turn.turn` commit.
- Forward `source` into `PracticeGuidance.render`. Host `format` is the parse channel only when `source` is omitted.
