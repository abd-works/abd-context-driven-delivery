# Segment verify — powers/sensory

## Checks
1. Span text length vs handbook L-spans
2. Named-entry completeness for #### effects + Senses option ALLCAPS headers

## Results
| Check | Result |
|-------|--------|
| Span length (7 chunks, ratio ~1.019) | PASS |
| #### effects: Sensory, Communication, Comprehend, Concealment, Mind Reading, Remote Sensing, Senses | PASS (bodies present; Concealment extras appear before #### due to OCR reorder) |
| Senses options with headers: Counters Illusion, Danger Sense, Darkvision, Infravision, Low-Light Vision, Radius, Ranged, Rapid, Time Sense, Tracking, Ultra-Hearing, Ultravision | PASS |
| Senses options mentioned elsewhere but MISSING_HEADER in chunk: Accurate, Acute, Awareness, Detect, Direction Sense, Distance Sense, Extended, Penetrates Concealment (partial prose bleed), Precognition, Postcognition, Microscopic, X-Ray | FAIL completeness |
| Shapeshift at file end | OCR bleed from general — ignore |

## Gate
- Lock stories against OK #### effects + listed OK Senses options.
- Missing Senses options = scenarios under Use Senses only if named in sense-types primer, else provisional until re-extract.
- Disbelieve Illusion stays under Use Control Powers; Counters Illusion = Use Senses scenario (auto-resist Illusion for a sense type).

## Status
verify: PASS length; PARTIAL Senses-option completeness — proceed with #### mechanics; incomplete sense options as scenarios/provisional.
