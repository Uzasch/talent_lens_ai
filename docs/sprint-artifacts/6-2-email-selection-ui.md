# Story 6.2: Email Selection UI

Status: review

## Story

As a **HR professional**,
I want **to select which candidates to email**,
So that **I control who receives interview invitations**.

## Acceptance Criteria

1. **AC6.2.1:** Each candidate card has a checkbox for email selection
2. **AC6.2.2:** "Email Selected" button shows count (e.g., "Email 3 Selected")
3. **AC6.2.3:** Button is disabled when no candidates are selected
4. **AC6.2.4:** Only candidates with valid emails can be selected

## Tasks / Subtasks

- [ ] **Task 1: Add selection state to DashboardPage** (AC: 6.2.1-6.2.3)
  - [ ] Add state management:
    ```jsx
    import { useState } from 'react';

    function DashboardPage() {
      const [selectedForEmail, setSelectedForEmail] = useState([]);
      const [showEmailModal, setShowEmailModal] = useState(false);

      const handleEmailSelect = (candidate) => {
        setSelectedForEmail(prev => {
          const exists = prev.some(c => c.id === candidate.id);
          if (exists) {
            return prev.filter(c => c.id !== candidate.id);
          }
          return [...prev, candidate];
        });
      };

      const isSelectedForEmail = (candidateId) => {
        return selectedForEmail.some(c => c.id === candidateId);
      };

      const clearEmailSelection = () => {
        setSelectedForEmail([]);
      };

      // ... render
    }
    ```

- [ ] **Task 2: Update CandidateCard with email checkbox** (AC: 6.2.1, 6.2.4)
  - [ ] Add checkbox to card:
    ```jsx
    import { Checkbox } from '@/components/ui/checkbox';

    function CandidateCard({
      candidate,
      onEmailSelect,
      isEmailSelected,
      ...props
    }) {
      const hasEmail = candidate.email && candidate.email.includes('@');

      return (
        <Card className="relative">
          {/* Email selection checkbox */}
          <div className="absolute top-3 right-3">
            <Checkbox
              checked={isEmailSelected}
              onCheckedChange={() => onEmailSelect(candidate)}
              disabled={!hasEmail}
              aria-label={`Select ${candidate.name} for email`}
            />
          </div>

          {/* Show email status */}
          {!hasEmail && (
            <div className="absolute top-3 right-10 text-xs text-muted-foreground">
              No email
            </div>
          )}

          {/* ... rest of card content ... */}
        </Card>
      );
    }
    ```

- [ ] **Task 3: Create EmailSelectedButton component** (AC: 6.2.2, 6.2.3)
  - [ ] Create `src/components/EmailSelectedButton.jsx`:
    ```jsx
    import { Mail } from 'lucide-react';
    import { Button } from '@/components/ui/button';

    function EmailSelectedButton({ count, onClick, disabled }) {
      return (
        <div className="fixed bottom-6 right-6 z-50">
          <Button
            size="lg"
            onClick={onClick}
            disabled={disabled || count === 0}
            className="shadow-lg"
          >
            <Mail className="h-5 w-5 mr-2" />
            {count === 0 ? 'Select candidates to email' : `Email ${count} Selected`}
          </Button>
        </div>
      );
    }

    export default EmailSelectedButton;
    ```

- [ ] **Task 4: Pass email props through CandidateCardGrid** (AC: 6.2.1)
  - [ ] Update grid to pass email selection:
    ```jsx
    function CandidateCardGrid({
      candidates,
      onEmailSelect,
      selectedForEmail,
      ...props
    }) {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {candidates.map((candidate) => (
            <CandidateCard
              key={candidate.id}
              candidate={candidate}
              onEmailSelect={onEmailSelect}
              isEmailSelected={selectedForEmail?.some(c => c.id === candidate.id)}
              {...props}
            />
          ))}
        </div>
      );
    }
    ```

