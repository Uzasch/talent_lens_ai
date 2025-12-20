# Story 5.10: Comparison View Component

Status: review

## Story

As a **HR professional**,
I want **to see two candidates side-by-side with visual score comparison**,
So that **I can easily see who is stronger in each dimension**.

## Acceptance Criteria

1. **AC5.10.1:** Side-by-side display of both candidates' names and match scores
2. **AC5.10.2:** All 5 dimension scores shown with visual bars
3. **AC5.10.3:** Winner highlighted per dimension (green for higher score)
4. **AC5.10.4:** Overall winner clearly indicated at top
5. **AC5.10.5:** Close button returns to dashboard

## Tasks / Subtasks

- [x] **Task 1: Install Dialog component**
  - [x] Dialog component already installed

- [x] **Task 2: Create ComparisonModal component** (AC: 5.10.1-5.10.5)
  - [ ] Create `src/components/ComparisonModal.jsx`:
    ```jsx
    import { useEffect, useState } from 'react';
    import { X, Trophy, Minus } from 'lucide-react';
    import {
      Dialog,
      DialogContent,
      DialogHeader,
      DialogTitle,
    } from '@/components/ui/dialog';
    import { Progress } from '@/components/ui/progress';
    import { compareCandidate } from '@/services/api';

    function ComparisonModal({ open, onClose, candidates, sessionId }) {
      const [comparison, setComparison] = useState(null);
      const [loading, setLoading] = useState(false);

      useEffect(() => {
        if (open && candidates.length === 2) {
          fetchComparison();
        }
      }, [open, candidates]);

      const fetchComparison = async () => {
        setLoading(true);
        try {
          const response = await compareCandidate(
            sessionId,
            candidates[0].id,
            candidates[1].id
          );
          if (response.success) {
            setComparison(response.data);
          }
        } catch (error) {
          console.error('Comparison error:', error);
        } finally {
          setLoading(false);
        }
      };

      const candidate1 = candidates[0];
      const candidate2 = candidates[1];

      return (
        <Dialog open={open} onOpenChange={onClose}>
          <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center justify-between">
                <span>Candidate Comparison</span>
                <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
                  <X className="h-5 w-5" />
                </button>
              </DialogTitle>
            </DialogHeader>

            {loading ? (
              <ComparisonSkeleton />
            ) : (
              <div className="space-y-6">
                {/* Header with names and overall winner */}
                <ComparisonHeader
                  candidate1={candidate1}
                  candidate2={candidate2}
                  winner={comparison?.overall_winner}
                />

                {/* Score comparison bars */}
                <ScoreComparison
                  candidate1={candidate1}
                  candidate2={candidate2}
                  dimensionWinners={comparison?.dimension_winners}
                />

                {/* AI Explanation */}
                {comparison?.explanation && (
                  <AIExplanation explanation={comparison.explanation} />
                )}

                {/* Key differences */}
                {comparison?.key_differences && (
                  <KeyDifferences differences={comparison.key_differences} />
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>
      );
    }

    export default ComparisonModal;
    ```

- [x] **Task 3: Create ComparisonHeader component** (AC: 5.10.1, 5.10.4)
  - [ ] Show candidates and winner:
    ```jsx
    function ComparisonHeader({ candidate1, candidate2, winner }) {
      const isCandidate1Winner = winner === 'candidate_1';
      const isCandidate2Winner = winner === 'candidate_2';

      return (
        <div className="grid grid-cols-2 gap-4">
          <CandidateHeaderCard
            candidate={candidate1}
            isWinner={isCandidate1Winner}
            label="Candidate A"
          />
          <CandidateHeaderCard
            candidate={candidate2}
            isWinner={isCandidate2Winner}
            label="Candidate B"
          />
        </div>
      );
    }

    function CandidateHeaderCard({ candidate, isWinner, label }) {
      return (
        <div className={`p-4 rounded-lg border ${
          isWinner ? 'border-primary bg-primary/5' : 'border-border'
        }`}>
          {isWinner && (
            <div className="flex items-center gap-1 text-primary text-sm mb-2">
              <Trophy className="h-4 w-4" />
              Overall Winner
            </div>
          )}
          <p className="text-xs text-muted-foreground">{label}</p>
          <h3 className="font-semibold text-lg">{candidate.name}</h3>
          <p className="text-3xl font-bold text-primary mt-1">
            {candidate.match_score}%
          </p>
        </div>
      );
    }
    ```

