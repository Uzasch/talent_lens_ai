# System-Level Test Design: TalentLens AI

**Date:** 2025-12-20
**Author:** Uzasch (via TEA Agent)
**Status:** Draft
**Phase:** 3 - Solutioning (Pre-Implementation)

---

## Executive Summary

This document provides a testability assessment and test strategy for TalentLens AI before implementation begins. The architecture (React SPA + Flask API + SQLite + Gemini API + Gmail SMTP) is well-suited for testing with minor enhancements needed.

**Overall Testability Rating:** PASS with CONCERNS

| Category | Rating | Summary |
|----------|--------|---------|
| Controllability | PASS | API-first design enables clean test setup |
| Observability | CONCERNS | Missing health endpoint and structured logging |
| Reliability | PASS | Simple architecture reduces failure modes |

---

## Testability Assessment

### Controllability: PASS

**Can we control system state for testing?**

| Aspect | Status | Details |
|--------|--------|---------|
| API Seeding | ✅ PASS | REST API allows direct role/candidate creation via POST /api/roles, /api/analyze |
| Database Reset | ✅ PASS | SQLite file-based - can delete/recreate between tests |
| External Dependencies | ⚠️ CONCERNS | Gemini API and Gmail SMTP are external - need mocking strategy |
| Dependency Injection | ⚠️ CONCERNS | Flask services not DI-configured - consider interfaces for testing |

**Recommendations:**
1. Add test fixtures for database seeding (create test candidates, roles)
2. Create mock services for `gemini_service.py` and `email_service.py`
3. Add `/api/test/reset` endpoint for test cleanup (development mode only)

### Observability: CONCERNS

**Can we inspect system state?**

| Aspect | Status | Details |
|--------|--------|---------|
| Health Endpoint | ❌ MISSING | No `/api/health` endpoint exists |
| Logging | ⚠️ PARTIAL | Basic logging mentioned but no structured format |
| Test Results | ✅ PASS | API responses include `success: true/false` - deterministic |
| Error Messages | ✅ PASS | Standard error format defined in architecture |

**Recommendations:**
1. **CRITICAL:** Add `/api/health` endpoint returning service status
2. Add structured logging with correlation IDs for request tracing
3. Consider adding response timing headers (Server-Timing) for performance monitoring

### Reliability: PASS

**Can we run tests reliably?**

| Aspect | Status | Details |
|--------|--------|---------|
| Test Isolation | ✅ PASS | SQLite allows per-test database creation |
| Parallel Safety | ✅ PASS | Separate file uploads per session |
| Deterministic Waits | ⚠️ CONCERNS | No websockets - polling for long operations needs handling |
| Cleanup Discipline | ⚠️ CONCERNS | No explicit cleanup strategy defined |

**Recommendations:**
1. Define test cleanup strategy (truncate tables or delete test data)
2. For Gemini API analysis (30-45s), implement polling endpoint or progress tracking
3. Add unique identifiers for test data (e.g., email prefix `test_`) for easy cleanup

---

## Architecturally Significant Requirements (ASRs)

These quality requirements drive architecture decisions and require specific testing approaches:

### High-Risk ASRs (Score ≥6)

| ID | Requirement | Category | Prob | Impact | Score | Testing Approach |
|----|-------------|----------|------|--------|-------|------------------|
| ASR-001 | Gemini API analysis completes <45s for 10-15 resumes | PERF | 3 | 2 | 6 | k6 load testing with mock API |
| ASR-002 | Multi-level ranking produces correct relative scores | BUS | 2 | 3 | 6 | Integration tests with known datasets |
| ASR-003 | Resume text extraction handles diverse PDF formats | TECH | 3 | 2 | 6 | Unit tests with PDF corpus |
| ASR-004 | Candidate pool comparisons are fair across sessions | BUS | 2 | 3 | 6 | E2E tests with multi-session scenarios |

### Medium-Risk ASRs (Score 3-4)

