package manage_customer_orders.place_new_order.submit_order;

import stories.StoryTypes.Story;
import stories.StoryTypes.Scenario;
import stories.StoryTypes.Interaction;
import java.util.List;
import java.util.Map;

// SubmitOrderStories.java
//
// One Story constant per file — the reference architecture shape. This file
// stays fully regeneratable: no test-framework calls, no user-authored logic,
// just literal scenario data. Tier implementations live next door in
// `Submit Order<Tier>Tier.java` (write-once, hand-owned after scaffolding).
//
// Fidelity progression across scenarios (Exploration → Specification):
//
//   1. "submissionSucceeds"               — Exploration happy path
//   2. "submissionRejectedForDeclinedCard" — Specification negative flow
//   3. "submissionOutlineByPaymentStatus"  — Specification outline (multi-then)

public final class SubmitOrderStories {
    public static final Story STORY = new Story() {
        @Override public String story()  { return "Submit Order"; }
        @Override public String actor()  { return "Customer"; }
        @Override public List<String> domainTerms() {
            return List.of("Order", "Cart", "Payment Method", "Order Number", "Order Status");
        }
        @Override public List<String> evidence() {
            return List.of(
                "Checkout workshop 2026-05-04 — happy-path wall walk",
                "API spec v3 — POST /orders §\"submission errors\""
            );
        }
        @Override public Map<String, Scenario> scenarios() {
            return Map.of(
                "submissionSucceeds", new Scenario(
                    "order accepted for a valid cart and payment method",
                    List.of(
                        "a Cart CART-9001 containing 3 Items totalling 149.98 USD",
                        "And a Payment Method Visa 4242 with status authorised"
                    ),
                    List.of(new Interaction(
                        List.of("the Customer submits the Order"),
                        List.of(
                            "an Order is created with status placed",
                            "And an Order Number matching ORD-<7 digits> is returned",
                            "And the Cart is emptied"
                        )
                    ))
                ),
                "submissionRejectedForDeclinedCard", new Scenario(
                    "order rejected when the payment method is declined",
                    List.of(
                        "a Cart CART-9002 totalling 89.50 USD",
                        "And a Payment Method MasterCard 5150 in status declined"
                    ),
                    List.of(new Interaction(
                        List.of("the Customer submits the Order"),
                        List.of(
                            "the Order is rejected with reason payment_declined",
                            "But the Cart contents are preserved for retry"
                        )
                    ))
                ),
                "submissionOutlineByPaymentStatus", new Scenario(
                    "submission outcome varies with payment method status",
                    List.of(
                        "a Cart with a known total and currency",
                        "And a Payment Method with a known status"
                    ),
                    List.of(new Interaction(
                        List.of("the Customer submits the Order"),
                        List.of(
                            "the Order status is set for an authorised payment to placed",
                            "And the Order status is set for a declined payment to rejected",
                            "And the Order status is set for an expired payment to rejected"
                        )
                    ))
                )
            );
        }
    };
}
