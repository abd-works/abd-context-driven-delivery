package manage_customer_orders.cancel_order.request_order_cancellation;

import stories.StoryTypes.Story;
import stories.StoryTypes.Scenario;
import stories.StoryTypes.Interaction;
import java.util.List;
import java.util.Map;

public final class RequestOrderCancellationStories {
    public static final Story STORY = new Story() {
        @Override public String story()  { return "Request Order Cancellation"; }
        @Override public String actor()  { return "Customer"; }
        @Override public List<String> domainTerms() {
            return List.of("Order", "Cancellation Request", "Cancellation Reason", "Order Status");
        }
        @Override public List<String> evidence() {
            return List.of(
                "Cancellation policy doc v2 §3",
                "Customer support call review 2026-05-18"
            );
        }
        @Override public Map<String, Scenario> scenarios() {
            return Map.of(
                "cancellationAcceptedBeforeShipment", new Scenario(
                    "cancellation accepted while the order is still placed",
                    List.of("an Order \"ORD-4200080\" in status placed"),
                    List.of(new Interaction(
                        List.of("the Customer submits a Cancellation Request with reason \"changed mind\""),
                        List.of(
                            "the Order status changes to cancelled",
                            "And the Cancellation Request records reason \"changed mind\""
                        )
                    ))
                ),
                "cancellationRejectedAfterShipment", new Scenario(
                    "cancellation rejected once the shipment is on the way",
                    List.of("an Order \"ORD-4200081\" in status shipped"),
                    List.of(new Interaction(
                        List.of("the Customer submits a Cancellation Request"),
                        List.of(
                            "the Cancellation Request is rejected",
                            "But the Order remains in status shipped"
                        )
                    ))
                )
            );
        }
    };
}
