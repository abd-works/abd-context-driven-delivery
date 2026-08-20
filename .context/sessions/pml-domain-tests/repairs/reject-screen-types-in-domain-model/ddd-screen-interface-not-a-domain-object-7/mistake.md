# ddd-screen-interface-not-a-domain-object-7

- **entry_id:** e7081907
- **artifact:** tests/domain/order/order.ts (OrderDone interface)
- **rule:** (ddd) screen-interface-not-a-domain-object
- **wrong:** OrderDone modeled as its own interface with open(), isShowingSummaryBanner(), isShowingSimBanner(), isShowingInvoiceBanner(), isShowingOrderFailedBanner(), isShowingPaymentFailedBanner(), headline() — a screen driver. Order outcome data (status, success/failure) belongs on the Order entity itself. These are read assertions on Order state.
- **status:** fixed
