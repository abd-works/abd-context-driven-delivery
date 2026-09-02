---
fidelity: [discovery]
artifact: [story-map]
format: md
---

# Story Map — Paradise Mobile consumer (front end + system hops)

**Base:** `.context/nico-chat/.context/story-map.md` — every existing line kept.

**Added from:** `.context/nico-chat/nico-chat.md`, `nico-chat 4.md`, `inventory.md`, `subscription.md`; `.context/granola-notes/` (screenshot-wall, weird-stuff, onboarding-flow, onboarding-flow-walkthrough); `pml-my` Amplify Cognito + `useLoggedUser`; `pml-website` Sign up handoff.

Front-end stories are the Prospect/Customer lines in My Paradise. Display and forward stays on the user story. A My Paradise hop is when it validates or decides. Other system hops name what happens to the information.

---

(E) Onboard A Customer
    (E) Get Sign Up Plan
        (S) Website --> Hand Off Sign Up To Onboarding
        (S) Prospect --> Open Plan Deep Link
        (S) Midtier --> Query Product Offerings
        (S) Mavenir --> List Product Offerings
        (S) Midtier --> Map Product Offerings To Catalog
        (S) Prospect --> Apply Catalog Voucher
        (S) Midtier --> Query Voucher
        (S) Vouchera --> Validate Voucher
    (E) Create Customer
        (E) Create Unconfirmed User
            (S) Prospect --> Enter Account Credentials
            (S) Cognito  --> Create Unconfirmed Cognito User
        (E) Verify Account
            (S) Prospect --> Enter Validation Code
            (S) Cognito  --> Confirm Cognito User
            (S) Cognito  --> Issue Account Token To Browser Session
        (E) Create Customer
            (S) My Paradise/Cognito --> Validate Mavenir Customer in Cognito User Attributes  
            (S) My Paradise --> Submit Create Customer Request to Mid-Tier
            (S) Midtier --> Validate Cognito User 
            (S) Midtier --> Submit Create Mavenir Customer
            (S) Mavenir --> Create Customer
            (S) My Paradise/Cognito --> Store Mavenir Customomer Id on Cognito User
         (E) Load Customer
            (S) My Paradise --> Load My Paradise Customer From Midtier And Store In Session
            (S) Midtier --> Get Mavenir Customer and Transform To My Paradise Customer And Return
            (S) Mavenir --> Get Mavenir Customer
        (E) Support Account Creation
            (S) Care --> Fix Orphan Cognito Account
            (S) Care --> Read False Initial Activation
     (E) Sign In With Existing Account
        (S) Prospect --> Enter Sign In Credentials
        (S) Cognito  --> Authenticate Cognito User
        (S) Cognito  --> Issue Token To Browser Session
    (E) Create Empty Cart
        (S) My Paradise --> Validate Mavenir Shopping Cart on My Paradise Customer
        (S) My Paradise --> Submit Create Cart Request to Mid-Tier
        (S) Midtier --> Validate Cognito User
        (S) Midtier --> Submit Create Mavenir Shopping Cart
        (S) Mavenir --> Create Shopping Cart
        (S) My Paradise --> Store Cart Id on My Paradise Customer in Session
    (E) Get Number
        (E) Get New Number
            (S) Prospect --> Determine Number
            (S) Midtier --> Query Msisdn Inventory
            (S) Mavenir --> List Msisdn Resources
            (S) Midtier --> Search Msisdn Inventory
            (S) Mavenir --> Search Msisdn Resources
            (S) Prospect --> Choose a Number
            (S) My Paradise --> Submit Reserve Number Request to Mid-Tier
            (S) Midtier --> Submit Reserve Msisdn
            (S) Mavenir --> Reserve Msisdn Resource
            (S) My Paradise --> Submit Patch Cart With Number Request to Mid-Tier
            (S) Midtier --> Patch Cart With Number
            (S) Mavenir --> Patch Shopping Cart
        (E) Get Ported Number
            (S) Prospect --> Bring a Number
            (S) Prospect --> Confirm Number Already With Paradise
            (S) GrowthBook --> Evaluate Porting Two Factor Flag
            (S) My Paradise --> Submit Portability Request to Mid-Tier
            (S) Midtier --> Query Msisdn Inventory
            (S) Mavenir --> List Msisdn Resources
            (S) Midtier --> Submit Reserve Msisdn
            (S) Mavenir --> Reserve Msisdn Resource
            (S) Midtier --> Patch Cart With Portability
            (S) Mavenir --> Patch Shopping Cart
            (S) Midtier --> Send Port Verification
            (S) Twilio --> Send Verification Sms
        (E) Verify Ported Number
            (S) Prospect --> Enter Porting Sms Code
            (S) Midtier --> Check Port Verification
            (S) Twilio --> Check Verification
        (E) Keep Current Number
            (S) Prospect --> Keep Current Number
        (E) Sweep Stale Reservations
            (S) Care --> Sweep Stale Number Reservations
    (E) Get Premium Number
        (E) Get Available Premium Numbers
            (S) Prospect --> Choose a Premium Number
            (S) Midtier --> Get Mavenir MSISDN Resources and Transform To Number Options And Return
            (S) Mavenir --> List Mavenir MSISDN Resources
        (E) Reserve Premium Msisdn Resource
            (S) My Paradise --> Submit Reserve Mavenir MSISDN Resource Request to Mid-Tier
            (S) Midtier --> Submit Reserve Mavenir MSISDN Resource
            (S) Mavenir --> Reserve Mavenir MSISDN Resource
        (E) Patch Cart With Premium Number
            (S) My Paradise --> Submit Patch Mavenir Shopping Cart Request to Mid-Tier And Store My Paradise Cart In Session
            (S) Midtier --> Patch Mavenir Shopping Cart and Transform To My Paradise Cart And Return
            (S) Mavenir --> Patch Mavenir Shopping Cart
    (E) Get Onboarding Plan
        (E) Get Catalog
            (S) Midtier --> Query Product Offerings And Map To Catalog
            (S) Mavenir --> List Product Offerings
        (E) Get Plan On Cart
            (S) Prospect --> Choose Onboarding Plan
            (S) Midtier --> Patch Cart With Plan
            (S) Mavenir --> Patch Shopping Cart
            (S) Prospect --> Keep Current Plan
    (E) Get Sim
        (S) GrowthBook --> Evaluate Esim Flag
        (S) Prospect --> Choose a Sim
        (S) Prospect --> Check Esim Compatibility
        (S) Prospect --> Continue To Sim Choice
        (E) Get Esim
            (S) Prospect --> Choose Esim
            (S) My Paradise --> Validate Sim Type on My Paradise Cart
            (S) My Paradise --> Submit Patch Cart With Sim Request to Mid-Tier
            (S) Midtier --> Validate Cognito User
            (S) Midtier --> Submit Patch Mavenir Shopping Cart With Sim
            (S) Mavenir --> Patch Shopping Cart
            (S) My Paradise --> Store Sim Type on My Paradise Customer Cart in Session
        (E) Get Paradise Sim Card
            (S) Prospect --> Request a Paradise Sim Card
            (S) My Paradise --> Submit Patch Cart With Sim Request to Mid-Tier
            (S) Midtier --> Validate Cognito User
            (S) Midtier --> Submit Patch Mavenir Shopping Cart With Sim
            (S) Mavenir --> Patch Shopping Cart
            (S) My Paradise --> Store Sim Type on My Paradise Customer Cart in Session
        (E) Get Existing Iccid
            (S) Prospect --> Enter Existing Sim
            (S) My Paradise --> Validate Iccid Format
            (S) My Paradise --> Submit Query Sim Resource Request to Mid-Tier
            (S) Midtier --> Validate Cognito User
            (S) Midtier --> Query Sim Resource
            (S) Mavenir --> Read Sim Resource
            (S) My Paradise --> Submit Patch Cart With Sim Request to Mid-Tier
            (S) Midtier --> Submit Patch Mavenir Shopping Cart With Sim
            (S) Mavenir --> Patch Shopping Cart
            (S) My Paradise --> Store Sim Type And Iccid on My Paradise Customer Cart in Session
        (E) Activate Sim From Almost There
            (S) Prospect --> Activate Sim From Almost There
            (S) My Paradise --> Validate Iccid Format
            (S) My Paradise --> Submit Query Sim Resource Request to Mid-Tier
            (S) Midtier --> Query Sim Resource
            (S) Mavenir --> Read Sim Resource
            (S) My Paradise --> Submit Patch Cart With Sim Request to Mid-Tier
            (S) Midtier --> Submit Patch Mavenir Shopping Cart With Sim
            (S) Mavenir --> Patch Shopping Cart
            (S) My Paradise --> Store Iccid on My Paradise Customer Cart in Session
            (S) My Paradise --> Submit Create Psim Delivered Order Request to Mid-Tier
            (S) Midtier --> Validate Waiting Psim on Mavenir Customer
            (S) Midtier --> Submit Create Mavenir Product Order
            (S) Mavenir --> Create Product Order
            (S) Midtier --> Submit Patch Waiting Psim on Mavenir Customer
            (S) Mavenir --> Patch Account
        (E) Complete Draft Sim Order
            (S) Care --> Complete Draft Sim Order
    (E) Get Verified Profile
        (E) Complete Persona Kyc
            (S) My Paradise --> Validate Persona Inquiry on My Paradise Customer
            (S) My Paradise --> Submit Create Inquiry Request to Persona
            (S) Persona --> Create Persona Inquiry
            (S) My Paradise --> Submit Query Inquiry Request to Mid-Tier
            (S) Midtier --> Validate Cognito User
            (S) Midtier --> Query Persona Inquiry and Transform To Document And Return
            (S) Persona --> Read Persona Document
            (S) My Paradise --> Map Persona Inquiry To Profile And Store In Session
        (E) Verify Later
            (S) Prospect --> Verify Later
        (E) Collect Identity Over Whatsapp
            (S) Prospect --> Contact Brand Ambassador
            (S) Ambassador --> Collect Identity Over Whatsapp
        (E) Patch Mavenir Customer
            (S) Prospect --> Enter Profile And Identity
            (S) My Paradise --> Submit Patch Customer Request to Mid-Tier
            (S) Midtier --> Validate Cognito User
            (S) Midtier --> Submit Patch Mavenir Customer
            (S) Mavenir --> Patch Mavenir Customer
            (S) My Paradise --> Store My Paradise Customer In Session
        (E) Patch Cart Verified
            (S) Midtier --> Submit Patch Mavenir Shopping Cart With Verified
            (S) Mavenir --> Patch Shopping Cart
    (E) Get Applied Voucher
        (S) My Paradise --> Submit Apply Voucher Request to Mid-Tier
        (S) Midtier --> Get Vouchera Voucher and Patch Mavenir Customer
        (S) Vouchera --> Validate Voucher
        (S) Mavenir --> Patch Mavenir Customer
        (S) My Paradise --> Store Vouchera Voucher on My Paradise Customer in Session
    (E) Get Order Review
        (E) Get Order Review
            (S) Prospect --> Check The Order
        (E) Get Data Freedom Upgrade
            (S) Prospect --> Upgrade To Data Freedom
            (S) Midtier --> Query Product Offerings
            (S) Mavenir --> List Product Offerings
            (S) Midtier --> Patch Cart With Plan
            (S) Mavenir --> Patch Shopping Cart
        (E) Get Review Plan
            (S) Prospect --> Change Plan From Review
            (S) Midtier --> Query Product Offerings
            (S) Mavenir --> List Product Offerings
            (S) Midtier --> Patch Cart With Plan
            (S) Mavenir --> Patch Shopping Cart
    (E) Get Payment
        (E) Enter Payment
            (S) Prospect --> Enter Payment
            (S) GrowthBook --> Evaluate Payment Flags
        (E) Load Customer
            (S) My Paradise --> Load My Paradise Customer From Midtier And Store In Session
            (S) Midtier --> Get Mavenir Customer and Transform To My Paradise Customer And Return
            (S) Mavenir --> Get Mavenir Customer
        (E) Authorize Card
            (S) Midtier --> Request Payment Authorization
            (S) Mavenir --> Authorize Card
            (S) Midtier --> Read Tokenized Card
            (S) Mavenir --> Read Tokenized Card
        (E) Provide Apple Pay Certificate
            (S) Midtier --> Provide Apple Pay Certificate
        (E) Adjust Credit
            (S) Care --> Adjust Credit Manually
    (E) Place Order
        (E) Create Billing Account
            (S) My Paradise --> Submit Create Billing Account Request to Mid-Tier
            (S) Midtier --> Validate Mavenir Customer Has No Billing Account
            (S) Midtier --> Submit Create Mavenir Billing Account
            (S) Mavenir --> Create Billing Account
        (E) Create Product Order
            (S) My Paradise --> Submit Create Product Order Request to Mid-Tier
            (S) Midtier --> Validate Customer Onboarding Is Not Done
            (S) GrowthBook --> Evaluate Order Flag
            (S) Midtier --> Submit Create Mavenir Product Order
            (S) Mavenir --> Create Product Order
        (E) View Order Result
            (S) My Paradise --> Store Order Result On My Paradise Customer
            (S) Prospect --> View Order Result
            (S) Prospect --> View Almost There
        (E) Create Order Ticket
            (S) Midtier --> Submit Create Order Ticket
            (S) Zendesk --> Create Ticket
        (E) View Order History
            (S) Care --> View Order History
    (E) Get Voucher Credit
        (E) Redeem Voucher
            (S) Midtier --> Submit Redeem Voucher Request to Vouchera
            (S) Vouchera --> Redeem Voucher
        (E) Apply Credit
            (S) Midtier --> Submit Apply Credit Request to Mavenir
            (S) Mavenir --> Apply Credit on Mavenir Customer

