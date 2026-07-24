# Segment verify — gear (equipment / vehicles / headquarters)

## Checks
1. Span text length (segment vs handbook L-spans)
2. Named-entry / section completeness (#### and ALL-CAPS feature headers vs catalogs mentioned in samples)
3. OCR trash signals (truncated table headers, numeric-only tables)

## Results

| Chunk | Span length | Completeness notes |
|-------|-------------|-------------------|
| equipment-segment.md (L9630-L9633, L9634-L10295, L10782-L11007) | PASS ratio ~1.006 | Devices/Inventing/Equipment lifecycle bodies OK. Melee/ranged/armor **tables OCR-truncated** (MELEE W / WEAPON stubs). Constructs creation/command/repair OK; sample PL blocks noisy. |
| vehicles-segment.md (L10296-L10592) | PASS ratio ~1.015 | Traits/Features/Powers/Shared/Alternate + medium categories OK. **Vehicle Size Categories table OCR-garbled**. Feature list partial but usable. |
| headquarters-segment.md (L10593-L10781) | PASS ratio ~1.01 | Size/Toughness + many Features have bodies (Combat Simulator, Defense System, Deathtraps, Dimensional Portal, Dock, Dual Size, Effect, Infirmary, Isolated, Lab, Library, Living Space, Personnel, Temporal Limbo, Workshop). **Missing dedicated bodies** for sample-only names: Communications, Computer, Concealed, Garage, Hangar, Gym, Holding Cells, Fire Prevention System, Power System, Security System, Sealed (mentioned in rebuild prose). |

## Gate
- Story inventory may lock against OK bodies only.
- Table-truncated weapon/armor lines = examples under Use Equipment Effect, not separate stories from tables.
- HQ sample-only features = scenarios under Use HQ Facility until chunk repair.
- Operate Vehicle already exists under Use Skills — do not duplicate under Use Vehicles.

## Status
verify: PASS length; PARTIAL completeness (tables + some HQ features) — proceed with mechanics from OK prose; mark table-only / sample-only as scenarios.
