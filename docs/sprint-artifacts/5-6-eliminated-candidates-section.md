# Story 5.6: Eliminated Candidates Section

Status: review

## Story

As a **HR professional**,
I want **to see which candidates were eliminated by thresholds**,
So that **I have complete transparency**.

## Acceptance Criteria

1. **AC5.6.1:** Shows total eliminated count in header
2. **AC5.6.2:** Breakdown by reason (e.g., "8: Experience < 60%", "5: Skills < 50%")
3. **AC5.6.3:** Collapsible list of eliminated candidate names
4. **AC5.6.4:** Section is collapsed by default

## Tasks / Subtasks

- [x] **Task 1: Install Accordion component** (AC: 5.6.3, 5.6.4)
  - [x] Run `npx shadcn@latest add accordion`

- [x] **Task 2: Create EliminatedSection component** (AC: 5.6.1-5.6.4)
  - [ ] Create `src/components/EliminatedSection.jsx`:
    ```jsx
    import { UserMinus, AlertTriangle } from 'lucide-react';
    import {
      Accordion,
      AccordionContent,
      AccordionItem,
      AccordionTrigger,
    } from '@/components/ui/accordion';

    function EliminatedSection({ eliminated }) {
      if (!eliminated || eliminated.count === 0) {
        return null;
      }

      const { count, breakdown, candidates } = eliminated;

      return (
        <div className="mt-8">
          <Accordion type="single" collapsible>
            <AccordionItem value="eliminated" className="border rounded-lg">
              <AccordionTrigger className="px-4 hover:no-underline">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-full bg-yellow-500/10">
                    <UserMinus className="h-4 w-4 text-yellow-500" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-medium">
                      Eliminated by Thresholds
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {count} candidate{count !== 1 ? 's' : ''} didn't meet minimum requirements
                    </p>
                  </div>
                </div>
              </AccordionTrigger>

              <AccordionContent className="px-4 pb-4">
                {/* Breakdown by reason */}
                {breakdown && Object.keys(breakdown).length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium mb-2">
                      Elimination Breakdown
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(breakdown).map(([dimension, count]) => (
                        <div
                          key={dimension}
                          className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted text-sm"
                        >
                          <span className="font-medium">{count}</span>
                          <span className="text-muted-foreground">
                            {formatDimension(dimension)} below threshold
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Candidate list */}
                {candidates && candidates.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-2">
                      Eliminated Candidates
                    </h4>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {candidates.map((candidate, i) => (
                        <div
                          key={i}
                          className="flex items-center justify-between py-2 px-3 rounded bg-muted/50"
                        >
                          <span className="text-sm">{candidate.name}</span>
                          <span className="text-xs text-muted-foreground">
                            {candidate.reason}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      );
    }

    function formatDimension(dim) {
      const labels = {
        experience: 'Experience',
        skills: 'Skills',
        projects: 'Projects',
        positions: 'Positions',
        education: 'Education'
      };
      return labels[dim] || dim;
    }

    export default EliminatedSection;
    ```

- [x] **Task 3: Add visual distinction**
  - [ ] Style eliminated section differently:
    ```jsx
    // Use warning colors
    <div className="border-yellow-500/30 bg-yellow-500/5">
    ```

- [x] **Task 4: Integrate into DashboardPage** (AC: 5.6.4)
  - [ ] Add to DashboardPage:
    ```jsx
    import EliminatedSection from '@/components/EliminatedSection';

    // After candidate cards:
    <EliminatedSection eliminated={data?.eliminated} />
    ```

- [x] **Task 5: Handle no eliminations**
  - [ ] Show nothing or success message:
    ```jsx
    if (!eliminated || eliminated.count === 0) {
      return (
        <div className="mt-8 p-4 rounded-lg bg-primary/5 border border-primary/30">
          <p className="text-sm text-primary flex items-center gap-2">
            <CheckCircle className="h-4 w-4" />
            All candidates passed threshold requirements
          </p>
        </div>
      );
    }
    ```

- [x] **Task 6: Test eliminated section**
  - [x] Verify collapsed by default
  - [x] Verify count displays correctly
  - [x] Verify breakdown shows all reasons
  - [x] Verify candidate list scrolls if long
  - [x] Test with no eliminations

## Dev Notes

### Architecture Alignment

This story displays threshold elimination results:
- **Source:** eliminated object from analysis response
- **Purpose:** Transparency into Level 2 filtering

### Section Layout

```
┌─────────────────────────────────────────────────────┐
│ ⚠️ Eliminated by Thresholds                      ▼  │
│    13 candidates didn't meet minimum requirements    │
├─────────────────────────────────────────────────────┤
│ Elimination Breakdown                                │
│ [8] Experience below threshold                       │
│ [5] Skills below threshold                           │
│                                                      │
│ Eliminated Candidates                                │
│ ┌─────────────────────────────────────────────────┐ │
│ │ John Doe        Experience score 45% < min 60%  │ │
│ │ Jane Smith      Skills score 40% < min 50%      │ │
│ │ ...                                             │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Data Structure

```javascript
eliminated: {
  count: 13,
  breakdown: {
    experience: 8,
    skills: 5
  },
  candidates: [
    { name: "John Doe", reason: "Experience score 45% < minimum 60%" },
    { name: "Jane Smith", reason: "Skills score 40% < minimum 50%" }
  ]
}
```

### UX Considerations

- Collapsed by default (not primary focus)
- Warning color scheme (yellow)
- Scrollable list for many eliminations
- Clear reason per candidate

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#Eliminated-Section]
- [Source: docs/epics.md#Story-5.6]
- [Source: docs/prd.md#FR36, FR50]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/5-6-eliminated-candidates-section.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- shadcn accordion component installed
- Vite build successful (4.68s)
- ESLint passes on EliminatedSection.jsx

### Completion Notes List

- All 6 tasks completed successfully
- All 4 acceptance criteria satisfied:
  - AC5.6.1: Shows total eliminated count in header (13 candidates)
  - AC5.6.2: Breakdown by reason shown as pills (8 Experience, 5 Skills below threshold)
  - AC5.6.3: Collapsible list of eliminated candidate names with specific reasons
  - AC5.6.4: Section collapsed by default using Accordion component
- Yellow/warning color scheme for visual distinction
- Scrollable candidate list for long lists (max-h-48)
- Success message shown when no eliminations (green CheckCircle)
- Mock data includes 13 eliminated candidates with varied reasons

### File List

**Created:**
- frontend/src/components/EliminatedSection.jsx
- frontend/src/components/ui/accordion.jsx (shadcn)

**Modified:**
- frontend/src/pages/DashboardPage.jsx (added import, eliminated mock data, component usage)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