| ID | Requirement | Category | Prob | Impact | Score | Testing Approach |
|----|-------------|----------|------|--------|-------|------------------|
| ASR-005 | Email delivery succeeds for valid addresses | OPS | 2 | 2 | 4 | Integration test with test SMTP |
| ASR-006 | Duplicate candidate detection by email works | DATA | 2 | 2 | 4 | Unit tests for detection logic |
| ASR-007 | Session history persists across app restarts | DATA | 1 | 3 | 3 | Integration tests with SQLite |
| ASR-008 | PDF upload validates file type and size | SEC | 2 | 2 | 4 | E2E tests with invalid files |

### Low-Risk ASRs (Score 1-2)

| ID | Requirement | Category | Prob | Impact | Score | Testing Approach |
|----|-------------|----------|------|--------|-------|------------------|
| ASR-009 | Dashboard renders in <1 second | PERF | 1 | 1 | 1 | Lighthouse CI checks |
| ASR-010 | Navigation between screens is instant (SPA) | PERF | 1 | 1 | 1 | Basic E2E smoke test |

---

## Test Levels Strategy

Based on architecture (React SPA + Flask API + SQLite + External APIs):

### Recommended Distribution

| Level | Target % | Rationale |
|-------|----------|-----------|
| **Unit** | 50% | Pure logic: ranking algorithms, extraction patterns, score calculations |
| **Integration** | 35% | API contracts, database operations, service interactions |
| **E2E** | 15% | Critical user journeys only: Upload→Analyze→Dashboard→Email |

### Level Selection by Epic

| Epic | Unit | Integration | E2E | Notes |
|------|------|-------------|-----|-------|
| 1: Foundation | 10% | 70% | 20% | API setup, DB schema - integration-heavy |
| 2: Upload & Role | 30% | 40% | 30% | File handling needs E2E validation |
| 3: Phase 1 Extraction | 60% | 30% | 10% | Pure extraction logic - unit test heavy |
| 4: Phase 2 Ranking | 70% | 25% | 5% | Algorithm logic - mostly unit tests |
| 5: Dashboard | 20% | 30% | 50% | UI rendering - E2E for visual validation |
| 6: Email | 20% | 60% | 20% | SMTP integration needs mocking |
| 7: History | 30% | 50% | 20% | Database persistence - integration focus |

### Test Framework Recommendations

| Level | Tool | Rationale |
|-------|------|-----------|
| **Unit (Python)** | pytest | Standard Python testing, beginner-friendly |
| **Unit (React)** | Vitest + React Testing Library | Fast, Vite-native |
| **Integration** | pytest + Flask test client | API contract validation |
| **E2E** | Playwright | Modern, reliable, great debugging |
| **Performance** | k6 | Load testing for API endpoints |

---

## NFR Testing Approach

### Security (SEC)

| Test Area | Approach | Tools | Priority |
|-----------|----------|-------|----------|
| File upload validation | E2E: Upload non-PDF, oversized files | Playwright | P0 |
| API key protection | Code review + .env check | Manual | P0 |
| SQL injection prevention | Integration: Parameterized query tests | pytest | P1 |
| CORS configuration | Integration: Cross-origin requests | pytest | P1 |
| XSS prevention | E2E: Inject script in job description | Playwright | P1 |

**Note:** No authentication in MVP - skip auth tests.

### Performance (PERF)

| Test Area | Target | Approach | Tools |
|-----------|--------|----------|-------|
| Phase 1 extraction | <15s for 10-15 resumes | Load test | k6 |
| Phase 2 ranking | <30s for 50 candidates | Load test with mock Gemini | k6 |
| Dashboard render | <1s after data received | Lighthouse CI | Playwright |
| Initial page load | <3s | Lighthouse CI | Playwright |

**Strategy:**
- Mock Gemini API for performance tests (real API adds network variability)
- Test with realistic resume corpus (10, 25, 50 resumes)
- Monitor SQLite query performance with large candidate pools

### Reliability (REL)

| Test Area | Approach | Tools |
|-----------|----------|-------|
| Gemini API failure handling | Mock 500 response, verify graceful error | Playwright |
| PDF parsing failure | Use corrupted PDF, verify skip + continue | pytest |
| Email send failure | Mock SMTP failure, verify retry/error display | pytest |
| Network timeout | Mock slow response, verify timeout message | Playwright |

### Maintainability (MAIN)

| Metric | Target | Validation |
|--------|--------|------------|
| Test coverage | ≥80% for Python backend | pytest-cov |
| Code duplication | <5% | jscpd in CI |
| No critical vulnerabilities | 0 critical/high | npm audit, pip-audit |

