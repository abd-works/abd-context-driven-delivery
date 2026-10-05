fidelity: story_map / model
evidence: intended — user message 2026-10-05
source: sandbox/single-client-view/.context/emil;-discussion.,txtx (open questions only; no answers yet)

=========
theme: Cross Sell Credit Cards
---------
stories:
Cross Sell Credit Cards
    Bring The Client Together
        Sales Person --> See Client Across PC Bank And EQ Bank
        Call Center --> See Client Across PC Bank And EQ Bank
        Store --> See Client Across PC Bank And EQ Bank
        // one person, both banks, so the offer is about the client and not one bank's record
        // PC Bank holds credit cards; EQ Bank does not
        // prospect, onboarding, and account say how far the relationship has gone
        // lines read here: retail deposits, business banking, international banking, and PC Bank credit cards
        Call Center --> Display PC Bank Onboarding Credit Cards
        Call Center --> Display PC Bank Account Credit Cards
        Single Client View --> Integrate PC Bank Onboarding Credit Cards
        Single Client View --> Integrate PC Bank Account Credit Cards
        Call Center --> Render Client Dashboard
    Sell Credit Cards
        Sales Person --> Offer Credit Cards To Client Of Either Bank
        Sales Person --> Offer Credit Cards To New Client Of One Bank
    Offer Credit Cards On The Call
        Call Center --> Offer Credit Cards To Client Of Either Bank
        Call Center --> Offer Credit Cards To New Client Of One Bank
    Offer Credit Cards In The Store
        Store --> Offer Credit Cards To Client Of Either Bank
        Store --> Offer Credit Cards To New Client Of One Bank
ce:
Client
  relationship
  offerCreditCards
       -> Relationship.read
       // sales person, call center, and store each offer a PC Bank credit card
       // offered when the client is known at PC Bank or EQ Bank and does not already hold one
       // same offer for a client of either bank and for a new client of one bank
Relationship
  bank
  perspective
  line
  read
       -> System.display
Bank
  // instances: PC Bank, EQ Bank
System
  display
  integrate
  // PC Bank credit card systems: onboarding, account
  // EQ Bank has no credit card system

=========
theme: Cross Sell Mortgages
---------
stories:
Cross Sell Mortgages
    Bring The Client Together
        Sales Person --> See Client Across PC Bank And EQ Bank
        Call Center --> See Client Across PC Bank And EQ Bank
        Store --> See Client Across PC Bank And EQ Bank
        // one person, both banks
        // EQ Bank holds mortgages; PC Bank does not
        // lines read here: retail deposits, business banking, international banking, and EQ Bank mortgages
        Call Center --> Display EQ Bank Onboarding Mortgages
        Call Center --> Display EQ Bank Account Mortgages
        Single Client View --> Integrate EQ Bank Onboarding Mortgages
        Single Client View --> Integrate EQ Bank Account Mortgages
        Call Center --> Render Client Dashboard
    Hand Off The Mortgage
        Call Center --> Hand Mortgage Client To Sales Person
    Sell Mortgages
        Sales Person --> Offer Mortgages To Client Of Either Bank
        Sales Person --> Offer Mortgages To New Client Of One Bank
    Offer Mortgages In The Store
        Store --> Offer Mortgages To Client Of Either Bank
        Store --> Offer Mortgages To New Client Of One Bank
ce:
Client
  handOffMortgage
       // call center spots the mortgage and passes the client to a sales person; call center does not offer it
  offerMortgages
       -> Relationship.read
       // sales person and store offer when the client does not already hold an EQ Bank mortgage
       // call center hands the client to a sales person and does not offer
       // same offer for a client of either bank and for a new client of one bank
Relationship
  read
       -> System.display
System
  // EQ Bank mortgage systems: onboarding, account
  // PC Bank has no mortgage system
