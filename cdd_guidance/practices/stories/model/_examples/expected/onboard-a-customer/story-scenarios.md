---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Onboard A Customer

## Domain terms

- ++account credentials++ — email, password, confirmPassword; `validate`, `register`, `signIn`. Sign-in rows also live on Sign In With Existing Account.
- ++account credential requirements++ — live rule checklist on Create Account
- ++plan++ — sellable offering the User selects on the Paradise Mobile site
- ++Cognito user++ — Cognito pool user (unconfirmed until ++validation code++ is confirmed). See `stories/system-terms.md`.
- ++Mavenir customer++ / ++PML customer++ — create-time rows live on Create Customer (`stories/onboard-a-customer/create-customer/create_customer_story.spec.md`).

## Examples

### account credentials

| account credentials | example | email | password | confirmPassword |
| --- | --- | --- | --- | --- |
| account credentials | valid account credentials | [Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com) | Spider-man99p | Spider-man99p |
| account credentials | invalid password letters | [Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com) | spider-man99p | spider-man99p |
| account credentials | invalid password number | [Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com) | Spider-manpp | Spider-manpp |
| account credentials | invalid password symbol | [Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com) | Spiderman99 | Spiderman99 |
| account credentials | invalid password length | [Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com) | Sp1!Man | Sp1!Man |
| account credentials | invalid confirm required | [Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com) | Spider-man99p |  |
| account credentials | invalid confirm mismatch | [Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com) | Spider-man99p | Spider-man00p |
| account credentials | invalid email required |  | Spider-man99p | Spider-man99p |
| account credentials | invalid email format | example.prospect | Spider-man99p | Spider-man99p |
| account credentials | invalid password required | [Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com) |  |  |
| account credentials | already-registered account credentials | [Jeff.anderson@Agilebydesign.com](mailto:Jeff.anderson@Agilebydesign.com) | Stub@12345 | Stub@12345 |
| account credentials | Paradise Mobile account credentials | [staff@paradisemobile.com](mailto:staff@paradisemobile.com) | Spider-man99p | Spider-man99p |

### plan

| plan | example | id | name | price | tagName |
| --- | --- | --- | --- | --- | --- |
| plan | Essentials | 100000000014 | Essentials | 70 |  |
| plan | Data Freedom | 100000000019 | Data Freedom | 55 |  |
| plan | Ace | 100000000042 | Ace | 99 | Best value |
| plan | Atlas | 100000000041 | Atlas | 129 |  |
| plan | Internal Test Plan PROMO | 100000000008 | Internal Test Plan PROMO | 0 |  |
