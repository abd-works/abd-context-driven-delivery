"""Fault/clean snippets from historical multi_language_scanners_spec.py (main @ c608b483)."""

_KEEP_OPERATIONS_SMALL_FOCUSED_FAULT = {
    'python': 'class Work:\n    def huge(self):\n        v1 = 1\n        v2 = 2\n        v3 = 3\n        v4 = 4\n        v5 = 5\n        v6 = 6\n        v7 = 7\n        v8 = 8\n        v9 = 9\n        v10 = 10\n        v11 = 11\n        v12 = 12\n        v13 = 13\n        v14 = 14\n        v15 = 15\n        v16 = 16\n        v17 = 17\n        v18 = 18\n        v19 = 19\n        v20 = 20\n        v21 = 21\n        return v1\n',
    'typescript': 'class Work {\n  huge(): number {\n    const v1 = 1;\n    const v2 = 2;\n    const v3 = 3;\n    const v4 = 4;\n    const v5 = 5;\n    const v6 = 6;\n    const v7 = 7;\n    const v8 = 8;\n    const v9 = 9;\n    const v10 = 10;\n    const v11 = 11;\n    const v12 = 12;\n    const v13 = 13;\n    const v14 = 14;\n    const v15 = 15;\n    const v16 = 16;\n    const v17 = 17;\n    const v18 = 18;\n    const v19 = 19;\n    const v20 = 20;\n    const v21 = 21;\n    return v1;\n  }\n}\n',
    'javascript': 'class Work {\n  huge() {\n    const v1 = 1;\n    const v2 = 2;\n    const v3 = 3;\n    const v4 = 4;\n    const v5 = 5;\n    const v6 = 6;\n    const v7 = 7;\n    const v8 = 8;\n    const v9 = 9;\n    const v10 = 10;\n    const v11 = 11;\n    const v12 = 12;\n    const v13 = 13;\n    const v14 = 14;\n    const v15 = 15;\n    const v16 = 16;\n    const v17 = 17;\n    const v18 = 18;\n    const v19 = 19;\n    const v20 = 20;\n    const v21 = 21;\n    return v1;\n  }\n}\n',
    'java': 'class Work {\n  int huge() {\n    int v1 = 1;\n    int v2 = 2;\n    int v3 = 3;\n    int v4 = 4;\n    int v5 = 5;\n    int v6 = 6;\n    int v7 = 7;\n    int v8 = 8;\n    int v9 = 9;\n    int v10 = 10;\n    int v11 = 11;\n    int v12 = 12;\n    int v13 = 13;\n    int v14 = 14;\n    int v15 = 15;\n    int v16 = 16;\n    int v17 = 17;\n    int v18 = 18;\n    int v19 = 19;\n    int v20 = 20;\n    int v21 = 21;\n    return v1;\n  }\n}\n',
}

_KEEP_OPERATIONS_SMALL_FOCUSED_CLEAN = {
    'python': 'class Work:\n    def tiny(self):\n        return 1\n',
    'typescript': 'class Work { tiny(): number { return 1; } }\n',
    'javascript': 'class Work { tiny() { return 1; } }\n',
    'java': 'class Work { int tiny() { return 1; } }\n',
}

_SIMPLIFY_CONTROL_FLOW_FAULT = {
    'python': 'class Gate:\n    def decide(self, a, b, c):\n        if a:\n            if b:\n                if c:\n                    if a and b:\n                        return 1\n        return 0\n',
    'typescript': 'class Gate {\n  decide(a: boolean, b: boolean, c: boolean): number {\n    if (a) { if (b) { if (c) { if (a && b) { return 1; } } } }\n    return 0;\n  }\n}\n',
    'javascript': 'class Gate {\n  decide(a, b, c) {\n    if (a) { if (b) { if (c) { if (a && b) { return 1; } } } }\n    return 0;\n  }\n}\n',
    'java': 'class Gate {\n  int decide(boolean a, boolean b, boolean c) {\n    if (a) { if (b) { if (c) { if (a && b) { return 1; } } } }\n    return 0;\n  }\n}\n',
}

_SIMPLIFY_CONTROL_FLOW_CLEAN = {
    'python': 'class Gate:\n    def decide(self, ready):\n        if not ready:\n            return 0\n        return 1\n',
    'typescript': 'class Gate { decide(ready: boolean): number { if (!ready) { return 0; } return 1; } }\n',
    'javascript': 'class Gate { decide(ready) { if (!ready) { return 0; } return 1; } }\n',
    'java': 'class Gate { int decide(boolean ready) { if (!ready) { return 0; } return 1; } }\n',
}

