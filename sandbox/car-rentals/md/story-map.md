---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Courier Fleet Service (MVP)

**Sources / context:** `sandbox/car-rentals/.context/courier-fleet-sketch.md`

---

(E) Manage Delivery Requests
    (E) Intake and Capture Requests
        (S) Customer --> Submit Direct Delivery Request
        (S) Retailer Ops --> Submit Forwarded Order Batch
        (S) Channel Adapter --> Ingest Retailer Payload Into Canonical Envelope
        (S) System --> Record Delivery Request Metadata
    (E) Normalize Inbound Orders
        (S) System --> Validate Sender and Recipient Completeness
        (S) Channel Adapter --> Map Retailer Fields to Canonical Envelope
        (S) System --> Derive Service Window and Service Level
        (S) System --> Mark Delivery Order Normalized
        (S) Dispatcher --> Review Normalization Exception
        (S) Customer --> Resubmit Corrected Request Details
        (S) System --> Reject Duplicate External Order Reference
        (S) System --> Reject Partial Batch Rows
    (E) Quote and Confirm Deliveries
        (S) System --> Estimate Delivery Window
        (S) Customer --> View Delivery Quote
        (S) Customer --> Confirm Delivery Order

(E) Dispatch Courier Fleet
    (E) Assign Drivers and Vehicles
        (S) System --> Place Order in Dispatch Queue
        (S) System --> Select Candidate Driver and Vehicle
        (S) Dispatcher --> Create Manual Assignment
        (S) Dispatcher --> Override Existing Assignment
        (S) Dispatcher --> Reassign Delivery Order

(E) Execute Delivery Route
    (E) Complete Pickup
        (S) Driver --> Confirm Pickup at Source
        (S) Driver --> Record Failed Pickup
        (S) System --> Update Tracking Session on Pickup
    (E) Complete Delivery
        (S) Driver --> Confirm Delivery at Destination
        (S) Driver --> Record Failed Delivery Attempt
        (S) System --> Update Tracking Session on Delivery
    (E) Prove and Close Delivery
        (S) Driver --> Capture Photo Proof of Delivery
        (S) Driver --> Capture Signature Proof of Delivery
        (S) System --> Validate Proof Completeness
        (S) System --> Close Delivery Order

(E) Recover from Delivery Exceptions
    (E) Reattempt Failed Execution
        (S) Dispatcher --> Requeue Failed Delivery Order
        (S) Dispatcher --> Reschedule Delivery Window
        (S) Dispatcher --> Escalate to Manual Resolution

(E) Inform Delivery Stakeholders
    (E) Send Delivery Notifications
        (S) System --> Send Order Confirmation Notification
        (S) System --> Send Pickup Status Update
        (S) System --> Send Delivery Arrival Update
    (E) Surface Delivery Tracking
        (S) Customer --> View Live Delivery Tracking
        (S) Retailer Ops --> View Forwarded Order Tracking

(E) Reconcile Retailer Forwarding
    (E) Resolve Retailer Source Issues
        (S) Retailer Ops --> Review Forwarded Batch Status
        (S) Retailer Ops --> Resolve Retailer Mapping Error
        (S) System --> Reconcile Forwarder Status with Platform

---

## Scope boundary

**In scope:** Single-city, single-depot courier operations; direct and retailer-forwarded intake; normalization gate before dispatch; same-day and next-day service levels; simple assignment with manual override; pickup, delivery, proof-of-delivery, and exception reattempts; sender and retailer tracking notifications.

**Out of scope:** Multi-city routing, route optimization beyond simple assignment heuristics, billing and revenue recognition, deep legal and compliance workflows.
