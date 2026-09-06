# Rule: Domain-Oriented Test Inheritance

**At small scale**, a single test class covering multiple domain objects in the same sub-epic is fine. **As domain objects develop distinct behavior**, extract them into domain-specific test classes with a shared abstract base class for common operations. Share fixtures and parameter data only when there is obvious shared logic — do not create shared infrastructure pre-emptively.

## DO

- At small scale: keep related tests together in one class.
- At scale: use abstract base classes for shared assertion logic; place shared base files at the appropriate hierarchy level (sub-epic or epic).

```python
# Small scale — fine
class TestPaymentOperations:
    def test_creates_wire_payment(self): ...
    def test_creates_ach_payment(self): ...

# At scale — domain-specific classes with shared base
class PaymentTestBase:
    def verify_payment_persisted(self, payment): ...

class TestWirePayment(PaymentTestBase):
    def test_creates_wire_payment(self): ...

class TestACHPayment(PaymentTestBase):
    def test_creates_ach_payment(self): ...
```

## DON'T

- Copy assertion logic across classes instead of using a base class.
- Create shared files before there is an explicit, demonstrated need.
- Group tests by operation layer or technology rather than domain object.

```python
# WRONG: duplicated assertion logic
class TestWirePayment:
    def test_creates_payment(self):
        assert payment.status == 'pending'   # duplicated
        assert payment.rail == 'wire'        # duplicated

class TestACHPayment:
    def test_creates_payment(self):
        assert payment.status == 'pending'   # same assertion copied
        assert payment.rail == 'ach'
```
