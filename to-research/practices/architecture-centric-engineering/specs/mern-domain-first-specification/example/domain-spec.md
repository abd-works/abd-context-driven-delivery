---
state: domain-spec
---

# Module: Recipients (Wire Payment Example)

Scope: Select Recipient sub-epic — enterprise beneficiaries eligible for wire payment. Example domain for the MERN Domain-First specification.

---

# Core Domain

## **Recipient**

A beneficiary account an **Enterprise** may pay via wire transfer. Identified by `id`; lifecycle tracked through **Recipient Status**.

### **Recipient** << Entity >>

Initialisation: loaded from persistence via **Recipients Repository**; validated with **Recipient Schema**
------
+ id: string
	Invariant: must be a UUID
+ enterpriseId: string
	Invariant: must belong to exactly one Enterprise
+ name: string
	Invariant: beneficiary name required; max 140 characters
+ accountNumber: string
	Invariant: masked display form always present
+ accountNumberFull: string
	Invariant: full account number stored server-side only
+ status: RecipientStatusType
	Invariant: one of Active, Pending, Inactive
+ << composition >> beneficiaryBank: BeneficiaryBank
+ intermediateBank: IntermediateBank
	Invariant: optional; present when wire route requires intermediary
+ createdAt: Date
+ activatedAt: Date
	Invariant: present only when status is Active
----
+ isEligibleForPayment(): boolean
	Invariant: true only when status is Active
+ fromDto(dto: RecipientDTO): Recipient
	Invariant: hydrates from Zod-parsed persistence or API payload

### **BeneficiaryBank** << ValueObject >>

+ BeneficiaryBank(swiftBic: string, name: string, addressLine1: string, city: string, country: string, abaRouting: string, addressLine2: string)
------
+ swiftBic: string
	Invariant: valid SWIFT/BIC format
+ abaRouting: string
	Invariant: nine digits when country is US
+ name: string
+ addressLine1: string
+ addressLine2: string
+ city: string
+ country: string
	Invariant: ISO 3166-1 alpha-2

### **IntermediateBank** << ValueObject >>

+ IntermediateBank(swiftBic: string, name: string)
------
+ swiftBic: string
+ name: string

### **RecipientStatus** << ValueObject >>

+ RecipientStatus(status: RecipientStatusType, createdAt: Date, countryCode: string)
------
+ status: RecipientStatusType
	Invariant: Active | Pending | Inactive
+ createdAt: Date
+ countryCode: string
	Invariant: US | MX | CA
----
+ isEligibleForPayment(): boolean
	Invariant: true only when status is Active
	Interaction:
		eligible: boolean = status equals Active
		return eligible
+ isPending(): boolean
+ remainingPendingMinutes(): number
	Invariant: non-null only for MX Pending recipients within 30-minute window

### references

**Ref — shared Recipient class**
Source: templates/packages/recipients/shared/Recipient.ts
Locator: whole file
Extract: whole

```source
export class Recipient {
  constructor(/* id, enterpriseId, name, … */) {}
  isEligibleForPayment(): boolean { ... }
  static fromDto(dto: RecipientDTO): Recipient { ... }
}
```

### decisions made

- **Recipient** is an Entity — tracked individually over time with status lifecycle; **class** in shared with `fromDto()` factory.
- Client **RecipientClient extends Recipient** — presentation helpers (`cardCssClass`, `bankName`).

---

## **Recipients**

Collection of **Recipient** instances scoped to an **Enterprise**. Supports filtering and search without mutating underlying items.

### **Recipients** << Entity >>

+ Recipients(items: List<Recipient>)
------
+ << aggregation >> items: List<Recipient>
	Invariant: collection is immutable; operations return new Recipients
----
+ filterByStatus(status: RecipientStatusType): Recipients
	Invariant: every returned Recipient has matching status
	Interaction:
		filtered: List<Recipient> = items where status matches
		result: Recipients = new Recipients(filtered)
		return result
+ filterByEnterprise(enterpriseId: string): Recipients
+ search(query: string): Recipients
	Invariant: matches name or beneficiaryBank.name case-insensitively
	Interaction:
		lower: string = query lowercased
		matched: List<Recipient> = items where name or bank name contains lower
		result: Recipients = new Recipients(matched)
		return result
+ toArray(): List<Recipient>
+ length: number

### **RecipientsServer : Recipients** << Entity >>