- [x] **Task 4: Create ScoreComparison component** (AC: 5.10.2, 5.10.3)
  - [ ] Side-by-side score bars:
    ```jsx
    function ScoreComparison({ candidate1, candidate2, dimensionWinners }) {
      const dimensions = ['experience', 'skills', 'projects', 'positions', 'education'];

      const labels = {
        experience: 'Experience',
        skills: 'Skills',
        projects: 'Projects',
        positions: 'Positions',
        education: 'Education'
      };

      return (
        <div className="space-y-4">
          <h4 className="font-medium">Dimension Comparison</h4>

          {dimensions.map((dim) => {
            const score1 = candidate1.scores?.[dim] || 0;
            const score2 = candidate2.scores?.[dim] || 0;
            const winner = dimensionWinners?.[dim];

            return (
              <div key={dim} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">{labels[dim]}</span>
                  <div className="flex items-center gap-2">
                    {winner === 'candidate_1' && <span className="text-primary">◄</span>}
                    {winner === 'tie' && <Minus className="h-3 w-3 text-muted-foreground" />}
                    {winner === 'candidate_2' && <span className="text-primary">►</span>}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="flex items-center gap-2">
                    <Progress
                      value={score1}
                      className={`h-3 flex-1 ${winner === 'candidate_1' ? 'border border-primary' : ''}`}
                    />
                    <span className={`text-sm w-10 ${winner === 'candidate_1' ? 'text-primary font-bold' : ''}`}>
                      {score1}%
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`text-sm w-10 text-right ${winner === 'candidate_2' ? 'text-primary font-bold' : ''}`}>
                      {score2}%
                    </span>
                    <Progress
                      value={score2}
                      className={`h-3 flex-1 ${winner === 'candidate_2' ? 'border border-primary' : ''}`}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      );
    }
    ```

- [x] **Task 5: Create AIExplanation component**
  - [ ] Display AI comparison text:
    ```jsx
    function AIExplanation({ explanation }) {
      return (
        <div className="p-4 bg-muted/30 rounded-lg">
          <h4 className="font-medium mb-2 flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-primary" />
            AI Analysis
          </h4>
          <p className="text-sm text-muted-foreground">{explanation}</p>
        </div>
      );
    }

    function KeyDifferences({ differences }) {
      return (
        <div>
          <h4 className="font-medium mb-2">Key Differences</h4>
          <ul className="space-y-1">
            {differences.map((diff, i) => (
              <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                <span className="text-primary">•</span>
                {diff}
              </li>
            ))}
          </ul>
        </div>
      );
    }
    ```

- [x] **Task 6: Test comparison modal**
  - [x] Verify modal opens with 2 candidates
  - [x] Verify scores displayed correctly
  - [x] Verify winner highlighting
  - [x] Verify close button works (ESC)
  - [x] Test loading state (mock data fallback)

## Dev Notes

### Architecture Alignment

This story displays the visual comparison view:
- **Modal:** shadcn/ui Dialog component
- **Data:** From POST /api/compare endpoint

### Comparison Layout

```
┌─────────────────────────────────────────────────────┐
│ Candidate Comparison                            [X] │
├─────────────────────────────────────────────────────┤
│  ┌───────────────────┐  ┌───────────────────┐      │
│  │ 🏆 Overall Winner │  │ Candidate B       │      │
│  │ Candidate A       │  │                   │      │
│  │ Sara Ahmed        │  │ Ali Khan          │      │
│  │ 94%               │  │ 91%               │      │
│  └───────────────────┘  └───────────────────┘      │
│                                                     │
│ Dimension Comparison                                │
│ Experience    ◄                                     │
│ [████████████95%] [██████████78%]                  │
│                                                     │
│ Skills                          ►                   │
│ [████████████88%] [██████████████95%]              │
│ ...                                                 │
│                                                     │
│ AI Analysis                                         │
│ Sara ranks higher because Experience is CRITICAL... │
│                                                     │
│ Key Differences                                     │
│ • Experience: Sara's 5yr at Google vs Ali's 3yr... │
│ • Skills: Ali's broader stack vs Sara's deeper...  │
└─────────────────────────────────────────────────────┘
```

### Winner Indicators

| Winner | Visual |
|--------|--------|
| Candidate 1 | ◄ arrow, green border, bold score |
| Candidate 2 | ► arrow, green border, bold score |
| Tie | - dash |

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#Comparison-View]
- [Source: docs/epics.md#Story-5.10]
- [Source: docs/prd.md#FR53-FR54, FR57]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/5-10-comparison-view-component.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Vite HMR updates applied successfully
- Modal opens correctly when 2 candidates selected
- Mock comparison data generated for development (backend unavailable)
- ESC key closes modal and returns to dashboard

### Completion Notes List

- All 6 tasks completed successfully
- All 5 acceptance criteria satisfied:
  - AC5.10.1: Side-by-side display with names and match scores
  - AC5.10.2: All 5 dimension scores shown with visual progress bars
  - AC5.10.3: Winner highlighted per dimension (◄/► arrows, bold green scores)
  - AC5.10.4: Overall winner with trophy badge at top
  - AC5.10.5: Close button (ESC) returns to dashboard
- Created ComparisonModal with sub-components: ComparisonHeader, CandidateHeaderCard, ScoreComparison, AIExplanation, KeyDifferences, ComparisonSkeleton
- Mock data generation for development when API unavailable
- Uses shadcn/ui Dialog component for modal

### File List

**Created:**
- frontend/src/components/ComparisonModal.jsx (full comparison modal with all sub-components)

**Modified:**
- frontend/src/pages/DashboardPage.jsx (imported and integrated ComparisonModal)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
