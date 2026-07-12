def checkout_total(line_items):
    return sum(item.extended_price for item in line_items)

def applyDiscount(total):
    return total * 0.9
