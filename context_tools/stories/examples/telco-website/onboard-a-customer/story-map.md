---
fidelity: [discovery]
artifact: [story-map]
format: md
example-of: story-map
---

# Story Map — Telco Website (slice)

Portion of **Onboard A Customer** — enough hierarchy to place the golden fixture example under Create Customer.

(E) Onboard A Customer
    (E) Get Sign Up Plan
        (S) Website --> Hand Off Sign Up To Onboarding
        (S) Prospect --> Open Plan Deep Link
        (S) Prospect --> Apply Catalog Voucher
    (E) Create Customer
        (E) Create Unconfirmed User
            (S) Prospect --> Enter Account Credentials
            (S) Identity Provider --> Create Unconfirmed User
        (E) Verify Account
            (S) Prospect --> Enter Validation Code
            (S) Identity Provider --> Confirm User
            (S) Identity Provider --> Issue Account Token To Browser Session
        (E) Create Customer
            (S) Website --> Submit Create Customer Request
            (S) Mid-Tier --> Create Billing Customer
        (E) Load Customer
            (S) Website --> Load Customer Into Session
