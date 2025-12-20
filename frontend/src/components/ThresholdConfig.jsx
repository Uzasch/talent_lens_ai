import { useState } from 'react';
import { ChevronDown, AlertTriangle } from 'lucide-react';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';

const DIMENSIONS = [
  { key: 'experience', label: 'Experience', description: 'Minimum experience score' },
  { key: 'skills', label: 'Skills', description: 'Minimum skills match' },
  { key: 'projects', label: 'Projects', description: 'Minimum project quality' },
  { key: 'positions', label: 'Positions', description: 'Minimum career progression' },
  { key: 'education', label: 'Education', description: 'Minimum education level' },
];

const DEFAULT_THRESHOLDS = {
  experience: { enabled: false, minimum: 50 },
  skills: { enabled: false, minimum: 50 },
  projects: { enabled: false, minimum: 50 },
  positions: { enabled: false, minimum: 50 },
  education: { enabled: false, minimum: 50 },
};

function ThresholdConfig({ thresholds, onChange }) {
  const [isOpen, setIsOpen] = useState(false);

  const handleToggle = (key, enabled) => {
    onChange({
      ...thresholds,
      [key]: { ...thresholds[key], enabled },
    });
  };

  const handleMinimumChange = (key, value) => {
    onChange({
      ...thresholds,
      [key]: { ...thresholds[key], minimum: value[0] },
    });
  };

  const enabledCount = Object.values(thresholds).filter((t) => t.enabled).length;

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <CollapsibleTrigger className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
        <ChevronDown
          className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
        <AlertTriangle className="h-4 w-4" />
        Advanced Settings: Minimum Thresholds
        {enabledCount > 0 && (
          <span className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded">
            {enabledCount} active
          </span>
        )}
      </CollapsibleTrigger>

      <CollapsibleContent className="mt-4 space-y-4 p-4 bg-card rounded-lg border">
        <p className="text-xs text-muted-foreground">
          Candidates scoring below these minimums will be eliminated before ranking.
        </p>

        {DIMENSIONS.map((dim) => (
          <div key={dim.key} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Switch
                  checked={thresholds[dim.key].enabled}
                  onCheckedChange={(checked) => handleToggle(dim.key, checked)}
                />
                <div>
                  <span className="text-sm font-medium">{dim.label}</span>
                  <p className="text-xs text-muted-foreground">{dim.description}</p>
                </div>
              </div>
              {thresholds[dim.key].enabled && (
                <span className="text-sm font-mono">
                  &ge; {thresholds[dim.key].minimum}%
                </span>
              )}
            </div>

            {thresholds[dim.key].enabled && (
              <>
                <Slider
                  value={[thresholds[dim.key].minimum]}
                  onValueChange={(value) => handleMinimumChange(dim.key, value)}
                  min={0}
                  max={100}
                  step={5}
                  className="ml-12"
                />
                {thresholds[dim.key].minimum > 80 && (
                  <p className="text-xs text-yellow-500 ml-12">
                    High threshold may eliminate most candidates
                  </p>
                )}
              </>
            )}
          </div>
        ))}

        <div className="pt-2 border-t text-xs text-muted-foreground">
          Note: Thresholds are applied before weighted scoring. Use sparingly.
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}

export { ThresholdConfig, DEFAULT_THRESHOLDS };
export default ThresholdConfig;
