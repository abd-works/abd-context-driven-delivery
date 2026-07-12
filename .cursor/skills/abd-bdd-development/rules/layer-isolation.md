---
name: layer-isolation
scanner: javascript/mock_boundaries_scanner.py
severity: warning
---

# Rule: Layer Isolation

Each test targets one architectural layer. Mocks appear only at the boundary between that layer and the next — never inside the layer being tested.

## DO

- Mock external services, repositories, and infrastructure adapters at the boundary.
- Test domain classes without mocks — they have no external boundary.
- When testing a service that calls a repository, mock the repository; not the service.

```typescript
// Testing service layer — mock the repository boundary
describe('VoucherService that is creating a voucher', () => {
  let service: VoucherService;
  let mockRepo: jest.Mocked<VoucherRepository>;

  beforeEach(() => {
    mockRepo = { save: jest.fn(), findById: jest.fn() } as any;
    service = new VoucherService(mockRepo); // inject mock at boundary
  });

  it('should persist the voucher when valid', async () => {
    await service.create({ code: 'ABC', campaignId: '1' });
    expect(mockRepo.save).toHaveBeenCalledWith(
      expect.objectContaining({ code: 'ABC' })
    );
  });
});
```

## DO NOT

- Mock the class under test: `jest.mock('../Character')` when the test is FOR Character.
- Use `jest.fn()` for internal business logic methods.
- Cross layer boundaries: a unit test that hits the real database or a real HTTP endpoint.

```typescript
// WRONG — mocking the thing you are testing
jest.mock('../VoucherService');
const mockService = VoucherService as jest.MockedClass<typeof VoucherService>;

it('should create a voucher', () => {
  const instance = new mockService();
  instance.create.mockResolvedValue({ code: 'ABC' }); // mocking the object under test
  // This proves nothing about VoucherService behavior
});
```

**Example (pass):**
Every mock in the test file targets a dependency declared as a constructor parameter or a module-level import at the layer boundary. No mock targets the class/function being tested. PASS.

**Example (fail):**
`jest.mock('../Character')` in a test file named `character.test.ts`. FAIL — you are mocking what you are supposed to be testing.
