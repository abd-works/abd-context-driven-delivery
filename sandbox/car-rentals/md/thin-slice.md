---
fidelity: [discovery]
artifact: [thin-slice]
format: md
section: body
---

# Thin slicing — Courier Fleet Service incremental backlog

## Product / context

**Product:** Courier fleet platform for same-day and next-day package delivery in one city from one depot — direct customer requests and retailer-forwarded batches share one DeliveryOrder lifecycle.

**Slicing intent:** Prove the walking skeleton on the direct channel first (capture → normalize → quote → assign → pickup → deliver → POD → close). Add retailer forwarding once the shared pipeline works. Layer exceptions, notifications breadth, and retailer reconciliation after the spine is demonstrable.

**Spine vs optional:** The mandatory spine is **submit request → normalize → quote/confirm → assign → pickup → deliver → capture POD → close**. Retailer batch ingestion, partial-batch rejection, dispatcher escalation depth, notification fan-out, and forwarder reconciliation are real work but not required for the smallest marketable slice.

## Increments

### Increment 1: Direct request through normalization gate

**Outcome:** A customer can submit a direct delivery request and the platform normalizes it to a dispatch-eligible DeliveryOrder or returns coded remediation errors.

**Slicing notes:** Single city, single depot. Direct UI only — no retailer adapter. Manual dispatcher review for normalization exceptions. No quote, assignment, or execution yet. Validates canonical envelope, normalization state machine, and error taxonomy from the sketch.

**Stories in this increment** *(order reflects flow within the slice):*

- *Submit Direct Delivery Request*
- *Record Delivery Request Metadata*
- *Validate Sender and Recipient Completeness*
- *Derive Service Window and Service Level*
- *Mark Delivery Order Normalized*
- *Review Normalization Exception*
- *Resubmit Corrected Request Details*
- *Reject Duplicate External Order Reference*

### Increment 2: Quote, confirm, and assign one delivery

**Outcome:** A normalized direct order can be quoted, confirmed, and assigned to a driver and vehicle using simple depot-scoped selection with manual override.

**Slicing notes:** Single assignment heuristic (no route optimization). Dispatcher can override or reassign. Still direct channel only.

**Stories in this increment:**

- *Estimate Delivery Window*
- *View Delivery Quote*
- *Confirm Delivery Order*
- *Place Order in Dispatch Queue*
- *Select Candidate Driver and Vehicle*
- *Create Manual Assignment*
- *Override Existing Assignment*

### Increment 3: Execute pickup, delivery, and proof-of-delivery

**Outcome:** An assigned driver completes pickup and delivery, captures POD evidence, and the platform closes the DeliveryOrder.

**Slicing notes:** Photo and signature POD both in scope per sketch. Failed pickup/delivery recorded but requeue deferred to Increment 4. Basic tracking session updates on pickup and delivery.

**Stories in this increment:**

- *Confirm Pickup at Source*
- *Update Tracking Session on Pickup*
- *Confirm Delivery at Destination*
- *Update Tracking Session on Delivery*
- *Capture Photo Proof of Delivery*
- *Capture Signature Proof of Delivery*
- *Validate Proof Completeness*
- *Close Delivery Order*

### Increment 4: Retailer forwarding and batch exceptions

**Outcome:** Retailer Ops can forward order batches through a channel adapter; accepted rows normalize into DeliveryOrders; rejected rows and mapping gaps are visible for remediation.

**Slicing notes:** One retailer adapter contract. Partial batch rejection and mapping-error stories. Reuses the normalization pipeline from Increment 1.

**Stories in this increment:**

- *Submit Forwarded Order Batch*
- *Ingest Retailer Payload Into Canonical Envelope*
- *Map Retailer Fields to Canonical Envelope*
- *Reject Partial Batch Rows*
- *Review Forwarded Batch Status*
- *Resolve Retailer Mapping Error*

### Increment 5: Exceptions, notifications, and reconciliation

**Outcome:** Failed execution can be requeued or rescheduled; stakeholders receive confirmation and status notifications; retailer forwarder status reconciles with platform state.

**Slicing notes:** Full exception and reattempt paths. Notification breadth beyond tracking-session updates. Forwarder reconciliation for retailer operations.

**Stories in this increment:**

- *Record Failed Pickup*
- *Record Failed Delivery Attempt*
- *Requeue Failed Delivery Order*
- *Reschedule Delivery Window*
- *Escalate to Manual Resolution*
- *Reassign Delivery Order*
- *Send Order Confirmation Notification*
- *Send Pickup Status Update*
- *Send Delivery Arrival Update*
- *View Live Delivery Tracking*
- *View Forwarded Order Tracking*
- *Reconcile Forwarder Status with Platform*
