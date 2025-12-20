# Story 5.9: Side-by-Side Comparison Selection

Status: review

## Story

As a **HR professional**,
I want **to select two candidates to compare**,
So that **I can see them head-to-head**.

## Acceptance Criteria

1. **AC5.9.1:** "Compare" button visible on each candidate card
2. **AC5.9.2:** First click shows "selected for comparison" state
3. **AC5.9.3:** Second click on different candidate opens comparison modal
4. **AC5.9.4:** Maximum 2 candidates can be selected (third replaces second)

## Tasks / Subtasks

- [x] **Task 1: Add comparison state to DashboardPage** (AC: 5.9.2-5.9.4)
  - [ ] Add state management:
    ```jsx
    const [compareSelection, setCompareSelection] = useState([]);
    const [showComparison, setShowComparison] = useState(false);

    const handleCompare = (candidate) => {
      setCompareSelection(prev => {
        // If already selected, deselect
        if (prev.some(c => c.id === candidate.id)) {
          return prev.filter(c => c.id !== candidate.id);
        }

        // If we have 2 already, replace the second
        if (prev.length >= 2) {
          return [prev[0], candidate];
        }

        // Add to selection
        const newSelection = [...prev, candidate];

        // If we now have 2, open modal
        if (newSelection.length === 2) {
          setShowComparison(true);
        }

        return newSelection;
      });
    };

    const clearComparison = () => {
      setCompareSelection([]);
      setShowComparison(false);
    };
    ```

- [x] **Task 2: Update CandidateCard compare button** (AC: 5.9.1, 5.9.2)
  - [ ] Add selected state styling:
    ```jsx
    function CandidateCard({ candidate, onCompare, isCompareSelected }) {
      return (
        <Card className={`${isCompareSelected ? 'ring-2 ring-primary' : ''}`}>
          {/* ... other content ... */}

          <button
            onClick={() => onCompare(candidate)}
            className={`text-sm ${
              isCompareSelected
                ? 'bg-primary text-primary-foreground px-3 py-1 rounded'
                : 'text-primary hover:underline'
            }`}
          >
            {isCompareSelected ? '✓ Selected' : 'Compare'}
          </button>
        </Card>
      );
    }
    ```

- [x] **Task 3: Add comparison indicator bar** (AC: 5.9.2)
  - [ ] Show when 1 candidate selected:
    ```jsx
    function ComparisonIndicator({ selection, onClear }) {
      if (selection.length === 0) return null;

      return (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 bg-card border rounded-lg shadow-lg p-4 flex items-center gap-4">
          <div className="text-sm">
            <span className="font-medium">{selection[0]?.name}</span>
            {selection.length === 1 && (
              <span className="text-muted-foreground ml-2">
                Select another candidate to compare
              </span>
            )}
            {selection.length === 2 && (
              <>
                <span className="text-muted-foreground mx-2">vs</span>
                <span className="font-medium">{selection[1]?.name}</span>
              </>
            )}
          </div>

          <button
            onClick={onClear}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Clear
          </button>
        </div>
      );
    }
    ```

- [x] **Task 4: Pass compare props to cards** (AC: 5.9.1-5.9.4)
  - [ ] Update CandidateCardGrid:
    ```jsx
    <CandidateCardGrid
      candidates={data.top_candidates}
      priorities={data.inferred_priorities}
      selectedIds={selectedCandidates}
      onSelect={handleSelectCandidate}
      onCompare={handleCompare}
      compareSelection={compareSelection}
    />
    ```
  - [ ] Update grid to pass isCompareSelected:
    ```jsx
    function CandidateCardGrid({ candidates, compareSelection, onCompare, ...props }) {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {candidates.map((candidate) => (
            <CandidateCard
              key={candidate.id}
              candidate={candidate}
              isCompareSelected={compareSelection?.some(c => c.id === candidate.id)}
              onCompare={onCompare}
              {...props}
            />
          ))}
        </div>
      );
    }
    ```

- [x] **Task 5: Add keyboard support**
  - [ ] ESC to clear selection:
    ```jsx
    useEffect(() => {
      const handleKeyDown = (e) => {
        if (e.key === 'Escape' && compareSelection.length > 0) {
          clearComparison();
        }
      };

      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }, [compareSelection]);
    ```

- [x] **Task 6: Test comparison selection**
  - [x] Click Compare on card 1 → shows selected state
  - [x] Click Compare on card 2 → opens modal
  - [x] Click selected card → deselects
  - [x] Select 2, click 3rd → replaces 2nd
  - [x] ESC clears selection

## Dev Notes

### Architecture Alignment

This story enables the comparison feature:
- **Selection:** Max 2 candidates at a time
- **Flow:** Select → Select → Modal opens

### Selection Flow

```
Initial State: []
      │
Click "Compare" on Card A
      │
      ▼
State: [A] - Card A shows "✓ Selected"
      │
Click "Compare" on Card B
      │
      ▼
State: [A, B] - Modal opens automatically
      │
Click "Compare" on Card C
      │
      ▼
State: [A, C] - C replaces B
```

### UI States

| State | Display |
|-------|---------|
| Not selected | "Compare" link |
| Selected | "✓ Selected" button, card ring |
| 1 selected | Bottom bar: "Select another..." |
| 2 selected | Modal opens automatically |

### Visual Indicators

```
┌─────────────────┐  ┌─────────────────┐
│ #1 Sara Ahmed   │  │ #2 Ali Khan     │
│ [✓ Selected]    │  │ [Compare]       │
│ ═══ring═══      │  │                 │
└─────────────────┘  └─────────────────┘

┌───────────────────────────────────────┐
│ Sara Ahmed   Select another to compare│
└───────────────────────────────────────┘
```

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#Comparison-Selection]
- [Source: docs/epics.md#Story-5.9]
- [Source: docs/prd.md#FR52]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/5-9-side-by-side-comparison-selection.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Vite HMR updates applied successfully
- All comparison flows tested via browser DevTools
- ESC key handler verified working

### Completion Notes List

- All 6 tasks completed successfully
- All 4 acceptance criteria satisfied:
  - AC5.9.1: "Compare" button visible on each candidate card
  - AC5.9.2: First click shows "Selected" state with ring indicator
  - AC5.9.3: Second click on different candidate opens comparison modal
  - AC5.9.4: Third candidate replaces second (first is preserved)
- Added `closeComparisonModal` function to allow modal close without clearing selection (enables AC5.9.4 UX)
- ComparisonIndicator component shows selection status at bottom of screen
- ESC key clears comparison selection (bonus accessibility feature)
- Modal placeholder ready for Story 5.10 implementation

### File List

**Created:**
- (none - extended existing files)

**Modified:**
- frontend/src/components/CandidateCard.jsx (added isCompareSelected prop, ring styling, Selected button state)
- frontend/src/pages/DashboardPage.jsx (compareSelection state, handleCompare, clearComparison, closeComparisonModal, ComparisonIndicator component, keyboard handler, comparison modal placeholder)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
