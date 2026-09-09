class CartTotal:
    def subtotal(self, line_items):
        return sum(item.extended_price for item in line_items)

    def write_audit(self, path, value):
        with open(path, "w") as audit:
            audit.write(str(value))

    def calculate_average(self, values):
        return sum(values) / len(values)
