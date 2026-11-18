Practice with the most rules: ddd (51)
Total rules: 190 (across 7 practices)

# Practice headings

Practice folders: the subfolders of `cdd_guidance/practices` that hold a `{name}.md`.
Skipped: `_examples` (shared example folder, no `_examples.md`; holds `car/`) and `sketch_document` (Python only, no `sketch_document.md`).

Rule count method: distinct names in bullet lines of the form `- **`rule-name`** — ...` in the practice's own `{practice}.md` (each bullet whose text starts with a bold backticked name, duplicates counted once). Note: clean_engineering's fidelity rules are written as plain backticked bullets (`- `name` —`) and so are not counted; with them it has 55. ux has 4 such plain bullets (20 with them).

## agent_bdd

  - ## Overview
  - ## Guidance
    - ### Harness
    - ### instruct vs instruct_use_tool
    - ### Session lifecycle
    - ### Assertions
    - ### Timeouts
    - ### Failures
  - ## Shared rules
- # Generate
  - ## Common mistakes still being made
- Rules: 16
- Examples: generate-action.py, repair-action.py, shell-captures.py

## bdd

  - ## Overview
  - ## Guidance
  - ## Shared rules
  - ## Fidelities
    - ### behavior
      - #### Overview
      - #### Guidance
      - #### Scaffold
      - #### Rules
    - ### realization
      - #### Overview
      - #### Sketch
      - #### Guidance
      - #### Scaffold
      - #### Rules
    - ### development
      - #### Overview
      - #### Guidance
      - #### Coverage check (existing module)
      - #### The RED-GREEN-REFACTOR cycle
      - #### Arrange-Act-Assert
      - #### Scaffold
      - #### Rules
  - ## Common mistakes still being made
    - ### Not nesting contexts properly
    - ### Treating results of install as install configuration
    - ### Missing the core subject under test
- Rules: 27
- Examples: examples.md, examples.py, examples.ts, faultyAsset.py

## clean_engineering

  - ## Overview
  - ## Guidance
  - ## Shared rules
  - ## Language
  - ## Fidelities
    - ### modules
      - #### Overview
      - #### Sketch
      - #### Language
      - #### Guidance
      - #### Scaffold
      - #### Rules
    - ### model
      - #### Overview
      - #### Sketch
      - #### Language
      - #### Guidance
      - #### Interfaces
      - #### Scaffold
      - #### Rules
    - ### code
      - #### Overview
      - #### Sketch
      - #### Guidance
      - #### Scaffold
      - #### Rules
  - ## Common mistakes still being made
- Rules: 3
- Examples: shopping-cart/faulty/examples.md, shopping-cart/faulty/examples.py, shopping-cart/repaired/repairedAsset.py

## ddd

  - ## Overview
  - ## Guidance
    - ### Default folder
    - ### Document
    - ### Generate
  - ## Shared rules
  - ## Fidelities
    - ### bounded_context
      - #### Overview
      - #### Sketch
      - #### Guidance
      - #### Scaffold
      - #### Rules
    - ### model
      - #### Overview
      - #### Sketch
      - #### Guidance
      - #### Scaffold
      - #### Rules
    - ### tactics
      - #### Overview
      - #### Sketch
      - #### Guidance
      - #### Scaffold
      - #### Rules
  - ## Common mistakes still being made
- Rules: 51
- Examples: examples.md, faultyAsset.py

## stories

  - ## Overview
  - ## Guidance
  - ## Shared rules
  - ## Fidelities
    - ### story_map
      - #### Overview
      - #### Sketch
      - #### Guidance
      - #### Scaffold
      - #### Rules
    - ### scenarios
      - #### Overview
      - #### Sketch
      - #### Guidance
      - #### Scaffold
      - #### Rules
      - #### Scenario realizations (default on)
    - ### acceptance_tests
      - #### Overview
      - #### Sketch
      - #### Guidance
      - #### Scaffold
      - #### Rules
  - ## Common mistakes still being made
- Rules: 43
- Examples: HandleRequest_story.test.ts, manage-customer-orders/examples.md, manage-customer-orders/md/scenario-inline.md, manage-customer-orders/md/scenario-outline.md, manage-customer-orders/md/story-map.md, manage-customer-orders/md/thin-slice.md, manage-customer-orders/py/manage-customer-orders/cancel-order/process-cancellation-refund/process_cancellation_refund_stories.py, manage-customer-orders/py/manage-customer-orders/cancel-order/request-order-cancellation/request_order_cancellation_stories.py, manage-customer-orders/py/manage-customer-orders/conftest.py, manage-customer-orders/py/manage-customer-orders/manage_customer_orders_helper.py, manage-customer-orders/py/manage-customer-orders/place-new-order/add-item-to-cart/add_item_to_cart_stories.py, manage-customer-orders/py/manage-customer-orders/place-new-order/browse-product-catalog/browse_product_catalog_stories.py, manage-customer-orders/py/manage-customer-orders/place-new-order/enter-shipping-address/enter_shipping_address_stories.py, manage-customer-orders/py/manage-customer-orders/place-new-order/select-delivery-option/select_delivery_option_stories.py, manage-customer-orders/py/manage-customer-orders/place-new-order/submit-order/submit_order_stories.py, manage-customer-orders/py/manage-customer-orders/story-context.md, manage-customer-orders/py/manage-customer-orders/story_runner.py, manage-customer-orders/py/manage-customer-orders/story_types.py, manage-customer-orders/py/manage-customer-orders/track-order-status/send-shipment-notification/send_shipment_notification_stories.py, manage-customer-orders/py/manage-customer-orders/track-order-status/view-current-order-status/view_current_order_status_stories.py, telco-website/examples.md, telco-website/onboard-a-customer/create-customer/create-unconfirmed-user/create_unconfirmed_user_story.test.md, telco-website/onboard-a-customer/create-customer/create-unconfirmed-user/create_unconfirmed_user_story.test.ts, telco-website/onboard-a-customer/create-customer/examples/account-credentials.examples.ts, telco-website/onboard-a-customer/create-customer/examples/identity-provider-user.examples.ts, telco-website/onboard-a-customer/create-customer/examples/purchasable-plans.examples.ts, telco-website/onboard-a-customer/story-map.md

## tdd

  - ## Overview
  - ## Guidance
    - ### Choose the flow first
    - ### Red, green, refactor
    - ### Arrange, act, assert
    - ### Test doubles and heavy coverage
    - ### Fixtures and example data
    - ### Tiers by speed
    - ### Make slow tests fast first
    - ### Cadence
    - ### Reviewing e2e screens
    - ### When stuck
  - ## Shared rules
  - ## stories-acceptance-tests, bdd-development
    - ### Rules
  - ## clean-engineering-code
    - ### Rules
  - ## stories-acceptance-tests
  - ## bdd-development
    - ### Rules
  - ## ddd-tactics
    - ### Rules
- Rules: 34
- Examples: no _examples folder

## ux

  - ## Overview
  - ## Guidance
  - ## Shared rules
  - ## Fidelities
    - ### ia
      - #### Overview
      - #### Sketch
      - #### Guidance
      - #### Scaffold
      - #### Rules
    - ### mockup
      - #### Overview
      - #### Sketch
      - #### Guidance
      - #### Scaffold
      - #### Rules
    - ### front_end_code
      - #### Overview
      - #### Sketch
      - #### Guidance
      - #### Scaffold
      - #### Rules
  - ## Common mistakes still being made
- Rules: 16
- Examples: checkout.js, fakeAdapter.js
