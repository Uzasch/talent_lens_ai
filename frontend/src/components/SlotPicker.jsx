import { useState } from 'react';
import { Calendar, Clock, Plus, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

/**
 * SlotPicker component for managing interview time slots.
 * Allows adding/removing slots with date/time pickers.
 */
function SlotPicker({ slots, onSlotsChange }) {
  const [newDate, setNewDate] = useState('');
  const [newTime, setNewTime] = useState('');
  const [error, setError] = useState('');

  // Get tomorrow's date as minimum (slots must be in the future)
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const minDate = tomorrow.toISOString().split('T')[0];

  const addSlot = () => {
    if (!newDate || !newTime) return;

    // Clear previous error
    setError('');

    // Validate future date/time
    const slotDateTime = new Date(`${newDate}T${newTime}`);
    const now = new Date();

    if (slotDateTime <= now) {
      setError('Interview slot must be in the future');
      return;
    }

    // Create sortKey for sorting and duplicate detection
    const sortKey = `${newDate}T${newTime}`;

    // Check for duplicate
    if (slots.some(s => s.sortKey === sortKey)) {
      setError('This time slot has already been added');
      return;
    }

    // Format date for display (e.g., "Dec 6, 2025")
    const formattedDate = new Date(newDate).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });

    // Convert 24h to 12h format (e.g., "14:30" -> "2:30 PM")
    const [hours, minutes] = newTime.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    const formattedTime = `${hour12}:${minutes} ${ampm}`;

    const newSlot = {
      date: formattedDate,
      time: formattedTime,
      sortKey: sortKey
    };

    // Add and sort by date/time
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

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Interview Slots</h4>
        <span className="text-xs text-muted-foreground">
          {slots.length} slot{slots.length !== 1 ? 's' : ''} added
        </span>
      </div>

      {/* Error message */}
      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}

      {/* Existing slots list */}
      {slots.length > 0 && (
        <div className="space-y-2">
          {slots.map((slot, index) => (
            <div
              key={slot.sortKey}
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
                className="p-1 hover:bg-destructive/10 rounded text-destructive transition-colors"
                aria-label={`Remove slot ${slot.date} at ${slot.time}`}
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Add new slot inputs */}
      <div className="flex items-end gap-2">
        <div className="flex-1">
          <label className="text-xs text-muted-foreground mb-1 block">
            Date
          </label>
          <Input
            type="date"
            value={newDate}
            onChange={(e) => {
              setNewDate(e.target.value);
              setError('');
            }}
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
            onChange={(e) => {
              setNewTime(e.target.value);
              setError('');
            }}
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

      {/* Hint when no slots */}
      {slots.length === 0 && (
        <p className="text-xs text-muted-foreground">
          Add 3-5 time slots for candidates to choose from
        </p>
      )}

      {/* Recommendation when few slots */}
      {slots.length > 0 && slots.length < 3 && (
        <p className="text-xs text-muted-foreground">
          Consider adding more slots to give candidates flexibility
        </p>
      )}
    </div>
  );
}

export default SlotPicker;
