# Story 6.4: Email Confirmation Modal

Status: review

## Story

As a **HR professional**,
I want **to preview and customize the email before sending**,
So that **I ensure the message is appropriate**.

## Acceptance Criteria

1. **AC6.4.1:** Modal shows list of selected recipients (names and emails)
2. **AC6.4.2:** Interview slots are displayed formatted nicely
3. **AC6.4.3:** Editable message template with placeholders: {name}, {job_title}, {company}, {slots}
4. **AC6.4.4:** Preview shows how email will look with placeholders replaced
5. **AC6.4.5:** Cancel button closes modal without sending
6. **AC6.4.6:** Send button is disabled until slots are added

## Tasks / Subtasks

- [ ] **Task 1: Create EmailModal component** (AC: 6.4.1-6.4.6)
  - [ ] Create `src/components/EmailModal.jsx`:
    ```jsx
    import { useState } from 'react';
    import { X, Send, Mail, Users, Loader2 } from 'lucide-react';
    import {
      Dialog,
      DialogContent,
      DialogHeader,
      DialogTitle,
      DialogFooter,
    } from '@/components/ui/dialog';
    import { Button } from '@/components/ui/button';
    import { Textarea } from '@/components/ui/textarea';
    import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
    import SlotPicker from '@/components/SlotPicker';
    import { sendEmails } from '@/services/api';
    import { useToast } from '@/components/ui/use-toast';

    const DEFAULT_TEMPLATE = `Dear {name},

We are pleased to invite you for an interview for the {job_title} position at {company}.

Please choose from the following available time slots:

{slots}

Please reply to this email with your preferred time slot.

Best regards,
HR Team`;

    function EmailModal({
      open,
      onClose,
      selectedCandidates,
      sessionId,
      jobTitle,
      company = 'Yoboho'
    }) {
      const [slots, setSlots] = useState([]);
      const [message, setMessage] = useState(DEFAULT_TEMPLATE);
      const [sending, setSending] = useState(false);
      const { toast } = useToast();

      const handleClose = () => {
        setSlots([]);
        setMessage(DEFAULT_TEMPLATE);
        onClose();
      };

      const handleSend = async () => {
        setSending(true);
        try {
          const response = await sendEmails({
            session_id: sessionId,
            candidate_emails: selectedCandidates.map(c => ({
              name: c.name,
              email: c.email
            })),
            interview_slots: slots.map(s => ({
              date: s.date,
              time: s.time
            })),
            message: message
          });

          if (response.success) {
            const { sent, failed } = response.data;
            toast({
              title: 'Emails sent',
              description: `${sent} email${sent !== 1 ? 's' : ''} sent successfully${
                failed > 0 ? `, ${failed} failed` : ''
              }`
            });
            handleClose();
          }
        } catch (error) {
          toast({
            variant: 'destructive',
            title: 'Failed to send emails',
            description: error.message || 'Please try again'
          });
        } finally {
          setSending(false);
        }
      };

      const canSend = slots.length > 0 && selectedCandidates.length > 0;

      return (
        <Dialog open={open} onOpenChange={handleClose}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                Send Interview Invitations
              </DialogTitle>
            </DialogHeader>

            <div className="space-y-6 py-4">
              {/* Recipients */}
              <RecipientsSection candidates={selectedCandidates} />

              {/* Slots */}
              <SlotPicker slots={slots} onSlotsChange={setSlots} />

              {/* Message with preview tabs */}
              <MessageSection
                message={message}
                onMessageChange={setMessage}
                slots={slots}
                jobTitle={jobTitle}
                company={company}
                sampleName={selectedCandidates[0]?.name || 'Candidate'}
              />
            </div>

            <DialogFooter className="gap-2">
              <Button variant="outline" onClick={handleClose} disabled={sending}>
                Cancel
              </Button>
              <Button onClick={handleSend} disabled={!canSend || sending}>
                {sending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Send {selectedCandidates.length} Email{selectedCandidates.length !== 1 ? 's' : ''}
                  </>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      );
    }

    export default EmailModal;
    ```

- [ ] **Task 2: Create RecipientsSection component** (AC: 6.4.1)
  - [ ] Show selected candidates:
    ```jsx
    function RecipientsSection({ candidates }) {
      return (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <h4 className="text-sm font-medium">
              Recipients ({candidates.length})
            </h4>
          </div>

          <div className="flex flex-wrap gap-2">
            {candidates.map((candidate) => (
              <div
                key={candidate.id}
                className="flex items-center gap-2 px-3 py-1.5 bg-muted rounded-full text-sm"
              >
                <span className="font-medium">{candidate.name}</span>
                <span className="text-muted-foreground text-xs">
                  {candidate.email}
                </span>
              </div>
            ))}
          </div>
        </div>
      );
    }
    ```