(E) Manage Billing
    (E) Know Current Bill
        (S) Customer --> View Billing
        (S) Midtier --> Query Customer
        (S) Mavenir --> Read Customer Details
        (S) Midtier --> Map Customer Details
        (S) Midtier --> Query Invoice Pdf
        (S) Mavenir --> Read Invoice Pdf
    (E) Settle Outstanding Balance
        (S) Customer --> Pay Now
        (S) Midtier --> Charge Outstanding Balance
        (S) Mavenir --> Charge Payment
        (S) Midtier --> Request Create Payment Failed Ticket
        (S) Zendesk --> Create Ticket
    (E) Store Payment Method
        (S) Customer --> Enter New Payment Method
        (S) Midtier --> Request Payment Authorization
        (S) Mavenir --> Authorize Card
        (S) Midtier --> Read Tokenized Card
        (S) Mavenir --> Read Tokenized Card
        (S) Midtier --> Provide Apple Pay Certificate

(E) Manage Services
    (S) Customer --> Change Plan
    (S) Midtier --> Query Product Offerings
    (S) Mavenir --> List Product Offerings
    (S) Midtier --> Request Plan Change Order
    (S) Mavenir --> Create Product Order
    (S) Customer --> Request Line Portability
    (S) Midtier --> Query Portability Tickets
    (S) Zendesk --> List Tickets
    (S) Midtier --> Request Create Portability Ticket
    (S) Zendesk --> Create Ticket
    (S) GrowthBook --> Evaluate Porting Two Factor Flag

