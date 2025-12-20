# Story 5.7: Why Not Others Section

Status: review

## Story

As a **HR professional**,
I want **to know why remaining candidates didn't make top 6**,
So that **I have complete transparency**.

## Acceptance Criteria

1. **AC5.7.1:** Section shows below top 6 candidate cards
2. **AC5.7.2:** Distinguishes between eliminated (thresholds) vs below top 6 (ranking)
3. **AC5.7.3:** Mentions pool context (total pool size, how many evaluated)

## Tasks / Subtasks

- [x] **Task 1: Create WhyNotOthers component** (AC: 5.7.1-5.7.3)
  - [ ] Create `src/components/WhyNotOthers.jsx`:
    ```jsx
    import { Info, Users, UserMinus, TrendingDown } from 'lucide-react';
    import { Card, CardContent } from '@/components/ui/card';

    function WhyNotOthers({ stats, eliminated, whyNotOthersText }) {
      const {
        total_in_pool,
        ranked_count,
        eliminated_count
      } = stats || {};

      const belowTop6 = (ranked_count || 0) - 6;

      return (
        <Card className="mt-8 bg-muted/30">
          <CardContent className="p-6">
            <div className="flex items-start gap-3">
              <Info className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div className="space-y-4">
                <h3 className="font-medium">Why Not Others?</h3>

                {/* Summary text from AI */}
                {whyNotOthersText && (
                  <p className="text-sm text-muted-foreground">
                    {whyNotOthersText}
                  </p>
                )}

                {/* Breakdown */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                  {/* Total pool */}
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <span className="font-medium">{total_in_pool}</span>
                      <span className="text-sm text-muted-foreground ml-1">
                        total in pool
                      </span>
                    </div>
                  </div>

                  {/* Eliminated */}
                  {eliminated_count > 0 && (
                    <div className="flex items-center gap-2">
                      <UserMinus className="h-4 w-4 text-yellow-500" />
                      <div>
                        <span className="font-medium">{eliminated_count}</span>
                        <span className="text-sm text-muted-foreground ml-1">
                          eliminated by thresholds
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Below top 6 */}
                  {belowTop6 > 0 && (
                    <div className="flex items-center gap-2">
                      <TrendingDown className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <span className="font-medium">{belowTop6}</span>
                        <span className="text-sm text-muted-foreground ml-1">
                          ranked below top 6
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Link to eliminated section */}
                {eliminated_count > 0 && (
                  <p className="text-xs text-muted-foreground">
                    See "Eliminated by Thresholds" section above for details.
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      );
    }

    export default WhyNotOthers;
    ```

- [x] **Task 2: Add common gaps analysis**
  - [ ] Show common reasons for not ranking higher:
    ```jsx
    {commonGaps && commonGaps.length > 0 && (
      <div className="mt-3">
        <h4 className="text-sm font-medium mb-2">Common Gaps</h4>
        <ul className="space-y-1">
          {commonGaps.map((gap, i) => (
            <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
              <span className="text-muted-foreground">•</span>
              {gap}
            </li>
          ))}
        </ul>
      </div>
    )}
    ```

- [x] **Task 3: Integrate into DashboardPage** (AC: 5.7.1)
  - [ ] Add to DashboardPage:
    ```jsx
    import WhyNotOthers from '@/components/WhyNotOthers';

    // After EliminatedSection:
    <WhyNotOthers
      stats={data?.stats}
      eliminated={data?.eliminated}
      whyNotOthersText={data?.why_not_others}
    />
    ```

- [x] **Task 4: Handle edge cases**
  - [ ] When all candidates are in top 6:
    ```jsx
    if (total_in_pool <= 6) {
      return (
        <Card className="mt-8 bg-primary/5 border-primary/30">
          <CardContent className="p-6">
            <p className="text-sm text-primary flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              All {total_in_pool} candidates in pool are shown above
            </p>
          </CardContent>
        </Card>
      );
    }
    ```

- [x] **Task 5: Test why not others section**
  - [x] Verify displays below cards
  - [x] Verify counts are accurate
  - [x] Verify AI text displays
  - [x] Test with small pool (<= 6)

## Dev Notes

### Architecture Alignment

This story provides context for non-selected candidates:
- **Source:** why_not_others text from analysis response
- **Purpose:** Complete transparency, no black box

### Section Layout

```
┌─────────────────────────────────────────────────────┐
│ ℹ️ Why Not Others?                                   │
│                                                      │
│ 45 candidates in pool. 13 eliminated by thresholds. │
│ Remaining 26 below top 6 due to: insufficient       │
│ project scale (15), no leadership experience (8),   │
│ skills gaps in required tech stack (3).             │
│                                                      │
│ [45] total in pool                                   │
│ [13] eliminated by thresholds                        │
│ [26] ranked below top 6                              │
│                                                      │
│ See "Eliminated by Thresholds" section for details. │
└─────────────────────────────────────────────────────┘
```

### Data Flow

```
stats.total_in_pool (45)
  └─> eliminated.count (13) ─ gone by thresholds
  └─> stats.ranked_count (32)
        └─> top 6 shown
        └─> 26 below top 6
```

### Pool Context Examples

- "45 candidates in pool across 3 sessions"
- "This is the largest Python Developer pool we've analyzed"
- "Average match score for candidates below top 6: 65%"

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#Why-Not-Others]
- [Source: docs/epics.md#Story-5.7]
- [Source: docs/prd.md#FR49, FR51]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/5-7-why-not-others-section.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Vite build successful (4.57s)
- Component renders correctly in browser

### Completion Notes List

- All 5 tasks completed successfully
- All 3 acceptance criteria satisfied:
  - AC5.7.1: Section displays below top 6 candidate cards
  - AC5.7.2: Distinguishes between eliminated (thresholds) vs below top 6 (ranking) with separate stats
  - AC5.7.3: Pool context shown (45 total, 13 eliminated, 26 below top 6)
- AI-generated explanation text displays prominently
- Common Gaps section shows 4 bullet points with candidate counts
- Edge case handling for small pools (shows success message when all candidates shown)
- Yellow icon used for eliminated count to match EliminatedSection styling

### File List

**Created:**
- frontend/src/components/WhyNotOthers.jsx

**Modified:**
- frontend/src/pages/DashboardPage.jsx (added import, mock data, component usage)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
