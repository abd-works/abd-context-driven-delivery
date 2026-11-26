---
fidelity: [model]
artifact: [ce-domain-model]
format: md
---

# Fulfilment

**Module:** `src/fulfilment`

The parcels the shop sends for paid orders.

---

## Shipment

A shipment and its faster kind.

### **Shipment** <<Aggregate Root>>

+ Shipment(order: Order, address: str)
------
+ address: str
+ dispatched: bool
+ << association >> order: Order
----
+ dispatch(): None
	-> Order.total
	// an order whose payment is not authorised is refused
+ days_to_arrive(): int

### **ExpressShipment** <<Entity>> : Shipment

+ ExpressShipment(order: Order, address: str, courier: str)
------
+ courier: str
----
+ days_to_arrive(): int
	// always one day
