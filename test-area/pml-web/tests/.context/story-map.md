---
fidelity: [discovery]
artifact: [story-map]
format: md
evidence: observed
---

# Story Map — Paradise Mobile (pml-web)

**Sources / context:** Leo's multi-line prototype, walked on 2026-11-17 and written up in `sandbox/extracted-context/app-extraction/extraction-overview.md` (goals 1 to 4, and its closing table "Against the current story map"). The Granola meeting *Domain modeling for credential and customer profile with Nico* (2026-11-17). The previous story map (this file before 2026-11-17) for what the prototype does not show: the credentials stories (Manage Credentials), with their behaviour from `pml-domainmodel/depecrated/v1-system-stories/stories/{access-selfcare,manage-billing,manage-services}/*.e2e.ts` and their screens from `pml-my/src/pages/{SignIn,My}/pages/*`. Domain words from `src/.context/bounded-context-map.md`.

The map describes a fresh system built from these stories and the domain. The six onboarding epics, Choose Lines to Place Order, follow the prototype screen by screen; each story links to its own scenarios, `../story_tests/{epic}/{story}/{story_snake}_story.test.md`.

---

# (E) Choose Lines
## (S) Customer --> [Display Plans](../story_tests/choose-lines/display-plans/display_plans_story.test.md#story-display-plans)
## (S) Customer --> [Add Line To Cart](../story_tests/choose-lines/add-line-to-cart/add_line_to_cart_story.test.md#story-add-line-to-cart)
## (S) Customer --> [View Cart](../story_tests/choose-lines/view-cart/view_cart_story.test.md#story-view-cart)
## (S) Customer --> [Remove Line From Cart](../story_tests/choose-lines/remove-line-from-cart/remove_line_from_cart_story.test.md#story-remove-line-from-cart)
## (S:system) My Paradise --> [Apply Family Discount](../story_tests/choose-lines/apply-family-discount/apply_family_discount_story.test.md#story-apply-family-discount)
## (S) Customer --> [Apply Voucher](../story_tests/choose-lines/apply-voucher/apply_voucher_story.test.md#story-apply-voucher)
## (S) Customer --> [Unlock Promo Plan](../story_tests/choose-lines/unlock-promo-plan/unlock_promo_plan_story.test.md#story-unlock-promo-plan)
# (E) Create Account
## (S) Customer --> [Create Credentials](../story_tests/create-account/create-credentials/create_credentials_story.test.md#story-create-credentials)
## (S) Customer --> [Enter Validation Code](../story_tests/create-account/enter-validation-code/enter_validation_code_story.test.md#story-enter-validation-code)
## (S) Customer --> [Resend Validation Code](../story_tests/create-account/resend-validation-code/resend_validation_code_story.test.md#story-resend-validation-code)
## (S:system) My Paradise --> [Create Customer](../story_tests/create-account/create-customer/create_customer_story.test.md#story-create-customer)
# (E) Finish Order
## (S) Customer --> [Check Order](../story_tests/finish-order/check-order/check_order_story.test.md#story-check-order)
## (S) Customer --> [Change Line Plan](../story_tests/finish-order/change-line-plan/change_line_plan_story.test.md#story-change-line-plan)
## (S) Customer --> [Return To Order Review](../story_tests/finish-order/return-to-order-review/return_to_order_review_story.test.md#story-return-to-order-review)
## (S) Customer --> [Save And Exit Order](../story_tests/finish-order/save-and-exit-order/save_and_exit_order_story.test.md#story-save-and-exit-order)
# (E) Set Up Lines
## (S) Customer --> [Name Line](../story_tests/set-up-lines/name-line/name_line_story.test.md#story-name-line)
## (S) Customer --> [Pick Number](../story_tests/set-up-lines/pick-number/pick_number_story.test.md#story-pick-number)
## (S) Customer --> [Enter Porting Number](../story_tests/set-up-lines/enter-porting-number/enter_porting_number_story.test.md#story-enter-porting-number)
## (S) Customer --> [Verify Ported Number](../story_tests/set-up-lines/verify-ported-number/verify_ported_number_story.test.md#story-verify-ported-number)
## (S) Customer --> [Defer Port Verification](../story_tests/set-up-lines/defer-port-verification/defer_port_verification_story.test.md#story-defer-port-verification)
## (S) Customer --> [Select Sim](../story_tests/set-up-lines/select-sim/select_sim_story.test.md#story-select-sim)
## (S) Customer --> [Enter Existing Sim](../story_tests/set-up-lines/enter-existing-sim/enter_existing_sim_story.test.md#story-enter-existing-sim)
## (S) Customer --> [Request Paradise Sim Card](../story_tests/set-up-lines/request-paradise-sim-card/request_paradise_sim_card_story.test.md#story-request-paradise-sim-card)
## (S) Customer --> [Activate Sim](../story_tests/set-up-lines/activate-sim/activate_sim_story.test.md#story-activate-sim)
# (E) Verify Identity
## (S) Customer --> [Verify Id With Persona](../story_tests/verify-identity/verify-id-with-persona/verify_id_with_persona_story.test.md#story-verify-id-with-persona)
## (S) Customer --> [Enter Id Details Manually](../story_tests/verify-identity/enter-id-details-manually/enter_id_details_manually_story.test.md#story-enter-id-details-manually)
## (S) Customer --> [Confirm Details](../story_tests/verify-identity/confirm-details/confirm_details_story.test.md#story-confirm-details)
## (S:system) My Paradise --> [Record Kyc Inquiry](../story_tests/verify-identity/record-kyc-inquiry/record_kyc_inquiry_story.test.md#story-record-kyc-inquiry)
# (E) Place Order
## (S:system) My Paradise --> [Reload Card Form](../story_tests/place-order/reload-card-form/reload_card_form_story.test.md#story-reload-card-form)
## (S) Customer --> [Enter Payment](../story_tests/place-order/enter-payment/enter_payment_story.test.md#story-enter-payment)
## (S:system) My Paradise --> [Authorize Card](../story_tests/place-order/authorize-card/authorize_card_story.test.md#story-authorize-card)
## (S:system) My Paradise --> [Create Billing Account](../story_tests/place-order/create-billing-account/create_billing_account_story.test.md#story-create-billing-account)
## (S) Customer --> [Pay And Subscribe](../story_tests/place-order/pay-and-subscribe/pay_and_subscribe_story.test.md#story-pay-and-subscribe)
## (S:system) My Paradise --> [Create Order Ticket](../story_tests/place-order/create-order-ticket/create_order_ticket_story.test.md#story-create-order-ticket)
## (S) Customer --> [View Order Result](../story_tests/place-order/view-order-result/view_order_result_story.test.md#story-view-order-result)
# (E) Manage Credentials
## (S) Customer --> [Sign In With Existing Account](../story_tests/manage-credentials/sign-in-with-existing-account/sign_in_with_existing_account_story.test.md#story-sign-in-with-existing-account)
## (S) Customer --> [Reset Password](../story_tests/manage-credentials/reset-password/reset_password_story.test.md#story-reset-password)
## (S) Customer --> [Set New Password](../story_tests/manage-credentials/set-new-password/set_new_password_story.test.md#story-set-new-password)
## (S) Customer --> [Sign Out](../story_tests/manage-credentials/sign-out/sign_out_story.test.md#story-sign-out)
## (S:system) CRM --> [Create Customer With Temporary Password](../story_tests/manage-credentials/create-customer-with-temporary-password/create_customer_with_temporary_password_story.test.md#story-create-customer-with-temporary-password)
## (S) Administrator --> [Force Password Reset](../story_tests/manage-credentials/force-password-reset/force_password_reset_story.test.md#story-force-password-reset)

