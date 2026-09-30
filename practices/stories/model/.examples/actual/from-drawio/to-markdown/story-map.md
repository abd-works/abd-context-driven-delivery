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
        (S) --> Confirm Cognito User
        (S) --> Issue Account Token To Browser Session
        (S) --> Validate Mavenir Customer in Cognito User Attributes
        (S) --> Submit Create Customer Request to Mid-Tier
        (S) --> Validate Cognito User
        (S) --> Submit Create Mavenir Customer
        (S) My Paradise --> Create Customer
        (S) --> Store Mavenir Customer Id on Cognito User
        (S) --> Load My Paradise Customer From Midtier And Store In Session
        (S) --> Get Mavenir Customer and Transform To My Paradise Customer And Return
        (S) --> Get Mavenir Customer
        (S) --> Ensure Cart on Customer
        (S) --> Fix Orphan Cognito Account
        (S) --> Read False Initial Activation
        (S) --> Sign In With Existing Account
    (E) Get Number
        (S) Customer --> Determine Number
        (S) --> Query Msisdn Inventory
        (S) --> List Msisdn Resources
        (S) --> Search Msisdn Inventory
        (S) --> Search Msisdn Resources
        (S) Customer --> Choose a Number
        (S) --> Submit Reserve Number Request to Mid-Tier
        (S) --> Submit Reserve Msisdn
        (S) --> Reserve Msisdn Resource
        (S) --> Submit Patch Cart With Number Request to Mid-Tier
        (S) --> Patch Cart With Number
        (S) --> Patch Shopping Cart
        (S) --> Bring a Number
        (S) --> Confirm Number Already With Paradise
        (S) --> Evaluate Porting Two Factor Flag
        (S) --> Submit Portability Request to Mid-Tier
        (S) --> Patch Cart With Portability
        (S) --> Send Port Verification
        (S) --> Send Verification Sms
        (S) --> Enter Porting Sms Code
        (S) --> Check Port Verification
        (S) --> Check Verification
        (S) Customer --> Keep Current Number
        (S) Care --> Sweep Stale Number Reservations
    (E) Get Onboarding Plan
        (S) --> Query Product Offerings And Map To Catalog
        (S) --> List Product Offerings
        (S) My Paradise --> Load Plan Catalog
        (S) Customer --> Choose Onboarding Plan
        (S) --> Patch Cart With Plan
        (S) --> Patch Shopping Cart
        (S) --> Keep Current Plan
    (E) Get Sim
        (S) Customer --> Choose Esim
        (S) --> Request a Paradise Sim Card
        (S) --> Enter Existing Sim
        (S) --> Activate Sim
        (S) --> Complete Draft Sim Order
    (E) Get Verified Profile
        (S) Customer --> Customer Complete Persona Kyc
        (S) Ambassador --> Collect Identity With Brand Amassador
    (E) Get Order Review
        (S) Customer --> Check The Order
        (S) --> Upgrade To Data Freedom
        (S) --> Change Plan From Review
    (E) Get Payment
        (S) Customer --> Enter Payment
        (S) --> Evaluate Payment Flags
        (S) My Paradise --> Authorize Card
        (S) --> Provide Apple Pay Certificate
        (S) Care --> Adjust Credit Manually
    (E) Place Order
        (S) My Paradise --> Create Billing Account
        (S) --> Create Product Order
        (S) Customer --> View Order Result
        (S) My Paradise --> Create Order Ticket
        (S) Care --> View Order History
    (E) Get Voucher Credit
        (S) My Paradise --> Redeem Voucher and Apply Credit
(E) Self-Serve Subscription
    (E) Access Selfcare
        (S) Customer --> Enter Sign In Credentials
        (S) --> Reset Password
        (S) --> Edit Profile
        (S) --> Sign Out
    (E) Manage Billing
        (S) Customer --> View Billing
        (S) --> Pay Now
        (S) --> Enter New Payment Method
    (E) Manage Services
        (S) Customer --> View Dashboard
        (S) --> Change Plan
        (S) --> Request Line Portability
        (S) --> Purchase Device
        (S) Customer --> Send Support Request