import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Info, ChevronDown } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

const PRIORITY_CONFIG = {
  CRITICAL: {
    label: 'CRITICAL',
    className: 'bg-red-500/20 text-red-500 border-red-500/50',
    symbol: '!'
  },
  IMPORTANT: {
    label: 'IMPORTANT',
    className: 'bg-orange-500/20 text-orange-500 border-orange-500/50',
    symbol: '•'
  },
  NICE_TO_HAVE: {
    label: 'NICE TO HAVE',
    className: 'bg-gray-500/20 text-gray-400 border-gray-500/50',
    symbol: ''
  },
  LOW_PRIORITY: {
    label: 'LOW',
    className: 'bg-gray-800/50 text-gray-500 border-gray-700',
    symbol: ''
  }
};

const DIMENSION_LABELS = {
  experience: 'Experience',
  skills: 'Skills',
  projects: 'Projects',
  positions: 'Positions',
  education: 'Education'
};

// Small badge for inline use (e.g., next to score bars)
function PriorityBadgeSmall({ priority }) {
  const config = PRIORITY_CONFIG[priority];
  if (!config || !config.symbol) return null;

  return (
    <span className={`text-xs px-1.5 py-0.5 rounded ${config.className}`}>
      {config.symbol}
    </span>
  );
}

function PriorityBadges({ priorities, reasoning }) {
  const [showReasoning, setShowReasoning] = useState(false);

  if (!priorities) return null;

  return (
    <div className="mb-6 p-4 bg-card rounded-lg border">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium">Job-Inferred Priorities</h3>
        {reasoning && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="h-4 w-4 text-muted-foreground hover:text-foreground cursor-help" />
              </TooltipTrigger>
              <TooltipContent className="max-w-sm">
                <p className="text-sm">{reasoning}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
      </div>

      <div className="flex flex-wrap gap-3">
        {Object.entries(priorities).map(([dimension, priority]) => {
          const config = PRIORITY_CONFIG[priority] || PRIORITY_CONFIG.NICE_TO_HAVE;
          return (
            <div key={dimension} className="flex items-center gap-1.5">
              <span className="text-sm text-muted-foreground">
                {DIMENSION_LABELS[dimension] || dimension}:
              </span>
              <Badge variant="outline" className={config.className}>
                {config.label}
              </Badge>
            </div>
          );
        })}
      </div>

      {/* Expandable reasoning for mobile */}
      {reasoning && (
        <>
          <button
            onClick={() => setShowReasoning(!showReasoning)}
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground mt-3 md:hidden"
          >
            <ChevronDown className={`h-3 w-3 transition-transform ${showReasoning ? 'rotate-180' : ''}`} />
            Why these priorities?
          </button>
          {showReasoning && (
            <p className="text-sm text-muted-foreground mt-2 pl-4 border-l-2 border-primary/30 md:hidden">
              {reasoning}
            </p>
          )}
        </>
      )}
    </div>
  );
}

export { PriorityBadgeSmall, PRIORITY_CONFIG, DIMENSION_LABELS };
export default PriorityBadges;