_ELIMINATE_DUPLICATION_FAULT = {
    'python': 'class Totals:\n    def subtotal(self, items):\n        total = 0\n        for item in items:\n            total += item.price\n        return total\n    def backup_subtotal(self, items):\n        total = 0\n        for item in items:\n            total += item.price\n        return total\n',
    'typescript': 'class Totals {\n  subtotal(items: {price:number}[]): number {\n    let total = 0;\n    for (const item of items) { total += item.price; }\n    return total;\n  }\n  backup_subtotal(items: {price:number}[]): number {\n    let total = 0;\n    for (const item of items) { total += item.price; }\n    return total;\n  }\n}\n',
    'javascript': 'class Totals {\n  subtotal(items) {\n    let total = 0;\n    for (const item of items) { total += item.price; }\n    return total;\n  }\n  backup_subtotal(items) {\n    let total = 0;\n    for (const item of items) { total += item.price; }\n    return total;\n  }\n}\n',
    'java': 'class Totals {\n  int subtotal(int[] prices) {\n    int total = 0;\n    for (int price : prices) { total += price; }\n    return total;\n  }\n  int backup_subtotal(int[] prices) {\n    int total = 0;\n    for (int price : prices) { total += price; }\n    return total;\n  }\n}\n',
}

_ELIMINATE_DUPLICATION_CLEAN = {
    'python': 'class Totals:\n    def subtotal(self, items):\n        return sum(i.price for i in items)\n',
    'typescript': 'class Totals { subtotal(items: {price:number}[]): number { return items.reduce((t,i)=>t+i.price,0); } }\n',
    'javascript': 'class Totals { subtotal(items) { return items.reduce((t,i)=>t+i.price,0); } }\n',
    'java': 'class Totals {\n  int subtotal(int[] prices) {\n    int total = 0;\n    for (int price : prices) { total += price; }\n    return total;\n  }\n}\n',
}

_USE_CLEAR_FUNCTION_PARAMETERS_FAULT = {
    'python': 'class Api:\n    def send(self, a, b, c, d, e, f):\n        return a\n',
    'typescript': 'class Api { send(a:number,b:number,c:number,d:number,e:number,f:number): number { return a; } }\n',
    'javascript': 'class Api { send(a,b,c,d,e,f) { return a; } }\n',
    'java': 'class Api { int send(int a,int b,int c,int d,int e,int f) { return a; } }\n',
}

_USE_CLEAR_FUNCTION_PARAMETERS_CLEAN = {
    'python': 'class Api:\n    def send(self, request):\n        return request\n',
    'typescript': 'class Api { send(request: object): object { return request; } }\n',
    'javascript': 'class Api { send(request) { return request; } }\n',
    'java': 'class Api { Object send(Object request) { return request; } }\n',
}

_USE_DOMAIN_LANGUAGE_FAULT = {
    'python': 'class Manager:\n    def process(self):\n        return None\n',
    'typescript': 'class Manager { process(): void { return; } }\n',
    'javascript': 'class Manager { process() { return; } }\n',
    'java': 'class Manager { void process() { return; } }\n',
}

_USE_DOMAIN_LANGUAGE_CLEAN = {
    'python': 'class Cart:\n    def place_order(self):\n        return None\n',
    'typescript': 'class Cart { placeOrder(): void { return; } }\n',
    'javascript': 'class Cart { placeOrder() { return; } }\n',
    'java': 'class Cart { void placeOrder() { return; } }\n',
}

_USE_CONSISTENT_NAMING_FAULT = {
    'python': 'class Checkout:\n    def checkout_total(self, items):\n        return 1\n    def applyDiscount(self, total):\n        return total\n',
    'typescript': 'class Checkout {\n  checkout_total(items: number[]): number { return 1; }\n  applyDiscount(total: number): number { return total; }\n}\n',
    'javascript': 'class Checkout {\n  checkout_total(items) { return 1; }\n  applyDiscount(total) { return total; }\n}\n',
    'java': 'class Checkout {\n  int checkout_total(int[] items) { return 1; }\n  int applyDiscount(int total) { return total; }\n}\n',
}