- [ ] **Task 3: Create MessageSection with tabs** (AC: 6.4.3, 6.4.4)
  - [ ] Edit and preview tabs:
    ```jsx
    function MessageSection({
      message,
      onMessageChange,
      slots,
      jobTitle,
      company,
      sampleName
    }) {
      const formatSlotsForPreview = () => {
        if (slots.length === 0) return '[No slots added yet]';
        return slots.map(s => `  - ${s.date} at ${s.time}`).join('\n');
      };

      const previewMessage = message
        .replace('{name}', sampleName)
        .replace('{job_title}', jobTitle || '[Job Title]')
        .replace('{company}', company)
        .replace('{slots}', formatSlotsForPreview());

      return (
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Email Message</h4>

          <Tabs defaultValue="edit" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="edit">Edit</TabsTrigger>
              <TabsTrigger value="preview">Preview</TabsTrigger>
            </TabsList>

            <TabsContent value="edit" className="mt-2">
              <Textarea
                value={message}
                onChange={(e) => onMessageChange(e.target.value)}
                rows={12}
                className="font-mono text-sm"
                placeholder="Enter your message..."
              />
              <p className="text-xs text-muted-foreground mt-2">
                Placeholders: {'{name}'}, {'{job_title}'}, {'{company}'}, {'{slots}'}
              </p>
            </TabsContent>

            <TabsContent value="preview" className="mt-2">
              <div className="p-4 bg-muted/30 rounded-lg border">
                <div className="text-sm font-medium mb-2 text-muted-foreground">
                  Subject: Interview Invitation - {jobTitle} at {company}
                </div>
                <pre className="text-sm whitespace-pre-wrap font-sans">
                  {previewMessage}
                </pre>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Previewing as: {sampleName}
              </p>
            </TabsContent>
          </Tabs>
        </div>
      );
    }
    ```

- [ ] **Task 4: Add validation indicators** (AC: 6.4.6)
  - [ ] Show what's missing:
    ```jsx
    {slots.length === 0 && (
      <div className="flex items-center gap-2 text-sm text-yellow-500 bg-yellow-500/10 p-2 rounded">
        <AlertCircle className="h-4 w-4" />
        Add at least one interview slot to send emails
      </div>
    )}
    ```

- [ ] **Task 5: Add keyboard shortcuts**
  - [ ] ESC to close, Enter to send (with confirmation):
    ```jsx
    useEffect(() => {
      const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
          handleClose();
        }
      };

      if (open) {
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
      }
    }, [open]);
    ```

- [ ] **Task 6: Test email modal**
  - [ ] Modal opens with selected recipients
  - [ ] Recipients shown with names and emails
  - [ ] Slot picker works (add/remove)
  - [ ] Message is editable
  - [ ] Preview tab shows formatted message
  - [ ] Send disabled without slots
  - [ ] Cancel closes modal
  - [ ] Send shows loading state

## Dev Notes

### Architecture Alignment

This story creates the email confirmation modal:
- **Component:** EmailModal with subcomponents
- **State:** Local state for slots, message, sending
- **API:** Calls POST /api/send-emails

### Modal Structure

```
┌─────────────────────────────────────────────────────────────┐
│ [Mail icon] Send Interview Invitations                   [X] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ [Users] Recipients (3)                                       │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │
│ │ Sara Ahmed  │ │ Ali Khan    │ │ Rahul Sharma│             │
│ │ sara@...    │ │ ali@...     │ │ rahul@...   │             │
│ └─────────────┘ └─────────────┘ └─────────────┘             │
│                                                              │
│ Interview Slots                            2 slots added     │
│ ┌─────────────────────────────────────────────────────┐     │
│ │ [Cal] Dec 6, 2025  [Clock] 10:00 AM            [×] │     │
│ │ [Cal] Dec 6, 2025  [Clock] 2:00 PM             [×] │     │
│ └─────────────────────────────────────────────────────┘     │
│ [Date input] [Time input] [+]                                │
│                                                              │
│ Email Message                                                │
│ ┌────────────────────────────────────────────────────┐      │
│ │ [Edit] [Preview]                                    │      │
│ ├────────────────────────────────────────────────────┤      │
│ │ Dear {name},                                        │      │
│ │                                                     │      │
│ │ We are pleased to invite you...                     │      │
│ │                                                     │      │
│ └────────────────────────────────────────────────────┘      │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                              [Cancel]  [Send 3 Emails]       │
└─────────────────────────────────────────────────────────────┘
```

### Template Placeholders

| Placeholder | Replaced With |
|-------------|---------------|
| {name} | Candidate's name |
| {job_title} | Role title from session |
| {company} | "Yoboho" (configurable) |
| {slots} | Formatted slot list |

### Button States

| State | Send Button |
|-------|-------------|
| No slots | Disabled |
| Has slots | Enabled |
| Sending | Loading spinner |
| Success | Modal closes |
| Error | Shows toast |

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-6.md#Email-Modal]
- [Source: docs/epics.md#Story-6.4]
- [Source: docs/prd.md#FR61-FR64]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/6-4-email-confirmation-modal.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Recipients section shows both name AND email in rounded-full chips
- Edit/Preview tabs working with Radix Tabs component
- Preview shows subject line, personalized message, and "Previewing as" indicator
- Validation warning appears when no slots added (yellow background with AlertCircle icon)
- Send button disabled until slots added
- Cancel button closes modal and clears selection
- Loading spinner (Loader2) displays during send
- Toast notifications integrated for success/failure

### Completion Notes List

- All 6 tasks completed successfully
- All 6 acceptance criteria satisfied:
  - AC6.4.1: Recipients show names and emails in pill format
  - AC6.4.2: Interview slots displayed via SlotPicker with nice formatting
  - AC6.4.3: Editable message template with placeholders ({name}, {job_title}, {company}, {slots})
  - AC6.4.4: Preview tab shows email with placeholders replaced, subject line, and sample recipient
  - AC6.4.5: Cancel button closes modal without sending
  - AC6.4.6: Send button disabled until slots added, validation warning shown
- Added Tabs component via shadcn
- Integrated sendEmails API function
- Added useToast hook for notifications
- MessageSection component with Edit/Preview tabs
- ValidationWarning component for slot requirement

### File List

**Created:**
- frontend/src/components/ui/tabs.jsx (via shadcn)

**Modified:**
- frontend/src/components/EmailModal.jsx (major enhancement - tabs, validation, API integration)
- frontend/src/services/api.js (added sendEmails function)
- frontend/src/pages/DashboardPage.jsx (added sessionId prop to EmailModal)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
