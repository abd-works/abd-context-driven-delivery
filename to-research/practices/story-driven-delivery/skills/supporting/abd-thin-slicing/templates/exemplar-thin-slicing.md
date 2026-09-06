# Thin slicing — PawPlace incremental backlog  

## Product / context  

**Product:** PawPlace — online pet store with in-store adoption visits.  

**Slicing intent (by value, store-first):** Each increment must put a working capability in the hands of a real store. Earlier increments deliberately leave out polish, payment depth, accounts, pets, returns, and marketing so that a store gets a usable product on day one and revenue/learning compounds with each release. *Pet appointments* — the adoption side — are explicitly held back until the e-commerce spine is real.  

**Spine vs optional:** The mandatory commerce spine is **catalog → store → cart → pay → fulfill**. Pets, accounts, multi-vendor payments, returns, marketing, reviews, and admin polish are real work but **not** required for the smallest store-supporting slice; they ride later increments.  

## Increments  

### Increment 1: `Walk-in driver — find the store, see what's in stock`  

**Outcome:** A customer can find their nearest *store*, browse the *product catalog*, see *real-time stock availability* for a product at that store, and walk in to ask for it. Drives foot traffic with zero checkout, payment, or accounts infrastructure. Store gets value on day one.  

**Slicing notes:** Single payment-free, account-free vertical slice. Manual stock updates by staff via a bare-bones admin form. Categories only — no keyword search yet. No cart, no checkout, no notifications. Validates the *catalog* data model, the *store* + geo model, the *stock availability* contract, and that customers find this useful enough to walk in. Risk validated: real customer traffic to real stores. Per the domain decision, **walk-in point-of-sale (paying at the counter) is in scope for a later phase** — it requires POS integration and a `point-of-sale` concept under Store. Today the walk-in capability is "find it, see it's in stock, walk in"; the in-store transaction itself is the customer talking to a staff member, not the system.  

**Stories in this increment** *(order reflects flow within the slice):*  

- *View Store Map* — customer opens map of stores  
- *View Store List* — customer sees a list of stores  
- *Calculate Distance to Store* — customer enters postcode or shares location  
- *View Product Details* — customer opens a product page  
- *Display Real-Time Stock Availability* — system shows whether the product is in stock at a given store  
- *Update Product Stock Levels* (store employee, manual) — front-line staff edit stock  

---  

### Increment 2: `Click-and-collect — buy online, pick up at the store`  

**Outcome:** A customer can put products in a *shopping cart*, pay online with a card, and pick the order up at a chosen *store*. The store gets online revenue without anyone solving home-delivery logistics. Single payment vendor (StripeWave) so the integration is real but bounded.  

**Slicing notes:** *Guest checkout* only — no accounts yet. Single payment vendor. Confirmation email from a static template. No shipping address, no delivery option fan-out — pickup is the only fulfillment path. Manual pick-prep by store staff. Validates the riskiest payment integration on a real card-present journey end-to-end.  

**Stories in this increment:**  

- *Add Product to Cart*  
- *Update Cart Quantity*  
- *Remove Product from Cart*  
- *Select Click-and-Collect Store*  
- *Check Out as Guest*  
- *Enter Billing Address*  
- *Select Payment Method* (StripeWave only at this point)  
- *Process Card Payment via StripeWave*  
- *Confirm Order and Send Confirmation Email*  
- *Prepare Click-and-Collect Orders for Pickup* (store employee)  
- *Fulfill Click-and-Collect Order* (store employee)  

---  

### Increment 3: `Ship to home — full standard-delivery e-commerce`  

**Outcome:** A customer can complete the same purchase journey but have it **shipped** to a delivery address. Standard delivery only. Now the store reaches customers outside its catchment.  

**Slicing notes:** Still *guest checkout*, still StripeWave-only. Standard delivery only — defer express and same-day. Manual shipping label creation by staff. Validates the order lifecycle past pickup: shipping notifications, tracking, and an order-status view.  

**Stories in this increment:**  

- *Enter Shipping Address*  
- *Select Delivery Option* (standard only)  
- *View and Process Incoming Orders* (store employee)  
- *Send Shipping Notification with Tracking Number*  
- *Track Order Status*  

---  

### Increment 4: `Returning customers — accounts, history, reorder`  

**Outcome:** Customers can register, log in, save addresses and payment methods, see their *order history*, manage a *wishlist*, and one-click reorder. Account creation is prompted during guest checkout. Lifts repeat-purchase rate without changing the buy flow.  

**Slicing notes:** Email + password only — no social login. *Email verification* mandatory. Reliable session management across devices is a non-negotiable per the *customer account* invariants. No password-strength theatre — just solid basics. *Saved address* and *saved payment method* land here as concepts (per the domain decision), so the checkout gains the option to pick from saved entities for logged-in customers.  

**Stories in this increment:**  

- *Register Account*  
- *Send Email Verification*  
- *Verify Email Address*  
- *Log In*  
- *Log Out*  
- *Reset Password*  
- *Maintain Session Across Devices*  
- *Save Delivery Address*  
- *Manage Saved Addresses*  
- *Save Payment Method*  
- *Manage Saved Payment Methods*  
- *Select Saved Address at Checkout*  
- *Select Saved Payment Method at Checkout*  
- *View Order History*  
- *Manage Wishlist*  
- *Reorder Previous Purchase*  

---  

### Increment 5: `Pay your way — multi-vendor payment with retries`  

**Outcome:** Customers can pay with *PayNova* (mobile wallet) and *VaultPay* (buy-now-pay-later) in addition to *StripeWave*. Failed payments retry automatically across all three. Lifts conversion among younger buyers and basket-size on premium items.  

