(E) Onboard A Customer
    (E) Create Customer
        (S) --> Create Customer
        (E) Create Empty Cart
            (S) --> Ensure Cart on Customer
        (E) Create Unconfirmed User
            (S) --> Create Unconfirmed Cognito User
        (E) Load Customer
            (S) --> Load My Paradise Customer From Midtier And Store In Session
        (E) Verify Account
            (S) --> Enter Validation Code
    (E) Get Number
        (E) Enter Porting Number
            (S) --> Submit Portability Request
        (E) Get New Number
            (S) --> Determine Number
            (S) --> Choose a Number
        (E) Verify Ported Number
            (S) --> Check Port Verification
    (E) Get Onboarding Plan
        (S) --> Load Plan Catalog
        (S) --> Choose Onboarding Plan
    (E) Get Order Review
        (S) --> Check The Order
        (S) --> Upgrade To Data Freedom
        (S) --> Change Plan From Review
    (E) Get Payment
        (S) --> Enter Payment
        (S) --> Authorize Card
        (S) --> Provide Apple Pay Certificate
    (E) Get Sign Up Plan
        (S) --> Open Plan Deep Link
        (S) --> Apply Catalog Voucher
    (E) Get Sim
        (S) --> Choose Esim
        (S) --> Request a Paradise Sim Card
        (S) --> Enter Existing Sim
        (S) --> Activate Sim
    (E) Get Verified Profile
        (S) --> Customer Complete Persona Kyc
        (S) --> Collect Identity With Brand Amassador
    (E) Get Voucher Credit
        (S) --> Redeem Voucher and Apply Credit
    (E) Place Order
        (S) --> Create Billing Account
        (S) --> Create Product Order
        (S) --> View Order Result
        (S) --> Create Order Ticket
    (E) Sign In With Existing Account
        (S) --> Sign In With Existing Account