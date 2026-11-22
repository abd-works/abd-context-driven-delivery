import React, { useState } from "react";
import type { Order } from "./api";
import { type Cart, Country, bookshop } from "./api";

interface CheckoutProps {
  cart: Cart;
  onPaid: (order: Order) => void;
  note?: string;
}

type Step = "address" | "payment";

const COUNTRIES: Country[] = ["Canada", "France"];

/** Screen: Checkout. Stories: Pay For Order. */
export function CheckoutView({ cart, onPaid, note = "Total: due" }: CheckoutProps): JSX.Element {
  const [city, setCity] = useState<string>("");
  const [country, setCountry] = useState<Country>(COUNTRIES[0]);
  const cityMissing: boolean = city.trim() === "";

  const handleCity = (event: React.ChangeEvent<HTMLInputElement>): void => setCity(event.target.value);

  async function handlePay(): Promise<void> {
    const order = (await bookshop.checkOut({ city, country })) as Order;
    onPaid(order!);
  }

  return (
    <main data-screen="Checkout">
      <p>Total: {cart.total} as charged, {note}</p>
      <label className={cityMissing ? "error" : ""}>City <input type="text" value={city} onChange={handleCity} /></label>
      <select value={country} onChange={(e) => setCountry(e.target.value as Country)}>
        {COUNTRIES.map((name: Country) => (<option key={name} value={name}>{name}</option>))}
      </select>
      <button type="button" disabled={cityMissing} onClick={handlePay}>Pay</button>
    </main>
  );
}
