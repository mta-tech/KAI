# KAI UI Unit Tests

This directory contains unit tests for KAI UI components, hooks, utilities, and API clients.

## Test Framework

- **Framework:** Vitest
- **Testing Library:** @testing-library/react
- **Coverage Tool:** vitest-coverage-v8

## Running Tests

```bash
# Run all unit tests
npm run test:unit

# Run tests in watch mode
npm run test:unit:watch

# Run tests with coverage
npm run test:unit:coverage

# Run specific test file
npx vitest button.test.tsx
```

## Test Organization

```
tests/unit/
├── components/         # Component tests
│   ├── ui/            # Base UI component tests
│   ├── chat/          # Chat feature tests
│   ├── layout/        # Layout component tests
│   └── ...            # Other feature components
├── hooks/             # Custom hook tests
├── lib/               # Utility function tests
├── api/               # API client tests
├── fixtures/          # Test data fixtures
└── helpers/           # Test helper functions
```

## Testing Guidelines

### Component Testing

1. **Test user behavior, not implementation details**
   - Test what users see and interact with
   - Avoid testing internal state or methods

2. **Use Testing Library queries**
   - Prefer accessible queries (`getByRole`, `getByLabelText`)
   - Use `getBy*` for expected elements
   - Use `queryBy*` for optional elements
   - Use `findBy*` for async operations

3. **Test component variants**
   - Different props combinations
   - Loading states
   - Error states
   - Empty states

### Hook Testing

1. **Test hook behavior**
   - Return values
   - State changes
   - Side effects

2. **Use @testing-library/react-hooks**
   - Render hooks in test environment
   - Test async operations

### Utility Testing

1. **Test pure functions**
   - Input/output combinations
   - Edge cases
   - Error handling

## Coverage Goals

- **Target:** 80%+ code coverage
- **Critical paths:** 100% coverage
- **UI components:** 80%+ coverage
- **Utilities:** 90%+ coverage
- **API clients:** 70%+ coverage (mostly mocked)

## Fixtures

Test fixtures are available in `fixtures/`:

- `mockData.ts` - Mock API responses
- `testHelpers.ts` - Custom test utilities
- `testConstants.ts` - Test constants

## Best Practices

1. **Arrange-Act-Assert Pattern**
   ```typescript
   test('should do something', () => {
     // Arrange: Setup test data and conditions
     const props = { ... };

     // Act: Execute the code being tested
     render(<Component {...props} />);

     // Assert: Verify expected outcomes
     expect(screen.getByText('Expected')).toBeInTheDocument();
   });
   ```

2. **Describe test intent clearly**
   - Test names should describe what is being tested
   - Use "should" format for test names

3. **Keep tests simple**
   - One assertion per test when possible
   - Complex scenarios can have multiple assertions

4. **Mock external dependencies**
   - Mock API calls
   - Mock hooks that depend on external services
   - Use MSW for API mocking when needed

## Writing New Tests

1. Create test file alongside component: `Component.test.tsx`
2. Import from `@testing-library/react`
3. Describe component functionality
4. Test all variants and states
5. Test accessibility attributes
6. Run tests to verify

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
