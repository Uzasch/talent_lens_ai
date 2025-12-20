import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Check } from 'lucide-react';
import { ScoreBreakdown } from '@/components/ScoreBar';
import WhySection from '@/components/WhySection';

function CandidateCard({
  candidate,
  priorities,
  isSelected,
  onSelect,
  onCompare,
  isCompareSelected
}) {
  const {
    id,
    rank,
    name,
    email,
    match_score,
    summary,
    scores,
    tie_breaker_applied
  } = candidate;

  const isTopCandidate = rank === 1;
  const hasValidEmail = email && email.includes('@');

  return (
    <Card className={`relative transition-all hover:border-primary/50 ${
      isTopCandidate ? 'border-primary shadow-lg shadow-primary/10' : ''
    } ${isCompareSelected ? 'ring-2 ring-primary ring-offset-2 ring-offset-background' : ''
    } ${isSelected ? 'ring-2 ring-green-500 bg-green-500/5' : ''}`}>
      {/* Rank Badge */}
      <div className={`absolute -top-3 -left-3 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
        isTopCandidate
          ? 'bg-primary text-primary-foreground'
          : 'bg-card border text-foreground'
      }`}>
        #{rank}
      </div>

      {/* Tie-breaker Icon */}
      {tie_breaker_applied && (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="absolute -top-2 -right-2 cursor-help">
                <span className="text-lg">&#x2696;&#xfe0f;</span>
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p className="text-sm">Tie-breaker applied</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )}

      <CardHeader className="pt-6 pb-2">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-lg">{name}</h3>
            <p className="text-sm text-muted-foreground">{email}</p>
          </div>

          {/* Match Score */}
          <div className="text-right">
            <span className="text-3xl font-bold text-primary">
              {match_score}%
            </span>
            <p className="text-xs text-muted-foreground">match</p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Summary Bullets */}
        <ul className="space-y-1">
          {summary?.map((bullet, i) => (
            <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
              <span className="text-primary mt-1">•</span>
              <span>{bullet}</span>
            </li>
          ))}
        </ul>

        {/* Score Breakdown - Story 5.4 */}
        <ScoreBreakdown scores={scores} priorities={priorities} />

        {/* WHY Section - Story 5.5 */}
        <WhySection candidate={candidate} />

        {/* Actions */}
        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex items-center gap-2">
            <Checkbox
              id={`select-${id}`}
              checked={isSelected}
              onCheckedChange={() => onSelect(candidate)}
              disabled={!hasValidEmail}
              aria-label={`Select ${name} for email`}
            />
            <label
              htmlFor={`select-${id}`}
              className={`text-sm cursor-pointer ${
                hasValidEmail ? 'text-muted-foreground' : 'text-muted-foreground/50'
              }`}
            >
              {hasValidEmail ? 'Select for email' : 'No email'}
            </label>
          </div>

          <button
            onClick={() => onCompare(candidate)}
            className={`text-sm transition-colors ${
              isCompareSelected
                ? 'bg-primary text-primary-foreground px-3 py-1 rounded flex items-center gap-1'
                : 'text-primary hover:underline'
            }`}
          >
            {isCompareSelected ? (
              <>
                <Check className="h-3 w-3" />
                Selected
              </>
            ) : (
              'Compare'
            )}
          </button>
        </div>
      </CardContent>
    </Card>
  );
}

function CandidateCardGrid({
  candidates,
  priorities,
  selectedForEmail = [],
  onEmailSelect,
  onCompare,
  compareSelection = []
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {candidates.map((candidate) => (
        <CandidateCard
          key={candidate.id}
          candidate={candidate}
          priorities={priorities}
          isSelected={selectedForEmail.some(c => c.id === candidate.id)}
          onSelect={onEmailSelect}
          onCompare={onCompare}
          isCompareSelected={compareSelection.some(c => c.id === candidate.id)}
        />
      ))}
    </div>
  );
}

export { CandidateCardGrid };
export default CandidateCard;
