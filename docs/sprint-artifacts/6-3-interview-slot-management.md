# Story 6.3: Interview Slot Management

Status: review

## Story

As a **HR professional**,
I want **to add interview time slots for candidates to choose from**,
So that **I can offer flexible scheduling options**.

## Acceptance Criteria

1. **AC6.3.1:** "Add Interview Slot" button is visible in email modal
2. **AC6.3.2:** Date picker and time picker appear when adding slot
3. **AC6.3.3:** Multiple slots can be added (3-5 recommended)
4. **AC6.3.4:** Added slots appear in a list with remove button
5. **AC6.3.5:** Slots are sorted by date/time
6. **AC6.3.6:** Slots must be in the future

## Tasks / Subtasks

- [ ] **Task 1: Create SlotPicker component** (AC: 6.3.1-6.3.4)
  - [ ] Create `src/components/SlotPicker.jsx`:
    ```jsx
    import { useState } from 'react';
    import { Calendar, Clock, Plus, X } from 'lucide-react';
    import { Button } from '@/components/ui/button';
    import { Input } from '@/components/ui/input';

    function SlotPicker({ slots, onSlotsChange }) {
      const [newDate, setNewDate] = useState('');
      const [newTime, setNewTime] = useState('');

      const addSlot = () => {
        if (!newDate || !newTime) return;

        const formattedDate = new Date(newDate).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        });

        // Convert 24h to 12h format
        const [hours, minutes] = newTime.split(':');
        const hour = parseInt(hours);
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const hour12 = hour % 12 || 12;
        const formattedTime = `${hour12}:${minutes} ${ampm}`;

        const newSlot = {
          date: formattedDate,
          time: formattedTime,
          sortKey: `${newDate}T${newTime}` // For sorting
        };

        const updatedSlots = [...slots, newSlot].sort(
          (a, b) => a.sortKey.localeCompare(b.sortKey)
        );

        onSlotsChange(updatedSlots);
        setNewDate('');
        setNewTime('');
      };

      const removeSlot = (index) => {
        const updated = slots.filter((_, i) => i !== index);
        onSlotsChange(updated);
      };

      // Get tomorrow's date as minimum
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const minDate = tomorrow.toISOString().split('T')[0];

      return (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium">Interview Slots</h4>
            <span className="text-xs text-muted-foreground">
              {slots.length} slot{slots.length !== 1 ? 's' : ''} added
            </span>
          </div>

          {/* Existing slots */}
          {slots.length > 0 && (
            <div className="space-y-2">
              {slots.map((slot, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 bg-muted/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{slot.date}</span>
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{slot.time}</span>
                  </div>
                  <button
                    onClick={() => removeSlot(index)}
                    className="p-1 hover:bg-destructive/10 rounded text-destructive"
                    aria-label="Remove slot"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Add new slot */}
          <div className="flex items-end gap-2">
            <div className="flex-1">
              <label className="text-xs text-muted-foreground mb-1 block">
                Date
              </label>
              <Input
                type="date"
                value={newDate}
                onChange={(e) => setNewDate(e.target.value)}
                min={minDate}
              />
            </div>
            <div className="flex-1">
              <label className="text-xs text-muted-foreground mb-1 block">
                Time
              </label>
              <Input
                type="time"
                value={newTime}
                onChange={(e) => setNewTime(e.target.value)}
              />
            </div>
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={addSlot}
              disabled={!newDate || !newTime}
              aria-label="Add slot"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>

          {/* Hint */}
          {slots.length === 0 && (
            <p className="text-xs text-muted-foreground">
              Add 3-5 time slots for candidates to choose from
            </p>
          )}
        </div>
      );
    }

    export default SlotPicker;
    ```

- [ ] **Task 2: Add slot validation** (AC: 6.3.6)
  - [ ] Validate slots are in the future:
    ```jsx
    const addSlot = () => {
      if (!newDate || !newTime) return;

      // Validate future date/time
      const slotDateTime = new Date(`${newDate}T${newTime}`);
      const now = new Date();

      if (slotDateTime <= now) {
        // Show toast or error
        toast({
          variant: 'destructive',
          title: 'Invalid slot',
          description: 'Interview slot must be in the future'
        });
        return;
      }

      // ... rest of add logic
    };
    ```

- [ ] **Task 3: Add duplicate detection**
  - [ ] Prevent adding duplicate slots:
    ```jsx
    const addSlot = () => {
      // ... validation ...

      const sortKey = `${newDate}T${newTime}`;

      // Check for duplicate
      if (slots.some(s => s.sortKey === sortKey)) {
        toast({
          variant: 'destructive',
          title: 'Duplicate slot',
          description: 'This time slot has already been added'
        });
        return;
      }

      // ... add slot
    };
    ```

