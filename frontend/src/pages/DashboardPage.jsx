import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect, useCallback } from 'react';
import { Users, UserPlus, UserMinus, Award, AlertCircle, X, Calendar, Plus, History, Download } from 'lucide-react';
import StatCard from '@/components/StatCard';
import PriorityBadges from '@/components/PriorityBadges';
import { CandidateCardGrid } from '@/components/CandidateCard';
import EliminatedSection from '@/components/EliminatedSection';
import WhyNotOthers from '@/components/WhyNotOthers';
import ComparisonModal from '@/components/ComparisonModal';
import EmailSelectedButton from '@/components/EmailSelectedButton';
import EmailModal from '@/components/EmailModal';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { getSession } from '@/services/api';
import { formatDate } from '@/lib/utils';

// Export candidates to CSV
function exportToCSV(candidates, roleTitle) {
  if (!candidates || candidates.length === 0) return;

  const headers = ['Rank', 'Name', 'Email', 'Match Score', 'Experience', 'Skills', 'Projects', 'Positions', 'Education'];
  const rows = candidates.map(c => [
    c.rank,
    c.name,
    c.email || '',
    c.match_score,
    c.scores?.experience || 0,
    c.scores?.skills || 0,
    c.scores?.projects || 0,
    c.scores?.positions || 0,
    c.scores?.education || 0
  ]);

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${roleTitle.replace(/\s+/g, '_')}_candidates.csv`;
  link.click();
}

function DashboardSkeleton() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header skeleton */}
      <div className="mb-8">
        <Skeleton className="h-8 w-64 mb-2" />
        <Skeleton className="h-4 w-full max-w-xl" />
      </div>

      {/* Stats skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-24 rounded-lg" />
        ))}
      </div>

      {/* Cards skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Skeleton key={i} className="h-64 rounded-lg" />
        ))}
      </div>
    </div>
  );
}

function DashboardError({ error, isNotFound }) {
  const navigate = useNavigate();

  if (isNotFound) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-2xl font-bold mb-2">Session Not Found</h2>
        <p className="text-muted-foreground mb-6">
          This analysis session doesn&apos;t exist or has been deleted.
        </p>
        <div className="flex gap-4 justify-center">
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
          >
            Start New Analysis
          </button>
          <button
            onClick={() => navigate('/history')}
            className="px-4 py-2 border rounded-lg hover:bg-muted"
          >
            View History
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-16 text-center">
      <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
      <h2 className="text-xl font-semibold mb-2">Unable to load results</h2>
      <p className="text-muted-foreground mb-4">{error}</p>
      <button
        onClick={() => window.location.reload()}
        className="text-primary hover:underline"
      >
        Try again
      </button>
    </div>
  );
}

// Comparison indicator bar shown when selecting candidates to compare
function ComparisonIndicator({ selection, onClear }) {
  if (selection.length === 0) return null;

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 bg-card border rounded-lg shadow-lg p-4 flex items-center gap-4">
      <div className="text-sm">
        <span className="font-medium">{selection[0]?.name}</span>
        {selection.length === 1 && (
          <span className="text-muted-foreground ml-2">
            Select another candidate to compare
          </span>
        )}
        {selection.length === 2 && (
          <>
            <span className="text-muted-foreground mx-2">vs</span>
            <span className="font-medium">{selection[1]?.name}</span>
          </>
        )}
      </div>

      <button
        onClick={onClear}
        className="text-muted-foreground hover:text-foreground p-1 rounded hover:bg-muted transition-colors"
        title="Clear selection (Esc)"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

// Mock data for development/demo when backend is unavailable
const MOCK_DATA = {
  session: {
    role_title: 'Senior Python Developer',
    job_description: 'We are looking for an experienced Python developer with strong backend skills. The ideal candidate will have experience with Flask/Django, PostgreSQL, and cloud services like AWS or GCP. You will be working on our core platform team building scalable microservices...'
  },
  stats: {
    total_in_pool: 45,
    added_this_session: 10,
    eliminated_count: 13,
    ranked_count: 32
  },
  inferred_priorities: {
    experience: 'CRITICAL',
    skills: 'CRITICAL',
    projects: 'IMPORTANT',
    positions: 'NICE_TO_HAVE',
    education: 'LOW_PRIORITY'
  },
  priority_reasoning: 'The job description emphasizes "5+ years experience" and specific technical skills (Python, Flask/Django, PostgreSQL, AWS/GCP), making Experience and Skills CRITICAL. Project quality is mentioned as IMPORTANT for evaluating practical abilities. Positions and Education are less emphasized.',
  candidates: [
    {
      id: 'c1', rank: 1, name: 'Sara Ahmed', email: 'sara.ahmed@email.com', match_score: 94,
      summary: ['5 years Python at Google', 'Led team of 5 on ML project', 'Junior→Senior in 3 years'],
      scores: { experience: 95, skills: 92, projects: 98, positions: 88, education: 85 },
      tie_breaker_applied: false,
      why_selected: 'Exceptional match in CRITICAL dimensions. 5 years of Python experience at Google directly aligns with the senior-level requirement.',
      compared_to_pool: 'Outranks 44 of 45 candidates. Top 2% in Experience score, top 5% in Skills.'
    },
    {
      id: 'c2', rank: 2, name: 'Michael Chen', email: 'michael.chen@email.com', match_score: 91,
      summary: ['4 years Django at Microsoft', 'Built scalable microservices', 'AWS certified architect'],
      scores: { experience: 88, skills: 94, projects: 90, positions: 85, education: 80 },
      tie_breaker_applied: true,
      why_selected: 'Strong Skills score in CRITICAL dimension. AWS certification demonstrates cloud expertise.',
      compared_to_pool: 'Tied with Priya Patel at 91% match. Outranks 42 of 45 candidates.',
      tie_breaker_reason: 'Ranked higher due to AWS certification (job explicitly mentions AWS/GCP).'
    },
    {
      id: 'c3', rank: 3, name: 'Priya Patel', email: 'priya.patel@email.com', match_score: 91,
      summary: ['6 years backend development', 'PostgreSQL optimization expert', 'Open source contributor'],
      scores: { experience: 92, skills: 90, projects: 88, positions: 82, education: 78 },
      tie_breaker_applied: true,
      why_selected: 'Highest Experience score among tied candidates. 6 years of backend development shows strong seniority.',
      compared_to_pool: 'Tied with Michael Chen at 91% match. Top 10% in Experience.',
      tie_breaker_reason: 'Ranked lower despite higher Experience because job prioritizes cloud certifications.'
    },
    {
      id: 'c4', rank: 4, name: 'James Wilson', email: 'james.wilson@email.com', match_score: 87,
      summary: ['3 years Flask development', 'GCP cloud infrastructure', 'CI/CD pipeline expert'],
      scores: { experience: 75, skills: 88, projects: 92, positions: 78, education: 72 },
      tie_breaker_applied: false,
      why_selected: 'Strong Projects score demonstrates practical ability. GCP infrastructure experience matches cloud requirements.',
      compared_to_pool: 'Outranks 38 of 45 candidates. Lower Experience offset by excellent project portfolio.'
    },
    {
      id: 'c5', rank: 5, name: 'Emily Rodriguez', email: 'emily.rodriguez@email.com', match_score: 85,
      summary: ['4 years Python/Django', 'Fintech experience', 'Strong testing practices'],
      scores: { experience: 82, skills: 85, projects: 80, positions: 75, education: 88 },
      tie_breaker_applied: false,
      why_selected: 'Balanced scores across CRITICAL dimensions. Fintech experience shows ability to work in regulated environments.',
      compared_to_pool: 'Outranks 35 of 45 candidates. Solid all-around profile.'
    },
    {
      id: 'c6', rank: 6, name: 'David Kim', email: 'david.kim@email.com', match_score: 82,
      summary: ['2 years Python at startup', 'Fast learner, quick growth', 'Docker/Kubernetes experience'],
      scores: { experience: 65, skills: 78, projects: 85, positions: 70, education: 90 },
      tie_breaker_applied: false,
      why_selected: 'High growth trajectory compensates for lower experience. Docker/Kubernetes skills valuable for microservices.',
      compared_to_pool: 'Outranks 32 of 45 candidates. Shows rapid career progression.'
    }
  ],
  eliminated: {
    count: 13,
    breakdown: { experience: 8, skills: 5 },
    candidates: [
      { name: 'John Doe', reason: 'Experience 45% < min 60%' },
      { name: 'Jane Smith', reason: 'Skills 40% < min 50%' },
      { name: 'Bob Johnson', reason: 'Experience 52% < min 60%' },
      { name: 'Alice Brown', reason: 'Skills 48% < min 50%' },
      { name: 'Charlie Wilson', reason: 'Experience 55% < min 60%' },
      { name: 'Diana Lee', reason: 'Skills 42% < min 50%' },
      { name: 'Edward Martinez', reason: 'Experience 38% < min 60%' },
      { name: 'Fiona Garcia', reason: 'Experience 50% < min 60%' },
      { name: 'George Taylor', reason: 'Skills 35% < min 50%' },
      { name: 'Hannah Anderson', reason: 'Experience 48% < min 60%' },
      { name: 'Ivan Thomas', reason: 'Experience 42% < min 60%' },
      { name: 'Julia Jackson', reason: 'Skills 45% < min 50%' },
      { name: 'Kevin White', reason: 'Experience 58% < min 60%' }
    ]
  },
  why_not_others: '45 candidates evaluated across 3 sessions. 13 were eliminated for not meeting minimum thresholds in Experience or Skills. The remaining 26 candidates passed thresholds but ranked below the top 6 due to lower weighted scores in CRITICAL dimensions.',
  common_gaps: [
    'Insufficient years of Python experience (15 candidates)',
    'No team leadership or mentorship experience (8 candidates)',
    'Missing cloud platform certifications (5 candidates)',
    'Limited microservices architecture exposure (4 candidates)'
  ]
};

function DashboardPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isNotFound, setIsNotFound] = useState(false);
  const [selectedForEmail, setSelectedForEmail] = useState([]);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [compareSelection, setCompareSelection] = useState([]);
  const [showComparison, setShowComparison] = useState(false);

  // Email selection handler - toggles full candidate object
  const handleEmailSelect = useCallback((candidate) => {
    setSelectedForEmail(prev => {
      const exists = prev.some(c => c.id === candidate.id);
      if (exists) {
        return prev.filter(c => c.id !== candidate.id);
      }
      return [...prev, candidate];
    });
  }, []);

  const clearEmailSelection = useCallback(() => {
    setSelectedForEmail([]);
  }, []);

  const handleCompare = useCallback((candidate) => {
    setCompareSelection(prev => {
      // If already selected, deselect
      if (prev.some(c => c.id === candidate.id)) {
        return prev.filter(c => c.id !== candidate.id);
      }

      // If we have 2 already, replace the second
      if (prev.length >= 2) {
        return [prev[0], candidate];
      }

      // Add to selection
      const newSelection = [...prev, candidate];

      // If we now have 2, open modal
      if (newSelection.length === 2) {
        setShowComparison(true);
      }

      return newSelection;
    });
  }, []);

  const clearComparison = useCallback(() => {
    setCompareSelection([]);
    setShowComparison(false);
  }, []);

  // Close modal without clearing selection (allows swapping candidates)
  const closeComparisonModal = useCallback(() => {
    setShowComparison(false);
  }, []);

  // Keyboard support: ESC to clear comparison selection
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && compareSelection.length > 0) {
        clearComparison();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [compareSelection, clearComparison]);

  useEffect(() => {
    const fetchSessionData = async () => {
      try {
        setLoading(true);
        setError(null);
        setIsNotFound(false);

        // Try to fetch from API
        const response = await getSession(sessionId);

        if (response.success) {
          setData(response.data);
        } else {
          throw new Error(response.error?.message || 'Failed to load session');
        }
      } catch (err) {
        console.error('Dashboard fetch error:', err);

        // Check for 404
        if (err.response?.status === 404) {
          setIsNotFound(true);
          setError('Session not found');
        } else if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error')) {
          // Backend not running - use mock data for development
          console.log('Backend unavailable, using mock data');
          setData(MOCK_DATA);
        } else {
          setError(err.message || 'Failed to load results');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchSessionData();
  }, [sessionId]);

  if (loading) return <DashboardSkeleton />;
  if (error && (isNotFound || !data)) return <DashboardError error={error} isNotFound={isNotFound} />;

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div className="flex-1">
            {data?.session?.created_at && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                <Calendar className="h-4 w-4" />
                Analysis from {formatDate(data.session.created_at)}
              </div>
            )}
            <h1 className="text-3xl">{data?.session?.role_title}</h1>
            <p className="text-muted-foreground mt-2 line-clamp-2">
              {data?.session?.job_description?.substring(0, 200)}...
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/history')}
            >
              <History className="h-4 w-4 mr-2" />
              History
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => exportToCSV(data?.candidates, data?.session?.role_title || 'candidates')}
              disabled={!data?.candidates?.length}
            >
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
            <Button
              size="sm"
              onClick={() => navigate('/')}
            >
              <Plus className="h-4 w-4 mr-2" />
              New Analysis
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content Card */}
      <Card className="border-border shadow-lg">
        <CardContent className="p-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard
              label="Total in Pool"
              value={data?.stats?.total_in_pool || 0}
              icon={Users}
            />
            <StatCard
              label="Added This Session"
              value={data?.stats?.added_this_session || 0}
              subtext="new candidates"
              icon={UserPlus}
              variant="success"
            />
            <StatCard
              label="Eliminated"
              value={data?.stats?.eliminated_count || 0}
              subtext="by thresholds"
              icon={UserMinus}
              variant="warning"
            />
            <StatCard
              label="Ranked"
              value={data?.stats?.ranked_count || 0}
              subtext="candidates"
              icon={Award}
            />
          </div>

          {/* Priority Badges - Story 5.2 */}
          <PriorityBadges
            priorities={data?.inferred_priorities}
            reasoning={data?.priority_reasoning}
          />

          {/* Candidate Cards - Story 5.3 */}
          <div className="mb-8">
            <h2 className="text-2xl mb-4">Top Candidates</h2>
            <CandidateCardGrid
              candidates={data?.candidates || []}
              priorities={data?.inferred_priorities}
              selectedForEmail={selectedForEmail}
              onEmailSelect={handleEmailSelect}
              onCompare={handleCompare}
              compareSelection={compareSelection}
            />
          </div>

          {/* Eliminated Section - Story 5.6 */}
          <EliminatedSection eliminated={data?.eliminated} />

          {/* Why Not Others - Story 5.7 */}
          <WhyNotOthers
            stats={data?.stats}
            whyNotOthersText={data?.why_not_others}
            commonGaps={data?.common_gaps}
          />
        </CardContent>
      </Card>

      {/* Email Selected Button - Story 6.2 */}
      <EmailSelectedButton
        count={selectedForEmail.length}
        onClick={() => setShowEmailModal(true)}
        disabled={selectedForEmail.length === 0}
      />

      {/* Comparison Indicator Bar - Story 5.9 */}
      <ComparisonIndicator
        selection={compareSelection}
        onClear={clearComparison}
      />

      {/* Comparison Modal - Story 5.10 */}
      <ComparisonModal
        open={showComparison && compareSelection.length === 2}
        onClose={closeComparisonModal}
        candidates={compareSelection}
        sessionId={sessionId}
      />

      {/* Email Modal - Story 6.3/6.4 */}
      <EmailModal
        open={showEmailModal}
        onClose={() => {
          setShowEmailModal(false);
          clearEmailSelection();
        }}
        selectedCandidates={selectedForEmail}
        sessionId={sessionId}
        jobTitle={data?.session?.role_title}
        company="Our Company"
      />
    </div>
  );
}

export default DashboardPage;
