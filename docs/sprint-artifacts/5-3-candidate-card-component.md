# Story 5.3: Candidate Card Component with Priority Labels

Status: review

## Story

As a **HR professional**,
I want **to see each top candidate with dimension priority indicators**,
So that **I know where they excel in CRITICAL areas**.

## Acceptance Criteria

1. **AC5.3.1:** Rank badge in top-left (#1, #2, etc.)
2. **AC5.3.2:** Tie-breaker icon (⚖️) shown if tie_breaker_applied is true
3. **AC5.3.3:** Name (bold), match percentage (large, green), 3-bullet summary displayed
4. **AC5.3.4:** Checkbox for email selection
5. **AC5.3.5:** Card #1 has visual emphasis (border glow or different background)

## Tasks / Subtasks

- [x] **Task 1: Install Checkbox component** (AC: 5.3.4)
  - [x] Run `npx shadcn@latest add checkbox`

- [x] **Task 2: Create CandidateCard component** (AC: 5.3.1-5.3.5)
  - [ ] Create `src/components/CandidateCard.jsx`:
    ```jsx
    import { Card, CardContent, CardHeader } from '@/components/ui/card';
    import { Checkbox } from '@/components/ui/checkbox';
    import { Scale } from 'lucide-react';

    function CandidateCard({
      candidate,
      priorities,
      isSelected,
      onSelect,
      onCompare,
      compareMode
    }) {
      const {
        rank,
        name,
        email,
        match_score,
        summary,
        tie_breaker_applied
      } = candidate;

      const isTopCandidate = rank === 1;

      return (
        <Card className={`relative transition-all hover:border-primary/50 ${
          isTopCandidate ? 'border-primary shadow-lg shadow-primary/10' : ''
        } ${compareMode ? 'cursor-pointer' : ''}`}>
          {/* Rank Badge */}
          <div className={`absolute -top-3 -left-3 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
            isTopCandidate
              ? 'bg-primary text-primary-foreground'
              : 'bg-card border text-foreground'
          }`}>
            #{rank}
          </div>

          {/* Tie-breaker Icon */}
          {tie_breaker_applied && (
            <div className="absolute -top-2 -right-2">
              <span title="Tie-breaker applied" className="text-lg">⚖️</span>
            </div>
          )}

          <CardHeader className="pt-6 pb-2">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-lg">{name}</h3>
                <p className="text-sm text-muted-foreground">{email}</p>
              </div>

              {/* Match Score */}
              <div className="text-right">
                <span className="text-3xl font-bold text-primary">
                  {match_score}%
                </span>
                <p className="text-xs text-muted-foreground">match</p>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            {/* Summary Bullets */}
            <ul className="space-y-1">
              {summary?.map((bullet, i) => (
                <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>{bullet}</span>
                </li>
              ))}
            </ul>

            {/* Score Breakdown - Story 5.4 */}
            {/* WHY Section - Story 5.5 */}

            {/* Actions */}
            <div className="flex items-center justify-between pt-2 border-t">
              <div className="flex items-center gap-2">
                <Checkbox
                  id={`select-${candidate.id}`}
                  checked={isSelected}
                  onCheckedChange={() => onSelect(candidate.id)}
                />
                <label
                  htmlFor={`select-${candidate.id}`}
                  className="text-sm text-muted-foreground cursor-pointer"
                >
                  Select for email
                </label>
              </div>

              <button
                onClick={() => onCompare(candidate)}
                className="text-sm text-primary hover:underline"
              >
                Compare
              </button>
            </div>
          </CardContent>
        </Card>
      );
    }

    export default CandidateCard;
    ```

- [x] **Task 3: Create CandidateCardGrid component** (AC: 5.3.5)
  - [ ] Grid layout for top 6:
    ```jsx
    function CandidateCardGrid({
      candidates,
      priorities,
      selectedIds,
      onSelect,
      onCompare
    }) {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {candidates.map((candidate) => (
            <CandidateCard
              key={candidate.id}
              candidate={candidate}
              priorities={priorities}
              isSelected={selectedIds.includes(candidate.id)}
              onSelect={onSelect}
              onCompare={onCompare}
            />
          ))}
        </div>
      );
    }

    export { CandidateCardGrid };
    ```

