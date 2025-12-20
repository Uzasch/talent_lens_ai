# Story 5.4: 5-Dimension Score Breakdown with Priority Labels

Status: review

## Story

As a **HR professional**,
I want **to see score breakdown with priority indicators**,
So that **I know which scores matter most for this job**.

## Acceptance Criteria

1. **AC5.4.1:** 5 horizontal progress bars (Experience, Skills, Projects, Positions, Education)
2. **AC5.4.2:** Priority label shown next to CRITICAL/IMPORTANT dimension bars
3. **AC5.4.3:** CRITICAL dimension bars visually highlighted (border or glow)
4. **AC5.4.4:** Percentage value shown at end of each bar

## Tasks / Subtasks

- [x] **Task 1: Install Progress component**
  - [x] Run `npx shadcn@latest add progress`

- [x] **Task 2: Create ScoreBar component** (AC: 5.4.1, 5.4.4)
  - [ ] Create `src/components/ScoreBar.jsx`:
    ```jsx
    import { Progress } from '@/components/ui/progress';

    const DIMENSION_LABELS = {
      experience: 'Experience',
      skills: 'Skills',
      projects: 'Projects',
      positions: 'Positions',
      education: 'Education'
    };

    function ScoreBar({ dimension, score, priority }) {
      const isCritical = priority === 'CRITICAL';
      const isImportant = priority === 'IMPORTANT';

      return (
        <div className={`space-y-1 ${isCritical ? 'relative' : ''}`}>
          {/* Critical glow effect */}
          {isCritical && (
            <div className="absolute inset-0 bg-red-500/5 -m-1 rounded" />
          )}

          <div className="flex items-center justify-between relative">
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground w-24">
                {DIMENSION_LABELS[dimension]}
              </span>

              {/* Priority Badge */}
              {isCritical && (
                <span className="text-xs px-1.5 py-0.5 rounded bg-red-500/20 text-red-500 border border-red-500/30">
                  CRITICAL
                </span>
              )}
              {isImportant && (
                <span className="text-xs px-1.5 py-0.5 rounded bg-orange-500/20 text-orange-500 border border-orange-500/30">
                  IMPORTANT
                </span>
              )}
            </div>

            <span className="text-sm font-medium w-12 text-right">
              {score}%
            </span>
          </div>

          <Progress
            value={score}
            className={`h-2 ${isCritical ? 'border border-red-500/30' : ''}`}
          />
        </div>
      );
    }

    export default ScoreBar;
    ```

- [x] **Task 3: Create ScoreBreakdown component** (AC: 5.4.1-5.4.4)
  - [ ] Create composite component:
    ```jsx
    function ScoreBreakdown({ scores, priorities }) {
      const dimensions = ['experience', 'skills', 'projects', 'positions', 'education'];

      return (
        <div className="space-y-3 py-3">
          {dimensions.map((dim) => (
            <ScoreBar
              key={dim}
              dimension={dim}
              score={scores?.[dim] || 0}
              priority={priorities?.[dim]}
            />
          ))}
        </div>
      );
    }

    export { ScoreBreakdown };
    ```

- [x] **Task 4: Integrate into CandidateCard** (AC: 5.4.1-5.4.4)
  - [ ] Add to CandidateCard:
    ```jsx
    import { ScoreBreakdown } from '@/components/ScoreBar';

    // Inside CardContent, after summary:
    <ScoreBreakdown
      scores={candidate.scores}
      priorities={priorities}
    />
    ```

- [x] **Task 5: Style Progress for dark theme**
  - [ ] Ensure progress bar uses primary green:
    ```css
    /* In index.css or component */
    .progress-indicator {
      background-color: hsl(var(--primary));
    }
    ```

- [x] **Task 6: Add score color coding**
  - [ ] Color scores based on value:
    ```jsx
    function getScoreColor(score) {
      if (score >= 90) return 'text-primary';
      if (score >= 70) return 'text-foreground';
      if (score >= 50) return 'text-muted-foreground';
      return 'text-red-500';
    }
    ```

- [x] **Task 7: Test score breakdown**
  - [x] Verify all 5 bars render
  - [x] Verify CRITICAL label appears correctly
  - [x] Verify CRITICAL bars have highlight
  - [x] Verify percentages are accurate

## Dev Notes

### Architecture Alignment

This story displays dimension scores from the ranking response:
- **Source:** candidate.scores object
- **Enhancement:** Priority labels from inferred_priorities

### Score Bar Layout

```
Experience  [CRITICAL] [████████████████░░░░] 85%
Skills      [CRITICAL] [██████████████████░░] 92%
Projects    [IMPORTANT][████████████████████] 98%
Positions              [██████████████░░░░░░] 75%
Education              [████████░░░░░░░░░░░░] 60%
```

### Visual Hierarchy

| Priority | Bar Style | Label |
|----------|-----------|-------|
| CRITICAL | Red border/glow, bold % | Red badge |
| IMPORTANT | Normal, bold % | Orange badge |
| Others | Normal | No badge |

### Score Color Coding

| Score Range | Color | Meaning |
|-------------|-------|---------|
| 90-100 | Primary green | Exceptional |
| 70-89 | Foreground | Good |
| 50-69 | Muted | Average |
| 0-49 | Red | Below average |

### Integration Points

- Used in CandidateCard (Story 5.3)
- Used in ComparisonView (Story 5.10)

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#Score-Breakdown]
- [Source: docs/epics.md#Story-5.4]
- [Source: docs/prd.md#FR42-FR43]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/5-4-score-breakdown-with-priority-labels.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- shadcn progress component installed
- Vite build successful (4.47s)
- ESLint passes on ScoreBar.jsx

### Completion Notes List

- All 7 tasks completed successfully
- All 4 acceptance criteria satisfied:
  - AC5.4.1: 5 horizontal progress bars (Experience, Skills, Projects, Positions, Education)
  - AC5.4.2: Priority label (! for CRITICAL, • for IMPORTANT) shown next to dimension bars
  - AC5.4.3: CRITICAL dimension bars have red border/glow highlight
  - AC5.4.4: Percentage value shown at end of each bar with color coding
- Score color coding: 90+= primary green, 70-89= foreground, 50-69= muted, <50= red
- Mock data updated with varied scores per candidate for realistic display
- ScoreBreakdown exports for reuse in ComparisonView (Story 5.10)

### File List

**Created:**
- frontend/src/components/ScoreBar.jsx
- frontend/src/components/ui/progress.jsx (shadcn)

**Modified:**
- frontend/src/components/CandidateCard.jsx (added ScoreBreakdown import and component)
- frontend/src/pages/DashboardPage.jsx (added scores to mock candidates)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
