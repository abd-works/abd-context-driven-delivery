"""
"""
def checkout_total(line_items):
    return sum(line_item.extended_price for line_item in line_items)
