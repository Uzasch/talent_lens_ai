import { useState } from 'react';
import { ChevronDown, Scale, Lightbulb } from 'lucide-react';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

function WhySection({ candidate }) {
  const [isOpen, setIsOpen] = useState(false);

  const {
    rank,
    why_selected,
    compared_to_pool,
    tie_breaker_applied,
    tie_breaker_reason
  } = candidate;

  // Handle empty state - if no explanation data available
  if (!why_selected && !compared_to_pool && !tie_breaker_reason) {
    return null;
  }

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen} className="mt-3">
      <CollapsibleTrigger className="flex items-center gap-2 w-full text-left py-2 px-3 rounded-md hover:bg-muted/50 transition-colors">
        <Lightbulb className="h-4 w-4 text-primary" />
        <span className="text-sm font-medium flex-1">
          WHY #{rank}?
        </span>
        <ChevronDown
          className={`h-4 w-4 text-muted-foreground transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </CollapsibleTrigger>

      <CollapsibleContent className="overflow-hidden data-[state=open]:animate-slideDown data-[state=closed]:animate-slideUp">
        <div className="pt-2 pb-3 px-3 space-y-3">
          {/* Why Selected */}
          {why_selected && (
            <div>
              <h4 className="text-xs font-medium text-muted-foreground mb-1">
                Why Selected
              </h4>
              <p className="text-sm">{why_selected}</p>
            </div>
          )}

          {/* Compared to Pool */}
          {compared_to_pool && (
            <div>
              <h4 className="text-xs font-medium text-muted-foreground mb-1">
                Pool Comparison
              </h4>
              <p className="text-sm text-muted-foreground">
                {compared_to_pool}
              </p>
            </div>
          )}

          {/* Tie-Breaker Section */}
          {tie_breaker_applied && tie_breaker_reason && (
            <div className="p-3 rounded-md bg-orange-500/10 border border-orange-500/30">
              <div className="flex items-center gap-2 mb-2">
                <Scale className="h-4 w-4 text-orange-500" />
                <h4 className="text-xs font-medium text-orange-500">
                  Tie-Breaker Applied
                </h4>
              </div>
              <p className="text-sm">{tie_breaker_reason}</p>
            </div>
          )}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}

export default WhySection;
