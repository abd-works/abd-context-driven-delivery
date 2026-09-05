# Specification by Example — Wire Payment (Recipients)

**Sources / context:** MERN architecture specification — `templates/`; epic **Create Wire Payment**, sub-epic **Select Recipient**.

---

## Story: View Active Recipients for Wire Payment

**Story type:** user

**Sources / context:** Wire payment initiation — user selects a beneficiary from enterprise recipients; only **Active** recipients are eligible.

---

## Scenarios

### Scenario 1: User views list of active recipients when initiating wire payment

Given a **User** is logged into ChannelOne 2.0
  And an **Enterprise** has **Recipients** with **Recipient Status** *Active*
    | name | status | bank name | account masked |
    | Acme Corporation | Active | Chase Bank | ****1234 |
    | Global Supplies LLC | Active | Bank of America | ****5678 |
When the **User** initiates **Create Wire Payment**
Then the **Recipient** selection includes only **Recipients** *Acme Corporation* and *Global Supplies LLC*
  And no **Recipient** with **Recipient Status** other than *Active* appears

### Scenario 2: System excludes pending and inactive recipients from selection

Given a **User** is logged into ChannelOne 2.0
  And an **Enterprise** has **Recipients** with mixed **Recipient Status** values
    | name | status |
    | Active Vendor Inc | Active |
    | Pending Vendor LLC | Pending |
    | Inactive Supplier | Inactive |
When the **User** initiates **Create Wire Payment**
Then the **Recipient** selection includes only *Active Vendor Inc*
  And **Recipients** *Pending Vendor LLC* and *Inactive Supplier* are excluded

### Scenario 3: System displays empty state when no active recipients exist

Given a **User** is logged into ChannelOne 2.0
  And an **Enterprise** has no **Recipients** with **Recipient Status** *Active*
When the **User** initiates **Create Wire Payment**
Then the **Recipient** selection is empty
  And the **Wire Payment View** shows an empty-state message

### Scenario 4: User without wire creation entitlement cannot view recipient selection

Given a **User** is logged into ChannelOne 2.0
  And that **User** does not have **Wire Payment.Create** entitlement
When the **User** attempts to access **Create Wire Payment**
Then access is denied with message *You do not have permission to create wire payments*
  And no **Recipient** list is returned

---

## Story: Search Recipients During Selection

**Story type:** user

**Sources / context:** Recipient list supports filtering by name or beneficiary bank while composing a wire payment.

---

## Scenarios

### Scenario 1: User narrows recipient list by beneficiary name

Given a **User** is viewing **Active Recipients** for **Create Wire Payment**
  And **Recipients** include *Acme Corporation* and *Global Supplies LLC*
When the **User** searches for *Acme*
Then the **Recipient** selection shows only *Acme Corporation*

### Scenario 2: User narrows recipient list by bank name

Given a **User** is viewing **Active Recipients** for **Create Wire Payment**
  And a **Recipient** *Acme Corporation* has **Beneficiary Bank** *Chase Bank*
When the **User** searches for *Chase*
Then the **Recipient** selection includes *Acme Corporation*
