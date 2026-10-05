def load_cart(path):
    try:
        return open(path).read()
    except:
        pass
