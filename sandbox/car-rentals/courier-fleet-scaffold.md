# Courier Fleet Service Discovery Sketch (MVP)

Date: 2026-09-09
Stage: Discoverer
Fidelity: Discovery

## Scope

This discovery pass defines the overall solution design for a courier platform that supports:
- direct user package delivery requests,
- retailer-originated requests forwarded into the platform,
- fleet dispatch, pickup, dropoff, and proof-of-delivery.

Operating assumptions:
- Single city, one depot, MVP-first.
- Same-day and next-day delivery are the target service classes.
- Requests must pass normalization before they can be dispatched.
- Proof-of-delivery is mandatory for order close-out.

Out of scope for this discovery pass:
- multi-city planning,
- route optimization beyond simple assignment heuristics,
- final billing/revenue recognition,
- deep legal/compliance workflows.

## Active Lenses

- Stories
- DDD
- UX
- Clean Engineering (modules)

## Discovery Decisions

### 1) Core operating model

The system has one dominant lifecycle for both direct and retailer flows:
- capture request,
- normalize request,
- quote/confirm,
- assign to vehicle and driver,
- execute pickup,
- complete delivery,
- capture proof,
- close order with exception handling where needed.

This keeps the service model consistent across channels and avoids creating separate delivery paths for each source.

### 2) Two inbound channels share one internal order

Direct user orders and forwarded retailer orders both become the same internal concept: a DeliveryOrder. The distinction matters only at the boundary:
- direct orders come from a customer UI or API,
- retailer orders come from inbound adapters or forwarded batches,
- both enter the same normalization and dispatch pipeline.

This means the internal domain language should not split around channel type once the request is accepted.

### 3) Normalization is the true gate to dispatch eligibility

The discovery decision is that normalization is not just validation; it is a first-class domain process. Before an order is eligible for dispatch, it must satisfy:
- sender and recipient details are valid,
- parcel details are interpretable,
- pickup/dropoff windows are understood,
- service level and pricing assumptions are derived,
- retailer-specific metadata has been mapped to canonical field names.

If normalization fails, the order stays in a review / remediation state rather than entering dispatch.

### 4) One depot, one city, one assignment arena

Given the MVP, assignment and fleet operations are city-scoped and effective only within the single depot operating model. The platform should not model multi-city route optimization in this pass.

Dispatch therefore owns simple assignment logic, assignment exceptions, and manual override controls; route optimization is a deliberate later concern.

## Stories Discovery

### Primary user journeys

1. Direct order flow
   - Customer creates delivery request
   - System quotes or confirms service window
   - Order is normalized
   - Driver/vehicle are assigned
   - Pickup occurs
   - Delivery occurs
   - POD is captured
   - Order closes

2. Retailer forwarding flow
   - Retailer pushes or emails order into the platform
   - Adapter ingests the payload
   - System normalizes and maps retailer data
   - Order enters assignment queue
   - Dispatch and execution proceed like direct orders
   - Reconciliation and exceptions are tracked for source-specific discrepancies

3. Failure and retry flow
   - Failed pickup or delivery creates an exception
   - Order is re-assigned or rescheduled
   - System reopens delivery execution without losing the original request identity
   - Proof is still required before final close

### Story map (discovery-level)

Epics and candidate story groups:

- Intake and Capture
  - Capture Direct Request
  - Capture Retailer Forwarded Request
  - Record Request Metadata

- Normalize Inbound Orders
  - Validate Request Completeness
  - Map Retailer Data to Canonical Fields
  - Resolve Service Window and Service Level
  - Flag Normalization Exceptions

- Quote and Confirm
  - Estimate Delivery Window
  - Present Quote to Sender
  - Confirm Order Before Dispatch

- Dispatch and Assignment
  - Place Order in Dispatch Queue
  - Select Candidate Driver and Vehicle
  - Create Assignment
  - Reassign or Override Assignment

- Pickup Execution
  - Confirm Pickup at Source
  - Record Pickup Status
  - Update Tracking Session

- Delivery Execution
  - Confirm Dropoff at Destination
  - Record Delivery State
  - Trigger Exception Handling on Failed Delivery

- Proof of Delivery
  - Capture Photo/Signature/Geo Evidence
  - Validate POD Completeness
  - Close Delivery Order

- Exceptions and Reattempts
  - Manage Failed Pickup
  - Manage Failed Delivery
  - Requeue or Reschedule Order
  - Escalate to Manual Resolution

- Notifications and Tracking
  - Send Order Confirmation
  - Send Pickup Status Update
  - Send Arrival and Delivery Updates
  - Surface Tracking to Sender and Retailer

- Retailer Forwarding Reconciliation
  - Reconcile Forwarder Status
  - Review Mapping/Normalization Errors
  - Resolve Source-Specific Mismatch

## DDD Discovery

### Bounded contexts

Request Intake
- Aggregate: DeliveryOrder
- Responsibilities:
  - own request lifecycle,
  - create and update canonical request state,
  - publish normalized order events,
  - carry fulfillment status and proof status.
- Emits:
  - RequestCaptured
  - OrderNormalized
  - DeliveryCompleted
  - DeliveryFailed
- Consumes:
  - ForwardingIngested

Channel Adapters
- Aggregate: ChannelForwardBatch
- Responsibilities:
  - absorb retailer inbound payloads,
  - normalize source contract differences,
  - emit a canonical forward event for intake.
- Emits:
  - ForwardingIngested

Dispatch
- Aggregate: Assignment
- Responsibilities:
  - convert a normalized order into a dispatchable assignment,
  - track driver/vehicle assignment and manual overrides,
  - publish assignment and reschedule events.
- Emits:
  - AssignmentCreated
  - AssignmentReopened
- Consumes:
  - OrderNormalized
  - DeliveryFailed