_USE_CONSISTENT_NAMING_CLEAN = {
    'python': 'class Checkout:\n    def checkout_total(self, items):\n        return 1\n    def apply_discount(self, total):\n        return total\n',
    'typescript': 'class Checkout {\n  checkoutTotal(items: number[]): number { return 1; }\n  applyDiscount(total: number): number { return total; }\n}\n',
    'javascript': 'class Checkout {\n  checkoutTotal(items) { return 1; }\n  applyDiscount(total) { return total; }\n}\n',
    'java': 'class Checkout {\n  int checkoutTotal(int[] items) { return 1; }\n  int applyDiscount(int total) { return total; }\n}\n',
}

_USE_INTENTION_REVEALING_NAMES_FAULT = {
    'python': 'class Checkout:\n    def total(self, line_items):\n        to = line_items\n        return to\n',
    'typescript': 'class Checkout { total(lineItems: object): object { const to = lineItems; return to; } }\n',
    'javascript': 'class Checkout { total(lineItems) { const to = lineItems; return to; } }\n',
    'java': 'class Checkout { Object total(Object lineItems) { Object to = lineItems; return to; } }\n',
}

_USE_INTENTION_REVEALING_NAMES_CLEAN = {
    'python': 'class Checkout:\n    def total(self, line_items):\n        return line_items\n',
    'typescript': 'class Checkout { total(lineItems: object): object { return lineItems; } }\n',
    'javascript': 'class Checkout { total(lineItems) { return lineItems; } }\n',
    'java': 'class Checkout { Object total(Object lineItems) { return lineItems; } }\n',
}

_PROVIDE_MEANINGFUL_CONTEXT_FAULT = {
    'python': 'class Split:\n    def split_items(self, item1, item2):\n        return item1\n',
    'typescript': 'class Split { splitItems(item1: object, item2: object): object { return item1; } }\n',
    'javascript': 'class Split { splitItems(item1, item2) { return item1; } }\n',
    'java': 'class Split { Object splitItems(Object item1, Object item2) { return item1; } }\n',
}

_PROVIDE_MEANINGFUL_CONTEXT_CLEAN = {
    'python': 'class Split:\n    def split_items(self, left_item, right_item):\n        return left_item\n',
    'typescript': 'class Split { splitItems(leftItem: object, rightItem: object): object { return leftItem; } }\n',
    'javascript': 'class Split { splitItems(leftItem, rightItem) { return leftItem; } }\n',
    'java': 'class Split { Object splitItems(Object leftItem, Object rightItem) { return leftItem; } }\n',
}

_SEPARATE_CONCERNS_FAULT = {
    'python': 'class Math:\n    def subtotal(self, a, b):\n        print("calculating")\n        return a + b\n',
    'typescript': 'class Math { subtotal(a: number, b: number): number { print("calculating"); return a + b; } }\n',
    'javascript': 'class Math { subtotal(a, b) { print("calculating"); return a + b; } }\n',
    'java': 'class Math {\n  int subtotal(int a, int b) {\n    println("calculating");\n    return a + b;\n  }\n}\n',
}

_SEPARATE_CONCERNS_CLEAN = {
    'python': 'class Math:\n    def subtotal(self, a, b):\n        return a + b\n',
    'typescript': 'class Math { subtotal(a: number, b: number): number { return a + b; } }\n',
    'javascript': 'class Math { subtotal(a, b) { return a + b; } }\n',
    'java': 'class Math { int subtotal(int a, int b) { return a + b; } }\n',
}

_KEEP_FUNCTIONS_SINGLE_RESPONSIBILITY_FAULT = {
    'python': 'class Math:\n    def subtotal(self, a, b):\n        print("calculating")\n        return a + b\n',
    'typescript': 'class Math { subtotal(a: number, b: number): number { print("calculating"); return a + b; } }\n',
    'javascript': 'class Math { subtotal(a, b) { print("calculating"); return a + b; } }\n',
    'java': 'class Math {\n  int subtotal(int a, int b) {\n    println("calculating");\n    return a + b;\n  }\n}\n',
}

_KEEP_FUNCTIONS_SINGLE_RESPONSIBILITY_CLEAN = {
    'python': 'class Math:\n    def subtotal(self, a, b):\n        return a + b\n',
    'typescript': 'class Math { subtotal(a: number, b: number): number { return a + b; } }\n',
    'javascript': 'class Math { subtotal(a, b) { return a + b; } }\n',
    'java': 'class Math { int subtotal(int a, int b) { return a + b; } }\n',
}

