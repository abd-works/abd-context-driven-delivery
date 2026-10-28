# Get Sign Up Plan

Catalog voucher apply lives on `Voucher` (`apply` / `applied` / `remove`). `VoucherRepository.get` is the CRUD read of Vouchera. `PlanRepository` is the Plan collection only — `list` / `findByName` / `get(id)`.

Vouchera get is two `when`/`then` pairs inside Apply Catalog Voucher. It is not a separate Validate Catalog Voucher story.

Feature-flag evaluation is application configuration. Do not add stories, domain types, or audit items for it.

In this epic's markdown, name Vouchera and Mavenir. Cite `pml-midtier` file paths as source evidence; do not name Midtier as an actor in step labels or narrative hops.
