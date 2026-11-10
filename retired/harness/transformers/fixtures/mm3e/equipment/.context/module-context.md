## Language

*Equipment* is the equipment-point pool spent on items, devices, vehicles, headquarters, and constructs.

### Equipment

- Spends equipment points on items.
- **Invariant:** Equipment bonus does not stack with same-type equipment bonus. Protection from a device is not equipment bonus.

### Device

- A power worn or carried as a removable device.

### Vehicle

- A vehicle with size traits and features.

### Headquarters

- A headquarters with size traits and features.

### Construct

- A construct with an ability profile that can be issued an order.

Build order: `checks` → `character-construction` → `ability` → `skill` → `advantage` → `power` → `equipment` → `combat`

---

# equipment
- **Purpose:** Spend equipment points; cost removable devices; invent; hold vehicle, headquarters, and construct traits.
- **Seam (terms):** Equipment, Device, Vehicle, Headquarters, Construct
- **Dependencies (one-way):** advantage (Equipment ranks → EP budget; Minion for construct), power (device is a power with Removable; vehicle/HQ power effects at 1/5), checks (design/construction checks)
- **Primary use case:** `equipment.pay_for(item)`; `construct.issue_order()`
- **Rationale:** A device is a *Power* with removable. Equipment points are not power points.
- **Public API:** `Equipment.pay_for`, `Construct.issue_order`
- **Sources / context:** `harness/transformers/fixtures/mm3e/mm3e-sketch.md` (`ce:` equipment; stories Configure Equipment Pool / Acquire Weapons)

## Constraint

Do not stack same-type equipment bonus. Do not treat Protection from a device as equipment bonus.
