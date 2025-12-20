# Story 5.2: Inferred Priorities Display

Status: review

## Story

As a **HR professional**,
I want **to see what dimensions Gemini determined as CRITICAL for this job**,
So that **I understand the ranking logic**.

## Acceptance Criteria

1. **AC5.2.1:** Each dimension shows priority badge (Experience, Skills, Projects, Positions, Education)
2. **AC5.2.2:** Badge colors: CRITICAL=red, IMPORTANT=orange, NICE_TO_HAVE=gray, LOW_PRIORITY=dim gray
3. **AC5.2.3:** Reasoning shown in tooltip or expandable section
4. **AC5.2.4:** Section appears above candidate cards

## Tasks / Subtasks

- [x] **Task 1: Create PriorityBadges component** (AC: 5.2.1, 5.2.2)
  - [ ] Create `src/components/PriorityBadges.jsx`:
    ```jsx
    import { Badge } from '@/components/ui/badge';
    import { Info } from 'lucide-react';
    import {
      Tooltip,
      TooltipContent,
      TooltipProvider,
      TooltipTrigger,
    } from '@/components/ui/tooltip';

    const PRIORITY_CONFIG = {
      CRITICAL: {
        label: 'CRITICAL',
        className: 'bg-red-500/20 text-red-500 border-red-500/50'
      },
      IMPORTANT: {
        label: 'IMPORTANT',
        className: 'bg-orange-500/20 text-orange-500 border-orange-500/50'
      },
      NICE_TO_HAVE: {
        label: 'NICE TO HAVE',
        className: 'bg-gray-500/20 text-gray-400 border-gray-500/50'
      },
      LOW_PRIORITY: {
        label: 'LOW',
        className: 'bg-gray-800/50 text-gray-500 border-gray-700'
      }
    };

    const DIMENSION_LABELS = {
      experience: 'Experience',
      skills: 'Skills',
      projects: 'Projects',
      positions: 'Positions',
      education: 'Education'
    };

    function PriorityBadges({ priorities, reasoning }) {
      if (!priorities) return null;

      return (
        <div className="mb-6 p-4 bg-card rounded-lg border">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium">Job-Inferred Priorities</h3>
            {reasoning && (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <Info className="h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-sm">
                    <p className="text-sm">{reasoning}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
          </div>

          <div className="flex flex-wrap gap-2">
            {Object.entries(priorities).map(([dimension, priority]) => {
              const config = PRIORITY_CONFIG[priority] || PRIORITY_CONFIG.NICE_TO_HAVE;
              return (
                <div key={dimension} className="flex items-center gap-1">
                  <span className="text-sm text-muted-foreground">
                    {DIMENSION_LABELS[dimension]}:
                  </span>
                  <Badge variant="outline" className={config.className}>
                    {config.label}
                  </Badge>
                </div>
              );
            })}
          </div>
        </div>
      );
    }

    export default PriorityBadges;
    ```

- [x] **Task 2: Install Tooltip component** (AC: 5.2.3)
  - [x] Run `npx shadcn@latest add tooltip`

- [x] **Task 3: Add compact badge variant** (AC: 5.2.1)
  - [ ] Create smaller badge for inline use:
    ```jsx
    function PriorityBadgeSmall({ priority }) {
      const config = PRIORITY_CONFIG[priority];
      if (!config) return null;

      return (
        <span className={`text-xs px-1.5 py-0.5 rounded ${config.className}`}>
          {priority === 'CRITICAL' ? '!' : priority === 'IMPORTANT' ? '•' : ''}
        </span>
      );
    }

    export { PriorityBadgeSmall };
    ```

- [x] **Task 4: Integrate into DashboardPage** (AC: 5.2.4)
  - [ ] Add to DashboardPage:
    ```jsx
    import PriorityBadges from '@/components/PriorityBadges';

    // In render, after stats grid:
    <PriorityBadges
      priorities={data?.inferred_priorities}
      reasoning={data?.priority_reasoning}
    />
    ```

- [x] **Task 5: Add expandable reasoning option** (AC: 5.2.3)
  - [ ] Alternative to tooltip for mobile:
    ```jsx
    import { useState } from 'react';
    import { ChevronDown } from 'lucide-react';

    function PriorityBadgesWithReasoning({ priorities, reasoning }) {
      const [showReasoning, setShowReasoning] = useState(false);

      return (
        <div className="mb-6 p-4 bg-card rounded-lg border">
          {/* Badges */}
          <div className="flex flex-wrap gap-2 mb-2">
            {/* ... badges ... */}
          </div>

          {/* Expandable reasoning */}
          {reasoning && (
            <button
              onClick={() => setShowReasoning(!showReasoning)}
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground mt-2"
            >
              <ChevronDown className={`h-3 w-3 transition-transform ${showReasoning ? 'rotate-180' : ''}`} />
              Why these priorities?
            </button>
          )}
          {showReasoning && (
            <p className="text-sm text-muted-foreground mt-2 pl-4 border-l-2 border-primary/30">
              {reasoning}
            </p>
          )}
        </div>
      );
    }
    ```

- [x] **Task 6: Test priority display**
  - [x] Verify all 5 dimensions displayed
  - [x] Verify color coding matches priority
  - [x] Verify tooltip shows reasoning
  - [x] Test with missing priorities (fallback)

## Dev Notes

### Architecture Alignment

This story displays Level 1 output from the ranking system:
- **Source:** inferred_priorities from analysis response
- **Purpose:** Transparency into AI decision-making

### Priority Visual Hierarchy

| Priority | Color | Visual Weight |
|----------|-------|---------------|
| CRITICAL | Red | High - demands attention |
| IMPORTANT | Orange | Medium - notable |
| NICE_TO_HAVE | Gray | Low - subtle |
| LOW_PRIORITY | Dim Gray | Minimal - de-emphasized |

### Badge Layout

```
Job-Inferred Priorities                              [i]
┌─────────────────────────────────────────────────────┐
│ Experience: [CRITICAL]  Skills: [CRITICAL]          │
│ Projects: [IMPORTANT]   Positions: [NICE TO HAVE]   │
│ Education: [LOW]                                     │
└─────────────────────────────────────────────────────┘
```

### Usage in Score Bars

The `PriorityBadgeSmall` component is used in Story 5.4 next to score bars to indicate which dimensions are CRITICAL.

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#Priority-Badges]
- [Source: docs/epics.md#Story-5.2]
- [Source: docs/prd.md#FR38]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/5-2-inferred-priorities-display.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- shadcn tooltip component installed
- Vite build successful (4.32s)
- ESLint passes on PriorityBadges.jsx

### Completion Notes List

- All 6 tasks completed successfully
- All 4 acceptance criteria satisfied:
  - AC5.2.1: All 5 dimensions display with proper badges (Experience, Skills, Projects, Positions, Education)
  - AC5.2.2: Color coding matches priority (CRITICAL=red, IMPORTANT=orange, NICE_TO_HAVE=gray, LOW_PRIORITY=dim gray)
  - AC5.2.3: Reasoning shown in tooltip (desktop) and expandable section (mobile)
  - AC5.2.4: Section appears above candidate cards in DashboardPage
- PriorityBadgeSmall component exported for use in Story 5.4 score bars
- Mock data includes all priority levels for demonstration

### File List

**Created:**
- frontend/src/components/PriorityBadges.jsx
- frontend/src/components/ui/tooltip.jsx (shadcn)

**Modified:**
- frontend/src/pages/DashboardPage.jsx (added import and component usage)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
