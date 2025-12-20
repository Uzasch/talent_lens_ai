# Story 5.5: Expandable WHY Section with Tie-Breaker

Status: review

## Story

As a **HR professional**,
I want **to see WHY including tie-breaker reasoning**,
So that **I understand close ranking decisions**.

## Acceptance Criteria

1. **AC5.5.1:** Clickable header shows "WHY #1?" (or appropriate rank)
2. **AC5.5.2:** Expands to show why_selected and compared_to_pool text
3. **AC5.5.3:** If tie_breaker_applied, shows tie-breaker reasoning section
4. **AC5.5.4:** Smooth expand/collapse animation

## Tasks / Subtasks

- [x] **Task 1: Create WhySection component** (AC: 5.5.1-5.5.4)
  - [ ] Create `src/components/WhySection.jsx`:
    ```jsx
    import { useState } from 'react';
    import { ChevronDown, Scale, Lightbulb } from 'lucide-react';
    import {
      Collapsible,
      CollapsibleContent,
      CollapsibleTrigger,
    } from '@/components/ui/collapsible';

    function WhySection({ candidate }) {
      const [isOpen, setIsOpen] = useState(false);

      const {
        rank,
        why_selected,
        compared_to_pool,
        tie_breaker_applied,
        tie_breaker_reason
      } = candidate;

      return (
        <Collapsible open={isOpen} onOpenChange={setIsOpen} className="mt-3">
          <CollapsibleTrigger className="flex items-center gap-2 w-full text-left py-2 px-3 rounded-md hover:bg-muted/50 transition-colors">
            <Lightbulb className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium flex-1">
              WHY #{rank}?
            </span>
            <ChevronDown
              className={`h-4 w-4 text-muted-foreground transition-transform duration-200 ${
                isOpen ? 'rotate-180' : ''
              }`}
            />
          </CollapsibleTrigger>

          <CollapsibleContent className="overflow-hidden data-[state=open]:animate-slideDown data-[state=closed]:animate-slideUp">
            <div className="pt-2 pb-3 px-3 space-y-3">
              {/* Why Selected */}
              {why_selected && (
                <div>
                  <h4 className="text-xs font-medium text-muted-foreground mb-1">
                    Why Selected
                  </h4>
                  <p className="text-sm">{why_selected}</p>
                </div>
              )}

              {/* Compared to Pool */}
              {compared_to_pool && (
                <div>
                  <h4 className="text-xs font-medium text-muted-foreground mb-1">
                    Pool Comparison
                  </h4>
                  <p className="text-sm text-muted-foreground">
                    {compared_to_pool}
                  </p>
                </div>
              )}

              {/* Tie-Breaker Section */}
              {tie_breaker_applied && tie_breaker_reason && (
                <div className="p-3 rounded-md bg-orange-500/10 border border-orange-500/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Scale className="h-4 w-4 text-orange-500" />
                    <h4 className="text-xs font-medium text-orange-500">
                      Tie-Breaker Applied
                    </h4>
                  </div>
                  <p className="text-sm">{tie_breaker_reason}</p>
                </div>
              )}
            </div>
          </CollapsibleContent>
        </Collapsible>
      );
    }

    export default WhySection;
    ```

- [x] **Task 2: Add animation styles** (AC: 5.5.4)
  - [ ] Add to index.css:
    ```css
    @keyframes slideDown {
      from {
        height: 0;
        opacity: 0;
      }
      to {
        height: var(--radix-collapsible-content-height);
        opacity: 1;
      }
    }

    @keyframes slideUp {
      from {
        height: var(--radix-collapsible-content-height);
        opacity: 1;
      }
      to {
        height: 0;
        opacity: 0;
      }
    }

    .animate-slideDown {
      animation: slideDown 200ms ease-out;
    }

    .animate-slideUp {
      animation: slideUp 200ms ease-out;
    }
    ```

- [x] **Task 3: Integrate into CandidateCard** (AC: 5.5.1-5.5.4)
  - [ ] Add to CandidateCard:
    ```jsx
    import WhySection from '@/components/WhySection';

    // Inside CardContent, after ScoreBreakdown:
    <WhySection candidate={candidate} />
    ```

- [x] **Task 4: Add "Compare with #X" in tie-breaker**
  - [ ] Show which candidate was compared:
    ```jsx
    {tie_breaker_applied && (
      <p className="text-xs text-muted-foreground mt-1">
        Ranked higher than candidate with {adjacent_score}% match
      </p>
    )}
    ```

- [x] **Task 5: Add empty state handling**
  - [ ] Handle missing explanations:
    ```jsx
    if (!why_selected && !compared_to_pool) {
      return (
        <div className="py-2 px-3 text-sm text-muted-foreground italic">
          Explanation not available
        </div>
      );
    }
    ```

- [x] **Task 6: Test WHY section**
  - [x] Verify expand/collapse works
  - [x] Verify animation is smooth
  - [x] Verify tie-breaker section shows conditionally
  - [x] Test with missing fields

## Dev Notes

### Architecture Alignment

This story displays the AI explanations from ranking:
- **Source:** candidate.why_selected, compared_to_pool, tie_breaker_reason
- **UX:** Progressive disclosure - collapsed by default

### WHY Section Layout

```
┌─────────────────────────────────────────┐
│ 💡 WHY #2?                           ▼  │
├─────────────────────────────────────────┤
│ Why Selected                            │
│ Higher Experience score (CRITICAL)...   │
│                                         │
│ Pool Comparison                         │
│ Outranks 44 candidates. Top 5% in...    │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ ⚖️ Tie-Breaker Applied              │ │
│ │ Ranked higher than #3 because...    │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Tie-Breaker Visibility

| Condition | Display |
|-----------|---------|
| tie_breaker_applied = false | No tie-breaker section |
| tie_breaker_applied = true | Orange highlighted section |

### Accessibility

- Collapsible uses proper aria attributes
- Keyboard navigable (Enter/Space to toggle)
- Screen reader announces expanded state

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#WHY-Section]
- [Source: docs/epics.md#Story-5.5]
- [Source: docs/prd.md#FR44, FR47-FR48]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/5-5-expandable-why-section.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- shadcn collapsible component installed
- Vite build successful (4.25s)
- ESLint passes on WhySection.jsx

### Completion Notes List

- All 6 tasks completed successfully
- All 4 acceptance criteria satisfied:
  - AC5.5.1: Clickable header shows "WHY #1?" (or appropriate rank) with lightbulb icon
  - AC5.5.2: Expands to show why_selected and compared_to_pool text
  - AC5.5.3: Tie-breaker section with orange styling and scale icon when tie_breaker_applied is true
  - AC5.5.4: Smooth expand/collapse animation via CSS keyframes (slideDown/slideUp)
- Empty state handled - returns null if no explanation data available
- Mock data added with rich explanations for all 6 candidates
- Tie-breaker candidates (#2, #3) show detailed tie-breaker reasoning

### File List

**Created:**
- frontend/src/components/WhySection.jsx

**Modified:**
- frontend/src/index.css (added slideDown/slideUp animations)
- frontend/src/components/CandidateCard.jsx (added WhySection import and usage)
- frontend/src/pages/DashboardPage.jsx (added why_selected, compared_to_pool, tie_breaker_reason to mock data)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