(E) Sell Devices
    (S) Midtier --> Query Device Catalog
    (S) Zoho --> List Items
    (S) Midtier --> Query Pricebooks
    (S) Zoho --> List Pricebook Entries
    (S) Midtier --> Query Item Group
    (S) Zoho --> Read Item Group
    (S) Midtier --> Map Device Catalog
    (S) Midtier --> Sign Fygaro Button Url

(E) Access Selfcare
    (E) Authenticate Customer
        (S) Customer --> Enter Sign In Credentials
        (S) Cognito --> Issue Token To Browser Session
        (S) Midtier --> Verify Cognito Account
        (S) Cognito --> Create Session From Apple
        (S) Midtier --> Query Customer
        (S) Mavenir --> Read Customer Details
        (S) Midtier --> Map Customer Details
        (S) Customer --> Sign Out
        (S) Cognito --> Clear Session
    (E) Get Password Reset
        (S) Customer --> Request Password Reset
        (S) Midtier --> Request Password Reset
        (S) Cognito --> Send Password Reset
    (E) Know Account Status
        (S) Customer --> View Dashboard
        (S) Midtier --> Query Customer
        (S) Mavenir --> Read Customer Details
        (S) Midtier --> Map Customer Details
        (S) Midtier --> Query Service Usage
        (S) Mavenir --> Read Service Usage
    (E) Manage Profile
        (S) Customer --> Edit Profile
        (S) Midtier --> Patch Customer
        (S) Mavenir --> Patch Account
    (E) Get Support
        (S) Customer --> Send Support Request
        (S) Midtier --> Request Create Support Ticket
        (S) Zendesk --> Create Ticket