- [ ] **Task 4: Integrate SlotPicker into EmailModal** (AC: 6.3.1-6.3.6)
  - [ ] Add to modal content:
    ```jsx
    import SlotPicker from '@/components/SlotPicker';

    function EmailModal({ open, onClose, selectedCandidates, ... }) {
      const [slots, setSlots] = useState([]);

      return (
        <Dialog open={open} onOpenChange={onClose}>
          <DialogContent className="max-w-2xl">
            {/* ... header ... */}

            <div className="space-y-6 py-4">
              {/* Recipients section */}
              <RecipientsSection candidates={selectedCandidates} />

              {/* Slot picker */}
              <SlotPicker
                slots={slots}
                onSlotsChange={setSlots}
              />

              {/* Message section */}
              <MessageSection ... />
            </div>

            {/* ... footer with buttons ... */}
          </DialogContent>
        </Dialog>
      );
    }
    ```

- [ ] **Task 5: Add slot summary in message preview**
  - [ ] Show how slots will appear in email:
    ```jsx
    function MessagePreview({ message, slots, recipientName, jobTitle }) {
      const formatSlotsForPreview = () => {
        if (slots.length === 0) return '[No slots added]';
        return slots.map(s => `  - ${s.date} at ${s.time}`).join('\n');
      };

      const preview = message
        .replace('{name}', recipientName || '[Candidate Name]')
        .replace('{job_title}', jobTitle || '[Job Title]')
        .replace('{company}', 'Yoboho')
        .replace('{slots}', formatSlotsForPreview());

      return (
        <div className="p-4 bg-muted/30 rounded-lg">
          <h4 className="text-sm font-medium mb-2">Preview</h4>
          <pre className="text-xs whitespace-pre-wrap font-mono">
            {preview}
          </pre>
        </div>
      );
    }
    ```

- [ ] **Task 6: Test slot management**
  - [ ] Add button shows date/time inputs
  - [ ] Selecting date and time enables add button
  - [ ] Added slot appears in list
  - [ ] Slots are sorted by date/time
  - [ ] Remove button removes slot
  - [ ] Past dates are disabled
  - [ ] Duplicate slots are rejected

## Dev Notes

### Architecture Alignment

This story adds interview slot management:
- **Component:** SlotPicker for adding/removing slots
- **Data:** Array of {date, time, sortKey} objects
- **Validation:** Future dates only, no duplicates

### Slot Data Structure

```javascript
{
  date: "Dec 6, 2025",      // Human-readable date
  time: "10:00 AM",         // Human-readable time
  sortKey: "2025-12-06T10:00"  // ISO format for sorting
}
```

### Date/Time Formatting

| Input | Output |
|-------|--------|
| 2025-12-06 | Dec 6, 2025 |
| 14:30 | 2:30 PM |
| 09:00 | 9:00 AM |

### Validation Rules

| Rule | Implementation |
|------|----------------|
| Future only | min attribute on date input, JS validation |
| No duplicates | Check sortKey before adding |
| Required fields | Disable add button if empty |

### Slot Limits

| Scenario | Handling |
|----------|----------|
| 0 slots | Show hint, disable send |
| 1-5 slots | Normal operation |
| 5+ slots | Allow (no hard limit) |

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-6.md#Slot-Picker]
- [Source: docs/epics.md#Story-6.3]
- [Source: docs/prd.md#FR59-FR60]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/6-3-interview-slot-management.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- SlotPicker component renders with date/time native inputs
- Add slot button disabled when date or time empty
- Future date validation using min attribute and JS validation
- Duplicate detection using sortKey comparison
- Slots sorted by date/time on add
- Remove button removes slot from list
- Error messages display inline for validation failures
- EmailModal integrates SlotPicker with message preview
- Preview shows formatted slots or "[No slots added]" placeholder
- Send button disabled when no slots added

### Completion Notes List

- All 6 tasks completed successfully
- All 6 acceptance criteria satisfied:
  - AC6.3.1: Add Interview Slot via date/time inputs with Plus button
  - AC6.3.2: Native date picker and time picker inputs
  - AC6.3.3: Multiple slots can be added (hint suggests 3-5)
  - AC6.3.4: Added slots appear in list with X remove button
  - AC6.3.5: Slots sorted by sortKey (ISO date-time format)
  - AC6.3.6: Future-only validation via min attribute and JS check
- Used inline error state instead of toast for validation feedback
- Added hint text when slots < 3 for flexibility reminder
- EmailModal shell created with Recipients, SlotPicker, Message Template, and Preview sections

### File List

**Created:**
- frontend/src/components/SlotPicker.jsx
- frontend/src/components/EmailModal.jsx
- frontend/src/components/ui/input.jsx (via shadcn)

**Modified:**
- frontend/src/pages/DashboardPage.jsx (EmailModal integration)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
