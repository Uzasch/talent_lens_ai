# Epic 6: Email & Scheduling - Technical Specification

## Epic Overview

| Attribute | Value |
|-----------|-------|
| Epic ID | 6 |
| Title | Email & Scheduling |
| Goal | User can send interview invitations with schedule slots to selected candidates |
| User Value | Take action and schedule interviews directly from results! |
| FRs Covered | FR58-FR64 |
| Stories | 5 |
| Status | contexted |

---

## Architecture Context

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Email & Scheduling Flow                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Dashboard                                                       │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ [✓] Sara Ahmed    [✓] Ali Khan    [ ] Rahul Sharma  │       │
│  │                                                       │       │
│  │              [Email 2 Selected]                       │       │
│  └──────────────────────────────────────────────────────┘       │
│                          │                                       │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ Email Modal                                           │       │
│  │                                                       │       │
│  │ Recipients: Sara Ahmed, Ali Khan                      │       │
│  │                                                       │       │
│  │ Interview Slots:                                      │       │
│  │   • Dec 6, 2025 at 10:00 AM  [×]                     │       │
│  │   • Dec 6, 2025 at 2:00 PM   [×]                     │       │
│  │   [+ Add Slot]                                        │       │
│  │                                                       │       │
│  │ Message:                                              │       │
│  │ ┌─────────────────────────────────────────────┐      │       │
│  │ │ Dear {name},                                 │      │       │
│  │ │ We'd like to invite you for an interview... │      │       │
│  │ │ Available slots: {slots}                    │      │       │
│  │ └─────────────────────────────────────────────┘      │       │
│  │                                                       │       │
│  │              [Cancel]  [Send Emails]                  │       │
│  └──────────────────────────────────────────────────────┘       │
│                          │                                       │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ Backend: POST /api/send-emails                        │       │
│  │                                                       │       │
│  │ email_service.py                                      │       │
│  │   └── Gmail SMTP                                      │       │
│  │         ├── Personalize message ({name}, {job_title}) │       │
│  │         ├── Format slots as bullet list              │       │
│  │         └── Send to each recipient                   │       │
│  └──────────────────────────────────────────────────────┘       │
│                          │                                       │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ Response                                              │       │
│  │   { sent: 2, failed: 0, results: [...] }             │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User selects candidates on Dashboard
         │
         ▼
Clicks "Email X Selected" button
         │
         ▼
Email Modal opens with:
  - Selected recipients (name + email)
  - Empty slots list
  - Default message template
         │
         ▼
User adds interview time slots
  - Date picker + Time picker
  - Multiple slots allowed (3-5 recommended)
         │
         ▼
User customizes message (optional)
  - Placeholders: {name}, {job_title}, {company}, {slots}
         │
         ▼
User clicks "Send Emails"
         │
         ▼
POST /api/send-emails
  {
    session_id,
    candidate_emails: [...],
    interview_slots: [...],
    message: "..."
  }
         │
         ▼
Backend processes:
  1. For each candidate:
     a. Replace {name} with candidate name
     b. Replace {job_title} with role title
     c. Replace {slots} with formatted slot list
     d. Send via Gmail SMTP
  2. Collect results (success/failure per email)
         │
         ▼
Response to frontend with status
         │
         ▼
