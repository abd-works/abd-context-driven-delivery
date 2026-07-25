# Segment verify — powers/sensory (repair pass)

## Checks
1. Re-extract #### Senses options from PDF pages 177–180 (column order)
2. `verify_segment_completeness` with `<!-- expected-entries -->` on sensory-segment.md

## Results
- Completeness: **PASS (27/27)** (short rank entries Direction/Distance/Time Sense count OK)
- Previously missing bodies restored: Accurate, Acute, Awareness, Detect, Precognition, Postcognition, Microscopic Vision, Penetrates Concealment, etc.
- X-Ray Vision: no separate ALL-CAPS option header in Deluxe PDF extract (sense-types primer only)

## Gate
- Use Senses / Sense Danger inventory may lock against OK option bodies.
- Call `verify_segment_completeness` after any future Senses chunk repair.
