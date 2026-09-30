(E) Onboard A Customer
    (E) Get Sign Up Plan
        (S) Website --> Hand Off Sign Up To Onboarding
        (S) Customer --> Open Plan Deep Link
        (S) My Paradise --> Load Plan Catalog
        (S) Customer --> Apply Catalog Voucher
    (E) Create Customer
        (S) --> Enter Account Credentials
        (S) --> Create Unconfirmed Cognito User
        (S) My Paradise --> Enter Validation Code
        (S) My Paradise --> Confirm Cognito User
        (S) My Paradise --> Issue Account Token To Browser Session
        (S) My Paradise --> Validate Mavenir Customer in Cognito User Attributes
        (S) My Paradise --> Submit Create Customer Request to Mid-Tier
        (S) My Paradise --> Validate Cognito User
        (S) My Paradise --> Submit Create Mavenir Customer
        (S) My Paradise --> Create Customer
        (S) My Paradise --> Store Mavenir Customer Id on Cognito User
        (S) My Paradise --> Load My Paradise Customer From Midtier And Store In Session
        (S) My Paradise --> Get Mavenir Customer and Transform To My Paradise Customer And Return
        (S) My Paradise --> Get Mavenir Customer
        (S) My Paradise --> Ensure Cart on Customer
        (S) My Paradise --> Fix Orphan Cognito Account
        (S) My Paradise --> Read False Initial Activation
        (S) My Paradise --> Sign In With Existing Account
    (E) Get Number
        (S) Customer --> Determine Number
        (S) Customer --> Query Msisdn Inventory
        (S) Customer --> List Msisdn Resources
        (S) Customer --> Search Msisdn Inventory
        (S) Customer --> Search Msisdn Resources
        (S) Customer --> Choose a Number
        (S) Customer --> Submit Reserve Number Request to Mid-Tier
        (S) Customer --> Submit Reserve Msisdn
        (S) Customer --> Reserve Msisdn Resource
        (S) Customer --> Submit Patch Cart With Number Request to Mid-Tier
        (S) Customer --> Patch Cart With Number
        (S) Customer --> Patch Shopping Cart
        (S) Customer --> Bring a Number
        (S) Customer --> Confirm Number Already With Paradise
        (S) Customer --> Evaluate Porting Two Factor Flag
        (S) Customer --> Submit Portability Request to Mid-Tier
        (S) Customer --> Patch Cart With Portability
        (S) Customer --> Send Port Verification
        (S) Customer --> Send Verification Sms
        (S) Customer --> Enter Porting Sms Code
        (S) Customer --> Check Port Verification
        (S) Customer --> Check Verification
        (S) Customer --> Keep Current Number
        (S) Care --> Sweep Stale Number Reservations
    (E) Get Onboarding Plan
        (S) --> Query Product Offerings And Map To Catalog
        (S) --> List Product Offerings
        (S) My Paradise --> Load Plan Catalog
        (S) Customer --> Choose Onboarding Plan
        (S) Customer --> Patch Cart With Plan
        (S) Customer --> Patch Shopping Cart
        (S) Customer --> Keep Current Plan
    (E) Get Sim
        (S) Customer --> Choose Esim
        (S) Customer --> Request a Paradise Sim Card
        (S) Customer --> Enter Existing Sim
        (S) Customer --> Activate Sim
        (S) Customer --> Complete Draft Sim Order
    (E) Get Verified Profile
        (S) Customer --> Customer Complete Persona Kyc
        (S) Ambassador --> Collect Identity With Brand Amassador
    (E) Get Order Review
        (S) Customer --> Check The Order
        (S) Customer --> Upgrade To Data Freedom
        (S) Customer --> Change Plan From Review
    (E) Get Payment
        (S) Customer --> Enter Payment
        (S) Customer --> Evaluate Payment Flags
        (S) My Paradise --> Authorize Card
        (S) My Paradise --> Provide Apple Pay Certificate
        (S) Care --> Adjust Credit Manually
    (E) Place Order
        (S) My Paradise --> Create Billing Account
        (S) My Paradise --> Create Product Order
        (S) Customer --> View Order Result
        (S) My Paradise --> Create Order Ticket
        (S) Care --> View Order History
    (E) Get Voucher Credit
        (S) My Paradise --> Redeem Voucher and Apply Credit
(E) Self-Serve Subscription
    (E) Access Selfcare
        (S) Customer --> Enter Sign In Credentials
        (S) Customer --> Reset Password
        (S) Customer --> Edit Profile
        (S) Customer --> Sign Out
    (E) Manage Billing
        (S) Customer --> View Billing
        (S) Customer --> Pay Now
        (S) Customer --> Enter New Payment Method
    (E) Manage Services
        (S) Customer --> View Dashboard
        (S) Customer --> Change Plan
        (S) Customer --> Request Line Portability
        (S) Customer --> Purchase Device
        (S) Customer --> Send Support Request