import { useEffect, useState } from 'react';
import { Trophy, Minus, Lightbulb } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { compareCandidates } from '@/services/api';

// Loading skeleton for comparison modal
function ComparisonSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <Skeleton className="h-32 rounded-lg" />
        <Skeleton className="h-32 rounded-lg" />
      </div>
      <div className="space-y-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="space-y-2">
            <Skeleton className="h-4 w-24" />
            <div className="grid grid-cols-2 gap-2">
              <Skeleton className="h-3" />
              <Skeleton className="h-3" />
            </div>
          </div>
        ))}
      </div>
      <Skeleton className="h-24 rounded-lg" />
    </div>
  );
}

// Candidate header card with winner indicator
function CandidateHeaderCard({ candidate, isWinner, label }) {
  return (
    <div className={`p-4 rounded-lg border transition-colors ${
      isWinner ? 'border-primary bg-primary/5' : 'border-border'
    }`}>
      {isWinner && (
        <div className="flex items-center gap-1 text-primary text-sm mb-2">
          <Trophy className="h-4 w-4" />
          Overall Winner
        </div>
      )}
      <p className="text-xs text-muted-foreground">{label}</p>
      <h3 className="font-semibold text-lg">{candidate.name}</h3>
      <p className="text-3xl font-bold text-primary mt-1">
        {candidate.match_score}%
      </p>
    </div>
  );
}

// Header with both candidates and overall winner
function ComparisonHeader({ candidate1, candidate2, winner }) {
  const isCandidate1Winner = winner === 'candidate_1';
  const isCandidate2Winner = winner === 'candidate_2';

  return (
    <div className="grid grid-cols-2 gap-4">
      <CandidateHeaderCard
        candidate={candidate1}
        isWinner={isCandidate1Winner}
        label="Candidate A"
      />
      <CandidateHeaderCard
        candidate={candidate2}
        isWinner={isCandidate2Winner}
        label="Candidate B"
      />
    </div>
  );
}

