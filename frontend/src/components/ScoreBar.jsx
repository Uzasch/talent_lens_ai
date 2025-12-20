import { Progress } from '@/components/ui/progress';

const DIMENSION_LABELS = {
  experience: 'Experience',
  skills: 'Skills',
  projects: 'Projects',
  positions: 'Positions',
  education: 'Education'
};

function getScoreColor(score) {
  if (score >= 90) return 'text-primary';
  if (score >= 70) return 'text-foreground';
  if (score >= 50) return 'text-muted-foreground';
  return 'text-red-500';
}

function ScoreBar({ dimension, score, priority }) {
  const isCritical = priority === 'CRITICAL';
  const isImportant = priority === 'IMPORTANT';

  return (
    <div className={`space-y-1 ${isCritical ? 'relative' : ''}`}>
      {/* Critical glow effect */}
      {isCritical && (
        <div className="absolute inset-0 bg-red-500/5 -m-1 rounded" />
      )}

      <div className="flex items-center justify-between relative">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground w-24">
            {DIMENSION_LABELS[dimension]}
          </span>

          {/* Priority Badge */}
          {isCritical && (
            <span className="text-xs px-1.5 py-0.5 rounded bg-red-500/20 text-red-500 border border-red-500/30">
              !
            </span>
          )}
          {isImportant && (
            <span className="text-xs px-1.5 py-0.5 rounded bg-orange-500/20 text-orange-500 border border-orange-500/30">
              •
            </span>
          )}
        </div>

        <span className={`text-sm font-medium w-12 text-right ${getScoreColor(score)}`}>
          {score}%
        </span>
      </div>

      <Progress
        value={score}
        className={`h-2 ${isCritical ? 'border border-red-500/30' : ''}`}
      />
    </div>
  );
}

function ScoreBreakdown({ scores, priorities }) {
  const dimensions = ['experience', 'skills', 'projects', 'positions', 'education'];

  if (!scores) return null;

  return (
    <div className="space-y-3 py-3">
      {dimensions.map((dim) => (
        <ScoreBar
          key={dim}
          dimension={dim}
          score={scores?.[dim] || 0}
          priority={priorities?.[dim]}
        />
      ))}
    </div>
  );
}

export { ScoreBreakdown, ScoreBar, getScoreColor };
export default ScoreBar;
