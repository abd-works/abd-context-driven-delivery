fidelity: story_map / model
evidence: intended — user message 2026-10-05
source: sandbox/single-client-view/.context/emil;-discussion.,txtx (open questions only; no answers yet)

=========
theme: View Client
---------
stories:
View Client
    Render Client Dashboard
        Call Center --> Render Client Dashboard
    Display PC Bank Client
        Call Center --> Display PC Bank Prospect
        Call Center --> Display PC Bank Onboarding Retail Deposits
        Call Center --> Display PC Bank Onboarding Business Banking
        Call Center --> Display PC Bank Onboarding International Banking
        Call Center --> Display PC Bank Account Retail Deposits
        Call Center --> Display PC Bank Account Business Banking
        Call Center --> Display PC Bank Account International Banking
        // prospect system name unknown
    Display EQ Bank Client
        Call Center --> Display EQ Bank Prospect
        Call Center --> Display EQ Bank Onboarding Retail Deposits
        Call Center --> Display EQ Bank Onboarding Business Banking
        Call Center --> Display EQ Bank Onboarding International Banking
        Call Center --> Display EQ Bank Account Retail Deposits
        Call Center --> Display EQ Bank Account Business Banking
        Call Center --> Display EQ Bank Account International Banking
        // prospect system name unknown
    Integrate PC Bank System
        Single Client View --> Integrate PC Bank Prospect
        Single Client View --> Integrate PC Bank Onboarding Retail Deposits
        Single Client View --> Integrate PC Bank Onboarding Business Banking
        Single Client View --> Integrate PC Bank Onboarding International Banking
        Single Client View --> Integrate PC Bank Account Retail Deposits
        Single Client View --> Integrate PC Bank Account Business Banking
        Single Client View --> Integrate PC Bank Account International Banking
    Integrate EQ Bank System
        Single Client View --> Integrate EQ Bank Prospect
        Single Client View --> Integrate EQ Bank Onboarding Retail Deposits
        Single Client View --> Integrate EQ Bank Onboarding Business Banking
        Single Client View --> Integrate EQ Bank Onboarding International Banking
        Single Client View --> Integrate EQ Bank Account Retail Deposits
        Single Client View --> Integrate EQ Bank Account Business Banking
        Single Client View --> Integrate EQ Bank Account International Banking
        // further call-out stories stay out until a perspective must be called out beyond display
ce:
Client
  render
       -> System.display
Bank
  system
  // instances: PC Bank, EQ Bank
System
  perspective
  line
  display
  integrate
  // perspective: prospect | onboarding | account
  // prospect: one system per bank; system name unknown; no line
  // onboarding and account: one system per line — retail deposits, business banking, international banking
  // line is a property; retail deposits, business banking, and international banking are not classes
  // PC Bank and EQ Bank are instances, not subtypes

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
