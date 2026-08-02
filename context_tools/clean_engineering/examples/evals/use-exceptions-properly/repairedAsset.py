"""
# @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
"""
def load_cart(path):
    try:
        return open(path).read()
    except OSError as error:
        raise RuntimeError("cart unavailable") from error