- [ ] **Task 5: Integrate in DashboardPage** (AC: 6.2.1-6.2.4)
  - [ ] Add components to dashboard:
    ```jsx
    import EmailSelectedButton from '@/components/EmailSelectedButton';
    import EmailModal from '@/components/EmailModal';

    // In DashboardPage render:
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* ... other sections ... */}

        {/* Top Candidates */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Top Candidates</h2>
          <CandidateCardGrid
            candidates={data.top_candidates}
            onEmailSelect={handleEmailSelect}
            selectedForEmail={selectedForEmail}
            {...otherProps}
          />
        </section>

        {/* Email Button */}
        <EmailSelectedButton
          count={selectedForEmail.length}
          onClick={() => setShowEmailModal(true)}
          disabled={selectedForEmail.length === 0}
        />

        {/* Email Modal */}
        <EmailModal
          open={showEmailModal}
          onClose={() => {
            setShowEmailModal(false);
            clearEmailSelection();
          }}
          selectedCandidates={selectedForEmail}
          sessionId={sessionId}
          jobTitle={data?.role?.title}
        />
      </div>
    );
    ```

- [ ] **Task 6: Add visual feedback for selection** (AC: 6.2.1)
  - [ ] Highlight selected cards:
    ```jsx
    <Card className={`relative transition-all ${
      isEmailSelected
        ? 'ring-2 ring-primary bg-primary/5'
        : ''
    }`}>
    ```

- [ ] **Task 7: Test email selection**
  - [ ] Verify checkbox appears on each card
  - [ ] Verify selecting updates button count
  - [ ] Verify button disabled when none selected
  - [ ] Verify cards without email show disabled checkbox
  - [ ] Verify selected cards have visual highlight

## Dev Notes

### Architecture Alignment

This story adds email selection functionality to the dashboard:
- **State:** Selected candidates stored in DashboardPage state
- **UI:** Checkbox on each card, floating button
- **Validation:** Only candidates with valid emails selectable

### Selection Flow

```
Initial State: [] selected
      │
Click checkbox on Card A
      │
      ▼
State: [A] - Button shows "Email 1 Selected"
      │
Click checkbox on Card B
      │
      ▼
State: [A, B] - Button shows "Email 2 Selected"
      │
Click button
      │
      ▼
Modal opens with A and B as recipients
```

### Visual States

| State | Display |
|-------|---------|
| Not selected | Empty checkbox |
| Selected | Checked, card has ring |
| No email | Disabled checkbox, "No email" label |
| Button (0 selected) | Disabled, "Select candidates to email" |
| Button (N selected) | Enabled, "Email N Selected" |

### Component Props

**CandidateCard:**
```typescript
interface CandidateCardProps {
  candidate: Candidate;
  onEmailSelect: (candidate: Candidate) => void;
  isEmailSelected: boolean;
  // ... other props
}
```

**EmailSelectedButton:**
```typescript
interface EmailSelectedButtonProps {
  count: number;
  onClick: () => void;
  disabled?: boolean;
}
```

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-6.md#Email-Selection]
- [Source: docs/epics.md#Story-6.2]
- [Source: docs/prd.md#FR58]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/6-2-email-selection-ui.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Checkbox appears on each candidate card with proper aria-label
- Button shows "Select candidates to email" when none selected (disabled)
- Button shows "Email 1 Selected" after first selection
- Button shows "Email 2 Selected" after second selection
- Checkboxes disabled for candidates without valid email (hasValidEmail check)
- Selected cards have green ring visual feedback

### Completion Notes List

- All 7 tasks completed successfully
- All 4 acceptance criteria satisfied:
  - AC6.2.1: Each candidate card has checkbox for email selection
  - AC6.2.2: Button shows count (e.g., "Email 2 Selected")
  - AC6.2.3: Button disabled when no candidates selected
  - AC6.2.4: Only candidates with valid emails can be selected
- Changed selection state to store full candidate objects for email modal
- Added green ring highlight for selected cards
- EmailSelectedButton component created as floating button

### File List

**Created:**
- frontend/src/components/EmailSelectedButton.jsx

**Modified:**
- frontend/src/components/CandidateCard.jsx (email validation, visual highlight, prop changes)
- frontend/src/pages/DashboardPage.jsx (email selection state, handlers, EmailSelectedButton integration)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