_MAINTAIN_ABSTRACTION_LEVELS_FAULT = {
    'python': 'class Flow:\n    def orchestrate_checkout(self, cart):\n        open("audit.log")\n        return cart\n',
    'typescript': 'class Flow { orchestrateCheckout(cart: object): object { open("audit.log"); return cart; } }\n',
    'javascript': 'class Flow { orchestrateCheckout(cart) { open("audit.log"); return cart; } }\n',
    'java': 'class Flow {\n  Object orchestrateCheckout(Object cart) {\n    open("audit.log");\n    return cart;\n  }\n}\n',
}

_MAINTAIN_ABSTRACTION_LEVELS_CLEAN = {
    'python': 'class Flow:\n    def orchestrate_checkout(self, cart, writer):\n        writer.write_audit(cart)\n        return cart\n',
    'typescript': 'class Flow { orchestrateCheckout(cart: object, writer: any): object { writer.writeAudit(cart); return cart; } }\n',
    'javascript': 'class Flow { orchestrateCheckout(cart, writer) { writer.writeAudit(cart); return cart; } }\n',
    'java': 'class Flow {\n  Object orchestrateCheckout(Object cart, Writer writer) {\n    writer.writeAudit(cart);\n    return cart;\n  }\n}\n',
}

_KEEP_CLASSES_SINGLE_RESPONSIBILITY_FAULT = {
    'python': 'class CartService:\n    def write_audit(self, path):\n        open(path)\n    def calculate_average(self, values):\n        return sum(values) / len(values)\n',
    'typescript': 'class CartService {\n  writeAudit(path: string): void { open(path); }\n  calculateAverage(values: number[]): number { return values[0] + values[1]; }\n}\n',
    'javascript': 'class CartService {\n  writeAudit(path) { open(path); }\n  calculateAverage(values) { return values[0] + values[1]; }\n}\n',
    'java': 'class CartService {\n  void writeAudit(String path) { open(path); }\n  int calculateAverage(int[] values) { return values[0] + values[1]; }\n}\n',
}

_KEEP_CLASSES_SINGLE_RESPONSIBILITY_CLEAN = {
    'python': 'class Cart:\n    def subtotal(self, items):\n        return sum(i.price for i in items)\n',
    'typescript': 'class Cart { subtotal(items: {price:number}[]): number { return items.reduce((t,i)=>t+i.price,0); } }\n',
    'javascript': 'class Cart { subtotal(items) { return items.reduce((t,i)=>t+i.price,0); } }\n',
    'java': 'class Cart {\n  int subtotal(int[] prices) {\n    int total = 0;\n    for (int p : prices) { total += p; }\n    return total;\n  }\n}\n',
}

_USE_EXPLICIT_DEPENDENCIES_FAULT = {
    'python': 'class Service:\n    def __init__(self):\n        self.repo = CartRepository()\n',
    'typescript': 'class Service { constructor() { this.repo = new CartRepository(); } }\n',
    'javascript': 'class Service { constructor() { this.repo = new CartRepository(); } }\n',
    'java': 'class Service {\n  Service() {\n    this.repo = new CartRepository();\n  }\n}\n',
}

_USE_EXPLICIT_DEPENDENCIES_CLEAN = {
    'python': 'class Service:\n    def __init__(self, repository):\n        self.repo = repository\n',
    'typescript': 'class Service { constructor(repository: object) { this._repo = repository; } }\n',
    'javascript': 'class Service { constructor(repository) { this._repo = repository; } }\n',
    'java': 'class Service {\n  Service(CartRepository repository) {\n    this._repo = repository;\n  }\n}\n',
}

_ENFORCE_ENCAPSULATION_FAULT = {
    'python': 'class Cart:\n    def __init__(self, owner):\n        self.owner = owner\n',
    'typescript': 'class Cart { constructor(owner: string) { this.owner = owner; } }\n',
    'javascript': 'class Cart { constructor(owner) { this.owner = owner; } }\n',
    'java': 'class Cart {\n  Cart(String owner) {\n    this.owner = owner;\n  }\n}\n',
}

_ENFORCE_ENCAPSULATION_CLEAN = {
    'python': 'class Cart:\n    def __init__(self, owner):\n        self._owner = owner\n    @property\n    def owner(self):\n        return self._owner\n',
    'typescript': 'class Cart {\n  private _owner: string;\n  constructor(owner: string) { this._owner = owner; }\n}\n',
    'javascript': 'class Cart {\n  constructor(owner) { this._owner = owner; }\n}\n',
    'java': 'class Cart {\n  private String _owner;\n  Cart(String owner) { this._owner = owner; }\n}\n',
}

