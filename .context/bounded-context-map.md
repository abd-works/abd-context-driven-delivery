<!--
  Bounded Context Map — Paradise Mobile System Landscape
  Fidelity: bounded_context
  Sources: System Landscape Overview (2026-08-24)
-->

# Bounded Context Map — Paradise Mobile

**Sources / context:** System Landscape Overview — customer-facing stack, integration layers, DEP/Mavenir back-end, marketing consolidation, distributed customer data problem, support stack, vouchers/loyalty, device commerce orphan data.

---

## Context Map

```
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  My Paradise                                                            │
  │  team: Digital product                                                  │
  │  onboarding + self-care customer experience                             │
  │                                                                         │
  │  Prospect, Customer, Subscriber, Cart                                     │
  └───────────────────────────────┬─────────────────────────────────────────┘
                                  │ Anticorruption Layer (customer API)
                                  │ Customer, Cart, Plan, Subscription, Billing
                                  ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Customer Gateway                                                       │
  │  team: Platform / integration                                         │
  │  mid-tier ACL — Cognito pool 2, limited customer role                 │
  └───────────────────────────────┬─────────────────────────────────────────┘
                                  │ Customer/Supplier
                                  │ Account, Subscription, Billing, Plan, Msisdn
                                  ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Subscription & Billing (DEP)                                           │
  │  team: Mavenir / billing ops                                            │
  │  de facto source of truth — CRM, subscriptions, billing, catalog, MSISDN │
  │                                                                         │
  │  Account, Subscription, Billing, Plan, MsisdnInventory                  │
  └───────┬─────────────────────────────┬───────────────────────────────────┘
          │ Conformist                  │ Customer/Supplier
          │ Account snapshot            │ Voucher apply, loyalty balance
          ▼                             ▼
  ┌───────────────────┐     ┌─────────────────────────────────────────┐
  │  Customer Support │     │  Promotions & Loyalty                     │
  │  Zendesk + 3CX    │     │  Vouchera in DEP                          │
  │  SupportCase      │     │  Voucher, LoyaltyAccount                  │
  └───────────────────┘     └─────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Device Commerce                                                        │
  │  Zoho Inventory Manager, Figaro, Vireo                                  │
  │  hard-asset sales — orphan from DEP today                               │
  │                                                                         │
  │  DeviceOrder, Payer, DeviceInventory                                    │
  └─────────────────────────────────────────────────────────────────────────┘
          ▲ Separate Ways (no sync today) — payer/subscriber gap open

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Marketing Engagement                                                   │
  │  Zoho Marketing Suite (consolidating Mailchimp, Typeforms, Zapier)      │
  │  Campaign, Lead                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
          ▲ Separate Ways / batch extract today — Juliano owns consolidation
```

### Context inventory

| Context | Team | Scope | Implementation |
|---|---|---|---|
| My Paradise | Digital product | Customer digital onboarding and self-care; one ubiquitous language for prospect → subscriber lifecycle | customer-facing web app (My Paradise portal) |
| Customer Gateway | Platform / integration | Mid-tier ACL between My Paradise and DEP; Cognito pool 2; grants limited customer API role | integration service (mid tier) |
| Subscription & Billing | Mavenir / billing ops | CRM accounts, subscriptions, billing, subscription product catalog, MSISDN inventory — de facto source of truth | DEP (Mavenir) — Cognito pool 1 for back-office |
| Device Commerce | Retail / inventory ops | Hard-asset sales (phones, accessories); payer may differ from subscriber; Figaro and Vireo for inventory billing | Zoho Inventory Manager + Figaro + Vireo (manual, no DEP sync) |
| Customer Support | Support ops (Samir) | Support tickets, case history, inbound social and phone interactions | Zendesk + 3CX PBX |
| Promotions & Loyalty | Marketing / product | Voucher and loyalty programs at customer, subscription, and cart levels | Vouchera (integrated into DEP) |
| Marketing Engagement | Marketing (Juliano) | Campaigns, lead capture, audience — consolidating legacy tool sprawl | Zoho Marketing Suite (target); Mailchimp, Typeforms, Zapier (retiring) |

---

## My Paradise

- **Owning team:** Digital product
- **Scope:** Customer-facing digital experience — acquisition (onboarding) and self-care share one language for Customer identity, plan selection, cart, and subscriber management. UI themes (onboarding screens, self-care dashboard) are not separate contexts.
- **Implementation:** customer-facing web app / portal

### Prospect

- **Root:** Prospect
- **Boundary members:** Cart, OnboardingStep — acquisition state and checkout cart must stay consistent for one prospect
- **Protected invariants:** onboarding step is derived from cart and identity completeness; cart is owned by the prospect for the duration of acquisition; prospect converts to subscriber only after successful checkout
- **Cross-aggregate refs:** Customer (by CustomerId) — consistency: immediate; Shared Kernel identity with Subscriber

