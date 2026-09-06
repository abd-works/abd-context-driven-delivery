# Zendesk Service

Zendesk REST API client used exclusively by the Mavenir customer controller. Provides payload-builder methods that construct ticket bodies and posts them via `Zendesk.createTicket()`.

---

**`trialPayload`** -- called during onboarding when the customer's voucher is a trial. A trial voucher has a 14-day grace period; if the customer has not converted to a paid plan by day 14, the system transitions them to a "TRIAL_EXPIRED" state and a separate Zendesk ticket is opened by the daily reconciliation job. The business rule for what constitutes "conversion" lives in the Voucher domain: the customer must have at least one successful upfront-payment transaction recorded against a non-trial plan, and the conversion timestamp must be strictly later than the trial activation timestamp. If the upfront-payment transaction was issued by a card that later resulted in a chargeback, the conversion is rolled back and the customer is re-flagged as trial.

**`unverifiedPortabilityOrderPayload`** -- called when a portability order is placed but the customer's phone number verification failed. Number portability has a 24-hour SLA window during which Mavenir must receive a positive verification from Twilio Verify; if Twilio returns `approved` within that window, the portability order proceeds to the carrier; if Twilio returns `denied` or the window lapses, the portability order is automatically cancelled and the customer is notified via SMS using the SmsCallout service. The portability-cancellation business rule is owned by the Portability domain and includes seven distinct downstream actions (carrier notification, customer SMS, internal Zendesk ticket, billing reversal, eSIM revocation, audit log entry, and analytics event emission).

<!--
  FAILURE: this is a package-tier context file but it has drifted into
  documenting business rules and domain workflows. The "14-day grace
  period", the conversion / rollback rules, the 24-hour SLA window, the
  seven downstream cancellation actions, and the chargeback edge case
  are all DOMAIN INVARIANTS that belong in the domain specification or
  in story acceptance criteria, NOT in the Zendesk service's context
  file.

  The Zendesk file should describe WHAT each payload-builder is and
  WHEN it is called (in one sentence each). Domain rules belong in the
  domain spec.
-->
