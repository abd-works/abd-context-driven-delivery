from story_test import scenario, story, then, when

with story("Submit Order"):
    with scenario("accepted"):
        with when("the Customer submits"):
            pass
        with then("an Order exists"):
            pass
    with scenario("rejected"):
        with when("the Customer submits"):
            pass
        with then("an Order is refused"):
            pass
