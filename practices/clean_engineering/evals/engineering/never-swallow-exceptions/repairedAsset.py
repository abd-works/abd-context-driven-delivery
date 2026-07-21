"""
# @toolset-manifest python -m tools manifest clean_code.clean_code:CleanCode
"""
def load_cart(path):
    try:
        return open(path).read()
    except OSError as error:
        raise RuntimeError("cart unavailable") from error