### Customer

- **Root:** Customer
- **Boundary members:** Identity, Address — contact and verification details
- **Protected invariants:** one customer identity across prospect and subscriber phases; email is the cross-system correlation key (today manual)
- **Cross-aggregate refs:** none within context — identity is the shared kernel anchor

### Subscriber

- **Root:** Subscriber
- **Boundary members:** Subscription, Billing — active lines and payment relationship
- **Protected invariants:** subscription is an invariant of subscriber (not independently retrievable); billing methods belong to the paying party on the account
- **Cross-aggregate refs:** Customer (by CustomerId) — consistency: immediate; Shared Kernel

### Cart

- **Root:** Cart
- **Boundary members:** PlanSelection, MsisdnSelection, SimSelection, PortabilityInformation — checkout selections
- **Protected invariants:** cart exists only in context of a prospect; selections must be complete before checkout; portability information required when porting a number
- **Cross-aggregate refs:** Plan (by PlanId, snapshot at select) — consistency: snapshot; MsisdnInventory (reservation) — consistency: immediate until checkout completes or expires

---

## Customer Gateway

- **Owning team:** Platform / integration
- **Scope:** Exclusive integration path between My Paradise and DEP for customer-level operations. Translates customer-facing concepts to DEP API contracts. Not a UI theme — an anticorruption boundary.
- **Implementation:** mid-tier integration service; Cognito user pool 2

### CustomerSession

- **Root:** CustomerSession
- **Boundary members:** AuthorizedScope — token-bound customer role with limited API surface
- **Protected invariants:** session grants only customer-scoped DEP operations; back-office operations route through pool 1, not through this gateway
- **Cross-aggregate refs:** none — gateway holds translation state, not business aggregates

---

## Subscription & Billing

- **Owning team:** Mavenir / billing ops
- **Scope:** De facto source of truth for subscriptions, CRM accounts, billing, subscription product catalog, and MSISDN number pool. Stable account identity; faster-changing line and billing lifecycle.
- **Implementation:** DEP (Mavenir); Cognito pool 1 for back-office / store access

### Account

- **Root:** Account
- **Boundary members:** ContactProfile — CRM-level customer record
- **Protected invariants:** one account per customer in DEP; account creation triggers downstream customer provisioning (Zendesk)
- **Cross-aggregate refs:** Subscription (by SubscriptionId) — consistency: immediate within account; Billing (by BillingId) — consistency: immediate

### Subscription

- **Root:** Subscription
- **Boundary members:** Bundle, Usage — active line, plan bundle, consumption
- **Protected invariants:** subscription status governs service availability; bundle change is a subscription lifecycle event; MSISDN and SIM type are fixed at activation unless ported or replaced
- **Cross-aggregate refs:** Plan (by PlanId) — consistency: snapshot at subscribe; MsisdnInventory (by Msisdn) — consistency: immediate at assignment

### Billing

- **Root:** Billing
- **Boundary members:** Invoice, PaymentMethod, Transaction — invoices and payment history
- **Protected invariants:** invoices roll up to billing account; payment method changes do not retroactively alter posted invoices
- **Cross-aggregate refs:** Account (by AccountId) — consistency: immediate

### Plan

- **Root:** Plan
- **Boundary members:** BundleTerms, PricingTier — subscription product catalog
- **Protected invariants:** plan availability and pricing are authoritative here; promotional overrides applied via Promotions context at checkout
- **Cross-aggregate refs:** none required for catalog reads

### MsisdnInventory

- **Root:** MsisdnInventory
- **Boundary members:** TelephoneNumber, PortingInformation — available numbers and port-in state
- **Protected invariants:** a number is either available, reserved, or assigned — never double-assigned; porting uses `port()`, not a separate portability-request type
- **Cross-aggregate refs:** Subscription (by SubscriptionId on assign) — consistency: immediate

---

## Device Commerce

- **Owning team:** Retail / inventory ops
- **Scope:** Hard-asset sales (phones, accessories) managed outside DEP. Supports non-subscriber device purchases and payer ≠ subscriber scenarios. No sync with DEP today — orphan data is a known integrity risk.
- **Implementation:** Zoho Inventory Manager; Figaro and Vireo for inventory billing

### DeviceOrder

- **Root:** DeviceOrder
- **Boundary members:** LineItem, Shipment — sale lines and fulfilment
- **Protected invariants:** payer and subscriber (beneficiary) may differ — both must be recorded; device sale does not require a DEP account for non-subscribers
- **Cross-aggregate refs:** Payer (by PayerId) — consistency: immediate; Subscriber (by SubscriberId, optional) — consistency: none today (manual cross-reference by email)