Fleet Operations
- Aggregate: Vehicle
- Aggregate: DriverShift
- Responsibilities:
  - maintain active fleet availability,
  - track shift coverage and assignment eligibility,
  - provide operational readiness signals for assignment.
- Consumes:
  - AssignmentCreated

Tracking and Notifications
- Aggregate: TrackingSession
- Aggregate: ProofOfDelivery
- Responsibilities:
  - maintain visibility through route execution,
  - accumulate proof evidence,
  - publish delivery/notification state.
- Emits:
  - ProofCaptured
- Consumes:
  - AssignmentCreated
  - PickupCompleted
  - DeliveryCompleted
  - DeliveryFailed

### Cross-context event map

- RequestCaptured
  - emitted by DeliveryOrder
  - consumed by the intake process and internal validation steps

- ForwardingIngested
  - emitted by ChannelForwardBatch
  - consumed by DeliveryOrder to begin canonical normalization

- OrderNormalized
  - emitted by DeliveryOrder
  - consumed by Assignment

- AssignmentCreated
  - emitted by Assignment
  - consumed by Fleet Operations, TrackingSession, and route execution

- PickupCompleted
  - emitted by route execution or dispatch state machine
  - consumed by TrackingSession and downstream execution monitoring

- DeliveryCompleted
  - emitted by order lifecycle when dropoff succeeds
  - consumed by TrackingSession, ProofOfDelivery, and deferred settlement logic

- DeliveryFailed
  - emitted by order lifecycle when execution fails
  - consumed by Assignment and TrackingSession

- ProofCaptured
  - emitted by ProofOfDelivery
  - consumed by settlement or reconciliation processing

### Ubiquitous language

- DeliveryOrder
- ForwardedRequest
- NormalizationException
- Assignment
- DriverShift
- Vehicle
- TrackingSession
- ProofOfDelivery
- Reschedule
- ManualOverride
- Depot
- ServiceWindow
- POD

## UX IA Discovery

### Sender-facing screens

- Create Delivery Request
- Quote and Confirm
- Live Tracking
- Delivery History
- Support and Exception View

### Dispatcher-facing screens

- Unassigned Queue
- Assignment Board
- Fleet Availability Board
- Active Deliveries Map
- Exception Queue
- Reassignment / Manual Override Panel

### Driver-facing screens

- Assigned Stops
- Pickup Confirmation
- Delivery Confirmation
- Proof-of-Delivery Capture
- Delivery Exception Reporting

### Retailer operations screens

- Forwarded Requests Inbox
- Mapping and Normalization Errors
- Reconciliation Overview
- Rejected or Delayed Orders

### Key navigation flow

Customer or retailer submits request -> request enters intake -> normalized order view -> quote/confirm -> assignment board -> pickup driver view -> delivery and POD -> tracking closed event.

That flow is common to both channels, with retailer operations gaining a secondary review path for inbound mapping and reconciliation issues.

## Clean Engineering Discovery

### Candidate modules

- module-intake
- module-channel-adapters
- module-order
- module-dispatch
- module-fleet
- module-tracking
- module-notifications
- module-settlement
- module-shared-kernel

### Public seams

- IntakePort
- ForwardingIngestPort
- OrderNormalizationPort
- DispatchPolicyPort
- AssignmentPort
- FleetStatusPort
- TrackingPort
- NotificationPort
- PODCapturePort

### Dependency direction

- channel-adapters -> intake
- intake -> order
- order -> dispatch
- dispatch -> fleet
- fleet -> tracking
- tracking -> notifications
- settlement depends on order + tracking summaries

### Module design intent

- Intake owns captured request creation and canonical request state.
- Channel adapters own source-specific translation only.
- Order module owns normalization and order lifecycle decisions.
- Dispatch owns assignment and reschedule policy.
- Fleet owns operational readiness and shift constraints.
- Tracking owns state visibility and POD evidence accumulation.
- Notifications own user-facing delivery updates.
- Settlement remains deferred/limited in MVP scope, but should not own the operational decision path.

## Integration Discovery

### Adapter types

- Retailer API/Webhook adapter
- Email parser adapter
- Web UI intake adapter

### Canonical inbound envelope

- externalOrderRef
- sender
- recipient
- parcelDetails
- pickupWindow
- dropoffWindow
- serviceLevel
- sourceChannel
- orderStatus

This envelope is the discovery-level contract between adapters and the intake/normalization flow.

## Assumptions locked at discovery

- Same-day and next-day service windows are in scope.
- Normalization is a required gating step before assignment eligibility.
- Manual override is allowed in assignment decisions.
- Proof-of-delivery is required to close an order.
- Retailer-originated orders are first-class but not separate operationally once normalized.

## Open questions for next roles

### Discoverer follow-ups

- Which service-level promises are guaranteed in MVP, and how do they differ by pickup/dropoff window?
- Which retailer channels are targeted in phase 1 versus later phases?
- What is the primary exception policy for failed delivery, wrong-address, and damaged parcel cases?

### Specifier follow-ups

- What are the exact assignment rules, override triggers, and reassignment transitions?
- What does the POD contract include: photo, signature, geolocation, timestamp, or a combination?
- What canonical error taxonomy will the normalization process return?

### Implementer follow-ups

- What adapter implementation order is safest and least risky?
- What observability, alerting, and retry strategy should cover intake, normalization, and assignment failures?

## Handoff Direction

Recommended next role: Discoverer or Specifier

Preferred next area to refine:
- intake + normalization flow for direct and retailer-forwarded requests, including canonical errors and resubmission behavior.

This discovery sketch intentionally leaves tactical details for specification and implementation, but it locks the core shape of the courier platform: one shared order lifecycle, one normalization gate, one depot assignment model, and mandatory POD closure.
