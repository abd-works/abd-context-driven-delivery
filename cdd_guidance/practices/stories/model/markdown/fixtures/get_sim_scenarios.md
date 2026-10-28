---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Sub-epic: Get Sim

### Evidence

| Source | Note |
| --- | --- |
| `pml-domainmodel/stories/onboard-a-customer/get-sim/` | Select Sim, Enter Existing Sim, Activate Sim (adapted) |
| `pml-my/src/pages/Onboarding/pages/SelectSim/ProspectSelecSim.tsx`, `ProspectPSim`, `useIccid.ts` | SIM choice, the cart update and its failure message, the next page (observed) |
| `tests/onboard-a-customer/get-sim/get_sim.story.shared.ts` | the shared story these scenarios describe; API `src/inventory/sim/sim-routes.ts` |

### Domain terms

- ++[onboarding cart](../../../src/.context/domain-model.md#onboarding-entity)++ — the prospect's subscription while onboarding: plan, number, SIM type, ICCID, and the onboarding step it is on.
- ++[SIM choice](../../../src/.context/domain-model.md#sim-value-object)++ — the SIM type the Customer picks for the cart: an eSIM or a Paradise SIM card (pSIM).
- ++ICCID++ — the number printed on a physical SIM card. ICCID inventory holds the cards that can be attached.
- ++waiting for pSIM++ — the order was placed with a Paradise SIM card that has no ICCID yet; the card is activated after the order.

> In steps: ++example++ names a row of a table below; {field} is a column of the scenario's Examples. Values live in the tables only.

## Examples

### onboarding cart

| onboarding cart | plan | number | SIM type | ICCID | waiting for pSIM | onboarding step |
| --- | --- | --- | --- | --- | --- | --- |
| ++cart ready to choose SIM++ | Essentials | 4415550101 |  |  |  | Select Sim |
| ++cart waiting for pSIM++ | Essentials | 4415550101 | pSIM |  | yes |  |
| ++pSIM cart not waiting++ | Essentials | 4415550101 | pSIM |  | no |  |
| ++pSIM cart never waiting++ | Essentials | 4415550101 | pSIM |  |  | Select Sim |

### messages

| message | text |
| --- | --- |
| ++SIM selection failed++ | Failed to select your sim |
| ++ICCID format rejected++ | Please enter a valid iccid |
| ++ICCID not in inventory++ | Invalid ICCID. |
| ++pSIM activation rejected++ | Could not complete pSIM activation. |

---

# Story: Select Sim

### Background

*Given* the Customer has the ++[onboarding cart](../../../src/.context/domain-model.md#onboarding-entity)++ ++cart ready to choose SIM++  

#### Scenario: Choose eSIM

*Given* no [SIM](../../../src/.context/domain-model.md#sim-value-object) type is on the ++[onboarding cart](../../../src/.context/domain-model.md#onboarding-entity)++  
*When* the **Customer** selects the ++SIM choice++ ++eSIM++  
*Then* the stored ++onboarding cart++ holds the ++eSIM++ SIM type  
  *But* the ++onboarding cart++ has no ++ICCID++  
  *And* the stored ++onboarding cart++ is on ++Verify ID++  

#### Scenario: Choose eSIM — cart update fails

*Given* the ++[onboarding cart](../../../src/.context/domain-model.md#onboarding-entity)++ cannot be updated  
*When* the **Customer** selects the ++[SIM choice](../../../src/.context/domain-model.md#sim-value-object)++ ++eSIM++  
*Then* the SIM selection fails with ++SIM selection failed++  
  *And* the stored ++onboarding cart++ has no SIM type  
  *And* the stored ++onboarding cart++ has no ++ICCID++  

# Story: Enter Existing Sim

### Background

*Given* the Customer has the ++[onboarding cart](../../../src/.context/domain-model.md#onboarding-entity)++ ++cart ready to choose SIM++  

#### Scenario: Enter existing SIM

*Given* ICCID inventory holds the ++ICCID++ ++valid ICCID++  
*When* the **Customer** attaches the ++ICCID++ ++valid ICCID++  
*Then* the stored ++[onboarding cart](../../../src/.context/domain-model.md#onboarding-entity)++ holds the ++Paradise SIM card++ [SIM](../../../src/.context/domain-model.md#sim-value-object) type and the ++valid ICCID++ stored ICCID  
  *And* the stored ++onboarding cart++ is on ++Verify ID++  

Observed on the live screen when verification is off: a successful port also stores the temporary number and continues to Select Sim, without a verification step.

#### Scenario Outline: Port the number is rejected

*When* the Customer ports ++portability++ ++${example}++  
*Then* the line shows *${message}*  
  *And* the line has no [portability](../../../src/.context/domain-model.md#portability-aggregate-root-entity)  
  *And* the Customer stays on Pick Number  

##### Examples

| example | message |
| --- | --- |
| incomplete port number | Please enter the full Bermuda number. |
| no provider | Please select a provider. |
| valid portability that cannot receive a message | This number is invalid. |

## Changed to follow pml-my

- Choose eSIM — cart update fails: the message is *Failed to select your sim* with no full stop (observed: pml-my ProspectSelecSim.tsx `enqueueSnackbarError`). Choose Paradise SIM card — cart update fails shows no message (observed: pml-my useIccid.ts sends the cart update and shows nothing when it fails).
- Choose Paradise SIM card: the cart moves on to Verify ID, as for eSIM; the card without an ICCID is collected after the order (observed: pml-my ProspectPSim `nextPage` '../verify-id').
