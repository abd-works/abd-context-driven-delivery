# Cross-practice relationships

Review of the Paradise Mobile explorer graph (`C:\dev\pml-domainmodel\.context\explorer-graph.json`), scanned 28 Sep 2026. 1,038 nodes. 269 edges cross a practice boundary.

Every one of those edges is the same kind: a stories node **demonstrates** a clean-engineering class (`OoadClass`). DDD has no edge into or out of another practice.

## What is in the graph

| From | Kind | To | Count |
| --- | --- | --- | --- |
| Example | demonstrates | OoadClass | 54 |
| Step | demonstrates | OoadClass | 106 |
| Scenario | demonstrates | OoadClass | 73 |
| Story | demonstrates | OoadClass | 31 |
| Background | demonstrates | OoadClass | 5 |

The 54 example edges are the links the scanner found. The other 215 copy those same classes onto the step, scenario, story, and background that use the example, so those nodes show a **ce** section. Create Customer’s **ce → demonstrates → AccountCredentials** is the copy of `enteredValidAccountCredentials`.

## Classes the examples demonstrate

54 examples, 21 classes.

| Class | Examples |
| --- | --- |
| AccountCredentials | 14 |
| CognitoUser | 6 |
| ValidationCode | 4 |
| Voucher | 3 |
| VoucherRedemption | 3 |
| PersonaInquiryFields | 3 |
| PersonaInquiryResult | 3 |
| Identity | 2 |
| Address | 2 |
| FacTokenizedCard | 2 |
| AccountToken | 2 |
| Billing | 1 |
| PersonaDocument | 1 |
| VoucheraVoucher | 1 |
| AppleCert | 1 |
| ApplePayCertificate | 1 |
| Payment | 1 |
| PaymentIframe | 1 |
| CartRepository | 1 |
| Portability | 1 |
| MavenirShoppingCart | 1 |

Eight examples demonstrate more than one class:

| Example | Classes |
| --- | --- |
| trialVoucher | Voucher, Billing |
| purchasablePlanIds | VoucheraVoucher, Voucher |
| incorrectCredentialOutlines | CognitoUser, AccountToken, AccountCredentials |
| storedCognitoUserWithAccountToken | CognitoUser, AccountToken |
| enteredValidAddress | Identity, Address |
| completedInquiryWithoutDocument | PersonaInquiryResult, PersonaInquiryFields |
| failedPersonaInquiryResult | PersonaInquiryResult, PersonaInquiryFields |
| maxPaymentAttempts | Payment, PaymentIframe |

## Written in the model, absent from this scan

| From | Kind | To | Why it is missing |
| --- | --- | --- | --- |
| Step | invokes | Operation | No operation nodes are loaded, and story call facts are not passed into the story map. |
| Step | observes | member | Same gap as invokes. |
| BDD description | describes | class | This repo has no Python BDD descriptions in the scan. |