Server-side extension — adds persistence-backed load operations. Listed under Boundary Domain below.

### references

**Ref — shared Recipients collection**
Source: templates/packages/recipients/shared/Recipients.ts
Locator: whole file
Extract: whole

```source
export class Recipients {
  constructor(private readonly items: Recipient[]) {}
  filterByStatus(status: RecipientStatusType): Recipients { ... }
  filterByEnterprise(enterpriseId: string): Recipients { ... }
  search(query: string): Recipients { ... }
  toArray(): Recipient[] { ... }
}
```

### decisions made

- **Recipients** collection is immutable — filter/search return new instances (functional collection pattern).
- Shared **Recipients** holds domain logic only; no persistence imports.

---

# Boundary Domain

## **RecipientsServer (server)**

Server-side **RecipientsServer** extends shared collection with repository-backed static loaders. Route handlers delegate here — never to repository or shared directly.

### **RecipientsServer : Recipients** << Entity >>

Initialisation: static factory methods; constructed from repository results wrapped in shared Recipients
------
+ loadByEnterprise(enterpriseId: string, repo: RecipientRepository, opts: { activeOnly: boolean }): List<Recipient>
	Invariant: when activeOnly, every returned Recipient has Active status
	Interaction:
		all: List<Recipient> = repo.findByEnterprise(enterpriseId)
		collection: Recipients = new Recipients(all)
		filtered: Recipients = collection.filterByStatus(Active) when activeOnly
		return filtered.toArray()
+ selectByIds(ids: List<string>, repo: RecipientRepository): List<Recipient>

### **RecipientRepositoryServer : RecipientRepository** << Repository >>

+ findByEnterprise(enterpriseId: string): List<Recipient>
	Invariant: each document validated via RecipientSchema.parse before mapping
+ findByIds(ids: List<string>): List<Recipient>

### references

**Ref — server RecipientsServer**
Source: templates/packages/recipients/server/RecipientsServer.ts
Locator: whole file
Extract: whole

```source
export class RecipientsServer extends Recipients {
  static async loadByEnterprise(enterpriseId, repo, opts?) { ... }
  static async selectByIds(ids, repo) { ... }
}
```

### decisions made

- Server **RecipientsServer** extends shared **Recipients** — domain behavior reused; persistence added at server tier only.
- **RecipientRepository** interface in shared — **RecipientRepositoryServer** implements it in server tier.
- **RecipientRouter** adapts HTTP — delegates to **RecipientsServer**, never repository directly.
- No separate application/service layer — routes call server **RecipientsServer** directly per MERN architecture spec.

---

## **RecipientsClient (client)**

Client-side **RecipientsClient** extends shared collection with selection state and API orchestration. **RecipientClient** extends shared with presentation helpers.

### **RecipientsClient : Recipients** << Entity >>

Initialisation: `load()` static factory from API; immutable updates via `toggleSelection()` returning new instance
------
+ selectedIds: Set<string>
	Invariant: selection tracked separately from filtered items
----
+ load(opts: { activeOnly: boolean }): RecipientsClient
	Interaction:
		items: List<Recipient> = RecipientApi.loadByEnterprise(opts)
		result: RecipientsClient = new RecipientsClient(items)
		return result
+ toggleSelection(id: string): RecipientsClient
+ displayed(query: string): List<RecipientClient>
	Invariant: search delegates to shared search; maps to presentation RecipientClient
+ confirmSelection(): List<Recipient>
	Invariant: validates with SelectRecipientsSchema before POST

### **RecipientClient : Recipient** << Entity >>

Initialisation: extends shared **Recipient** via `fromRecipient()`
------
+ cardCssClass(isSelected: boolean): string
+ bankName: string
	Invariant: presentation accessor over beneficiaryBank.name

### references

**Ref — client RecipientsClient**
Source: templates/packages/recipients/client/RecipientsClient.ts
Locator: whole file
Extract: whole

### decisions made

- Client **RecipientsClient** extends shared — reuses `search()` from shared; adds selection and load orchestration.
- Client **RecipientClient extends Recipient** — presentation helpers; tier-suffix naming keeps shared imports unambiguous.
- **RecipientApi** class in `Recipient.api.ts` — type-safe HTTP client called by **RecipientsClient**.
- Hook (`useRecipients`) is a thin React bridge — no business logic in the hook.