- [x] **Task 4: Add selection state management**
  - [ ] Add to DashboardPage:
    ```jsx
    const [selectedCandidates, setSelectedCandidates] = useState([]);

    const handleSelectCandidate = (candidateId) => {
      setSelectedCandidates(prev =>
        prev.includes(candidateId)
          ? prev.filter(id => id !== candidateId)
          : [...prev, candidateId]
      );
    };
    ```

- [x] **Task 5: Add "Email Selected" button**
  - [ ] Show count of selected:
    ```jsx
    {selectedCandidates.length > 0 && (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setShowEmailModal(true)}
          className="bg-primary text-primary-foreground px-4 py-2 rounded-lg shadow-lg flex items-center gap-2"
        >
          <Mail className="h-4 w-4" />
          Email {selectedCandidates.length} Selected
        </button>
      </div>
    )}
    ```

- [x] **Task 6: Test candidate cards**
  - [x] Verify rank badge positioning
  - [x] Verify tie-breaker icon shows conditionally
  - [x] Verify #1 card has emphasis
  - [x] Verify checkbox toggles selection
  - [x] Test compare button click

## Dev Notes

### Architecture Alignment

This story implements the main candidate display per UX specification:
- **Cards:** Top 6 candidates in grid
- **Emphasis:** #1 candidate has visual prominence
- **Actions:** Email selection, comparison

### Card Layout

```
┌─────────────────────────────────────────┐
│ [#1]                              ⚖️    │
│                                         │
│ Sara Ahmed                        94%   │
│ sara@email.com                   match  │
│                                         │
│ • 5 years Python at Google              │
│ • Led team of 5 on ML project           │
│ • Junior→Senior in 3 years              │
│                                         │
│ [Score Bars - Story 5.4]                │
│                                         │
│ [WHY Section - Story 5.5]               │
│─────────────────────────────────────────│
│ [✓] Select for email      [Compare]     │
└─────────────────────────────────────────┘
```

### Visual Hierarchy

| Element | Style |
|---------|-------|
| Rank #1 | Primary background, glow |
| Rank #2-6 | Bordered, muted |
| Match Score | Large, primary green |
| Summary | Muted foreground |
| Tie-breaker | ⚖️ emoji, tooltip |

### Comparison Flow

1. Click "Compare" on first candidate → selected state
2. Click "Compare" on second → opens ComparisonModal
3. Max 2 candidates in comparison

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#Candidate-Cards]
- [Source: docs/ux-design-specification.md#Cards]
- [Source: docs/epics.md#Story-5.3]
- [Source: docs/prd.md#FR40-FR41, FR45-FR46]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/5-3-candidate-card-component.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- shadcn checkbox component installed
- Vite build successful (4.50s)
- ESLint passes on CandidateCard.jsx

### Completion Notes List

- All 6 tasks completed successfully
- All 5 acceptance criteria satisfied:
  - AC5.3.1: Rank badge in top-left (#1, #2, etc.) with proper positioning
  - AC5.3.2: Tie-breaker icon (⚖️) shown with tooltip when tie_breaker_applied is true
  - AC5.3.3: Name (bold), match percentage (large, green), 3-bullet summary displayed
  - AC5.3.4: Checkbox for email selection with state management
  - AC5.3.5: Card #1 has visual emphasis (primary border and shadow glow)
- Fixed positioning for Email Selected button (fixed bottom-right)
- Mock data includes 6 candidates with varied scores and tie-breaker flags
- Compare button wired up (logs to console, implementation in Story 5.9/5.10)

### File List

**Created:**
- frontend/src/components/CandidateCard.jsx
- frontend/src/components/ui/checkbox.jsx (shadcn)

**Modified:**
- frontend/src/pages/DashboardPage.jsx (added CandidateCardGrid, selection state, Email button)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