Toast notification: "2 emails sent successfully"
```

---

## Stories Summary

| Story | Title | Focus | FRs |
|-------|-------|-------|-----|
| 6.1 | Email Service Setup | Gmail SMTP backend service | FR62 |
| 6.2 | Email Selection UI | Checkbox selection on cards | FR58 |
| 6.3 | Interview Slot Management | Date/time picker for slots | FR59, FR60 |
| 6.4 | Email Confirmation Modal | Preview and customize message | FR61, FR64 |
| 6.5 | Send Emails API with Slots | API endpoint and delivery | FR63 |

---

## Technical Components

### Backend: email_service.py

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.gmail_address = os.getenv('GMAIL_ADDRESS')
        self.gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587

    def format_slots(self, slots: list) -> str:
        """Format interview slots as bullet list."""
        formatted = []
        for slot in slots:
            # slot: {"date": "2025-12-06", "time": "10:00 AM"}
            formatted.append(f"• {slot['date']} at {slot['time']}")
        return "\n".join(formatted)

    def personalize_message(
        self,
        template: str,
        name: str,
        job_title: str,
        company: str,
        slots: list
    ) -> str:
        """Replace placeholders in message template."""
        formatted_slots = self.format_slots(slots)
        return template.replace('{name}', name) \
                      .replace('{job_title}', job_title) \
                      .replace('{company}', company) \
                      .replace('{slots}', formatted_slots)

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> dict:
        """Send a single email via Gmail SMTP."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.gmail_address
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.gmail_address, self.gmail_password)
                server.send_message(msg)

            logger.info(f'Email sent to {to_email}')
            return {'email': to_email, 'sent': True}

        except Exception as e:
            logger.error(f'Failed to send email to {to_email}: {e}')
            return {'email': to_email, 'sent': False, 'error': str(e)}

    def send_bulk(
        self,
        recipients: list,
        job_title: str,
        company: str,
        slots: list,
        message_template: str
    ) -> dict:
        """Send emails to multiple recipients."""
        results = []
        sent_count = 0
        failed_count = 0

        subject = f"Interview Invitation - {job_title} at {company}"

        for recipient in recipients:
            personalized = self.personalize_message(
                message_template,
                recipient['name'],
                job_title,
                company,
                slots
            )

            result = self.send_email(
                recipient['email'],
                subject,
                personalized
            )
            results.append(result)

            if result['sent']:
                sent_count += 1
            else:
                failed_count += 1

        return {
            'sent': sent_count,
            'failed': failed_count,
            'results': results
        }
```

### Frontend: EmailModal Component

```jsx
// src/components/EmailModal.jsx
import { useState } from 'react';
import { X, Calendar, Clock, Plus, Send, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { sendEmails } from '@/services/api';

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
  const [newDate, setNewDate] = useState('');
  const [newTime, setNewTime] = useState('');
  const [message, setMessage] = useState(DEFAULT_TEMPLATE);
  const [sending, setSending] = useState(false);

  const addSlot = () => {
    if (newDate && newTime) {
      setSlots([...slots, { date: newDate, time: newTime }]);
      setNewDate('');
      setNewTime('');
    }
  };

  const removeSlot = (index) => {
    setSlots(slots.filter((_, i) => i !== index));
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
        interview_slots: slots,
        message: message
      });

      if (response.success) {
        // Show success toast
        onClose();
      }
    } catch (error) {
      // Show error toast
    } finally {
      setSending(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Modal content */}
      </DialogContent>
    </Dialog>
  );
}
```

### API Endpoint

```python
@app.route('/api/send-emails', methods=['POST'])
def send_emails():
    try:
        data = request.get_json()

        session_id = data.get('session_id')
        recipients = data.get('candidate_emails', [])
        slots = data.get('interview_slots', [])
        message = data.get('message', '')

        if not recipients:
            return error_response('VALIDATION_ERROR', 'No recipients specified', 400)

        if not slots:
            return error_response('VALIDATION_ERROR', 'No interview slots specified', 400)

        # Get session for job title
        session = get_session_by_id(session_id)
        role = get_role_by_id(session['role_id'])
        job_title = role['title']

        # Send emails
        email_service = EmailService()
        result = email_service.send_bulk(
            recipients=recipients,
            job_title=job_title,
            company='Yoboho',
            slots=slots,
            message_template=message
        )

        return success_response(result)

    except Exception as e:
        logger.error(f'Email send error: {e}')
        return error_response('EMAIL_ERROR', str(e), 500)
```

---

## API Contract

### POST /api/send-emails

**Request:**
```json
{
  "session_id": "uuid-string",
  "candidate_emails": [
    {"name": "Sara Ahmed", "email": "sara@email.com"},
    {"name": "Ali Khan", "email": "ali@email.com"}
  ],
  "interview_slots": [
    {"date": "Dec 6, 2025", "time": "10:00 AM"},
    {"date": "Dec 6, 2025", "time": "2:00 PM"},
    {"date": "Dec 7, 2025", "time": "11:00 AM"}
  ],
  "message": "Dear {name},\n\nWe would like to invite you..."
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "sent": 2,
    "failed": 0,
    "results": [
      {"email": "sara@email.com", "sent": true},
      {"email": "ali@email.com", "sent": true}
    ]
  }
}
```

**Response (Partial Failure):**
```json
{
  "success": true,
  "data": {
    "sent": 1,
    "failed": 1,
    "results": [
      {"email": "sara@email.com", "sent": true},
      {"email": "invalid@", "sent": false, "error": "Invalid email address"}
    ]
  }
}
```

