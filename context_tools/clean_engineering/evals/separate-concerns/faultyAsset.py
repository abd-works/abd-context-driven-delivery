def subtotal(line_items):
    print("subtotal")
    return sum(item.extended_price for item in line_items)
