# Zendesk Service

Zendesk REST API client used exclusively by the Mavenir customer controller (`src/entities/Mavenir/controllers/customer/controller.ts`). Provides a library of payload-builder methods that construct typed ticket bodies from `CustomerResponse` domain objects, then posts them via `Zendesk.createTicket()`.

Uses the legacy `helpers/axios` bare instance rather than `AxiosFactory`.

---

**Payload builders and when they are called:**

**`trialPayload`** -- called during onboarding when the customer's voucher is a trial; creates a sales task ticket with a future due date for the customer success team to follow up.

**`defaultPayload('id')`** -- called during onboarding when the customer is unverified and needs identity verification; creates a support ticket to trigger the ID check process.

**`defaultPayload('pSim')`** / **`defaultPayload('idAndPsim')`** -- called during onboarding when the customer has selected a physical SIM that hasn't been assigned an ICCID yet; requests SIM fulfilment with or without a combined ID check.

**`unverifiedPortabilityOrderPayload`** -- called when a portability order is placed but the customer's phone number verification failed; creates a ticket flagging the failed verification.

**`roamingPlanTicket`** -- called when a customer activates a roaming plan; creates an internal ticket instructing the team to issue a roaming-enabled eSIM.

**`payUpFrontPayload`** -- called when an upfront payment attempt fails during plan activation; creates a ticket for the customer success team.

**`needNewSimPayload`** -- called when a customer changes plan and the new plan requires a different SIM; creates a task ticket for the team to contact the customer and arrange a SIM swap.

**`cardAdditionFailed`** -- called when a card addition transaction fails; creates a ticket to alert the team.

**`paymentFailedPayload`** -- called when a recurring payment fails; creates an outbound-call task ticket for the team to chase payment.

**`getTicketFromSubject`** -- called before creating a `needNewSim` ticket to check whether one already exists for the customer, avoiding duplicates.