---

## Evidence — onboarding (Choose Lines to Place Order)

Every source below is a section of `sandbox/extracted-context/app-extraction/extraction-overview.md` unless it names another.

| Story | Evidence | Behaviour source |
|---|---|---|
| Display Plans | observed | *Choose Your Unlimited Mobile Plan* — the first screen of the prototype: the four plans (Atlas, Ace, Data Freedom, Essentials) with price, what each gives in Bermuda and when you travel, *All fees included*, the country-list links; footer "Add a line to start. 3 or more lines get a family discount." |
| Add Line To Cart | observed | *Line added*; *Several lines* — **Add** puts a plan on as Line 1, then every plan offers **Add one more**; *Goal 4* — **Add a line** from the checklist opens the catalog with **Back to your order** and the new line joins the checklist as *to do* |
| Remove Line From Cart | observed | *Cart* — **Remove Line 1, Atlas**; *Goal 4* — **Remove line** from a line's Edit asks "Remove Sam’s line? Everything you set up for this line will be lost.", **Keep it** / **Remove line**; going from 2 lines to 1 turns the progress bar's **Lines** back to **Your line** |
| Apply Voucher | observed | *Vouchers* — ALL10 ($10 off every line), CART10 (10% off the first bill), TRAVEL25 ($25 off each Atlas or Ace line); one at a time; first bill only; stacks with the family discount; any other code: "Invalid code. Please try again."; **Remove** brings the code field back |
| Unlock Promo Plan | observed | *Goal 3* — PROMO30 on the catalog unlocks the hidden *Promo* plan (free for 30 days, Essentials' allowances, $0/mo) and puts it in the cart as Line 1 |
| Apply Family Discount | observed | *Family discount* — $5 per line per month from 3 lines; each line's price struck through; "Family discount · $5 × 3 lines −$15/mo"; the footer nudges "save $180 a year with 2 more lines", then "1 more line", then "$240 with a 4th line" |
| View Cart | observed | *Cart*; *Goal 4* — each line with its plan and price, the voucher, "You pay now $168, then $193/mo", **Hide cart** |
| Create Credentials | observed | *Let's create your account* — email, password with **Show password**, confirm password; the password hint; agreement links; empty-field messages |
| Enter Validation Code | observed | *Check your email!* — **Verify email**; "Code is required." |
| Resend Validation Code | observed | *Check your email!* — **Resend**: "We sent you a new code. Please check your email.", then "Resend in 30s" |
| Create Customer | observed | Granola 2026-11-17 — the customer profile is created only after the credentials are verified; *Order checklist* — the account step is then *done* |
| Name Line | observed | *Choose a number* — **Who is this line for?** ("e.g. Me, Mom or Alice"), required: "Please provide a name."; Granola 2026-11-17 — a nickname is required on every line; *Goal 4* — **Change name** from Edit |
| Pick Number | observed | *Get a new number* — search 3 to 5 letters or digits, five numbers, **Refresh**, "Choose a number to continue."; *Several lines* — a number one line holds is left out of the next line's list; *Goal 4* — **Change number** returns with the line's number selected at the top |
| Enter Porting Number | observed | *Bring your mobile number* — provider, number, account number, account, account type, two confirmations; the line starts today on a temporary number; moving takes 3–5 business days |
| Verify Ported Number | observed | *Bring your mobile number* — **Is this phone with you?** → **Yes, text me the code** (the code screen itself was not captured) |
| Defer Port Verification | observed | *Bring your mobile number* — **No, verify it later**: the line shows its temporary number and "Porting … We'll contact you to verify it"; Granola 2026-11-17 — verifying later opens a support ticket instead of sending a code |
| Select Sim | observed | *Now you need a SIM* — eSIM (default) or physical SIM; *SIM choices* — **Check here** explains dialling \*#06# for an EID; **No, use a physical SIM** / **Yes, I have eSIM**; *Goal 4* — **Change SIM** from Edit (sheet not captured) |
| Enter Existing Sim | observed | *SIM choices* — **I have my Paradise SIM card.**: 20-digit ICCID; "Enter the ICCID number of your SIM card."; "The ICCID must be 20 digits." |
| Request Paradise Sim Card | observed | *SIM choices* — **I need a Paradise SIM card.**: pick it up at a Paradise store or an authorized retailer; details by email |
| Activate Sim | observed (pml-my) | not in the prototype; kept from the previous map: a Paradise SIM card ordered without its ICCID is activated when the customer has it |
| Verify Id With Persona | observed | *Verify your ID* — **Finish ID**; *Confirm your details (Finish ID path)* — marked **Verified**, filled from the ID check, ID fields locked |
| Enter Id Details Manually | observed | *Verify your ID* — **Skip and enter my details**; *Confirm your details (skip path)* — every field and its message; "We're checking your ID — It takes up to 48 hours. Our team will be in touch."; coming back reopens this form, not the ID check |
| Confirm Details | observed | *Confirm your details* (both paths) — alternate contact number, preferred name, and address stay editable; **Save details** |
| Record Kyc Inquiry | observed | Granola 2026-11-17 — whether the identity is verified, and whether an identity ticket is required, belong to the KYC inquiry, not the customer profile |
| Check Order | observed | *Order checklist*; *Several lines*; *Your order is ready* — progress bar Account, Lines (Your line with one), Your ID, Payment; each line as name · plan with number, SIM, porting, and **Edit**; ID verified or manual review; **What to expect**; **Continue to payment** |
| Change Line Plan | observed | *Goal 4* — **Change plan**: "Everything you set up for this line stays."; current plan marked **Current plan**; others **Select this plan** |
| Return To Order Review | observed | *Goal 4* — after a line's name, number, or SIM, or the ID, is changed from **Edit**, the customer is back on the checklist; Granola 2026-11-17 — the customer may edit details before confirming |
| Save And Exit Order | observed | *Check your email!* — **Save and exit** is offered from here on: leave and come back later (what the return shows was not captured) |
| Enter Payment | observed | *Payment: Add your card* — the card processor's form; "You pay now" with the full price struck through and each discount; "Then $193/mo. Cancel anytime." |
| Reload Card Form | observed | Granola 2026-11-17 — the card form is preloaded from the order summary and reloaded about every 5 minutes while the customer stays, because the hosted payment page times out |
| Authorize Card | observed | *Payment: Add your card* — "You may see a $1 authorization. It isn't a charge." |
| Create Billing Account | observed (pml-my) | kept from the previous map: the account that takes the payment is opened for the customer at the payment step |
| Pay And Subscribe | observed | *Payment: Add your card* — **Pay and subscribe**; *Goal 3* — "You pay now $0 — Free for 30 days." with **Start for free**; *Order result* — the first bill on the 1st is pro-rated |
| Create Order Ticket | observed | *Your order is ready* — "ID check: we check it manually, up to 48 hours."; *Order result* — "We'll contact you to verify it first"; Granola 2026-11-17 — verifying later opens a support ticket |
| View Order Result | observed | *Order result* — **Almost there!** while the ID is in manual review; **You're all set!** grouped by line: install eSIMs (QR code by email), put your SIM in, porting your number; "You paid $168"; pro-rated first bill; **Understand your first bill**, **Contact us**, **Go to my account** (the last two are not built in the prototype) |

## Evidence — Manage Credentials

| Story | Evidence | Behaviour source | Screen (pml-my) |
|---|---|---|---|
| Sign In With Existing Account | observed | onboarding sign-in and `access-selfcare/sign-in.e2e.ts` — one sign-in page; wrong password and unknown email show the incorrect-credentials message; a temporary password asks for a new one. The prototype's **Sign in** links were not captured | `SignIn/pages/SignIn` |
| Reset Password | observed | `access-selfcare/reset-forgotten-password.e2e.ts` — request a temporary password by email, see *Continue to login* | `SignIn/pages/ForgotPassword` |
| Set New Password | observed | none in v1 — from the screen: when sign-in asks for a new password, the customer sets it and confirms. Granola 2026-11-17: sign-in asks for one when the password was created by the CRM or an administrator forced a reset | `SignIn/pages/NewPassword` |
| Sign Out | observed | `access-selfcare/sign-out.e2e.ts` and the onboarding header — both ask *Do you want to log out?* and clear the session | `My/components/Navbar/LogoutModal`, `Onboarding/components/Header/LogoutButton` |
| Create Customer With Temporary Password | intended | Granola 2026-11-17 — a customer created in the CRM gets a temporary password, so their first sign-in asks for a new one. Backlog | none |
| Force Password Reset | intended | Granola 2026-11-17 — an administrator forces a reset for a locked-out customer, so their next sign-in asks for a new password. Backlog | none |

## Notes on the structure

**The order holds several lines.** In the prototype a customer adds as many lines as they like from the catalog, and each line is named and set up in turn (number, then SIM). Choose Lines is everything that happens to the cart before the account exists; Set Up Lines repeats for every line; Finish Order is the prototype's *Finish your order* checklist, shown right after the account is created: it ties the lines, the ID, and the payment together, and the customer comes back to it after each line and after the ID.

**One mechanic, one story.** Adding a line from the catalog and **Add a line** from the checklist are one story (Add Line To Cart); removing a line from the cart and from a line's Edit are one story (Remove Line From Cart). Changing a line's name, number, or SIM from Edit reopens Name Line, Pick Number, or Select Sim, so each is a scenario of that story, and coming back is Return To Order Review. Changing a line's plan keeps everything set up for the line, which no catalog story does, so it is its own story (Change Line Plan). Removing a voucher is a scenario of Apply Voucher, since only one voucher holds at a time.

**Unlock Promo Plan is not Apply Voucher.** PROMO30 does not discount the first bill: it reveals a plan the catalog hides and adds a line on it, so it acts on the cart's lines rather than on its price.

**Port verification now or later.** Verify Ported Number sends the SMS code; Defer Port Verification leaves the line on its temporary number and the order opens a ticket so the team contacts the customer. The 2026-11-17 meeting describes the "text code now or verify later" choice as opening a support ticket.

**ID: Persona or manual review.** Verify Id With Persona and Enter Id Details Manually both end on Confirm Details. The skipped path puts the ID in manual review (up to 48 hours); Create Order Ticket opens the ticket for the team, and View Order Result shows **Almost there!** instead of **You're all set!**. Record Kyc Inquiry keeps the verified flag and whether a ticket is required on the KYC inquiry, apart from the customer profile.

**Manage Credentials is its own epic.** Sign in, password recovery, and sign out act on the same credentials for an onboarding customer and a subscriber, so they sit once; their tests already live under `tests/access-my-paradise/`. The two backlog stories from the meeting are the two ways a customer reaches Set New Password.

**Sizes.** The map has 7 epics, each a stage of the prototype or the credentials around it: Choose Lines 7, Create Account 4, Finish Order 4, Set Up Lines 9, Verify Identity 4, Place Order 7, Manage Credentials 6.

---

## Scope boundary

**In scope:** Onboarding as the prototype shows it (several lines per order, family discount, vouchers, the Promo plan, line nicknames, the order checklist with Edit, port-in with a temporary number, physical SIM by ICCID or store pickup, ID by Persona or manual review, payment with a pro-rated first bill, the result grouped by line). Manage Credentials, with the two backlog password stories.

**Out of scope:** Self-care after the order (the previous map's Serve A Subscriber: dashboard, profile, support, billing, services), taken off the map on 2026-11-18 until Leo's self-care prototype arrives; its tests stay under `tests/serve-a-subscriber/`. Federated sign-in (Google, Apple). Changing the account email (**Change** on *Check your email!*), the country lists behind each plan, and the self-care screens behind **Go to my account** and **Understand your first bill**, which the prototype does not show. Self-care for several lines waits for Leo's self-care prototype.
