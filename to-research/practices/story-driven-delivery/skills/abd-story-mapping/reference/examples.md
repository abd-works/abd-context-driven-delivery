# Story Mapping — Example

## Example story map

(E) Manage Customer Orders
    (E) Place New Order
        (S) Customer --> Browse Product Catalog
        (S) Customer --> Add Item To Cart
        (S) Customer --> Enter Shipping Address
        (S) Customer --> Select Delivery Option
        (S) Customer --> Submit Order
    (E) Track Order Status
        (S) Customer --> View Current Order Status
        (S) System --> Send Shipment Notification
    (E) Cancel Order
        (S) Customer --> Request Order Cancellation
        (S) System --> Process Cancellation Refund

## What to notice

- Epic names are **verb–noun**, no actor in the name
- Actor goes before `-->`, not in the story name
- Each story is one observable behavior — not a task or feature
- Sub-epics group stories into coherent flows
