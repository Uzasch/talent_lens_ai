import { UserMinus, CheckCircle } from 'lucide-react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';

const DIMENSION_LABELS = {
  experience: 'Experience',
  skills: 'Skills',
  projects: 'Projects',
  positions: 'Positions',
  education: 'Education'
};

function formatDimension(dim) {
  return DIMENSION_LABELS[dim] || dim;
}

function EliminatedSection({ eliminated }) {
  // Show success message if no eliminations
  if (!eliminated || eliminated.count === 0) {
    return (
      <div className="mt-8 p-4 rounded-lg bg-primary/5 border border-primary/30">
        <p className="text-sm text-primary flex items-center gap-2">
          <CheckCircle className="h-4 w-4" />
          All candidates passed threshold requirements
        </p>
      </div>
    );
  }

  const { count, breakdown, candidates } = eliminated;

  return (
    <div className="mt-8">
      <Accordion type="single" collapsible>
        <AccordionItem value="eliminated" className="border border-yellow-500/30 rounded-lg bg-yellow-500/5">
          <AccordionTrigger className="px-4 hover:no-underline">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-full bg-yellow-500/10">
                <UserMinus className="h-4 w-4 text-yellow-500" />
              </div>
              <div className="text-left">
                <h3 className="font-medium">
                  Eliminated by Thresholds
                </h3>
                <p className="text-sm text-muted-foreground">
                  {count} candidate{count !== 1 ? 's' : ''} didn&apos;t meet minimum requirements
                </p>
              </div>
            </div>
          </AccordionTrigger>

          <AccordionContent className="px-4 pb-4">
            {/* Breakdown by reason */}
            {breakdown && Object.keys(breakdown).length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium mb-2">
                  Elimination Breakdown
                </h4>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(breakdown).map(([dimension, dimCount]) => (
                    <div
                      key={dimension}
                      className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted text-sm"
                    >
                      <span className="font-medium text-yellow-500">{dimCount}</span>
                      <span className="text-muted-foreground">
                        {formatDimension(dimension)} below threshold
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Candidate list */}
            {candidates && candidates.length > 0 && (
              <div>
                <h4 className="text-sm font-medium mb-2">
                  Eliminated Candidates
                </h4>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {candidates.map((candidate, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between py-2 px-3 rounded bg-muted/50"
                    >
                      <span className="text-sm">{candidate.name}</span>
                      <span className="text-xs text-muted-foreground">
                        {candidate.reason}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}

export default EliminatedSection;
