# Segment verify — gear (repair pass)

## Checks
1. Re-extract equipment weapons/armor (PDF pp.214–222), vehicles (222–227), HQ features (227–232)
2. HQ `verify_segment_completeness` with expected-entries

## Results
| Chunk | Completeness / notes |
|-------|----------------------|
| equipment-segment.md | Weapons/armor prose restored (Melee/Ranged present). Table rows = scenarios under Use Equipment Effect. |
| vehicles-segment.md | Vehicles section restored from PDF column extract. |
| headquarters-segment.md | **PASS 28/28** feature bodies (Communications, Garage, Hangar, Holding Cells, Fire Prevention, etc.) |

## Gate
- Lock stories against OK prose only.
- Operate Vehicle stays under Use Skills — do not duplicate under Use Vehicles.
- Call `verify_segment_completeness` on HQ (and catalog chunks) after future repairs.
