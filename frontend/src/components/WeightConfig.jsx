import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { Slider } from '@/components/ui/slider';

const DIMENSIONS = [
  { key: 'experience', label: 'Experience' },
  { key: 'projects', label: 'Projects' },
  { key: 'positions', label: 'Positions' },
  { key: 'skills', label: 'Skills' },
  { key: 'education', label: 'Education' },
];

function WeightConfig({ weights, onChange }) {
  const [isOpen, setIsOpen] = useState(false);

  const handleWeightChange = (changedKey, newValue) => {
    const otherKeys = DIMENSIONS.map((d) => d.key).filter((k) => k !== changedKey);

    const remaining = 100 - newValue;
    const currentOthersTotal = otherKeys.reduce((sum, k) => sum + weights[k], 0);

    const newWeights = { ...weights, [changedKey]: newValue };

    // Redistribute remaining among others proportionally
    if (currentOthersTotal > 0) {
      otherKeys.forEach((k) => {
        newWeights[k] = Math.round((weights[k] / currentOthersTotal) * remaining);
      });
    } else {
      // Equal distribution if others are zero
      const perOther = Math.round(remaining / otherKeys.length);
      otherKeys.forEach((k) => {
        newWeights[k] = perOther;
      });
    }

    // Adjust for rounding to ensure total is exactly 100
    const total = Object.values(newWeights).reduce((a, b) => a + b, 0);
    if (total !== 100) {
      const diff = 100 - total;
      const adjustKey = otherKeys[0];
      newWeights[adjustKey] += diff;
    }

    onChange(newWeights);
  };

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <CollapsibleTrigger className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
        <ChevronDown
          className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
        Customize Weights
      </CollapsibleTrigger>
      <CollapsibleContent className="mt-4 space-y-4">
        {DIMENSIONS.map((dim) => (
          <div key={dim.key} className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>{dim.label}</span>
              <span className="text-muted-foreground">{weights[dim.key]}%</span>
            </div>
            <Slider
              value={[weights[dim.key]]}
              onValueChange={(value) => handleWeightChange(dim.key, value[0])}
              max={100}
              step={5}
            />
          </div>
        ))}
        <p className="text-xs text-muted-foreground">
          Total: {Object.values(weights).reduce((a, b) => a + b, 0)}%
        </p>
      </CollapsibleContent>
    </Collapsible>
  );
}

export default WeightConfig;
