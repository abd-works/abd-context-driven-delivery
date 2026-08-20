# screen-interface-not-a-domain-object

- **tool:** Ddd
- **error:** SelectSim, PickNumber, Dashboard, BillingPage, and other screens modeled as types with open() / isShowing(). Those are UI drivers; the actions belong on Cart / Subscriber / Billing / Order / Customer.
- **rule:** screen-interface-not-a-domain-object
- **what changed:**
  - **Prose — yes.** Rule bullet on ddd.md building_blocks and templates/ddd-sketch.md.
  - **Detector — yes.** ddd/scanners/screen_interface_not_a_domain_object_scanner.py flags open() / isShowing() types.
  - **Generator — no.** The AI is told not to mint screen types; the scanner catches them if it still does.