### Payer

- **Root:** Payer
- **Boundary members:** PaymentDetails — who pays for the device
- **Protected invariants:** payer identity is independent of subscription holder; same person may be payer on a device order and subscriber on a DEP account without automatic linkage
- **Cross-aggregate refs:** none — Separate Ways from DEP until formally modeled

### DeviceInventory

- **Root:** DeviceInventory
- **Boundary members:** StockLevel, Sku — phones and accessories on hand
- **Protected invariants:** stock decrements on confirmed sale; no subscription catalog overlap (DEP cart handles subscriptions only today)
- **Cross-aggregate refs:** none

---

## Customer Support

- **Owning team:** Support ops (Samir)
- **Scope:** Customer support cases, ticket history, and phone interactions. Unique data: tickets and case history; customer profile sourced from DEP.
- **Implementation:** Zendesk; 3CX PBX integrated for inbound calls

### SupportCase

- **Root:** SupportCase
- **Boundary members:** CaseComment, CaseHistory — ticket thread and status transitions
- **Protected invariants:** case history is append-only; customer identity on case matches DEP account at creation time (snapshot)
- **Cross-aggregate refs:** Account (by AccountId, snapshot) — consistency: snapshot; CallRecord (by CallId) — consistency: immediate when linked

### CallRecord

- **Root:** CallRecord
- **Boundary members:** Transcript, SentimentSummary — call metadata and future transcription output
- **Protected invariants:** inbound call lookup by phone number; unknown caller creates new ticket; transcription and sentiment are opportunities, not yet implemented
- **Cross-aggregate refs:** SupportCase (by CaseId) — consistency: immediate on match

---

## Promotions & Loyalty

- **Owning team:** Marketing / product
- **Scope:** Voucher, loyalty, and promotional capabilities integrated into DEP via Vouchera (replaced Voucherify). Three voucher levels: customer (affiliate/volume), subscription (sign-up campaigns), cart (longer-term, not yet implemented).
- **Implementation:** Vouchera in DEP; N8N automates volume discount logic for affiliate codes

### Voucher

- **Root:** Voucher
- **Boundary members:** DiscountRule, Redemption — code, eligibility, and application
- **Protected invariants:** voucher level determines application point (customer, subscription, or cart); one-time campaign vouchers consumed at sign-up; affiliate volume discounts automated via N8N
- **Cross-aggregate refs:** Cart (at checkout) — consistency: immediate; Subscription (at sign-up) — consistency: immediate

### LoyaltyAccount

- **Root:** LoyaltyAccount
- **Boundary members:** PointsBalance, Tier — loyalty standing
- **Protected invariants:** points accrue and redeem per program rules; loyalty is customer-scoped
- **Cross-aggregate refs:** Account (by AccountId) — consistency: eventual

---

## Marketing Engagement

- **Owning team:** Marketing (Juliano)
- **Scope:** Campaign management, lead capture, and audience engagement. Consolidating Mailchimp, Typeforms, spreadsheets, and Zapier into Zoho Marketing Suite. Tool retirement order and cost-benefit TBD.
- **Implementation:** Zoho Marketing Suite (target); legacy tools retiring

### Campaign

- **Root:** Campaign
- **Boundary members:** AudienceSegment, Content — campaign definition and targeting
- **Protected invariants:** campaign audience is derived from leads and CRM segments; consolidation must not duplicate customer records already in DEP
- **Cross-aggregate refs:** Lead (by LeadId) — consistency: eventual

### Lead

- **Root:** Lead
- **Boundary members:** FormResponse — captured from Typeforms and landing pages
- **Protected invariants:** lead is pre-account — conversion to DEP account is a separate lifecycle event
- **Cross-aggregate refs:** none today — Separate Ways from DEP; manual entry contributes to distributed monolith problem

---

## Dependencies

### My Paradise → Customer Gateway

- **Direction:** My Paradise is upstream; Customer Gateway is downstream
- **What crosses:** Customer, Cart, Plan, Subscription, Billing — translated to DEP API contracts
- **How they integrate:** Synchronous REST — at each customer action (e.g. `Cart.checkout()`, `Subscriber.changePlan()`), My Paradise calls mid-tier endpoints which translate and forward to DEP
- **Relationship pattern:** Anticorruption Layer
- **Rationale:** Mid tier is the exclusive integration path for customer-level access; isolates My Paradise from DEP API churn and enforces limited customer role (Cognito pool 2)

### Customer Gateway → Subscription & Billing