---

## Testability Concerns

### CONCERNS (Require Attention)

| ID | Concern | Risk | Mitigation | Owner |
|----|---------|------|------------|-------|
| TC-001 | Gemini API not mockable in current design | Cannot unit test ranking logic | Add interface for AI service, create mock | Dev |
| TC-002 | No health endpoint for monitoring | Cannot validate service status in tests | Add `/api/health` endpoint | Dev |
| TC-003 | Long-running analysis (30-45s) with no progress | Tests timeout or flaky | Add polling endpoint for analysis progress | Dev |
| TC-004 | Gmail SMTP requires real credentials | Integration tests depend on email config | Use test SMTP server (Mailhog) or mock | Dev |
| TC-005 | No database seeding utility | Test setup is manual | Create `/api/test/seed` endpoint (dev only) | Dev |

### NOT BLOCKERS (Low Risk)

| ID | Concern | Risk | Notes |
|----|---------|------|-------|
| TC-006 | SQLite concurrent writes | Very low | Single-user app, SQLite handles fine |
| TC-007 | No caching layer | Very low | MVP scope, not performance-critical |
| TC-008 | File upload storage local only | Low | Demo app, not production deployment |

---

## Test Environment Requirements

### Local Development

| Component | Setup |
|-----------|-------|
| **Backend** | Flask dev server, SQLite file in `data/app.db` |
| **Frontend** | Vite dev server, proxies to Flask |
| **Database** | SQLite (auto-created on first run) |
| **External APIs** | Real Gemini API (free tier) or mocked |
| **Email** | Mailhog (local SMTP trap) or mocked |

### CI Environment (GitHub Actions)

```yaml
# Recommended CI matrix
jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r backend/requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest backend/tests --cov=backend --cov-report=xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: cd frontend && npm ci
      - run: cd frontend && npm test

  test-e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
      - uses: actions/setup-node@v4
      - run: pip install -r backend/requirements.txt
      - run: cd frontend && npm ci
      - run: npx playwright install --with-deps
      - run: python backend/app.py &
      - run: cd frontend && npm run dev &
      - run: npx playwright test
```

### Test Data Strategy

| Data Type | Strategy |
|-----------|----------|
| **Resume PDFs** | Curated test corpus (10-15 resumes with known content) |
| **Job Descriptions** | Fixed test JDs for deterministic ranking |
| **Candidate Pool** | Seeded via API with known scores for validation |
| **Email Addresses** | Faker-generated or `test_*@example.com` pattern |

---

## Recommendations for Sprint 0

### Critical (Do First)

1. **Add Health Endpoint** - Create `/api/health` returning `{"status": "healthy"}`
2. **Create Mock Services** - Interface + mock for `gemini_service.py`
3. **Setup Test Infrastructure** - pytest fixtures for backend, Playwright config for E2E

### Important (Sprint 0)

4. **PDF Test Corpus** - Collect 10-15 diverse resume PDFs for testing
5. **Database Reset Utility** - Script to reset SQLite for test isolation
6. **CI Pipeline** - GitHub Actions for unit + integration tests

### Nice to Have (Sprint 1)

7. **Mailhog Setup** - Local SMTP trap for email testing
8. **Lighthouse CI** - Performance monitoring in CI
9. **Test Coverage Tracking** - Coverage reports in PRs

---

## Quality Gate Criteria

For solutioning phase approval:

- [x] Testability assessment complete with PASS/CONCERNS/FAIL ratings
- [x] ASRs identified with risk scores
- [x] Test levels strategy defined
- [x] NFR testing approach documented
- [x] Testability concerns flagged with mitigations
- [x] Test environment requirements specified

**Gate Decision: PASS with CONCERNS**

Proceed to implementation with action items:
1. Add `/api/health` endpoint before Epic 1 completion
2. Create mock service pattern before Phase 2 (ranking) implementation
3. Setup Playwright E2E before Epic 5 (Dashboard) starts

---

**Generated by**: TEA Agent - Test Architect Module
**Workflow**: `.bmad/bmm/testarch/test-design` (System-Level Mode)
**Version**: 4.0 (BMad v6)
