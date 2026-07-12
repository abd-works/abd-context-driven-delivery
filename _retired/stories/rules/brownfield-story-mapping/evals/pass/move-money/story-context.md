# Move Money

**Status:** partially expanded

**Stories in scope:**
- *Submit Same-Day Transfer*

**Context / notes:** Evidence gathered from live system: existing `POST /payments` handler at `src/payments/api.ts:47` and `test/payments/submit.spec.ts` § "settles same-day when submitted before cutoff". Ops Lead confirmed the 15:00 ET cutoff in the 2026-06-14 interview. _Evidence: `src/payments/api.ts:47`_
