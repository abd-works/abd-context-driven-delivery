def subtotal(line_items):
    print("calculating subtotal")
    total = line_items[0].extended_price + line_items[1].extended_price
    return total
