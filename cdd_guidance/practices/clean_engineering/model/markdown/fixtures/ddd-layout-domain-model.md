---
fidelity: [model]
artifact: [ce-domain-model]
format: md
extends: practices/clean_engineering/templates/class-model.md
---

# Domain Model — My Paradise

**Extends:** `practices/clean_engineering/templates/class-model.md` — same class notation (`------` properties · `----` operations). Constructors are left out of this view; the per-aggregate class models keep them.

---

## Layout

`##` is a bounded context, `###` an aggregate inside it, `####` a class inside the aggregate. The root's section ends with its repository, a `**{Root}Repository** «Repository»` block drawn inside the root's card below its domain operations.

---

## Customer

Who the customer is and how they sign in — credentials, profile, and identity check.

### Credentials

The email and password a customer signs in with, and the session token.

#### Credentials <<Aggregate Root>> <<Entity>>

The *Credentials* are the email and password a customer signs in with. The Credentials ask the *PasswordReset* for a temporary password when the customer forgets theirs.

- **Signing in.** The Credentials check the password and issue a session token.

------
+ email: string
	// identity
+ << composition >> passwordReset: PasswordReset
	// Access Selfcare
----
+ register(): Credentials
	-> CredentialsRepository.create(this)
+ requestTemporaryPassword(): Credentials
	-> CredentialsRepository.load(this)
	-> PasswordReset.send()
	// refused during the resend wait
+ signOut(): void
	-> CredentialsRepository.update(this)

**Invariants**

- A token is issued only to a verified account with no new password pending.

**CredentialsRepository** «Repository»

------
+ accounts: Collection<Credentials>
----
+ create(credentials: Credentials): Credentials
+ load(credentials: Credentials): Credentials | null
+ update(credentials: Credentials): Credentials

#### PasswordReset <<Entity>>

Access Selfcare.

------
+ newPasswordRequired: boolean
+ resendWaitSeconds: number
	// 30 after a resend: "Resend in 30s"
----
+ send(): string
	// issues a temporary password and emails it to the account's email
+ clear(): void

### SIM

How a line reaches the phone: an eSIM, or a physical Paradise SIM card with its ICCID.

#### IccidInventoryRepository <<Repository>>

------
+ << aggregation >> availableIccids: Collection<string>
	// the physical SIM stock
----
+ validate(iccid: string): void
	// refuses when the ICCID is not in stock ("Invalid ICCID.")

---

## Coverage

Each prototype screen, and the model elements that support it.

| Screen | Model elements |
| --- | --- |
| `create-credentials.jpg` | Credentials.register; CredentialsRepository.create |
