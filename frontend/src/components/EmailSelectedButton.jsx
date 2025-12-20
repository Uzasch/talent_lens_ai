import { Mail } from 'lucide-react';
import { Button } from '@/components/ui/button';

/**
 * Floating button for emailing selected candidates.
 * Shows count when candidates are selected, disabled when none selected.
 */
function EmailSelectedButton({ count, onClick, disabled }) {
  const isDisabled = disabled || count === 0;

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Button
        size="lg"
        onClick={onClick}
        disabled={isDisabled}
        className="shadow-lg"
      >
        <Mail className="h-5 w-5 mr-2" />
        {count === 0 ? 'Select candidates to email' : `Email ${count} Selected`}
      </Button>
    </div>
  );
}

export default EmailSelectedButton;
