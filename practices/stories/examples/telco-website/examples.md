# telco-website — golden example

Reference layout for **`shared-example-fixtures`** and story hierarchy on disk. Derived from Paradise Mobile `onboard-a-customer/create-customer/create-unconfirmed-user`.

## Ideal shape

1. **Story map** at the epic root — discovery hierarchy on disk.
2. **Folders mirror the map** — epic → sub-epic → nested sub-epic / story.
3. **`examples/` at the sub-epic** — named fixture files shared by every story under that sub-epic (`create-customer/examples/`).
4. **Per story** — markdown spec (`story-scenarios.md`) and acceptance spec (`*_story.spec.ts`); both name the same examples; code imports from the sub-epic `examples/` folder.

```
onboard-a-customer/
  story-map.md
  create-customer/                          # (E) Create Customer
    examples/                               # sub-epic — shared fixtures
      account-credentials.examples.ts
      purchasable-plans.examples.ts
      identity-provider-user.examples.ts
    create-unconfirmed-user/                # (E) Create Unconfirmed User
      story-scenarios.md                    # scenarios fidelity — GWT + Examples tables
      create_unconfirmed_user_story.spec.ts # acceptance_tests — imports ../../examples/
```

Markdown holds domain terms, example tables, and behaviors. Code holds runnable scenarios that import fixtures — never duplicate literals in either file.
