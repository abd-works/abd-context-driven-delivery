(E) Onboard A Customer
    (E) Create Customer
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
        (E) Verify Ported Number
            (S) --> Check Port Verification