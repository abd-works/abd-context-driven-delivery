---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Get Number

## Epic: Verify Ported Number

### Story: Enter Porting Sms Code

**Story type:** pml-my

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/LineNumber/ProspectLineNumberSmsVerification.tsx` · `pml-my/src/pages/Onboarding/pages/LineNumber/usePortabilitySmsVerification.ts` · `pml-my/src/pages/Onboarding/pages/LineNumber/LineNumber.tsx`
- Granola: `.context/granola-notes/screenshot-wall.md` L34 · `miro-areas/06-port-sms-verify.png` · `.context/granola-notes/weird-stuff.md` L29
- Run: `.context/sandbox-walkthrough/live.log` L3226–L3422 (`/onboarding`; Confirm your number / Enter SMS code not in the dump)

**Intended:** Twilio check after Continue when `porting-2fa` is on. Live sandbox: flag off; SMS step is not mounted.

#### Examples

##### porting SMS code

| porting SMS code | example | code |
| --- | --- | --- |
| porting SMS code | valid porting SMS code | 123456 |
| porting SMS code | mismatch porting SMS code | 000000 |

| porting SMS code | example | helper |
| --- | --- | --- |
| porting SMS code | mismatch porting SMS code | Invalid verification code. |

++portability++ examples are on Bring a Number (`stories/onboard-a-customer/get-number/enter_porting_number_story.spec.md`).

#### Background

*Given* the Prospect is in Account Setup  
  *And* a ++My Paradise customer++ with a ++Mavenir shopping cart++  
  *And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++  
  *And* My Paradise has SMSed a ++porting SMS code++ through the Midtier

#### Scenario: Enter ++porting SMS code++

*When* the Prospect proceeds to confirming their number for porting  
*Then* the Prospect sees the code was sent to the ++portability++ number  
  *And* the Prospect can enter ++porting SMS code++ in Enter SMS code  
  *And* the Prospect can Resend  
  *And* Resend is disabled for 30 seconds  
  *And* the Prospect can Change  
  *And* the Prospect can go Back  
  *And* the Verify code operation is disabled  
*When* the Prospect enters ++porting SMS code++ ++valid porting SMS code++  
*Then* the Verify code operation is enabled  
*When* the Prospect clicks Verify code  
*Then* My Paradise checks the ++porting SMS code++ through the Midtier  
  *And* the Prospect is forwarded to Select Sim

#### Scenario: Verify with unusable ++porting SMS code++

*When* the Prospect clicks Verify code with ++porting SMS code++ ++mismatch porting SMS code++  
*Then* Enter SMS code shows helper text *Invalid verification code.*

#### Scenario: Resend ++porting SMS code++

*When* the Prospect clicks Resend  
*Then* My Paradise SMSes a ++porting SMS code++ through the Midtier  
  *And* the Prospect sees *A new code was sent to* the ++portability++ number  
  *And* Resend is disabled for 30 seconds before it can be used again

### Story: Check Port Verification

**Story type:** Midtier

**Source**
- Code: `pml-midtier/src/entities/Mavenir/mavenir.routes.ts` `POST /customer/portability/verify` · `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` `postPortabilityVerify`
- Granola: `.context/granola-notes/screenshot-wall.md` L34 · `miro-areas/06-port-sms-verify.png`

#### Background

*Given* a ++PML customer++ with a ++Mavenir shopping cart++  
  *And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++  
  *And* a ++porting SMS code++ was sent to ++portability++ ++valid portability++ portNumber

#### Scenario: Check port verification — code valid

*When* Midtier is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber  
*Then* Midtier checks the ++porting SMS code++ with Twilio  
  *And* Twilio returns `approved`  
  *And* Midtier marks the ++PML customer++ phone as verified  
  *And* Midtier returns `{ verified: true }` to My Paradise

#### Scenario: Check port verification — code mismatch

*When* Midtier is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber  
*Then* Midtier checks the ++porting SMS code++ with Twilio  
  *And* Twilio returns a non-approved status  
  *And* Midtier returns `{ verified: false }` to My Paradise

### Story: Check Verification

**Story type:** Twilio

**Source**
- Code: `pml-midtier/src/services/Twilio/twilio.service.ts` `checkPortabilityVerification` (`verificationChecks.create`)
- Granola: `.context/granola-notes/screenshot-wall.md` L34 · `miro-areas/06-port-sms-verify.png`

#### Background

*Given* a verification was sent to ++portability++ ++valid portability++ portNumber

#### Scenario: Check verification — code valid

*When* Twilio is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber  
*Then* Twilio creates a verification check (`verificationChecks.create`)  
  *And* Twilio returns `approved` to Midtier

#### Scenario: Check verification — code mismatch

*When* Twilio is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber  
*Then* Twilio creates a verification check  
  *And* Twilio returns a non-approved status to Midtier
