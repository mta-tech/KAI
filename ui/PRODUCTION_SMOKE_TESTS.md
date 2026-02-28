# Production Smoke Tests Guide

This guide covers running smoke tests in staging/production environments to validate critical functionality before and after deployment.

## Purpose

Production smoke tests provide quick validation that critical user flows work in the production environment. They are designed to:
- Run quickly (under 15 minutes total)
- Test only critical paths (not edge cases)
- Catch major regressions before users do
- Validate deployment success

## When to Run

### Before Deployment
Run smoke tests on staging environment before promoting to production:
```bash
# Run against staging
BASE_URL=https://staging.example.com npm run test:e2e --project=chromium
```

### After Deployment
Run smoke tests in production immediately after deployment:
```bash
# Run against production
BASE_URL=https://app.example.com npm run test:e2e --project=chromium
```

### Continuous Monitoring
Set up scheduled smoke tests to run periodically:
```bash
# Run every hour via cron
0 * * * * cd /app && npm run test:e2e --project=chromium
```

## Running Production Smoke Tests

### Quick Smoke Test (Chromium Only)
Fastest option for quick validation:
```bash
npm run test:e2e --grep "Production Smoke"
```

### Full Smoke Test (All Browsers)
Complete validation across all supported browsers:
```bash
npm run test:e2e --grep "Production Smoke"
```

### Against Specific Environment
```bash
# Staging
BASE_URL=https://staging.kai.example.com npm run test:e2e --grep "Production Smoke"

# Production
BASE_URL=https://kai.example.com npm run test:e2e --grep "Production Smoke"
```

### With Real Browser (Headed Mode)
For visual inspection during smoke tests:
```bash
npm run test:e2e:headed --grep "Production Smoke"
```

## Test Coverage

### Environment Tests
- ✅ Application loads successfully
- ✅ Correct environment (production vs development)
- ✅ No critical console errors

### Critical Path Tests
- ✅ Navigation between all main pages
- ✅ Database connection handling
- ✅ Chat interface functionality
- ✅ Knowledge base functionality

### Performance Tests
- ✅ Page load times acceptable (< 10s)
- ✅ No memory leaks during navigation

### Cross-Browser Tests
- ✅ Chrome/Edge compatibility
- ✅ Firefox compatibility
- ✅ Safari (WebKit) compatibility

### Mobile Tests
- ✅ iPhone compatibility
- ✅ Android compatibility
- ✅ Touch target sizes (44x44px minimum)

### Error Handling Tests
- ✅ 404 pages handled gracefully
- ✅ Error recovery works

### Accessibility Tests
- ✅ Proper page structure
- ✅ Keyboard navigation
- ✅ Heading hierarchy

### Integration Tests
- ✅ API connectivity
- ✅ Static assets load

## Interpretation

### All Tests Pass ✅
**Meaning**: Application is production-ready
**Action**: Safe to deploy or continue running

### Some Tests Fail ❌
**Meaning**: Critical regression detected
**Action**:
1. Review failed tests
2. Identify root cause
3. Fix issues
4. Re-run smoke tests
5. Only deploy when all pass

### Flaky Tests ⚠️
**Meaning**: Tests sometimes fail intermittently
**Action**:
1. Review failure patterns
2. Fix timing issues or increase timeouts
3. Stabilize tests before relying on them

## Troubleshooting

### Test Timeout
**Problem**: Tests timeout waiting for page load
**Solutions**:
- Check network connectivity
- Verify all services are running
- Increase timeout in test configuration
- Check for blocking operations

### Console Errors
**Problem**: Console errors detected
**Solutions**:
- Review error messages in test output
- Check for missing API endpoints
- Verify environment variables
- Check for failed resource loads

### Navigation Failures
**Problem**: Cannot navigate to certain pages
**Solutions**:
- Verify routes are configured correctly
- Check for authentication requirements
- Verify page components are built
- Check for client-side routing issues

### Memory Issues
**Problem**: Memory usage too high
**Solutions**:
- Check for memory leaks in components
- Verify proper cleanup in effects
- Check for large data structures
- Profile with browser DevTools

## CI/CD Integration

### Pre-deployment Gate
Add to deployment pipeline:
```yaml
# In deployment workflow
- name: Run smoke tests on staging
  run: |
    BASE_URL=https://staging.kai.example.com
    npm run test:e2e --grep "Production Smoke"
```

### Post-deployment Validation
```yaml
# After deployment to production
- name: Run smoke tests on production
  run: |
    BASE_URL=https://kai.example.com
    npm run test:e2e --grep "Production Smoke"
  on_failure: Alert team
```

### Scheduled Monitoring
```yaml
# GitHub Actions workflow
name: Production Smoke Tests
on:
  schedule:
    - cron: '0 */2 * * *'  # Every 2 hours
jobs:
  smoke-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: npm ci
        working-directory: ./ui
      - name: Run smoke tests
        run: |
          BASE_URL=https://kai.example.com
          npm run test:e2e --grep "Production Smoke"
        env:
          BASE_URL: ${{ secrets.PRODUCTION_URL }}
        working-directory: ./ui
```

## Best Practices

### 1. Keep Tests Fast
- Focus on critical paths only
- Avoid complex assertions
- Use efficient selectors
- Limit test data

### 2. Be Specific
- Test exact user flows, not variations
- Use realistic data
- Test production-like scenarios

### 3. Fail Fast
- Configure appropriate timeouts
- Stop on first critical failure
- Provide clear error messages

### 4. Monitor Results
- Track test pass/fail rates
- Alert on failures
- Review trends over time

### 5. Maintain Tests
- Update tests as features change
- Remove obsolete tests
- Add tests for new critical paths
- Keep tests independent

## Test Data

### Using Test Accounts
For smoke tests, use dedicated test accounts:
```typescript
// Use test credentials
const TEST_CREDENTIALS = {
  email: process.env.SMOKE_TEST_EMAIL,
  password: process.env.SMOKE_TEST_PASSWORD,
};
```

### Test Database
- Use separate test database if possible
- Or use read-only operations
- Clean up test data after tests

## Alerts and Notifications

### On Failure
Configure alerts to notify team:
```yaml
# Slack notification example
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Production smoke tests failed!'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Scheduled Test Results
Send summary of scheduled runs:
```yaml
- name: Send summary
  if: always()
  run: |
    echo "Smoke test results: ${{ job.status }}"
    # Send to monitoring service
```

## Metrics to Track

- Test execution time
- Pass/fail rate
- Most common failures
- Performance trends
- Browser-specific issues

## Emergency Procedures

### Critical Failure Detected
1. **Alert the team immediately**
2. **Verify user impact**
3. **Rollback if necessary**
4. **Fix and redeploy**
5. **Re-run smoke tests**

### All Tests Pass
1. **Document the deployment**
2. **Update monitoring dashboards**
3. **Notify stakeholders**
4. **Continue monitoring**

## Related Documentation

- **Browser Testing Matrix**: `BROWSER_TESTING_MATRIX.md`
- **Mobile Testing Guide**: `MOBILE_TESTING_GUIDE.md`
- **Testing Guide**: `tests/README.md`
- **E2E Tests**: `tests/e2e/`