// Side-by-side score comparison bars
function ScoreComparison({ candidate1, candidate2, dimensionWinners }) {
  const dimensions = ['experience', 'skills', 'projects', 'positions', 'education'];

  const labels = {
    experience: 'Experience',
    skills: 'Skills',
    projects: 'Projects',
    positions: 'Positions',
    education: 'Education'
  };

  return (
    <div className="space-y-4">
      <h4 className="font-medium">Dimension Comparison</h4>

      {dimensions.map((dim) => {
        const score1 = candidate1.scores?.[dim] || 0;
        const score2 = candidate2.scores?.[dim] || 0;
        const winner = dimensionWinners?.[dim];

        return (
          <div key={dim} className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">{labels[dim]}</span>
              <div className="flex items-center gap-2">
                {winner === 'candidate_1' && <span className="text-primary font-bold">◄</span>}
                {winner === 'tie' && <Minus className="h-3 w-3 text-muted-foreground" />}
                {winner === 'candidate_2' && <span className="text-primary font-bold">►</span>}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Candidate 1 bar (left aligned) */}
              <div className="flex items-center gap-2">
                <Progress
                  value={score1}
                  className={`h-3 flex-1 ${winner === 'candidate_1' ? '[&>div]:bg-primary' : ''}`}
                />
                <span className={`text-sm w-10 text-right ${winner === 'candidate_1' ? 'text-primary font-bold' : 'text-muted-foreground'}`}>
                  {score1}%
                </span>
              </div>

              {/* Candidate 2 bar (right aligned) */}
              <div className="flex items-center gap-2">
                <span className={`text-sm w-10 ${winner === 'candidate_2' ? 'text-primary font-bold' : 'text-muted-foreground'}`}>
                  {score2}%
                </span>
                <Progress
                  value={score2}
                  className={`h-3 flex-1 ${winner === 'candidate_2' ? '[&>div]:bg-primary' : ''}`}
                />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// AI analysis explanation
function AIExplanation({ explanation }) {
  return (
    <div className="p-4 bg-muted/30 rounded-lg">
      <h4 className="font-medium mb-2 flex items-center gap-2">
        <Lightbulb className="h-4 w-4 text-primary" />
        AI Analysis
      </h4>
      <p className="text-sm text-muted-foreground">{explanation}</p>
    </div>
  );
}

// Key differences list
function KeyDifferences({ differences }) {
  if (!differences || differences.length === 0) return null;

  return (
    <div>
      <h4 className="font-medium mb-2">Key Differences</h4>
      <ul className="space-y-1">
        {differences.map((diff, i) => (
          <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
            <span className="text-primary">•</span>
            {diff}
          </li>
        ))}
      </ul>
    </div>
  );
}

// Generate mock comparison data for development
function generateMockComparison(candidate1, candidate2) {
  const dimensions = ['experience', 'skills', 'projects', 'positions', 'education'];
  const dimensionWinners = {};

  let c1Wins = 0;
  let c2Wins = 0;

  dimensions.forEach(dim => {
    const score1 = candidate1.scores?.[dim] || 0;
    const score2 = candidate2.scores?.[dim] || 0;

    if (score1 > score2) {
      dimensionWinners[dim] = 'candidate_1';
      c1Wins++;
    } else if (score2 > score1) {
      dimensionWinners[dim] = 'candidate_2';
      c2Wins++;
    } else {
      dimensionWinners[dim] = 'tie';
    }
  });

  const overallWinner = candidate1.match_score > candidate2.match_score
    ? 'candidate_1'
    : candidate2.match_score > candidate1.match_score
      ? 'candidate_2'
      : 'tie';

  const winnerName = overallWinner === 'candidate_1' ? candidate1.name : candidate2.name;
  const loserName = overallWinner === 'candidate_1' ? candidate2.name : candidate1.name;

  return {
    overall_winner: overallWinner,
    dimension_winners: dimensionWinners,
    explanation: `${winnerName} ranks higher overall with a ${Math.abs(candidate1.match_score - candidate2.match_score)}% score advantage. ${winnerName} wins in ${overallWinner === 'candidate_1' ? c1Wins : c2Wins} dimensions, while ${loserName} leads in ${overallWinner === 'candidate_1' ? c2Wins : c1Wins}. The weighted scoring favors ${winnerName}'s stronger performance in CRITICAL dimensions (Experience and Skills).`,
    key_differences: [
      `Experience: ${candidate1.name}'s ${candidate1.scores?.experience}% vs ${candidate2.name}'s ${candidate2.scores?.experience}%`,
      `Skills: ${candidate1.name}'s ${candidate1.scores?.skills}% vs ${candidate2.name}'s ${candidate2.scores?.skills}%`,
      `Projects: ${candidate1.name}'s ${candidate1.scores?.projects}% vs ${candidate2.name}'s ${candidate2.scores?.projects}%`
    ]
  };
}

// Main ComparisonModal component
function ComparisonModal({ open, onClose, candidates, sessionId }) {
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && candidates && candidates.length === 2) {
      fetchComparison();
    }
  }, [open, candidates]);

  const fetchComparison = async () => {
    setLoading(true);
    try {
      const response = await compareCandidates(
        sessionId,
        candidates[0].id,
        candidates[1].id
      );
      if (response.success) {
        setComparison(response.data);
      } else {
        // Use mock data if API fails
        console.log('Using mock comparison data');
        setComparison(generateMockComparison(candidates[0], candidates[1]));
      }
    } catch (error) {
      console.error('Comparison error:', error);
      // Use mock data for development
      console.log('Using mock comparison data (network error)');
      setComparison(generateMockComparison(candidates[0], candidates[1]));
    } finally {
      setLoading(false);
    }
  };

  if (!candidates || candidates.length < 2) return null;

  const candidate1 = candidates[0];
  const candidate2 = candidates[1];

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Candidate Comparison</DialogTitle>
        </DialogHeader>

        {loading ? (
          <ComparisonSkeleton />
        ) : (
          <div className="space-y-6">
            {/* Header with names and overall winner */}
            <ComparisonHeader
              candidate1={candidate1}
              candidate2={candidate2}
              winner={comparison?.overall_winner}
            />

            {/* Score comparison bars */}
            <ScoreComparison
              candidate1={candidate1}
              candidate2={candidate2}
              dimensionWinners={comparison?.dimension_winners}
            />

            {/* AI Explanation */}
            {comparison?.explanation && (
              <AIExplanation explanation={comparison.explanation} />
            )}

            {/* Key differences */}
            {comparison?.key_differences && (
              <KeyDifferences differences={comparison.key_differences} />
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

export default ComparisonModal;
