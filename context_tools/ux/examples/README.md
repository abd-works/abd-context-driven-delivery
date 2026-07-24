# UX examples

Worked samples of UX output (mockup HTML, story modules, domain JS) — not part of the `story-demo` runtime package.

| Example | What it shows |
|--------|----------------|
| `manage-customer-orders/` | Place New Order greybox + Story Demo shell wiring |
| `shopping_cart/` | Domain modules used by that example |

## Run

From the repo root:

```
node context_tools/ux/story-demo/run.mjs
```

Then open:

`http://localhost:3000/context_tools/ux/examples/manage-customer-orders/place-new-order/place-new-order.html`

Optional: `PORT=3001` or `STORY_DEMO_EXAMPLE=/path/to/other.html`.
