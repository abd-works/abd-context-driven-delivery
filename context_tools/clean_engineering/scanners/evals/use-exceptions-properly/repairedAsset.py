"""
"""
def load_cart(path):
    try:
        return open(path).read()
    except OSError as error:
        raise RuntimeError("cart unavailable") from error