---

## UI Components

### Email Selection State

```jsx
// In DashboardPage.jsx
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

// In render
<EmailSelectedButton
  count={selectedForEmail.length}
  onClick={() => setShowEmailModal(true)}
  disabled={selectedForEmail.length === 0}
/>
```

### Interview Slot Picker

```jsx
function SlotPicker({ slots, onAdd, onRemove }) {
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');

  const handleAdd = () => {
    if (date && time) {
      const formattedDate = new Date(date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
      onAdd({ date: formattedDate, time });
      setDate('');
      setTime('');
    }
  };

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium">Interview Slots</h4>

      {/* Existing slots */}
      {slots.map((slot, i) => (
        <div key={i} className="flex items-center gap-2 text-sm">
          <Calendar className="h-4 w-4 text-muted-foreground" />
          <span>{slot.date} at {slot.time}</span>
          <button onClick={() => onRemove(i)} className="text-destructive">
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}

      {/* Add new slot */}
      <div className="flex gap-2">
        <Input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          min={new Date().toISOString().split('T')[0]}
        />
        <Input
          type="time"
          value={time}
          onChange={(e) => setTime(e.target.value)}
        />
        <Button variant="outline" size="sm" onClick={handleAdd}>
          <Plus className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
```

---

## Message Template System

### Placeholders

| Placeholder | Replaced With | Source |
|-------------|---------------|--------|
| `{name}` | Candidate's name | candidate.name |
| `{job_title}` | Role title | role.title |
| `{company}` | Company name | Config (default: "Yoboho") |
| `{slots}` | Formatted slot list | interview_slots array |

### Default Template

```
Dear {name},

We are pleased to invite you for an interview for the {job_title} position at {company}.

Please choose from the following available time slots:

{slots}

Please reply to this email with your preferred time slot.

Best regards,
HR Team
```

### Rendered Example

```
Dear Sara Ahmed,

We are pleased to invite you for an interview for the Python Developer position at Yoboho.

Please choose from the following available time slots:

• Dec 6, 2025 at 10:00 AM
• Dec 6, 2025 at 2:00 PM
• Dec 7, 2025 at 11:00 AM

Please reply to this email with your preferred time slot.

Best regards,
HR Team
```

---

## Gmail SMTP Setup

### Prerequisites

1. **Gmail Account** - Regular Gmail account
2. **App Password** - Generate at https://myaccount.google.com/apppasswords
3. **2FA Enabled** - Required for app passwords

### Environment Variables

```env
GMAIL_ADDRESS=yourname@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

### SMTP Configuration

| Setting | Value |
|---------|-------|
| Server | smtp.gmail.com |
| Port | 587 |
| Encryption | TLS (STARTTLS) |
| Authentication | Email + App Password |

---

## Error Handling

### Frontend Errors

| Error | Display |
|-------|---------|
| No recipients | Disable send button |
| No slots | Disable send button |
| Network error | Toast: "Failed to send emails. Please try again." |
| Partial failure | Toast: "2 of 3 emails sent. 1 failed." |

### Backend Errors

| Error | Response |
|-------|----------|
| Invalid session | 404: "Session not found" |
| No recipients | 400: "No recipients specified" |
| No slots | 400: "No interview slots specified" |
| SMTP auth failure | 500: "Email service configuration error" |
| Individual send failure | Continue with others, log error |

---

## Testing Checklist

- [ ] Select candidates via checkboxes
- [ ] Button shows correct count
- [ ] Modal opens with selected recipients
- [ ] Add multiple interview slots
- [ ] Remove slots
- [ ] Customize message
- [ ] Preview shows placeholders replaced
- [ ] Send succeeds for valid emails
- [ ] Send handles invalid emails gracefully
- [ ] Success toast shows count
- [ ] Modal closes on success

---

## Dependencies

### Frontend
- shadcn/ui Dialog, Button, Input, Textarea
- lucide-react icons (Calendar, Clock, Send, etc.)

### Backend
- smtplib (Python standard library)
- email.mime (Python standard library)

### External Services
- Gmail SMTP

---

## References

- [Source: docs/architecture.md#POST-api-send-emails]
- [Source: docs/prd.md#FR58-FR64]
- [Source: docs/epics.md#Epic-6]

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial tech spec created |
