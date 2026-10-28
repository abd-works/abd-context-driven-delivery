# Domain Model

## Customer | custom

### Customer Profile

#### CustomerProfile <<Aggregate Root>> <<Entity>>

------
+ id: string
+ accountEmail: string
+ << composition >> identity: Identity
+ << composition >> address: Address
+ << association >> kycInquiryId: string
----
+ enterProfileDetails(identity: Identity, address: Address): void
+ sendSupportRequest(subject: string, message: string): SupportTicket
	-> KycInquiryRepository.create(identity, address)

#### CustomerProfileRepository <<Repository>>

------
+ << aggregation >> profiles: Collection<CustomerProfile>
----
+ create(accountCredentials: AccountCredentials): CustomerProfile
+ load(accountCredentials: AccountCredentials): CustomerProfile
+ update(profile: CustomerProfile): void

#### Identity <<Value Object>>

------
+ name: string
+ lastName: string
+ dateOfBirth: string
----

#### Address <<Value Object>>

------
+ street: string
+ city: string
+ postalCode: string
----

### KYC

#### KycInquiry <<Aggregate Root>> <<Entity>>

------
+ inquiryId: string
+ verified: boolean
----
+ fill(identity: Identity, address: Address): void
+ verify(): void

#### KycInquiryRepository <<Repository>>

------
----
+ create(identity: Identity, address: Address): KycInquiry
+ load(inquiryId: string): KycInquiry
+ update(inquiry: KycInquiry): void

## Service | custom

### Subscription

#### Subscription <<Aggregate Root>> <<Entity>>

------
+ id: string
+ << association >> planId: string
----
+ changePlan(planId: string): void
	-> PlanRepository.load(planId)

#### SubscriptionRepository <<Repository>>

------
----
+ create(customerProfile: CustomerProfile): Subscription
+ load(customerProfile: CustomerProfile): Subscription
+ update(subscription: Subscription): void

Integrations:
  - → Customer · Customer Profile · CustomerProfile
    pattern: Customer/Supplier
    direction: downstream
    crosses: customer identity
    integration: SubscriptionRepository.create(customerProfile)