- **Direction:** Customer Gateway is upstream; Subscription & Billing is downstream
- **What crosses:** Account, Subscription, Billing, Plan, MsisdnInventory operations
- **How they integrate:** Synchronous API — gateway authenticates via Cognito pool 2 and calls DEP customer-scoped endpoints; back-office routes use pool 1 directly (Leo to confirm current vs target routing)
- **Relationship pattern:** Customer/Supplier
- **Rationale:** DEP is supplier of record; gateway is customer of DEP APIs with joint acceptance tests on translated contracts

### Subscription & Billing → Customer Support

- **Direction:** Subscription & Billing is upstream; Customer Support is downstream
- **What crosses:** Account (customer identity snapshot) — triggers Zendesk customer creation on Mavenir account creation
- **How they integrate:** Event-driven — on `Account.created`, provision Zendesk customer; support reads DEP-sourced profile, owns ticket history only
- **Relationship pattern:** Conformist
- **Rationale:** Zendesk adopts DEP customer identity; unique data in support is tickets and case history

### Customer Support → Customer Support (3CX internal)

- **Direction:** 3CX is upstream for call events; Zendesk is downstream for ticket creation
- **What crosses:** phone number lookup → SupportCase; CallRecord → case link; future Transcript and SentimentSummary
- **How they integrate:** Synchronous lookup on inbound call — 3CX queries by phone number, auto-opens or creates Zendesk ticket; social channels (Facebook, LinkedIn, Instagram) feed inbound tickets separately
- **Relationship pattern:** Customer/Supplier
- **Rationale:** 3CX supplies call events; Zendesk is the case system of record

### Promotions & Loyalty → Subscription & Billing

- **Direction:** Promotions & Loyalty is upstream for discount application; Subscription & Billing is downstream for priced outcome
- **What crosses:** Voucher redemption, LoyaltyAccount balance — applied at customer, subscription, or cart level
- **How they integrate:** Synchronous — at `Cart.checkout()` or subscription sign-up, Vouchera validates and applies discount; N8N automates affiliate volume discount workflows
- **Relationship pattern:** Customer/Supplier
- **Rationale:** Vouchera replaced Voucherify and lives inside DEP; promotions context owns rules, billing context owns priced subscription

### Device Commerce → Subscription & Billing

- **Direction:** no integration today
- **What crosses:** none — same customer may exist as four different "Jeffs" across Zoho Inventory, Zoho CRM, DEP, and Zendesk
- **How they integrate:** none — manual independent entry; email used for ad-hoc cross-reference ("did Jeff buy a phone?")
- **Relationship pattern:** Separate Ways
- **Rationale:** orphan data is the core pain; payer vs subscriber relationship must be formally modeled before integration. Open question: DEP shopping cart vs Zoho CRM cart vs custom cart as inventory expands

### Marketing Engagement → Subscription & Billing

- **Direction:** Marketing Engagement is upstream for leads; Subscription & Billing is downstream for converted accounts
- **What crosses:** Lead → Account conversion (manual today)
- **How they integrate:** Batch / manual — leads from Typeforms and campaigns entered independently; consolidation into Zoho Marketing Suite will reduce sprawl but does not yet sync to DEP
- **Relationship pattern:** Separate Ways (today); target Open Host / Published Language after Juliano consolidation
- **Rationale:** tool sprawl creates security, cost, and inefficiency; retirement order TBD with Juliano

### My Paradise → Marketing Engagement

- **Direction:** mutual — Paradise Mobile website and My Paradise may deep-link to campaigns and forms
- **What crosses:** Campaign landing URLs, Lead capture from marketing CTAs
- **How they integrate:** HTTP deep-link — customer arrives from marketing site or external campaign; no shared customer record until manual conversion
- **Relationship pattern:** Separate Ways
- **Rationale:** marketing stack is consolidating; integration pattern to be decided during Zoho Marketing Suite migration

---

## Standalone / follow-up

| Item | Owner | Target | Notes |
|---|---|---|---|
| Mid tier vs back office routing | Leo | TBD | Confirm which connections route through each layer vs intended target state |
| Marketing tool retirement order | Juliano | TBD | Cost-benefit and buy-in for Zoho Marketing Suite consolidation |
| 3CX transcription + sentiment | Samir | TBD | Opportunity on inbound call → ticket generation |
| Payer vs subscriber model | Retail / product | TBD | Formalize across Device Commerce and Subscription & Billing |
| Shopping cart strategy | Product | TBD | DEP cart (subscriptions only) vs Zoho CRM cart vs custom as inventory expands |
| Customer distributed monolith | Cross-team | first fix: consistent data entry | Maps to many downstream problems; DEP is de facto subscription truth |
