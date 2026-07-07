package manage_customer_orders.track_order_status.view_current_order_status;

import stories.StoryTypes.Story;
import stories.StoryTypes.Scenario;
import stories.StoryTypes.Interaction;
import java.util.List;
import java.util.Map;

public final class ViewCurrentOrderStatusStories {
    public static final Story STORY = new Story() {
        @Override public String story()  { return "View Current Order Status"; }
        @Override public String actor()  { return "Customer"; }
        @Override public List<String> domainTerms() {
            return List.of("Order", "Order Status", "Timeline Event");
        }
        @Override public List<String> evidence() {
            return List.of("Order tracking discovery session 2026-05-11");
        }
        @Override public Map<String, Scenario> scenarios() {
            return Map.of(
                "mainFlow", new Scenario(
                    "customer sees the latest status of a placed order",
                    List.of(
                        "an Order \"ORD-4200077\" in status placed",
                        "And a Timeline Event \"payment authorised\" recorded 10 minutes ago"
                    ),
                    List.of(new Interaction(
                        List.of("the Customer opens the order detail view"),
                        List.of(
                            "the Order status placed is displayed prominently",
                            "And the Timeline shows the payment-authorised event"
                        )
                    ))
                )
            );
        }
    };
}
