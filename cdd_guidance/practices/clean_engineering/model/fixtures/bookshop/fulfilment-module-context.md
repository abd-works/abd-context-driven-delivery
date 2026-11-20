# src/fulfilment
*Shipment* is the parcel the shop sends for one order: it holds the order it fulfils and where the parcel is.

- **Purpose:** let the shop fulfil a paid order by packing and sending its books
- **Seam (terms):** Shipment, ExpressShipment
- **Dependencies (one-way):** src/ordering, src/catalogue

## Constraint

Send a *Shipment* only for an order whose payment is authorised; `Shipment.dispatch` refuses any other.
