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

## Grill Decision Locked

Decision: direct and retailer requests share one normalized DeliveryOrder lifecycle after intake.

Rationale:
- The platform should have one operational delivery model rather than two parallel internal implementations.
- Channel differences remain at the adapter and intake boundary.
- Dispatch, execution, tracking, and proof-of-delivery should operate on one canonical order state.

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

### 2) Two inbound channels share one internal order

Direct user orders and retailer-forwarded orders both become the same internal concept: DeliveryOrder.

The distinction matters only at the boundary:
- direct orders originate from customer UI or API,
- retailer orders originate from adapters or forwarded batches,
- both enter the same normalization and dispatch pipeline.

### 3) Normalization is the true gate to dispatch eligibility

Before an order is dispatchable, it must pass normalization:
- sender and recipient details are valid,
- parcel details are interpretable,
- pickup/dropoff windows are understood,
- service level and pricing assumptions are derived,
- retailer metadata is mapped to canonical fields.

If normalization fails, the order remains in a review/remediation state rather than entering dispatch.

### 4) One depot, one city, one assignment arena

Given the MVP, assignment and fleet operations are city-scoped and effective only within the single depot model. Route optimization is intentionally deferred.

Dispatch owns simple assignment logic, manual override controls, and exception handling.

## Stories Discovery

### Primary user journeys

1. Direct order flow
   - Customer creates delivery request
   - System quotes or confirms service window
   - Order is normalized
   - Driver and vehicle are assigned
   - Pickup occurs
   - Delivery occurs
   - POD is captured
   - Order closes

2. Retailer forwarding flow
   - Retailer pushes or emails order into the platform
   - Adapter ingests payload
   - System normalizes and maps retailer data
   - Order enters assignment queue
   - Dispatch and execution proceed like direct orders
   - Reconciliation tracks source-specific discrepancies

3. Failure and retry flow
   - Failed pickup or delivery creates an exception
   - Order is reassigned or rescheduled
   - System reopens delivery execution without losing request identity
   - Proof remains required before final close

### Story map (discovery-level)

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
- Emits: RequestCaptured, OrderNormalized, DeliveryCompleted, DeliveryFailed
- Consumes: ForwardingIngested

Channel Adapters
- Aggregate: ChannelForwardBatch
- Emits: ForwardingIngested

Dispatch
- Aggregate: Assignment
- Emits: AssignmentCreated, AssignmentReopened
- Consumes: OrderNormalized, DeliveryFailed

Fleet Operations
- Aggregate: Vehicle
- Aggregate: DriverShift
- Consumes: AssignmentCreated

Tracking and Notifications
- Aggregate: TrackingSession
- Aggregate: ProofOfDelivery
- Emits: ProofCaptured
- Consumes: AssignmentCreated, PickupCompleted, DeliveryCompleted, DeliveryFailed

### Cross-context event map

- RequestCaptured
  - emitted by DeliveryOrder
  - consumed by intake validation and order lifecycle steps

- ForwardingIngested
  - emitted by ChannelForwardBatch
  - consumed by DeliveryOrder for canonical normalization

- OrderNormalized
  - emitted by DeliveryOrder
  - consumed by Assignment

- AssignmentCreated
  - emitted by Assignment
  - consumed by fleet readiness, tracking, and route execution

- PickupCompleted
  - emitted during route execution
  - consumed by TrackingSession

- DeliveryCompleted
  - emitted when dropoff succeeds
  - consumed by TrackingSession, ProofOfDelivery, and later settlement logic

- DeliveryFailed
  - emitted when execution fails
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

## Intake + Normalization Flow Discovery

### Flow

1. External request enters via customer UI, retailer API, or email ingestion.
2. Source adapter converts it into the canonical inbound envelope.
3. Intake captures a DeliveryOrder with source metadata and request identity.
4. Normalization validates and maps parcel, timing, and address data to the internal model.
5. Normalization emits either a normalized order or a review exception.
6. Dispatchable orders move to assignment, while failed or incomplete orders remain in exception review.

### States in the flow

- DraftRequest
- Ingested
- Captured
- AwaitingNormalization
- Normalized
- NormalizationException
- AwaitingAssignment
- Assigned
- PickupCompleted
- Delivered
- PODCaptured
- Closed

### Domain responsibilities

- Channel adapters own source-specific translation and payload reliability.
- Intake owns capture and canonical record creation.
- Order normalization owns completeness checks, canonical mapping, service window translation, and exception creation.
- Dispatch owns eligibility for assignment after normalization succeeds.
- Tracking owns state visibility across execution.

### Why this branch matters

This is the critical seam for the MVP. Most operational risk sits here:
- inconsistent retailer payload shapes,
- missing parcel details,
- invalid pickup/dropoff windows,
- partial requests that cannot be dispatched safely.

The design decision is that these problems are not hidden in dispatch; they are surfaced at normalization and triaged explicitly.

## Assumptions locked at discovery

- Same-day and next-day service windows are in scope.
- Normalization is a required gating step before assignment eligibility.
- Manual override is allowed in assignment decisions.
- Proof-of-delivery is required to close an order.
- Retailer-originated orders are first-class but not separate operationally once normalized.

## Open Questions for Next Roles

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

Recommended next role: Specifier or Discoverer

Preferred next area to refine:
- intake + normalization flow for direct and retailer-forwarded requests, including canonical errors and resubmission behavior.

This discovery sketch intentionally leaves tactical details for specification and implementation, but it locks the core design: one shared order lifecycle, one normalization gate, one depot assignment model, and mandatory POD closure.