(E) Complete Care In Dep
    (S) Care --> View Base Customer
    (S) Care --> View Resource Inventory
    (S) Care --> View Order History
    (S) Care --> View Staff User Profiles

---

## Added on top of the Nico map

Kept every story from `.context/nico-chat/.context/story-map.md`. Inserted:

**Get Sign Up Plan / Create Account (this slice + code hops the Nico map skipped):** website handoff; plan deep-link; catalog voucher; Care orphan; Care false Initial Activation. After confirm, `useFormActivateAccount` calls the same `signIn` as the Sign In page. Tokens, JWT credentials, Mavenir customer, and empty cart run on Protected `useLoggedUser` after login.

**Get Ported Number:** Confirm Number Already With Paradise sits after Bring a Number and before ++portability++ is added to the cart. Enter Porting Sms Code includes Resend (Twilio send is the existing `Send Port Verification` / `Send Verification Sms` hops — no Request Porting Sms Resend hop).

**Get Premium Number:** Choose a Premium Number is the user story: retrieve premium ++MSISDN++ inventory, reserve, and add through the Midtier. Reserve Premium Msisdn Resource and Patch Cart With Premium Number stay the system hops.

**Nico notes / granola screens the Nico map named as missing:** premium/vanity numbers; transfer-code field; verify MSISDN already with Paradise; eSIM `*#06#` + GrowthBook eSIM flag; Care draft SIM order; almost-there activate; verify later / ambassador / WhatsApp; cart verified characteristic; Review Order / Data Freedom / edit plan from review (internal catalog); payment-upfront flag; manual credit; almost-there + DEP order history; DEP care screens.

