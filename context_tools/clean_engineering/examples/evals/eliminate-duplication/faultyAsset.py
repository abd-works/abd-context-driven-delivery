def subtotal(line_items):
    total = 0
    for item in line_items:
        total += item.extended_price
    return total

def backup_subtotal(line_items):
    total = 0
    for item in line_items:
        total += item.extended_price
    return total
