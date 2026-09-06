# UX — Procedural Guidance (ia fidelity)

## How to build the information architecture

IA answers: what screens exist, how users move between them, and what's on each screen (named regions only — no control detail yet).

1. **Start from user goals** — each distinct user goal gets a screen. "Sign up" is a screen. "Browse products" is a screen. "Manage subscription" is a screen.
2. **Map the transitions** — how does the user get from one screen to another? Click a button, select a tab, follow a wizard step? Each transition is an explicit arc.
3. **Name the regions** — each screen is divided into named slots: header, main content, sidebar, footer. At IA, these are just names — no control types yet.
4. **Group system stories with visible triggers** — a system story (background sync, notification push) groups with the closest user-visible screen that triggers or displays it.

## Screen decomposition thinking

When deciding whether something is one screen or many:

- **Different tab contents = different screens** — even if they share the same header/nav chrome. Use `chrome_of` to share the frame.
- **Different states of the same form = same screen** — editing vs viewing an order is one screen with states, not two screens.
- **Different user types seeing different things = different screens** — admin vs customer dashboard, even if the URL is the same.

## Layout pattern thinking

Before sketching a screen's regions from scratch, check `specifications/generic/` (or the brand-specific folder). There are 43 layout patterns with ready-to-adapt reference artifacts. Read the matching pattern's slots first, then alter for the real screen. Don't invent layouts when a pattern already covers the shape.

## No control detail at IA

At IA, regions are named slots only. Don't specify control types (dropdowns, radio buttons, text inputs). Don't add interaction JavaScript. Don't apply branding. Those come at mockup fidelity.
