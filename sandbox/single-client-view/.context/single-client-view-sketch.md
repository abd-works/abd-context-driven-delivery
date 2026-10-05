fidelity: story_map / model
evidence: intended — user message 2026-10-05
source: sandbox/single-client-view/.context/emil;-discussion.,txtx (open questions only; no answers yet)

=========
theme: View Client
---------
stories:
View Client < scaffold
    * approx — one display story per perspective × system × bank < scaffold
    Render Client Dashboard
        Call Center --> Render Client Dashboard
    Display Client Perspective
        Call Center --> Display {Bank} {System} Prospect < scaffold
        Call Center --> Display {Bank} {System} Onboarding < scaffold
        Call Center --> Display {Bank} {System} Subscription < scaffold
        Call Center --> Display {Bank} {System} Active Account < scaffold
        * approx — another display story for every other perspective on a bank-specific system < scaffold
        // display only; bank names and system names still unknown
    Integrate Client System
        * approx — one integration story per system, separate from display < scaffold
        * approx — further call-out stories when a perspective must be called out beyond display < scaffold
ce:
Client < scaffold
ClientPerspective < scaffold
Bank < scaffold
System < scaffold
Product < scaffold
// "services" is a source word; property or subtype of Product, not a second class yet
// Bank and System are both source words; whether a bank is a system is unresolved

=========
theme: Cross Sell Products
---------
stories:
Cross Sell Products < scaffold
    * approx 4–7 total stories < scaffold
    View Upsell Opportunity < scaffold
        Call Center --> View Upsell Opportunity < scaffold
        * approx 2–4 more stories (other operational features; products and services) < scaffold
ce:
UpsellOpportunity < scaffold
// opportunity is shown while the call center is on with the client; trigger detail waits

=========
theme: Understand Client Demographics
---------
stories:
Understand Client Demographics < scaffold
    * approx 3–5 total stories < scaffold
    View Client Demographics < scaffold
        Call Center --> View Client Demographics < scaffold
        * approx 2–4 more stories < scaffold
ce:
// demographics stays on Client until it owns a rule of its own

=========
theme: Feed Sales Force
---------
stories:
Feed Sales Force < scaffold
    * approx 3–5 total stories < scaffold
    Receive Upsell Opportunity < scaffold
        Sales Force --> Receive Upsell Opportunity < scaffold
        * approx 2–4 more stories < scaffold
ce:
SalesForce < scaffold
// domain depends on the sales-force contract; the contract does not depend on Client
