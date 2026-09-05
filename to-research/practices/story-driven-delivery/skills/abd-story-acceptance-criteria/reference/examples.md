# Acceptance Criteria — Example

Worked example using the same **Manage Customer Orders** domain as `abd-story-mapping/reference/examples.md`.

Full multi-story sample (Browse Product Catalog, Add Item To Cart, Submit Order): **`../templates/acceptance-criteria-example.md`**.

Below is one story in full so agents can read a single complete pattern without leaving `reference/`.

---

## Story: Browse Product Catalog

**Story type:** user

### Domain terms

- *Product Catalog* — browsable list of products available to order
- *Category* — grouping used to narrow what the customer sees
- *Product Detail* — name, description, price, and image for one product
- *Out Of Stock* — product not available to add to an order right now

### Acceptance criteria

1. **WHEN** the customer opens the *Product Catalog*
   **THEN** the system displays available products grouped by *Category*
   **AND** each row shows at least product name and price
   **Evidence:** Order Management Workshop — whiteboard “Place order” flow, 2026-03-15, sticky “browse by category”

2. **WHEN** the customer selects a *Category*
   **THEN** the *Product Catalog* lists only products in that *Category*
   **Evidence:** Order Management Workshop — same session, “filter catalog by category”

3. **WHEN** the customer selects a product from the *Product Catalog*
   **THEN** the system shows *Product Detail* for that product
   **Evidence:** Order Management Workshop — “click through to product detail”

4. **WHEN** a product is *Out Of Stock*
   **THEN** the *Product Catalog* and *Product Detail* show that the product cannot be added to an order
   **BUT** the customer can still browse other products
   **Evidence:** Order Management Workshop — “don’t block browsing when one SKU is gone”

## What to notice

- Stories match **verb—noun** names from the story map; actor is in **Story type**, not the title
- **Domain terms** are defined before AC; the same *italic* terms appear in the criteria
- **when / then / and / but** — negatives use **but**; no **given** in AC
- Each AC is a **delta** or distinct case — general browse flow once, then category, detail, and out-of-stock paths
- **Evidence** cites a concrete source even for workshop-derived discovery

---

## Same story in `*-stories.ts` code format

```typescript
import type { Step, AcceptanceCriterion, Background } from '../../story-types'

export const BROWSE_PRODUCT_CATALOG = {
  story: `Browse Product Catalog`,
  actor: `Customer`,

  acceptance_criteria: [
    [
      { when: `the *customer* opens the **Product Catalog**` },
      { then: `the system displays available products grouped by **Category**` },
      { and:  `each row shows at least product name and price` },
    ],
    [
      { when: `the *customer* selects a **Category**` },
      { then: `the **Product Catalog** lists only products in that **Category**` },
    ],
    [
      { when: `the *customer* selects a product from the **Product Catalog**` },
      { then: `the system shows **Product Detail** for that product` },
    ],
    [
      { when: `a product is **Out Of Stock**` },
      { then: `the **Product Catalog** and **Product Detail** show the product cannot be added` },
      { but:  `the *customer* can still browse other products` },
    ],
  ] as const satisfies readonly AcceptanceCriterion[],

  domain_terms: ['Product Catalog', 'Category', 'Product Detail', 'Out Of Stock'] as const,
  evidence: [
    'Order Management Workshop — whiteboard "Place order" flow, 2026-03-15',
    'Order Management Workshop — "filter catalog by category"',
    'Order Management Workshop — "click through to product detail"',
    'Order Management Workshop — "don\'t block browsing when one SKU is gone"',
  ] as const,

  customerOpensProductCatalogSystemDisplays: {
    name: `customer opens product catalog system displays`,
    steps: [
      { when: `the *customer* opens the **Product Catalog**` },
      { then: `the system displays available products grouped by **Category**` },
      { and:  `each row shows at least product name and price` },
    ] as const satisfies readonly Step[],
  },

  customerSelectsCategoryProductCatalogLists: {
    name: `customer selects category product catalog lists`,
    steps: [
      { when: `the *customer* selects a **Category**` },
      { then: `the **Product Catalog** lists only products in that **Category**` },
    ] as const satisfies readonly Step[],
  },

  customerSelectsProductProductDetail: {
    name: `customer selects product product detail`,
    steps: [
      { when: `the *customer* selects a product from the **Product Catalog**` },
      { then: `the system shows **Product Detail** for that product` },
    ] as const satisfies readonly Step[],
  },

  productOutOfStockProductCatalogShows: {
    name: `product out of stock product catalog shows`,
    steps: [
      { when: `a product is **Out Of Stock**` },
      { then: `the **Product Catalog** and **Product Detail** show the product cannot be added` },
      { but:  `the *customer* can still browse other products` },
    ] as const satisfies readonly Step[],
  },

} as const
```

The `acceptance_criteria` array and the named scenario objects contain **identical steps** — the criteria drive what the scenarios test.