**Slicing notes:** Proves the *payment vendor* abstraction generalises beyond StripeWave. Webhook handling and failed-payment retries across all three vendors land here together because they share the same operational surface. Refund routing is in scope so Increment 7 can build cleanly.  

**Stories in this increment:**  

- *Process Digital Wallet Payment via PayNova*  
- *Process Buy-Now-Pay-Later via VaultPay*  
- *Retry Failed Payment*  

---  

### Increment 6: `Pet visits — gallery and in-store appointments`  

**Outcome:** The adoption side goes live. Customers browse the *pet* gallery, see which *store* a pet is at and how far away it is, and book an *appointment* to visit. Store staff see incoming bookings, check customers in, record visit outcomes, handle no-shows, and set follow-up actions. Pet status (available/adopted) is admin-managed.  

**Slicing notes:** Held back until now per the explicit guidance that *pet appointments* can be later. The *appointment* confirmation and day-before reminder ride on the transactional notification rails added in Increment 4 (or land here together with this slice if Increment 4 didn't include them — see Increment 8). Single-store flow first if multi-store appointment scheduling is too complex; otherwise multi-store from the start. Per the domain decision, *appointment* booking is **customer-account-only** — guest checkout cannot book; an account-gate is part of the `Confirm Appointment Booking` AC. The *pet adopted before visit* notification + the customer-side `Cancel or Rebook` flow ride here too because they're inseparable from the appointment lifecycle.  

**Stories in this increment:**  

- *Browse Pets by Species*  
- *View Pet Profile*  
- *View Pet Store Location and Distance*  
- *View Available Time Slots at Store*  
- *Select Date and Time Slot*  
- *Add Visit Note*  
- *Confirm Appointment Booking* (account-gated)  
- *View Upcoming and Past Appointments* (customer)  
- *Cancel or Rebook Appointment After Pet Adoption* (customer)  
- *Update Pet Profile* (store employee)  
- *Mark Pet as Adopted* (store employee)  
- *View Incoming Appointments* (store employee)  
- *Check In Customer* (store employee)  
- *Record Visit Outcome* (store employee)  
- *Record No-Show* (store employee)  
- *Set Follow-Up Action* (store employee)  
- *Send Appointment Reminder* (transactional)  
- *Send Pet Adopted Before Visit Notification* (transactional)  
- *Send Visit Follow-Up Notification* (transactional)  

---  

### Increment 7: `Returns and refunds — close the loop`  

**Outcome:** Customers can initiate a *return* from their *order* history, get a printable label or QR code, and watch the *refund* land back on their original payment method. In-store returns are reflected in the customer's account too.  

**Slicing notes:** The vendor-routing invariant on *refund* is the design rule that drives this slice — refund must always route through the vendor that took the original payment, regardless of which vendor mix the customer has used since. Online return flow first; in-store return reconciliation second.  

**Stories in this increment:**  

- *Initiate Return from Order History*  
- *Generate Return Label or QR Code*  
- *Route Refund through Original Payment Vendor*  
- *Track Refund Status*  
- *Process In-Store Return* (store employee)  
- *Send Return and Refund Status Update* (transactional)  

---  

### Increment 8: `Marketing engine — reviews, alerts, and content`  

**Outcome:** Drives repeat traffic and conversion through *customer review* social proof, opt-in marketing emails, *restock alert* nudges, personalised recommendations, and a content stream of blog posts and pet care guides. Engagement features only — the buy flow is unchanged.  

**Slicing notes:** Marketing notifications must respect the explicit-opt-in invariant on *communication preferences* — no broadcast without opt-in for that category. Transactional notifications added in earlier increments stay independent of marketing rails. Content publishing is admin-only at first.  

**Stories in this increment:**  

- *Submit Written Review with Star Rating*  
- *Submit Photo Review*  
- *Read Customer Reviews*  
- *Set Notification Preferences*  
- *Set Communication Preferences*  
- *Opt In to Marketing Email List*  
- *Send Promotional Email*  
- *Send Personalized Recommendation*  
- *Send Restock Alert*  
- *Send In-Store Event Notification*  
- *Unsubscribe from Marketing Emails*  
- *Send Click-and-Collect Ready Notification* (transactional — notify customer when their order is ready for pickup)  
- *Send Order Confirmation* *(if not delivered earlier as part of Increment 2's confirmation email)*  
- *Send Shipping Update with Tracking* *(if not delivered earlier as part of Increment 3)*  
- *Publish Blog Post*  
- *Publish Pet Care Guide*  

---  

### Increment 9: `Power-ups — search, personalization, admin polish`  

**Outcome:** Smart search lifts conversion on a deep catalog; store personalization and customer pet profiles tighten loyalty; the admin inventory dashboard replaces the bare-bones stock form from Increment 1. Polish layer over a fully-functional product.  

**Slicing notes:** Each story here adds value but none is required for the core commerce or adoption journeys. Sequence within the increment follows whichever stakeholder pulls hardest — search and inventory dashboard typically pay back first.  

**Stories in this increment:**  

- *Search Products by Keyword*  
- *Filter Products*  
- *Display Low Stock Badge* (customer-facing low-stock indicator on product listings)  
- *Allow Backorder Purchase* (let customers buy out-of-stock products with backorder enabled)  
- *Filter Stores by Availability and Specialization*  
- *Set My Store Preference*  
- *Tailor Experience to Preferred Store*  
- *Create Pet Profile* (customer's own pets — distinct from the store's *Pet* concept)  
- *Update Pet Profile* (customer's own)  
- *View Inventory Dashboard* (store owner)  
