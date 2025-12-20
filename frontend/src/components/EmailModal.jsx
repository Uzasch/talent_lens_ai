import { useState } from 'react';
import { Mail, Send, Users, Loader2, AlertCircle } from 'lucide-react';
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
import { useToast } from '@/hooks/use-toast';
import { sendEmails } from '@/services/api';

// Default email template
const DEFAULT_TEMPLATE = `Dear {name},

Congratulations! We are pleased to invite you to interview for the {job_title} position at {company}.

Based on your resume and qualifications, we believe you could be an excellent fit for our team.

Available Interview Slots:
{slots}

Please reply to this email with your preferred time slot, or let us know if none of these work for you.

We look forward to speaking with you!

Best regards,
The {company} Hiring Team`;

/**
 * Recipients section showing selected candidates with emails
 */
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

/**
 * Message section with Edit/Preview tabs
 */
function MessageSection({
  message,
  onMessageChange,
  slots,
  jobTitle,
  company,
  sampleName
}) {
  const formatSlotsForPreview = () => {
    if (slots.length === 0) return '  [No slots added yet]';
    return slots.map(s => `  - ${s.date} at ${s.time}`).join('\n');
  };

  const previewMessage = message
    .replace('{name}', sampleName || '[Candidate Name]')
    .replace('{job_title}', jobTitle || '[Job Title]')
    .replace(/\{company\}/g, company || 'Our Company')
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
            rows={10}
            className="font-mono text-sm"
            placeholder="Enter your email message..."
          />
          <p className="text-xs text-muted-foreground mt-2">
            Placeholders: {'{name}'}, {'{job_title}'}, {'{company}'}, {'{slots}'}
          </p>
        </TabsContent>

        <TabsContent value="preview" className="mt-2">
          <div className="p-4 bg-muted/30 rounded-lg border max-h-64 overflow-y-auto">
            <div className="text-sm font-medium mb-2 text-muted-foreground">
              Subject: Interview Invitation - {jobTitle || '[Job Title]'} at {company || 'Our Company'}
            </div>
            <pre className="text-sm whitespace-pre-wrap font-sans">
              {previewMessage}
            </pre>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Previewing as: {sampleName || '[Candidate Name]'}
          </p>
        </TabsContent>
      </Tabs>
    </div>
  );
}

/**
 * Validation warning when no slots added
 */
function ValidationWarning({ show }) {
  if (!show) return null;

  return (
    <div className="flex items-center gap-2 text-sm text-yellow-600 bg-yellow-500/10 p-3 rounded-lg">
      <AlertCircle className="h-4 w-4 flex-shrink-0" />
      <span>Add at least one interview slot to send emails</span>
    </div>
  );
}

/**
 * Email modal for sending interview invitations.
 * Includes recipients list, slot picker, message editor with tabs, and preview.
 */
function EmailModal({
  open,
  onClose,
  selectedCandidates,
  sessionId,
  jobTitle,
  company = 'Our Company'
}) {
  const [slots, setSlots] = useState([]);
  const [message, setMessage] = useState(DEFAULT_TEMPLATE);
  const [sending, setSending] = useState(false);
  const { toast } = useToast();

  const handleClose = () => {
    // Reset state on close
    setSlots([]);
    setMessage(DEFAULT_TEMPLATE);
    setSending(false);
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
        message_template: message,
        job_title: jobTitle,
        company: company
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
      } else {
        throw new Error(response.error?.message || 'Failed to send emails');
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

  const canSend = selectedCandidates?.length > 0 && slots.length > 0;

  if (!selectedCandidates || selectedCandidates.length === 0) {
    return null;
  }

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
          {/* Recipients - AC6.4.1 */}
          <RecipientsSection candidates={selectedCandidates} />

          {/* Interview Slots - AC6.4.2 */}
          <SlotPicker
            slots={slots}
            onSlotsChange={setSlots}
          />

          {/* Validation Warning - AC6.4.6 */}
          <ValidationWarning show={slots.length === 0} />

          {/* Message with Edit/Preview Tabs - AC6.4.3, AC6.4.4 */}
          <MessageSection
            message={message}
            onMessageChange={setMessage}
            slots={slots}
            jobTitle={jobTitle}
            company={company}
            sampleName={selectedCandidates[0]?.name}
          />
        </div>

        <DialogFooter className="gap-2 sm:gap-2">
          {/* Cancel Button - AC6.4.5 */}
          <Button variant="outline" onClick={handleClose} disabled={sending}>
            Cancel
          </Button>
          {/* Send Button - AC6.4.6 */}
          <Button
            onClick={handleSend}
            disabled={!canSend || sending}
          >
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