---

## Scope boundary

**In scope:** Nico map hops plus Nico/granola screen stories and My Paradise/midtier/Mavenir/Cognito/Twilio/Zendesk/Vouchera/Persona/Care calls those notes and code evidence.

**Out of scope:** Scenario GWT, acceptance-test files, replacing `tests/.contexts/story-map.md`, Zoho Marketing Suite MQL funnel, SendGrid template editing in pods, provisioning-gateway reverse-engineer. LNP carrier review, Vireo API, and live Apple certificate fetch have no matching call in pml-my or midtier.

---

## Thin slices

### Increment 1: Prospect can complete paid onboarding

**Outcome:** A prospect selects a plan, creates and confirms an account, configures cart (number, plan, SIM), passes KYC, pays, and sees the order result — including the midtier maps and Mavenir/Cognito/Persona creates those steps require.

**Stories:**
- Open Plan Deep Link
- Query Product Offerings
- Map Product Offerings To Catalog
- Enter Account Credentials
- Create Unconfirmed Cognito User
- Enter Validation Code
- Confirm Account
- Create Customer
- Choose a Number
- Choose Onboarding Plan
- Choose a Sim
- Enter Profile And Identity
- Query Voucher
- Enter Payment
- Request Payment Authorization
- Create Product Order
- Redeem Voucher
- View Order Result

### Increment 2: Subscriber can sign in and see self-care

**Outcome:** A subscriber authenticates through Cognito, loads Mavenir customer + usage, and can sign out.

**Stories:**
- Enter Sign In Credentials
- Issue Token To Browser Session
- Verify Cognito Account
- Create Session From Apple
- View Dashboard
- Query Service Usage
- Sign Out

### Increment 3: Subscriber can pay and change service

**Outcome:** A subscriber views bills, pays an invoice through Mavenir payment, updates the stored payment method, changes plan on Mavenir, or opens a Zendesk portability ticket.

**Stories:**
- View Billing
- Pay Now
- Enter New Payment Method
- Change Plan
- Request Line Portability
- Send Support Request
- Edit Profile
- Request Password Reset

### Increment 4: Staff can sell a device without a DEP subscription

**Outcome:** Midtier can list Zoho Inventory devices and prices and sign a Fygaro button URL. No My Paradise front-end story exists for this yet.

**Stories:**
- Query Device Catalog
- List Items
- Map Device Catalog
- Sign Fygaro Button Url