_STOP_WRITING_USELESS_COMMENTS_FAULT = {
    'python': 'class Totals:\n    def subtotal(self, items):\n        # return the subtotal\n        return sum(i.price for i in items)\n',
    'typescript': 'class Totals {\n  subtotal(items: {price:number}[]): number {\n    // return the subtotal\n    return items.reduce((t,i)=>t+i.price,0);\n  }\n}\n',
    'javascript': 'class Totals {\n  subtotal(items) {\n    // return the subtotal\n    return items.reduce((t,i)=>t+i.price,0);\n  }\n}\n',
    'java': 'class Totals {\n  int subtotal(int[] prices) {\n    // return the subtotal\n    int total = 0;\n    for (int p : prices) { total += p; }\n    return total;\n  }\n}\n',
}

_STOP_WRITING_USELESS_COMMENTS_CLEAN = {
    'python': 'class Totals:\n    def subtotal(self, items):\n        # WHY: loyalty threshold uses pre-tax total\n        return sum(i.price for i in items)\n',
    'typescript': 'class Totals {\n  subtotal(items: {price:number}[]): number {\n    // WHY: loyalty threshold uses pre-tax total\n    return items.reduce((t,i)=>t+i.price,0);\n  }\n}\n',
    'javascript': 'class Totals {\n  subtotal(items) {\n    // WHY: loyalty threshold uses pre-tax total\n    return items.reduce((t,i)=>t+i.price,0);\n  }\n}\n',
    'java': 'class Totals {\n  int subtotal(int[] prices) {\n    // WHY: loyalty threshold uses pre-tax total\n    int total = 0;\n    for (int p : prices) { total += p; }\n    return total;\n  }\n}\n',
}

_USE_EXCEPTIONS_PROPERLY_FAULT = {
    'python': 'class Loader:\n    def load_cart(self, path):\n        try:\n            return open(path).read()\n        except:\n            pass\n',
    'typescript': 'class Loader {\n  loadCart(path: string): string {\n    try { return open(path); } catch { }\n  }\n}\n',
    'javascript': 'class Loader {\n  loadCart(path) {\n    try { return open(path); } catch { }\n  }\n}\n',
    'java': 'class Loader {\n  String loadCart(String path) {\n    try { return open(path); } catch (Exception e) { }\n  }\n}\n',
}

_USE_EXCEPTIONS_PROPERLY_CLEAN = {
    'python': 'class Loader:\n    def load_cart(self, path):\n        try:\n            return open(path).read()\n        except OSError:\n            raise\n',
    'typescript': 'class Loader {\n  loadCart(path: string): string {\n    try { return open(path); } catch (err) { throw err; }\n  }\n}\n',
    'javascript': 'class Loader {\n  loadCart(path) {\n    try { return open(path); } catch (err) { throw err; }\n  }\n}\n',
    'java': 'class Loader {\n  String loadCart(String path) {\n    try { return open(path); } catch (IOException e) { throw e; }\n  }\n}\n',
}

_NEVER_SWALLOW_EXCEPTIONS_FAULT = {
    'python': 'class Loader:\n    def load_cart(self, path):\n        try:\n            return open(path).read()\n        except:\n            pass\n',
    'typescript': 'class Loader {\n  loadCart(path: string): string {\n    try { return open(path); } catch { }\n  }\n}\n',
    'javascript': 'class Loader {\n  loadCart(path) {\n    try { return open(path); } catch { }\n  }\n}\n',
    'java': 'class Loader {\n  String loadCart(String path) {\n    try { return open(path); } catch (Exception e) { }\n  }\n}\n',
}

_NEVER_SWALLOW_EXCEPTIONS_CLEAN = {
    'python': 'class Loader:\n    def load_cart(self, path):\n        try:\n            return open(path).read()\n        except OSError:\n            raise\n',
    'typescript': 'class Loader {\n  loadCart(path: string): string {\n    try { return open(path); } catch (err) { throw err; }\n  }\n}\n',
    'javascript': 'class Loader {\n  loadCart(path) {\n    try { return open(path); } catch (err) { throw err; }\n  }\n}\n',
    'java': 'class Loader {\n  String loadCart(String path) {\n    try { return open(path); } catch (IOException e) { throw e; }\n  }\n}\n',
}
